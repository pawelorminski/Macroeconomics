import React, { useState, useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const KOLORY = {
  tlo: '#0F1B2A',
  karta: '#16273B',
  pole: '#1C3149',
  linia: '#2A3B52',
  tekst: '#EDEEE9',
  tekstStlumiony: '#8B98AA',
  tekstFaint: '#5D6B80',
  ujemny: '#C4694A',
  dodatni: '#4FB8A6',
  akcentZloty: '#C9A24B',
};

const SZKOLY = [
  { key: 'neoklasyczna', label: 'Neoklasyczna', mult: 0.4, kolor: '#8FA3BD' },
  { key: 'glownego_nurtu', label: 'Głównego nurtu', mult: 0.9, kolor: '#C9A24B' },
  { key: 'postkeynesowska', label: 'Postkeynesowska / MMT', mult: 1.6, kolor: '#4FB8A6' },
];

const GDP_0 = 100;
const GOV_BALANCE_0 = -3;
const DEBT_0 = 50;
const R0 = 4;
const G0 = 4;
const TAX_ELASTICITY = 0.35;

function symuluj(deltaG, deltaR, horyzont) {
  const wynik = {};
  SZKOLY.forEach(({ key, mult }) => {
    let gdp = GDP_0;
    let dlug = DEBT_0;
    const traj = [];
    for (let rok = 1; rok <= horyzont; rok++) {
      const wzrost = rok === 1 ? G0 + mult * deltaG : G0;
      gdp = gdp * (1 + wzrost / 100);
      const pb = rok === 1
        ? GOV_BALANCE_0 - deltaG + TAX_ELASTICITY * mult * deltaG
        : GOV_BALANCE_0 - deltaG;
      dlug = dlug + (-pb) + ((R0 + deltaR - wzrost) / 100) * dlug;
      traj.push({ rok, pkb: gdp, dlug: dlug });
    }
    wynik[key] = traj;
  });
  return wynik;
}

function scal(wynik, pole) {
  return wynik.neoklasyczna.map((_, i) => ({
    rok: wynik.neoklasyczna[i].rok,
    neoklasyczna: Number(wynik.neoklasyczna[i][pole].toFixed(1)),
    glownego_nurtu: Number(wynik.glownego_nurtu[i][pole].toFixed(1)),
    postkeynesowska: Number(wynik.postkeynesowska[i][pole].toFixed(1)),
  }));
}

function tozsamosc(deltaG, cab) {
  const publiczny = GOV_BALANCE_0 - deltaG;
  const zagraniczny = -cab;
  const prywatny = -publiczny - zagraniczny;
  return { prywatny, publiczny, zagraniczny };
}

function PasekSalda({ etykieta, wartosc, maxAbs }) {
  const dodatni = wartosc >= 0;
  const szerokosc = Math.min(50, (Math.abs(wartosc) / maxAbs) * 50);
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '7px 0' }}>
      <div style={{ width: '108px', color: KOLORY.tekstStlumiony, fontSize: '13px', flexShrink: 0 }}>{etykieta}</div>
      <div style={{ position: 'relative', flex: 1, height: '20px', background: KOLORY.pole, borderRadius: '3px', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', left: '50%', top: 0, bottom: 0, width: '1px', background: KOLORY.tekstFaint }} />
        <div
          style={{
            position: 'absolute',
            top: '2px',
            bottom: '2px',
            width: `${szerokosc}%`,
            background: dodatni ? KOLORY.dodatni : KOLORY.ujemny,
            borderRadius: '2px',
            left: dodatni ? '50%' : undefined,
            right: dodatni ? undefined : '50%',
          }}
        />
      </div>
      <div style={{ width: '64px', textAlign: 'right', fontFamily: "'IBM Plex Mono', monospace", fontSize: '13px', color: dodatni ? KOLORY.dodatni : KOLORY.ujemny, flexShrink: 0 }}>
        {dodatni ? '+' : ''}{wartosc.toFixed(1)}%
      </div>
    </div>
  );
}

