from pathlib import Path
from typing import Dict
from .http import BrowserSession
from .scraper import SeLogerScraper
from .utils import get_last_scraped_page
from .utils import should_stop

def run_scraping(cities: Dict[str, str], size: int = 30):
    session = BrowserSession()

    scrapers = {
        name: SeLogerScraper(name, loc, session)
        for name, loc in cities.items()
    }

    alive = set(cities)
    current_page = {
        city: get_last_scraped_page(city) + 1
        for city in cities
    }

    while alive:

        if should_stop():
            print("🛑 STOP demandé → arrêt propre")
            return

        for city in list(alive):
            page = current_page[city]

            print(f"\n=== {city} → page {page} ===")
            n = scrapers[city].scrape_page(page, size)

            if n == -1:  # Signal d'arrêt depuis scrape_page
                return
            if n == 0:
                alive.remove(city)
            else:
                current_page[city] += 1

