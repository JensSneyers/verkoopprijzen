"""
Genereert realistische demo-data voor het vastgoedrapport.
Wordt gebruikt wanneer de scraper nog niet live is of voor testing.
"""

import random
from datetime import datetime, timedelta

random.seed(42)

STRATEN_ANT = [
    "Nationalestraat", "Meir", "Frankrijklei", "Belgiëlei", "Amerikalei",
    "Gitschotellei", "Turnhoutsebaan", "Antwerpsesteenweg", "Herentalsebaan",
    "Grotesteenweg", "Krijgsbaan", "Boomsesteenweg", "Mechelsesteenweg"
]
STRATEN_VB = [
    "Diestsestraat", "Tiensestraat", "Bondgenotenlaan", "Naamsestraat",
    "Brusselsestraat", "Leuvensesteenweg", "Vilvoordsebaan", "Aarschotsesteenweg",
    "Haachtsesteenweg", "Stationsstraat", "Kerkstraat", "Dorpsstraat"
]
STRATEN_LIM = [
    "Hasseltweg", "Genkersteenweg", "Diestersteenweg", "Stadsomvaart",
    "Kempische Steenweg", "Kuringersteenweg", "Luikersteenweg", "Maastrichtersteenweg",
    "Tongersebaan", "Trichterheideweg", "Herkenrodestraat", "Aldestraat"
]

POSTCODES = {
    "Antwerpen": [
        (2000, "Antwerpen"), (2018, "Antwerpen"), (2020, "Antwerpen"),
        (2050, "Antwerpen"), (2060, "Antwerpen"), (2100, "Deurne"),
        (2140, "Borgerhout"), (2150, "Borsbeek"), (2170, "Merksem"),
        (2180, "Ekeren"), (2200, "Herentals"), (2300, "Turnhout"),
        (2400, "Mol"), (2440, "Geel"), (2500, "Lier"),
        (2550, "Kontich"), (2600, "Berchem"), (2610, "Wilrijk"),
        (2640, "Mortsel"), (2800, "Mechelen"), (2900, "Schoten"),
        (2950, "Kapellen"),
    ],
    "Vlaams-Brabant": [
        (1500, "Halle"), (1540, "Herne"), (1560, "Hoeilaart"),
        (1600, "Sint-Pieters-Leeuw"), (1700, "Dilbeek"), (1730, "Asse"),
        (1800, "Vilvoorde"), (1820, "Perk"), (1830, "Machelen"),
        (1850, "Grimbergen"), (1930, "Zaventem"), (1980, "Eppegem"),
        (3000, "Leuven"), (3010, "Kessel-Lo"), (3012, "Wilsele"),
        (3020, "Herent"), (3050, "Oud-Heverlee"), (3060, "Bertem"),
        (3070, "Kortenberg"), (3080, "Tervuren"), (3090, "Overijse"),
        (3110, "Rotselaar"), (3200, "Aarschot"), (3290, "Diest"),
        (3300, "Tienen"), (3320, "Hoegaarden"), (3390, "Tielt-Winge"),
        (3400, "Landen"), (3440, "Zoutleeuw"),
    ],
    "Limburg": [
        (3500, "Hasselt"), (3510, "Kermt"), (3511, "Kuringen"),
        (3520, "Zonhoven"), (3530, "Houthalen"), (3540, "Herk-de-Stad"),
        (3550, "Heusden-Zolder"), (3560, "Lummen"), (3570, "Alken"),
        (3580, "Beringen"), (3590, "Diepenbeek"), (3600, "Genk"),
        (3620, "Lanaken"), (3630, "Maasmechelen"), (3650, "Dilsen-Stokkem"),
        (3660, "Opglabbeek"), (3670, "Oudsbergen"), (3680, "Maaseik"),
        (3700, "Tongeren"), (3720, "Kortessem"), (3730, "Hoeselt"),
        (3740, "Bilzen"), (3770, "Riemst"), (3800, "Sint-Truiden"),
        (3840, "Borgloon"), (3870, "Heers"), (3890, "Gingelom"),
        (3900, "Overpelt"), (3920, "Lommel"), (3930, "Hamont-Achel"),
        (3940, "Hechtel-Eksel"), (3950, "Bocholt"), (3960, "Bree"),
        (3970, "Leopoldsburg"), (3980, "Tessenderlo"), (3990, "Peer"),
    ],
}

