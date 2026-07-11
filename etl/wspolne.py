"""Funkcje pomocnicze współdzielone przez skrypty ETL."""

from __future__ import annotations

import datetime as dt
import os
from pathlib import Path
from typing import Any

import yaml

KATALOG_GLOWNY = Path(__file__).resolve().parent.parent
REJESTR_WSKAZNIKOW = KATALOG_GLOWNY / "data" / "registry_wskaznikow.yaml"
REJESTR_KRAJOW = KATALOG_GLOWNY / "data" / "registry_krajow.yaml"

DATA_MIN = dt.date(1950, 1, 1)


class BladWalidacji(ValueError):
    pass


def wczytaj_rejestr(sciezka: Path | str = REJESTR_WSKAZNIKOW) -> list[dict[str, Any]]:
    """Wczytuje rejestr wskaźników (lub krajów) z pliku YAML."""
    with open(sciezka, encoding="utf-8") as plik:
        return yaml.safe_load(plik) or []


def wskazniki_aktywne(rejestr: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Zwraca tylko wskaźniki oznaczone jako aktywny: true, pomija pochodne bez seria_template."""
    if rejestr is None:
        rejestr = wczytaj_rejestr(REJESTR_WSKAZNIKOW)
    return [w for w in rejestr if w.get("aktywny") and w.get("seria_template")]


def kraje(rejestr: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    if rejestr is None:
        rejestr = wczytaj_rejestr(REJESTR_KRAJOW)
    return rejestr


def waliduj_fakt(kraj_kod: str, wskaznik_id: str, data: dt.date, wartosc: float) -> None:
    """Podstawowa walidacja pojedynczego faktu przed zapisem: brak null i sensowny zakres daty."""
    if wartosc is None:
        raise BladWalidacji(f"Brak wartości dla {kraj_kod}/{wskaznik_id}/{data}")
    if not isinstance(wartosc, (int, float)):
        raise BladWalidacji(f"Wartość nienumeryczna dla {kraj_kod}/{wskaznik_id}/{data}: {wartosc!r}")
    if data is None:
        raise BladWalidacji(f"Brak daty dla {kraj_kod}/{wskaznik_id}")
    dzis = dt.date.today()
    if data < DATA_MIN or data > dzis + dt.timedelta(days=1):
        raise BladWalidacji(f"Data poza sensownym zakresem dla {kraj_kod}/{wskaznik_id}: {data}")


def _klient_supabase():
    """Tworzy klienta Supabase na podstawie zmiennych środowiskowych.

    Wymaga SUPABASE_URL i SUPABASE_KEY. Nie zgaduje ani nie zapisuje wartości domyślnych —
    brak zmiennych powinien jawnie przerwać zapis, a nie pisać do przypadkowej bazy.
    """
    from supabase import Client, create_client

    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError(
            "Brak SUPABASE_URL / SUPABASE_KEY w środowisku. Ustaw je przed próbą zapisu do bazy."
        )
    return create_client(url, key)


def zapisz_fakt(
    kraj_kod: str,
    wskaznik_id: str,
    data: dt.date,
    wartosc: float,
    zrodlo: str,
    klient=None,
) -> None:
    """Upsert pojedynczego wiersza do tabeli fakty_makro, klucz: kraj_kod + wskaznik_id + data."""
    waliduj_fakt(kraj_kod, wskaznik_id, data, wartosc)
    if klient is None:
        klient = _klient_supabase()
    klient.table("fakty_makro").upsert(
        {
            "kraj_kod": kraj_kod,
            "wskaznik_id": wskaznik_id,
            "data": data.isoformat(),
            "wartosc": wartosc,
            "zrodlo": zrodlo,
        },
        on_conflict="kraj_kod,wskaznik_id,data",
    ).execute()


def zapisz_wiele(fakty: list[dict[str, Any]], klient=None) -> int:
    """Waliduje i zapisuje listę faktów (słowniki z kluczami kraj_kod, wskaznik_id, data, wartosc, zrodlo).

    Zwraca liczbę zapisanych wierszy.
    """
    if klient is None:
        klient = _klient_supabase()
    zapisane = 0
    for fakt in fakty:
        zapisz_fakt(
            kraj_kod=fakt["kraj_kod"],
            wskaznik_id=fakt["wskaznik_id"],
            data=fakt["data"],
            wartosc=fakt["wartosc"],
            zrodlo=fakt["zrodlo"],
            klient=klient,
        )
        zapisane += 1
    return zapisane
