import { describe, expect, test } from "vitest";
import {
  convertOutput,
  convertWindspeed,
  getWindResource,
  percentToFactor,
  applyLoss,
  roundToSignificantDigits,
} from ".";

describe("getWindResource", () => {
  test("with high wind speed", () => {
    expect(getWindResource(6)).toBe("High");
  });
  test("with moderate wind speed", () => {
    expect(getWindResource(4)).toBe("Moderate");
  });
  test("with low wind speed", () => {
    expect(getWindResource(2)).toBe("Low");
  });
});

describe("convertWindspeed", () => {
  test("converts to mph", () => {
    expect(convertWindspeed(10, "mph")).toBe("22.4 mph");
  });
  test("converts to m/s", () => {
    expect(convertWindspeed(10, "m/s")).toBe("10.0 m/s");
  });
});

describe("convertOutput", () => {
  test("converts to kWh", () => {
    expect(convertOutput(1000, "kWh")).toBe("1,000.0 kWh");
  });
  test("converts to MWh", () => {
    expect(convertOutput(1000, "MWh")).toBe("1.0 MWh");
  });
});

describe("percentToFactor", () => {
  test("17% -> 0.83", () => {
    expect(percentToFactor(17)).toBeCloseTo(0.83, 2);
  });
  test("0% -> 1", () => {
    expect(percentToFactor(0)).toBe(1);
  });
  test("100% -> 0", () => {
    expect(percentToFactor(100)).toBe(0);
  });
  test("clamps and handles NaN", () => {
    // @ts-expect-error testing bad input
    expect(percentToFactor("abc")).toBe(1);
    expect(percentToFactor(-10)).toBe(1);
    expect(percentToFactor(150)).toBe(0);
  });
});

describe("applyLoss", () => {
  test("applies factor correctly", () => {
    expect(applyLoss(1000, 0.83)).toBeCloseTo(830, 0);
  });
  test("clamps factor and handles non-number value", () => {
    // @ts-expect-error testing bad input
    expect(applyLoss("abc", 0.9)).toBe(0);
    expect(applyLoss(1000, 2)).toBe(1000);
    expect(applyLoss(1000, -1)).toBe(0);
  });
  test("rounds to nearest whole when configured", () => {
    expect(applyLoss(1234.56, 0.83, { mode: "nearest" })).toBe(1025);
  });
  test("floors to whole when configured", () => {
    expect(applyLoss(1234.56, 0.83, { mode: "floor" })).toBe(1024);
  });
  test("floors to 2 decimals when configured", () => {
    expect(applyLoss(2.089, 1, { mode: "floor", digits: 2 })).toBe(2.08);
  });
  test("rounds to nearest 1 decimal when configured", () => {
    expect(applyLoss(123.45, 0.83, { mode: "nearest", digits: 1 })).toBe(102.5);
  });
  test("rounds to significant digits when configured", () => {
    expect(applyLoss(12.345, 0.83, { mode: "sig", digits: 2 })).toBeCloseTo(
      10,
      10
    );
  });
});

describe("roundToSignificantDigits", () => {
  test("handles zeros", () => {
    expect(roundToSignificantDigits(0, 2)).toBe(0);
  });
  test("simple rounding", () => {
    expect(roundToSignificantDigits(1234.56, 2)).toBe(1200);
    expect(roundToSignificantDigits(0.012345, 2)).toBe(0.012);
  });
});
