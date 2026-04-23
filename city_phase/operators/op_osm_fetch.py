import bpy
import os
import json
import math
import time
import urllib.request
import urllib.parse
import threading


class CITYP_OT_FetchOSM(bpy.types.Operator):
    bl_idname = "cityp.fetch_osm"
    bl_label = "Fetch OSM Data"
    bl_description = "Fetch building and road data from Overpass API"
    bl_options = {"REGISTER"}

    def modal(self, context, event):
        if event.type == "TIMER":
            if self._done:
                context.window_manager.event_timer_remove(self._timer)

                if self._error:
                    self.report({"ERROR"}, self._error)
                    return {"CANCELLED"}

                if self._result:
                    props = context.scene.cityp_settings
                    cache_path = self._get_cache_path(props)
                    self._save_cache(self._result, cache_path)
                    context.scene.cityp_osm_data_raw = json.dumps(self._result)
                    count = len(self._result.get("elements", []))
                    self.report({"INFO"}, f"OSM data fetched: {count} elements")

                return {"FINISHED"}

        return {"PASS_THROUGH"}

    def execute(self, context):
        self._timer = None
        self._thread = None
        self._result = None
        self._error = None
        self._done = False
        self._progress = 0.0
        self._status_message = ""

        props = context.scene.cityp_settings

        cache_path = self._get_cache_path(props)
        cached = self._load_cache(cache_path)
        if cached:
            context.scene.cityp_osm_data_raw = json.dumps(cached)
            self.report({"INFO"}, "Loaded OSM data from cache")
            return {"FINISHED"}

        query = self._build_query(props)

        self._thread = threading.Thread(target=self._fetch_thread, args=(query,))
        self._thread.start()

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.5, window=context.window)
        wm.modal_handler_add(self)

        return {"RUNNING_MODAL"}

    def cancel(self, context):
        if self._timer:
            context.window_manager.event_timer_remove(self._timer)

    def _fetch_thread(self, query):
        try:
            self._status_message = "Connecting to Overpass API..."
            self._progress = 0.1

            url = "https://overpass-api.de/api/interpreter"
            data = urllib.parse.urlencode({"data": query}).encode("utf-8")

            req = urllib.request.Request(url, data=data, method="POST")
            req.add_header("User-Agent", "CityPhase Blender Plugin/0.1")

            self._status_message = "Downloading..."
            self._progress = 0.3

            with urllib.request.urlopen(req, timeout=120) as response:
                raw = response.read()
                self._progress = 0.9
                self._status_message = "Parsing..."

            self._result = json.loads(raw.decode("utf-8"))
            self._progress = 1.0
            self._status_message = "Done"

        except Exception as e:
            self._error = f"OSM fetch failed: {str(e)}"
        finally:
            self._done = True

    def _build_query(self, props):
        if props.osm_source == "bbox":
            lat_min = props.bbox_lat_min
            lon_min = props.bbox_lon_min
            lat_max = props.bbox_lat_max
            lon_max = props.bbox_lon_max
        else:
            center_lat = props.osm_lat
            center_lon = props.osm_lon
            radius = props.osm_radius
            lat_min = center_lat - radius / 111000.0
            cos_lat = max(0.01, math.cos(math.radians(center_lat)))
            lon_min = center_lon - radius / (111000.0 * cos_lat)
            lat_max = center_lat + radius / 111000.0
            lon_max = center_lon + radius / (111000.0 * cos_lat)

        query = f"""
        [out:json][timeout:120];
        (
          way["building"]({lat_min},{lon_min},{lat_max},{lon_max});
          way["highway"]({lat_min},{lon_min},{lat_max},{lon_max});
          relation["building"]({lat_min},{lon_min},{lat_max},{lon_max});
        );
        out body;
        >;
        out skel qt;
        """
        return query.strip()

    def _get_cache_path(self, props):
        cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "osm_cache")
        os.makedirs(cache_dir, exist_ok=True)

        if props.osm_source == "bbox":
            key = f"{props.bbox_lat_min:.4f}_{props.bbox_lon_min:.4f}_{props.bbox_lat_max:.4f}_{props.bbox_lon_max:.4f}"
        else:
            key = f"{props.osm_lat:.4f}_{props.osm_lon:.4f}_{props.osm_radius}"

        return os.path.join(cache_dir, f"osm_{key}.json")

    def _save_cache(self, data, path):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception:
            pass

    def _load_cache(self, path):
        if os.path.exists(path):
            try:
                age = time.time() - os.path.getmtime(path)
                if age < 7 * 24 * 3600:
                    with open(path, "r", encoding="utf-8") as f:
                        return json.load(f)
            except Exception:
                pass
        return None
