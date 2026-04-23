"""
Parametric Rule Sets (PRS) for architectural styles.
Each style is defined as a dictionary of constrained parameters.
"""

BAUHAUS_PRS = {
    "style_name": "Bauhaus",
    "volume_count": (1, 2),
    "rotation_range_deg": (-5.0, 5.0),
    "inset_depth_ratio": (0.05, 0.1),
    "extrude_amplitude": (0.0, 0.5),
    "color_palette": ["white", "grey", "black", "glass"],
    "proportion_constraint": "modular_grid",
    "symmetry": "bilateral",
    "dominant_element": None,
    "bay_width": 5.4,
    "floor_height": 3.6,
    "glass_ratio": (0.3, 0.6),
    "openness": (0.2, 0.4),
    "flowing_space": False,
}

CONSTRUCTIVIST_PRS = {
    "style_name": "Constructivism",
    "volume_count": (2, 5),
    "rotation_range_deg": (-45.0, 45.0),
    "inset_depth_ratio": (0.1, 0.3),
    "extrude_amplitude": (2.0, 8.0),
    "color_palette": ["red", "blue", "yellow", "concrete"],
    "proportion_constraint": "dynamic_diagonal",
    "symmetry": "asymmetric",
    "dominant_element": "bridge_or_cantilever",
    "bridge_probability": 0.6,
    "cantilever_ratio": (0.2, 0.5),
}

MINIMALIST_PRS = {
    "style_name": "Minimalism",
    "volume_count": (1, 2),
    "rotation_range_deg": (0.0, 0.0),
    "inset_depth_ratio": (0.02, 0.08),
    "extrude_amplitude": (0.0, 0.2),
    "color_palette": ["concrete", "white_stucco", "wood"],
    "proportion_constraint": "golden_or_integer_ratio",
    "symmetry": "bilateral_or_radial",
    "dominant_element": "wall_slit",
    "wall_count": (2, 5),
    "wall_height_ratio": (1.2, 1.8),
    "slit_levels": (3, 6),
    "skylight": True,
    "module": 3.6,
}

POSTMODERN_PRS = {
    "style_name": "Postmodern",
    "volume_count": (1, 3),
    "rotation_range_deg": (-15.0, 15.0),
    "inset_depth_ratio": (0.1, 0.4),
    "extrude_amplitude": (0.5, 3.0),
    "color_palette": ["pastel_pink", "mint_green", "sky_blue", "terracotta"],
    "proportion_constraint": "playful_scale",
    "symmetry": "intentionally_broken",
    "dominant_element": "historical_motif",
    "n_motifs": (1, 3),
    "n_zones": (2, 4),
    "exaggeration": (1.2, 2.0),
    "gigantic_element_probability": 0.3,
}

BRUTALIST_PRS = {
    "style_name": "Brutalism",
    "volume_count": (1, 3),
    "rotation_range_deg": (-10.0, 10.0),
    "inset_depth_ratio": (0.3, 0.8),
    "extrude_amplitude": (1.0, 5.0),
    "color_palette": ["raw_concrete", "board_concrete"],
    "proportion_constraint": "monumental",
    "symmetry": "asymmetric_but_axial",
    "dominant_element": "hero_volume",
    "hero_volume_ratio": (0.5, 0.8),
    "surface_roughness": (0.8, 1.0),
    "deep_recess": True,
}


ALL_STYLES = {
    "bauhaus": BAUHAUS_PRS,
    "constructivist": CONSTRUCTIVIST_PRS,
    "minimalist": MINIMALIST_PRS,
    "postmodern": POSTMODERN_PRS,
    "brutalist": BRUTALIST_PRS,
}


def get_prs(style_key):
    """Get the PRS for a given style key."""
    return ALL_STYLES.get(style_key, BAUHAUS_PRS)
