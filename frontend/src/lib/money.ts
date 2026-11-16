// Reading and showing money as whole pennies (1000 means £10.00).
// Everything is done with whole numbers, so nothing is ever rounded.

export function parsePounds(text: string): number | null {
  const match = /^(\d+)(?:\.(\d{1,2}))?$/.exec(text.trim());
  if (match === null) {
    return null;
  }
  const pounds = Number(match[1]);
  const pence = Number((match[2] ?? "").padEnd(2, "0"));
  const total = pounds * 100 + pence;
  return Number.isSafeInteger(total) ? total : null;
}

export function formatPounds(pence: number): string {
  const pounds = Math.floor(pence / 100).toLocaleString("en-GB");
  return `£${pounds}.${String(pence % 100).padStart(2, "0")}`;
}
