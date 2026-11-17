from __future__ import annotations

import html
import os
import logging
import uuid

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Final

import streamlit as st

from frontend.api_client import (
    FraudAPIClient,
)

from frontend.components import (
    status_badge,
)

from frontend.styles import (
    CUSTOM_CSS,
)

from frontend.utils.state import (
    initialize_state,
)

from frontend.views.claim_analysis import (
    render as render_claim_analysis,
)

from frontend.views.investigation_queue import (
    render as render_investigation_queue,
)

from frontend.views.model_insights import (
    render as render_model_insights,
)

from frontend.views.overview import (
    render as render_overview,
)

from frontend.views.portfolio_scoring import (
    render as render_portfolio_scoring,
)

from frontend.views.data_science import render as render_data_science

from frontend.views.system_status import (
    render as render_system_status,
)


# =============================================================================
# Product configuration
# =============================================================================


APP_TITLE: Final[str] = (
    "Health Fraud Intelligence"
)

APP_SHORT_TITLE: Final[str] = (
    "Fraud Intelligence"
)

APP_SUBTITLE: Final[str] = (
    "AI-assisted health insurance "
    "investigation prioritization"
)

APP_DESCRIPTION: Final[str] = (
    "Human-in-the-loop fraud risk scoring "
    "and investigation decision support."
)

APP_VERSION: Final[str] = (
    "6.1"
)

DEFAULT_API_URL: Final[str] = (
    "http://127.0.0.1:8000"
)

API_URL: Final[str] = (
    os.getenv(
        "FRAUD_API_URL",
        DEFAULT_API_URL,
    )
    .strip()
    .rstrip("/")
)

ENVIRONMENT: Final[str] = (
    os.getenv(
        "APP_ENV",
        "development",
    )
    .strip()
    .lower()
)


# =============================================================================
# Streamlit configuration
# =============================================================================


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        "Get Help":
            None,

        "Report a bug":
            None,

        "About":
            (
                f"{APP_TITLE}\n\n"
                f"{APP_DESCRIPTION}\n\n"
                f"Frontend v{APP_VERSION}"
            ),
    },
)


# =============================================================================
# Global styling
# =============================================================================


st.markdown(
    CUSTOM_CSS,
    unsafe_allow_html=True,
)


# =============================================================================
# Session state
# =============================================================================


initialize_state()


# =============================================================================
# API client
# =============================================================================


def get_api_client(base_url: str) -> FraudAPIClient:
    """Reuse connections inside one session; never share mutable cookies globally."""
    cached = st.session_state.get("_inference_client")
    if cached is not None and cached.base_url != base_url:
        cached.close()
        cached = None
    if cached is None:
        cached = FraudAPIClient(base_url=base_url, connect_timeout=3., read_timeout=60., retry_total=2)
        st.session_state["_inference_client"] = cached
    return cached


client = (
    get_api_client(
        API_URL
    )
)


# =============================================================================
# Runtime probe
# =============================================================================


