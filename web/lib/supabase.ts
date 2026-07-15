import { createClient } from "@supabase/supabase-js";

/**
 * Klient przeglądarkowy — używa klucza anon/public (NEXT_PUBLIC_*), NIE klucza
 * service role, który ETL (etl/wspolne.py) trzyma po stronie serwera jako
 * SUPABASE_KEY. Mylenie tych dwóch kluczy wystawiłoby pełny dostęp zapisu do
 * bazy w kodzie klienckim.
 */
export function pobierzKlientaSupabase() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if (!url || !anonKey) return null;
  return createClient(url, anonKey);
}
