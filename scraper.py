"""
Vastgoed Scraper - Immoweb & Zimmo
Provincies: Antwerpen, Vlaams-Brabant, Limburg (België)
"""

import requests
from bs4 import BeautifulSoup
import time
import random
import json
import re
from datetime import datetime

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "nl-BE,nl;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Postcode ranges per provincie
PROVINCIE_POSTCODES = {
    "Antwerpen":       list(range(2000, 2999)),
    "Vlaams-Brabant":  list(range(1500, 1999)) + list(range(3000, 3499)),
    "Limburg":         list(range(3500, 3999)),
}

# Immoweb district codes per provincie (gebruikt in URL)
IMMOWEB_DISTRICTS = {
    "Antwerpen":      "province-antwerp",
    "Vlaams-Brabant": "province-flemish-brabant",
    "Limburg":        "province-limburg",
}


def detect_btw_regime(price, surface, description=""):
    """
    Detecteert het BTW-regime op basis van prijs, m² en beschrijving.
    - 6% BTW: renovatie of sociaal wonen
    - 21% BTW: nieuwbouw standaard
    - Geen BTW: bestaand pand (registratierecht)
    """
    desc_lower = description.lower()
    if any(k in desc_lower for k in ["nieuwbouw", "bouw", "project", "btw", "21%", "6%", "nieuw"]):
        if "6%" in desc_lower or "sociaal" in desc_lower or "renovatie" in desc_lower:
            return "Nieuwbouw 6% BTW"
        return "Nieuwbouw 21% BTW"
    return "Bestaand (reg. rechten)"


def classify_property(prop_type, surface):
    """Classificeer als woning, appartement, of <50m²"""
    if surface and surface < 50:
        return "Klein (<50m²)"
    if prop_type in ["APARTMENT", "apartment", "Appartement"]:
        return "Appartement"
    return "Woning"


def scrape_immoweb_province(provincie, property_type="house", page=1):
    """
    Scrapt Immoweb voor een provincie.
    property_type: 'house' of 'apartment'
    """
    district = IMMOWEB_DISTRICTS.get(provincie, "")
    type_map = {"house": "huis", "apartment": "appartement"}
    url = (
        f"https://www.immoweb.be/nl/zoeken/{type_map[property_type]}/te-koop"
        f"?countries=BE&districts={district}&page={page}&orderBy=newest"
    )

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        listings = []

        cards = soup.select("article.card--result")
        for card in cards:
            try:
                listing = parse_immoweb_card(card, provincie, property_type)
                if listing:
                    listings.append(listing)
            except Exception:
                continue

        return listings

    except requests.RequestException as e:
        print(f"[Immoweb] Fout bij scrapen {provincie}: {e}")
        return []


def parse_immoweb_card(card, provincie, property_type):
    """Parseert één Immoweb listingkaart."""
    data = {}

    # Prijs
    price_el = card.select_one("p.card--result__price")
    if not price_el:
        return None
    price_text = price_el.get_text(strip=True).replace(".", "").replace("€", "").replace("\xa0", "").strip()
    price_match = re.search(r"\d+", price_text.replace(",", ""))
    if not price_match:
        return None
    data["prijs"] = int(price_match.group())

    # Adres
    addr_el = card.select_one("p.card--result__locality")
    data["adres"] = addr_el.get_text(strip=True) if addr_el else "Onbekend"

    # Postcode uit adres halen
    pc_match = re.search(r"\b(\d{4})\b", data["adres"])
    data["postcode"] = pc_match.group(1) if pc_match else "0000"

    # Oppervlakte
    surface_el = card.select_one("[data-type='surface']") or card.find(string=re.compile(r"\d+\s*m²"))
    data["oppervlakte_m2"] = None
    if surface_el:
        m2_match = re.search(r"(\d+)", str(surface_el))
        if m2_match:
            data["oppervlakte_m2"] = int(m2_match.group(1))

    # Bouwjaar
    bouwjaar_el = card.find(string=re.compile(r"Bouwjaar|bouwjaar"))
    data["bouwjaar"] = None
    if bouwjaar_el:
        yr_match = re.search(r"(19|20)\d{2}", str(bouwjaar_el))
        if yr_match:
            data["bouwjaar"] = int(yr_match.group())

    # Beschrijving voor BTW-detectie
    desc_el = card.select_one(".card--result__title")
    description = desc_el.get_text(strip=True) if desc_el else ""

    data["provincie"] = provincie
    data["type"] = classify_property(
        "APARTMENT" if property_type == "apartment" else "HOUSE",
        data["oppervlakte_m2"]
    )
    data["btw_regime"] = detect_btw_regime(data["prijs"], data["oppervlakte_m2"], description)
    data["prijs_per_m2"] = (
        round(data["prijs"] / data["oppervlakte_m2"])
        if data["oppervlakte_m2"] and data["oppervlakte_m2"] > 0
        else None
    )
    data["bron"] = "Immoweb"
    data["scraped_op"] = datetime.now().strftime("%Y-%m-%d")

    return data


