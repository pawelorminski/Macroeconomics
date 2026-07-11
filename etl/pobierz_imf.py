"""ETL: dane IMF (World Economic Outlook / IFS / BOP), SDMX REST.

TODO: Składnia zapytań SDMX dla dataservices.imf.org jest nietrywialna
(struktura dataflow/key różni się między WEO, IFS i BOP) i wymaga
przetestowania interaktywnie na żywym API, czego nie dało się zrobić w tej
sesji (brak dostępu do dowolnych hostów z tego środowiska). Ten plik to
szkielet gotowy do dopisania — struktura funkcji odpowiada
`etl/pobierz_nbp.py` i `etl/pobierz_gus.py`, żeby dopisanie właściwych
zapytań SDMX nie wymagało przebudowy reszty.

Wskaźniki z registry_wskaznikow.yaml, które mają tu trafić:
- gdp_growth_yoy      (seria_template: NGDP_RPCH.{country}, zrodlo: IMF_WEO)
- gov_debt_gdp        (seria_template: GGXWDG_NGDP.{country}, zrodlo: IMF_WEO)
- gov_balance_gdp     (seria_template: GGXCNL_NGDP.{country}, zrodlo: IMF_WEO)
- primary_balance_gdp (seria_template: GGXONLB_NGDP.{country}, zrodlo: IMF_WEO)
- current_account_gdp (seria_template: BCA_NGDPD.{country}, zrodlo: IMF_BOP)
"""

from __future__ import annotations

import logging

from etl.wspolne import wskazniki_aktywne, kraje

LOG = logging.getLogger(__name__)

BASE_URL = "https://dataservices.imf.org/REST/SDMX_JSON.svc"


def zbuduj_zapytanie(seria_template: str, kod_kraju: str) -> str:
    """TODO: zbudować właściwy URL SDMX (dataflow + key) dla danej serii i kraju.

    Punkt startowy do sprawdzenia na żywo: {BASE_URL}/CompactData/{dataflow}/{key}
    gdzie `dataflow` to np. WEO, i `key` koduje wymiary (częstotliwość, kraj, wskaźnik).
    """
    raise NotImplementedError("Zapytanie SDMX do IMF wymaga przetestowania na żywym API")


def pobierz_serie(wskaznik: dict, kod_kraju: str) -> list[dict]:
    """TODO: wykonać zapytanie HTTP i sparsować odpowiedź SDMX-JSON na listę {data, wartosc}."""
    raise NotImplementedError


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    wskazniki_imf = [w for w in wskazniki_aktywne() if str(w.get("zrodlo", "")).startswith("IMF")]
    if not wskazniki_imf:
        LOG.info("Brak aktywnych wskaźników ze źródłem IMF w rejestrze.")
        return

    for wskaznik in wskazniki_imf:
        for kraj in kraje():
            LOG.info("TODO: pobrać %s dla %s z IMF (%s)", wskaznik["id"], kraj["kod"], wskaznik["zrodlo"])
            # try:
            #     serie = pobierz_serie(wskaznik, kraj["kod"])
            # except NotImplementedError:
            #     continue


if __name__ == "__main__":
    main()
