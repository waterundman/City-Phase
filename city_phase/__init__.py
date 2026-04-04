bl_info = {
    "name": "城市相 CityPhase",
    "author": "CityPhase Team",
    "version": (0, 4, 0),
    "blender": (3, 6, 0),
    "category": "Add Mesh",
    "description": "Procedural city white model generator with render pipeline presets",
}

import bpy
import json
from .properties import CityPhaseSettings
from .operators.op_generate import CITYP_OT_Generate
from .operators.op_osm_fetch import CITYP_OT_FetchOSM
from .operators.op_apply_pipeline import CITYP_OT_ApplyPipeline
from .operators.op_export import CITYP_OT_Export
from .panels.panel_main import CITYP_PT_MainPanel

classes = (
    CityPhaseSettings,
    CITYP_OT_Generate,
    CITYP_OT_FetchOSM,
    CITYP_OT_ApplyPipeline,
    CITYP_OT_Export,
    CITYP_PT_MainPanel,
)


def _get_osm_data(self):
    raw = self.get("cityp_osm_data_raw", "")
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            return None
    return None


def _set_osm_data(self, value):
    if value is None:
        self["cityp_osm_data_raw"] = ""
    else:
        self["cityp_osm_data_raw"] = json.dumps(value)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.cityp_settings = bpy.props.PointerProperty(type=CityPhaseSettings)
    bpy.types.Scene.cityp_osm_data = property(_get_osm_data, _set_osm_data)
    bpy.types.Scene.cityp_pipeline = bpy.props.EnumProperty(
        name="Pipeline",
        items=[
            ("arch_white", "Arch White", "建筑白膜"),
            ("golden_hour", "Golden Hour", "黄昏金切"),
            ("neon_rain", "Neon Rain", "霓虹雨夜"),
            ("iso_clear", "Iso Clear", "等轴晴空"),
        ],
        default="arch_white",
    )


def unregister():
    del bpy.types.Scene.cityp_pipeline
    del bpy.types.Scene.cityp_osm_data
    del bpy.types.Scene.cityp_settings
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
