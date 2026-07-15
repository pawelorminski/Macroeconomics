# Barometr Globalny

Narzędzie do zbierania, przechowywania i analizy globalnych danych
makroekonomicznych (Polska jako priorytet, pełne G20, agregaty UE i Świat),
z rejestrem wskaźników pozwalającym dodawać nowe serie bez zmian w kodzie ETL,
oraz edukacyjnym modelem bilansów sektorowych (Godley/SFC) symulującym wpływ
decyzji fiskalnych i monetarnych na PKB, dług publiczny i bilanse sektora
prywatnego/publicznego/zagranicznego. Zebrane dane mają docelowo zasilać
automatyczne generowanie treści (Substack, X, Instagram, LinkedIn).

## Struktura repozytorium

```
.
├── data/
│   ├── registry_wskaznikow.yaml   # rejestr wskaźników — dodanie = nowy wpis, bez zmian w kodzie
│   └── registry_krajow.yaml       # rejestr krajów/agregatów (Polska, G20, UE, Świat)
├── etl/
│   ├── wspolne.py                 # wczytywanie rejestru, walidacja, upsert do Supabase
│   ├── pobierz_nbp.py             # kursy walutowe NBP — w pełni działający
│   ├── pobierz_gus.py             # dane GUS BDL — w pełni działający
│   ├── pobierz_imf.py             # szkielet, SDMX do dopisania po testach na żywo
│   ├── pobierz_eurostat.py        # szkielet, SDMX do dopisania po testach na żywo
│   └── pobierz_danegovpl.py       # szkielet, katalog do przejrzenia na żywo
├── models/
│   └── symulator_sfc.py           # model bilansów sektorowych, port 1:1 z prototypu React
├── db/
│   └── schema.sql                 # schemat tabeli fakty_makro (Postgres/Supabase)
├── web/
│   ├── README.md
│   └── prototypes/symulator_bilansow.jsx  # prototyp UI symulatora (React + recharts)
├── content/
│   ├── prompts/                   # prompty do generowania treści
│   └── templates/                 # szablony postów (Substack, X, Instagram, LinkedIn)
└── .github/workflows/etl_daily.yml
```

