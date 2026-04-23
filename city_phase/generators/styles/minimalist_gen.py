"""Minimalist style generator: pure geometry, wall protagonist, light cutting."""

import random
import math
from mathutils import Vector
from ..composition import CompositionBuilder
from ..styles import MINIMALIST_PRS


def generate(params, context=None):
    rng = random.Random(params.get("seed", 7))
    prs = MINIMALIST_PRS.copy()

    cb = CompositionBuilder()

    module = params.get("module", prs["module"])
    w_mod = max(1, params.get("w_mod", rng.randint(2, 5)))
    d_mod = max(1, params.get("d_mod", rng.randint(2, 4)))
    h_mod = max(1, params.get("h_mod", rng.randint(2, 6)))
    n_walls = params.get("n_walls", rng.randint(*prs["wall_count"]))
    wall_h_ratio = rng.uniform(*prs["wall_height_ratio"])

    total_w = module * w_mod
    total_d = module * d_mod
    total_h = module * h_mod

    # --- Rule 1: Pure geometric box ---
    main_vol = cb.place_box(total_w, total_d, total_h, pos=(0, 0, 0), rot=(0, 0, 0))

    # --- Rule 2: Wall protagonist — independent walls around the main volume ---
    for i in range(n_walls):
        wall_w = module * rng.uniform(2, 6)
        wall_h = total_h * wall_h_ratio
        wall_t = module * 0.1  # thin wall

        # Position wall outside main volume
        angle = (2 * math.pi * i) / n_walls + rng.uniform(-0.2, 0.2)
        dist = max(total_w, total_d) * 0.6 + rng.uniform(2, 8)
        wx = math.cos(angle) * dist
        wy = math.sin(angle) * dist

        wall = cb.place_box(wall_w, wall_t, wall_h, pos=(wx, wy, 0))
        # Slight tilt for poetic effect
        cb.offset_volume(wall, Vector((0, 0, 0)), 0)  # just to log

    # --- Rule 3: Light cutting — horizontal slits at specific levels ---
    n_slits = rng.randint(*prs["slit_levels"])
    vertical_faces = [f for f in main_vol.faces
                      if f.is_valid and abs(f.normal.z) < 0.1]

    for level in range(1, n_slits + 1):
        z_level = total_h * (level / (n_slits + 1))
        # Find faces near this level
        for face in vertical_faces:
            fz = face.calc_center_median().z
            if abs(fz - z_level) < total_h * 0.05:
                # Very narrow horizontal slit
                cb.inset_faces([face], thickness=module * 0.4, depth=module * 0.05)

    # --- Rule 4: Skylight — inset on top face ---
    if prs["skylight"] and rng.random() < 0.6:
        top_z = max(v.co.z for v in main_vol.verts)
        top_faces = [f for f in main_vol.faces
                     if f.is_valid and all(v.co.z >= top_z - 0.1 for v in f.verts)]
        if top_faces:
            cb.inset_faces(top_faces, thickness=module * 0.3, depth=module * 0.15)

    obj = cb.build(name=params.get("name", "CityP_Minimalist"), context=context)
    return obj
