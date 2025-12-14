import sys
import threading
from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from streamlit_autorefresh import st_autorefresh

# ─────────────────────────────
# CORE / ORCHESTRATION
# ─────────────────────────────
from orchestrator import run_with_auto_refresh
from core.location import location_autocomplete
from core.http import BrowserSession
from core.utils import normalize_city

# ─────────────────────────────
# CONFIG
# ─────────────────────────────
st.set_page_config(page_title="Scraping", page_icon="🏠", layout="centered")

SESSION_PATH = Path("cookies/seloger_session.json")
STOP_FLAG = Path(__file__).parent.parent / "stop_scraping.flag"

# ─────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────
defaults = {
    "is_scraping": False,
    "scraping_city1": None,
    "scraping_city2": None,
    "scraping_city1_raw": None,
    "scraping_city2_raw": None,
}

for k, v in defaults.items():
    st.session_state.setdefault(k, v)

if st.session_state.is_scraping:
    st_autorefresh(interval=2000, key="scrape_refresh")

# ─────────────────────────────
# DATA : communes
# ─────────────────────────────
@st.cache_data
def load_communes():
    df = pd.read_csv("data/merged_cities_communes.csv")
    return df["city"].unique().tolist()

communes = load_communes()

# ─────────────────────────────
# UI : Sélection villes
# ─────────────────────────────
st.title("🏠 Scraping SeLoger")

col1, col2, col3 = st.columns([2, 1, 2])

with col1:
    city1 = st.selectbox(
        "Ville 1",
        [""] + communes,
        disabled=st.session_state.is_scraping,
    )

with col2:
    st.markdown(
        "<div style='text-align:center; padding-top:30px; "
        "font-size:24px; font-weight:bold;'>VS</div>",
        unsafe_allow_html=True,
    )

with col3:
    # Exclure city1 de la liste
    available_cities = [""] + [c for c in communes if c != city1]
    city2 = st.selectbox(
        "Ville 2",
        available_cities,
        disabled=st.session_state.is_scraping,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────
# START / STOP
# ─────────────────────────────
col_btn = st.columns([1, 2, 1])

with col_btn[1]:

    # ── STOP ─────────────────
    if st.session_state.is_scraping:
        with stylable_container(
            "red_button",
            css_styles="button { background-color:#CE0E00; color:white; }",
        ):
            if st.button("🛑 STOP", use_container_width=True):
                STOP_FLAG.touch()
                st.session_state.is_scraping = False
                st.rerun()

    # ── START ────────────────
    else:
        with stylable_container(
            "green_button",
            css_styles="button { background-color:#00AE00; color:white; }",
        ):
            if st.button("▶️ START", use_container_width=True):
                if not city1 or not city2:
                    st.error("⚠️ Veuillez renseigner les deux villes")
                else:
                    try:
                        session = BrowserSession()

                        id1, api_name1 = location_autocomplete(city1, session)
                        id2, api_name2 = location_autocomplete(city2, session)

                        clean1 = normalize_city(api_name1)
                        clean2 = normalize_city(api_name2)

                        st.session_state.scraping_city1 = clean1
                        st.session_state.scraping_city2 = clean2
                        st.session_state.scraping_city1_raw = api_name1
                        st.session_state.scraping_city2_raw = api_name2
                        st.session_state.is_scraping = True

                        STOP_FLAG.unlink(missing_ok=True)

                        cities = {clean1: id1, clean2: id2}

                        def scrape_thread():
                            try:
                                run_with_auto_refresh(cities, size=30)
                            finally:
                                STOP_FLAG.unlink(missing_ok=True)   # ← NETTOYAGE
                                st.session_state.is_scraping = False


                        threading.Thread(
                            target=scrape_thread,
                            daemon=True
                        ).start()

                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Erreur : {e}")

# ─────────────────────────────
# STATUT
# ─────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

if st.session_state.is_scraping:
    l1 = st.session_state.scraping_city1_raw
    l2 = st.session_state.scraping_city2_raw
    st.success(f"✅ Scraping en cours : {l1} vs {l2}")
else:
    st.info("En attente de démarrage…")

# ─────────────────────────────
# STATS
# ─────────────────────────────
def count_annonces(slug: str) -> int:
    if not slug:
        return 0
    p = Path("jsons") / slug / "annonces"
    return len(list(p.glob("*.json"))) if p.exists() else 0

st.markdown("---")
st.subheader("📊 Statistiques")

col_m1, col_m2 = st.columns(2)

c1 = st.session_state.scraping_city1
c2 = st.session_state.scraping_city2

with col_m1:
    st.metric("Annonces – Ville 1", count_annonces(c1))
    if c1:
        st.caption(st.session_state.scraping_city1_raw)

with col_m2:
    st.metric("Annonces – Ville 2", count_annonces(c2))
    if c2:
        st.caption(st.session_state.scraping_city2_raw)

# ─────────────────────────────
# HISTORIQUE
# ─────────────────────────────
st.markdown("---")
st.subheader("🗂️ Villes déjà scrapées")

root = Path("jsons")
if root.exists():
    rows = []
    for d in sorted(root.iterdir()):
        if d.is_dir():
            rows.append({
                "Ville": d.name.replace("_", " ").title(),
                "Dossier": d.name,
                "Annonces": count_annonces(d.name),
            })

    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune ville scrapée")
else:
    st.info("Aucune ville scrapée")
