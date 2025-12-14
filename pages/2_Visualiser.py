import streamlit as st
import pandas as pd
import os
import json
import streamlit.components.v1 as components

from streamlit_extras.stylable_container import stylable_container
from pathlib import Path

from core.data_loader import load_city_dataframe
from core.geo import get_city_coords
from viz.maps import make_price_map
from viz.plots import price_surface_scatter, weekly_price_evolution, annonces_distribution_pie
from viz.stats import basic_stats, weekly_median
from gpt_agent.gpt_assistant import GPTAssistant 
from gpt_agent.prompts import build_dashboard_analysis_prompt
from gpt_agent.pdf_generator import generate_comparison_report

from image_service.dashboard_to_image import dashboard_to_image

# -------------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------------
st.set_page_config(page_title="Visualisation", page_icon="📊", layout="wide")
st.title("📊 Visualisation des données")


# -------------------------------------------------------------------
# DATA
# -------------------------------------------------------------------
def get_scraped_cities():
    root = Path("jsons")
    return sorted([d.name.capitalize() for d in root.iterdir() if d.is_dir()]) if root.exists() else []


cities = get_scraped_cities()
if not cities:
    st.warning("⚠️ Aucune ville scrapée.")
    st.stop()


# -------------------------------------------------------------------
# UI — Sélection
# -------------------------------------------------------------------
st.markdown("---")
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    city1 = st.selectbox("Ville 1", cities)

with col2:
    city2 = st.selectbox("Ville 2", [c for c in cities if c != city1])

with col3:
    st.markdown("<br>", unsafe_allow_html=True)
    launch = st.button("Visualiser", use_container_width=True)


# -------------------------------------------------------------------
# LOAD DATA
# -------------------------------------------------------------------
if launch:
    with st.spinner("Chargement des données…"):
        # Convertir en minuscules pour accéder aux dossiers (jsons/lyon, jsons/paris, etc.)
        df1 = load_city_dataframe(city1.lower())
        df2 = load_city_dataframe(city2.lower())

    st.session_state.df1 = df1
    st.session_state.df2 = df2
    st.session_state.show = True


