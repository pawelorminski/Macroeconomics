# Prompt: post na Substack

## Wejście

- Wynik `wybor_tematu.md` (wybrany wiersz + uzasadnienie).
- Opcjonalnie: 2-3 dodatkowe powiązane wskaźniki dla kontekstu (np. przy
  temacie inflacji — stopa referencyjna i realna stopa procentowa).
- Szablon: `templates/substack.md`.

## Instrukcja

Napisz długą formę (600-1000 słów) w stylu newslettera analitycznego —
zaczynasz od liczby i jej znaczenia, nie od ogólników. Struktura:

1. **Lead** (2-3 zdania) — sama liczba, zmiana, i dlaczego to dziś temat.
2. **Kontekst** — jak ten odczyt wygląda na tle historii tego wskaźnika dla
   tego kraju (trend, poprzednie punkty zwrotne), z konkretnymi liczbami, nie
   ogólnym „rośnie od jakiegoś czasu”.
3. **Mechanizm** — *dlaczego* to się dzieje, jeśli da się to wywnioskować z
   powiązanych wskaźników w danych wejściowych. Jeśli przyczyna wymaga
   spekulacji wykraczającej poza dane, jasno to oznacz jako interpretację, nie
   fakt.
4. **Rozbieżność ocen** (tylko dla tematów fiskalnych/monetarnych) — pokaż,
   jak inaczej oceniłyby to neoklasyczna, głównego nurtu i postkeynesowska
   szkoła ekonomiczna, odwołując się do logiki `models/symulator_sfc.py`
   (różne mnożniki fiskalne = różne wnioski o tej samej liczbie), bez
   wskazywania, która szkoła ma rację.
5. **Co obserwować dalej** — 1-2 konkretne przyszłe daty/wydarzenia (kolejny
   odczyt, decyzja RPP/EBC/Fed), nie ogólne „warto śledzić sytuację”.

Zakaz: frazesów bez treści ("w niepewnych czasach", "jak wiadomo"), doradzania
konkretnych decyzji inwestycyjnych, twierdzenia z pewnością o przyszłości.

Zakończ zawsze zastrzeżeniem z `templates/substack.md` (nie pomijaj, nie
parafrazuj na coś słabszego).
