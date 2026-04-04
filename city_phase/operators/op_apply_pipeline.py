import bpy
from ..pipelines import PIPELINES


class CITYP_OT_ApplyPipeline(bpy.types.Operator):
    bl_idname = "cityp.apply_pipeline"
    bl_label = "Apply Pipeline"
    bl_description = "Apply a render pipeline preset"
    bl_options = {"REGISTER", "UNDO"}

    pipeline: bpy.props.EnumProperty(
        name="Pipeline",
        items=[
            ("arch_white", "Arch White", "建筑白膜"),
            ("golden_hour", "Golden Hour", "黄昏金切"),
            ("neon_rain", "Neon Rain", "霓虹雨夜"),
            ("iso_clear", "Iso Clear", "等轴晴空"),
        ],
        default="arch_white",
    )

    def execute(self, context):
        pipeline_info = PIPELINES.get(self.pipeline)
        if pipeline_info is None:
            self.report({"ERROR"}, f"Unknown pipeline: {self.pipeline}")
            return {"CANCELLED"}

        try:
            pipeline_info["apply"](context)
            self.report({"INFO"}, f"Applied pipeline: {pipeline_info['name_zh']}")
        except Exception as e:
            self.report({"ERROR"}, f"Failed to apply pipeline: {str(e)}")
            return {"CANCELLED"}

        return {"FINISHED"}
