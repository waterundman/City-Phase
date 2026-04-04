import random
from ..utils.geo_utils import polygon_area


def split_block_into_plots(block_polygon, setback, min_area, max_area, seed, density=1.0):
    rng = random.Random(seed)

    inset_polygon = _inset_polygon(block_polygon, setback)
    if inset_polygon is None or abs(polygon_area(inset_polygon)) < min_area:
        return []

    plots = []
    _recursive_split(inset_polygon, min_area, max_area, rng, plots, depth=0)

    if density < 1.0:
        plots = [p for p in plots if rng.random() < density]

    return plots


def _inset_polygon(polygon, distance):
    if len(polygon) < 3:
        return None

    cx = sum(p[0] for p in polygon) / len(polygon)
    cy = sum(p[1] for p in polygon) / len(polygon)

    inset = []
    for px, py in polygon:
        dx = px - cx
        dy = py - cy
        dist = (dx * dx + dy * dy) ** 0.5
        if dist < distance:
            inset.append((cx, cy))
        else:
            scale = (dist - distance) / dist
            inset.append((cx + dx * scale, cy + dy * scale))

    return inset


def _recursive_split(polygon, min_area, max_area, rng, plots, depth):
    if depth > 10:
        plots.append(polygon)
        return

    area = abs(polygon_area(polygon))
    if area <= 0:
        return

    if area <= max_area * 1.3:
        plots.append(polygon)
        return

    split_axis = 0 if rng.random() < 0.5 else 1

    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]

    if split_axis == 0:
        min_val, max_val = min(xs), max(xs)
    else:
        min_val, max_val = min(ys), max(ys)

    split_pos = min_val + (max_val - min_val) * rng.uniform(0.3, 0.7)

    poly_a, poly_b = _split_polygon_by_line(polygon, split_axis, split_pos)

    if poly_a is None or poly_b is None:
        plots.append(polygon)
        return

    area_a = abs(polygon_area(poly_a))
    area_b = abs(polygon_area(poly_b))

    if area_a > 0 and area_b > 0:
        _recursive_split(poly_a, min_area, max_area, rng, plots, depth + 1)
        _recursive_split(poly_b, min_area, max_area, rng, plots, depth + 1)
    else:
        plots.append(polygon)


def _split_polygon_by_line(polygon, axis, pos):
    poly_a = []
    poly_b = []
    prev_point = polygon[-1]
    prev_side = 1 if prev_point[axis] >= pos else -1

    for curr_point in polygon:
        curr_side = 1 if curr_point[axis] >= pos else -1

        if curr_side == 1:
            poly_a.append(curr_point)
        else:
            poly_b.append(curr_point)

        if curr_side != prev_side:
            t = (pos - prev_point[axis]) / (curr_point[axis] - prev_point[axis]) if curr_point[axis] != prev_point[axis] else 0
            ix = prev_point[0] + t * (curr_point[0] - prev_point[0])
            iy = prev_point[1] + t * (curr_point[1] - prev_point[1])
            if curr_side == 1:
                poly_a.append((ix, iy))
                poly_b.append((ix, iy))
            else:
                poly_a.append((ix, iy))
                poly_b.append((ix, iy))

        prev_point = curr_point
        prev_side = curr_side

    return (poly_a if len(poly_a) >= 3 else None,
            poly_b if len(poly_b) >= 3 else None)
