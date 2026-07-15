import type { Metadata } from "next";
import { pobierzKlientaSupabase } from "@/lib/supabase";

export const metadata: Metadata = {
  title: "Dane — Barometr Globalny",
};

type WierszFaktu = {
  kraj_kod: string;
  wskaznik_id: string;
  data: string;
  wartosc: number;
  zrodlo: string;
};

async function pobierzOstatnieFakty(): Promise<
  { stan: "brak_konfiguracji" } | { stan: "blad"; komunikat: string } | { stan: "ok"; wiersze: WierszFaktu[] }
> {
  const klient = pobierzKlientaSupabase();
  if (!klient) return { stan: "brak_konfiguracji" };

  const { data, error } = await klient
    .from("fakty_makro")
    .select("kraj_kod, wskaznik_id, data, wartosc, zrodlo")
    .order("data", { ascending: false })
    .limit(50);

  if (error) return { stan: "blad", komunikat: error.message };
  return { stan: "ok", wiersze: data ?? [] };
}

export default async function DanePage() {
  const wynik = await pobierzOstatnieFakty();

  return (
    <div className="mx-auto max-w-[980px] px-6 py-6">
      <div className="mb-1 text-[11px] tracking-[0.08em] text-tekst-faint uppercase">
        fakty_makro · ostatnie 50 wierszy
      </div>
      <h1 className="mb-6 text-[25px] font-bold">Dane</h1>

      {wynik.stan === "brak_konfiguracji" && (
        <div className="rounded-[10px] border border-linia bg-karta p-5 text-sm leading-relaxed text-tekst-stlumiony">
          Brak <code className="font-mono text-tekst">NEXT_PUBLIC_SUPABASE_URL</code> /{" "}
          <code className="font-mono text-tekst">NEXT_PUBLIC_SUPABASE_ANON_KEY</code> w środowisku —
          ta strona pokaże dane, gdy klucze publiczne (anon, nie service role) zostaną ustawione.
          Zobacz <code className="font-mono text-tekst">web/.env.example</code>.
        </div>
      )}

      {wynik.stan === "blad" && (
        <div className="rounded-[10px] border border-ujemny/40 bg-karta p-5 text-sm text-ujemny">
          Błąd zapytania do Supabase: {wynik.komunikat}
        </div>
      )}

      {wynik.stan === "ok" && wynik.wiersze.length === 0 && (
        <div className="rounded-[10px] border border-linia bg-karta p-5 text-sm leading-relaxed text-tekst-stlumiony">
          Połączenie z Supabase działa, ale tabela <code className="font-mono text-tekst">fakty_makro</code>{" "}
          jest jeszcze pusta — ETL (zob. <code className="font-mono text-tekst">etl/</code> w repo)
          jeszcze nie zapisał żadnego wiersza.
        </div>
      )}

      {wynik.stan === "ok" && wynik.wiersze.length > 0 && (
        <div className="overflow-x-auto rounded-[10px] border border-linia bg-karta">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-linia text-xs tracking-wide text-tekst-stlumiony uppercase">
                <th className="px-4 py-3 font-semibold">Kraj</th>
                <th className="px-4 py-3 font-semibold">Wskaźnik</th>
                <th className="px-4 py-3 font-semibold">Data</th>
                <th className="px-4 py-3 text-right font-semibold">Wartość</th>
                <th className="px-4 py-3 font-semibold">Źródło</th>
              </tr>
            </thead>
            <tbody>
              {wynik.wiersze.map((w) => (
                <tr key={`${w.kraj_kod}-${w.wskaznik_id}-${w.data}`} className="border-b border-linia last:border-0">
                  <td className="px-4 py-2.5 font-mono text-tekst-stlumiony">{w.kraj_kod}</td>
                  <td className="px-4 py-2.5">{w.wskaznik_id}</td>
                  <td className="px-4 py-2.5 font-mono text-tekst-stlumiony">{w.data}</td>
                  <td className="px-4 py-2.5 text-right font-mono">{w.wartosc}</td>
                  <td className="px-4 py-2.5 text-tekst-stlumiony">{w.zrodlo}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
