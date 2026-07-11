# web/

Next.js dashboard i symulator, do zbudowania w kolejnym etapie po ustabilizowaniu ETL.

## prototypes/

`prototypes/symulator_bilansow.jsx` to działający prototyp komponentu React
(suwaki dla zmiany wydatków rządowych, salda obrotów bieżących, zmiany stóp
procentowych i horyzontu symulacji, z wykresami PKB/długu i paskiem tożsamości
sektorowej). Logika liczbowa jest tożsama z `models/symulator_sfc.py` — to on
jest źródłem prawdy dla modelu, ten plik to punkt startowy do osadzenia w
przyszłej aplikacji Next.js, nie samodzielna aplikacja.
