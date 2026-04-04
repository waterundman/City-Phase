import bpy
import os


class CITYP_OT_Export(bpy.types.Operator):
    bl_idname = "cityp.export"
    bl_label = "Export City"
    bl_description = "Export city to FBX/OBJ/USD"
    bl_options = {"REGISTER"}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        props = context.scene.cityp_settings
        fmt = props.export_format
        layered = props.export_layered

        base_path = self.filepath
        if not base_path:
            base_path = os.path.join(bpy.path.abspath("//"), "cityp_export")

        if layered:
            return self._export_layered(context, base_path, fmt)
        else:
            return self._export_merged(context, base_path, fmt)

    def _export_layered(self, context, base_path, fmt):
        collections = {
            "CityP_Buildings": "buildings",
            "CityP_Roads": "roads",
        }

        for col_name, suffix in collections.items():
            col = bpy.data.collections.get(col_name)
            if not col or not col.objects:
                continue

            ext = fmt.lower()
            filepath = f"{base_path}_{suffix}.{ext}"

            self._export_collection(context, col, filepath, fmt)
            self.report({"INFO"}, f"Exported {col_name} → {filepath}")

        return {"FINISHED"}

    def _export_merged(self, context, base_path, fmt):
        ext = fmt.lower()
        filepath = f"{base_path}.{ext}"

        all_objs = []
        for col_name in ["CityP_Buildings", "CityP_Roads"]:
            col = bpy.data.collections.get(col_name)
            if col:
                all_objs.extend(col.objects)

        if not all_objs:
            self.report({"WARNING"}, "No objects to export")
            return {"CANCELLED"}

        prev_sel = context.selected_objects
        prev_active = context.view_layer.objects.active

        for obj in all_objs:
            obj.select_set(True)
        context.view_layer.objects.active = all_objs[0] if all_objs else None

        if fmt == "FBX":
            bpy.ops.export_scene.fbx(
                filepath=filepath,
                use_selection=True,
                apply_unit_scale=True,
            )
        elif fmt == "OBJ":
            bpy.ops.export_scene.obj(
                filepath=filepath,
                use_selection=True,
                use_materials=False,
            )
        elif fmt == "USD":
            bpy.ops.export_scene.usd(
                filepath=filepath,
                use_selection=True,
            )

        for obj in bpy.data.objects:
            obj.select_set(False)
        for obj in prev_sel:
            obj.select_set(True)
        context.view_layer.objects.active = prev_active

        self.report({"INFO"}, f"Exported merged → {filepath}")
        return {"FINISHED"}

    def _export_collection(self, context, col, filepath, fmt):
        prev_sel = context.selected_objects
        prev_active = context.view_layer.objects.active

        for obj in bpy.data.objects:
            obj.select_set(False)
        for obj in col.objects:
            obj.select_set(True)
        context.view_layer.objects.active = col.objects[0] if col.objects else None

        if fmt == "FBX":
            bpy.ops.export_scene.fbx(
                filepath=filepath,
                use_selection=True,
                apply_unit_scale=True,
            )
        elif fmt == "OBJ":
            bpy.ops.export_scene.obj(
                filepath=filepath,
                use_selection=True,
                use_materials=False,
            )
        elif fmt == "USD":
            bpy.ops.export_scene.usd(
                filepath=filepath,
                use_selection=True,
            )

        for obj in bpy.data.objects:
            obj.select_set(False)
        for obj in prev_sel:
            obj.select_set(True)
        context.view_layer.objects.active = prev_active

    def invoke(self, context, event):
        props = context.scene.cityp_settings
        ext = props.export_format.lower()
        self.filepath = f"cityp_export.{ext}"
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
