import math
import random
from ..utils.geo_utils import polygon_area, polygon_centroid


def split_block_into_plots(block_polygon, setback, min_area, max_area, seed, density=1.0):
    """Split a city block into building plots with street-frontage-aware orientation.

    Returns a list of plot dicts:
        {
            "polygon": [(x1,y1), ...],
            "center": (cx, cy),
            "area": float,
            "street_front_angle": float,  # radians, 0 = aligned with +X
        }
    """
    rng = random.Random(seed)

    inset_polygon = _offset_polygon(block_polygon, setback)
    if inset_polygon is None or abs(polygon_area(inset_polygon)) < min_area:
        return []

    # Determine street frontage angle from original block
    street_angle = _find_street_front_angle(block_polygon)

    plots = []
    _recursive_split(inset_polygon, min_area, max_area, rng, plots, depth=0, street_angle=street_angle)

    if density < 1.0:
        plots = [p for p in plots if rng.random() < density]

    return plots


# ============================================================
# Correct polygon offset (parallel-edge with miter join)
# ============================================================
def _offset_polygon(polygon, distance):
    """Inset polygon by moving each edge inward parallel by distance.
    Uses miter join; filters out points that fall outside the original polygon.
    """
    n = len(polygon)
    if n < 3 or distance <= 0:
        return polygon

    # Build offset edges
    offset_edges = []
    for i in range(n):
        p1 = polygon[i]
        p2 = polygon[(i + 1) % n]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = math.hypot(dx, dy)
        if length < 0.001:
            continue
        # Inward normal for CCW polygon
        nx = -dy / length * distance
        ny = dx / length * distance
        offset_edges.append(
            ((p1[0] + nx, p1[1] + ny), (p2[0] + nx, p2[1] + ny))
        )

    m = len(offset_edges)
    if m < 3:
        return None

    # Intersect consecutive offset edges
    result = []
    for i in range(m):
        a1, a2 = offset_edges[i]
        b1, b2 = offset_edges[(i + 1) % m]
        ix = _line_intersection(a1, a2, b1, b2)
        if ix is not None:
            result.append(ix)

    if len(result) < 3:
        return None

    # Filter out points that drifted outside the original polygon
    result = [p for p in result if _point_in_polygon(p, polygon)]

    cleaned = _clean_polygon(result)
    return cleaned if len(cleaned) >= 3 else None


# ============================================================
# Street-frontage helpers
# ============================================================
def _find_street_front_angle(polygon):
    """Return the angle (radians) of the longest edge, assumed street frontage."""
    n = len(polygon)
    max_len = 0.0
    best_angle = 0.0
    for i in range(n):
        p1 = polygon[i]
        p2 = polygon[(i + 1) % n]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = math.hypot(dx, dy)
        if length > max_len:
            max_len = length
            best_angle = math.atan2(dy, dx)
    return best_angle


def _get_split_direction(street_angle):
    """Split perpendicular to street frontage so building long axis is parallel to street."""
    return street_angle + math.pi / 2


# ============================================================
# Recursive split with street-aware orientation
# ============================================================
def _recursive_split(polygon, min_area, max_area, rng, plots, depth, street_angle):
    if depth > 10:
        plots.append(_make_plot_dict(polygon, street_angle))
        return

    area = abs(polygon_area(polygon))
    if area <= 0:
        return

    if area <= max_area * 1.3:
        plots.append(_make_plot_dict(polygon, street_angle))
        return

    # Split perpendicular to street frontage
    split_dir = _get_split_direction(street_angle)
    poly_a, poly_b = _split_polygon_by_direction(polygon, split_dir, rng.uniform(0.35, 0.65))

    if poly_a is None or poly_b is None:
        plots.append(_make_plot_dict(polygon, street_angle))
        return

    area_a = abs(polygon_area(poly_a))
    area_b = abs(polygon_area(poly_b))

    if area_a > 0 and area_b > 0:
        _recursive_split(poly_a, min_area, max_area, rng, plots, depth + 1, street_angle)
        _recursive_split(poly_b, min_area, max_area, rng, plots, depth + 1, street_angle)
    else:
        plots.append(_make_plot_dict(polygon, street_angle))


def _make_plot_dict(polygon, street_angle):
    return {
        "polygon": polygon,
        "center": polygon_centroid(polygon),
        "area": abs(polygon_area(polygon)),
        "street_front_angle": street_angle,
    }


# ============================================================
# Directional polygon split
# ============================================================
def _split_polygon_by_direction(polygon, direction_angle, pos_ratio=0.5):
    """Split polygon by a line perpendicular to direction_angle.

    All points are projected onto the direction vector;
    the split occurs at the given ratio along the projection range.
    """
    ux = math.cos(direction_angle)
    uy = math.sin(direction_angle)

    projections = [p[0] * ux + p[1] * uy for p in polygon]
    min_p = min(projections)
    max_p = max(projections)
    split_pos = min_p + (max_p - min_p) * pos_ratio

    poly_a = []
    poly_b = []
    prev_point = polygon[-1]
    prev_proj = prev_point[0] * ux + prev_point[1] * uy
    prev_side = 1 if prev_proj >= split_pos else -1

    for curr_point in polygon:
        curr_proj = curr_point[0] * ux + curr_point[1] * uy
        curr_side = 1 if curr_proj >= split_pos else -1

        if curr_side == 1:
            poly_a.append(curr_point)
        else:
            poly_b.append(curr_point)

        if curr_side != prev_side:
            denom = curr_proj - prev_proj
            if abs(denom) < 1e-9:
                t = 0.0
            else:
                t = (split_pos - prev_proj) / denom
            ix = prev_point[0] + t * (curr_point[0] - prev_point[0])
            iy = prev_point[1] + t * (curr_point[1] - prev_point[1])
            poly_a.append((ix, iy))
            poly_b.append((ix, iy))

        prev_point = curr_point
        prev_side = curr_side

    poly_a = _clean_polygon(poly_a)
    poly_b = _clean_polygon(poly_b)

    return (poly_a if len(poly_a) >= 3 else None,
            poly_b if len(poly_b) >= 3 else None)


# ============================================================
# Geometry utilities
# ============================================================
def _line_intersection(a1, a2, b1, b2):
    """Return intersection of two line segments (extended as infinite lines)."""
    x1, y1 = a1
    x2, y2 = a2
    x3, y3 = b1
    x4, y4 = b2

    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-9:
        return None

    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom
    return (px, py)


def _point_in_polygon(point, polygon):
    """Ray-casting point-in-polygon test."""
    x, y = point
    inside = False
    n = len(polygon)
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def _clean_polygon(polygon):
    """Remove duplicate / nearly-duplicate consecutive vertices."""
    if len(polygon) < 2:
        return polygon

    cleaned = [polygon[0]]
    for p in polygon[1:]:
        if _dist2(p, cleaned[-1]) > 0.001:
            cleaned.append(p)

    # Remove closing duplicate
    if len(cleaned) > 2 and _dist2(cleaned[0], cleaned[-1]) < 0.001:
        cleaned.pop()

    return cleaned


def _dist2(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
