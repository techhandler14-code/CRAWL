"""
styling.py

Shared visual styling for the whole dashboard. Every page calls
inject_custom_css() and render_sidebar_branding() once at the top, so the
look stays consistent without copy-pasting the same code into every file.
"""

import streamlit as st

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* Apply our heading/UI font everywhere by default */
html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
}

/* Data-heavy elements get the monospace font - phone numbers, tables */
[data-testid="stDataFrame"], code {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Hide Streamlit's default chrome - being conservative here after
   learning the hard way that hiding too much (like the toolbar) can
   also remove the sidebar's collapse/expand toggle. Only hiding what
   we're confident is safe: the hamburger menu and footer. The Deploy
   button staying visible is a small cosmetic trade-off for keeping
   navigation reliably working. */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Sidebar: give it a distinct surface color from the main background */
[data-testid="stSidebar"] {
    background-color: #1B1F29;
    border-right: 1px solid #262B38;
}

/* Buttons: rounded since they're interactive, using our accent color */
.stButton > button {
    border-radius: 6px;
    font-family: 'Sora', sans-serif;
    font-weight: 600;
    border: 1px solid #E8A33D;
    color: #E8A33D;
    background-color: transparent;
}
.stButton > button:hover {
    background-color: rgba(232, 163, 61, 0.1);
    color: #E8A33D;
}

/* Our custom metric card (used on the Home page hero stats) */
.metric-card {
    background-color: #1B1F29;
    border: 1px solid #262B38;
    border-radius: 4px;
    padding: 24px;
}
.metric-card .metric-value {
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    font-size: 2.5rem;
    color: #EDEEF0;
    line-height: 1.1;
}
.metric-card .metric-label {
    font-family: 'Sora', sans-serif;
    font-size: 0.9rem;
    color: #8B93A3;
    margin-top: 6px;
}

/* Status badges - color coding is functional, same colors used everywhere
   a status appears, so the meaning stays consistent across the whole app */
.status-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
    font-family: 'Sora', sans-serif;
}
.status-pending    { background-color: rgba(232, 163, 61, 0.15); color: #E8A33D; }
.status-no-reply   { background-color: rgba(201, 108, 92, 0.15); color: #C96C5C; }
.status-conversion { background-color: rgba(95, 168, 140, 0.15); color: #5FA88C; }

/* Logo wordmark - bold, letter-spaced app name with an accent-colored
   dot, sitting at the top of the sidebar */
.logo-wordmark {
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    font-size: 1.6rem;
    letter-spacing: 0.04em;
    color: #EDEEF0;
    margin-bottom: 0;
}
.logo-dot {
    color: #E8A33D;
}
</style>
"""


def inject_custom_css() -> None:
    """Call this once at the top of every page, right after st.set_page_config()."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def metric_card(label: str, value) -> None:
    """Renders one big-number stat card, e.g. metric_card('Total Leads', 142)."""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_badge(status: str) -> str:
    """
    Returns an HTML snippet for a colored status pill. This returns a
    string (not st.markdown directly) because it's usually embedded
    inside a table cell alongside other content, not shown standalone.
    """
    css_class_map = {
        "Pending": "status-pending",
        "No Reply": "status-no-reply",
        "Conversion": "status-conversion",
    }
    css_class = css_class_map.get(status, "status-pending")
    return f'<span class="status-badge {css_class}">{status}</span>'


def render_sidebar_branding() -> None:
    """
    Renders the branding block at the top of the sidebar - the CRAWL
    wordmark plus tagline. Every page was repeating this block before it
    got pulled into one shared function, so updating branding once here
    updates it everywhere, instead of hunting through every page file.
    """
    with st.sidebar:
        st.markdown(
            '<div class="logo-wordmark">CRAWL<span class="logo-dot">.</span></div>',
            unsafe_allow_html=True,
        )
        st.caption("Local business lead pipeline")