## Uruchomienie lokalne

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # uzupełnij SUPABASE_URL / SUPABASE_KEY
```

Utwórz tabelę w Postgresie/Supabase:

```bash
psql "$SUPABASE_DB_URL" -f db/schema.sql
```

Uruchom pojedynczy ETL (bez zmiennych Supabase w środowisku skrypty tylko
logują, co by zapisały, i nie przerywają się błędem):

```bash
python -m etl.pobierz_nbp
python -m etl.pobierz_gus
```

Uruchom model symulatora:

```bash
python -c "
from models.symulator_sfc import symuluj, tozsamosc_sektorowa
print(symuluj(delta_g=2, delta_r=0, horyzont=8)['postkeynesowska'])
print(tozsamosc_sektorowa(delta_g=2, cab=-1))
"
```

### Stan ETL

`pobierz_nbp.py` i `pobierz_gus.py` zostały zweryfikowane na żywym API przez
`workflow_dispatch` w GitHub Actions (zapytania nie mogły zostać przetestowane
z sandboxa, w którym powstał ten kod — brak tam dostępu do ogólnego ruchu
wychodzącego):

- **NBP**: pobrał realne kursy średnie USD/PLN i EUR/PLN z ostatnich 5 dni
  roboczych, poprawnie sparsowane i zwalidowane.
- **GUS BDL**: wyszukał zmienną „stopa bezrobocia rejestrowanego” i pobrał
  realne wartości roczne 2011–2025 (13,1% → 5,4%, zgodne ze znanymi danymi
  GUS); walidacja poprawnie odrzuciła nieprawidłowy wiersz z datą w
  przyszłości. Uwaga: `szukaj_zmiennej()` bierze pierwsze dopasowanie po
  nazwie — GUS BDL bywa ma kilka podobnie nazwanych zmiennych o różnej
  granulacji, więc przy dodawaniu kolejnych fraz w `SZUKANE_ZMIENNE` warto
  przejrzeć logi (`Fraza ... ma N dopasowań ...`) i w razie potrzeby
  doprecyzować wybór.

`pobierz_imf.py` jest teraz w pełni zaimplementowany i zweryfikowany na
żywo. Stary endpoint SDMX (`dataservices.imf.org`) już nie istnieje — DNS
się nie rozwiązuje, IMF go wycofał. Zamiast niego użyty jest IMF DataMapper
API (`www.imf.org/external/datamapper/api/v1`), potwierdzony na żywo:
zwraca WSZYSTKIE kraje jednym zapytaniem na wskaźnik (segment `{country}` w
starym szkielecie URL okazał się ignorowany), z kluczami ISO3 zgodnymi z
`registry_krajow.yaml` (POL i EU obecne). WEO zawiera też lata prognozowane
do ok. 2031 — nie są filtrowane ręcznie, bo istniejąca walidacja dat w
`etl/wspolne.py` i tak odrzuca wiersze z datą w przyszłości.

Zweryfikowane na żywo end-to-end (realne wartości, zero błędów) dla
`gdp_growth_yoy`, `gov_debt_gdp`, `gov_balance_gdp`, `current_account_gdp`
— po tysiące wierszy na wskaźnik, w tym sensowne liczby jak dług Brazylii
88.9%/83.9%/84.0% PKB za 2021–2023. Jeden realny problem znaleziony po
drodze: kod serii `GGXONLB_NGDP` dla `primary_balance_gdp` z rejestru **nie
istnieje** w DataMapperze — zwraca pusty zbiór (kod obsłużył to bez błędu,
tylko logiem ostrzeżenia i pominięciem). Właściwy kod DataMapper dla salda
pierwotnego trzeba jeszcze ustalić i poprawić w
`data/registry_wskaznikow.yaml`.

`pobierz_eurostat.py` jest częściowo zaimplementowany: stopa bezrobocia dla
agregatu UE (`une_rt_m`, geo `EU27_2020`) działa end-to-end na żywych
danych — struktura JSON-stat (pola `id`/`size`/`dimension`/`value`)
rozpracowana i przetestowana, 317 realnych miesięcznych wierszy od 2000
roku (9,7% na start, 5,9% w maju 2026, zgodne ze znaną historią stopy
bezrobocia w UE). Wzrost PKB r/r dla UE zostaje jako TODO świadomie:
dataset `namq_10_gdp` odpowiada, ale nie zweryfikowano, który kod jednostki
oznacza zmianę r/r a który kw/kw — wolę zostawić to jako jawny brak niż
zapisać dane pod błędną etykietą częstotliwości.

`pobierz_danegovpl.py` zostaje szkieletem — wybór konkretnych zbiorów z
katalogu ok. 25 tys. datasetów wymaga przeglądu, nie samej weryfikacji
jednego endpointu.

Wszystkie zapisy do Supabase są nadal pomijane tylko dlatego, że sekrety
`SUPABASE_URL`/`SUPABASE_KEY` nie są jeszcze skonfigurowane w repo (GitHub
Settings → Secrets and variables → Actions) — reszta ścieżki (HTTP,
parsowanie, walidacja) działa bez błędów dla NBP, GUS BDL, IMF i
częściowo Eurostatu.

## Dodawanie nowego wskaźnika

Nowy wskaźnik to nowy wpis w `data/registry_wskaznikow.yaml`, bez zmian w
kodzie ETL (o ile źródło jest już obsługiwane przez istniejący skrypt).
Przykład — dodanie realnego tempa wzrostu płac jako wskaźnika pochodnego:

```yaml
- id: real_wage_growth_yoy
  nazwa_pl: "Wzrost płac realnych r/r"
  kategoria: praca
  zrodlo: pochodna
  formula: "nominal_wage_growth_yoy - cpi_yoy"
  czestotliwosc: kwartalna
  jednostka: procent
  aktywny: true
```

Pola:
- `id` — unikalny identyfikator, używany jako `wskaznik_id` w tabeli `fakty_makro`.
- `zrodlo` — nazwa źródła (`OECD`, `IMF_WEO`, `IMF_BOP`, `BIS`, `FRED`, `pochodna`, ...).
- `seria_template` — szablon kodu serii źródła, z `{country}` podstawianym per kraj (pomijane dla wskaźników pochodnych).
- `formula` — tylko dla `zrodlo: pochodna`, wyrażenie odwołujące się do innych `id` z rejestru.
- `aktywny` — `false` wyłącza wskaźnik z przetwarzania bez usuwania definicji.

Analogicznie `data/registry_krajow.yaml` — nowy kraj to nowy wpis `{ kod, nazwa_pl, grupa }`.

## Model symulatora

`models/symulator_sfc.py` to uproszczony, edukacyjny model bilansów
sektorowych (Godley/SFC). Warstwa tożsamości księgowej
(`tozsamosc_sektorowa`) jest zawsze prawdziwa rachunkowo, niezależnie od
założeń. Warstwa mnożnikowa (`symuluj`) to jawnie oznaczone założenie
ilustracyjne — trzy szkoły ekonomiczne (neoklasyczna, głównego nurtu,
postkeynesowska/MMT) różnią się przyjętym mnożnikiem fiskalnym, więc dają
inne trajektorie PKB i długu dla tej samej decyzji politycznej. To nie są
trzy prognozy do wyboru, tylko pokazanie wrażliwości wyniku na założenie.

Model w Pythonie jest portem 1:1 prototypu React w
`web/prototypes/symulator_bilansow.jsx` — te same stałe startowe i te same
wzory, więc obie wersje dają identyczne liczby.

## Stack

- **Baza**: Postgres hostowany na Supabase — darmowy plan wystarcza na start, daje automatyczne REST API nad tabelami bez własnego backendu.
- **Harmonogram**: GitHub Actions (`cron`), bez dodatkowej infrastruktury.
- **Web**: Next.js na Vercel w kolejnym etapie (patrz `web/README.md`).
