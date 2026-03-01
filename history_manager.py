"""
Historisch Data Beheer — Vastgoed Scraper Pro
Houdt bij wanneer listings online komen en offline gaan.
Bewaart ALLE data, ook listings die niet meer actief zijn.
"""

import json
import os
from datetime import datetime


HISTORY_FILE = "output/vastgoed_historiek.json"


def load_history():
    """Laad de volledige historische database."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_history(db):
    """Sla de historische database op."""
    os.makedirs("output", exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


def make_listing_key(listing):
    """
    Unieke sleutel per listing op basis van adres + oppervlakte + bron.
    Dit is de 'vingerafdruk' van een listing.
    """
    adres = (listing.get("adres") or "").strip().lower()
    opp   = listing.get("oppervlakte_m2") or 0
    bron  = (listing.get("bron") or "").strip().lower()
    prijs = listing.get("prijs") or 0
    return f"{adres}|{opp}|{bron}|{prijs}"


def update_history(new_scrape_data):
    """
    Vergelijkt de nieuwe scrapedata met de historische database.
    
    - Nieuwe listings: datum_online wordt gezet
    - Verdwenen listings: datum_offline + dagen_online worden berekend
    - Bestaande listings: dagen_online wordt bijgewerkt
    
    Geeft de volledige gecombineerde dataset terug (actief + historisch).
    """
    today = datetime.now().strftime("%Y-%m-%d")
    db = load_history()
    
    # Index van huidige scrape op sleutel
    current_keys = {}
    for listing in new_scrape_data:
        key = make_listing_key(listing)
        current_keys[key] = listing

    stats = {"nieuw": 0, "offline": 0, "bijgewerkt": 0, "onveranderd": 0}

    # ── Verwerk nieuwe scrapedata ──────────────────────────────────────────
    for key, listing in current_keys.items():
        if key not in db:
            # Nieuwe listing gevonden
            listing["datum_online"]  = today
            listing["datum_offline"] = None
            listing["dagen_online"]  = 0
            listing["status"]        = "actief"
            db[key] = listing
            stats["nieuw"] += 1
        else:
            # Bestaande listing — bijwerken
            existing = db[key]
            if existing.get("datum_online"):
                d_online = datetime.strptime(existing["datum_online"], "%Y-%m-%d")
                existing["dagen_online"] = (datetime.now() - d_online).days
            else:
                existing["datum_online"] = today
                existing["dagen_online"] = 0
            existing["status"]        = "actief"
            existing["datum_offline"] = None
            # Prijswijziging detecteren
            if listing.get("prijs") and listing["prijs"] != existing.get("prijs"):
                existing["prijs_vorig"]    = existing.get("prijs")
                existing["prijs"]          = listing["prijs"]
                existing["prijs_gewijzigd"]= today
            existing["prijs_per_m2"] = listing.get("prijs_per_m2")
            existing["scraped_op"]   = today
            db[key] = existing
            stats["bijgewerkt"] += 1

    # ── Detecteer offline gegane listings ─────────────────────────────────
    for key, existing in db.items():
        if existing.get("status") == "actief" and key not in current_keys:
            # Was actief, staat niet meer in de scrape → offline
            existing["status"]        = "offline"
            existing["datum_offline"] = today
            if existing.get("datum_online"):
                d_online = datetime.strptime(existing["datum_online"], "%Y-%m-%d")
                existing["dagen_online"] = (datetime.now() - d_online).days
            db[key] = existing
            stats["offline"] += 1

    save_history(db)

    totaal_actief  = sum(1 for r in db.values() if r.get("status") == "actief")
    totaal_offline = sum(1 for r in db.values() if r.get("status") == "offline")

    print(f"""
📊 Historisch database bijgewerkt:
   Nieuw gevonden: {stats['nieuw']}
   Offline gegaan: {stats['offline']}
   Bijgewerkt:     {stats['bijgewerkt']}
   ─────────────────────────────
   Totaal actief:  {totaal_actief}
   Totaal historiek:{totaal_offline}
   Totaal database: {len(db)}
    """)

    # Geef volledige lijst terug (actief + offline)
    return list(db.values())


def generate_history_dashboard(all_data, output_path=None):
    """Genereert het historisch dashboard met alle data."""
    from dashboard_generator import generate_dashboard
    if output_path is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
        output_path = f"output/vastgoed_historisch_dashboard_{date_str}.html"
    
    # Gebruik het historisch dashboard template
    template_path = "output/vastgoed_historisch_dashboard.html"
    if not os.path.exists(template_path):
        print("⚠️  Historisch dashboard template niet gevonden, gebruik standaard dashboard")
        return generate_dashboard(all_data, output_path)
    
    with open(template_path, encoding="utf-8") as f:
        html = f.read()
    
    data_json = json.dumps(all_data, ensure_ascii=False)
    html = html.replace('const RAW_DATA = INJECT_DATA_HERE;', f'const RAW_DATA = {data_json};')
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ Historisch dashboard opgeslagen: {output_path}")
    return output_path


if __name__ == "__main__":
    # Test: simuleer een tweede scraperun waarbij 10% verdwenen is
    import random
    from demo_data import generate_demo_dataset

    print("Test historisch tracking systeem...")
    
    # Eerste scrape
    data1 = generate_demo_dataset(n_per_category=20)
    print(f"\n=== Eerste scrape: {len(data1)} listings ===")
    combined1 = update_history(data1)
    
    # Tweede scrape: 90% van de data + 10 nieuwe
    data2 = random.sample(data1, int(len(data1)*0.9)) + generate_demo_dataset(n_per_category=3)[:10]
    print(f"\n=== Tweede scrape: {len(data2)} listings (10% verdwenen, 10 nieuw) ===")
    combined2 = update_history(data2)
    
    print(f"\nDatabase bevat nu {len(combined2)} listings (actief + historiek)")
