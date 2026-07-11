"""
Uproszczony model bilansów sektorowych (Godley/SFC) do celów edukacyjnych.
Warstwa tożsamości księgowej jest zawsze prawdziwa. Warstwa mnożnikowa to
jawnie oznaczone założenie ilustracyjne, nie prognoza.

Port jeden do jednego z prototypu React (symulator_bilansow.jsx) — te same
stałe i te same wzory, żeby obie wersje dawały identyczne liczby.
"""

SZKOLY = {
    "neoklasyczna": 0.4,
    "glownego_nurtu": 0.9,
    "postkeynesowska": 1.6,
}

GDP_0 = 100.0
GOV_BALANCE_0 = -3.0   # % PKB, punkt startowy
DEBT_0 = 50.0          # % PKB
R0 = 4.0               # % efektywna stopa od długu
G0 = 4.0               # % bazowy wzrost nominalny PKB
TAX_ELASTICITY = 0.35  # frakcja wzrostu PKB odzyskiwana jako dochody podatkowe w roku 1


def symuluj(delta_g: float, delta_r: float, horyzont: int) -> dict:
    wynik = {}
    for szkola, mult in SZKOLY.items():
        gdp = GDP_0
        dlug = DEBT_0
        trajektoria = []
        for rok in range(1, horyzont + 1):
            wzrost = G0 + mult * delta_g if rok == 1 else G0
            gdp *= (1 + wzrost / 100)
            if rok == 1:
                pb = GOV_BALANCE_0 - delta_g + TAX_ELASTICITY * mult * delta_g
            else:
                pb = GOV_BALANCE_0 - delta_g
            dlug += -pb + ((R0 + delta_r - wzrost) / 100) * dlug
            trajektoria.append({"rok": rok, "pkb_indeks": round(gdp, 1), "dlug_pkb": round(dlug, 1)})
        wynik[szkola] = trajektoria
    return wynik


def tozsamosc_sektorowa(delta_g: float, cab: float) -> dict:
    """Saldo prywatne + publiczne + zagraniczne = 0. Zawsze prawdziwe, niezależnie od szkoły."""
    publiczny = GOV_BALANCE_0 - delta_g
    zagraniczny = -cab
    prywatny = -publiczny - zagraniczny
    return {
        "prywatny": round(prywatny, 1),
        "publiczny": round(publiczny, 1),
        "zagraniczny": round(zagraniczny, 1),
    }
