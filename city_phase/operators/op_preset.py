import bpy
import json
import os


PRESET_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "presets")


def _ensure_preset_dir():
    os.makedirs(PRESET_DIR, exist_ok=True)
    return PRESET_DIR


def _get_preset_path(name):
    return os.path.join(_ensure_preset_dir(), f"{name}.json")


PRESET_KEYS = [
    "base_w", "base_d", "height", "typology",
    "sections", "setback_ratio", "twist_deg",
    "taper_ratio", "podium_height", "tower_ratio",
    "city_radius", "main_grid_spacing", "sub_grid_spacing",
    "perturbation_pct", "building_density",
    "avg_floors", "floor_variance", "setback",
    "road_width", "lod_level",
]


class CITYP_OT_SavePreset(bpy.types.Operator):
    bl_idname = "cityp.save_preset"
    bl_label = "Save Preset"
    bl_description = "Save current parameters as a preset"
    bl_options = {"REGISTER"}

    preset_name: bpy.props.StringProperty(name="Preset Name", default="MyPreset")

    def execute(self, context):
        props = context.scene.cityp_settings
        preset = {}
        for key in PRESET_KEYS:
            if hasattr(props, key):
                preset[key] = getattr(props, key)

        path = _get_preset_path(self.preset_name)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(preset, f, indent=2)
            self.report({"INFO"}, f"Preset saved: {self.preset_name}")
        except Exception as e:
            self.report({"ERROR"}, f"Failed to save preset: {str(e)}")
            return {"CANCELLED"}

        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class CITYP_OT_LoadPreset(bpy.types.Operator):
    bl_idname = "cityp.load_preset"
    bl_label = "Load Preset"
    bl_description = "Load parameters from a preset"
    bl_options = {"REGISTER", "UNDO"}

    preset_name: bpy.props.EnumProperty(
        name="Preset",
        items=lambda self, context: _list_presets(),
    )

    def execute(self, context):
        if not self.preset_name:
            self.report({"ERROR"}, "No preset selected")
            return {"CANCELLED"}

        path = _get_preset_path(self.preset_name)
        if not os.path.exists(path):
            self.report({"ERROR"}, f"Preset not found: {self.preset_name}")
            return {"CANCELLED"}

        try:
            with open(path, "r", encoding="utf-8") as f:
                preset = json.load(f)
        except Exception as e:
            self.report({"ERROR"}, f"Failed to load preset: {str(e)}")
            return {"CANCELLED"}

        props = context.scene.cityp_settings
        for key, value in preset.items():
            if hasattr(props, key):
                setattr(props, key, value)

        self.report({"INFO"}, f"Preset loaded: {self.preset_name}")
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class CITYP_OT_DeletePreset(bpy.types.Operator):
    bl_idname = "cityp.delete_preset"
    bl_label = "Delete Preset"
    bl_description = "Delete a saved preset"
    bl_options = {"REGISTER"}

    preset_name: bpy.props.EnumProperty(
        name="Preset",
        items=lambda self, context: _list_presets(),
    )

    def execute(self, context):
        if not self.preset_name:
            return {"CANCELLED"}

        path = _get_preset_path(self.preset_name)
        if os.path.exists(path):
            os.remove(path)
            self.report({"INFO"}, f"Preset deleted: {self.preset_name}")
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


def _list_presets():
    _ensure_preset_dir()
    files = sorted([f for f in os.listdir(PRESET_DIR) if f.endswith(".json")])
    return [(f[:-5], f[:-5], f"Load preset: {f[:-5]}") for f in files] or [("NONE", "No Presets", "Save a preset first")]
