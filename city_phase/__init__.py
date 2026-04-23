bl_info = {
    "name": "城市相 CityPhase",
    "author": "CityPhase Team",
    "version": (0, 8, 0),
    "blender": (3, 6, 0),
    "category": "Add Mesh",
    "description": "Procedural city white model generator with render pipeline presets",
}

import bpy
from .properties import CityPhaseSettings
from .operators.op_generate import CITYP_OT_Generate
from .operators.op_osm_fetch import CITYP_OT_FetchOSM
from .operators.op_apply_pipeline import CITYP_OT_ApplyPipeline
from .operators.op_export import CITYP_OT_Export
from .operators.op_import_osm import CITYP_OT_ImportOSMFile
from .operators.op_preset import CITYP_OT_SavePreset, CITYP_OT_LoadPreset, CITYP_OT_DeletePreset
from .panels.panel_main import CITYP_PT_MainPanel

classes = (
    CityPhaseSettings,
    CITYP_OT_Generate,
    CITYP_OT_FetchOSM,
    CITYP_OT_ApplyPipeline,
    CITYP_OT_Export,
    CITYP_OT_ImportOSMFile,
    CITYP_OT_SavePreset,
    CITYP_OT_LoadPreset,
    CITYP_OT_DeletePreset,
    CITYP_PT_MainPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.cityp_settings = bpy.props.PointerProperty(type=CityPhaseSettings)
    bpy.types.Scene.cityp_osm_data_raw = bpy.props.StringProperty(
        name="OSM Data Raw",
        description="Raw JSON string of cached OSM data",
        default="",
    )
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
    del bpy.types.Scene.cityp_osm_data_raw
    del bpy.types.Scene.cityp_settings
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
