import bpy
import hashlib
import json
import math
import random
from ..generators import building_gen
from ..generators import city_layout
from ..generators import block_extract
from ..generators import plot_split
from ..generators import height_assign
from ..generators import batch_buildings
from ..generators import lod_system
from ..generators import detail_gen
from ..utils import osm_parser
from ..utils import geo_projection
from ..utils import typology_classifier
from ..utils.geo_utils import polygon_area, polygon_centroid


class CITYP_OT_Generate(bpy.types.Operator):
    bl_idname = "cityp.generate"
    bl_label = "Generate"
    bl_description = "Generate a parametric building or city"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.cityp_settings

        if props.gen_mode == "single":
            return self._generate_single(props, context)
        elif props.gen_mode == "city":
            return self._generate_city(props, context)
        else:
            return self._generate_osm(props, context)

    def _generate_single(self, props, context):
        params = {
            "base_w": props.base_w,
            "base_d": props.base_d,
            "height": props.height,
            "typology": props.typology,
            "seed": props.seed,
            "sections": props.sections,
            "setback_ratio": props.setback_ratio,
            "setback_variance": 0.06,
            "twist_deg": props.twist_deg,
            "taper_ratio": props.taper_ratio,
            "podium_height": props.podium_height,
            "tower_ratio": props.tower_ratio,
            "roof_type": props.roof_type,
            "facade_detail": props.facade_detail,
        }

        obj = building_gen.generate_building(params, context=context)

        if obj is None:
            self.report({"ERROR"}, "Generation failed. Check console for details.")
            return {"CANCELLED"}

        self.report({"INFO"}, f"Generated {props.typology} · {props.height}m")
        return {"FINISHED"}

    def _generate_city(self, props, context):
        seed = props.seed

        self.report({"INFO"}, "Generating road graph...")
        graph = city_layout.generate_road_graph(
            radius=props.city_radius,
            main_spacing=props.main_grid_spacing,
            sub_spacing=props.sub_grid_spacing,
            perturbation_pct=props.perturbation_pct,
            seed=seed,
            road_mode=props.road_mode,
        )
        self.report({"INFO"}, f"Road graph: {graph.node_count()} nodes, {len(graph.edges)} edges")

        self.report({"INFO"}, "Extracting blocks...")
        blocks = block_extract.extract_blocks_from_graph(graph)
        self.report({"INFO"}, f"Found {len(blocks)} blocks")

        all_plots = []
        for block in blocks:
            min_area = 200.0
            max_area = 1500.0
            cx, cy = block["center"]
            block_seed = int(hashlib.md5(f"{cx:.4f},{cy:.4f},{seed}".encode()).hexdigest(), 16) % 10000
            plots = plot_split.split_block_into_plots(
                block["polygon"],
                setback=props.setback,
                min_area=min_area,
                max_area=max_area,
                seed=block_seed,
                density=props.building_density,
            )
            for plot in plots:
                all_plots.append(plot)

        self.report({"INFO"}, f"Generated {len(all_plots)} plots")

        building_specs = height_assign.assign_heights(
            all_plots,
            city_center=(0, 0),
            avg_floors=props.avg_floors,
            floor_variance=props.floor_variance,
            seed=seed,
            height_mode=props.height_mode,
            corridor_angle=props.corridor_angle,
            corridor_width=props.corridor_width,
            metro_peak=props.metro_peak,
            metro_intensity=props.metro_intensity,
            waterfront_premium=props.waterfront_premium,
            waterfront_dir=props.waterfront_dir,
            waterfront_dist=props.waterfront_dist,
        )

        road_edges = graph.get_edges_with_width()

        building_col, road_col = batch_buildings.batch_place_buildings(
            building_specs,
            seed=seed,
            road_edges=road_edges,
            context=context,
            road_width=props.road_width,
            roof_type=props.roof_type,
            facade_detail=props.facade_detail,
        )

        if props.add_roof_details:
            for obj in list(building_col.objects):
                obj_seed = int(hashlib.md5(obj.name.encode()).hexdigest(), 16) % 10000
                detail_gen.add_roof_details(obj, seed + obj_seed)

        if props.lod_level < 3:
            for obj in list(building_col.objects):
                lod_system.apply_lod(obj, props.lod_level)

        self.report({"INFO"}, f"City generated: {len(building_specs)} buildings")
        return {"FINISHED"}

    def _generate_osm(self, props, context):
        raw = context.scene.cityp_osm_data_raw
        if not raw:
            self.report({"ERROR"}, "No OSM data loaded. Click 'Fetch OSM Data' first.")
            return {"CANCELLED"}

        try:
            osm_json = json.loads(raw)
        except json.JSONDecodeError:
            self.report({"ERROR"}, "Corrupted OSM cache data.")
            return {"CANCELLED"}

        osm = osm_parser.parse_osm_json(osm_json)

        origin_lat = osm.origin_lat
        origin_lon = osm.origin_lon

        self.report({"INFO"}, f"Processing {len(osm.buildings)} buildings from OSM...")

        building_specs = []
        for idx, way in enumerate(osm.buildings):
            footprint = osm_parser.get_building_footprint(way, osm)
            if footprint is None or len(footprint) < 3:
                continue

            local_coords = [geo_projection.latlon_to_local(lat, lon, origin_lat, origin_lon) for lat, lon in footprint]

            area = abs(polygon_area(local_coords))
            if area < 10:
                continue

            center = polygon_centroid(local_coords)
            cx, cy = center
            dist = (cx * cx + cy * cy) ** 0.5
            dist_ratio = min(dist / 800.0, 1.0)

            height = self._infer_height(way)

            typology = typology_classifier.classify_typology(
                area=area,
                height=height,
                dist_ratio=dist_ratio,
                osm_tags=way.get("tags", {}),
                rng=random.Random(int(hashlib.md5(str(way["id"]).encode()).hexdigest(), 16)),
            )

            building_specs.append({
                "plot": local_coords,
                "center": center,
                "area": area,
                "height": height,
                "typology": typology,
                "dist_ratio": dist_ratio,
            })

        self.report({"INFO"}, f"Building specs prepared: {len(building_specs)}")

        road_edges = []
        for way in osm.highways:
            hcoords = osm_parser.get_highway_coords(way, osm)
            if len(hcoords) < 2:
                continue
            local_hcoords = [geo_projection.latlon_to_local(lat, lon, origin_lat, origin_lon) for lat, lon in hcoords]
            for i in range(len(local_hcoords) - 1):
                road_edges.append((local_hcoords[i], local_hcoords[i + 1]))

        building_col, road_col = batch_buildings.batch_place_buildings(
            building_specs,
            seed=props.seed,
            road_edges=road_edges,
            context=context,
            roof_type=props.roof_type,
            facade_detail=props.facade_detail,
        )

        if props.add_roof_details:
            for obj in list(building_col.objects):
                obj_seed = int(hashlib.md5(obj.name.encode()).hexdigest(), 16) % 10000
                detail_gen.add_roof_details(obj, props.seed + obj_seed)

        if props.lod_level < 3:
            for obj in list(building_col.objects):
                lod_system.apply_lod(obj, props.lod_level)

        self.report({"INFO"}, f"OSM city generated: {len(building_specs)} buildings, {len(road_edges)} road segments")
        return {"FINISHED"}

    def _infer_height(self, way):
        tags = way.get("tags", {})

        if "height" in tags:
            try:
                h = float(tags["height"])
                return max(h, 3.0)
            except (ValueError, TypeError):
                pass

        if "building:levels" in tags:
            try:
                levels = float(tags["building:levels"])
                return max(levels * 3.0, 3.0)
            except (ValueError, TypeError):
                pass

        building_type = tags.get("building", "").lower()
        type_heights = {
            "residential": 20.0,
            "apartments": 30.0,
            "commercial": 25.0,
            "office": 40.0,
            "retail": 10.0,
            "industrial": 8.0,
            "warehouse": 6.0,
            "house": 8.0,
            "garage": 3.0,
        }
        base = type_heights.get(building_type, 15.0)

        way_id = way.get("id", 0)
        try:
            seed_val = int(way_id)
        except (ValueError, TypeError):
            seed_val = int(hashlib.md5(str(way_id).encode()).hexdigest(), 16)
        rng = random.Random(seed_val)
        return max(base * (0.7 + 0.6 * rng.random()), 3.0)
