"""Visual theme, assets, and styled components for the auction UI."""
from __future__ import annotations

import streamlit as st

BRAND_NAME = "BidVault"
BRAND_TAGLINE = "Premium Online Auctions"

CATEGORY_IMAGES = {
    "Electronics": "https://images.unsplash.com/photo-1498049794561-7780e7231661?w=800&q=80",
    "Books": "https://images.unsplash.com/photo-1512820790817-5977792398b6?w=800&q=80",
    "Sports": "https://images.unsplash.com/photo-1460353581641-37cadd9e4a00?w=800&q=80",
    "Collectibles": "https://images.unsplash.com/photo-1587280503325-4a5106115ec9?w=800&q=80",
    "Home & Kitchen": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=800&q=80",
}

# Fallback when imageURL is missing — matched against item name + description.
ITEM_KEYWORD_IMAGES: list[tuple[tuple[str, ...], str]] = [
    (
        ("stanley", "quencher", "tumbler", "water bottle", "hydration", "flask"),
        "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=800&q=80",
    ),
    (
        ("polaroid", "instant camera"),
        "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=800&q=80",
    ),
    (
        ("dune", "novel", "first edition"),
        "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=800&q=80",
    ),
    (
        ("nike", "jordan", "sneaker", "sneakers"),
        "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&q=80",
    ),
    (
        ("baseball", "card", "trading card", "rookie"),
        "https://images.unsplash.com/photo-1587280503325-4a5106115ec9?w=800&q=80",
    ),
    (
        ("walkman", "cassette", "sony"),
        "https://images.unsplash.com/photo-1618366712010-f17ae1096949?w=800&q=80",
    ),
    (
        ("camera",),
        "https://images.unsplash.com/photo-1495121553079-4c61bcacf109?w=800&q=80",
    ),
    (
        ("book",),
        "https://images.unsplash.com/photo-1512820790817-5977792398b6?w=800&q=80",
    ),
]

DEFAULT_ITEM_IMAGE = "https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800&q=80"

NAV_PAGES = [
    "Dashboard",
    "Auctions",
    "My Bids",
    "Seller Items",
    "Create Item",
    "Create Auction",
    "Payments",
    "Shipments",
    "Profile",
    "Admin",
]

HERO_IMAGES = {
    "login": "https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=1400&q=80",
    "dashboard": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=1400&q=80",
    "auctions": "https://images.unsplash.com/photo-1579621970795-87facc979f44?w=1400&q=80",
    "bids": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1400&q=80",
    "items": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=1400&q=80",
    "payments": "https://images.unsplash.com/photo-1556740758-90de374c12ad?w=1400&q=80",
    "shipments": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=1400&q=80",
    "profile": "https://images.unsplash.com/photo-1556155092-490a1ba16284?w=1400&q=80",
    "admin": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1400&q=80",
    "create": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1400&q=80",
}

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@400;500;600;700&display=swap');

:root {
    --bv-gold: #d4a853;
    --bv-gold-light: #f0c96a;
    --bv-gold-dark: #a67c2e;
    --bv-navy: #0c1220;
    --bv-navy-mid: #141c2e;
    --bv-navy-card: #1a2438;
    --bv-blue: #4d9fff;
    --bv-text: #e8ecf4;
    --bv-muted: #94a3b8;
}

