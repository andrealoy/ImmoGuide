# 🏠 ImmoGuide- Analyse Immobilière Automatisée

Application web complète pour scraper, analyser et comparer les données immobilières locatives de différentes villes françaises avec génération automatique de rapports PDF enrichis par IA.

## 📋 Fonctionnalités

### 🔍 Scraping Intelligent
- Extraction automatique des annonces immobilières depuis SeLoger
- Gestion des cookies et headers pour éviter les blocages
- Support multi-villes (Lyon, Paris, Annecy, Annemasse, etc.)
- Sauvegarde structurée en JSON

### 📊 Visualisations Interactives
- **Diagramme circulaire** : Distribution des annonces par ville
- **Scatter plot** : Prix au m² vs Surface avec distributions marginales
- **Évolution temporelle** : Tendances des prix hebdomadaires
- **Cartes interactives** : Heatmap de densité ou scatter des prix avec Pydeck
- Toggle dynamique entre modes de visualisation

### 🤖 Analyses IA
- Analyse contextuelle des visualisations avec OpenAI Vision API
- Comparaison intelligente entre deux villes
- Insights automatiques sur les tendances et opportunités

### 📄 Rapports PDF Professionnels
- Génération automatique de rapports multi-pages
- Introduction et conclusion rédigées par IA
- Analyse détaillée de chaque graphique
- Images avec ratio d'aspect préservé
- Support Unicode complet (multi-OS)
- Barre de progression en temps réel

## 🛠️ Technologies

**Backend & Data**
- Python 3.11
- Pandas, NumPy (manipulation de données)
- Requests, urllib3 (HTTP)

**Scraping**
- Selenium WebDriver (automation)
- BeautifulSoup (parsing HTML)

**Visualisation**
- Streamlit (web app)
- Plotly Express (graphiques interactifs)
- Pydeck (cartes 3D/Mapbox)

