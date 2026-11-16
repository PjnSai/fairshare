import { describe, expect, it } from "vitest";

import { formatPounds, parsePounds } from "./money";

describe("parsePounds", () => {
  it.each([
    ["20", 2000],
    ["20.5", 2050],
    ["20.50", 2050],
    ["0.07", 7],
    ["0", 0],
    ["  12.30 ", 1230],
  ])("reads %j as %d pence", (text, pence) => {
    expect(parsePounds(text)).toBe(pence);
  });

  it.each([
    "",
    "abc",
    "-5",
    "1.234",
    ".5",
    "5.",
    "1,000",
    "£5",
    "1e3",
    "1.2.3",
  ])("rejects %j", (text) => {
    expect(parsePounds(text)).toBeNull();
  });
});

describe("formatPounds", () => {
  it.each([
    [0, "£0.00"],
    [7, "£0.07"],
    [2050, "£20.50"],
    [100000, "£1,000.00"],
    [123456789, "£1,234,567.89"],
  ])("shows %d pence as %s", (pence, text) => {
    expect(formatPounds(pence)).toBe(text);
  });
});
