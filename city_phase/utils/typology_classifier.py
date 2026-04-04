import json
import os
import random


_typology_cache = None


def load_typology_data():
    global _typology_cache
    if _typology_cache is not None:
        return _typology_cache

    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "typologies.json")
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            _typology_cache = json.load(f)
    except Exception:
        _typology_cache = _get_fallback_data()

    return _typology_cache


def classify_typology(area, height, dist_ratio, osm_tags=None, rng=None):
    if rng is None:
        rng = random.Random()

    if osm_tags:
        result = _classify_from_osm_tags(osm_tags, area, height, rng)
        if result:
            return result

    return _classify_heuristic(area, height, dist_ratio, rng)


def _classify_from_osm_tags(tags, area, height, rng):
    typology_data = load_typology_data()
    mapping = typology_data.get("osm_type_mapping", {})

    building_type = tags.get("building", "").lower()
    candidates = mapping.get(building_type, [])

    if not candidates:
        return None

    if len(candidates) == 1:
        return _map_to_generator(candidates[0])

    return _map_to_generator(rng.choice(candidates))


def _classify_heuristic(area, height, dist_ratio, rng):
    if height > 60 and area < 800:
        return "stepped_tower"
    elif height > 40 and area > 1000:
        return "podium_tower"
    elif height > 15 and area > 400 and area < 2000:
        if rng.random() < 0.5:
            return "slab"
        else:
            return "tapered"
    elif height < 20 and area < 300:
        return "old_res"
    elif area > 1500 and height > 15:
        return "complex"
    elif height < 12 and area > 500:
        return "industrial"
    elif dist_ratio < 0.3:
        return rng.choice(["stepped_tower", "podium_tower"])
    elif dist_ratio < 0.6:
        return rng.choice(["tapered", "slab", "old_res"])
    else:
        return rng.choice(["old_res", "industrial", "tapered"])


def _map_to_generator(typology_key):
    mapping = {
        "tower": "stepped_tower",
        "podium": "podium_tower",
        "slab": "slab",
        "old_res": "old_res",
        "complex": "complex",
        "industrial": "industrial",
    }
    return mapping.get(typology_key, "stepped_tower")


def get_typology_params(typology_key, rng=None):
    if rng is None:
        rng = random.Random()

    data = load_typology_data()
    typologies = data.get("typologies", {})

    key_map = {
        "stepped_tower": "tower",
        "podium_tower": "podium",
        "slab": "slab",
        "old_res": "old_res",
        "complex": "complex",
        "industrial": "industrial",
    }

    json_key = key_map.get(typology_key, typology_key)
    typology = typologies.get(json_key, {})
    params = typology.get("params", {})

    result = {}
    for key, value in params.items():
        if isinstance(value, list) and len(value) == 2:
            if isinstance(value[0], int):
                result[key] = rng.randint(value[0], value[1])
            else:
                result[key] = rng.uniform(value[0], value[1])
        else:
            result[key] = value

    return result


def _get_fallback_data():
    return {
        "typologies": {
            "tower": {"generator": "stepped_tower", "params": {}},
            "podium": {"generator": "podium_tower", "params": {}},
            "slab": {"generator": "slab", "params": {}},
            "old_res": {"generator": "old_res", "params": {}},
            "complex": {"generator": "complex", "params": {}},
            "industrial": {"generator": "industrial", "params": {}},
        },
        "osm_type_mapping": {
            "apartments": ["tower"],
            "residential": ["tower"],
            "commercial": ["complex"],
            "office": ["tower"],
            "industrial": ["industrial"],
        },
    }
