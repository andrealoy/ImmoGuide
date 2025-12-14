"""
Core module - Logique métier du scraping immobilier
"""

from .models import ScraperConfig
from .scraper import SeLogerScraper
from .cleaner import SeLogerDataProcessor

__all__ = [
    "ScraperConfig",
    "SeLogerScraper",
    "SeLogerDataProcessor",
]
