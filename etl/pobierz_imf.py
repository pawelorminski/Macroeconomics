"""ETL: dane IMF World Economic Outlook / Balance of Payments, przez IMF
DataMapper API (www.imf.org/external/datamapper/api/v1).

Stary endpoint SDMX (dataservices.imf.org) już nie istnieje — nie rozwiązuje
się nawet DNS, IMF go wycofał. DataMapper to publiczne, nieudokumentowane
formalnie, ale stabilne API stojące za wizualizacjami na imf.org/external/datamapper,
i używa dokładnie tych samych krótkich kodów wskaźników, które już są w
`seria_template` w registry_wskaznikow.yaml (np. NGDP_RPCH, GGXWDG_NGDP) —
stąd pewność, że to właściwe źródło, nie zgadywanie.

Potwierdzone na żywo (zob. historia komitów — sonda _probe_sdmx.py, usunięta
po zakończeniu):
- GET /v1/{wskaznik} zwraca WSZYSTKIE kraje na raz — segment {country} w
  ścieżce jest ignorowany (te same bajty z i bez), więc pobieramy raz na
  wskaźnik, nie raz na kraj×wskaźnik.
- Klucze krajów w odpowiedzi to kody ISO3 zgodne z `registry_krajow.yaml`
  (potwierdzone: POL, EU obecne).
- WEO zawiera też lata prognozowane (do ok. 2031) — nie filtrujemy ich tu
  ręcznie, `waliduj_fakt` w etl/wspolne.py i tak odrzuca daty w przyszłości,
  więc trafiają do bazy tylko lata faktyczne/szacunkowe do dziś.
"""

from __future__ import annotations

import datetime as dt
import logging

import requests

from etl.wspolne import BladWalidacji, kraje, wskazniki_aktywne, zapisz_fakt

LOG = logging.getLogger(__name__)

BASE_URL = "https://www.imf.org/external/datamapper/api/v1"


def kod_wskaznika_imf(seria_template: str) -> str:
    """`'NGDP_RPCH.{country}'` -> `'NGDP_RPCH'` — DataMapper adresuje wskaźnik samą nazwą."""
    return seria_template.split(".")[0]


def pobierz_wskaznik(kod: str) -> dict[str, dict[str, float]]:
    """Pobiera pełny zbiór (wszystkie kraje, wszystkie lata) dla jednego wskaźnika DataMapper."""
    url = f"{BASE_URL}/{kod}"
    odpowiedz = requests.get(url, timeout=30)
    odpowiedz.raise_for_status()
    dane = odpowiedz.json()
    return dane.get("values", {}).get(kod, {})


def przetworz(wskaznik_id: str, zrodlo: str, kraj_kod: str, lata: dict[str, float]) -> list[dict]:
    wiersze = []
    for rok_str, wartosc in lata.items():
        try:
            rok = int(rok_str)
        except ValueError:
            continue
        wiersze.append(
            {
                "kraj_kod": kraj_kod,
                "wskaznik_id": wskaznik_id,
                "data": dt.date(rok, 12, 31),
                "wartosc": float(wartosc),
                "zrodlo": zrodlo,
            }
        )
    return wiersze


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    wskazniki_imf = [w for w in wskazniki_aktywne() if str(w.get("zrodlo", "")).startswith("IMF")]
    if not wskazniki_imf:
        LOG.info("Brak aktywnych wskaźników ze źródłem IMF w rejestrze.")
        return

    kody_krajow = [k["kod"] for k in kraje()]

    for wskaznik in wskazniki_imf:
        kod_imf = kod_wskaznika_imf(wskaznik["seria_template"])
        try:
            dane_wskaznika = pobierz_wskaznik(kod_imf)
        except requests.RequestException as blad:
            LOG.error("Błąd pobierania %s (%s) z IMF DataMapper: %s", wskaznik["id"], kod_imf, blad)
            continue

        if not dane_wskaznika:
            LOG.warning("IMF DataMapper zwrócił pusty zbiór dla %s", kod_imf)
            continue

        for kraj_kod in kody_krajow:
            lata = dane_wskaznika.get(kraj_kod)
            if lata is None:
                LOG.info("Brak danych %s dla kraju %s w IMF DataMapper", kod_imf, kraj_kod)
                continue

            wiersze = przetworz(wskaznik["id"], wskaznik["zrodlo"], kraj_kod, lata)
            for wiersz in wiersze:
                try:
                    zapisz_fakt(**wiersz)
                    LOG.info(
                        "Zapisano %s/%s/%s = %s",
                        wiersz["kraj_kod"],
                        wiersz["wskaznik_id"],
                        wiersz["data"],
                        wiersz["wartosc"],
                    )
                except BladWalidacji as blad:
                    LOG.info("Pominięto %s (poza zakresem/przyszłość): %s", wiersz, blad)
                except RuntimeError as blad:
                    LOG.warning("Zapis pominięty (%s). Wiersz do zapisania: %s", blad, wiersz)


if __name__ == "__main__":
    main()
