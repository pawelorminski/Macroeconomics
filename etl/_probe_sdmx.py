"""Skrypt diagnostyczny, jednorazowy: sprawdza, które kandydackie endpointy IMF i
Eurostat faktycznie odpowiadają na żywo. Uruchamiany ręcznie przez workflow_dispatch,
nieużywany w codziennym ETL. Do usunięcia po ustaleniu właściwych URL-i.
"""

import logging

import requests

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

KANDYDACI = [
    ("IMF SDMX (stary)", "https://dataservices.imf.org/REST/SDMX_JSON.svc/Dataflow"),
    ("IMF DataMapper indicators", "https://www.imf.org/external/datamapper/api/v1/indicators"),
    ("IMF DataMapper NGDP_RPCH/POL", "https://www.imf.org/external/datamapper/api/v1/NGDP_RPCH/POL"),
    ("IMF DataMapper GGXWDG_NGDP/POL", "https://www.imf.org/external/datamapper/api/v1/GGXWDG_NGDP/POL"),
    ("IMF DataMapper NGDP_RPCH/EU", "https://www.imf.org/external/datamapper/api/v1/NGDP_RPCH/EU"),
    ("IMF DataMapper groups", "https://www.imf.org/external/datamapper/api/v1/groups"),
    (
        "Eurostat SDMX dataflow",
        "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/dataflow/ESTAT/all/latest?format=JSON",
    ),
    (
        "Eurostat namq_10_gdp EU27_2020",
        "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/namq_10_gdp"
        "?format=JSON&geo=EU27_2020&na_item=B1GQ&unit=CLV_PCH_PRE&s_adj=SCA&lang=en",
    ),
    (
        "Eurostat une_rt_m EU27_2020",
        "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/une_rt_m"
        "?format=JSON&geo=EU27_2020&s_adj=SA&age=TOTAL&sex=T&unit=PC_ACT&lang=en",
    ),
]


def main() -> None:
    for nazwa, url in KANDYDACI:
        try:
            odp = requests.get(url, timeout=20)
            fragment = odp.text[:300].replace("\n", " ")
            LOG.info("[%s] %s -> HTTP %s | %s", nazwa, url, odp.status_code, fragment)
        except requests.RequestException as blad:
            LOG.error("[%s] %s -> BŁĄD: %s", nazwa, url, blad)


if __name__ == "__main__":
    main()
