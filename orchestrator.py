# orchestrator.py
from core.runner import run_scraping

def run_with_auto_refresh(
    cities: dict,
    size: int = 30,
):
    run_scraping(
        cities=cities,
        size=size,
    )
