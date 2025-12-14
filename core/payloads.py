def search_payload(place_id: str, page: int, size: int) -> dict:
    return {
        "criteria": {
            "distributionTypes": ["Rent"],
            "estateTypes": ["Apartment", "House"],
            "projectTypes": ["Stock"],
            "location": {
                "placeIds": [place_id]
            }
        },
        "paging": {
            "page": page,
            "size": size,
            "order": "Default"
        }
    }
