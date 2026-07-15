# content/

Prompty i szablony do automatycznego generowania treści (Substack, X,
Instagram, LinkedIn) na bazie danych z tabeli `fakty_makro` i rejestrów w
`data/`. To warstwa nad ETL i modelem — nie ETL sam w sobie.

## Przepływ

1. **Wybór tematu** — `prompts/wybor_tematu.md` bierze świeże wiersze z
   `fakty_makro` (nowe od ostatniego uruchomienia, plus wartość poprzednia dla
   porównania r/r lub m/m) i wybiera, który wskaźnik/kraj jest dziś wart posta
   — po skali zmiany, nie po przypadkowej kolejności.
2. **Generowanie treści per kanał** — `prompts/post_substack.md`,
   `prompts/post_x.md`, `prompts/post_instagram.md`,
   `prompts/post_linkedin.md` biorą wybrany temat (wynik kroku 1) i
   `nazwa_pl`/`jednostka`/`zrodlo` z `registry_wskaznikow.yaml`, i generują
   treść w formacie odpowiedniego szablonu z `templates/`.
3. **Szablony** w `templates/` to gotowa struktura wyjścia (pola do
   wypełnienia), nie treść — pilnują spójnego formatu niezależnie od tego,
   który model/prompt generował dany post.

To celowo nie jest jeszcze zautomatyzowane (brak orkiestracji / wywołania
LLM w kodzie) — pierwszy krok to mieć sprawdzone prompty i szablony do ręcznego
użycia, automatyzacja (kolejny krok w GitHub Actions albo osobny serwis) ma
sens dopiero gdy ETL faktycznie zasila bazę danymi (patrz `README.md` w
katalogu głównym, sekcja „Stan ETL”).

## Ton i zasady, wspólne dla wszystkich kanałów

- Materiał **edukacyjny**, nie jest rekomendacją inwestycyjną ani prognozą —
  to samo zastrzeżenie, które nosi symulator w `web/prototypes/symulator_bilansow.jsx`
  ("Symulator edukacyjny · nie jest prognozą"). Utrzymuj tę samą uczciwość w
  treściach: liczby i tożsamości księgowe są faktami, interpretacje —
  jawnie oznaczonymi założeniami.
- Zawsze podawaj źródło (`zrodlo` z rejestru) i datę danych — bez tego liczba
  nie jest weryfikowalna.
- Gdzie temat dotyczy polityki fiskalnej/monetarnej i jest miejsce na niuans
  (dług, deficyt, stopy), pokazuj rozbieżność ocen między szkołami
  ekonomicznymi (neoklasyczna / głównego nurtu / postkeynesowska), zamiast
  podawać jedną liczbę jako bezsporną prawdę — spójne z `models/symulator_sfc.py`.
- Priorytet: Polska. Reszta krajów G20 i agregaty (UE, Świat) jako kontekst
  porównawczy, nie temat sam w sobie, chyba że dane akurat są wyjątkowe.
