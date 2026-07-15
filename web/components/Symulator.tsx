"use client";

import { useMemo, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  DEBT_0,
  G0,
  GOV_BALANCE_0,
  R0,
  SZKOLY,
  Salda,
  scal,
  symuluj,
  tozsamosc,
} from "@/lib/symulator";

function nazwaSzkoly(key: string) {
  return SZKOLY.find((s) => s.key === key)?.label ?? key;
}

function PasekSalda({
  etykieta,
  wartosc,
  maxAbs,
}: {
  etykieta: string;
  wartosc: number;
  maxAbs: number;
}) {
  const dodatni = wartosc >= 0;
  const szerokosc = Math.min(50, (Math.abs(wartosc) / maxAbs) * 50);
  return (
    <div className="flex items-center gap-3 py-[7px]">
      <div className="w-[108px] shrink-0 text-[13px] text-tekst-stlumiony">{etykieta}</div>
      <div className="relative h-5 flex-1 overflow-hidden rounded-[3px] bg-pole">
        <div className="absolute inset-y-0 left-1/2 w-px bg-tekst-faint" />
        <div
          className="absolute top-[2px] bottom-[2px] rounded-[2px]"
          style={{
            width: `${szerokosc}%`,
            background: dodatni ? "var(--dodatni)" : "var(--ujemny)",
            left: dodatni ? "50%" : undefined,
            right: dodatni ? undefined : "50%",
          }}
        />
      </div>
      <div
        className="w-16 shrink-0 text-right font-mono text-[13px]"
        style={{ color: dodatni ? "var(--dodatni)" : "var(--ujemny)" }}
      >
        {dodatni ? "+" : ""}
        {wartosc.toFixed(1)}%
      </div>
    </div>
  );
}

function Suwak({
  etykieta,
  wartosc,
  min,
  max,
  krok,
  jednostka,
  onChange,
}: {
  etykieta: string;
  wartosc: number;
  min: number;
  max: number;
  krok: number;
  jednostka: string;
  onChange: (v: number) => void;
}) {
  return (
    <div className="mb-[18px]">
      <div className="mb-1.5 flex items-baseline justify-between">
        <label className="text-[13px] text-tekst-stlumiony">{etykieta}</label>
        <span className="font-mono text-sm text-tekst">
          {wartosc > 0 ? "+" : ""}
          {wartosc}
          {jednostka}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={krok}
        value={wartosc}
        onChange={(e) => onChange(Number(e.target.value))}
        className="block w-full"
      />
    </div>
  );
}

