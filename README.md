# Ceny ujemne na polskim rynku energii elektrycznej

Strona: https://szymoncyranowicz.github.io/ceny-ujemne/

Statyczna strona (GitHub Pages) z analizą godzin z ujemną ceną na TGE – Rynek Dnia Następnego:

- liczba cen ujemnych wg dnia tygodnia,
- liczba cen ujemnych wg miesięcy,
- mapa godzina vs dzień tygodnia,
- skumulowana liczba cen ujemnych w podziale na lata,

## Jak to działa

`build.py` (czysty Python, bez zależności) czyta wszystkie pliki `data/*.csv`, wybiera godziny z ceną < 0
i wstawia je do szablonu `template.html`, tworząc `site/index.html`. Wykresy rysuje Chart.js w przeglądarce.

Po każdym `git push` na gałąź `main` GitHub Actions buduje stronę i publikuje ją na GitHub Pages.

## Aktualizacja danych

Podmień / dodaj plik CSV w `data/` (kolumny: `DeliveryDatePL, Hour, product, price, ...`) i zrób push.

## Lokalnie

```bash
python build.py
# otwórz site/index.html w przeglądarce
```