# -------------------------------------------------------------------
# VISUALISATION
# -------------------------------------------------------------------
if st.session_state.get("show", False):
    df1 = st.session_state.df1
    df2 = st.session_state.df2

    st.success(f"📊 {city1} vs {city2}")

    # Stats
    s1 = basic_stats(df1)
    s2 = basic_stats(df2)

    colA, colB, colC = st.columns([3, 2, 2])
    with colA:
        st.plotly_chart(annonces_distribution_pie(df1, df2, city1, city2), use_container_width=True)
    with colB:
        st.metric(f"{city1} – Prix médian", f"{s1['median']:,.0f} € / m²")
        st.metric(f"{city1} – Annonces", s1["count"])
    with colC:
        st.metric(f"{city2} – Prix médian", f"{s2['median']:,.0f} € / m²")
        st.metric(f"{city2} – Annonces", s2["count"])

    st.header("📉 Prix / Surface")

    use_log = st.checkbox("Échelle Logarithmique", value=True)
    
    st.plotly_chart(
        price_surface_scatter(df1, df2, city1, city2, use_log=use_log),
        use_container_width=True,
    )



    # Weekly
    st.header("📈 Évolution temporelle")
    date1 = "update_date" if "update_date" in df1.columns else "creation_date"
    date2 = "update_date" if "update_date" in df2.columns else "creation_date"

    weekly_all = pd.concat([
    weekly_median(df1, city1, date1).assign(city_role=city1),
    weekly_median(df2, city2, date2).assign(city_role=city2),
])


    st.plotly_chart(weekly_price_evolution(weekly_all), use_container_width=True)

    # Maps
    st.header("🗺️ Cartes")
    
    map_mode = st.radio(
        "Type de carte",
        ["Densité", "Prix au m²"],
        horizontal=True,
    )
    
    colA, colB = st.columns(2)

    with colA:
        coords1 = get_city_coords(city1.lower())
        if map_mode == "Densité":
            st.pydeck_chart(make_price_map(df1, coords1["lat"], coords1["lon"]))
        else:
            st.pydeck_chart(make_price_map(df1, coords1["lat"], coords1["lon"], show_heatmap=False))

    with colB:
        coords2 = get_city_coords(city2.lower())
        if map_mode == "Densité":
            st.pydeck_chart(make_price_map(df2, coords2["lat"], coords2["lon"]))
        else:
            st.pydeck_chart(make_price_map(df2, coords2["lat"], coords2["lon"], show_heatmap=False))
            
    # IA
    st.markdown("---")
    st.header("🤖 Assistant IA")

    key_file = Path("config/api_key.json")
    if key_file.exists():
        st.session_state["openai_api_key"] = json.loads(key_file.read_text()).get("openai_api_key")

    if "openai_api_key" not in st.session_state:
        st.warning("Ajoutez votre clé API dans Configuration.")
        st.stop()

    os.environ["OPENAI_API_KEY"] = st.session_state["openai_api_key"]
    assistant = GPTAssistant()

    question = st.text_area("Question à l’assistant")
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        analyze_btn = st.button("Analyser", use_container_width=True)
    
    with col_btn2:
        pdf_btn = st.button("Générer un Rapport PDF", use_container_width=True)
    
    if analyze_btn:
        
        with st.spinner("Génération de l'image…"):
            # Utiliser le mode choisi par l'utilisateur
            use_heatmap = (map_mode == "Densité")
            dash_img = dashboard_to_image(
                plt=[
                    annonces_distribution_pie(df1, df2, city1, city2),
                    price_surface_scatter(df1, df2, city1, city2, use_log=use_log), 
                    weekly_price_evolution(weekly_all)
                ], 
                pdk=[make_price_map(df1, coords1["lat"], coords1["lon"], show_heatmap=False, zoom=13), 
                     make_price_map(df2, coords2["lat"], coords2["lon"], show_heatmap=False, zoom=13)]
            )
        st.success("Image sauvegardée dans le dossier imgs/")
        
        with st.spinner("Analyse…"):
            # Construire le prompt avec la fonction dédiée
            prompt = build_dashboard_analysis_prompt(
                city1, city2,
                s1, s2,
                weekly_all[weekly_all.city == city1]["median_price_m2"].tolist(),
                weekly_all[weekly_all.city == city2]["median_price_m2"].tolist(),
                question
            )
            
            # Appeler l'assistant avec le prompt et l'image
            result = assistant.ask_with_image(prompt, dash_img)

        st.write(result)
    
    if pdf_btn:
        # Créer les éléments de progression
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(progress: int, message: str):
            progress_bar.progress(progress)
            status_text.text(message)
        
        update_progress(10, "📸 Génération des images...")
        dash_img = dashboard_to_image(
            plt=[
                annonces_distribution_pie(df1, df2, city1, city2),
                price_surface_scatter(df1, df2, city1, city2, use_log=use_log), 
                weekly_price_evolution(weekly_all)
            ], 
            pdk=[make_price_map(df1, coords1["lat"], coords1["lon"], show_heatmap=False, zoom=13), 
                 make_price_map(df2, coords2["lat"], coords2["lon"], show_heatmap=False, zoom=13)]
        )
        
        update_progress(20, "📄 Génération du rapport PDF...")
        pdf_path = generate_comparison_report(
            city1=city1,
            city2=city2,
            df1=df1,
            df2=df2,
            stats1=s1,
            stats2=s2,
            weekly1=weekly_all[weekly_all.city == city1]["median_price_m2"].tolist(),
            weekly2=weekly_all[weekly_all.city == city2]["median_price_m2"].tolist(),
            question=question or "Quelle ville est la plus attractive pour investir ?",
            output_path="imgs/rapport_comparatif.pdf",
            progress_callback=update_progress
        )
        
        progress_bar.progress(100)
        status_text.text("✅ Rapport terminé !")
        st.success(f"✅ Rapport PDF généré : {pdf_path}")
        
        # Télécharger le PDF
        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="📥 Télécharger le rapport PDF",
                data=pdf_file,
                file_name=f"rapport_{city1}_vs_{city2}.pdf",
                mime="application/pdf",
                use_container_width=True
            )


