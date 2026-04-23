"""Design Intent Parser — natural language to architectural style mapping."""

import re

# Keyword → {style: weight} mapping
KEYWORD_MAP = {
    # Bauhaus keywords
    "grid": {"bauhaus": 1.0},
    "orthogonal": {"bauhaus": 1.0, "minimalist": 0.5},
    "modular": {"bauhaus": 1.0},
    "functional": {"bauhaus": 0.8, "minimalist": 0.6},
    "flowing": {"bauhaus": 0.7, "minimalist": 0.4},
    "glass": {"bauhaus": 0.8, "minimalist": 0.6},
    "transparent": {"bauhaus": 0.6, "minimalist": 0.8},
    "clean": {"bauhaus": 0.7, "minimalist": 0.9},
    "rational": {"bauhaus": 1.0},

    # Constructivist keywords
    "dynamic": {"constructivist": 1.0, "brutalist": 0.4},
    "diagonal": {"constructivist": 1.0},
    "intersecting": {"constructivist": 1.0},
    "cantilever": {"constructivist": 1.0, "brutalist": 0.5},
    "floating": {"constructivist": 0.8},
    "light": {"constructivist": 0.7, "minimalist": 0.6},
    "airy": {"constructivist": 0.8, "minimalist": 0.7},
    "suspended": {"constructivist": 0.9},
    "tension": {"constructivist": 0.8},

    # Minimalist keywords
    "pure": {"minimalist": 1.0},
    "simple": {"minimalist": 1.0, "bauhaus": 0.5},
    "zen": {"minimalist": 1.0},
    "quiet": {"minimalist": 0.9},
    "subtle": {"minimalist": 0.8},
    "restrained": {"minimalist": 1.0},
    "essence": {"minimalist": 1.0},
    "void": {"minimalist": 0.9},
    "silence": {"minimalist": 0.8},

    # Postmodern keywords
    "playful": {"postmodern": 1.0},
    "colorful": {"postmodern": 1.0},
    "whimsical": {"postmodern": 1.0},
    "eclectic": {"postmodern": 0.9},
    "ironic": {"postmodern": 0.8},
    "historical": {"postmodern": 0.9},
    "ornament": {"postmodern": 0.8},
    "fun": {"postmodern": 1.0},
    "vibrant": {"postmodern": 0.9},

    # Brutalist keywords
    "heavy": {"brutalist": 1.0},
    "massive": {"brutalist": 1.0, "constructivist": 0.3},
    "monumental": {"brutalist": 1.0},
    "raw": {"brutalist": 1.0},
    "concrete": {"brutalist": 1.0, "minimalist": 0.4},
    "rough": {"brutalist": 0.9},
    "powerful": {"brutalist": 0.9, "constructivist": 0.5},
    "solid": {"brutalist": 1.0},
    "imposing": {"brutalist": 0.9},
    "heroic": {"brutalist": 0.8},
}

STYLE_ALIASES = {
    "bauhaus": ["bauhaus", "gropius", "mies", "modernist", "functionalism"],
    "constructivist": ["constructivist", "constructivism", "lissitzky", "melnikov", "avant-garde"],
    "minimalist": ["minimalist", "minimalism", "ando", "zen", "less is more", "purity"],
    "postmodern": ["postmodern", "postmodernism", "venturi", "graves", "playful", "colorful"],
    "brutalist": ["brutalist", "brutalism", "smithson", "rudolph", "raw concrete", "heroic"],
}


def parse_intent(text):
    """Parse a natural language design intent into style recommendations.

    Returns:
        dict: {
            "primary": str,      # top style key
            "secondary": str,    # second style key
            "blend": float,      # 0.0-1.0, how much secondary vs primary
            "confidence": float, # 0.0-1.0
            "matched_keywords": [str],
        }
    """
    text_lower = text.lower()
    # Tokenize: split on non-alphabetic characters
    tokens = re.findall(r"[a-z]+", text_lower)

    scores = {
        "bauhaus": 0.0,
        "constructivist": 0.0,
        "minimalist": 0.0,
        "postmodern": 0.0,
        "brutalist": 0.0,
    }
    matched = []

    # Match keywords
    for keyword, weights in KEYWORD_MAP.items():
        if keyword in text_lower or any(keyword in t for t in tokens):
            for style, weight in weights.items():
                scores[style] += weight
            matched.append(keyword)

    # Match style aliases
    for style_key, aliases in STYLE_ALIASES.items():
        for alias in aliases:
            if alias in text_lower:
                scores[style_key] += 2.0  # Direct style mention gets high weight
                matched.append(alias)

    if not matched:
        return {
            "primary": "bauhaus",
            "secondary": "minimalist",
            "blend": 0.5,
            "confidence": 0.0,
            "matched_keywords": [],
        }

    # Sort by score
    sorted_styles = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    primary = sorted_styles[0][0]
    secondary = sorted_styles[1][0] if len(sorted_styles) > 1 else primary

    total_top2 = sorted_styles[0][1] + sorted_styles[1][1]
    blend = sorted_styles[1][1] / total_top2 if total_top2 > 0 else 0.5

    # Confidence based on how much the top score dominates
    all_scores = list(scores.values())
    max_score = max(all_scores)
    sum_scores = sum(all_scores)
    confidence = max_score / sum_scores if sum_scores > 0 else 0.0

    return {
        "primary": primary,
        "secondary": secondary,
        "blend": round(blend, 2),
        "confidence": round(confidence, 2),
        "matched_keywords": matched,
    }


def apply_intent_to_props(props, intent_result):
    """Apply parsed intent to Blender property group."""
    props.typology = "mixed"
    props.style_a = intent_result["primary"]
    props.style_b = intent_result["secondary"]
    props.blend_ratio = intent_result["blend"]