def scrape_zimmo_province(provincie, property_type="house", page=1):
    """
    Scrapt Zimmo voor een provincie.
    """
    type_map = {"house": "woning", "apartment": "appartement"}
    prov_map = {
        "Antwerpen": "antwerpen",
        "Vlaams-Brabant": "vlaams-brabant",
        "Limburg": "limburg",
    }
    prov_slug = prov_map.get(provincie, provincie.lower())
    url = (
        f"https://www.zimmo.be/nl/{prov_slug}/te-koop/"
        f"?search=eyJmaWx0ZXIiOnt9fQ==&page={page}"
    )

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        listings = []

        cards = soup.select("div.property-block")
        for card in cards:
            try:
                listing = parse_zimmo_card(card, provincie, property_type)
                if listing:
                    listings.append(listing)
            except Exception:
                continue

        return listings

    except requests.RequestException as e:
        print(f"[Zimmo] Fout bij scrapen {provincie}: {e}")
        return []


def parse_zimmo_card(card, provincie, property_type):
    """Parseert één Zimmo listingkaart."""
    data = {}

    price_el = card.select_one(".price")
    if not price_el:
        return None
    price_text = price_el.get_text(strip=True).replace(".", "").replace("€", "").replace("\xa0", "")
    price_match = re.search(r"\d+", price_text)
    if not price_match:
        return None
    data["prijs"] = int(price_match.group())

    addr_el = card.select_one(".property-address") or card.select_one(".address")
    data["adres"] = addr_el.get_text(strip=True) if addr_el else "Onbekend"

    pc_match = re.search(r"\b(\d{4})\b", data["adres"])
    data["postcode"] = pc_match.group(1) if pc_match else "0000"

    surface_el = card.find(string=re.compile(r"\d+\s*m²"))
    data["oppervlakte_m2"] = None
    if surface_el:
        m2_match = re.search(r"(\d+)", str(surface_el))
        if m2_match:
            data["oppervlakte_m2"] = int(m2_match.group(1))

    data["bouwjaar"] = None
    desc_el = card.select_one(".property-title") or card.select_one("h2")
    description = desc_el.get_text(strip=True) if desc_el else ""

    data["provincie"] = provincie
    data["type"] = classify_property(
        "APARTMENT" if property_type == "apartment" else "HOUSE",
        data["oppervlakte_m2"]
    )
    data["btw_regime"] = detect_btw_regime(data["prijs"], data["oppervlakte_m2"], description)
    data["prijs_per_m2"] = (
        round(data["prijs"] / data["oppervlakte_m2"])
        if data["oppervlakte_m2"] and data["oppervlakte_m2"] > 0
        else None
    )
    data["bron"] = "Zimmo"
    data["scraped_op"] = datetime.now().strftime("%Y-%m-%d")

    return data


def run_full_scrape(max_pages=3):
    """Voert de volledige scrape uit voor alle provincies en types."""
    all_listings = []
    provincies = list(IMMOWEB_DISTRICTS.keys())
    property_types = ["house", "apartment"]

    for prov in provincies:
        for ptype in property_types:
            print(f"  → Immoweb: {prov} / {ptype}...")
            for page in range(1, max_pages + 1):
                listings = scrape_immoweb_province(prov, ptype, page)
                all_listings.extend(listings)
                time.sleep(random.uniform(2, 4))

            print(f"  → Zimmo: {prov} / {ptype}...")
            for page in range(1, max_pages + 1):
                listings = scrape_zimmo_province(prov, ptype, page)
                all_listings.extend(listings)
                time.sleep(random.uniform(2, 4))

    print(f"\nTotaal gescrapt: {len(all_listings)} listings")
    return all_listings


if __name__ == "__main__":
    results = run_full_scrape(max_pages=2)
    with open("scraped_data.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("Data opgeslagen in scraped_data.json")