ONTWIKKELAARS = [
    "Matexi", "ION", "Revive", "Cores Development", "Wilma",
    "Immobel", "BPI", "Atenor", "Thomas & Piron", "Alides",
    "Democo", "Kairos", "Trilogy", "Novus", "Urban Living",
]

MAKELAARS = [
    "ERA", "Century 21", "Dewaele", "Sotheby's", "Renson",
    "Vastgoed Dhaeze", "Immo Michaël", "Re/Max", "Coldwell Banker",
]


def random_date_within_months(months=3):
    start = datetime.now() - timedelta(days=months * 30)
    delta = timedelta(days=random.randint(0, months * 30))
    return (start + delta).strftime("%Y-%m-%d")


def generate_listing(provincie, property_type, force_small=False):
    postcodes = POSTCODES[provincie]
    pc, gemeente = random.choice(postcodes)

    straten = {
        "Antwerpen": STRATEN_ANT,
        "Vlaams-Brabant": STRATEN_VB,
        "Limburg": STRATEN_LIM,
    }[provincie]

    straat = random.choice(straten)
    nummer = random.randint(1, 200)
    adres = f"{straat} {nummer}, {gemeente}"

    # Oppervlakte
    if force_small:
        oppervlakte = random.randint(20, 49)
    elif property_type == "Woning":
        oppervlakte = random.randint(80, 350)
    else:
        oppervlakte = random.randint(45, 150)

    # BTW regime
    roll = random.random()
    if roll < 0.25:
        btw = "Nieuwbouw 21% BTW"
        bouwjaar = random.randint(2022, 2026)
        # Nieuwbouwprijzen hoger
        base_prijs_m2 = {
            "Antwerpen":      random.randint(3200, 5800),
            "Vlaams-Brabant": random.randint(3000, 5500),
            "Limburg":        random.randint(2400, 4200),
        }[provincie]
    elif roll < 0.35:
        btw = "Nieuwbouw 6% BTW"
        bouwjaar = random.randint(2020, 2026)
        base_prijs_m2 = {
            "Antwerpen":      random.randint(2800, 4800),
            "Vlaams-Brabant": random.randint(2600, 4500),
            "Limburg":        random.randint(2000, 3600),
        }[provincie]
    else:
        btw = "Bestaand (reg. rechten)"
        bouwjaar = random.randint(1930, 2010)
        base_prijs_m2 = {
            "Antwerpen":      random.randint(1800, 4200),
            "Vlaams-Brabant": random.randint(1700, 3900),
            "Limburg":        random.randint(1400, 3200),
        }[provincie]

    # Locatiecorrectie: centrum is duurder
    if pc % 100 == 0:
        base_prijs_m2 = int(base_prijs_m2 * 1.15)

    prijs = oppervlakte * base_prijs_m2
    prijs = round(prijs / 5000) * 5000  # Afronden op 5k

    # Bron
    if btw.startswith("Nieuwbouw"):
        bron_naam = random.choice(ONTWIKKELAARS)
        bron_type = "Ontwikkelaar"
    else:
        bron_naam = random.choice(MAKELAARS + ["Immoweb", "Zimmo"])
        bron_type = "Makelaar" if bron_naam not in ["Immoweb", "Zimmo"] else bron_naam

    return {
        "provincie":      provincie,
        "type":           "Klein (<50m²)" if force_small else property_type,
        "adres":          adres,
        "postcode":       str(pc),
        "gemeente":       gemeente,
        "oppervlakte_m2": oppervlakte,
        "bouwjaar":       bouwjaar,
        "btw_regime":     btw,
        "prijs":          prijs,
        "prijs_per_m2":   base_prijs_m2,
        "bron":           bron_naam,
        "bron_type":      bron_type,
        "scraped_op":     random_date_within_months(1),
    }


def generate_demo_dataset(n_per_category=40):
    data = []
    provincies = ["Antwerpen", "Vlaams-Brabant", "Limburg"]
    types = ["Woning", "Appartement"]

    for prov in provincies:
        for ptype in types:
            for _ in range(n_per_category):
                data.append(generate_listing(prov, ptype))
            # Klein (<50m²) - vooral appartementen
            for _ in range(12):
                data.append(generate_listing(prov, ptype, force_small=True))

    random.shuffle(data)
    return data


if __name__ == "__main__":
    import json
    data = generate_demo_dataset()
    with open("demo_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Demo dataset gegenereerd: {len(data)} listings")
