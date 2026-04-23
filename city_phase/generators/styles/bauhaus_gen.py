"""Bauhaus style generator: orthogonal grid, free plan, flowing space."""

import random
import math
from mathutils import Vector
from ..composition import CompositionBuilder, ConnType
from ..styles import BAUHAUS_PRS


def generate(params, context=None):
    rng = random.Random(params.get("seed", 7))
    prs = BAUHAUS_PRS.copy()

    cb = CompositionBuilder()

    # --- Parameters ---
    bay = params.get("bay_width", prs["bay_width"])
    floor_h = params.get("floor_height", prs["floor_height"])
    floors = params.get("floors", max(1, int(params.get("height", 36.0) / floor_h)))
    nx = max(1, params.get("bays_x", 3))
    ny = max(1, params.get("bays_y", 2))
    openness = params.get("openness", rng.uniform(*prs["openness"]))
    glass_ratio = params.get("glass_ratio", rng.uniform(*prs["glass_ratio"]))
    flowing = params.get("flowing_space", prs["flowing_space"])

    total_w = nx * bay
    total_d = ny * bay
    total_h = floors * floor_h

    # --- Rule 1: Orthogonal grid volume ---
    main_vol = cb.place_box(total_w, total_d, total_h, pos=(0, 0, 0), rot=(0, 0, 0))

    # --- Rule 2: Free plan — inset ground floor to create pilotis ---
    ground_faces = [f for f in main_vol.faces
                    if f.is_valid and abs(f.normal.z) < 0.1 and f.calc_center_median().z < floor_h * 0.5]
    if ground_faces and openness > 0.2:
        # Create a pilotis effect: deep inset on ground floor facade
        cb.inset_faces(ground_faces, thickness=bay * openness, depth=floor_h * 0.4)

    # --- Rule 3: Flowing space — stepped slabs if enabled ---
    if flowing and floors > 2:
        # Find top faces of main volume
        top_z = max(v.co.z for v in main_vol.verts)
        top_faces = [f for f in main_vol.faces if f.is_valid and all(v.co.z >= top_z - 0.1 for v in f.verts)]
        if top_faces:
            # Create a secondary smaller volume on top
            setback = bay * rng.uniform(0.8, 1.2)
            upper_vol = cb.place_box(
                total_w - setback * 2,
                total_d - setback * 2,
                floor_h * rng.uniform(1, 2),
                pos=(0, 0, top_z)
            )
            cb.center_volume_on(main_vol, upper_vol)

    # --- Rule 4: Curtain wall — subdivide vertical faces for window grid ---
    vertical_faces = [f for f in main_vol.faces
                      if f.is_valid and abs(f.normal.z) < 0.1]

    for face in vertical_faces:
        # Only process large enough faces
        area = face.calc_area()
        if area < bay * floor_h * 0.5:
            continue
        # Determine window density based on glass_ratio
        if rng.random() < glass_ratio:
            # Create window panel by inset
            inner = cb.inset_faces([face], thickness=bay * 0.15, depth=bay * 0.08)
            if inner and rng.random() < 0.3:
                # Some windows are floor-to-ceiling (deeper inset)
                cb.inset_faces(inner, thickness=bay * 0.05, depth=bay * 0.15)

    # --- Rule 5: Proportion constraint — all dimensions should be bay multiples ---
    # This is enforced at parameter level, not geometric

    obj = cb.build(name=params.get("name", "CityP_Bauhaus"), context=context)
    return obj
