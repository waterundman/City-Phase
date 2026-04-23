import math
import random
from ..utils import typology_classifier


def assign_heights(plots, city_center, avg_floors, floor_variance, seed, use_bimodal=True):
    rng = random.Random(seed)

    noise_field = _generate_noise_field(plots, seed)

    max_height = avg_floors * 3.0
    min_height = 4.0

    building_specs = []
    for idx, plot in enumerate(plots):
        cx, cy = plot["center"]
        dist = ((cx - city_center[0]) ** 2 + (cy - city_center[1]) ** 2) ** 0.5

        dist_ratio = min(dist / 800.0, 1.0)

        if use_bimodal:
            base_height = _bimodal_height(dist_ratio, max_height, min_height)
        else:
            base_height = _lerp(max_height, min_height, dist_ratio)

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
