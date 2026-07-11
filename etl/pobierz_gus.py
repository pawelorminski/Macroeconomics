"""ETL: dane z GUS BDL (Bank Danych Lokalnych, api.bdl.stat.gov.pl).

Zamiast hardkodować numeryczne identyfikatory zmiennych GUS (są nieudokumentowane
semantycznie i łatwo je pomylić), skrypt najpierw wyszukuje zmienną po nazwie
przez `/variables/search`, a dopiero potem pobiera dane po jej id. Działa bez
klucza API przy niższych limitach; ustaw GUS_BDL_API_KEY, żeby podnieść limit
(nagłówek X-ClientId).

Uwaga: ten kod nie mógł zostać przetestowany na żywym API z tej sesji
(środowisko sandboxowe blokuje ogólny ruch wychodzący do dowolnych hostów).
Endpointy są zgodne z oficjalną dokumentacją GUS BDL
(https://api.bdl.stat.gov.pl/), ale przed użyciem produkcyjnym warto zrobić
szybki smoke test (`python -m etl.pobierz_gus`) w środowisku z pełnym
dostępem do sieci, np. w GitHub Actions.
"""

from __future__ import annotations

import datetime as dt
import logging
import os

import requests

from etl.wspolne import BladWalidacji, zapisz_fakt

LOG = logging.getLogger(__name__)

BASE_URL = "https://bdl.stat.gov.pl/api/v1"
JEDNOSTKA_POLSKA = "000000000000"  # id jednostki terytorialnej najwyższego poziomu (cały kraj)

# Frazy do wyszukania w GUS BDL -> docelowy wskaznik_id z registry_wskaznikow.yaml
SZUKANE_ZMIENNE = {
    "stopa bezrobocia rejestrowanego": "unemployment_rate",
}


def _naglowki() -> dict[str, str]:
    klucz = os.environ.get("GUS_BDL_API_KEY")
    return {"X-ClientId": klucz} if klucz else {}


def szukaj_zmiennej(fraza: str) -> list[dict]:
    """Wyszukuje zmienne BDL po nazwie, zwraca listę pasujących definicji (z ich id)."""
    url = f"{BASE_URL}/variables/search"
    odpowiedz = requests.get(
        url,
        params={"name": fraza, "lang": "pl", "format": "json", "page-size": 10},
        headers=_naglowki(),
        timeout=15,
    )
    odpowiedz.raise_for_status()
    return odpowiedz.json().get("results", [])


def pobierz_dane(zmienna_id: int, jednostka_id: str = JEDNOSTKA_POLSKA) -> list[dict]:
    """Pobiera szereg czasowy dla danej zmiennej i jednostki terytorialnej."""
    url = f"{BASE_URL}/data/by-unit/{jednostka_id}"
    odpowiedz = requests.get(
        url,
        params={"var-id": zmienna_id, "lang": "pl", "format": "json"},
        headers=_naglowki(),
        timeout=15,
    )
    odpowiedz.raise_for_status()
    dane = odpowiedz.json()
    wyniki = dane.get("results", [])
    if not wyniki:
        return []
    return wyniki[0].get("values", [])


def przetworz(wskaznik_id: str, wartosci: list[dict]) -> list[dict]:
    """Zamienia surowe punkty danych BDL (rok/okres + wartość) na wiersze fakty_makro."""
    wiersze = []
    for punkt in wartosci:
        rok = punkt.get("year")
        if rok is None or punkt.get("val") is None:
            continue
        wiersze.append(
            {
                "kraj_kod": "POL",
                "wskaznik_id": wskaznik_id,
                "data": dt.date(int(rok), 12, 31),
                "wartosc": float(punkt["val"]),
                "zrodlo": "GUS_BDL",
            }
        )
    return wiersze


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    for fraza, wskaznik_id in SZUKANE_ZMIENNE.items():
        try:
            trafienia = szukaj_zmiennej(fraza)
        except requests.RequestException as blad:
            LOG.error("Błąd wyszukiwania zmiennej '%s' w GUS BDL: %s", fraza, blad)
            continue

        if not trafienia:
            LOG.warning("Brak dopasowań w GUS BDL dla frazy '%s'", fraza)
            continue

        zmienna_id = trafienia[0]["id"]
        LOG.info("Znaleziono zmienną id=%s dla '%s': %s", zmienna_id, fraza, trafienia[0].get("n1", ""))

        try:
            wartosci = pobierz_dane(zmienna_id)
        except requests.RequestException as blad:
            LOG.error("Błąd pobierania danych dla zmiennej %s: %s", zmienna_id, blad)
            continue

        wiersze = przetworz(wskaznik_id, wartosci)
        for wiersz in wiersze:
            try:
                zapisz_fakt(**wiersz)
                LOG.info("Zapisano %s/%s/%s = %.2f", wiersz["kraj_kod"], wiersz["wskaznik_id"], wiersz["data"], wiersz["wartosc"])
            except BladWalidacji as blad:
                LOG.warning("Pominięto niepoprawny wiersz %s: %s", wiersz, blad)
            except RuntimeError as blad:
                LOG.warning("Zapis pominięty (%s). Wiersz do zapisania: %s", blad, wiersz)


if __name__ == "__main__":
    main()
