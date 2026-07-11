"""ETL: dane.gov.pl (api.dane.gov.pl), katalog CKAN-podobny.

TODO: dane.gov.pl agreguje ok. 25 tys. zbiorów, z czego około 400 ma
bezpośrednie API (dokumentacja Swagger pod /doc). Traktować jako źródło
uzupełniające dla zbiorów resortowych (np. dane specyficzne dla Polski
niedostępne w GUS BDL / IMF), nie jako główne źródło szeregów makro —
te lepiej ciągnąć z GUS BDL i IMF. Wymaga wyboru konkretnych zbiorów
danych (dataset id) do zaciągania, co powinno być ustalone po przejrzeniu
katalogu na żywo.
"""

from __future__ import annotations

import logging

LOG = logging.getLogger(__name__)

BASE_URL = "https://api.dane.gov.pl/1.4"


def szukaj_zbiorow(fraza: str) -> list[dict]:
    """TODO: GET {BASE_URL}/datasets?q={fraza} — wyszukiwanie zbiorów po słowie kluczowym."""
    raise NotImplementedError("Wybór zbiorów danych z dane.gov.pl wymaga przeglądu katalogu na żywo")


def pobierz_zasob(dataset_id: str, zasob_id: str) -> list[dict]:
    """TODO: GET {BASE_URL}/datasets/{dataset_id}/resources/{zasob_id}/data — pobranie danych zasobu."""
    raise NotImplementedError


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    LOG.info(
        "Szkielet pobierz_danegovpl.py: brak jeszcze wybranych zbiorów danych. "
        "Uzupełnić po przejrzeniu katalogu api.dane.gov.pl na żywo."
    )


if __name__ == "__main__":
    main()
