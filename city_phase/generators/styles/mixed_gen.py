"""Mixed style generator: interpolate between two style PRS."""

import random
import math
from mathutils import Vector
from ..composition import CompositionBuilder, ConnType
from ..styles import interpolate_prs


def generate(params, context=None):
    rng = random.Random(params.get("seed", 7))

    style_a = params.get("style_a", "bauhaus")
    style_b = params.get("style_b", "constructivist")
    blend = params.get("blend_ratio", 0.5)

    prs = interpolate_prs(style_a, style_b, blend)

    cb = CompositionBuilder()

    # --- Extract interpolated parameters ---
    n_volumes = int(_lerp_range(prs["volume_count"], rng))
    rot_range = math.radians(_lerp_range(prs.get("rotation_range_deg", (0, 0)), rng))
    inset_ratio = _lerp_range(prs.get("inset_depth_ratio", (0.1, 0.3)), rng)
    extrude_amp = _lerp_range(prs.get("extrude_amplitude", (0.5, 2.0)), rng)

    base_w = params.get("base_w", 24)
    base_d = params.get("base_d", 18)
    base_h = params.get("height", 40)

    volumes = []

    # --- Generate volumes with blended characteristics ---
    for i in range(n_volumes):
        w = base_w * rng.uniform(0.4, 1.0)
        d = base_d * rng.uniform(0.4, 1.0)
        h = base_h * rng.uniform(0.5, 1.0)

        angle = rng.uniform(-rot_range, rot_range)
        offset_x = rng.uniform(-base_w * 0.3, base_w * 0.3)
        offset_y = rng.uniform(-base_d * 0.3, base_d * 0.3)

        vol = cb.place_box(w, d, h, pos=(offset_x, offset_y, 0), rot=(0, 0, angle))
        volumes.append(vol)

    # --- Merge ---
    if len(volumes) > 1:
        merged = volumes[0]
        for vol in volumes[1:]:
            merged = cb.boolean_union(merged, vol)

    # --- Apply blended surface operations ---
    for vol in volumes:
        vertical_faces = [f for f in vol.faces
                          if f.is_valid and abs(f.normal.z) < 0.1]

        # Blend of inset (from style A tendency) and extrude (from style B tendency)
        for face in vertical_faces:
            r = rng.random()
            if r < blend * 0.6:
                # More style B: bold extrusions
                cb.extrude_faces([face], distance=extrude_amp * rng.uniform(0.5, 1.5), taper=0.2)
            elif r < 0.5:
                # More style A: controlled insets
                cb.inset_faces([face], thickness=2.0, depth=base_w * inset_ratio)

    obj = cb.build(name=params.get("name", "CityP_Mixed"), context=context)
    return obj


def _lerp_range(rng_tuple, rng):
    """Pick a random value within a (min, max) tuple."""
    if isinstance(rng_tuple, (tuple, list)) and len(rng_tuple) >= 2:
        return rng.uniform(rng_tuple[0], rng_tuple[1])
    return float(rng_tuple)
