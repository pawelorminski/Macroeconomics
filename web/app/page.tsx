import Link from "next/link";

function Karta({
  href,
  tytul,
  opis,
}: {
  href: string;
  tytul: string;
  opis: string;
}) {
  return (
    <Link
      href={href}
      className="block rounded-[10px] border border-linia bg-karta p-5 transition-colors hover:border-akcent-zloty"
    >
      <div className="mb-1.5 font-semibold text-tekst">{tytul}</div>
      <div className="text-sm leading-relaxed text-tekst-stlumiony">{opis}</div>
    </Link>
  );
}

export default function Home() {
  return (
    <div className="mx-auto max-w-[980px] px-6 py-6">
      <div className="mb-1 text-[11px] tracking-[0.08em] text-tekst-faint uppercase">
        Projekt edukacyjny · nie jest doradztwem inwestycyjnym
      </div>
      <h1 className="mb-2 text-[25px] font-bold">Barometr Globalny</h1>
      <p className="mb-8 max-w-[640px] text-sm leading-relaxed text-tekst-stlumiony">
        Dane makroekonomiczne (Polska jako priorytet, G20, agregaty UE i Świat) i edukacyjny
        model bilansów sektorowych pokazujący, jak decyzje fiskalne i monetarne rozkładają się
        między sektor publiczny, prywatny i zagraniczny.
      </p>

      <div className="grid gap-4 sm:grid-cols-2">
        <Karta
          href="/symulator"
          tytul="Symulator bilansów sektorowych"
          opis="Suwaki dla wydatków rządowych, salda obrotów bieżących i stóp procentowych — z wykresami PKB i długu wg trzech szkół ekonomicznych."
        />
        <Karta
          href="/dane"
          tytul="Dane"
          opis="Ostatnie odczyty wskaźników makro z bazy fakty_makro, zasilanej przez codzienny ETL (NBP, GUS BDL, IMF, Eurostat)."
        />
      </div>
    </div>
  );
}
