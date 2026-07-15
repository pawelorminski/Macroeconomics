import type { Metadata } from "next";
import Symulator from "@/components/Symulator";

export const metadata: Metadata = {
  title: "Symulator bilansów sektorowych — Barometr Globalny",
};

export default function SymulatorPage() {
  return <Symulator />;
}
