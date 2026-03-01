# Vastgoed Scraper Pro
## Wekelijks Vastgoedmarktrapport — Antwerpen · Vlaams-Brabant · Limburg

---

## Wat doet dit systeem?

Elke week scrapt dit systeem automatisch vraagprijsdata van **Immoweb** en **Zimmo**
en genereert een professioneel Excel-rapport + interactief HTML-dashboard met:

- Prijs per m² per provincie, type en BTW-regime
- Onderscheid woning / appartement / klein (<50m²)
- Onderscheid nieuwbouw 21% BTW / nieuwbouw 6% BTW / bestaand pand
- Adres, postcode, bouwjaar, oppervlakte, vraagprijs, bron
- Statistieken: top-10 duurste postcodes, gemiddelden per gemeente

---

## Installatie (eenmalig)

### 1. GitHub repository aanmaken
```bash
# Maak een nieuwe (private) repo aan op github.com
# Upload alle bestanden
```

### 2. Python dependencies installeren (voor lokaal gebruik)
```bash
pip install requests beautifulsoup4 openpyxl lxml playwright fake-useragent tenacity
playwright install chromium
```

### 3. GitHub Secrets instellen (voor automatische e-mail)
Ga naar je repo → Settings → Secrets → Actions → New repository secret:

| Secret naam      | Waarde                          |
|------------------|---------------------------------|
| `MAIL_USERNAME`  | jouw-email@gmail.com            |
| `MAIL_PASSWORD`  | Gmail App Password (16 tekens)  |
| `MAIL_TO`        | bestemming@email.com            |

**Gmail App Password aanmaken:**
1. Ga naar myaccount.google.com → Beveiliging
2. 2-staps verificatie moet aan staan
3. Zoek "App-wachtwoorden" → genereer voor "Mail"

---

## Gebruik

### Demo-modus (geen internet, test het systeem)
```bash
python main.py
```
→ Genereert rapport met 312 realistische gesimuleerde listings

### Live scraping
```bash
python main.py --live --pages 5
```
→ Scrapt Immoweb + Zimmo, 5 pagina's per provincie/type (~300-600 listings)

### Output
Alle bestanden worden opgeslagen in de `output/` map:
- `vastgoed_rapport_YYYY-MM-DD.xlsx` — Excel met 9 tabbladen
- `vastgoed_dashboard_YYYY-MM-DD.html` — Interactief dashboard
- `data_YYYY-MM-DD.json` — Ruwe data voor archief

---

## Automatisering via GitHub Actions

Het bestand `.github/workflows/weekly_report.yml` zorgt dat:
- **Elke maandag om 06:00** automatisch wordt gescrapt
- Het rapport als e-mail bijlage wordt verstuurd
- Het rapport 90 dagen bewaard blijft als GitHub Artifact
- (Optioneel) rapporten worden gecommit naar de `reports` branch

**Handmatig starten:**
GitHub → Actions → "Wekelijks Vastgoedrapport" → "Run workflow"

---

## Structuur

```
vastgoed_scraper/
├── main.py                    # Hoofdprogramma
├── scraper.py                 # Immoweb & Zimmo scraper
├── demo_data.py               # Realistische demo-data generator
├── report_generator.py        # Excel rapport generator
├── dashboard_generator.py     # HTML dashboard generator
├── requirements.txt           # Python dependencies
├── README.md                  # Deze handleiding
└── .github/
    └── workflows/
        └── weekly_report.yml  # GitHub Actions automatisering
```

---

## Tabbladen in het Excel-rapport

| Tabblad                   | Inhoud                                              |
|---------------------------|-----------------------------------------------------|
| 📊 Samenvatting           | KPI's, stats per provincie, top-10 postcodes        |
| 🏡 Woningen — Bestaand    | Bestaande woningen, registratierechten              |
| 🏡 Woningen — Nieuwbouw   | Nieuwbouwwoningen (6% & 21% BTW)                   |
| 🏢 Appartementen — Bestaand| Bestaande appartementen                             |
| 🏢 Appartementen — Nieuwbouw| Nieuwbouwappartementen                              |
| 📐 Klein (<50m²)          | Alle panden kleiner dan 50m²                        |
| 🏗️ Nieuwbouw 21% BTW      | Alle nieuwbouw aan 21% BTW                          |
| ♻️ Nieuwbouw 6% BTW       | Alle nieuwbouw aan 6% BTW (renovatie/sociaal)       |
| 📋 Alle Listings          | Volledige dataset, alle types en regimes            |

---

## Uitbreiden met eigen vastgoedontwikkelaars

Voeg toe aan `scraper.py`:
```python
def scrape_ontwikkelaar_xyz(provincie):
    url = "https://www.ontwikkelaar-xyz.be/projecten"
    # Eigen parsing logica hier
    ...
```

Elke ontwikkelaarsite heeft een unieke structuur. Geef de URL's mee
en ik pas de scraper specifiek aan voor elke site.

---

## Juridische nota

Dit systeem scrapt **vraagprijzen** (niet transactieprijzen) van publiek
toegankelijke websites. Gebruik uitsluitend voor intern marktonderzoek.
Raadpleeg de gebruiksvoorwaarden van elke website.
