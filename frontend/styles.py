CUSTOM_CSS = """
<style>

/* ==========================================================================
   DESIGN TOKENS
   ========================================================================== */

/* The native appearance menu is the only preference store. The small v2
   adapter mirrors its resolved theme; CSS never changes Streamlit's preference. */
:root {
    --bg-main: #080E1A;
    --bg-secondary: #0C1423;
    --bg-tertiary: #111B2C;
    --card-bg: #111B2C;
    --input-bg: #152034;
    --input-hover: #1A2941;
    --header-bg: #080E1A;
    --surface-01: rgba(255,255,255,.02);
    --surface-02: rgba(255,255,255,.035);
    --surface-03: rgba(255,255,255,.05);
    --surface-hover: rgba(255,255,255,.07);
    --border-soft: #233149;
    --border: #30415C;
    --border-strong: #587297;
    --text-primary: #EAF0F9;
    --text-secondary: #B0BED2;
    --text-muted: #9CACC4;
    --text-disabled: #8190A8;
    --primary: #659CFF;
    --primary-text: #93BAFF;
    --primary-soft: rgba(76,141,255,.12);
    --secondary: #B39BFF;
    --secondary-soft: rgba(139,92,246,.12);
    --success: #61DFA7;
    --success-soft: rgba(97,223,167,.10);
    --warning: #F1C364;
    --warning-soft: rgba(241,195,100,.10);
    --high: #FFA679;
    --high-soft: rgba(255,166,121,.10);
    --critical: #FF829A;
    --critical-soft: rgba(255,130,154,.10);
    --on-accent: #FFFFFF;
    --radius-xs: 8px;
    --radius-sm: 10px;
    --radius-md: 14px;
    --radius-lg: 18px;
    --radius-xl: 22px;
    --shadow-sm: 0 6px 18px rgba(0,0,0,.13);
    --shadow-md: 0 12px 30px rgba(0,0,0,.18);
    --shadow-lg: 0 20px 48px rgba(0,0,0,.24);
    --transition-fast: 150ms cubic-bezier(.2,.8,.2,1);
    --transition: 200ms cubic-bezier(.2,.8,.2,1);
    --color-scheme: dark;
}
:root[data-fraud-theme="light"] {
    --bg-main: #F3F6FC;
    --bg-secondary: #EAF0F8;
    --bg-tertiary: #FFFFFF;
    --card-bg: #FFFFFF;
    --input-bg: #FFFFFF;
    --input-hover: #F5F8FD;
    --header-bg: #F3F6FC;
    --surface-01: rgba(24,45,78,.02);
    --surface-02: rgba(24,45,78,.035);
    --surface-03: rgba(24,45,78,.05);
    --surface-hover: rgba(24,45,78,.07);
    --border-soft: #D9E2EF;
    --border: #B8C7DC;
    --border-strong: #7C93B2;
    --text-primary: #15243B;
    --text-secondary: #405570;
    --text-muted: #50617B;
    --text-disabled: #687B95;
    --primary: #2458D3;
    --primary-text: #234FAF;
    --primary-soft: rgba(36,88,211,.08);
    --secondary: #6848C6;
    --secondary-soft: rgba(104,72,198,.08);
    --success: #06734D;
    --success-soft: rgba(6,115,77,.08);
    --warning: #895605;
    --warning-soft: rgba(137,86,5,.08);
    --high: #B5470B;
    --high-soft: rgba(181,71,11,.08);
    --critical: #BF2340;
    --critical-soft: rgba(191,35,64,.08);
    --shadow-sm: 0 3px 12px rgba(24,45,78,.05);
    --shadow-md: 0 8px 24px rgba(24,45,78,.07);
    --shadow-lg: 0 16px 40px rgba(24,45,78,.12);
    --color-scheme: light;
}


/* ==========================================================================
   UNIVERSAL SAFETY
   ========================================================================== */

*,
*::before,
*::after {
    box-sizing: border-box;
}


html,
body {
    max-width: 100%;
    overflow-x: hidden;
}


html {
    scroll-behavior: smooth;
}


body {
    margin: 0;

    color: var(--text-primary);

    font-family:
        Inter,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Roboto,
        Helvetica,
        Arial,
        sans-serif;

    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
}


[class*="css"] {
    font-family:
        Inter,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Roboto,
        Helvetica,
        Arial,
        sans-serif;
}


/* ==========================================================================
   GLOBAL APP SHELL
   ========================================================================== */

.stApp {
    min-height: 100vh;

    color-scheme: var(--color-scheme);
    background: var(--bg-main);

    color: var(--text-primary);
}


.block-container {
    width: 100%;
    max-width: 1540px;

    padding-top: 3.5rem;
    padding-bottom: 4rem;
    padding-left: 3rem;
    padding-right: 3rem;
}


/* ==========================================================================
   STREAMLIT CHROME
   ========================================================================== */

[data-testid="stSidebarNav"] a {
    min-height: 44px;
    border-radius: 10px;
    padding: .55rem .8rem;
}
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: color-mix(in srgb, var(--primary) 15%, transparent);
    box-shadow: inset 3px 0 0 var(--primary-text);
}

#MainMenu {
    visibility: visible;
}


footer {
    visibility: hidden;
}


header[data-testid="stHeader"] {
    background: var(--header-bg);
}


/* ==========================================================================
   GLOBAL LAYOUT SAFETY
   ========================================================================== */

[data-testid="stHorizontalBlock"] {
    width: 100%;
}


[data-testid="stHorizontalBlock"] > div,
[data-testid="stColumn"],
[data-testid="column"] {
    min-width: 0 !important;
}


[data-testid="stColumn"] {
    overflow: visible !important;
}


[data-testid="stColumn"] > div,
[data-testid="stColumn"] [data-testid="stVerticalBlock"],
[data-testid="stColumn"] [data-testid="stVerticalBlockBorderWrapper"] {
    min-width: 0 !important;
    max-width: 100% !important;
}


/* ==========================================================================
   SIDEBAR
   ========================================================================== */

[data-testid="stSidebar"] {
    background:
        radial-gradient(
            circle at 0% 0%,
            color-mix(in srgb, var(--primary) 5.5%, transparent),
            transparent 28%
        ),
        linear-gradient(
            180deg,
            var(--bg-secondary) 0%,
            var(--bg-main) 100%
        );

    border-right:
        1px solid var(--border-soft);
}


[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.55rem;
}


[data-testid="stSidebar"] * {
    color: var(--text-primary);
}


[data-testid="stSidebar"] hr {
    margin-top: 1.15rem;
    margin-bottom: 1.15rem;

    border-color: var(--border-soft);
}


[data-testid="stSidebar"] h2 {
    margin-bottom: 0.15rem;

    font-size: 1.25rem;
    font-weight: 800;
    letter-spacing: -0.025em;
}


.sidebar-product-meta {
    color: var(--text-disabled);

    font-size: .66rem;
    line-height: 1.65;

    text-transform: uppercase;
    letter-spacing: .085em;
}


/* ==========================================================================
   SIDEBAR NAVIGATION
   ========================================================================== */

[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    gap: .18rem;
}


[data-testid="stSidebar"] [data-testid="stRadio"] label {
    min-height: 42px;

    padding:
        .54rem
        .68rem;

    border:
        1px solid transparent;

    border-radius:
        11px;

    transition:
        background var(--transition-fast),
        border-color var(--transition-fast),
        transform var(--transition-fast);
}


[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    transform: translateX(2px);

    background:
        color-mix(in srgb, var(--text-primary) 3.8%, transparent);

    border-color:
        color-mix(in srgb, var(--text-primary) 4.5%, transparent);
}


[data-testid="stSidebar"] [data-testid="stRadio"] p {
    font-size: .90rem;
    font-weight: 600;

    white-space: normal !important;
}


/* ==========================================================================
   APPLICATION HEADER
   ========================================================================== */

.dashboard-title {
    max-width: 100%;

    margin: 0;

    font-size:
        clamp(
            2.1rem,
            4vw,
            3.45rem
        );

    line-height: 1.02;

    font-weight: 850;

    letter-spacing: -0.052em;

    overflow-wrap: anywhere;

    background:
        linear-gradient(
            92deg,
            var(--text-primary) 0%,
            var(--primary-text) 40%,
            var(--primary-text) 72%,
            var(--secondary) 100%
        );

    -webkit-background-clip: text;
    background-clip: text;

    -webkit-text-fill-color: transparent;
}


.dashboard-subtitle {
    max-width: 800px;

    margin-top: .75rem;
    margin-bottom: 1.3rem;

    color: var(--text-secondary);

    font-size: .98rem;
    line-height: 1.65;

    overflow-wrap: anywhere;
}


.page-context-strip {
    display: inline-flex;

    align-items: center;

    flex-wrap: wrap;

    gap: .52rem;

    max-width: 100%;

    padding:
        .40rem
        .72rem;

    margin-bottom: 1.05rem;

    border:
        1px solid var(--border-soft);

    border-radius: 999px;

    background:
        color-mix(in srgb, var(--text-primary) 2.2%, transparent);

    color: var(--text-secondary);

    font-size: .73rem;

    backdrop-filter: blur(10px);

    overflow-wrap: anywhere;
}


.page-context-strip strong {
    color: var(--text-primary);
    font-weight: 750;
}


/* ==========================================================================
   TYPOGRAPHY
   ========================================================================== */

h1,
h2,
h3,
h4,
h5 {
    max-width: 100%;

    color: var(--text-primary);

    letter-spacing: -.025em;

    white-space: normal;

    overflow-wrap: anywhere;
}


h1 {
    font-weight: 850;
}


h2,
h3 {
    font-weight: 780;
}


h4 {
    font-weight: 720;
}


p {
    max-width: 100%;

    line-height: 1.62;

    overflow-wrap: anywhere;
}


small {
    color: var(--text-muted);
}


[data-testid="stCaptionContainer"] {
    max-width: 100%;

    color: var(--text-secondary);

    white-space: normal !important;

    overflow-wrap: anywhere;
}


/* ==========================================================================
   SECTION HEADINGS
   ========================================================================== */

.section-heading {
    max-width: 100%;

    margin-top: .45rem;
    margin-bottom: 1.05rem;
}


.section-eyebrow {
    margin-bottom: .28rem;

    color: var(--primary-text);

    font-size: .66rem;
    font-weight: 800;

    letter-spacing: .14em;

    text-transform: uppercase;
}


.section-title {
    max-width: 100%;

    color: var(--text-primary);

    font-size:
        clamp(
            1.05rem,
            1.8vw,
            1.28rem
        );

    line-height: 1.25;

    font-weight: 800;

    letter-spacing: -.028em;

    white-space: normal;

    overflow-wrap: anywhere;
}


.section-subtitle {
    max-width: 900px;

    margin-top: .34rem;

    color: var(--text-secondary);

    font-size: .83rem;
    line-height: 1.55;

    white-space: normal;

    overflow-wrap: anywhere;
}


/* ==========================================================================
   PAGE INTRO
   ========================================================================== */

.page-intro {
    max-width: 100%;

    margin-bottom: 1.55rem;
}


.page-intro-eyebrow {
    max-width: 100%;

    margin-bottom: .32rem;

    color: var(--primary-text);

    font-size: .67rem;

    font-weight: 850;

    letter-spacing: .14em;

    text-transform: uppercase;

    white-space: normal;

    overflow-wrap: anywhere;
}


.page-intro-title {
    max-width: 100%;

    color: var(--text-primary);

    font-size:
        clamp(
            1.4rem,
            2.5vw,
            1.72rem
        );

    font-weight: 850;

    letter-spacing: -.04em;

    white-space: normal;

    overflow-wrap: anywhere;
}


.page-intro-subtitle {
    max-width: 850px;

    margin-top: .35rem;

    color: var(--text-secondary);

    font-size: .90rem;
    line-height: 1.6;

    white-space: normal;

    overflow-wrap: anywhere;
}


/* ==========================================================================
   GENERIC GLASS CARDS
   ========================================================================== */

.glass-card {
    position: relative;

    width: 100%;
    min-width: 0;

    min-height: 128px;
    height: auto;

    overflow: hidden;

    padding:
        1.3rem
        1.4rem;

    background:
        linear-gradient(
            145deg,
            color-mix(in srgb, var(--text-primary) 5.8%, transparent),
            color-mix(in srgb, var(--text-primary) 2%, transparent)
        );

    border:
        1px solid var(--border);

    border-radius:
        var(--radius-xl);

    box-shadow:
        var(--shadow-md);

    backdrop-filter:
        blur(16px);

    -webkit-backdrop-filter:
        blur(16px);

    transition:
        transform var(--transition),
        border-color var(--transition),
        background var(--transition),
        box-shadow var(--transition);
}


.glass-card::after {
    content: "";

    position: absolute;

    inset: 0;

    pointer-events: none;

    border-radius: inherit;

    background:
        linear-gradient(
            120deg,
            color-mix(in srgb, var(--text-primary) 3.5%, transparent),
            transparent 35%
        );
}


.glass-card:hover {
    transform: translateY(-2px);

    border-color: var(--border-strong);

    background:
        linear-gradient(
            145deg,
            color-mix(in srgb, var(--text-primary) 7.1%, transparent),
            color-mix(in srgb, var(--text-primary) 2.6%, transparent)
        );

    box-shadow:
        var(--shadow-lg);
}


/* ==========================================================================
   METRIC CARDS
   ========================================================================== */

.metric-card-pro {
    width: 100%;

    min-width: 0;

    height: auto;

    overflow: hidden;
}


.metric-accent {
    position: absolute;

    top: 0;
    left: 0;

    width: 100%;
    height: 2px;

    opacity: .88;
}


.metric-label {
    position: relative;
    z-index: 1;

    max-width: 100%;

    color: var(--text-secondary);

    font-size: .72rem;

    font-weight: 750;

    text-transform: uppercase;

    letter-spacing: .105em;

    white-space: normal;

    overflow-wrap: anywhere;
}


.metric-value {
    position: relative;
    z-index: 1;

    max-width: 100%;

    margin-top: .52rem;

    color: var(--text-primary);

    font-size:
        clamp(
            1.25rem,
            2.2vw,
            2rem
        );

    line-height: 1.12;

    font-weight: 850;

    letter-spacing: -.04em;

    white-space: normal !important;

    overflow: visible !important;

    text-overflow: clip !important;

    overflow-wrap: anywhere;
}


.metric-helper {
    position: relative;
    z-index: 1;

    min-height: 1.15rem;

    margin-top: .52rem;

    color: var(--text-secondary);

    font-size: .76rem;

    line-height: 1.42;

    white-space: normal;

    overflow-wrap: anywhere;
}


/* ==========================================================================
   MINI METRICS
   ========================================================================== */

.mini-metric {
    --mini-accent: var(--text-secondary);

    position: relative;

    width: 100%;
    min-width: 0;

    min-height: 96px;

    overflow: hidden;

    padding:
        .92rem
        1rem;

    border:
        1px solid var(--border-soft);

    border-radius:
        var(--radius-md);

    background:
        linear-gradient(
            145deg,
            color-mix(in srgb, var(--text-primary) 3.2%, transparent),
            color-mix(in srgb, var(--text-primary) 1.4%, transparent)
        );

    box-shadow:
        var(--shadow-sm);

    transition:
        transform var(--transition-fast),
        border-color var(--transition-fast),
        background var(--transition-fast);
}


.mini-metric::before {
    content: "";

    position: absolute;

    top: 0;
    left: 0;

    width: 100%;
    height: 2px;

    background:
        var(--mini-accent);

    opacity: .82;
}


.mini-metric:hover {
    transform: translateY(-1px);

    border-color:
        var(--border-strong);

    background:
        linear-gradient(
            145deg,
            color-mix(in srgb, var(--text-primary) 4.2%, transparent),
            color-mix(in srgb, var(--text-primary) 1.8%, transparent)
        );
}


.mini-metric-label {
    max-width: 100%;

    color: var(--text-secondary);

    font-size: .67rem;

    font-weight: 780;

    letter-spacing: .095em;

    text-transform: uppercase;

    white-space: normal;

    overflow-wrap: anywhere;
}


.mini-metric-value {
    max-width: 100%;

    margin-top: .34rem;

    color: var(--text-primary);

    font-size:
        clamp(
            1rem,
            1.8vw,
            1.35rem
        );

    line-height: 1.2;

    font-weight: 820;

    letter-spacing: -.025em;

    white-space: normal !important;

    overflow: visible !important;

    text-overflow: clip !important;

    overflow-wrap: anywhere !important;
}


.mini-metric-helper {
    max-width: 100%;

    margin-top: .32rem;

    color: var(--text-secondary);

    font-size: .70rem;

    line-height: 1.42;

    white-space: normal;

    overflow-wrap: anywhere;
}


/* ==========================================================================
   SURFACE CARD
   ========================================================================== */

.surface-card-heading {
    --surface-accent: var(--text-secondary);

    position: relative;

    width: 100%;
    min-width: 0;

    margin:
        .35rem
        0
        .9rem;

    padding:
        .9rem
        1rem
        .9rem
        1.15rem;

    overflow: hidden;

    border:
        1px solid var(--border-soft);

    border-radius:
        var(--radius-md);

    background:
        linear-gradient(
            135deg,
            color-mix(in srgb, var(--text-primary) 2.8%, transparent),
            color-mix(in srgb, var(--text-primary) 1.2%, transparent)
        );
}


.surface-card-heading::before {
    content: "";

    position: absolute;

    top: .75rem;
    bottom: .75rem;
    left: 0;

    width: 3px;

    border-radius: 999px;

    background:
        var(--surface-accent);
}


.surface-card-title {
    max-width: 100%;

    color: var(--text-primary);

    font-size: .92rem;

    line-height: 1.35;

    font-weight: 780;

    letter-spacing: -.015em;

    white-space: normal;

    overflow-wrap: anywhere;
}


.surface-card-subtitle {
    max-width: 900px;

    margin-top: .25rem;

    color: var(--text-secondary);

    font-size: .78rem;

    line-height: 1.5;

    white-space: normal;

    overflow-wrap: anywhere;
}


/* ==========================================================================
   NATIVE STREAMLIT METRICS
   ========================================================================== */

div[data-testid="stMetric"] {
    width: 100%;

    min-width: 0;

    min-height: 124px;
    height: auto;

    overflow: visible;

    padding:
        1rem
        1.08rem;

    border:
        1px solid var(--border);

    border-radius:
        var(--radius-md);

    background:
        linear-gradient(
            145deg,
            color-mix(in srgb, var(--text-primary) 4%, transparent),
            color-mix(in srgb, var(--text-primary) 1.8%, transparent)
        );

    box-shadow:
        var(--shadow-sm);
}


div[data-testid="stMetric"] > div {
    min-width: 0;
    max-width: 100%;
}


div[data-testid="stMetric"] label {
    max-width: 100%;

    color: var(--text-secondary) !important;

    white-space: normal !important;

    overflow: visible !important;

    text-overflow: clip !important;

    overflow-wrap: anywhere;
}


div[data-testid="stMetricValue"] {
    max-width: 100%;

    color: var(--text-primary);

    font-size:
        clamp(
            1.45rem,
            2.5vw,
            2.45rem
        ) !important;

    line-height: 1.08 !important;

    font-weight: 820;

    letter-spacing: -.035em;

    white-space: normal !important;

    overflow: visible !important;

    text-overflow: clip !important;

    overflow-wrap: anywhere !important;

    word-break: normal !important;
}


div[data-testid="stMetricValue"] > div {
    max-width: 100%;

    white-space: normal !important;

    overflow: visible !important;

    text-overflow: clip !important;

    overflow-wrap: anywhere !important;
}


div[data-testid="stMetricDelta"] {
    font-size: .75rem;

    white-space: normal;
}


/* ==========================================================================
   APPLICATION BADGES
   ========================================================================== */

.app-badge {
    --badge-color: var(--text-secondary);

    display: inline-flex;

    align-items: center;
    justify-content: center;

    gap: .32rem;

    max-width: 100%;

    padding:
        .42rem
        .72rem;

    border:
        1px solid
        var(--badge-color);

    border-radius:
        999px;

    background:
        color-mix(in srgb, var(--text-primary) 2.5%, transparent);

    color:
        var(--badge-color);

    font-size:
        .72rem;

    font-weight:
        800;

    letter-spacing:
        .055em;

    line-height:
        1.2;

    white-space: normal;

    overflow-wrap: anywhere;

    text-align: center;

    box-shadow:
        inset 0 0 0 1px
        color-mix(in srgb, var(--text-primary) 1.5%, transparent);
}


/* ==========================================================================
   LEGACY STATUS BADGES
   ========================================================================== */

.status-ok,
.status-offline {
    display: inline-flex;

    align-items: center;

    gap: .32rem;

    max-width: 100%;

    padding:
        .42rem
        .72rem;

    border-radius: 999px;

    font-size: .72rem;

    font-weight: 800;

    letter-spacing: .055em;

    white-space: normal;

    overflow-wrap: anywhere;
}


.status-ok {
    border:
        1px solid
        color-mix(in srgb, var(--success) 34%, transparent);

    background:
        var(--success-soft);

    color:
        var(--success);
}


.status-offline {
    border:
        1px solid
        color-mix(in srgb, var(--critical) 34%, transparent);

    background:
        var(--critical-soft);

    color:
        var(--critical);
}


/* ==========================================================================
   RISK BADGE
   ========================================================================== */

.risk-badge-wrapper {
    width: 100%;

    display: flex;

    justify-content: center;

    margin-top:
        .65rem;
}


.risk-badge {
    --risk-color: var(--success);

    display: inline-flex;

    align-items: center;
    justify-content: center;

    max-width: 100%;

    min-width:
        92px;

    padding:
        .50rem
        1rem;

    border:
        1px solid
        var(--risk-color);

    border-radius:
        999px;

    background:
        color-mix(in srgb, var(--text-primary) 2.5%, transparent);

    color:
        var(--risk-color);

    font-size:
        .77rem;

    font-weight:
        850;

    letter-spacing:
        .135em;

    text-transform:
        uppercase;

    white-space: normal;

    overflow-wrap: anywhere;

    text-align: center;

    box-shadow:
        0 8px 24px
        color-mix(in srgb, var(--bg-main) 14%, transparent);
}


/* ==========================================================================
   RISK GAUGE
   ========================================================================== */

.risk-gauge-wrapper {
    width: 100%;

    display: flex;

    align-items: center;
    justify-content: center;

    padding:
        1.35rem
        0;
}


.risk-gauge-ring {
    --risk-color: var(--success);
    --risk-degrees: 0deg;

    position: relative;

    width:
        clamp(
            190px,
            18vw,
            238px
        );

    max-width: 100%;

    aspect-ratio: 1;

    display: flex;

    align-items: center;
    justify-content: center;

    border-radius:
        50%;

    background:
        conic-gradient(
            from 0deg,
            var(--risk-color) 0deg,
            var(--risk-color) var(--risk-degrees),
            color-mix(in srgb, var(--text-primary) 6.5%, transparent) var(--risk-degrees),
            color-mix(in srgb, var(--text-primary) 6.5%, transparent) 360deg
        );

    box-shadow:
        0 0 58px color-mix(in srgb, var(--primary) 10%, transparent),
        0 18px 50px color-mix(in srgb, var(--bg-main) 22%, transparent),
        inset 0 0 22px color-mix(in srgb, var(--text-primary) 2.5%, transparent);

    transition:
        transform var(--transition),
        box-shadow var(--transition);
}


.risk-gauge-ring::before {
    content: "";

    position: absolute;

    inset: -1px;

    border:
        1px solid
        color-mix(in srgb, var(--text-primary) 7.5%, transparent);

    border-radius:
        inherit;

    pointer-events:
        none;
}


.risk-gauge-ring::after {
    content: "";

    position: absolute;

    inset: 0;

    border-radius: inherit;

    background:
        radial-gradient(
            circle at 50% 0%,
            color-mix(in srgb, var(--text-primary) 8%, transparent),
            transparent 34%
        );

    pointer-events:
        none;
}


.risk-gauge-ring:hover {
    transform:
        scale(1.015);

    box-shadow:
        0 0 65px color-mix(in srgb, var(--primary) 13%, transparent),
        0 22px 55px color-mix(in srgb, var(--bg-main) 28%, transparent),
        inset 0 0 24px color-mix(in srgb, var(--text-primary) 3%, transparent);
}


.risk-gauge-inner {
    position: relative;
    z-index: 1;

    width: 76.5%;

    aspect-ratio: 1;

    display: flex;

    flex-direction: column;

    align-items: center;
    justify-content: center;

    border:
        1px solid
        color-mix(in srgb, var(--text-primary) 9%, transparent);

    border-radius:
        50%;

    background:
        radial-gradient(
            circle at 50% 35%,
            color-mix(in srgb, var(--text-primary) 3.5%, transparent),
            transparent 48%
        ),
        linear-gradient(
            145deg,
            var(--bg-tertiary),
            var(--bg-main)
        );

    box-shadow:
        inset 0 0 35px
        color-mix(in srgb, var(--bg-main) 20%, transparent);
}


.risk-gauge-label {
    max-width: 90%;

    color:
        var(--text-secondary);

    font-size:
        .68rem;

    font-weight:
        750;

    letter-spacing:
        .14em;

    text-transform:
        uppercase;

    text-align: center;

    white-space: normal;
}


.risk-gauge-value {
    max-width: 90%;

    margin-top:
        .16rem;

    color:
        var(--text-primary);

    font-size:
        clamp(
            1.8rem,
            3vw,
            2.35rem
        );

    line-height:
        1.1;

    font-weight:
        850;

    letter-spacing:
        -.045em;

    white-space: normal;

    text-align: center;

    overflow-wrap: anywhere;
}


.risk-gauge-tier {
    max-width: 90%;

    margin-top:
        .28rem;

    font-size:
        .78rem;

    font-weight:
        850;

    letter-spacing:
        .135em;

    text-transform:
        uppercase;

    text-align: center;

    white-space: normal;

    overflow-wrap: anywhere;
}


/* ==========================================================================
   INFORMATION PANELS
   ========================================================================== */

.info-panel {
    --panel-color: var(--primary-text);

    position: relative;

    width: 100%;
    min-width: 0;

    overflow: hidden;

    padding:
        1rem
        1.15rem;

    border:
        1px solid
        color-mix(in srgb, var(--text-primary) 8%, transparent);

    border-left:
        3px solid
        var(--panel-color);

    border-radius:
        var(--radius-md);

    background:
        linear-gradient(
            135deg,
            color-mix(in srgb, var(--text-primary) 3.5%, transparent),
            color-mix(in srgb, var(--text-primary) 1.5%, transparent)
        );

    box-shadow:
        var(--shadow-sm);
}


.info-panel::before {
    content: "";

    position: absolute;

    width: 90px;
    height: 90px;

    left: -40px;
    top: -40px;

    border-radius: 50%;

    background:
        var(--panel-color);

    opacity: .05;

    filter:
        blur(22px);

    pointer-events: none;
}


.info-panel-title {
    position: relative;

    max-width: 100%;

    color:
        var(--panel-color);

    font-size:
        .72rem;

    font-weight:
        850;

    letter-spacing:
        .075em;

    text-transform:
        uppercase;

    white-space: normal;

    overflow-wrap: anywhere;
}


.info-panel-message {
    position: relative;

    max-width: 1000px;

    margin-top:
        .38rem;

    color:
        var(--text-secondary);

    font-size:
        .86rem;

    line-height:
        1.58;

    white-space: normal;

    overflow-wrap: anywhere;
}


/* ==========================================================================
   DECISION PANEL
   ========================================================================== */

.decision-panel {
    --decision-color: var(--primary-text);

    position: relative;

    width: 100%;
    min-width: 0;

    padding:
        1.05rem
        1.15rem;

    overflow: hidden;

    border:
        1px solid var(--border);

    border-radius:
        var(--radius-lg);

    background:
        linear-gradient(
            135deg,
            color-mix(in srgb, var(--text-primary) 4%, transparent),
            color-mix(in srgb, var(--text-primary) 1.4%, transparent)
        );

    box-shadow:
        var(--shadow-sm);
}


.decision-panel::before {
    content: "";

    position: absolute;

    width: 130px;
    height: 130px;

    top: -75px;
    right: -60px;

    border-radius: 50%;

    background:
        var(--decision-color);

    opacity: .055;

    filter:
        blur(28px);

    pointer-events: none;
}


.decision-panel-header {
    position: relative;

    display: flex;

    align-items: center;

    gap: .55rem;

    min-width: 0;
}


.decision-panel-dot {
    flex: 0 0 auto;

    width: 8px;
    height: 8px;

    border-radius: 50%;

    background:
        var(--decision-color);

    box-shadow:
        0 0 16px
        var(--decision-color);
}


.decision-panel-title {
    min-width: 0;

    max-width: 100%;

    color:
        var(--decision-color);

    font-size: .74rem;

    font-weight: 850;

    letter-spacing: .075em;

    text-transform: uppercase;

    white-space: normal;

    overflow-wrap: anywhere;
}


.decision-panel-message {
    position: relative;

    max-width: 1000px;

    margin-top: .48rem;

    color:
        var(--text-secondary);

    font-size: .88rem;

    line-height: 1.62;

    white-space: normal;

    overflow-wrap: anywhere;
}


.decision-panel-caption {
    position: relative;

    max-width: 1000px;

    margin-top: .55rem;

    color:
        var(--text-secondary);

    font-size: .72rem;

    line-height: 1.5;

    white-space: normal;

    overflow-wrap: anywhere;
}


/* ==========================================================================
   TREE SHAP DRIVER CARDS
   ========================================================================== */

.driver-card {
    --driver-color: var(--text-secondary);

    position: relative;

    width: 100%;
    min-width: 0;

    margin-bottom: .62rem;

    padding:
        .95rem
        1rem;

    overflow: hidden;

    border:
        1px solid var(--border-soft);

    border-left:
        3px solid
        var(--driver-color);

    border-radius:
        var(--radius-md);

    background:
        linear-gradient(
            135deg,
            color-mix(in srgb, var(--text-primary) 3.2%, transparent),
            color-mix(in srgb, var(--text-primary) 1.2%, transparent)
        );

    box-shadow:
        0 8px 26px
        color-mix(in srgb, var(--bg-main) 10%, transparent);

    transition:
        transform var(--transition-fast),
        border-color var(--transition-fast),
        background var(--transition-fast),
        box-shadow var(--transition-fast);
}


.driver-card::before {
    content: "";

    position: absolute;

    width: 90px;
    height: 90px;

    top: -45px;
    left: -45px;

    border-radius: 50%;

    background:
        var(--driver-color);

    opacity: .045;

    filter:
        blur(18px);

    pointer-events: none;
}


.driver-card:hover {
    transform:
        translateY(-1px);

    border-color:
        var(--border);

    border-left-color:
        var(--driver-color);

    background:
        linear-gradient(
            135deg,
            color-mix(in srgb, var(--text-primary) 4.3%, transparent),
            color-mix(in srgb, var(--text-primary) 1.7%, transparent)
        );

    box-shadow:
        0 12px 32px
        color-mix(in srgb, var(--bg-main) 14%, transparent);
}


.driver-direction {
    position: relative;

    max-width: 100%;

    color:
        var(--driver-color);

    font-size:
        .62rem;

    font-weight:
        850;

    letter-spacing:
        .105em;

    text-transform:
        uppercase;

    white-space:
        normal;

    overflow-wrap:
        anywhere;
}


.driver-label {
    position: relative;

    max-width: 100%;

    margin-top: .28rem;

    color:
        var(--text-primary);

    font-size:
        .90rem;

    line-height:
        1.4;

    font-weight:
        750;

    white-space:
        normal;

    overflow-wrap:
        anywhere;
}


.driver-meta {
    position: relative;

    display: flex;

    flex-wrap: wrap;

    gap:
        .55rem
        1.25rem;

    margin-top:
        .65rem;
}


.driver-value,
.driver-contribution {
    min-width: 0;

    display: flex;

    flex-direction: column;

    gap: .12rem;
}


.driver-value span,
.driver-contribution span {
    color:
        var(--text-secondary);

    font-size:
        .64rem;

    font-weight:
        700;

    letter-spacing:
        .06em;

    text-transform:
        uppercase;
}


.driver-value strong,
.driver-contribution strong {
    max-width: 100%;

    color:
        var(--text-secondary);

    font-size:
        .77rem;

    line-height:
        1.4;

    font-weight:
        720;

    white-space:
        normal;

    overflow-wrap:
        anywhere;
}


.driver-contribution strong {
    color:
        var(--driver-color);
}


/* ==========================================================================
   KEY VALUE ROW
   ========================================================================== */

.key-value-row {
    width: 100%;
    min-width: 0;

    display: grid;

    grid-template-columns:
        minmax(130px, .75fr)
        minmax(0, 1.25fr);

    gap: .75rem;

    align-items: start;

    padding:
        .72rem
        .15rem;

    border-bottom:
        1px solid
        color-mix(in srgb, var(--text-primary) 4.5%, transparent);
}


.key-value-row:last-child {
    border-bottom: none;
}


.key-value-label {
    min-width: 0;

    color:
        var(--text-secondary);

    font-size:
        .72rem;

    line-height:
        1.45;

    font-weight:
        700;

    white-space:
        normal;

    overflow-wrap:
        anywhere;
}


.key-value-value {
    min-width: 0;

    max-width: 100%;

    color:
        var(--text-primary);

    font-size:
        .78rem;

    line-height:
        1.48;

    font-weight:
        650;

    text-align: right;

    white-space:
        normal;

    overflow:
        visible;

    text-overflow:
        clip;

    overflow-wrap:
        anywhere;
}


.key-value-monospace {
    font-family:
        "SFMono-Regular",
        Consolas,
        "Liberation Mono",
        Menlo,
        monospace;

    font-size:
        .72rem;

    word-break:
        break-word;
}


/* ==========================================================================
   SOFT DIVIDER
   ========================================================================== */

.soft-divider {
    width: 100%;
    min-width: 0;

    display: flex;

    align-items: center;

    gap: .65rem;

    margin:
        .9rem
        0;
}


.soft-divider-line {
    flex: 1 1 auto;

    min-width: 10px;

    height: 1px;

    background:
        var(--border-soft);
}


.soft-divider-label {
    flex: 0 1 auto;

    max-width: 70%;

    color:
        var(--text-secondary);

    font-size:
        .64rem;

    font-weight:
        750;

    letter-spacing:
        .085em;

    text-transform:
        uppercase;

    text-align:
        center;

    white-space:
        normal;

    overflow-wrap:
        anywhere;
}


/* ==========================================================================
   BUTTONS
   ========================================================================== */

.stButton > button,
.stDownloadButton > button,
[data-testid="stFormSubmitButton"] > button {
    min-width: 0;

    min-height: 45px;
    height: auto;

    padding:
        .58rem
        1.05rem;

    border:
        1px solid
        color-mix(in srgb, var(--primary) 32%, transparent);

    border-radius:
        12px;

    background:
        linear-gradient(
            135deg,
            #286CF4 0%,
            #6255EE 100%
        );

    color:
        var(--text-primary);

    font-weight:
        750;

    letter-spacing:
        -.005em;

    white-space: normal;

    overflow-wrap: anywhere;

    box-shadow:
        0 8px 25px
        color-mix(in srgb, var(--primary) 14%, transparent);

    transition:
        transform var(--transition-fast),
        border-color var(--transition-fast),
        box-shadow var(--transition-fast),
        filter var(--transition-fast);
}


.stButton > button:hover,
.stDownloadButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    transform:
        translateY(-1px);

    border-color:
        color-mix(in srgb, var(--text-primary) 40%, transparent);

    box-shadow:
        0 12px 32px
        color-mix(in srgb, var(--primary) 22%, transparent);

    filter:
        brightness(1.06);
}


.stButton > button:active,
.stDownloadButton > button:active {
    transform:
        translateY(0);
}


.stButton > button:disabled {
    opacity:
        .45;

    cursor:
        not-allowed;

    transform:
        none;
}


button[kind="secondary"] {
    background:
        color-mix(in srgb, var(--text-primary) 3.5%, transparent) !important;

    border:
        1px solid var(--border) !important;

    color:
        var(--text-secondary) !important;

    box-shadow:
        none !important;
}


button[kind="secondary"]:hover {
    background:
        color-mix(in srgb, var(--text-primary) 6.5%, transparent) !important;

    border-color:
        var(--border-strong) !important;
}


.stButton > button *,
.stDownloadButton > button *,
[data-testid="stFormSubmitButton"] > button * {
    max-width: 100%;

    white-space: normal !important;

    overflow: visible !important;

    text-overflow: clip !important;

    overflow-wrap: anywhere !important;

    text-align: center;
}


/* ==========================================================================
   FORM LABELS
   ========================================================================== */

[data-testid="stWidgetLabel"] p {
    max-width: 100%;

    color:
        var(--text-secondary);

    font-size:
        .81rem;

    font-weight:
        650;

    white-space: normal;

    overflow-wrap: anywhere;
}

[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] *,
[data-testid="stTooltipIcon"],
[data-testid="stTooltipIcon"] * {
    color: var(--text-secondary) !important;
}

[data-testid="stTooltipIcon"] svg {
    color: var(--text-secondary) !important;
    fill: currentColor !important;
}


/* ==========================================================================
   INPUTS — ADAPTIVE THEME
   ========================================================================== */

/* Controls and portal menus share the active semantic palette. */

div[data-baseweb="input"],
div[data-baseweb="textarea"],
div[data-baseweb="select"],
[data-testid="stDateInput"],
[data-testid="stNumberInput"],
[data-testid="stTextInput"],
[data-testid="stTextArea"] {
    min-width: 0;
    color: var(--text-primary) !important;
    color-scheme: var(--color-scheme) !important;
}

div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div,
div[data-baseweb="select"] > div {
    min-width: 0;
    background: var(--input-bg) !important;
    border-color: color-mix(in srgb, var(--text-primary) 10%, transparent) !important;
    border-radius: 11px !important;
    color: var(--text-primary) !important;
    box-shadow: none;
    transition: border-color var(--transition-fast), box-shadow var(--transition-fast), background var(--transition-fast);
}

div[data-baseweb="input"] > div:hover,
div[data-baseweb="textarea"] > div:hover,
div[data-baseweb="select"] > div:hover {
    background: var(--input-hover) !important;
    border-color: color-mix(in srgb, var(--text-primary) 18%, transparent) !important;
}

div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="textarea"] > div:focus-within,
div[data-baseweb="select"] > div:focus-within {
    background: var(--input-bg) !important;
    border-color: color-mix(in srgb, var(--primary) 72%, transparent) !important;
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--primary) 12%, transparent) !important;
}

input,
textarea,
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea,
[data-testid="stDateInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    min-width: 0;
    background: transparent !important;
    color: var(--text-primary) !important;
    -webkit-text-fill-color: var(--text-primary) !important;
    caret-color: var(--primary) !important;
    opacity: 1 !important;
}

input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus,
textarea:-webkit-autofill,
textarea:-webkit-autofill:hover,
textarea:-webkit-autofill:focus {
    -webkit-text-fill-color: var(--text-primary) !important;
    -webkit-box-shadow: 0 0 0 1000px var(--input-bg) inset !important;
    box-shadow: 0 0 0 1000px var(--input-bg) inset !important;
    caret-color: var(--primary) !important;
}

input::placeholder,
textarea::placeholder,
div[data-baseweb="input"] input::placeholder,
div[data-baseweb="textarea"] textarea::placeholder {
    color: var(--text-disabled) !important;
    -webkit-text-fill-color: var(--text-disabled) !important;
    opacity: 1 !important;
}

div[data-baseweb="select"] span,
div[data-baseweb="select"] p,
div[data-baseweb="select"] [role="combobox"],
div[data-baseweb="select"] [aria-selected="true"] {
    color: var(--text-primary) !important;
    -webkit-text-fill-color: var(--text-primary) !important;
    opacity: 1 !important;
}

div[data-baseweb="select"] svg,
div[data-baseweb="input"] svg,
[data-testid="stDateInput"] svg,
[data-testid="stNumberInput"] svg {
    color: var(--text-secondary) !important;
    fill: currentColor !important;
}

[data-testid="stNumberInput"] button {
    color: var(--text-primary) !important;
    background: transparent !important;
    border-color: transparent !important;
}

[data-testid="stNumberInput"] button:hover {
    color: var(--text-primary) !important;
    background: color-mix(in srgb, var(--text-primary) 5.5%, transparent) !important;
}

input:disabled,
textarea:disabled,
input[readonly],
textarea[readonly],
[data-baseweb="select"] [aria-disabled="true"] {
    color: var(--text-secondary) !important;
    -webkit-text-fill-color: var(--text-secondary) !important;
    opacity: .78 !important;
}

input::-webkit-calendar-picker-indicator {
    filter: invert(86%) sepia(8%) saturate(430%) hue-rotate(177deg) brightness(98%) contrast(92%);
    opacity: .90;
}

input[type="number"] {
    color-scheme: var(--color-scheme);
}

/* ==========================================================================
   SELECTBOX / MULTISELECT — ADAPTIVE THEME
   ========================================================================== */

[data-baseweb="select"] {
    min-width: 0;
    border-radius: 11px;
    color: var(--text-primary) !important;
}

[data-baseweb="select"] * {
    min-width: 0;
    max-width: 100%;
}

[data-baseweb="select"] span,
[data-baseweb="select"] div,
[data-baseweb="select"] p {
    color: var(--text-primary) !important;
    -webkit-text-fill-color: var(--text-primary) !important;
}

[data-baseweb="select"] p {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    overflow-wrap: anywhere !important;
}

[data-baseweb="popover"] {
    border-radius: var(--radius-md);
    max-width: min(92vw, 760px) !important;
    color-scheme: var(--color-scheme) !important;
}

[data-baseweb="popover"] > div {
    max-width: min(92vw, 760px) !important;
    background: var(--bg-tertiary) !important;
    color: var(--text-primary) !important;
}

[data-baseweb="menu"],
div[role="listbox"] {
    max-width: min(92vw, 760px) !important;
    overflow-x: hidden;
    background: var(--bg-tertiary) !important;
    color: var(--text-primary) !important;
    border: 1px solid color-mix(in srgb, var(--text-primary) 10%, transparent);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-lg);
}

[data-baseweb="menu"] li,
[data-baseweb="menu"] [role="option"],
div[role="listbox"] [role="option"] {
    min-width: 0;
    max-width: 100%;
    height: auto !important;
    min-height: 40px;
    padding-top: .52rem;
    padding-bottom: .52rem;
    background: transparent !important;
    color: var(--text-primary) !important;
    -webkit-text-fill-color: var(--text-primary) !important;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    overflow-wrap: anywhere !important;
    transition: background var(--transition-fast), color var(--transition-fast);
}

[data-baseweb="menu"] li *,
[data-baseweb="menu"] [role="option"] *,
div[role="listbox"] [role="option"] * {
    color: inherit !important;
    -webkit-text-fill-color: inherit !important;
}

[data-baseweb="menu"] li:hover,
[data-baseweb="menu"] [role="option"]:hover,
div[role="listbox"] [role="option"]:hover {
    background: color-mix(in srgb, var(--primary) 10.5%, transparent) !important;
    color: var(--text-primary) !important;
}

[data-baseweb="menu"] [aria-selected="true"],
[data-baseweb="menu"] [role="option"][aria-selected="true"],
div[role="listbox"] [role="option"][aria-selected="true"] {
    background: color-mix(in srgb, var(--primary) 17%, transparent) !important;
    color: var(--text-primary) !important;
    font-weight: 700;
}

[data-baseweb="menu"] [aria-disabled="true"],
div[role="listbox"] [role="option"][aria-disabled="true"] {
    color: var(--text-disabled) !important;
    -webkit-text-fill-color: var(--text-disabled) !important;
    opacity: .72;
}

[data-baseweb="tag"] {
    background: color-mix(in srgb, var(--primary) 15%, transparent) !important;
    border: 1px solid color-mix(in srgb, var(--primary) 24%, transparent) !important;
    color: var(--primary-text) !important;
}

[data-baseweb="tag"] * {
    color: var(--primary-text) !important;
    -webkit-text-fill-color: var(--primary-text) !important;
}

[data-baseweb="select"] button,
[data-baseweb="tag"] svg {
    color: var(--text-secondary) !important;
    fill: currentColor !important;
}

/* ==========================================================================
   CHECKBOX / TOGGLE
   ========================================================================== */

[data-testid="stCheckbox"] label,
[data-testid="stToggle"] label {
    color:
        var(--text-secondary);

    white-space:
        normal;
}


/* ==========================================================================
   SLIDERS
   ========================================================================== */

[data-testid="stSlider"] {
    padding-top:
        .1rem;
}


[data-testid="stSlider"] [role="slider"] {
    box-shadow:
        0 0 0 4px
        color-mix(in srgb, var(--primary) 10%, transparent);
}


/* ==========================================================================
   FILE UPLOADER
   ========================================================================== */

[data-testid="stFileUploaderDropzone"] {
    min-width: 0;

    padding:
        2.15rem
        1.5rem;

    background:
        linear-gradient(
            145deg,
            color-mix(in srgb, var(--primary) 3.5%, transparent),
            color-mix(in srgb, var(--text-primary) 1.8%, transparent)
        );

    border:
        1px dashed
        color-mix(in srgb, var(--primary) 22%, transparent);

    border-radius:
        var(--radius-xl);

    transition:
        background var(--transition),
        border-color var(--transition);
}


[data-testid="stFileUploaderDropzone"]:hover {
    background:
        linear-gradient(
            145deg,
            color-mix(in srgb, var(--primary) 6%, transparent),
            color-mix(in srgb, var(--text-primary) 2.6%, transparent)
        );

    border-color:
        color-mix(in srgb, var(--primary) 42%, transparent);
}


[data-testid="stFileUploaderDropzoneInstructions"] {
    color:
        var(--text-secondary);

    white-space:
        normal;

    overflow-wrap:
        anywhere;
}


/* ==========================================================================
   FORMS
   ========================================================================== */

[data-testid="stForm"] {
    min-width: 0;

    padding:
        1.15rem;

    border:
        1px solid var(--border-soft);

    border-radius:
        var(--radius-lg);

    background:
        color-mix(in srgb, var(--text-primary) 1.4%, transparent);
}


[data-testid="stForm"] *,
[data-testid="stFileUploader"] *,
[data-testid="stCheckbox"] *,
[data-testid="stToggle"] * {
    max-width: 100%;
}


/* ==========================================================================
   TABS
   ========================================================================== */

[data-testid="stTabs"] {
    min-width: 0;

    margin-top:
        .25rem;
}


[data-baseweb="tab-list"] {
    gap:
        .28rem;

    border-bottom:
        1px solid var(--border-soft);

    overflow-x:
        auto;
}


button[data-baseweb="tab"] {
    min-height:
        43px;

    padding:
        .5rem
        .8rem;

    color:
        var(--text-secondary);

    font-weight:
        650;

    border-radius:
        9px 9px 0 0;

    white-space:
        normal;

    transition:
        color var(--transition-fast),
        background var(--transition-fast);
}


button[data-baseweb="tab"]:hover {
    color:
        var(--text-secondary);

    background:
        color-mix(in srgb, var(--text-primary) 2.5%, transparent);
}


button[data-baseweb="tab"][aria-selected="true"] {
    color:
        var(--text-primary);

    background:
        linear-gradient(
            180deg,
            color-mix(in srgb, var(--primary) 7.5%, transparent),
            transparent
        );
}

button[data-baseweb="tab"][aria-disabled="true"] {
    color: var(--text-disabled) !important;
    opacity: .78;
}


button[data-baseweb="tab"] *,
[data-baseweb="tab-panel"],
[data-baseweb="tab-panel"] * {
    max-width:
        100%;

    white-space:
        normal;

    overflow-wrap:
        anywhere;
}


/* ==========================================================================
   EXPANDERS
   ========================================================================== */

[data-testid="stExpander"] {
    min-width: 0;

    overflow:
        hidden;

    border:
        1px solid var(--border);

    border-radius:
        var(--radius-md);

    background:
        color-mix(in srgb, var(--text-primary) 1.8%, transparent);
}


[data-testid="stExpander"] summary {
    white-space:
        normal;

    transition:
        background var(--transition-fast);
}


[data-testid="stExpander"] summary:hover {
    background:
        color-mix(in srgb, var(--text-primary) 2.5%, transparent);
}


[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary *,
[data-testid="stExpanderDetails"],
[data-testid="stExpanderDetails"] * {
    max-width: 100%;

    white-space:
        normal !important;

    overflow-wrap:
        anywhere !important;
}


/* ==========================================================================
   ALERTS
   ========================================================================== */

[data-testid="stAlert"] {
    min-width: 0;

    border:
        1px solid var(--border);

    border-radius:
        var(--radius-md);

    backdrop-filter:
        blur(10px);

    box-shadow:
        0 8px 28px
        color-mix(in srgb, var(--bg-main) 10%, transparent);
}


[data-testid="stAlert"] * {
    white-space:
        normal;

    overflow-wrap:
        anywhere;
}


/* ==========================================================================
   DATAFRAMES / TABLES
   ========================================================================== */

[data-testid="stDataFrame"] {
    max-width: 100%;

    overflow:
        auto;

    border:
        1px solid var(--border);

    border-radius:
        var(--radius-lg);

    background:
        color-mix(in srgb, var(--text-primary) 1.8%, transparent);

    box-shadow:
        var(--shadow-sm);
}


[data-testid="stDataFrame"] > div {
    max-width:
        100% !important;
}


[data-testid="stDataFrame"] canvas {
    max-width:
        none;
}


[data-testid="stTable"] {
    max-width: 100%;

    overflow:
        auto;

    border:
        1px solid var(--border);

    border-radius:
        var(--radius-md);
}


/* ==========================================================================
   JSON / CODE
   ========================================================================== */

[data-testid="stJson"] {
    max-width: 100%;

    overflow:
        auto;

    border:
        1px solid var(--border);

    border-radius:
        var(--radius-md);

    background:
        color-mix(in srgb, var(--bg-main) 52%, transparent);
}


[data-testid="stCode"] {
    max-width: 100%;

    overflow:
        auto;

    border:
        1px solid var(--border);

    border-radius:
        var(--radius-md);
}


code,
pre {
    max-width: 100%;

    overflow-x:
        auto;

    white-space:
        pre-wrap;

    overflow-wrap:
        anywhere;
}


/* ==========================================================================
   CHART CONTAINERS
   ========================================================================== */

[data-testid="stVegaLiteChart"],
[data-testid="stPlotlyChart"] {
    width: 100%;

    max-width: 100%;

    overflow: visible;

    padding: 0;

    border:
        1px solid var(--border-soft);

    border-radius:
        var(--radius-lg);

    background:
        color-mix(in srgb, var(--text-primary) 1%, transparent);
}


/* ==========================================================================
   IMAGES
   ========================================================================== */

[data-testid="stImage"] {
    max-width: 100%;
}


[data-testid="stImage"] img {
    max-width: 100%;

    height: auto;

    border-radius:
        var(--radius-lg);
}


/* ==========================================================================
   EMPTY STATES
   ========================================================================== */

.empty-state {
    position: relative;

    width: 100%;
    min-width: 0;

    overflow: hidden;

    padding:
        3.1rem
        2rem;

    text-align:
        center;

    border:
        1px dashed
        color-mix(in srgb, var(--primary) 18%, transparent);

    border-radius:
        var(--radius-xl);

    background:
        linear-gradient(
            145deg,
            color-mix(in srgb, var(--text-primary) 2%, transparent),
            color-mix(in srgb, var(--text-primary) 1%, transparent)
        );
}


.empty-state::before {
    content: "";

    position: absolute;

    width: 180px;
    height: 180px;

    left: 50%;
    top: -120px;

    transform:
        translateX(-50%);

    border-radius:
        50%;

    background:
        color-mix(in srgb, var(--primary) 6%, transparent);

    filter:
        blur(30px);
}


.empty-title {
    position: relative;

    max-width: 100%;

    color:
        var(--text-primary);

    font-size:
        1.08rem;

    font-weight:
        780;

    white-space:
        normal;

    overflow-wrap:
        anywhere;
}


.empty-message {
    position: relative;

    max-width:
        620px;

    margin:
        .52rem
        auto
        0;

    color:
        var(--text-secondary);

    font-size:
        .84rem;

    line-height:
        1.6;

    white-space:
        normal;

    overflow-wrap:
        anywhere;
}


.empty-hint {
    position: relative;

    margin-top:
        .9rem;

    color:
        var(--text-disabled);

    font-size:
        .74rem;

    white-space:
        normal;

    overflow-wrap:
        anywhere;
}


/* ==========================================================================
   PROGRESS
   ========================================================================== */

[data-testid="stProgress"] > div > div {
    border-radius:
        999px;
}


/* ==========================================================================
   TOAST
   ========================================================================== */

[data-testid="stToast"] {
    max-width:
        min(
            420px,
            90vw
        );

    border:
        1px solid var(--border);

    border-radius:
        var(--radius-md);

    background:
        color-mix(in srgb, var(--bg-main) 94%, transparent);

    backdrop-filter:
        blur(16px);

    box-shadow:
        var(--shadow-lg);
}


[data-testid="stToast"] * {
    white-space:
        normal;

    overflow-wrap:
        anywhere;
}


/* ==========================================================================
   DIALOGS
   ========================================================================== */

[data-testid="stDialog"] > div {
    max-width:
        min(
            920px,
            94vw
        );

    border:
        1px solid var(--border);

    border-radius:
        var(--radius-xl);

    background:
        var(--bg-tertiary);
}


/* ==========================================================================
   TOOLTIPS
   ========================================================================== */

[data-baseweb="tooltip"],
[role="tooltip"] {
    max-width:
        min(
            420px,
            90vw
        ) !important;

    white-space:
        normal !important;

    overflow-wrap:
        anywhere !important;
}


/* ==========================================================================
   LINKS
   ========================================================================== */

a {
    max-width: 100%;

    overflow-wrap:
        anywhere;

    word-break:
        break-word;
}


/* ==========================================================================
   DIVIDERS
   ========================================================================== */

hr {
    border: none;

    border-top:
        1px solid var(--border-soft);
}


/* ==========================================================================
   FOCUS / ACCESSIBILITY
   ========================================================================== */

button:focus-visible,
input:focus-visible,
textarea:focus-visible,
[role="combobox"]:focus-visible,
summary:focus-visible,
[tabindex]:focus-visible {
    outline:
        2px solid
        color-mix(in srgb, var(--primary) 75%, transparent);

    outline-offset:
        2px;
}


/* ===========================================================================
   PRODUCT INTERACTION POLISH
   =========================================================================== */

/* Main-workspace radios are used as compact workflow selectors. This keeps
   Claim Analysis visually calm while making the active operating mode clear. */
[data-testid="stMain"] [data-testid="stRadio"] > div {
    gap: .45rem;
}


[data-testid="stMain"] [data-testid="stRadio"] label {
    min-height: 42px;

    padding: .45rem .78rem;

    border: 1px solid var(--border-soft);
    border-radius: 10px;

    background: color-mix(in srgb, var(--text-primary) 1.8%, transparent);

    transition:
        transform var(--transition-fast),
        background var(--transition-fast),
        border-color var(--transition-fast),
        box-shadow var(--transition-fast);
}


[data-testid="stMain"] [data-testid="stRadio"] label:hover {
    transform: translateY(-1px);

    border-color: color-mix(in srgb, var(--primary) 34%, transparent);

    background: color-mix(in srgb, var(--primary) 6.5%, transparent);
}


[data-testid="stMain"] [data-testid="stRadio"] label:has(input:checked) {
    border-color: color-mix(in srgb, var(--primary) 58%, transparent);

    background:
        linear-gradient(
            135deg,
            color-mix(in srgb, var(--primary) 16%, transparent),
            color-mix(in srgb, var(--primary) 10%, transparent)
        );

    box-shadow:
        0 8px 22px color-mix(in srgb, var(--primary) 13%, transparent);
}


[data-testid="stMain"] [data-testid="stRadio"] label p {
    color: var(--text-secondary);

    font-size: .82rem;
    font-weight: 700;
}


/* Make primary actions easier to scan and operate on desktop and touch
   devices without changing the visual language of secondary actions. */
.stButton > button,
.stDownloadButton > button,
[data-testid="stFormSubmitButton"] > button {
    line-height: 1.25;

    touch-action: manipulation;
}


@media (hover: none) {

    .stButton > button:hover,
    .stDownloadButton > button:hover,
    [data-testid="stFormSubmitButton"] > button:hover,
    [data-testid="stMain"] [data-testid="stRadio"] label:hover {
        transform: none;
    }

}


@media (prefers-contrast: more) {

    :root {
        --border-soft: color-mix(in srgb, var(--text-primary) 18%, transparent);
        --border: color-mix(in srgb, var(--text-primary) 28%, transparent);
        --text-secondary: var(--text-secondary);
        --text-muted: var(--text-secondary);
    }

}


/* ==========================================================================
   SELECTION
   ========================================================================== */

::selection {
    color:
        var(--text-primary);

    background:
        color-mix(in srgb, var(--primary) 38%, transparent);
}


/* ==========================================================================
   SCROLLBAR
   ========================================================================== */

::-webkit-scrollbar {
    width:
        8px;

    height:
        8px;
}


::-webkit-scrollbar-track {
    background:
        transparent;
}


::-webkit-scrollbar-thumb {
    background:
        color-mix(in srgb, var(--text-primary) 11.5%, transparent);

    border-radius:
        999px;
}


::-webkit-scrollbar-thumb:hover {
    background:
        color-mix(in srgb, var(--text-primary) 20%, transparent);
}


/* ==========================================================================
   GLOBAL CONTENT SAFETY
   ========================================================================== */

.metric-value,
.mini-metric-label,
.mini-metric-value,
.mini-metric-helper,
.risk-gauge-value,
.risk-gauge-tier,
.section-title,
.page-intro-title,
.page-intro-eyebrow,
.dashboard-title,
.info-panel-title,
.info-panel-message,
.surface-card-title,
.surface-card-subtitle,
.decision-panel-title,
.decision-panel-message,
.decision-panel-caption,
.driver-direction,
.driver-label,
.driver-value,
.driver-contribution,
.key-value-label,
.key-value-value,
.empty-title,
.empty-message,
[data-testid="stMetricValue"],
[data-testid="stMetricLabel"],
[data-testid="stCaptionContainer"] {
    overflow:
        visible !important;

    text-overflow:
        clip !important;

    white-space:
        normal !important;

    overflow-wrap:
        anywhere !important;

    word-break:
        normal !important;
}


/* Generic business-value safety */

.model-name,
.model-value,
.action-value,
.status-value,
.claim-id,
.technical-value,
.business-value,
.business-label,
.card-value,
.card-label {
    max-width:
        100%;

    overflow:
        visible !important;

    text-overflow:
        clip !important;

    white-space:
        normal !important;

    overflow-wrap:
        anywhere !important;

    word-break:
        normal !important;
}


/* Never force important cards to one line */

.glass-card,
.metric-card-pro,
.mini-metric,
.surface-card-heading,
.info-panel,
.decision-panel,
.driver-card,
.empty-state,
[data-testid="stMetric"],
[data-testid="stAlert"],
[data-testid="stExpander"],
[data-testid="stForm"] {
    min-width:
        0;

    overflow-wrap:
        anywhere;
}


/* ==========================================================================
   RESPONSIVE — LARGE TABLET / LAPTOP
   ========================================================================== */

@media (max-width: 1300px) {

    .block-container {
        padding-left:
            2rem;

        padding-right:
            2rem;
    }


    div[data-testid="stMetricValue"] {
        font-size:
            clamp(
                1.35rem,
                2.3vw,
                2.1rem
            ) !important;
    }


    .metric-value {
        font-size:
            clamp(
                1.2rem,
                2vw,
                1.75rem
            );
    }

}


/* ==========================================================================
   RESPONSIVE — TABLET
   ========================================================================== */

@media (max-width: 1100px) {

    .block-container {
        padding-left:
            1.6rem;

        padding-right:
            1.6rem;
    }


    .glass-card {
        min-height:
            118px;
    }


    .mini-metric {
        min-height:
            90px;
    }


    .metric-value {
        font-size:
            clamp(
                1.2rem,
                2.5vw,
                1.65rem
            );
    }


    div[data-testid="stMetricValue"] {
        font-size:
            clamp(
                1.3rem,
                2.8vw,
                1.95rem
            ) !important;
    }


    .risk-gauge-ring {
        width:
            210px;
    }


    .driver-meta {
        gap:
            .5rem
            1rem;
    }


    .key-value-row {
        grid-template-columns:
            minmax(110px, .7fr)
            minmax(0, 1.3fr);
    }

}


/* ==========================================================================
   RESPONSIVE — MOBILE
   ========================================================================== */

@media (max-width: 700px) {

    /* Streamlit preserves desktop column rows by default. On phones, stack
       every card and result panel before labels are compressed vertically. */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 1rem !important;
    }


    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        flex: 1 1 100% !important;
        width: 100% !important;
    }


    .block-container {
        padding-top:
            3.5rem;

        padding-left:
            1rem;

        padding-right:
            1rem;

        padding-bottom:
            2.5rem;
    }


    .dashboard-title {
        font-size:
            2.05rem;

        line-height:
            1.08;
    }


    .dashboard-subtitle {
        margin-bottom:
            1rem;

        font-size:
            .88rem;
    }


    .page-context-strip {
        display:
            flex;

        width:
            fit-content;

        flex-wrap:
            wrap;
    }


    .page-intro-eyebrow {
        font-size:
            .63rem;
    }


    .glass-card,
    .metric-card-pro,
    div[data-testid="stMetric"] {
        min-height:
            auto;

        padding:
            1.1rem;
    }


    .surface-card-heading {
        padding:
            .82rem
            .9rem
            .82rem
            1.05rem;
    }


    .mini-metric {
        min-height:
            auto;

        padding:
            .85rem
            .9rem;
    }


    .mini-metric-value {
        font-size:
            1.15rem;
    }


    .metric-value {
        font-size:
            1.4rem;
    }


    div[data-testid="stMetricValue"] {
        font-size:
            1.6rem !important;
    }


    .section-title {
        font-size:
            1.15rem;
    }


    [data-testid="stFileUploaderDropzone"] {
        padding:
            1.4rem
            1rem;
    }


    .risk-gauge-wrapper {
        padding:
            1rem
            0;
    }


    .risk-gauge-ring {
        width:
            min(
                205px,
                70vw
            );
    }


    .risk-gauge-value {
        font-size:
            1.9rem;
    }


    .risk-badge {
        min-width:
            84px;
    }


    .info-panel {
        padding:
            .9rem
            1rem;
    }


    .decision-panel {
        padding:
            .92rem
            1rem;
    }


    .driver-card {
        padding:
            .88rem
            .92rem;
    }


    .driver-meta {
        flex-direction:
            column;

        gap:
            .48rem;
    }


    .key-value-row {
        grid-template-columns:
            1fr;

        gap:
            .22rem;

        padding:
            .65rem
            .1rem;
    }


    .key-value-value {
        text-align:
            left;
    }


    .soft-divider-label {
        max-width:
            82%;
    }

}


/* ==========================================================================
   VERY SMALL MOBILE
   ========================================================================== */

@media (max-width: 420px) {

    .block-container {
        padding-left:
            .75rem;

        padding-right:
            .75rem;
    }


    .dashboard-title {
        font-size:
            1.75rem;
    }


    .surface-card-title {
        font-size:
            .86rem;
    }


    .metric-value {
        font-size:
            1.25rem;
    }


    .mini-metric-value {
        font-size:
            1.05rem;
    }


    div[data-testid="stMetricValue"] {
        font-size:
            1.4rem !important;
    }


    .risk-gauge-ring {
        width:
            min(
                185px,
                72vw
            );
    }


    .decision-panel-message {
        font-size:
            .82rem;
    }


    .driver-label {
        font-size:
            .84rem;
    }

}


/* ==========================================================================
   REDUCED MOTION
   ========================================================================== */

@media (
    prefers-reduced-motion:
    reduce
) {

    *,
    *::before,
    *::after {
        scroll-behavior:
            auto !important;

        transition-duration:
            0.01ms !important;

        animation-duration:
            0.01ms !important;

        animation-iteration-count:
            1 !important;
    }

}

/* Compact workspace hierarchy and grouped navigation. */
[data-testid="stSidebarCollapseButton"] { visibility: visible !important; opacity: 1 !important; }

.app-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: .65rem;
    margin-bottom: 1rem;
    padding-bottom: .9rem;
    border-bottom: 1px solid var(--border-soft);
}
.app-wordmark { color: var(--text-secondary); font-size: .9rem; font-weight: 700; }
.app-topbar .page-context-strip { margin: 0; border-radius: 9px; font-size: .77rem; }
h1.section-title { font-size: clamp(1.55rem, 2.5vw, 1.95rem); line-height: 1.2; }
h2.section-title { font-size: 1.22rem; line-height: 1.3; }
h3.section-title { font-size: 1.08rem; line-height: 1.35; }
.section-heading .section-title { margin: 0; padding: 0; }
.section-heading { margin-top: .65rem; margin-bottom: .85rem; }
.section-subtitle { font-size: .9rem; color: var(--text-secondary); }
.section-eyebrow { font-size: .74rem; letter-spacing: .09em; }
.sidebar-brand { margin-bottom: .7rem; }
.sidebar-brand-title { font-size: 1.1rem; font-weight: 800; letter-spacing: -.02em; }
.sidebar-brand-subtitle { font-size: .78rem; color: var(--text-secondary) !important; margin-top: .35rem; }
.nav-group-label { font-size: .75rem; font-weight: 700; letter-spacing: .07em; text-transform: uppercase; margin: .9rem 0 .15rem; color: var(--text-secondary) !important; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: .4rem; }
[data-testid="stSidebar"] .stButton > button {
    min-height: 44px;
    text-align: left;
    justify-content: flex-start;
    border: 1px solid transparent;
    background: transparent;
    box-shadow: none;
    padding: .6rem .8rem;
    border-radius: 10px;
}
[data-testid="stSidebar"] button[kind="primary"],
[data-testid="stSidebar"] button[kind="secondary"] {
    min-height: 44px;
    text-align: left;
    justify-content: flex-start;
    border: 1px solid transparent;
    background: transparent;
    box-shadow: none;
    padding: .6rem .8rem;
    border-radius: 10px;
}
[data-testid="stSidebar"] .nav-group-label { font-size: .75rem; margin: .9rem 0 .15rem; }
[data-testid="stSidebar"] [data-testid="stButton"] button,
[data-testid="stSidebar"] .stButton button {
    min-height: 44px;
    text-align: left;
    justify-content: flex-start;
    border: 1px solid transparent;
    background: transparent;
    box-shadow: none;
    padding: .6rem .8rem;
    border-radius: 10px;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: color-mix(in srgb, var(--primary) 15%, transparent);
    border-color: color-mix(in srgb, var(--primary) 35%, transparent);
    box-shadow: inset 3px 0 0 var(--primary-text);
}
[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] {
    background: color-mix(in srgb, var(--primary) 15%, transparent);
    border-color: color-mix(in srgb, var(--primary) 35%, transparent);
    box-shadow: inset 3px 0 0 var(--primary-text);
}
.stButton button, [data-testid="stButton"] button,
.stDownloadButton button { min-height: 44px; }
button[kind="primary"], button[kind="secondary"] { min-height: 44px; }
[data-testid="stMain"] button:focus-visible,
[data-testid="stSidebar"] button:focus-visible {
    outline: 2px solid var(--primary-text);
    outline-offset: 3px;
}
[data-testid="stSidebar"] .stButton > button:hover { background: color-mix(in srgb, var(--primary) 8%, transparent); transform: none; }
.sidebar-page-context { margin-top: .6rem; padding: .7rem .8rem; border-left: 2px solid var(--border-strong); }
.sidebar-page-category { display: block; font-size: .7rem; font-weight: 700; letter-spacing: .08em; color: var(--primary-text) !important; }
.sidebar-page-description { display: block; margin-top: .3rem; font-size: .82rem; line-height: 1.5; color: var(--text-secondary) !important; }
.sidebar-product-meta { color: var(--text-secondary); font-size: .76rem; }
.metric-card-pro { min-height: 118px; border-radius: 16px; }
.metric-label { font-size: .78rem; letter-spacing: .06em; line-height: 1.4; min-height: 1.4em; }
.metric-helper { font-size: .81rem; line-height: 1.5; color: var(--text-secondary); }
.mini-metric-label { font-size: .77rem; color: var(--text-secondary); }
.mini-metric-helper { font-size: .77rem; color: var(--text-secondary); }
input::placeholder, textarea::placeholder,
div[data-baseweb="input"] input::placeholder,
div[data-baseweb="textarea"] textarea::placeholder {
    color: var(--text-secondary) !important;
    -webkit-text-fill-color: var(--text-secondary) !important;
}
.empty-hint { color: var(--text-secondary); font-size: .81rem; }
[data-testid="stSegmentedControl"] button { min-height: 44px; }
[data-testid="stButtonGroup"] button { min-height: 44px; }
[data-testid="stTabs"] [role="tab"] { min-height: 44px; font-size: .88rem; }
[data-testid="stMetric"] { min-height: 108px; }

@media (max-width: 700px) {
    .app-topbar { margin-bottom: .7rem; padding-bottom: .6rem; gap: .4rem; }
    .app-wordmark { font-size: .8rem; }
    .app-topbar .page-context-strip { font-size: .72rem; padding: .3rem .5rem; }
    h1.section-title { font-size: 1.55rem; }
    h2.section-title { font-size: 1.18rem; }
    .section-subtitle { font-size: .86rem; }
    .metric-card-pro { min-height: 108px; padding: .9rem; }
    .metric-label { font-size: .75rem; }
    .metric-helper { font-size: .78rem; }
    .risk-gauge-wrapper { display: none; }
    [data-testid="stTabs"] [role="tablist"] { overflow-x: auto; scrollbar-width: thin; }
    [data-testid="stTabs"] [role="tab"] { flex-shrink: 0; }
    .stButton > button, .stDownloadButton > button { min-height: 44px; }
}
@media (max-width: 900px) {
    [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        flex: 1 1 100% !important;
        width: 100% !important;
    }
}
@media (min-width: 360px) and (max-width: 1100px) {
    .st-key-science_kpis [data-testid="stHorizontalBlock"],
    .st-key-overview_kpis [data-testid="stHorizontalBlock"],
    .st-key-portfolio_kpis [data-testid="stHorizontalBlock"],
    .st-key-queue_summary [data-testid="stHorizontalBlock"],
    .st-key-model_metrics [data-testid="stHorizontalBlock"],
    .st-key-service_metrics [data-testid="stHorizontalBlock"],
    .st-key-capacity_metrics [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
    .st-key-science_kpis [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
    .st-key-overview_kpis [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
    .st-key-portfolio_kpis [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
    .st-key-queue_summary [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
    .st-key-model_metrics [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
    .st-key-service_metrics [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
    .st-key-capacity_metrics [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        flex: 1 1 calc(50% - .5rem) !important;
        width: calc(50% - .5rem) !important;
    }
    .st-key-science_kpis [data-testid="stMetric"] { padding: .8rem; }
    .st-key-overview_kpis .metric-card-pro { padding: .8rem; }
}


/* Appearance remains available in the native menu, including on small screens. */
[data-testid="stMainMenuButton"] {
    visibility: visible;
    min-height: 44px;
    min-width: 108px;
    margin-right: .5rem;
    border: 1px solid var(--border);
    border-radius: 10px;
    background: var(--card-bg);
    color: var(--text-primary);
}
[data-testid="stMainMenuButton"]::before { content: "Appearance"; font-size: .81rem; font-weight: 650; }
.st-key-theme_adapter { height: 0 !important; min-height: 0 !important; margin: 0 !important; }
.metric-card-pro, .mini-metric, .glass-card, .info-panel,
.decision-panel, [data-testid="stMetric"] { background-color: var(--card-bg); }
button[kind="primary"], [data-testid="stBaseButton-primary"],
[data-testid="stBaseButton-primaryFormSubmit"] {
    color: var(--on-accent) !important;
    background: linear-gradient(135deg, #2458D3, #6848C6) !important;
    border-color: transparent !important;
}
button[kind="primary"] *, [data-testid="stBaseButton-primary"] *,
[data-testid="stBaseButton-primaryFormSubmit"] * { color: var(--on-accent) !important; }
:root[data-fraud-theme="light"] [data-testid="stSidebar"] img[alt="Logo"] { filter: brightness(.25); }
:root[data-fraud-theme="light"] input::-webkit-calendar-picker-indicator { filter: none; }
:root[data-fraud-theme="light"] .glass-card,
:root[data-fraud-theme="light"] .metric-card-pro { background: var(--card-bg); }
/* Native tables, alerts, charts and tooltips are themed by config.toml. */
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {
    color: var(--text-muted) !important;
    opacity: 1;
}
/* Native Vega labels default to a faint neutral in light mode. Keep the
   interactive SVG's labels in sync with the same accessible text palette. */
[data-testid="stVegaLiteChart"] .role-axis-label text,
[data-testid="stVegaLiteChart"] .role-legend-label text {
    fill: var(--text-secondary) !important;
}
[data-testid="stVegaLiteChart"] .role-axis-title text,
[data-testid="stVegaLiteChart"] .role-legend-title text {
    fill: var(--text-primary) !important;
}

</style>
"""
