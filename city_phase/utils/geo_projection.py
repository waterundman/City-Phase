import math

EARTH_RADIUS = 6371000.0


def latlon_to_local(lat, lon, origin_lat, origin_lon):
    R = EARTH_RADIUS
    x = R * math.radians(lon - origin_lon) * math.cos(math.radians(origin_lat))
    y = R * math.radians(lat - origin_lat)
    return x, y


def latlon_batch_to_local(coords, origin_lat, origin_lon):
    R = EARTH_RADIUS
    cos_lat = math.cos(math.radians(origin_lat))
    lon_rad = math.radians(origin_lon)
    lat_rad = math.radians(origin_lat)

    result = []
    for lat, lon in coords:
        x = R * (math.radians(lon) - lon_rad) * cos_lat
        y = R * (math.radians(lat) - lat_rad)
        result.append((x, y))
    return result


def local_to_latlon(x, y, origin_lat, origin_lon):
    R = EARTH_RADIUS
    lat = origin_lat + math.degrees(y / R)
    lon = origin_lon + math.degrees(x / (R * math.cos(math.radians(origin_lat))))
    return lat, lon