@st.cache_data(
    ttl=8,
    show_spinner=False,
)
def get_runtime_status(
    base_url: str,
) -> dict[str, Any]:
    """
    Perform a lightweight independent runtime probe.

    The probe intentionally uses a short-lived client so sidebar
    diagnostics do not interfere with scoring requests.

    API connectivity and model readiness are evaluated separately.
    """

    probe = FraudAPIClient(
        base_url=base_url,
        connect_timeout=1.5,
        read_timeout=3.0,
        retry_total=0,
    )

    result: dict[
        str,
        Any,
    ] = {
        "api_online":
            False,

        "model_ready":
            False,

        "health":
            {},

        "model":
            {},

        "error":
            None,
    }

    try:

        health = (
            probe.health()
        )

        result[
            "health"
        ] = (
            health
            if isinstance(
                health,
                dict,
            )
            else {}
        )

        result[
            "api_online"
        ] = True

        # ---------------------------------------------------------------------
        # Prefer explicit model_loaded from /health when available.
        # ---------------------------------------------------------------------

        explicit_ready = (
            result[
                "health"
            ]
            .get(
                "model_loaded"
            )
        )

        if explicit_ready is not None:

            result[
                "model_ready"
            ] = bool(
                explicit_ready
            )

        # ---------------------------------------------------------------------
        # Otherwise confirm readiness through /model-info.
        # ---------------------------------------------------------------------

        if explicit_ready is None:

            try:

                model = (
                    probe.model_info()
                )

                if isinstance(
                    model,
                    dict,
                ):

                    result[
                        "model"
                    ] = model

                    result[
                        "model_ready"
                    ] = bool(
                        model.get(
                            "model_name"
                        )
                        and model.get(
                            "model_version"
                        )
                    )

            except Exception as exc:

                result[
                    "error"
                ] = str(
                    exc
                )

        else:

            # model-info remains useful for sidebar identity,
            # but failure does not redefine explicit health readiness.

            try:

                model = (
                    probe.model_info()
                )

                if isinstance(
                    model,
                    dict,
                ):

                    result[
                        "model"
                    ] = model

            except Exception:
                pass

    except Exception as exc:

        result[
            "error"
        ] = str(
            exc
        )

    finally:

        probe.close()

    return result


# =============================================================================
# Page registry
# =============================================================================


PageRenderer = Callable[
    [FraudAPIClient],
    None,
]


@dataclass(
    frozen=True,
    slots=True,
)
class PageDefinition:
    """
    Definition of one application workspace.
    """

    name: str

    short_description: str

    renderer: PageRenderer

    category: str


PAGES: Final[
    tuple[
        PageDefinition,
        ...,
    ]
] = (
    PageDefinition(
        name="Overview",
        short_description=(
            "Executive risk and model overview"
        ),
        renderer=render_overview,
        category="MONITOR",
    ),

    PageDefinition(
        name="Data Science Lab",
        short_description="Explore data, experiments and scientific evidence",
        renderer=render_data_science,
        category="EXPLORE",
    ),

    PageDefinition(
        name="Claim Analysis",
        short_description=(
            "Individual claim risk assessment"
        ),
        renderer=render_claim_analysis,
        category="ANALYZE",
    ),

    PageDefinition(
        name="Portfolio Scoring",
        short_description=(
            "Batch portfolio risk scoring"
        ),
        renderer=render_portfolio_scoring,
        category="SCORE",
    ),

    PageDefinition(
        name="Investigation Queue",
        short_description=(
            "Prioritized human-review workflow"
        ),
        renderer=render_investigation_queue,
        category="INVESTIGATE",
    ),

    PageDefinition(
        name="Model Insights",
        short_description=(
            "Performance and explainability"
        ),
        renderer=render_model_insights,
        category="UNDERSTAND",
    ),

    PageDefinition(
        name="System Status",
        short_description=(
            "Inference and artifact readiness"
        ),
        renderer=render_system_status,
        category="OPERATE",
    ),
)


PAGE_BY_NAME: Final[
    dict[
        str,
        PageDefinition,
    ]
] = {
    page.name:
        page

    for page in PAGES
}


# =============================================================================
# Sidebar helpers
# =============================================================================


def _sidebar_model_identity(
    runtime: dict[str, Any],
) -> tuple[
    str,
    str,
]:
    """
    Resolve model identity from model-info first,
    then fall back to health payload.
    """

    model = (
        runtime.get(
            "model"
        )
        or {}
    )

    health = (
        runtime.get(
            "health"
        )
        or {}
    )

    model_name = (
        model.get(
            "model_name"
        )
        or health.get(
            "model_name"
        )
        or "Model"
    )

    model_version = (
        model.get(
            "model_version"
        )
        or health.get(
            "model_version"
        )
        or "—"
    )

    return (
        str(
            model_name
        ),
        str(
            model_version
        ),
    )


# =============================================================================
# Sidebar
# =============================================================================