.stApp {
    background:
        radial-gradient(ellipse at 10% 0%, rgba(212, 168, 83, 0.12) 0%, transparent 45%),
        radial-gradient(ellipse at 90% 10%, rgba(77, 159, 255, 0.08) 0%, transparent 40%),
        linear-gradient(165deg, #0c1220 0%, #111827 45%, #0f172a 100%);
    font-family: 'DM Sans', sans-serif;
}

.block-container {
    padding-top: 0.5rem;
    max-width: 1200px;
}

/* Hide left sidebar — navigation is in the top bar */
[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    display: none !important;
}

section.main .block-container {
    padding-top: 0.25rem;
}

.top-nav-wrapper [data-testid="stHorizontalBlock"] {
    gap: 0.35rem;
}

div[data-testid="stVerticalBlockBorderWrapper"]:has(.top-nav-brand) {
    background: linear-gradient(180deg, rgba(10, 15, 26, 0.98) 0%, rgba(18, 26, 43, 0.95) 100%) !important;
    border-color: rgba(212, 168, 83, 0.35) !important;
    border-radius: 14px !important;
    margin-bottom: 1.25rem !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
    position: sticky;
    top: 0.5rem;
    z-index: 999;
}

div[data-testid="stVerticalBlockBorderWrapper"]:has(.top-nav-brand) .stButton > button {
    font-size: 0.76rem !important;
    padding: 0.3rem 0.45rem !important;
    min-height: 2.1rem;
    white-space: nowrap;
}

.top-nav-brand {
    font-family: 'Playfair Display', serif;
    font-size: 1.35rem;
    font-weight: 700;
    background: linear-gradient(135deg, #f0c96a, #d4a853);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
}

.top-nav-tagline {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: var(--bv-muted);
}

.top-nav-user {
    text-align: right;
    font-size: 0.82rem;
    color: var(--bv-muted);
}

.top-nav-user strong {
    color: var(--bv-gold-light);
    display: block;
    font-size: 0.92rem;
}

div[data-testid="column"] .stButton > button[kind="secondary"] {
    background: rgba(26, 36, 56, 0.85) !important;
    color: #cbd5e1 !important;
    border: 1px solid rgba(212, 168, 83, 0.2) !important;
    font-size: 0.78rem !important;
    padding: 0.35rem 0.5rem !important;
    min-height: 2.2rem;
}

div[data-testid="column"] .stButton > button[kind="secondary"]:hover {
    border-color: rgba(212, 168, 83, 0.55) !important;
    color: var(--bv-gold-light) !important;
}

div[data-testid="column"] .stButton > button[kind="primary"] {
    font-size: 0.78rem !important;
    padding: 0.35rem 0.5rem !important;
    min-height: 2.2rem;
    box-shadow: 0 0 12px rgba(212, 168, 83, 0.35);
}

h1, h2, h3, .hero-title {
    font-family: 'Playfair Display', serif !important;
    letter-spacing: -0.02em;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0f1a 0%, #121a2b 100%);
    border-right: 1px solid rgba(212, 168, 83, 0.25);
}

[data-testid="stSidebar"] [data-testid="stMarkdown"] p,
[data-testid="stSidebar"] label {
    color: var(--bv-text) !important;
}

.sidebar-brand {
    text-align: center;
    padding: 0.5rem 0 1.25rem;
    margin-bottom: 0.5rem;
    border-bottom: 1px solid rgba(212, 168, 83, 0.3);
}

.sidebar-brand .brand-icon {
    font-size: 2rem;
    display: block;
    margin-bottom: 0.25rem;
}

.sidebar-brand .brand-name {
    font-family: 'Playfair Display', serif;
    font-size: 1.55rem;
    font-weight: 700;
    background: linear-gradient(135deg, #f0c96a, #d4a853, #a67c2e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.sidebar-brand .brand-tagline {
    display: block;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    color: var(--bv-muted);
    margin-top: 0.15rem;
}

.sidebar-user {
    background: rgba(212, 168, 83, 0.08);
    border: 1px solid rgba(212, 168, 83, 0.22);
    border-radius: 12px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.75rem;
}

.sidebar-user .user-name {
    font-weight: 600;
    color: var(--bv-gold-light);
    font-size: 1rem;
}

.sidebar-user .user-role {
    font-size: 0.8rem;
    color: var(--bv-muted);
    margin-top: 0.15rem;
}

.hero-banner {
    position: relative;
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 1.75rem;
    min-height: 200px;
    background-size: cover;
    background-position: center;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.45);
    border: 1px solid rgba(212, 168, 83, 0.35);
}

.hero-banner::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(
        105deg,
        rgba(12, 18, 32, 0.92) 0%,
        rgba(12, 18, 32, 0.65) 45%,
        rgba(12, 18, 32, 0.35) 100%
    );
}

.hero-content {
    position: relative;
    z-index: 1;
    padding: 2.25rem 2.5rem;
}

.hero-title {
    font-size: 2.35rem;
    font-weight: 700;
    color: #fff;
    margin: 0 0 0.4rem;
    line-height: 1.15;
}

.hero-subtitle {
    font-size: 1.05rem;
    color: #cbd5e1;
    margin: 0;
    max-width: 620px;
    line-height: 1.5;
}

.hero-badge {
    display: inline-block;
    margin-top: 1rem;
    padding: 0.35rem 0.85rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--bv-gold-light);
    background: rgba(212, 168, 83, 0.15);
    border: 1px solid rgba(212, 168, 83, 0.4);
}

.section-header {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    margin: 1.5rem 0 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid rgba(212, 168, 83, 0.35);
}

.section-header .section-icon {
    font-size: 1.35rem;
}

.section-header .section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.35rem;
    font-weight: 600;
    color: var(--bv-gold-light);
    margin: 0;
}

