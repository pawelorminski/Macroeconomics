"""ETL: dane Eurostat, SDMX REST (ec.europa.eu/eurostat/api).

TODO: podobnie jak w przypadku IMF, dokładna składnia zapytań SDMX (kody
datasetów, filtry wymiarów) wymaga przetestowania na żywym API — nie dało
się tego zrobić w tej sesji (brak dostępu do dowolnych hostów z tego
środowiska). Szkielet poniżej odzwierciedla strukturę pozostałych
skryptów ETL, żeby dopisanie właściwych zapytań nie wymagało przebudowy.

Eurostat jest tu głównie źródłem uzupełniającym dla agregatu UE (kod EU
w registry_krajow.yaml) tam, gdzie IMF WEO nie publikuje agregatu unijnego.
"""

from __future__ import annotations

import logging

from etl.wspolne import wskazniki_aktywne

LOG = logging.getLogger(__name__)

BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data"


def zbuduj_zapytanie(dataset: str, filtr: str) -> str:
    """TODO: zbudować właściwy URL SDMX 2.1, np. {BASE_URL}/{dataset}/{filtr}?format=JSON."""
    raise NotImplementedError("Zapytanie SDMX do Eurostatu wymaga przetestowania na żywym API")


def pobierz_serie(dataset: str, filtr: str) -> list[dict]:
    """TODO: wykonać zapytanie HTTP i sparsować odpowiedź SDMX-JSON na listę {data, wartosc}."""
    raise NotImplementedError


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    LOG.info(
        "Szkielet pobierz_eurostat.py: %d aktywnych wskaźników w rejestrze, "
        "składnia zapytań SDMX do dopisania po weryfikacji na żywym API.",
        len(wskazniki_aktywne()),
    )


if __name__ == "__main__":
    main()
