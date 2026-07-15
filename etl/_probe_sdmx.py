"""Runda 3 sondy: struktura JSON-stat dla datasetu Eurostat, który już
potwierdzony jako działający w rundzie 1 (une_rt_m). Tymczasowe.
"""

import json
import logging

import requests

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


def main() -> None:
    odp = requests.get(
        "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/une_rt_m",
        params={
            "format": "JSON",
            "geo": "PL",
            "s_adj": "SA",
            "age": "TOTAL",
            "sex": "T",
            "unit": "PC_ACT",
            "lang": "en",
        },
        timeout=20,
    )
    dane = odp.json()
    LOG.info("Klucze najwyższego poziomu: %s", list(dane.keys()))
    LOG.info("'id' (kolejność wymiarów): %s", dane.get("id"))
    LOG.info("'size' (rozmiary wymiarów): %s", dane.get("size"))
    wymiary = dane.get("dimension", {})
    czas = wymiary.get("time", {}).get("category", {})
    LOG.info("Wymiar czasu - liczba kategorii: %d", len(czas.get("index", {})))
    LOG.info("Wymiar czasu - index (ostatnie 5): %s", dict(list(czas.get("index", {}).items())[-5:]))
    LOG.info("Wymiar czasu - label (ostatnie 5): %s", dict(list(czas.get("label", {}).items())[-5:]))
    wartosci = dane.get("value", {})
    LOG.info("Liczba wartości: %d", len(wartosci))
    LOG.info("Wartości (ostatnie 5 wg klucza numerycznego): %s", dict(sorted(wartosci.items(), key=lambda kv: int(kv[0]))[-5:]))
    LOG.info("geo wymiar (do potwierdzenia, że przefiltrowało tylko PL): %s", wymiary.get("geo", {}).get("category", {}).get("index"))


if __name__ == "__main__":
    main()