def render_sidebar() -> str:
    from frontend.utils.presentation import go_to

    selected_page = st.session_state.setdefault("main_navigation", "Overview")
    if selected_page not in PAGE_BY_NAME:
        selected_page = st.session_state["main_navigation"] = "Overview"
    with st.sidebar:
        st.markdown(
            '<div class="sidebar-brand"><div class="sidebar-brand-title">◇ Fraud Intelligence</div>'
            '<div class="sidebar-brand-subtitle">Health insurance · synthetic research</div></div>',
            unsafe_allow_html=True,
        )
        for group, names in {
            "Discover": ["Overview", "Data Science Lab", "Model Insights"],
            "Analyze & investigate": ["Claim Analysis", "Portfolio Scoring", "Investigation Queue"],
            "Operate": ["System Status"],
        }.items():
            st.markdown(f'<p class="nav-group-label">{group}</p>', unsafe_allow_html=True)
            for name in names:
                st.button(name, key="nav_" + name, width="stretch",
                          type="primary" if name == selected_page else "secondary",
                          on_click=go_to, args=(name,), help=PAGE_BY_NAME[name].short_description)
        page = PAGE_BY_NAME[selected_page]
        st.markdown(
            '<div class="sidebar-page-context"><span class="sidebar-page-category">'
            + html.escape(page.category) + '</span><span class="sidebar-page-description">'
            + html.escape(page.short_description) + '</span></div>', unsafe_allow_html=True,
        )
        st.divider()
        runtime = get_runtime_status(API_URL)
        online = bool(runtime.get("api_online"))
        ready = bool(runtime.get("model_ready"))
        status_badge(online and ready, label="INFERENCE READY" if online and ready else "SCORING UNAVAILABLE")
        st.caption("Scoring service operational" if online and ready else "Scoring is preparing or temporarily unavailable.")
        with st.expander("Runtime details"):
            model_name, version = _sidebar_model_identity(runtime)
            st.caption(f"{model_name} v{version} · Frontend v{APP_VERSION} · {ENVIRONMENT.title()}")
            st.caption("Co-located demo inference" if os.getenv("FRAUD_INFERENCE_MODE") == "embedded" else "Remote inference service")
        st.caption("Synthetic data only. Scores guide human investigation; they do not establish fraud.")
    return selected_page


# =============================================================================
# Global header
# =============================================================================


def render_header(selected_page: str) -> None:
    page = PAGE_BY_NAME[selected_page]
    st.markdown(
        '<div class="app-topbar"><span class="app-wordmark">Health Fraud Intelligence</span>'
        '<span class="page-context-strip"><span>' + html.escape(page.category)
        + '</span><span aria-hidden="true"> / </span><strong>' + html.escape(page.name)
        + '</strong></span></div>', unsafe_allow_html=True,
    )


# =============================================================================
# Router
# =============================================================================


def render_page(
    page_name: str,
) -> None:
    """
    Render one registered application workspace.

    Page-level failures are isolated so a failure in one view does
    not make the complete investigation console unusable.
    """

    definition = (
        PAGE_BY_NAME.get(
            page_name
        )
    )

    if definition is None:

        st.error(
            (
                "The requested application "
                "workspace does not exist."
            )
        )

        return

    try:

        definition.renderer(
            client
        )

    except Exception as exc:
        reference = uuid.uuid4().hex[:12]
        logging.getLogger("health_fraud.frontend").exception("Workspace error reference=%s page=%s", reference, page_name)
        st.error("This operation could not be completed. Check the input or try again shortly.")
        st.caption(f"Diagnostic reference: {reference}. Other workspaces remain available.")
        if ENVIRONMENT == "development":
            with st.expander("Development diagnostics", expanded=False):
                st.exception(exc)


# =============================================================================
# Main
# =============================================================================


def main() -> None:
    """
    Application entry point.
    """

    selected_page = (
        render_sidebar()
    )

    render_header(
        selected_page
    )

    render_page(
        selected_page
    )


if __name__ == "__main__":
    main()
