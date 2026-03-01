"""
Vastgoed Scraper Pro — Hoofdprogramma
Wekelijks vastgoedmarktrapport voor Antwerpen, Vlaams-Brabant & Limburg

Gebruik:
  python main.py          → Demo-modus (gesimuleerde data, geen internet nodig)
  python main.py --live   → Live scraping van Immoweb & Zimmo
"""

import argparse
import json
import os
import sys
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description="Vastgoed Scraper Pro")
    parser.add_argument("--live", action="store_true",
                        help="Live scraping (anders: demo-data)")
    parser.add_argument("--pages", type=int, default=3,
                        help="Aantal pagina's per provincie/type (default: 3)")
    parser.add_argument("--output-dir", default="output",
                        help="Output directory (default: output/)")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")

    # ── Data ophalen ──────────────────────────────────────────────────────────
    if args.live:
        print("🌐 Live scraping gestart...")
        from scraper import run_full_scrape
        data = run_full_scrape(max_pages=args.pages)
        if not data:
            print("⚠️  Geen data gescrapt, schakelen naar demo-modus...")
            from demo_data import generate_demo_dataset
            data = generate_demo_dataset()
    else:
        print("🎭 Demo-modus: realistische gesimuleerde data wordt geladen...")
        from demo_data import generate_demo_dataset
        data = generate_demo_dataset()

    print(f"✅ {len(data)} listings geladen")

    # Statistieken tonen
    types_count = {}
    btw_count   = {}
    for r in data:
        t = r.get("type", "Onbekend")
        b = r.get("btw_regime", "Onbekend")
        types_count[t] = types_count.get(t, 0) + 1
        btw_count[b]   = btw_count.get(b, 0) + 1

    print("\n📊 Verdeling:")
    for k, v in sorted(types_count.items()):
        print(f"   {k}: {v}")
    print("\n🏷️  BTW-regimes:")
    for k, v in sorted(btw_count.items()):
        print(f"   {k}: {v}")

    # Data opslaan als JSON (voor debugging / archief)
    json_path = os.path.join(args.output_dir, f"data_{date_str}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Raw data opgeslagen: {json_path}")

    # ── Excel rapport genereren ───────────────────────────────────────────────
    print("\n📊 Excel rapport genereren...")
    from report_generator import generate_report
    xlsx_path = os.path.join(args.output_dir, f"vastgoed_rapport_{date_str}.xlsx")
    generate_report(data, xlsx_path)

    # ── HTML dashboard genereren ──────────────────────────────────────────────
    print("🖥️  HTML dashboard genereren...")
    from dashboard_generator import generate_dashboard
    html_path = os.path.join(args.output_dir, f"vastgoed_dashboard_{date_str}.html")
    generate_dashboard(data, html_path)

    print(f"""
╔══════════════════════════════════════════════════════╗
║  ✅ Rapport voltooid voor week van {date_str}   ║
╠══════════════════════════════════════════════════════╣
║  📊 Excel:     {os.path.basename(xlsx_path):<37}║
║  🖥️  Dashboard: {os.path.basename(html_path):<37}║
║  💾 JSON:      {os.path.basename(json_path):<37}║
╚══════════════════════════════════════════════════════╝
    """)

    return xlsx_path, html_path


if __name__ == "__main__":
    main()
