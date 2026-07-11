"""ETL: kursy walutowe NBP (api.nbp.pl).

API NBP nie wymaga klucza i zwraca JSON. Nie publikuje historii stopy
referencyjnej w czystym REST (to strona HTML), więc ten skrypt ciągnie
kursy średnie (tabela A) — dobre uzupełnienie dla wskaźników płynnościowych
i punkt odniesienia dla analiz kursowych.

Uwaga: ten kod nie mógł zostać przetestowany na żywym API z tej sesji
(środowisko sandboxowe blokuje ogólny ruch wychodzący do dowolnych hostów).
Endpointy i format odpowiedzi są zgodne z oficjalną dokumentacją NBP
(https://api.nbp.pl/), ale przed użyciem produkcyjnym warto zrobić szybki
smoke test (`python -m etl.pobierz_nbp`) w środowisku z pełnym dostępem
do sieci, np. w GitHub Actions.
"""

from __future__ import annotations

import datetime as dt
import logging

import requests

from etl.wspolne import BladWalidacji, zapisz_fakt

LOG = logging.getLogger(__name__)

BASE_URL = "https://api.nbp.pl/api/exchangerates/rates"
WALUTY = ("USD", "EUR")
TABELA = "A"


def pobierz_kurs(kod: str, tabela: str = TABELA, ostatnie_n: int = 5) -> list[dict]:
    """Pobiera ostatnie `ostatnie_n` notowań średniego kursu danej waluty."""
    url = f"{BASE_URL}/{tabela}/{kod}/last/{ostatnie_n}/?format=json"
    odpowiedz = requests.get(url, timeout=15)
    odpowiedz.raise_for_status()
    dane = odpowiedz.json()
    return dane.get("rates", [])


def przetworz(kod: str, notowania: list[dict]) -> list[dict]:
    """Zamienia surowe notowania NBP na wiersze gotowe do zapisu w fakty_makro."""
    wiersze = []
    for notowanie in notowania:
        wiersze.append(
            {
                "kraj_kod": "POL",
                "wskaznik_id": f"fx_rate_{kod.lower()}_pln",
                "data": dt.date.fromisoformat(notowanie["effectiveDate"]),
                "wartosc": float(notowanie["mid"]),
                "zrodlo": "NBP",
            }
        )
    return wiersze


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    for kod in WALUTY:
        try:
            notowania = pobierz_kurs(kod)
        except requests.RequestException as blad:
            LOG.error("Błąd pobierania kursu %s z NBP: %s", kod, blad)
            continue

        wiersze = przetworz(kod, notowania)
        for wiersz in wiersze:
            try:
                zapisz_fakt(**wiersz)
                LOG.info("Zapisano %s/%s/%s = %.4f", wiersz["kraj_kod"], wiersz["wskaznik_id"], wiersz["data"], wiersz["wartosc"])
            except BladWalidacji as blad:
                LOG.warning("Pominięto niepoprawny wiersz %s: %s", wiersz, blad)
            except RuntimeError as blad:
                # brak konfiguracji Supabase — pokaż co by zostało zapisane i przerwij pętlę
                LOG.warning("Zapis pominięty (%s). Wiersz do zapisania: %s", blad, wiersz)


if __name__ == "__main__":
    main()
