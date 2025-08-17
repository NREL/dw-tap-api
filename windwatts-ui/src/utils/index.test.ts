import { describe, expect, test } from "vitest";
import { convertOutput, convertWindspeed, getWindResource } from ".";

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
    expect(convertWindspeed(10, "mph")).toBe("22.37 mph");
  });
  test("converts to m/s", () => {
    expect(convertWindspeed(10, "m/s")).toBe("10 m/s");
  });
});

describe("convertOutput", () => {
  test("converts to kWh", () => {
    expect(convertOutput(1000, "kWh")).toBe("1,000 kWh");
  });
  test("converts to MWh", () => {
    expect(convertOutput(1000, "MWh")).toBe("1 MWh");
  });
});
