import bpy
import bmesh
import math
import random
from mathutils import Vector
from . import building_gen

TYPOLOGY_CONFIG = {
    "stepped_tower": {
        "sections_factor": 0.2,
        "setback_ratio": 0.80,
        "twist_range": 5.0,
    },
    "tapered": {
        "taper_ratio": 0.30,
    },
    "podium_tower": {
        "podium_height_ratio": 0.2,
        "tower_ratio": 0.45,
        "setback_ratio": 0.80,
        "twist_range": 5.0,
    },
    "slab": {
        "width_ratio": 1.5,
        "depth_ratio": 0.5,
    },
    "old_res": {
        "width_ratio": 0.8,
        "depth_ratio": 0.8,
    },
    "complex": {
        "complex_base_height": 18.0,
    },
    "industrial": {
        "width_ratio": 1.8,
        "depth_ratio": 1.2,
        "height_multiplier": 0.4,
    },
}


def batch_place_buildings(building_specs, seed, road_edges=None, context=None, road_width=8.0, roof_type="flat", facade_detail="none"):
    if context is None:
        context = bpy.context

    rng = random.Random(seed)

    building_col = _ensure_collection("CityP_Buildings", context)
    road_col = _ensure_collection("CityP_Roads", context)

    for obj in list(building_col.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    mesh_cache = {}

    for idx, spec in enumerate(building_specs):
        typology = spec.get("typology", "stepped_tower")
        config = TYPOLOGY_CONFIG.get(typology, {})

        area = spec["area"]
        footprint_side = area ** 0.5

        if typology == "slab":
            bw = footprint_side * config.get("width_ratio", 1.5)
            bd = footprint_side * config.get("depth_ratio", 0.5)
        elif typology == "old_res":
            bw = footprint_side * config.get("width_ratio", 0.8)
            bd = footprint_side * config.get("depth_ratio", 0.8)
        elif typology == "industrial":
            bw = footprint_side * config.get("width_ratio", 1.8)
            bd = footprint_side * config.get("depth_ratio", 1.2)
        elif typology == "complex":
            bw = footprint_side * 1.2
            bd = footprint_side * 1.2
        else:
            bw = footprint_side * 0.6
            bd = footprint_side * 0.5

        bw = max(6.0, bw)
        bd = max(6.0, bd)

        height = spec["height"]
        if typology == "industrial":
            height = height * config.get("height_multiplier", 0.4)

        sections = min(12, max(2, int(height / 20)))

        params = {
            "base_w": bw,
            "base_d": bd,
            "height": height,
            "typology": typology,
            "seed": seed + idx,
            "sections": sections,
            "setback_ratio": config.get("setback_ratio", 0.80),
            "setback_variance": 0.06,
            "twist_deg": rng.uniform(-config.get("twist_range", 5), config.get("twist_range", 5)),
            "taper_ratio": config.get("taper_ratio", 0.30),
            "podium_height": min(height * config.get("podium_height_ratio", 0.2), height * 0.3),
            "tower_ratio": config.get("tower_ratio", 0.45),
            "complex_base_height": config.get("complex_base_height", 18.0),
            "roof_type": roof_type,
            "facade_detail": facade_detail,
        }

        cache_key = (
            typology,
            sections,
            round(bw, 1),
            round(bd, 1),
            round(height, 1),
            round(params.get("setback_ratio", 0.8), 2),
            round(params.get("twist_deg", 0), 1),
            round(params.get("taper_ratio", 0.3), 2),
            round(params.get("podium_height", 0), 1),
            round(params.get("tower_ratio", 0.45), 2),
            round(params.get("complex_base_height", 18.0), 1),
            roof_type,
            facade_detail,
        )
        if cache_key not in mesh_cache:
            mesh_cache[cache_key] = building_gen.generate_building(params, name=f"CityP_City_Building_{idx}")

        source_obj = mesh_cache[cache_key]
        if source_obj is None:
            continue

        cx, cy = spec["center"]

        obj = bpy.data.objects.new(f"CityP_City_Building_{idx}", source_obj.data.copy())
        obj.location = Vector((cx, cy, 0))

        street_angle = spec.get("street_front_angle", 0.0)
        if street_angle != 0.0:
            obj.rotation_euler = (0, 0, street_angle)

        if source_obj.data.materials:
            for mat in source_obj.data.materials:
                if mat:
                    obj.data.materials.append(mat)

        building_col.objects.link(obj)

    if road_edges:
        _generate_road_mesh(road_edges, road_col, default_width=road_width)

    return building_col, road_col


def _ensure_collection(name, context):
    existing = bpy.data.collections.get(name)
    if existing:
        for obj in list(existing.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        return existing

    col = bpy.data.collections.new(name)
    context.scene.collection.children.link(col)
    return col


def _generate_road_mesh(road_edges, road_col, default_width=8.0):
    mesh = bpy.data.meshes.new("CityP_City_Roads")
    bm = bmesh.new()

    for edge in road_edges:
        if len(edge) == 3:
            a, b, width = edge
            width = width if width else default_width
        else:
            a, b = edge
            width = default_width

        ax, ay = a
        bx, by = b

        dx = bx - ax
        dy = by - ay
        length = (dx * dx + dy * dy) ** 0.5
        if length < 0.01:
            continue

        nx = -dy / length * width / 2
        ny = dx / length * width / 2

        verts = [
            bm.verts.new(Vector((ax + nx, ay + ny, 0.05))),
            bm.verts.new(Vector((ax - nx, ay - ny, 0.05))),
            bm.verts.new(Vector((bx - nx, by - ny, 0.05))),
            bm.verts.new(Vector((bx + nx, by + ny, 0.05))),
        ]
        bm.faces.new(verts)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("CityP_City_Roads", mesh)
    road_col.objects.link(obj)

    mat = bpy.data.materials.get("CityP_RoadMat")
    if not mat:
        mat = bpy.data.materials.new(name="CityP_RoadMat")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (0.35, 0.35, 0.38, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.9
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
