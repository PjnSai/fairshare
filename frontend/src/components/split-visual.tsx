import { formatPounds } from "@/lib/money";
import { splitByWeights } from "@/lib/splits/splitting";

export interface SplitRow {
  id: string;
  name: string;
  pence: number;
}

// Tailwind only picks up whole class names, so the palette is written out in full.
const COLOURS = [
  "bg-sky-500",
  "bg-amber-500",
  "bg-emerald-500",
  "bg-rose-500",
  "bg-violet-500",
  "bg-orange-500",
  "bg-teal-500",
  "bg-fuchsia-500",
];

function colourFor(index: number): string {
  return COLOURS[index % COLOURS.length];
}

function percentage(pence: number, total: number): string {
  return `${(Math.round((pence * 1000) / total) / 10).toFixed(1)}%`;
}

export function SplitVisual({ rows }: { rows: SplitRow[] }) {
  const total = rows.reduce((sum, row) => sum + row.pence, 0);
  if (rows.length === 0 || total === 0) {
    return (
      <p className="text-zinc-600 dark:text-zinc-400">
        Enter a bill to see the split.
      </p>
    );
  }

  // 100 squares, each worth 1% of the bill, shared out with the same rounding
  // rule as the money itself.
  const squares = splitByWeights(
    100,
    rows.map((row) => row.pence),
  );
  const cells = squares.flatMap((count, personIndex) =>
    Array.from({ length: count }, () => personIndex),
  );

  return (
    <div className="flex flex-col gap-6 sm:flex-row sm:items-start">
      <div
        role="img"
        aria-label="A grid of 100 squares showing each person's share of the bill. The table gives the exact amounts."
        className="grid w-full max-w-xs shrink-0 grid-cols-10 gap-1"
      >
        {cells.map((personIndex, i) => (
          <div
            key={i}
            className={`aspect-square rounded-sm ${colourFor(personIndex)}`}
          />
        ))}
      </div>

      <table className="w-full text-left text-sm">
        <caption className="sr-only">Amount each person owes</caption>
        <thead>
          <tr className="border-b border-zinc-300 dark:border-zinc-700">
            <th scope="col" className="py-2 pr-4 font-medium">
              Person
            </th>
            <th scope="col" className="py-2 pr-4 text-right font-medium">
              Owes
            </th>
            <th scope="col" className="py-2 text-right font-medium">
              Share
            </th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr
              key={row.id}
              className="border-b border-zinc-200 dark:border-zinc-800"
            >
              <th scope="row" className="py-2 pr-4 font-normal">
                <span className="flex items-center gap-2">
                  <span
                    aria-hidden="true"
                    className={`inline-block size-3 rounded-sm ${colourFor(i)}`}
                  />
                  {row.name}
                </span>
              </th>
              <td className="py-2 pr-4 text-right tabular-nums">
                {formatPounds(row.pence)}
              </td>
              <td className="py-2 text-right tabular-nums">
                {percentage(row.pence, total)}
              </td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <th scope="row" className="py-2 pr-4 font-medium">
              Total
            </th>
            <td className="py-2 pr-4 text-right font-medium tabular-nums">
              {formatPounds(total)}
            </td>
            <td />
          </tr>
        </tfoot>
      </table>
    </div>
  );
}
