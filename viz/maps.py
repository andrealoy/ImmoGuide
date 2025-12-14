# core/viz/maps.py
import numpy as np
import pydeck as pdk

def make_price_map(df, lat, lon, show_heatmap=True, zoom=11):
    df = df.copy()

    # --- Auto-échelle à partir des données ---
    p_low, p_high = np.percentile(df["price_m2"], [5, 95])
    df["price_clipped"] = df["price_m2"].clip(p_low, p_high)

    def price_to_color(p):
        # On travaille sur les valeurs "clippées"
        p = np.clip(p, p_low, p_high)
        t = (p - p_low) / (p_high - p_low + 1e-9)
        return [
            int(255 * t),
            int(30 * (1 - t)),
            int(255 * (1 - t)),
            255,
        ]

    df["color"] = df["price_m2"].apply(price_to_color)

    df["weight"] = 1.0

    # ---------------------------
    # 1. HEATMAP LAYER (optionnel)
    # ---------------------------
    layers = []
    
    if show_heatmap:
        heat = pdk.Layer(
            "HeatmapLayer",
            df,
            get_position='[lon, lat]',
            get_weight="weight",
            radiusPixels=40,
            opacity=0.7,
            color_range = [
            [0, 0, 139],       # bleu foncé (faible densité)
            [75, 0, 130],      # violet
            [255, 69, 0],      # orange-rouge
            [255, 0, 0],       # rouge vif
            [255, 215, 0],     # jaune doré
            [255, 255, 255]    # blanc (haute densité)
        ]
        )
        layers.append(heat)
    else:
        # ---------------------------
        # 2. SCATTER LAYER (seulement si pas de heatmap)
        # ---------------------------
        points = pdk.Layer(
            "ScatterplotLayer",
            df,
            get_position='[lon, lat]',
            get_fill_color="color",
            get_radius=30,
            stroked=False,
            opacity=1,
            pickable=True,
        )
        layers.append(points)

    # ---------------------------
    # VIEW
    # ---------------------------
    view_state = pdk.ViewState(
        latitude=lat,
        longitude=lon,
        zoom=zoom,
        # pitch=45,
        bearing=20,
    )

    # ---------------------------
    # RENDER
    # ---------------------------
    r = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        # map_style="mapbox://styles/mapbox/dark-v11",
        tooltip={
            "html": "<b>Prix/m²:</b> {price_m2} €<br><b>Surface:</b> {livingSpace} m²",
            "style": {"color": "white"}
        }
    )

    return r

