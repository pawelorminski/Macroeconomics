create table if not exists fakty_makro (
    id bigserial primary key,
    kraj_kod text not null,
    wskaznik_id text not null,
    data date not null,
    wartosc numeric not null,
    zrodlo text not null,
    pobrano_o timestamptz default now(),
    unique (kraj_kod, wskaznik_id, data)
);

create index if not exists idx_fakty_kraj_wskaznik on fakty_makro (kraj_kod, wskaznik_id);

-- Dodatek (poza pierwotną specyfikacją briefu): web/ czyta tę tabelę kluczem
-- anon/public po stronie klienta (zob. web/lib/supabase.ts). Bez RLS klucz
-- anon miałby domyślnie pełny dostęp zapisu, nie tylko odczytu. ETL pisze
-- kluczem service role, który omija RLS, więc poniższa polityka nie wpływa
-- na zapisy z etl/wspolne.py.
alter table fakty_makro enable row level security;

create policy "fakty_makro: odczyt publiczny"
    on fakty_makro for select
    to anon
    using (true);
