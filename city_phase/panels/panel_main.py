import bpy
import json


class CITYP_PT_MainPanel(bpy.types.Panel):
    bl_label = "城市相"
    bl_idname = "CITYP_PT_MainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "城市相"

    def draw(self, context):
        layout = self.layout
        props = context.scene.cityp_settings

        box = layout.box()
        box.label(text="Mode", icon="WORLD_DATA")
        box.prop(props, "gen_mode")
        box.prop(props, "seed")

        if props.gen_mode == "single":
            self._draw_single(layout, props)
        elif props.gen_mode == "city":
            self._draw_city(layout, props)
        else:
            self._draw_osm(layout, props)

        layout.separator()
        op = layout.operator("cityp.generate", icon="PLAY")

        self._draw_render_pipeline(layout, context)
        self._draw_detail_export(layout, props)

    def _draw_single(self, layout, props):
        box = layout.box()
        box.label(text="Geometry", icon="MESH_CUBE")
        box.prop(props, "typology")
        box.prop(props, "base_w")
        box.prop(props, "base_d")
        box.prop(props, "height")

        if props.typology == "stepped_tower":
            box = layout.box()
            box.label(text="Stepped Tower", icon="MOD_BUILD")
            box.prop(props, "sections")
            box.prop(props, "setback_ratio")
            box.prop(props, "twist_deg")

        elif props.typology == "tapered":
            box = layout.box()
            box.label(text="Tapered Tower", icon="CON_SIZELIKE")
            box.prop(props, "taper_ratio")

        elif props.typology == "podium_tower":
            box = layout.box()
            box.label(text="Podium + Tower", icon="OUTLINER_OB_GROUP_INSTANCE")
            box.prop(props, "podium_height")
            box.prop(props, "tower_ratio")

    def _draw_city(self, layout, props):
        box = layout.box()
        box.label(text="City Layout", icon="GRID")
        box.prop(props, "road_mode")
        box.prop(props, "city_radius")
        box.prop(props, "main_grid_spacing")
        box.prop(props, "sub_grid_spacing")
        box.prop(props, "perturbation_pct")
        box.prop(props, "road_width")

        box = layout.box()
        box.label(text="Buildings", icon="OUTLINER_OB_MESH")
        box.prop(props, "building_density")
        box.prop(props, "avg_floors")
        box.prop(props, "floor_variance")
        box.prop(props, "setback")

    def _draw_osm(self, layout, props):
        box = layout.box()
        box.label(text="OSM Data Source", icon="WORLD")
        box.prop(props, "osm_source")

        if props.osm_source == "center_radius":
            box.prop(props, "osm_lat")
            box.prop(props, "osm_lon")
            box.prop(props, "osm_radius")
        else:
            box.prop(props, "bbox_lat_min")
            box.prop(props, "bbox_lat_max")
            box.prop(props, "bbox_lon_min")
            box.prop(props, "bbox_lon_max")

        box.prop(props, "osm_use_cache")

        row = box.row()
        row.operator("cityp.fetch_osm", icon="URL")
        row.operator("cityp.import_osm_file", icon="FILEBROWSER")

        raw = context.scene.cityp_osm_data_raw
        if raw:
            try:
                od = json.loads(raw)
                box.label(text=f"Loaded: {len(od.get('elements', []))} elements", icon="CHECKMARK")
            except Exception:
                pass

        box = layout.box()
        box.label(text="OSM Generation", icon="OUTLINER_OB_MESH")
        box.prop(props, "setback")

    def _draw_render_pipeline(self, layout, context):
        box = layout.box()
        box.label(text="Render Pipeline", icon="RENDER_STILL")
        box.prop(context.scene, "cityp_pipeline", text="Preset")
        row = box.row()
        row.operator("cityp.apply_pipeline", icon="PLAY", text="Apply Pipeline").pipeline = context.scene.cityp_pipeline

    def _draw_detail_export(self, layout, props):
        box = layout.box()
        box.label(text="Details & Export", icon="EXPORT")
        box.prop(props, "lod_level")
        box.prop(props, "add_roof_details")
        box.prop(props, "export_format")
        box.prop(props, "export_layered")
        row = box.row()
        row.operator("cityp.export", icon="FILE_TICK")

        box = layout.box()
        box.label(text="Presets", icon="PRESET")
        row = box.row(align=True)
        row.operator("cityp.save_preset", icon="ADD")
        row.operator("cityp.load_preset", icon="IMPORT")
        row.operator("cityp.delete_preset", icon="X")
