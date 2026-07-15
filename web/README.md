# web/

Dashboard i symulator Barometru Globalnego — Next.js (App Router,
TypeScript, Tailwind v4).

## Strony

- `/` — landing z linkami do symulatora i danych.
- `/symulator` — model bilansów sektorowych (`components/Symulator.tsx`),
  port jeden-do-jednego z `lib/symulator.ts`, który z kolei jest portem
  `models/symulator_sfc.py` — trzy implementacje (Python, ten plik TS,
  oryginalny prototyp w `prototypes/symulator_bilansow.jsx`) dają identyczne
  liczby dla tych samych parametrów wejściowych.
- `/dane` — ostatnie 50 wierszy z `fakty_makro`, czytane bezpośrednio z
  Supabase kluczem anon (server component, `app/dane/page.tsx`).

## Uruchomienie lokalne

```bash
npm install
cp .env.example .env.local   # uzupełnij NEXT_PUBLIC_SUPABASE_URL/ANON_KEY
npm run dev
```

Bez zmiennych Supabase strona `/dane` działa, ale pokazuje komunikat o braku
konfiguracji zamiast tabeli — `/symulator` i `/` działają zawsze, nie
zależą od bazy.

**Uwaga o kluczach**: `NEXT_PUBLIC_SUPABASE_ANON_KEY` to klucz publiczny,
bezpieczny w kodzie klienckim, o ile w bazie jest włączone Row Level
Security z polityką tylko-do-odczytu (zob. `db/schema.sql`). To NIE jest
ten sam klucz co `SUPABASE_KEY` (service role) używany przez ETL w
`etl/wspolne.py` — service role ma pełny dostęp zapisu i nigdy nie powinien
trafić do kodu przeglądarki.

## Build

```bash
npm run build
```

Zweryfikowane lokalnie (`npm run build` przechodzi czysto) w tym repo —
patrz commit wprowadzający tę aplikację.

## prototypes/

`prototypes/symulator_bilansow.jsx` to pierwotny, samodzielny prototyp
komponentu React, z którego powstał `components/Symulator.tsx`. Zostawiony
jako punkt odniesienia / archiwum, nie jest importowany przez aplikację.

## Deploy

Docelowo Vercel (patrz `SUPABASE_URL`/`SUPABASE_KEY` w sekretach GitHub dla
ETL — to osobna konfiguracja od zmiennych `NEXT_PUBLIC_*` tej aplikacji,
które ustawia się w Vercel Project Settings → Environment Variables).
