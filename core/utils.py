import json
import re
from pathlib import Path
from typing import Dict, Any

STOP_FLAG = Path(__file__).parent.parent / "stop_scraping.flag"

def should_stop() -> bool:
    return STOP_FLAG.exists()

def normalize_city(name: str) -> str:
    name = name.lower()
    name = re.sub(r"\([^)]*\)", "", name)
    name = re.sub(r"[, ]+", "_", name).strip("_")
    return name


def save_json(data: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def get_last_scraped_page(city_slug: str) -> int:
    pages_dir = Path("jsons") / city_slug / "pages"
    if not pages_dir.exists():
        return 0

    pages = []
    for f in pages_dir.glob("page_*.json"):
        try:
            pages.append(int(f.stem.split("_")[1]))
        except ValueError:
            pass

    return max(pages) if pages else 0
