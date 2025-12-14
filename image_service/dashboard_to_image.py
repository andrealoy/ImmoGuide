import plotly.graph_objects as go
import pydeck as pdk
import time
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image

def save_plotly_figure(fig: go.Figure, path: str):
    fig.write_html(path)
    
def save_pydeck_deck(deck: pdk.Deck, path: str):
    deck.to_html(path)
    
def screenshot_dashboard(url: str, output_path: str, wait_time: int = 2, driver=None):
    """
    Prend un screenshot d'une page HTML.
    Si driver est fourni, réutilise la session Selenium existante.
    Sinon, crée une nouvelle session (plus lent).
    """
    should_quit = False
    
    if driver is None:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(options=options)
        should_quit = True
    
    driver.get(url)
    time.sleep(wait_time)
    driver.save_screenshot(output_path)
    
    if should_quit:
        driver.quit()
    
def merge_images(image_paths: list, output_path: str, columns: int = 2):
    """
    Fusionne les images en grille avec un nombre défini de colonnes.
    Par défaut, crée une grille 2x2 (ou 2xN selon le nombre d'images).
    """
    images = [Image.open(p) for p in image_paths]
    
    if not images:
        return
    
    # Calculer la largeur et hauteur max de chaque image
    max_width = max(img.width for img in images)
    max_height = max(img.height for img in images)
    
    # Calculer le nombre de lignes nécessaires
    rows = (len(images) + columns - 1) // columns  # Arrondi supérieur
    
    # Créer une nouvelle image vide (grille)
    merged_width = max_width * columns
    merged_height = max_height * rows
    merged_image = Image.new('RGB', (merged_width, merged_height), color='white')

    # Coller les images en grille
    for idx, img in enumerate(images):
        row = idx // columns
        col = idx % columns
        x = col * max_width
        y = row * max_height
        merged_image.paste(img, (x, y))

    # Sauvegarder l'image fusionnée
    merged_image.save(output_path)

def dashboard_to_image(plt , pdk):
    """
    Génère une image fusionnée du dashboard en réutilisant une seule session Selenium.
    """
    # Créer le dossier imgs s'il n'existe pas
    Path("imgs").mkdir(exist_ok=True)
    
    # Créer une seule session Selenium pour tous les screenshots
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    
    try:
        # Listes pour tracker les fichiers temporaires
        temp_files = []
        
        # Sauvegarder les visualisations en tant que fichiers HTML temporaires
        for i, fig in enumerate(plt):
            plotly_path = f"imgs/temp_plotly_{i}.html"
            temp_files.append(plotly_path)
            save_plotly_figure(fig, plotly_path)
            # Convertir en chemin absolu pour file://
            abs_path = os.path.abspath(plotly_path)
            screenshot_dashboard(url=f"file://{abs_path}", output_path=f"imgs/plotly_screenshot_{i}.png", driver=driver)
        
        for j, deck in enumerate(pdk):
            pydeck_path = f"imgs/temp_pydeck_{j}.html"
            temp_files.append(pydeck_path)
            save_pydeck_deck(deck, pydeck_path)
            # Convertir en chemin absolu pour file://
            abs_path = os.path.abspath(pydeck_path)
            # Plus de temps pour les cartes (chargement des tiles)
            screenshot_dashboard(url=f"file://{abs_path}", output_path=f"imgs/pydeck_screenshot_{j}.png", wait_time=5, driver=driver)

        # Fusionner les captures d'écran en une seule image
        merged_output_path = "imgs/dashboard_image.png"
        to_merge = [f"imgs/plotly_screenshot_{i}.png" for i in range(len(plt))] + [f"imgs/pydeck_screenshot_{j}.png" for j in range(len(pdk))]
        merge_images(to_merge, merged_output_path)
        
        # Nettoyer les fichiers HTML temporaires
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        return merged_output_path
    
    finally:
        # Fermer la session Selenium
        driver.quit()