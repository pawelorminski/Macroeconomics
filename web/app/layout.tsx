import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Barometr Globalny",
  description:
    "Dane makroekonomiczne (Polska, G20, UE, Świat) i edukacyjny symulator bilansów sektorowych.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pl" className="h-full antialiased">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
