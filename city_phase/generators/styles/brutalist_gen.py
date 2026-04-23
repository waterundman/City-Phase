"""Brutalist style generator: monumental scale, sculptural facade, raw concrete."""

import random
import math
from mathutils import Vector
from ..composition import CompositionBuilder
from ..styles import BRUTALIST_PRS


def generate(params, context=None):
    rng = random.Random(params.get("seed", 7))
    prs = BRUTALIST_PRS.copy()

    cb = CompositionBuilder()

    n_volumes = rng.randint(*prs["volume_count"])
    hero_ratio = rng.uniform(*prs["hero_volume_ratio"])

    volumes = []

    # --- Rule 1 & 5: Hero volume + asymmetric satellites ---
    hero_w = params.get("base_w", 30)
    hero_d = params.get("base_d", 25)
    hero_h = params.get("height", 60)

    hero_vol = cb.place_box(hero_w, hero_d, hero_h, pos=(0, 0, 0))
    volumes.append(hero_vol)

    # Satellite volumes
    for i in range(n_volumes - 1):
        sat_w = hero_w * rng.uniform(0.2, 0.5)
        sat_d = hero_d * rng.uniform(0.2, 0.5)
        sat_h = hero_h * rng.uniform(0.3, 0.8)

        angle = rng.uniform(-0.5, 0.5)
        dist = hero_w * rng.uniform(0.4, 0.8)
        sx = math.cos(angle) * dist
        sy = math.sin(angle) * dist

        sat = cb.place_box(sat_w, sat_d, sat_h, pos=(sx, sy, 0))
        volumes.append(sat)

    # --- Rule 2: Sculptural facade — deep inset/extrude on hero ---
    vertical_faces = [f for f in hero_vol.faces
                      if f.is_valid and abs(f.normal.z) < 0.1]

    # Deep recesses (Rule 4: dramatic light)
    for face in vertical_faces:
        if rng.random() < 0.4:
            depth = rng.uniform(2.0, 4.0)
            cb.inset_faces([face], thickness=2.5, depth=depth)

    # Bold extrusions
    for face in vertical_faces:
        if rng.random() < 0.2:
            cb.extrude_faces([face], distance=rng.uniform(1.0, 3.0))

    # --- Rule 3: Raw concrete texture hint via surface subdivision ---
    for face in vertical_faces:
        if rng.random() < 0.3 and len(face.verts) == 4:
            cb.subdivide_face(face, cuts_u=2, cuts_v=2)

    # --- Material assignment ---
    cb.set_face_material(hero_vol.faces, 0)  # raw concrete

    obj = cb.build(name=params.get("name", "CityP_Brutalist"), context=context)
    return obj
