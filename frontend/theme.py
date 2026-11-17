"""Connect custom product styles to Streamlit's native appearance preference.

The framework owns System/Light/Dark, persistence, native controls and charts.
This inline v2 component observes its documented theme CSS properties so custom
HTML updates immediately, without a Python rerun or a second preference store.
"""
from pathlib import Path

import streamlit as st

_adapter = st.components.v2.component(
    "fraud_theme_adapter",
    html='<span class="theme-probe" aria-hidden="true"></span>',
    css=".theme-probe { display: none; color: var(--st-background-color); }",
    js=(Path(__file__).resolve().parent / "assets/theme.js").read_text(),
    isolate_styles=False,
)


def apply_theme() -> None:
    """Mount one invisible, session-independent native-theme adapter."""
    _adapter(key="theme_adapter", height=1)
