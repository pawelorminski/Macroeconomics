"""Runda 4 sondy: domknięcie dwóch znanych luk z poprzedniej rundy —
poprawny kod IMF DataMapper dla salda pierwotnego i poprawny kod jednostki
Eurostat dla wzrostu PKB r/r (nie kw/kw). Tymczasowe.
"""

import logging

import requests

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


def main() -> None:
    # 1. Szukamy właściwego kodu DataMapper dla salda pierwotnego (primary balance).
    odp = requests.get("https://www.imf.org/external/datamapper/api/v1/indicators", timeout=20)
    wskazniki = odp.json().get("indicators", {})
    trafienia = {
        kod: info.get("label")
        for kod, info in wskazniki.items()
        if "primary" in (info.get("label") or "").lower() or "primary" in kod.lower()
    }
    LOG.info("Kandydaci DataMapper dla 'primary balance': %s", trafienia)

    # 2. Sprawdzamy, jak namq_10_gdp koduje wzrost PKB r/r (unit dimension) — pobieramy
    # bez filtra unit, żeby zobaczyć wszystkie dostępne kody i ich etykiety.
    odp2 = requests.get(
        "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/namq_10_gdp",
        params={
            "format": "JSON",
            "geo": "EU27_2020",
            "na_item": "B1GQ",
            "s_adj": "SCA",
            "lang": "en",
        },
        timeout=20,
    )
    dane2 = odp2.json()
    jednostki = dane2.get("dimension", {}).get("unit", {}).get("category", {}).get("label", {})
    LOG.info("Dostępne kody 'unit' dla namq_10_gdp (PKB): %s", jednostki)


if __name__ == "__main__":
    main()