.metric-tile {
    background: linear-gradient(145deg, rgba(26, 36, 56, 0.95), rgba(20, 28, 46, 0.9));
    border: 1px solid rgba(212, 168, 83, 0.28);
    border-radius: 14px;
    padding: 1.25rem 1.35rem;
    text-align: center;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
    height: 100%;
}

.metric-tile .metric-label {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--bv-muted);
    margin-bottom: 0.35rem;
}

.metric-tile .metric-value {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--bv-gold-light);
    line-height: 1.1;
}

.auction-tile {
    background: linear-gradient(160deg, rgba(26, 36, 56, 0.98), rgba(15, 23, 42, 0.95));
    border: 1px solid rgba(212, 168, 83, 0.22);
    border-radius: 14px;
    overflow: hidden;
    margin-bottom: 1rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.auction-tile:hover {
    border-color: rgba(212, 168, 83, 0.5);
}

.auction-tile-img {
    width: 100%;
    height: 160px;
    object-fit: cover;
    display: block;
}

.auction-tile-body {
    padding: 1rem 1.15rem 1.15rem;
}

.auction-tile-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: #f1f5f9;
    margin: 0 0 0.35rem;
}

.auction-tile-meta {
    font-size: 0.82rem;
    color: var(--bv-muted);
    margin-bottom: 0.65rem;
}

.auction-tile-bid {
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--bv-gold-light);
}

.auction-tile-bid span {
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--bv-muted);
    display: block;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.status-pill {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
}

.status-active {
    background: rgba(34, 197, 94, 0.18);
    color: #4ade80;
    border: 1px solid rgba(34, 197, 94, 0.35);
}

.status-closed {
    background: rgba(248, 113, 113, 0.15);
    color: #fca5a5;
    border: 1px solid rgba(248, 113, 113, 0.35);
}

.status-pending {
    background: rgba(251, 191, 36, 0.15);
    color: #fcd34d;
    border: 1px solid rgba(251, 191, 36, 0.35);
}

.status-completed {
    background: rgba(34, 197, 94, 0.15);
    color: #86efac;
    border: 1px solid rgba(34, 197, 94, 0.3);
}

.status-shipped {
    background: rgba(77, 159, 255, 0.15);
    color: #93c5fd;
    border: 1px solid rgba(77, 159, 255, 0.35);
}

.card-panel {
    background: linear-gradient(160deg, rgba(26, 36, 56, 0.85), rgba(20, 28, 46, 0.9));
    border: 1px solid rgba(212, 168, 83, 0.2);
    border-radius: 14px;
    padding: 0.25rem;
}

[data-testid="stExpander"] {
    background: rgba(26, 36, 56, 0.6);
    border: 1px solid rgba(212, 168, 83, 0.22) !important;
    border-radius: 12px !important;
}

[data-testid="stExpander"] summary {
    font-weight: 600;
    color: #e2e8f0 !important;
}

div[data-testid="stMetric"] {
    background: rgba(26, 36, 56, 0.7);
    border: 1px solid rgba(212, 168, 83, 0.2);
    border-radius: 12px;
    padding: 0.75rem 1rem;
}

div[data-testid="stMetric"] label {
    color: var(--bv-muted) !important;
}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: var(--bv-gold-light) !important;
    font-family: 'Playfair Display', serif;
}

.stButton > button[kind="primary"],
.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    transition: all 0.2s ease;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #d4a853, #b8892e) !important;
    color: #0c1220 !important;
    border: none !important;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #f0c96a, #d4a853) !important;
    box-shadow: 0 4px 20px rgba(212, 168, 83, 0.4);
}

[data-testid="stTable"] {
    border-radius: 10px;
    overflow: hidden;
}

.login-showcase {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    margin-top: 1rem;
}

@media (max-width: 768px) {
    .login-showcase { grid-template-columns: 1fr; }
    .hero-title { font-size: 1.75rem; }
    .hero-content { padding: 1.5rem; }
}

.feature-strip {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin: 1.25rem 0 0;
}

.feature-chip {
    flex: 1;
    min-width: 140px;
    background: rgba(212, 168, 83, 0.08);
    border: 1px solid rgba(212, 168, 83, 0.2);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    text-align: center;
    font-size: 0.85rem;
    color: #cbd5e1;
}

