import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import {
  AmountsDoNotMatchTotalError,
  InvalidSplitError,
  splitBill,
  splitBillWithLeftover,
  splitByWeights,
  splitEqually,
  splitExact,
  type Person,
  type Weight,
} from "./splitting";

interface Case {
  name: string;
  function: string;
  input: {
    total: number;
    count?: number;
    weights?: Weight[];
    amounts?: number[];
    people?: Person[];
  };
  expected?: unknown;
  error?: "mismatch" | "invalid";
  difference?: number;
}

// The same file the Python tests read, found from this file's location.
const vectorsUrl = new URL(
  "../../../../shared/test-vectors/splits.json",
  import.meta.url,
);
const { cases } = JSON.parse(readFileSync(vectorsUrl, "utf-8")) as {
  cases: Case[];
};

function need<T>(value: T | undefined): T {
  if (value === undefined) {
    throw new Error("a test vector is missing a field");
  }
  return value;
}

function run(testCase: Case): unknown {
  const { total, count, weights, amounts, people } = testCase.input;
  switch (testCase.function) {
    case "split_equally":
      return splitEqually(total, need(count));
    case "split_by_weights":
      return splitByWeights(total, need(weights));
    case "split_exact":
      return splitExact(total, need(amounts));
    case "split_bill":
      return splitBill(total, need(people));
    case "split_bill_with_leftover":
      return splitBillWithLeftover(total, need(people));
    default:
      throw new Error(
        `unknown function in the test vectors: ${testCase.function}`,
      );
  }
}

describe("shared split test vectors", () => {
  it.each(cases)("$name", (testCase) => {
    if (testCase.error === undefined) {
      expect(run(testCase)).toEqual(testCase.expected);
      return;
    }

    let caught: unknown;
    try {
      run(testCase);
    } catch (error) {
      caught = error;
    }
    expect(caught).toBeInstanceOf(InvalidSplitError);
    if (testCase.error === "mismatch") {
      expect(caught).toBeInstanceOf(AmountsDoNotMatchTotalError);
      expect((caught as AmountsDoNotMatchTotalError).difference).toBe(
        testCase.difference,
      );
    } else {
      expect(caught).not.toBeInstanceOf(AmountsDoNotMatchTotalError);
    }
  });
});
