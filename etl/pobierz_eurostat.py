"""ETL: dane Eurostat, JSON-stat REST (ec.europa.eu/eurostat/api/dissemination).

Zakres celowo ograniczony do tego, co faktycznie zweryfikowano na żywo (zob.
historia komitów — sonda _probe_sdmx.py, usunięta po zakończeniu):

- Dataset `une_rt_m` (stopa bezrobocia, miesięczna) dla `geo=EU27_2020`
  potwierdzony end-to-end: kształt JSON-stat rozpracowany (pola id/size/
  dimension/value), wartości sensowne (~6% dla UE).
- Dataset `namq_10_gdp` (PKB, kwartalne) też odpowiedział HTTP 200 z danymi,
  ALE nie zweryfikowano, który kod jednostki (`unit`) odpowiada wzrostowi
  r/r (`gdp_growth_yoy` w rejestrze) a który q/q — `CLV_PCH_PRE` użyty w
  sondzie to prawdopodobnie zmiana kw/kw, nie r/r. Podpięcie tego bez
  potwierdzenia ryzykowałoby zapisanie danych pod złą etykietą
  częstotliwości, więc zostaje jako TODO, nie zgadywanie.

Eurostat pokrywa tu wyłącznie agregat UE (`registry_krajow.yaml`, kod `EU`)
jako uzupełnienie tam, gdzie IMF DataMapper nie ma tego wskaźnika (np.
unemployment_rate, którego IMF w ogóle nie publikuje) — zgodnie z notatką w
brief_claude_code.md, że Eurostat jest tu źródłem uzupełniającym, nie
głównym.
"""

from __future__ import annotations

import calendar
import datetime as dt
import logging

import requests

from etl.wspolne import BladWalidacji, zapisz_fakt

LOG = logging.getLogger(__name__)

BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"

# geo Eurostatu dla naszego kodu "EU" z registry_krajow.yaml — Eurostat nie używa
# gołego "EU", tylko konkretnej definicji składu (UE-27 po Brexicie).
GEO_EU = "EU27_2020"


def pobierz_json_stat(dataset: str, **filtry: str) -> dict:
    parametry = {"format": "JSON", "lang": "en", **filtry}
    odpowiedz = requests.get(f"{BASE_URL}/{dataset}", params=parametry, timeout=30)
    odpowiedz.raise_for_status()
    dane = odpowiedz.json()
    if "error" in dane and "value" not in dane:
        raise ValueError(f"Eurostat zwrócił błąd dla {dataset}/{filtry}: {dane['error']}")
    return dane


def wartosci_czasowe(dane_json_stat: dict) -> dict[str, float]:
    """Zakłada, że WSZYSTKIE wymiary poza `time` są zawężone do jednej wartości
    filtrami zapytania (tak jak w `main()` niżej) — wtedy klucz w `value` to
    wprost indeks pozycji na osi czasu, bez potrzeby dekodowania pełnego
    iloczynu kartezjańskiego wymiarów JSON-stat.
    """
    indeks_do_etykiety = {
        str(i): etykieta
        for etykieta, i in dane_json_stat["dimension"]["time"]["category"]["index"].items()
    }
    return {
        indeks_do_etykiety[klucz]: wartosc
        for klucz, wartosc in dane_json_stat.get("value", {}).items()
        if klucz in indeks_do_etykiety
    }


def etykieta_na_date(etykieta: str) -> dt.date:
    """'2026-05' (miesięczne) -> ostatni dzień maja 2026."""
    rok, miesiac = (int(x) for x in etykieta.split("-"))
    ostatni_dzien = calendar.monthrange(rok, miesiac)[1]
    return dt.date(rok, miesiac, ostatni_dzien)


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    try:
        dane = pobierz_json_stat(
            "une_rt_m",
            geo=GEO_EU,
            s_adj="SA",
            age="TOTAL",
            sex="T",
            unit="PC_ACT",
        )
    except (requests.RequestException, ValueError) as blad:
        LOG.error("Błąd pobierania stopy bezrobocia UE z Eurostatu: %s", blad)
        return

    for etykieta, wartosc in wartosci_czasowe(dane).items():
        wiersz = {
            "kraj_kod": "EU",
            "wskaznik_id": "unemployment_rate",
            "data": etykieta_na_date(etykieta),
            "wartosc": float(wartosc),
            "zrodlo": "Eurostat",
        }
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
            LOG.info("Pominięto %s (poza zakresem): %s", wiersz, blad)
        except RuntimeError as blad:
            LOG.warning("Zapis pominięty (%s). Wiersz do zapisania: %s", blad, wiersz)

    LOG.info(
        "TODO: gdp_growth_yoy dla EU (namq_10_gdp) — kod jednostki r/r vs kw/kw "
        "wymaga jeszcze jednej weryfikacji na żywym API przed podpięciem, "
        "zob. docstring modułu."
    )


if __name__ == "__main__":
    main()
