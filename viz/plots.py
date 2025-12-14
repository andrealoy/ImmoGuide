# core/viz/plots.py
import pandas as pd
import plotly.express as px


# Couleurs par rôle (RGBA → mélange visuel)
ROLE_COLORS = {
    "Ville 1": "rgba(31, 119, 180, 0.35)",  # bleu
    "Ville 2": "rgba(255, 127, 14, 0.35)",  # orange
}


# --------------------------------------------------
# Scatter : Prix / Surface
# --------------------------------------------------
def price_surface_scatter(df1, df2, city1, city2, use_log=True):
    # Fusion simple
    df_all = pd.concat([
        df1.assign(city=city1, city_role=city1),
        df2.assign(city=city2, city_role=city2),
    ], ignore_index=True)

    # Création du Scatter avec Marginals et Log
    fig = px.scatter(
        df_all,
        x="livingSpace",
        y="price_m2",
        color="city_role",                # Génère automatiquement la légende
        color_discrete_map={              # Couleurs fixes
            city1: "#0062f4", 
            city2: "#d400ff"
        },
        opacity=0.5,                      # Transparence pour voir la densité
        log_x=use_log,                    # Échelle Log indispensable pour l'immo
        log_y=use_log,
        marginal_x="box",                 # Ajoute la distribution (box) en haut
        marginal_y="box",                 # Ajoute la distribution (box) à droite
        labels={
            "livingSpace": "Surface (m²)",
            "price_m2": "Prix au m² (€)",
            "city_role": "Ville",
            "city": "Ville"
        },
        title="Prix au m² vs Surface (Échelle Log)" if use_log else "Prix au m² vs Surface",
        hover_data={"city": True, "city_role": False}
    )

    # Nettoyage du layout
    fig.update_layout(
        height=600,                       # Un peu plus haut pour les marginaux
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"), # Légende en bas
        margin=dict(l=20, r=20, t=60, b=60)
    )

    return fig


# --------------------------------------------------
# Courbe temporelle (classique, lisible)
# --------------------------------------------------
def weekly_price_evolution(weekly_df):
    # Get unique cities for color mapping
    cities = weekly_df["city_role"].unique()
    color_map = {cities[0]: "#0062f4", cities[1]: "#d400ff"} if len(cities) >= 2 else {}
    
    fig = px.line(
        weekly_df,
        x="week",
        y="smooth",
        color="city_role",
        color_discrete_map=color_map,
        title="Évolution du prix MÉDIAN au m² (hebdomadaire, lissé)",
        labels={
            "week": "Semaine",
            "smooth": "Prix médian au m² (€)",
            "city_role": "Ville",
            "city": "Ville"
        },
        hover_data={"city": True, "city_role": False}
    )

    fig.update_traces(line=dict(width=3))
    fig.update_layout(height=450)

    return fig


# --------------------------------------------------
# Diagramme circulaire : Distribution des annonces
# --------------------------------------------------
def annonces_distribution_pie(df1, df2, city1, city2):
    """
    Affiche un diagramme circulaire montrant la distribution des annonces entre les deux villes.
    """
    counts = [len(df1), len(df2)]
    cities = [city1, city2]
    
    fig = px.pie(
        values=counts,
        names=cities,
        title="Distribution des annonces par ville",
        color_discrete_sequence=["#0062f4", "#d400ff"],  # Bleu et violet
        hole=0.3  # Donut chart pour un look moderne
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont_size=14
    )
    
    fig.update_layout(
        height=400,
        showlegend=True,
        legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center")
    )
    
    return fig
