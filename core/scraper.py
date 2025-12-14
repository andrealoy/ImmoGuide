from typing import Dict, Any
from .models import ScraperConfig
from .http import HttpClient
from .utils import save_json, should_stop


class SeLogerScraper:
    BASE = "https://www.seloger.com"
    SEARCH = BASE + "/serp-bff/search"
    DETAIL = BASE + "/cdp-bff/v1/classified/{}"

    def __init__(self, city_name: str, location_id: str, session):
        self.cfg = ScraperConfig.from_city(city_name, location_id)
        self.http = HttpClient(session)

        self.cfg.pages.mkdir(parents=True, exist_ok=True)
        self.cfg.annonces.mkdir(parents=True, exist_ok=True)

    def payload(self, page: int, size: int) -> Dict[str, Any]:
        return {
            "criteria": {
                "distributionTypes": ["Rent"],
                "estateTypes": ["House", "Apartment"],
                "projectTypes": ["Stock", "Flatsharing"],
                "location": {"placeIds": [self.cfg.location_id]},
            },
            "paging": {"page": page, "size": size, "order": "Default"},
        }

    def search_page(self, page: int, size: int):
        resp = self.http.request(
            "POST",
            self.SEARCH,
            json_body=self.payload(page, size),
        )
        data = resp.json()
        return data.get("classifieds", []), data

    def scrape_ad(self, ad_id: str):
        path = self.cfg.annonces / f"{ad_id}.json"
        if path.exists():
            return

        resp = self.http.request(
            "GET",
            self.DETAIL.format(ad_id),
        )
        
        # Annonce supprimée/expirée
        if resp.status_code == 404:
            print(f"⚠️ Annonce {ad_id} introuvable (404) - ignorée")
            return
        
        save_json(resp.json(), path)

    def scrape_page(self, page: int, size: int) -> int:
        ads, data = self.search_page(page, size)
        if not ads:
            return 0

        for ad in ads:
            if should_stop():
                print("🛑 Arrêt pendant scraping des annonces")
                return -1  # Signal d'arrêt
            self.scrape_ad(str(ad["id"]))

        save_json(data, self.cfg.pages / f"page_{page}.json")
        return len(ads)
