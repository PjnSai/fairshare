// Splitting a bill into whole pennies without losing or inventing any.
// This mirrors backend/splits/splitting.py, and both are tested against
// shared/test-vectors/splits.json.

export type Weight = number | string; // a whole number, or a fraction like "1/3"

export interface Person {
  fixed?: number;
  weight?: Weight;
}

export class InvalidSplitError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "InvalidSplitError";
  }
}

function mismatchMessage(total: number, amountsTotal: number): string {
  const difference = amountsTotal - total;
  const detail =
    difference > 0 ? `${difference}p too much` : `${-difference}p short`;
  return `amounts add up to ${amountsTotal}p but the bill is ${total}p (${detail})`;
}

export class AmountsDoNotMatchTotalError extends InvalidSplitError {
  readonly difference: number;

  constructor(total: number, amountsTotal: number) {
    super(mismatchMessage(total, amountsTotal));
    this.name = "AmountsDoNotMatchTotalError";
    this.difference = amountsTotal - total;
  }
}

// BigInt keeps the shares exact; ordinary numbers can round.
const ZERO = BigInt(0);
const ONE = BigInt(1);

function requirePence(value: number, label: string): void {
  if (!Number.isSafeInteger(value) || value < 0) {
    throw new InvalidSplitError(
      `${label} must be whole pennies and not negative`,
    );
  }
}

function gcd(a: bigint, b: bigint): bigint {
  let x = a;
  let y = b;
  while (y !== ZERO) {
    [x, y] = [y, x % y];
  }
  return x;
}

function parseWeight(weight: Weight): [bigint, bigint] {
  const problem = "weights must be whole numbers or fractions like '1/3'";
  if (typeof weight === "number") {
    if (!Number.isSafeInteger(weight)) {
      throw new InvalidSplitError(problem);
    }
    return [BigInt(weight), ONE];
  }
  const match = /^(-?\d+)(?:\/(\d+))?$/.exec(weight.trim());
  if (match === null) {
    throw new InvalidSplitError(problem);
  }
  const denominator = BigInt(match[2] ?? "1");
  if (denominator === ZERO) {
    throw new InvalidSplitError("a weight cannot have a zero denominator");
  }
  return [BigInt(match[1]), denominator];
}

// Rewrite every weight as a whole number over one shared denominator, so that
// 1/2, 1/4 and 1/4 become 2, 1 and 1. Shares and remainders are then whole numbers.
function toIntegerWeights(weights: Weight[]): bigint[] {
  const parsed = weights.map(parseWeight);
  if (parsed.some(([numerator]) => numerator < ZERO)) {
    throw new InvalidSplitError("weights cannot be negative");
  }
  let common = ONE;
  for (const [, denominator] of parsed) {
    common = (common / gcd(common, denominator)) * denominator;
  }
  return parsed.map(
    ([numerator, denominator]) => numerator * (common / denominator),
  );
}

// Everyone's share rounded down, each person's discarded remainder (all over the
// same denominator, so they compare as whole numbers), and the pennies left over.
function shareOut(total: number, weights: Weight[]) {
  requirePence(total, "total");
  if (weights.length === 0) {
    throw new InvalidSplitError("at least one weight is required");
  }
  const integerWeights = toIntegerWeights(weights);
  const weightTotal = integerWeights.reduce((sum, w) => sum + w, ZERO);
  if (weightTotal === ZERO) {
    throw new InvalidSplitError("weights cannot all be zero");
  }

  const scaled = integerWeights.map((w) => BigInt(total) * w);
  const parts = scaled.map((s) => s / weightTotal);
  const remainders = scaled.map((s) => s % weightTotal);
  const leftover = Number(
    BigInt(total) - parts.reduce((sum, p) => sum + p, ZERO),
  );
  return { parts, remainders, leftover };
}

export function splitEqually(total: number, count: number): number[] {
  requirePence(total, "total");
  if (!Number.isSafeInteger(count) || count < 1) {
    throw new InvalidSplitError("count must be at least 1");
  }
  const base = Number(BigInt(total) / BigInt(count));
  const leftover = Number(BigInt(total) % BigInt(count));
  return Array.from({ length: count }, (_, i) => base + (i < leftover ? 1 : 0));
}

export function splitByWeights(total: number, weights: Weight[]): number[] {
  const { parts, remainders, leftover } = shareOut(total, weights);
  const result = parts.map((p) => Number(p));
  const byLargestRemainder = parts
    .map((_, index) => index)
    .sort((a, b) => {
      if (remainders[a] === remainders[b]) {
        return a - b; // a tie goes to the earlier person
      }
      return remainders[a] > remainders[b] ? -1 : 1;
    });
  for (const index of byLargestRemainder.slice(0, leftover)) {
    result[index] += 1;
  }
  return result;
}

export function splitWithLeftover(
  total: number,
  weights: Weight[],
): { shares: number[]; leftover: number } {
  const { parts, leftover } = shareOut(total, weights);
  return { shares: parts.map((p) => Number(p)), leftover };
}

export function splitExact(total: number, amounts: number[]): number[] {
  requirePence(total, "total");
  if (amounts.length === 0) {
    throw new InvalidSplitError("at least one amount is required");
  }
  for (const amount of amounts) {
    requirePence(amount, "amounts");
  }
  const amountsTotal = amounts.reduce((sum, a) => sum + a, 0);
  if (amountsTotal !== total) {
    throw new AmountsDoNotMatchTotalError(total, amountsTotal);
  }
  return [...amounts];
}

function takeOutFixed(total: number, people: Person[]) {
  requirePence(total, "total");
  if (people.length === 0) {
    throw new InvalidSplitError("at least one person is required");
  }
  const fixed = people.map((person) => person.fixed ?? 0);
  for (const amount of fixed) {
    requirePence(amount, "fixed amounts");
  }
  const weights = people.map((person) => person.weight ?? 1);
  const integerWeights = toIntegerWeights(weights);

  const fixedTotal = fixed.reduce((sum, a) => sum + a, 0);
  if (fixedTotal > total) {
    throw new AmountsDoNotMatchTotalError(total, fixedTotal);
  }
  const remainder = total - fixedTotal;
  if (remainder > 0 && integerWeights.every((w) => w === ZERO)) {
    throw new AmountsDoNotMatchTotalError(total, fixedTotal);
  }
  return { fixed, remainder, weights };
}

export function splitBill(total: number, people: Person[]): number[] {
  const { fixed, remainder, weights } = takeOutFixed(total, people);
  if (remainder === 0) {
    return fixed;
  }
  const shares = splitByWeights(remainder, weights);
  return fixed.map((amount, i) => amount + shares[i]);
}

export function splitBillWithLeftover(
  total: number,
  people: Person[],
): { amounts: number[]; leftover: number } {
  const { fixed, remainder, weights } = takeOutFixed(total, people);
  if (remainder === 0) {
    return { amounts: fixed, leftover: 0 };
  }
  const { shares, leftover } = splitWithLeftover(remainder, weights);
  return { amounts: fixed.map((amount, i) => amount + shares[i]), leftover };
}
