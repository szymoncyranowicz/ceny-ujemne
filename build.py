"""Generuje statyczną stronę z analizą cen ujemnych na RDN (TGE).

Użycie:
    python build.py [plik_csv ...] [--out site]

Domyślnie czyta wszystkie pliki *.csv z katalogu `data/` i zapisuje stronę do `site/index.html`.
Strona jest w pełni statyczna (GitHub Pages) – filtrowanie po latach i rynkach odbywa się w przeglądarce.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).parent
TEMPLATE = ROOT / "template.html"


def parse_date(value: str) -> date:
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d.%m.%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"Nieznany format daty: {value!r}")


def parse_number(value: str) -> float:
    return float(value.strip().replace(" ", "").replace(",", "."))


def parse_hour(value: str) -> int:
    # "2A" = dodatkowa godzina przy zmianie czasu na zimowy -> traktujemy jak godzinę 2
    return int(value.strip().upper().rstrip("A"))


def load(paths: list[Path]):
    records = []  # [rok, miesiąc, dzień_tygodnia(0=pon), godzina(1-24), produkt, cena, "RRRR-MM-DD"]
    products: list[str] = []
    first_day: date | None = None
    last_day: date | None = None
    total_rows = 0

    for path in paths:
        with path.open(encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                d = parse_date(row["DeliveryDatePL"])
                product = row["product"].strip()
                price = parse_number(row["price"])
                total_rows += 1
                first_day = d if first_day is None or d < first_day else first_day
                last_day = d if last_day is None or d > last_day else last_day
                if product not in products:
                    products.append(product)
                if price < 0:
                    records.append([
                        d.year, d.month, d.weekday(), parse_hour(row["Hour"]),
                        products.index(product), round(price, 2), d.isoformat(),
                    ])

    records.sort(key=lambda r: (r[6], r[3]))
    return {
        "records": records,
        "products": products,
        "years": sorted({y for y in range(first_day.year, last_day.year + 1)}),
        "firstDay": first_day.isoformat(),
        "lastDay": last_day.isoformat(),
        "totalRows": total_rows,
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", nargs="*", type=Path, help="pliki CSV z danymi")
    parser.add_argument("--out", type=Path, default=ROOT / "site", help="katalog wyjściowy")
    args = parser.parse_args()

    paths = args.csv or sorted((ROOT / "data").glob("*.csv"))
    if not paths:
        raise SystemExit("Brak plików CSV (umieść je w katalogu data/).")

    data = load(paths)
    html = TEMPLATE.read_text(encoding="utf-8").replace(
        "/*__DATA__*/null", json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    )
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "index.html").write_text(html, encoding="utf-8")
    (args.out / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Wczytano {data['totalRows']} wierszy, cen ujemnych: {len(data['records'])} "
          f"({data['firstDay']} – {data['lastDay']}) -> {args.out / 'index.html'}")


if __name__ == "__main__":
    main()
