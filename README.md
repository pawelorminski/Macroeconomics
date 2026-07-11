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

`pobierz_nbp.py` i `pobierz_gus.py` są w pełni zaimplementowane (prawdziwe
zapytania HTTP, parsowanie, walidacja, upsert), ale **nie zostały jeszcze
przetestowane na żywym API** — to środowisko, w którym powstał ten kod, nie
ma dostępu do ogólnego ruchu wychodzącego do dowolnych hostów. Przed pierwszym
uruchomieniem produkcyjnym zrób smoke test lokalnie albo przez
`workflow_dispatch` w GitHub Actions i zweryfikuj, że odpowiedzi API pasują do
oczekiwanego kształtu. `pobierz_imf.py`, `pobierz_eurostat.py` i
`pobierz_danegovpl.py` to celowo szkielety — składnia zapytań SDMX (IMF,
Eurostat) i wybór konkretnych zbiorów (dane.gov.pl) wymagają przetestowania
na żywym API.

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
