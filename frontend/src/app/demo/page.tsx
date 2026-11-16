import type { Metadata } from "next";

import { SplitVisual } from "@/components/split-visual";
import { splitEqually } from "@/lib/splits/splitting";

export const metadata: Metadata = { title: "Demo | FairShare" };

export default function DemoPage() {
  const names = ["Alex", "Sam", "Jo", "Priya"];
  const amounts = splitEqually(2000, names.length);
  const rows = names.map((name, i) => ({ id: name, name, pence: amounts[i] }));

  return (
    <main className="mx-auto max-w-3xl p-6">
      <h1 className="mb-6 text-2xl font-semibold">Try FairShare</h1>
      <SplitVisual rows={rows} />
    </main>
  );
}