.feature-chip strong {
    display: block;
    color: var(--bv-gold-light);
    font-size: 1.1rem;
    margin-bottom: 0.15rem;
}
</style>
"""


def inject_theme() -> None:
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def item_image_url(record: dict) -> str:
    url = record.get("imageurl")
    if url:
        return url

    name = (record.get("itemname") or "").lower()
    desc = (record.get("description") or "").lower()
    text = f"{name} {desc}"

    for keywords, image in ITEM_KEYWORD_IMAGES:
        if any(kw in text for kw in keywords):
            return image

    category = record.get("category", "")
    return CATEGORY_IMAGES.get(category, DEFAULT_ITEM_IMAGE)


def render_top_nav(user: dict, current_page: str) -> None:
    """Horizontal button navigation bar at the top of the page."""
    role_icons = {"Buyer": "🛒", "Seller": "🏪", "Admin": "⚙️"}
    icon = role_icons.get(user.get("role", ""), "👤")

    with st.container(border=True):
        header_col, logout_col = st.columns([5, 1])
        with header_col:
            st.markdown(
                f"""
                <div class="top-nav-brand">🔨 {BRAND_NAME}</div>
                <div class="top-nav-tagline">{BRAND_TAGLINE}</div>
                """,
                unsafe_allow_html=True,
            )
        with logout_col:
            st.markdown(
                f"""
                <div class="top-nav-user">
                    <strong>{icon} {user['login']}</strong>
                    {user.get('role', 'Buyer')}
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Logout", key="nav_logout", use_container_width=True):
                st.session_state.user = None
                st.session_state.page = "Login"
                st.rerun()

        nav_cols = st.columns(len(NAV_PAGES))
        for col, label in zip(nav_cols, NAV_PAGES):
            with col:
                is_active = label == current_page
                if st.button(
                    label,
                    key=f"nav_btn_{label}",
                    type="primary" if is_active else "secondary",
                    use_container_width=True,
                ):
                    if label != current_page:
                        st.session_state.page = label
                        st.rerun()


def hero_banner(title: str, subtitle: str, image_key: str, badge: str | None = None) -> None:
    image = HERO_IMAGES.get(image_key, HERO_IMAGES["auctions"])
    badge_html = f'<span class="hero-badge">{badge}</span>' if badge else ""
    st.markdown(
        f"""
        <div class="hero-banner" style="background-image: url('{image}');">
            <div class="hero-content">
                <h1 class="hero-title">{title}</h1>
                <p class="hero-subtitle">{subtitle}</p>
                {badge_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, icon: str = "✦") -> None:
    st.markdown(
        f"""
        <div class="section-header">
            <span class="section-icon">{icon}</span>
            <h3 class="section-title">{title}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_tile(label: str, value: str | int) -> None:
    st.markdown(
        f"""
        <div class="metric-tile">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_pill(status: str) -> str:
    mapping = {
        "Active": ("status-active", "● Live"),
        "Closed": ("status-closed", "● Closed"),
        "Pending": ("status-pending", "● Pending"),
        "Completed": ("status-completed", "● Paid"),
        "Failed": ("status-closed", "● Failed"),
        "Shipped": ("status-shipped", "● Shipped"),
        "Delivered": ("status-completed", "● Delivered"),
    }
    css_class, label = mapping.get(status, ("status-pending", f"● {status}"))
    return f'<span class="status-pill {css_class}">{label}</span>'


def auction_tile_html(
    title: str,
    category: str,
    seller: str,
    auction_id: int,
    bid: str,
    status: str,
    image_url: str,
) -> str:
    return f"""
    <div class="auction-tile">
        <img class="auction-tile-img" src="{image_url}" alt="{title}" />
        <div class="auction-tile-body">
            <div class="auction-tile-title">{title}</div>
            <div class="auction-tile-meta">
                #{auction_id} · {category} · {seller}
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div class="auction-tile-bid">
                    <span>Current bid</span>
                    {bid}
                </div>
                {status_pill(status)}
            </div>
        </div>
    </div>
    """


def sidebar_brand() -> None:
    st.markdown(
        f"""
        <div class="sidebar-brand">
            <span class="brand-icon">🔨</span>
            <span class="brand-name">{BRAND_NAME}</span>
            <span class="brand-tagline">{BRAND_TAGLINE}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_user(login: str, role: str) -> None:
    role_icons = {"Buyer": "🛒", "Seller": "🏪", "Admin": "⚙️"}
    icon = role_icons.get(role, "👤")
    st.markdown(
        f"""
        <div class="sidebar-user">
            <div class="user-name">{icon} {login}</div>
            <div class="user-role">{role}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def login_feature_strip() -> None:
    st.markdown(
        """
        <div class="feature-strip">
            <div class="feature-chip"><strong>Live</strong>Bidding rooms</div>
            <div class="feature-chip"><strong>Secure</strong>Payments</div>
            <div class="feature-chip"><strong>Fast</strong>Shipping</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
