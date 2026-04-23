import bpy
import json
import os


class CITYP_OT_ImportOSMFile(bpy.types.Operator):
    bl_idname = "cityp.import_osm_file"
    bl_label = "Import OSM File"
    bl_description = "Import OSM data from a local JSON or XML file"
    bl_options = {"REGISTER"}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.json;*.xml;*.osm", options={"HIDDEN"})

    def execute(self, context):
        if not self.filepath or not os.path.exists(self.filepath):
            self.report({"ERROR"}, f"File not found: {self.filepath}")
            return {"CANCELLED"}

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                raw = f.read()
        except Exception as e:
            self.report({"ERROR"}, f"Failed to read file: {str(e)}")
            return {"CANCELLED"}

        ext = os.path.splitext(self.filepath)[1].lower()

        try:
            if ext in (".json",):
                data = json.loads(raw)
                count = len(data.get("elements", []))
            elif ext in (".xml", ".osm"):
                data = raw
                count = raw.count('<node') + raw.count('<way') + raw.count('<relation')
            else:
                self.report({"ERROR"}, f"Unsupported file format: {ext}")
                return {"CANCELLED"}
        except Exception as e:
            self.report({"ERROR"}, f"Failed to parse file: {str(e)}")
            return {"CANCELLED"}

        from ..utils import osm_parser

        if ext == ".json":
            osm = osm_parser.parse_osm_json(data)
        else:
            osm = osm_parser.parse_osm_xml(data)

        if not osm.buildings and not osm.highways:
            self.report({"WARNING"}, "No buildings or roads found in OSM file")
            return {"CANCELLED"}

        context.scene.cityp_osm_data_raw = json.dumps(data) if ext == ".json" else raw
        self.report({"INFO"}, f"Imported OSM: {len(osm.buildings)} buildings, {len(osm.highways)} roads")
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
