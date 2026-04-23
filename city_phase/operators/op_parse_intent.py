import bpy
from ..utils.design_intent import parse_intent, apply_intent_to_props


class CITYP_OT_ParseIntent(bpy.types.Operator):
    bl_idname = "cityp.parse_intent"
    bl_label = "Parse Design Intent"
    bl_description = "Parse natural language design intent and update style parameters"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.cityp_settings
        text = props.design_intent.strip()

        if not text:
            self.report({"WARNING"}, "Please enter a design intent first.")
            return {"CANCELLED"}

        result = parse_intent(text)
        apply_intent_to_props(props, result)

        keywords = ", ".join(result["matched_keywords"][:5])
        self.report(
            {"INFO"},
            f"Intent: {result['primary']} × {result['secondary']} @ {result['blend']:.0%} "
            f"(confidence: {result['confidence']:.0%}) [{keywords}]"
        )
        return {"FINISHED"}