function WykresLinii({
  dane,
  tytul,
}: {
  dane: ReturnType<typeof scal>;
  tytul: string;
}) {
  return (
    <div className="rounded-[10px] border border-linia bg-karta p-[18px]">
      <div className="mb-2 text-xs font-semibold tracking-wide text-tekst-stlumiony">{tytul}</div>
      <ResponsiveContainer width="100%" height={180}>
        <LineChart data={dane} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2A3B52" />
          <XAxis dataKey="rok" tick={{ fill: "#5D6B80", fontSize: 11 }} />
          <YAxis tick={{ fill: "#5D6B80", fontSize: 11 }} domain={["auto", "auto"]} />
          <Tooltip
            contentStyle={{ background: "#1C3149", border: "1px solid #2A3B52", borderRadius: 6, fontSize: 12 }}
            labelStyle={{ color: "#EDEEE9" }}
          />
          <Legend wrapperStyle={{ fontSize: 11 }} formatter={(v) => nazwaSzkoly(String(v))} />
          {SZKOLY.map((s) => (
            <Line key={s.key} type="monotone" dataKey={s.key} name={s.key} stroke={s.kolor} strokeWidth={2} dot={false} />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function Symulator() {
  const [deltaG, setDeltaG] = useState(2);
  const [deltaR, setDeltaR] = useState(0);
  const [cab, setCab] = useState(-1);
  const [horyzont, setHoryzont] = useState(8);

  const wynik = useMemo(() => symuluj(deltaG, deltaR, horyzont), [deltaG, deltaR, horyzont]);
  const danePkb = useMemo(() => scal(wynik, "pkb"), [wynik]);
  const daneDlug = useMemo(() => scal(wynik, "dlug"), [wynik]);
  const salda: Salda = useMemo(() => tozsamosc(deltaG, cab), [deltaG, cab]);
  const maxAbs = Math.max(10, Math.abs(salda.prywatny), Math.abs(salda.publiczny), Math.abs(salda.zagraniczny));

  return (
    <div className="mx-auto max-w-[980px] px-6 py-6">
      <div className="mb-1 text-[11px] tracking-[0.08em] text-tekst-faint uppercase">
        Symulator edukacyjny · nie jest prognozą
      </div>
      <h1 className="mb-2 text-[25px] font-bold">Symulator bilansów sektorowych</h1>
      <p className="mb-6 max-w-[640px] text-sm leading-relaxed text-tekst-stlumiony">
        Przesuń suwaki, żeby zobaczyć, jak decyzja fiskalna i monetarna rozkłada się między
        sektor publiczny, prywatny i zagraniczny, oraz jak różne szkoły ekonomiczne przewidują
        inny wpływ tej samej decyzji na PKB i dług.
      </p>

      <div className="mb-5 rounded-[10px] border border-linia bg-karta px-5 pt-5 pb-4">
        <div className="mb-3 text-xs font-semibold tracking-wide text-tekst-stlumiony">
          TOŻSAMOŚĆ KSIĘGOWA — ZAWSZE PRAWDZIWA, NIEZALEŻNIE OD ZAŁOŻEŃ
        </div>
        <PasekSalda etykieta="Sektor prywatny" wartosc={salda.prywatny} maxAbs={maxAbs} />
        <PasekSalda etykieta="Sektor publiczny" wartosc={salda.publiczny} maxAbs={maxAbs} />
        <PasekSalda etykieta="Sektor zagraniczny" wartosc={salda.zagraniczny} maxAbs={maxAbs} />
        <div className="mt-2.5 border-t border-linia pt-2.5 font-mono text-xs text-tekst-faint">
          {salda.prywatny.toFixed(1)}% + {salda.publiczny.toFixed(1)}% + {salda.zagraniczny.toFixed(1)}% = 0.0% PKB
        </div>
      </div>

      <div className="flex flex-wrap gap-5">
        <div className="h-fit w-full shrink-0 rounded-[10px] border border-linia bg-karta p-5 sm:w-[260px]">
          <div className="mb-4 text-xs font-semibold tracking-wide text-tekst-stlumiony">DŹWIGNIE POLITYKI</div>
          <Suwak etykieta="Zmiana wydatków rządowych" wartosc={deltaG} min={-5} max={5} krok={0.5} jednostka="% PKB" onChange={setDeltaG} />
          <Suwak etykieta="Saldo obrotów bieżących" wartosc={cab} min={-6} max={4} krok={0.5} jednostka="% PKB" onChange={setCab} />
          <Suwak etykieta="Zmiana stóp procentowych" wartosc={deltaR} min={-3} max={3} krok={0.25} jednostka="pp" onChange={setDeltaR} />
          <Suwak etykieta="Horyzont symulacji" wartosc={horyzont} min={3} max={10} krok={1} jednostka=" lat" onChange={setHoryzont} />
          <div className="mt-3.5 border-t border-linia pt-3.5 text-[11.5px] leading-relaxed text-tekst-faint">
            Punkt startowy: saldo budżetu {GOV_BALANCE_0}% PKB, dług {DEBT_0}% PKB, stopa {R0}%,
            wzrost bazowy {G0}%.
          </div>
        </div>

        <div className="flex flex-1 flex-col gap-4" style={{ minWidth: 320 }}>
          <WykresLinii dane={danePkb} tytul="PKB — INDEKS (DZIŚ = 100)" />
          <WykresLinii dane={daneDlug} tytul="DŁUG PUBLICZNY (% PKB)" />
        </div>
      </div>

      <div className="mt-5 rounded-lg bg-pole px-4 py-3.5 text-[13px] leading-relaxed text-tekst-stlumiony">
        Sektor publiczny: {salda.publiczny.toFixed(1)}% PKB. Sektor zagraniczny:{" "}
        {salda.zagraniczny.toFixed(1)}% PKB. Z tożsamości księgowej wynika, że sektor prywatny
        musi zbilansować się na poziomie {salda.prywatny.toFixed(1)}% PKB, niezależnie od tego,
        jak ta liczba jest oceniana. Trzy linie na wykresach obok nie są trzema prognozami do
        wyboru, tylko pokazaniem, że sama skala efektu na PKB i dług zależy od przyjętego
        założenia o mnożniku fiskalnym, nie tylko od samej decyzji politycznej.
      </div>

      <div className="mt-3.5 text-[11px] leading-relaxed text-tekst-faint">
        Model uproszczony do celów edukacyjnych. Tożsamość sektorowa jest rachunkowo prawdziwa
        zawsze. Trajektorie PKB i długu zależą od przyjętych parametrów (mnożnik, elastyczność
        podatkowa, dynamika r−g) i nie są prognozą rynkową.
      </div>
    </div>
  );
}
