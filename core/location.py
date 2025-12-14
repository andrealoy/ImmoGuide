# core/location.py

from typing import Tuple, Optional
from .http import HttpClient , BrowserSession


AUTOCOMPLETE_URL = "https://www.seloger.com/search-mfe-bff/autocomplete"

def location_autocomplete(
    query: str,
    session: BrowserSession,
    limit: int = 5
) -> Tuple[Optional[str], Optional[str]]:
    payload = {
        "text": query,
        "limit": limit,
        "placeTypes": [
            "NBH1", "NBH3", "AD09", "NBH2",
            "AD08", "AD06", "AD04", "POCO", "AD02"
        ],
        "parentTypes": [
            "NBH1", "NBH3", "AD09", "NBH2",
            "AD08", "AD06", "AD04", "POCO", "AD02"
        ],
        "locale": "fr"
    }

    client = HttpClient(session)

    resp = client.request(
        "POST",
        AUTOCOMPLETE_URL,
        json_body=payload
    )

    data = resp.json()

    if not data:
        return None, None

    loc_id = data[0].get("id")
    labels = data[0].get("labels") or []
    loc_name = labels[0] if labels else None

    return loc_id, loc_name
