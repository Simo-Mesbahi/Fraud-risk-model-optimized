"""Guard contrast and native/custom palette consistency in both appearances."""
from pathlib import Path
import re
import tomllib

import pytest

from frontend.styles import CUSTOM_CSS

ROOT = Path(__file__).resolve().parents[2]
CONFIG = tomllib.loads((ROOT / ".streamlit/config.toml").read_text())["theme"]


def contrast(first, second):
    def luminance(color):
        channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        linear = [x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in channels]
        return sum(x * w for x, w in zip(linear, (.2126, .7152, .0722)))
    low, high = sorted((luminance(first), luminance(second)))
    return (high + .05) / (low + .05)


@pytest.mark.parametrize("mode", ["light", "dark"])
def test_both_palettes_are_legible_and_match_native_widgets(mode):
    selector = ":root {" if mode == "dark" else ':root[data-fraud-theme="light"] {'
    block = CUSTOM_CSS.split(selector, 1)[1].split("}", 1)[0]
    tokens = dict(re.findall(r"--([\w-]+):\s*(#[\da-fA-F]{6})", block))
    assert CONFIG[mode]["backgroundColor"] == tokens["bg-main"]
    assert CONFIG[mode]["textColor"] == tokens["text-primary"]
    for text in ("text-primary", "text-secondary", "text-muted", "primary-text",
                 "success", "warning", "high", "critical"):
        for surface in ("bg-main", "card-bg", "input-bg"):
            assert contrast(tokens[text], tokens[surface]) >= 4.5, (mode, text, surface)
    assert contrast("#FFFFFF", CONFIG[mode]["primaryColor"]) >= 4.5
    for color in CONFIG[mode]["chartCategoricalColors"]:
        assert contrast(color, tokens["bg-main"]) >= 3
