# gpt_agent/prompts.py

import json


def build_dashboard_analysis_prompt(
    city1, city2,
    stats_city1, stats_city2,
    weekly_city1, weekly_city2,
    user_question
):
    """
    Construit un prompt pour l'analyse globale du dashboard.
    """
    prompt = f"""
    Tu es un expert en analyse immobilière, spécialisé dans l'interprétation de 
    tableaux de bord de données (dashboard analytics).

    Tu dois analyser à quelqu'un qui ne s'y connait pas les données de deux villes et expliquer, résumer le plus simplement possible :
    - leurs tendances immobilières
    - leurs différences structurelles
    - ce que racontent les courbes de prix médians
    - ce que montrent les cartes de densité et de prix
    - les insights les plus importants

    -----------------------------------------------------
    Ville 1 : {city1}
    -----------------------------------------------------
    Statistiques globales :
    {json.dumps(stats_city1, indent=2, ensure_ascii=False)}

    Tendance hebdomadaire (prix médian lissé) :
    {weekly_city1}

    -----------------------------------------------------
    Ville 2 : {city2}
    -----------------------------------------------------
    Statistiques globales :
    {json.dumps(stats_city2, indent=2, ensure_ascii=False)}

    Tendance hebdomadaire (prix médian lissé) :
    {weekly_city2}

    -----------------------------------------------------
    Question utilisateur :
    "{user_question}"
    -----------------------------------------------------

    Mission :
    Rédige une analyse fluide et professionnelle en 4-5 paragraphes.
    
    Couvre dans l'ordre :
    - Vue d'ensemble comparative (prix, volumes)
    - Évolution temporelle des prix (tendances, pics, stabilité)
    - Différences géographiques et patterns spatiaux
    - Réponse directe à la question utilisateur
    
    Format :
    - Texte en paragraphes fluides (pas de numérotation, pas de tirets)
    - Sauts de ligne entre les paragraphes
    - Langage clair et accessible
    - Pas de formules d'introduction/conclusion ("En résumé", "Pour conclure", etc.) 
    """
    
    return prompt.strip()


def build_single_chart_analysis_prompt(chart_type, city1, city2, context):
    """
    Construit un prompt pour l'analyse d'un graphique spécifique.
    
    Args:
        chart_type: Type de graphique (scatter, temporal, map, pie, etc.)
        city1, city2: Noms des villes
        context: Dictionnaire avec contexte additionnel
    """
    prompt = f"""
    Tu es un expert en analyse immobilière. Analyse ce graphique de type "{chart_type}" 
    comparant {city1} et {city2}.
    
    Contexte additionnel :
    {json.dumps(context, indent=2, ensure_ascii=False)}
    
    Rédige une analyse en 2-3 paragraphes courts et fluides.
    Décris ce que montre le graphique, les insights clés, et les conclusions pratiques.
    
    Format :
    - Texte en paragraphes (pas de listes, pas de numérotation)
    - Sauts de ligne entre paragraphes
    - Pas de formules génériques ("ce graphique montre que...", "en conclusion...")
    """
    
    return prompt.strip()


def build_pdf_report_prompt(city1, city2, all_stats):
    """
    Construit un prompt pour générer un rapport PDF complet.
    """
    prompt = f"""
    Tu es un expert en analyse immobilière. Génère un rapport d'analyse détaillé 
    comparant {city1} et {city2}.
    
    Données complètes :
    {json.dumps(all_stats, indent=2, ensure_ascii=False)}
    
    Structure du rapport :
    1. Résumé exécutif (1 page)
    2. Analyse du marché par ville (2 pages)
    3. Analyse comparative (1 page)
    4. Tendances temporelles (1 page)
    5. Distribution géographique (1 page)
    6. Recommandations (1 page)
    
    Utilise un ton professionnel mais accessible.
    """
    
    return prompt.strip()
