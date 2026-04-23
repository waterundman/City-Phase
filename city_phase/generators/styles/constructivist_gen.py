"""Constructivist style generator: intersecting volumes, diagonal dynamics, asymmetry."""

import random
import math
from mathutils import Vector
from ..composition import CompositionBuilder, ConnType
from ..styles import CONSTRUCTIVIST_PRS


def generate(params, context=None):
    rng = random.Random(params.get("seed", 7))
    prs = CONSTRUCTIVIST_PRS.copy()

    cb = CompositionBuilder()

    n_volumes = params.get("n_volumes", rng.randint(*prs["volume_count"]))
    rotation_range = math.radians(params.get("rotation_range", rng.uniform(*prs["rotation_range_deg"])))

    volumes = []

    # --- Rule 1: Generate 2-5 volumes with random rotation and offset ---
    for i in range(n_volumes):
        w = rng.uniform(10, 30)
        d = rng.uniform(10, 30)
        h = rng.uniform(15, max(20, params.get("height", 80)))

        angle = rng.uniform(-rotation_range, rotation_range)
        offset_x = rng.uniform(-20, 20)
        offset_y = rng.uniform(-20, 20)

        vol = cb.place_box(w, d, h, pos=(offset_x, offset_y, 0), rot=(0, 0, angle))
        volumes.append(vol)

    # --- Rule 2: Boolean union (logical merge) ---
    if len(volumes) > 1:
        merged = volumes[0]
        for vol in volumes[1:]:
            merged = cb.boolean_union(merged, vol)

    # --- Rule 3: Diagonal bridges between volumes ---
    if len(volumes) >= 2 and rng.random() < prs["bridge_probability"]:
        for i in range(len(volumes) - 1):
            bridge = cb.connect_volumes(volumes[i], volumes[i + 1], ConnType.BRIDGE)

    # --- Rule 4: Asymmetric balance — one dominant cantilever ---
    if volumes and rng.random() < 0.5:
        hero = rng.choice(volumes)
        # Find a vertical face to cantilever from
        vfaces = [f for f in hero.faces if f.is_valid and abs(f.normal.z) < 0.1]
        if vfaces:
            face = rng.choice(vfaces)
            cantilever_len = rng.uniform(*prs["cantilever_ratio"]) * 20
            # Extrude outward for cantilever effect
            cb.extrude_faces([face], distance=cantilever_len, taper=0.2)

    # --- Rule 5: Color/material marking (material index assignment) ---
    colors = prs["color_palette"]
    for i, vol in enumerate(volumes):
        mat_idx = i % len(colors)
        cb.set_face_material(vol.faces, mat_idx)

    obj = cb.build(name=params.get("name", "CityP_Constructivist"), context=context)
    return obj
