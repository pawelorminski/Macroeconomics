"""Runda 2 sondy diagnostycznej: sprawdza dokładny kształt odpowiedzi IMF
DataMapper (czy filtr kraju w URL działa) i Eurostat JSON-stat (jak zdekodować
wymiar czasu). Tymczasowe, do usunięcia po ustaleniu implementacji.
"""

import json
import logging

import requests

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


def main() -> None:
    # 1. Czy /{indicator}/{country} filtruje po kraju, czy zwraca wszystko?
    odp = requests.get("https://www.imf.org/external/datamapper/api/v1/NGDP_RPCH/POL", timeout=20)
    dane = odp.json()
    kraje_w_odpowiedzi = list(dane["values"]["NGDP_RPCH"].keys())
    LOG.info("NGDP_RPCH/POL -> liczba krajów w odpowiedzi: %d", len(kraje_w_odpowiedzi))
    LOG.info("Czy 'POL' jest w kluczach: %s", "POL" in kraje_w_odpowiedzi)
    LOG.info("Czy 'EU' jest w kluczach: %s", "EU" in kraje_w_odpowiedzi)
    if "POL" in dane["values"]["NGDP_RPCH"]:
        pol = dane["values"]["NGDP_RPCH"]["POL"]
        ostatnie = dict(list(pol.items())[-5:])
        LOG.info("POL ostatnie 5 lat: %s", ostatnie)
    LOG.info("Pierwsze 10 kluczy krajów: %s", kraje_w_odpowiedzi[:10])

    # 2. Ta sama zmienna, ale zapytanie BEZ segmentu kraju w URL, dla porównania rozmiaru odpowiedzi
    odp2 = requests.get("https://www.imf.org/external/datamapper/api/v1/NGDP_RPCH", timeout=20)
    LOG.info("NGDP_RPCH (bez kraju) -> rozmiar odpowiedzi: %d znaków", len(odp2.text))
    LOG.info("NGDP_RPCH (z /POL) -> rozmiar odpowiedzi: %d znaków", len(odp.text))

    # 3. Eurostat JSON-stat: pełna struktura dla jednego wskaźnika/kraju, żeby zrozumieć wymiar czasu
    odp3 = requests.get(
        "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/une_rt_a",
        params={"format": "JSON", "geo": "EU27_2020", "s_adj": "NSA", "age": "TOTAL", "sex": "T", "unit": "PC_ACT", "lang": "en"},
        timeout=20,
    )
    dane3 = odp3.json()
    LOG.info("Eurostat une_rt_a klucze najwyższego poziomu: %s", list(dane3.keys()))
    LOG.info("Eurostat 'id' (kolejność wymiarów): %s", dane3.get("id"))
    LOG.info("Eurostat 'size' (rozmiary wymiarów): %s", dane3.get("size"))
    czas = dane3.get("dimension", {}).get("time", {}).get("category", {})
    LOG.info("Eurostat wymiar czasu - index (pierwsze 5): %s", dict(list(czas.get("index", {}).items())[:5]))
    LOG.info("Eurostat 'value' (surowe): %s", dane3.get("value"))
    LOG.info("Eurostat 'status' (braki danych, jeśli są): %s", dane3.get("status"))


if __name__ == "__main__":
    main()
