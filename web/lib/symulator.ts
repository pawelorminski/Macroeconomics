/**
 * Uproszczony model bilansów sektorowych (Godley/SFC) do celów edukacyjnych.
 * Port 1:1 z models/symulator_sfc.py — te same stałe i wzory, żeby obie
 * wersje dawały identyczne liczby.
 */

export const SZKOLY = [
  { key: "neoklasyczna", label: "Neoklasyczna", mult: 0.4, kolor: "#8FA3BD" },
  { key: "glownego_nurtu", label: "Głównego nurtu", mult: 0.9, kolor: "#C9A24B" },
  { key: "postkeynesowska", label: "Postkeynesowska / MMT", mult: 1.6, kolor: "#4FB8A6" },
] as const;

export const GDP_0 = 100;
export const GOV_BALANCE_0 = -3;
export const DEBT_0 = 50;
export const R0 = 4;
export const G0 = 4;
export const TAX_ELASTICITY = 0.35;

export type PunktTrajektorii = { rok: number; pkb: number; dlug: number };

export function symuluj(
  deltaG: number,
  deltaR: number,
  horyzont: number,
): Record<string, PunktTrajektorii[]> {
  const wynik: Record<string, PunktTrajektorii[]> = {};
  for (const { key, mult } of SZKOLY) {
    let gdp = GDP_0;
    let dlug = DEBT_0;
    const traj: PunktTrajektorii[] = [];
    for (let rok = 1; rok <= horyzont; rok++) {
      const wzrost = rok === 1 ? G0 + mult * deltaG : G0;
      gdp = gdp * (1 + wzrost / 100);
      const pb =
        rok === 1
          ? GOV_BALANCE_0 - deltaG + TAX_ELASTICITY * mult * deltaG
          : GOV_BALANCE_0 - deltaG;
      dlug = dlug + -pb + ((R0 + deltaR - wzrost) / 100) * dlug;
      traj.push({ rok, pkb: gdp, dlug });
    }
    wynik[key] = traj;
  }
  return wynik;
}

export function scal(
  wynik: Record<string, PunktTrajektorii[]>,
  pole: "pkb" | "dlug",
) {
  return wynik.neoklasyczna.map((_, i) => ({
    rok: wynik.neoklasyczna[i].rok,
    neoklasyczna: Number(wynik.neoklasyczna[i][pole].toFixed(1)),
    glownego_nurtu: Number(wynik.glownego_nurtu[i][pole].toFixed(1)),
    postkeynesowska: Number(wynik.postkeynesowska[i][pole].toFixed(1)),
  }));
}

export type Salda = { prywatny: number; publiczny: number; zagraniczny: number };

export function tozsamosc(deltaG: number, cab: number): Salda {
  const publiczny = GOV_BALANCE_0 - deltaG;
  const zagraniczny = -cab;
  const prywatny = -publiczny - zagraniczny;
  return { prywatny, publiczny, zagraniczny };
}
