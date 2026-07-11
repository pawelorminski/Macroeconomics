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
