import math
import random
from ..utils import typology_classifier


def assign_heights(
    plots,
    city_center,
    avg_floors,
    floor_variance,
    seed,
    use_bimodal=True,
    height_mode="radial",
    corridor_angle=0.0,
    corridor_width=250.0,
    metro_peak=False,
    metro_intensity=1.0,
    waterfront_premium=False,
    waterfront_dir=0.0,
    waterfront_dist=200.0,
):
    rng = random.Random(seed)

    noise_field = _generate_noise_field(plots, seed)

    max_height = avg_floors * 3.0
    min_height = 4.0

    # Pre-generate metro stations for procedural mode
    metro_stations = []
    if metro_peak and height_mode != "osm":
        n_stations = max(1, int(len(plots) / 80))
        angle_rad = math.radians(corridor_angle)
        for i in range(n_stations):
            t = rng.uniform(-0.8, 0.8)
            r = rng.uniform(0, 400)
            # Place along corridor axis with some spread
            mx = city_center[0] + math.cos(angle_rad) * t * r
            my = city_center[1] + math.sin(angle_rad) * t * r
            metro_stations.append((mx, my))

    # Waterfront line: a straight line at waterfront_dir, waterfront_dist from center
    wf_line = None
    if waterfront_premium and height_mode != "osm":
        wf_angle = math.radians(waterfront_dir)
        # Two points on the line
        dx = math.cos(wf_angle + math.pi / 2)
        dy = math.sin(wf_angle + math.pi / 2)
        ox = city_center[0] + math.cos(wf_angle) * waterfront_dist
        oy = city_center[1] + math.sin(wf_angle) * waterfront_dist
        wf_line = ((ox - dx * 2000, oy - dy * 2000), (ox + dx * 2000, oy + dy * 2000))

    building_specs = []
    for idx, plot in enumerate(plots):
        cx, cy = plot["center"]
        dist = ((cx - city_center[0]) ** 2 + (cy - city_center[1]) ** 2) ** 0.5
        dist_ratio = min(dist / 800.0, 1.0)

        if height_mode == "corridor":
            base_height = _corridor_height(
                cx, cy, city_center, corridor_angle, corridor_width, max_height, min_height
            )
        elif use_bimodal:
            base_height = _bimodal_height(dist_ratio, max_height, min_height)
        else:
            base_height = _lerp(max_height, min_height, dist_ratio)

        # Metro peak
        if metro_peak and metro_stations:
            base_height = _apply_metro_peak(cx, cy, base_height, max_height, metro_stations, metro_intensity)

        # Waterfront premium
        if waterfront_premium and wf_line:
            base_height = _apply_waterfront_premium(cx, cy, base_height, max_height, wf_line)

        noise = noise_field.get(idx, 0.0)
        height = base_height + noise * floor_variance * 3.0
        height = max(height, 3.0)

        typology = typology_classifier.classify_typology(
            area=plot["area"],
            height=height,
            dist_ratio=dist_ratio,
            rng=rng,
        )

        building_specs.append({
            "plot": plot["polygon"],
            "center": plot["center"],
            "area": plot["area"],
            "height": height,
            "typology": typology,
            "dist_ratio": dist_ratio,
            "street_front_angle": plot.get("street_front_angle", 0.0),
        })

    return building_specs


def _lerp(a, b, t):
    return a * (1 - t) + b * t


def _bimodal_height(dist_ratio, max_height, min_height, cbd_weight=0.7, sub_center_dist=0.5):
    cbd_height = _lerp(max_height, min_height, dist_ratio)
    sub_dist = abs(dist_ratio - sub_center_dist) * 2.0
    sub_dist = min(sub_dist, 1.0)
    sub_height = _lerp(max_height * 0.6, min_height, sub_dist)
    return cbd_height * cbd_weight + sub_height * (1 - cbd_weight)


def _corridor_height(cx, cy, city_center, angle_deg, width, max_height, min_height):
    angle = math.radians(angle_deg)
    dx = cx - city_center[0]
    dy = cy - city_center[1]
    # Project point onto corridor axis
    proj = dx * math.cos(angle) + dy * math.sin(angle)
    # Perpendicular distance from axis
    perp = abs(-dx * math.sin(angle) + dy * math.cos(angle))
    # Height along axis: peak at center, decay with |proj|
    axis_dist = abs(proj) / 800.0
    axis_height = _lerp(max_height, min_height, min(axis_dist, 1.0))
    # Perpendicular decay
    perp_ratio = min(perp / (width * 0.5), 1.0)
    return _lerp(axis_height, min_height, perp_ratio)


def _apply_metro_peak(cx, cy, base_height, max_height, stations, intensity):
    bonus = 0.0
    for sx, sy in stations:
        d = math.hypot(cx - sx, cy - sy)
        if d < 150.0:
            peak = max_height * 0.4 * intensity * max(0, 1 - d / 150.0)
            bonus = max(bonus, peak)
    return base_height + bonus


def _apply_waterfront_premium(cx, cy, base_height, max_height, line):
    (x1, y1), (x2, y2) = line
    # Distance from point to line segment (infinite line approximation is fine here)
    num = abs((y2 - y1) * cx - (x2 - x1) * cy + x2 * y1 - y2 * x1)
    den = math.hypot(y2 - y1, x2 - x1)
    d = num / den if den > 0 else 9999.0
    if d < 300.0:
        bonus = max_height * 0.25 * max(0, 1 - d / 300.0)
        return base_height + bonus
    return base_height


def _build_grid(plots, cell_size=100.0):
    grid = {}
    for idx, plot in enumerate(plots):
        cx, cy = plot["center"]
        gx, gy = int(cx // cell_size), int(cy // cell_size)
        grid.setdefault((gx, gy), []).append(idx)
    return grid


def _generate_noise_field(plots, seed):
    rng = random.Random(seed + 42)

    noise = {}
    for idx in range(len(plots)):
        noise[idx] = rng.gauss(0, 1)

    grid = _build_grid(plots, cell_size=100.0)

    for _ in range(3):
        smoothed = {}
        for idx in range(len(plots)):
            neighbors = _find_neighbors_grid(idx, plots, grid, radius=100.0)
            if neighbors:
                val = noise[idx] * 0.5 + sum(noise[n] for n in neighbors) / len(neighbors) * 0.5
            else:
                val = noise[idx]
            smoothed[idx] = val
        noise = smoothed

    return noise


def _find_neighbors_grid(idx, plots, grid, radius):
    cx, cy = plots[idx]["center"]
    cell_size = radius
    gx, gy = int(cx // cell_size), int(cy // cell_size)
    neighbors = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for j in grid.get((gx + dx, gy + dy), []):
                if j == idx:
                    continue
                ox, oy = plots[j]["center"]
                if ((cx - ox) ** 2 + (cy - oy) ** 2) ** 0.5 < radius:
                    neighbors.append(j)
    return neighbors
