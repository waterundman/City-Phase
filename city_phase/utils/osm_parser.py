import json
import xml.etree.ElementTree as ET


class OSMData:
    def __init__(self):
        self.nodes = {}
        self.ways = []
        self.buildings = []
        self.highways = []
        self.origin_lat = 0.0
        self.origin_lon = 0.0

    def compute_origin(self):
        if not self.nodes:
            return
        lats = [n["lat"] for n in self.nodes.values()]
        lons = [n["lon"] for n in self.nodes.values()]
        self.origin_lat = (min(lats) + max(lats)) / 2.0
        self.origin_lon = (min(lons) + max(lons)) / 2.0


def parse_osm_json(data):
    osm = OSMData()
    relations = []
    all_ways = {}  # way_id -> nodes list

    if isinstance(data, str):
        data = json.loads(data)

    elements = data.get("elements", [])

    for elem in elements:
        etype = elem.get("type")

        if etype == "node":
            osm.nodes[elem["id"]] = {
                "lat": elem.get("lat", 0),
                "lon": elem.get("lon", 0),
                "tags": elem.get("tags", {}),
            }

        elif etype == "way":
            tags = elem.get("tags", {})
            way = {
                "id": elem["id"],
                "nodes": elem.get("nodes", []),
                "tags": tags,
            }
            all_ways[elem["id"]] = elem.get("nodes", [])

            if _is_building(tags):
                osm.buildings.append(way)
            elif _is_highway(tags):
                osm.highways.append(way)
            else:
                osm.ways.append(way)

        elif etype == "relation":
            tags = elem.get("tags", {})
            if tags.get("type") == "multipolygon" and _is_building(tags):
                relations.append({
                    "id": elem["id"],
                    "tags": tags,
                    "members": elem.get("members", []),
                })

    for rel in relations:
        outer_nodes = _extract_multipolygon_outer(rel, all_ways)
        if outer_nodes:
            osm.buildings.append({
                "id": rel["id"],
                "nodes": outer_nodes,
                "tags": rel["tags"],
                "_relation": True,
            })

    osm.compute_origin()
    return osm


def _extract_multipolygon_outer(relation, all_ways):
    outer_nodes = []
    for member in relation.get("members", []):
        if member.get("type") == "way" and member.get("role") == "outer":
            way_id = member.get("ref")
            if way_id in all_ways:
                outer_nodes.extend(all_ways[way_id])
    if len(outer_nodes) < 3:
        return None
    return outer_nodes


def parse_osm_xml(xml_string):
    osm = OSMData()

    root = ET.fromstring(xml_string)

    for child in root:
        if child.tag == "node":
            node_id = int(child.get("id"))
            lat = float(child.get("lat"))
            lon = float(child.get("lon"))
            tags = {}
            for tag_elem in child:
                if tag_elem.tag == "tag":
                    tags[tag_elem.get("k")] = tag_elem.get("v")
            osm.nodes[node_id] = {"lat": lat, "lon": lon, "tags": tags}

        elif child.tag == "way":
            way_id = int(child.get("id"))
            nd_refs = []
            tags = {}
            for tag_elem in child:
                if tag_elem.tag == "nd":
                    nd_refs.append(int(tag_elem.get("ref")))
                elif tag_elem.tag == "tag":
                    tags[tag_elem.get("k")] = tag_elem.get("v")

            way = {"id": way_id, "nodes": nd_refs, "tags": tags}

            if _is_building(tags):
                osm.buildings.append(way)
            elif _is_highway(tags):
                osm.highways.append(way)
            else:
                osm.ways.append(way)

    osm.compute_origin()
    return osm


def _is_building(tags):
    if "building" not in tags:
        return False
    val = tags["building"].lower()
    return val not in ("no", "none", "null", "")


def _is_highway(tags):
    if "highway" not in tags:
        return False
    val = tags["highway"].lower()
    return val not in ("no", "none", "null", "", "footway", "path", "steps", "pedestrian", "cycleway", "bridleway", "track")


def get_building_footprint(way, osm_data):
    coords = []
    for nid in way["nodes"]:
        if nid in osm_data.nodes:
            node = osm_data.nodes[nid]
            coords.append((node["lat"], node["lon"]))

    if len(coords) < 3:
        return None

    if coords[0] != coords[-1]:
        coords.append(coords[0])

    return coords


def get_highway_coords(way, osm_data):
    coords = []
    for nid in way["nodes"]:
        if nid in osm_data.nodes:
            node = osm_data.nodes[nid]
            coords.append((node["lat"], node["lon"]))
    return coords
