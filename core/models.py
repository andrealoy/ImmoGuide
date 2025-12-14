from dataclasses import dataclass
from pathlib import Path
from .utils import normalize_city


@dataclass(frozen=True)
class ScraperConfig:
    city: str
    location_id: str
    base: Path

    @classmethod
    def from_city(cls, city_name: str, location_id: str):
        clean = normalize_city(city_name)
        return cls(clean, location_id, Path("jsons") / clean)

    @property
    def pages(self) -> Path:
        return self.base / "pages"

    @property
    def annonces(self) -> Path:
        return self.base / "annonces"