function Suwak({ etykieta, wartosc, min, max, krok, jednostka, onChange }) {
  return (
    <div style={{ marginBottom: '18px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '6px' }}>
        <label style={{ color: KOLORY.tekstStlumiony, fontSize: '13px' }}>{etykieta}</label>
        <span style={{ fontFamily: "'IBM Plex Mono', monospace", color: KOLORY.tekst, fontSize: '14px' }}>
          {wartosc > 0 ? '+' : ''}{wartosc}{jednostka}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={krok}
        value={wartosc}
        onChange={(e) => onChange(Number(e.target.value))}
        style={{ width: '100%', display: 'block' }}
      />
    </div>
  );
}

export default function SymulatorBilansow() {
  const [deltaG, setDeltaG] = useState(2);
  const [deltaR, setDeltaR] = useState(0);
  const [cab, setCab] = useState(-1);
  const [horyzont, setHoryzont] = useState(8);

  const wynik = useMemo(() => symuluj(deltaG, deltaR, horyzont), [deltaG, deltaR, horyzont]);
  const danePkb = useMemo(() => scal(wynik, 'pkb'), [wynik]);
  const daneDlug = useMemo(() => scal(wynik, 'dlug'), [wynik]);
  const salda = useMemo(() => tozsamosc(deltaG, cab), [deltaG, cab]);
  const maxAbs = Math.max(10, Math.abs(salda.prywatny), Math.abs(salda.publiczny), Math.abs(salda.zagraniczny));

  return (
    <div style={{ background: KOLORY.tlo, minHeight: '100%', padding: '24px', fontFamily: "'IBM Plex Sans', -apple-system, sans-serif", color: KOLORY.tekst }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
        input[type=range] { -webkit-appearance: none; height: 4px; border-radius: 2px; background: ${KOLORY.pole}; }
        input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; width: 14px; height: 14px; border-radius: 50%; background: ${KOLORY.akcentZloty}; cursor: pointer; border: 2px solid ${KOLORY.tlo}; }
        input[type=range]::-moz-range-thumb { width: 14px; height: 14px; border-radius: 50%; background: ${KOLORY.akcentZloty}; cursor: pointer; border: 2px solid ${KOLORY.tlo}; }
      `}</style>

      <div style={{ maxWidth: '980px', margin: '0 auto' }}>
        <div style={{ marginBottom: '4px', fontSize: '11px', letterSpacing: '0.08em', color: KOLORY.tekstFaint, textTransform: 'uppercase' }}>
          Symulator edukacyjny · nie jest prognozą
        </div>
        <h1 style={{ fontSize: '25px', fontWeight: 700, margin: '0 0 8px 0' }}>Symulator bilansów sektorowych</h1>
        <p style={{ color: KOLORY.tekstStlumiony, fontSize: '14px', maxWidth: '640px', margin: '0 0 26px 0', lineHeight: 1.6 }}>
          Przesuń suwaki, żeby zobaczyć, jak decyzja fiskalna i monetarna rozkłada się między sektor publiczny, prywatny i zagraniczny, oraz jak różne szkoły ekonomiczne przewidują inny wpływ tej samej decyzji na PKB i dług.
        </p>

        <div style={{ background: KOLORY.karta, borderRadius: '10px', padding: '20px 20px 16px', marginBottom: '20px', border: `1px solid ${KOLORY.linia}` }}>
          <div style={{ fontSize: '12px', fontWeight: 600, color: KOLORY.tekstStlumiony, marginBottom: '12px', letterSpacing: '0.03em' }}>
            TOŻSAMOŚĆ KSIĘGOWA — ZAWSZE PRAWDZIWA, NIEZALEŻNIE OD ZAŁOŻEŃ
          </div>
          <PasekSalda etykieta="Sektor prywatny" wartosc={salda.prywatny} maxAbs={maxAbs} />
          <PasekSalda etykieta="Sektor publiczny" wartosc={salda.publiczny} maxAbs={maxAbs} />
          <PasekSalda etykieta="Sektor zagraniczny" wartosc={salda.zagraniczny} maxAbs={maxAbs} />
          <div style={{ marginTop: '10px', paddingTop: '10px', borderTop: `1px solid ${KOLORY.linia}`, fontSize: '12px', color: KOLORY.tekstFaint, fontFamily: "'IBM Plex Mono', monospace" }}>
            {salda.prywatny.toFixed(1)}% + {salda.publiczny.toFixed(1)}% + {salda.zagraniczny.toFixed(1)}% = 0.0% PKB
          </div>
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px' }}>
          <div style={{ flex: '0 0 260px', background: KOLORY.karta, borderRadius: '10px', padding: '20px', border: `1px solid ${KOLORY.linia}`, height: 'fit-content' }}>
            <div style={{ fontSize: '12px', fontWeight: 600, color: KOLORY.tekstStlumiony, marginBottom: '16px', letterSpacing: '0.03em' }}>DŹWIGNIE POLITYKI</div>
            <Suwak etykieta="Zmiana wydatków rządowych" wartosc={deltaG} min={-5} max={5} krok={0.5} jednostka="% PKB" onChange={setDeltaG} />
            <Suwak etykieta="Saldo obrotów bieżących" wartosc={cab} min={-6} max={4} krok={0.5} jednostka="% PKB" onChange={setCab} />
            <Suwak etykieta="Zmiana stóp procentowych" wartosc={deltaR} min={-3} max={3} krok={0.25} jednostka="pp" onChange={setDeltaR} />
            <Suwak etykieta="Horyzont symulacji" wartosc={horyzont} min={3} max={10} krok={1} jednostka=" lat" onChange={setHoryzont} />
            <div style={{ marginTop: '14px', paddingTop: '14px', borderTop: `1px solid ${KOLORY.linia}`, fontSize: '11.5px', color: KOLORY.tekstFaint, lineHeight: 1.6 }}>
              Punkt startowy: saldo budżetu {GOV_BALANCE_0}% PKB, dług {DEBT_0}% PKB, stopa {R0}%, wzrost bazowy {G0}%.
            </div>
          </div>

          <div style={{ flex: '1 1 420px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ background: KOLORY.karta, borderRadius: '10px', padding: '18px', border: `1px solid ${KOLORY.linia}` }}>
              <div style={{ fontSize: '12px', fontWeight: 600, color: KOLORY.tekstStlumiony, marginBottom: '8px', letterSpacing: '0.03em' }}>PKB — INDEKS (DZIŚ = 100)</div>
              <ResponsiveContainer width="100%" height={180}>
                <LineChart data={danePkb} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={KOLORY.linia} />
                  <XAxis dataKey="rok" tick={{ fill: KOLORY.tekstFaint, fontSize: 11 }} />
                  <YAxis tick={{ fill: KOLORY.tekstFaint, fontSize: 11 }} domain={['auto', 'auto']} />
                  <Tooltip contentStyle={{ background: KOLORY.pole, border: `1px solid ${KOLORY.linia}`, borderRadius: '6px', fontSize: '12px' }} labelStyle={{ color: KOLORY.tekst }} />
                  <Legend wrapperStyle={{ fontSize: '11px' }} formatter={(v) => (SZKOLY.find(s => s.key === v) || {}).label || v} />
                  {SZKOLY.map(s => (
                    <Line key={s.key} type="monotone" dataKey={s.key} name={s.key} stroke={s.kolor} strokeWidth={2} dot={false} />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div style={{ background: KOLORY.karta, borderRadius: '10px', padding: '18px', border: `1px solid ${KOLORY.linia}` }}>
              <div style={{ fontSize: '12px', fontWeight: 600, color: KOLORY.tekstStlumiony, marginBottom: '8px', letterSpacing: '0.03em' }}>DŁUG PUBLICZNY (% PKB)</div>
              <ResponsiveContainer width="100%" height={180}>
                <LineChart data={daneDlug} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={KOLORY.linia} />
                  <XAxis dataKey="rok" tick={{ fill: KOLORY.tekstFaint, fontSize: 11 }} />
                  <YAxis tick={{ fill: KOLORY.tekstFaint, fontSize: 11 }} domain={['auto', 'auto']} />
                  <Tooltip contentStyle={{ background: KOLORY.pole, border: `1px solid ${KOLORY.linia}`, borderRadius: '6px', fontSize: '12px' }} labelStyle={{ color: KOLORY.tekst }} />
                  <Legend wrapperStyle={{ fontSize: '11px' }} formatter={(v) => (SZKOLY.find(s => s.key === v) || {}).label || v} />
                  {SZKOLY.map(s => (
                    <Line key={s.key} type="monotone" dataKey={s.key} name={s.key} stroke={s.kolor} strokeWidth={2} dot={false} />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        <div style={{ marginTop: '20px', padding: '14px 16px', background: KOLORY.pole, borderRadius: '8px', fontSize: '13px', color: KOLORY.tekstStlumiony, lineHeight: 1.65 }}>
          Sektor publiczny: {salda.publiczny.toFixed(1)}% PKB. Sektor zagraniczny: {salda.zagraniczny.toFixed(1)}% PKB. Z tożsamości księgowej wynika, że sektor prywatny musi zbilansować się na poziomie {salda.prywatny.toFixed(1)}% PKB, niezależnie od tego, jak ta liczba jest oceniana. Trzy linie na wykresach obok nie są trzema prognozami do wyboru, tylko pokazaniem, że sama skala efektu na PKB i dług zależy od przyjętego założenia o mnożniku fiskalnym, nie tylko od samej decyzji politycznej.
        </div>

        <div style={{ marginTop: '14px', fontSize: '11px', color: KOLORY.tekstFaint, lineHeight: 1.6 }}>
          Model uproszczony do celów edukacyjnych. Tożsamość sektorowa jest rachunkowo prawdziwa zawsze. Trajektorie PKB i długu zależą od przyjętych parametrów (mnożnik, elastyczność podatkowa, dynamika r−g) i nie są prognozą rynkową.
        </div>
      </div>
    </div>
  );
}
