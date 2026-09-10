import { describe, expect, it } from "vitest";
import { dataBadge, inr } from "./format";

describe("format helpers", () => {
  it("formats INR", () => {
    expect(inr(580)).toContain("580");
  });

  it("labels demo data", () => {
    expect(dataBadge("DEMO")).toBe("DEMO");
    expect(dataBadge("LIVE")).toBe("LIVE");
  });
});