**Export & Reporting**
- ReportLab (génération PDF)
- Pillow (traitement d'images)

**Intelligence Artificielle**
- OpenAI API (GPT-5-mini avec Vision)

## 📁 Structure du Projet

```
immoGuide/
├── app.py                      # Point d'entrée Streamlit
├── orchestrator.py             # Orchestration du scraping
├── requirements.txt            # Dépendances Python
│
├── core/                       # Logique métier
│   ├── scraper.py             # Extraction des données
│   ├── cleaner.py             # Nettoyage des données
│   ├── data_loader.py         # Chargement des CSV
│   ├── geo.py                 # Gestion des coordonnées
│   ├── models.py              # Modèles de données
│   └── utils.py               # Utilitaires
│
├── viz/                        # Visualisations
│   ├── plots.py               # Graphiques Plotly
│   ├── maps.py                # Cartes Pydeck
│   └── stats.py               # Statistiques
│
├── gpt_agent/                  # Intégration IA
│   ├── gpt_assistant.py       # Client OpenAI générique
│   ├── prompts.py             # Templates de prompts
│   └── pdf_generator.py       # Génération de rapports PDF
│
├── image_service/              # Capture d'écran
│   └── dashboard_to_image.py  # Export Selenium
│
├── pages/                      # Pages Streamlit
│   ├── 1_Scrapper.py          # Interface de scraping
│   ├── 2_Visualiser.py        # Dashboard de comparaison
│   └── 3_Configuration.py     # Paramètres
│
├── data/                       # Données nettoyées (CSV)
├── jsons/                      # Données brutes (JSON)
│   ├── lyon/
│   ├── paris/
│   └── ...
├── imgs/                       # Exports (PNG, PDF)
└── config/                     # Configuration
    └── api_key.json           # Clés API
```

## 🚀 Installation

### Prérequis

**Système**
- Python 3.11+
- Google Chrome (pour Selenium)
- ChromeDriver (compatible avec votre version de Chrome)

**Linux** : DejaVu Sans font (généralement préinstallée)
```bash
sudo apt-get install fonts-dejavu
```

### Installation

1. **Cloner le dépôt**
```bash
git clone https://github.com/andrealoy/ImmoGuide/
cd ImmoGuide
```

2. **Créer un environnement virtuel**
```bash
python3 -m venv scrapimmo
source scrapimmo/bin/activate  # Linux/Mac
# ou
scrapimmo\Scripts\activate     # Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer ChromeDriver**
```bash
# Linux
sudo apt-get install chromium-chromedriver

# Mac
brew install chromedriver

# Windows - Télécharger depuis
# https://chromedriver.chromium.org/
```

## ⚙️ Configuration

### 1. Clé API OpenAI

Créer `config/api_key.json` :
```json
{
  "openai_api_key": "sk-votre-cle-api-openai"
}
```

**Recommandation** : Utilisez un fichier `.env` en production :
```bash
# .env
OPENAI_API_KEY=sk-votre-cle-api
```

## 📖 Utilisation

### Lancer l'application

```bash
streamlit run app.py
```

L'application s'ouvre sur `http://localhost:8501`

### 1. Scraper des Données

1. Aller sur la page **Scrapper**
2. Entrer le nom de la ville (ex: "lyon")
3. Configurer les paramètres (nombre de pages, etc.)
4. Cliquer sur "Start Scraping"

Les données sont sauvegardées dans :
- `jsons/{ville}/` (données brutes)
- `data/{ville}_clean.csv` (données nettoyées)

### 2. Visualiser et Comparer

1. Aller sur la page **Visualiser**
2. Sélectionner deux villes dans les menus déroulants
3. Cliquer sur "Visualiser"

**Fonctionnalités disponibles** :
- Toggle heatmap/scatter sur les cartes
- Échelle logarithmique pour les graphiques
- Export dashboard en image

### 3. Analyser avec l'IA

Dans la section "Assistant IA" :
1. Poser une question (ex: "Quelle ville est la plus attractive ?")
2. Cliquer sur **Analyser** pour une analyse rapide
3. Cliquer sur **Generate PDF Report** pour un rapport complet

Le PDF est généré dans `imgs/rapport_comparatif.pdf` et téléchargeable directement.

## 📊 Exemple de Rapport PDF

Le rapport généré contient :
1. **Page de titre** avec noms des villes et date
2. **Introduction** contextualisée (IA)
3. **Vue d'ensemble** comparative (analyse globale)
4. **5 graphiques détaillés** :
   - Distribution des annonces
   - Prix au m² vs Surface
   - Évolution temporelle
   - Carte ville 1
   - Carte ville 2
5. **Conclusion** avec recommandations (IA)

## 🔧 Développement

### Structure des données

**Champs principaux** :
- `id` : Identifiant unique de l'annonce
- `price` : Prix mensuel (€)
- `livingSpace` : Surface habitable (m²)
- `price_m2` : Prix au m² calculé
- `lat`, `lon` : Coordonnées GPS
- `creation_date`, `update_date` : Dates

### Ajouter une nouvelle ville

1. Scraper la ville (page Scrapper)
2. Ajouter les coordonnées dans `core/geo.py` :
```python
CITIES_COORDS = {
    "nouvelle_ville": {"lat": 45.0, "lon": 5.0}
}
```

### Personnaliser les prompts IA

Éditer `gpt_agent/prompts.py` :
- `build_dashboard_analysis_prompt()` : Analyse globale
- `build_single_chart_analysis_prompt()` : Analyse par graphique
- `build_pdf_report_prompt()` : Structure du rapport

## 🐛 Dépannage

**"ChromeDriver not found"**
```bash
which chromedriver  # Vérifier l'installation
# Mettre à jour PATH si nécessaire
```

**"Font not found" dans le PDF**
- Linux : `sudo apt-get install fonts-dejavu`
- Fallback automatique sur Arial (Mac) ou Helvetica

**Scraping bloqué**
- Ajouter des cookies valides dans `cookies/seloger_cookies.json`
- Augmenter les délais entre requêtes
- Utiliser un VPN/proxy

**Erreur OpenAI API**
- Vérifier la clé API dans `config/api_key.json`
- Vérifier les crédits OpenAI
- Tester avec `gpt-3.5-turbo` si `gpt-5-mini` indisponible

## 📝 TODO / Améliorations

- [ ] Tests unitaires (pytest)
- [ ] Logging structuré (logging module)
- [ ] Gestion d'erreurs robuste (try/except)
- [ ] Variables d'environnement (.env)
- [ ] Cache des résultats IA
- [ ] Export Excel en plus du PDF
- [ ] Comparaison 3+ villes simultanées
- [ ] API REST (FastAPI)
- [ ] Docker containerization

## 📄 Licence

MIT License - Libre d'utilisation et de modification
