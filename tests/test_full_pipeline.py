"""
Test end-to-end du pipeline SeLoger
- Session
- Autocomplete
- Search
- Classified
"""

from core.http import BrowserSession, HttpClient
from core.location import location_autocomplete
from core.payloads import search_payload


# -------------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------------

CITY_QUERY = "Bordeaux"
SEARCH_URL = "https://www.seloger.com/serp-bff/search"
CLASSIFIED_URL = "https://www.seloger.com/cdp-bff/v1/classified"

PAGE = 1
SIZE = 10


# -------------------------------------------------------------------
# 1️⃣ Charger la session navigateur
# -------------------------------------------------------------------

print("\n=== 1️⃣ Chargement session ===")

session = BrowserSession()
client = HttpClient(session)

cookies = session.load_cookies()
print("✔ Cookies chargés :", cookies[:80], "...")
print("✔ Longueur cookies :", len(cookies))


# -------------------------------------------------------------------
# 2️⃣ AUTOCOMPLETE
# -------------------------------------------------------------------

print("\n=== 2️⃣ Autocomplete ===")

place_id, place_name = location_autocomplete(CITY_QUERY, session)

print("➡ Résultat autocomplete :")
print("   place_id =", place_id)
print("   place_name =", place_name)

if not place_id:
    raise RuntimeError("❌ Autocomplete a échoué")


# -------------------------------------------------------------------
# 3️⃣ SEARCH (UNE SEULE FOIS)
# -------------------------------------------------------------------

print("\n=== 3️⃣ Search ===")

payload = search_payload(place_id, PAGE, SIZE)

resp = client.request(
    "POST",
    SEARCH_URL,
    json_body=payload
)

print("✔ Search status :", resp.status_code)

data = resp.json()
ads = data.get("classifieds", [])

print("✔ Annonces trouvées :", len(ads))

if not ads:
    raise RuntimeError("❌ Search OK mais aucune annonce retournée")

classified_id = ads[0].get("id")
print("➡ First classified id :", classified_id)


# -------------------------------------------------------------------
# 4️⃣ CLASSIFIED
# -------------------------------------------------------------------

print("\n=== 4️⃣ Classified ===")

resp = client.request(
    "GET",
    f"{CLASSIFIED_URL}/{classified_id}"
)

print("✔ Classified status :", resp.status_code)

classified = resp.json()

sections = classified.get("sections", {})

title = sections.get("description", {}).get("title")
price = sections.get("hardFacts", {}).get("price", {}).get("value")
surface = sections.get("hardFacts", {}).get("livingSpace", {}).get("value")

print("\n=== ✅ SUCCÈS ===")
print("Titre :", title)
print("Prix :", price)
print("Surface :", surface)

