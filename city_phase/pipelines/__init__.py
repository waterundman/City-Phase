from . import arch_white
from . import golden_hour
from . import neon_rain
from . import iso_clear

PIPELINES = {
    "arch_white": {
        "name": "Arch White",
        "name_zh": "建筑白膜",
        "apply": arch_white.apply,
    },
    "golden_hour": {
        "name": "Golden Hour",
        "name_zh": "黄昏金切",
        "apply": golden_hour.apply,
    },
    "neon_rain": {
        "name": "Neon Rain",
        "name_zh": "霓虹雨夜",
        "apply": neon_rain.apply,
    },
    "iso_clear": {
        "name": "Iso Clear",
        "name_zh": "等轴晴空",
        "apply": iso_clear.apply,
    },
}
