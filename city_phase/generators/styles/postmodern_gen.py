"""Postmodern style generator: historical motifs, juxtaposition, playful scale."""

import random
import math
from mathutils import Vector
from ..composition import CompositionBuilder
from ..styles import POSTMODERN_PRS


def _generate_abstracted_arch(cb, base_vol, rng):
    """Abstracted arch motif: inset on a facade creates arch-like void."""
    vertical_faces = [f for f in base_vol.faces
                      if f.is_valid and abs(f.normal.z) < 0.1]
    if not vertical_faces:
        return
    face = rng.choice(vertical_faces)
    # Deep rounded inset to suggest arch
    inner = cb.inset_faces([face], thickness=2.0, depth=1.5)
    if inner:
        cb.inset_faces(inner, thickness=0.5, depth=0.5)


def _generate_abstracted_column_grid(cb, base_vol, rng):
    """Abstracted column grid: vertical extrusions on facade."""
    vertical_faces = [f for f in base_vol.faces
                      if f.is_valid and abs(f.normal.z) < 0.1]
    for face in vertical_faces:
        if rng.random() < 0.3:
            # Small vertical extrusions
            cb.extrude_faces([face], distance=rng.uniform(0.5, 1.5), taper=0.1)


def _generate_abstracted_pediment(cb, base_vol, rng):
    """Abstracted pediment: triangular top extrusion."""
    top_z = max(v.co.z for v in base_vol.verts)
    top_faces = [f for f in base_vol.faces
                 if f.is_valid and all(v.co.z >= top_z - 0.1 for v in f.verts)]
    if top_faces:
        # Extrude top then taper to create pediment feel
        new_faces = cb.extrude_faces(top_faces, distance=rng.uniform(2, 5), taper=0.5)


def generate(params, context=None):
    rng = random.Random(params.get("seed", 7))
    prs = POSTMODERN_PRS.copy()

    cb = CompositionBuilder()

    n_motifs = params.get("n_motifs", rng.randint(*prs["n_motifs"]))
    n_zones = params.get("n_zones", rng.randint(*prs["n_zones"]))
    exaggeration = rng.uniform(*prs["exaggeration"])

    # --- Base volume ---
    base_w = params.get("base_w", 24)
    base_d = params.get("base_d", 18)
    base_h = params.get("height", 40)
    main_vol = cb.place_box(base_w, base_d, base_h, pos=(0, 0, 0))

    # --- Rule 1: Historical motifs ---
    MOTIFS = {
        "arch": _generate_abstracted_arch,
        "column": _generate_abstracted_column_grid,
        "pediment": _generate_abstracted_pediment,
    }

    chosen = random.sample(list(MOTIFS.keys()), k=min(n_motifs, len(MOTIFS)))
    for motif in chosen:
        MOTIFS[motif](cb, main_vol, rng)

    # --- Rule 2: Facade zones with contradictory styles ---
    vertical_faces = [f for f in main_vol.faces
                      if f.is_valid and abs(f.normal.z) < 0.1]

    if vertical_faces and n_zones > 1:
        # Split faces into zones by height
        faces_by_zone = [[] for _ in range(n_zones)]
        for face in vertical_faces:
            z = face.calc_center_median().z
            zone_idx = min(int(z / base_h * n_zones), n_zones - 1)
            faces_by_zone[zone_idx].append(face)

        styles = ["grid", "strip", "arch", "plain"]
        for zone_faces in faces_by_zone:
            style = rng.choice(styles)
            if style == "grid":
                for f in zone_faces:
                    cb.inset_faces([f], thickness=1.0, depth=0.3)
            elif style == "strip":
                for f in zone_faces:
                    cb.extrude_faces([f], distance=0.5)
            elif style == "arch":
                if zone_faces:
                    _generate_abstracted_arch(cb, main_vol, rng)
            # plain: do nothing

    # --- Rule 5: Gigantic element ---
    if rng.random() < prs["gigantic_element_probability"]:
        # Scale up one motif to building scale
        giant = cb.place_box(base_w * 0.5, base_d * 0.5, base_h * exaggeration,
                             pos=(base_w * 0.3, base_d * 0.3, 0))

    obj = cb.build(name=params.get("name", "CityP_Postmodern"), context=context)
    return obj
