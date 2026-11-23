import assert from "node:assert/strict";
import test from "node:test";
import { apiBaseUrl, readinessTone } from "./api.ts";

test("apiBaseUrl normalizes trailing slashes", () => {
  assert.equal(apiBaseUrl("http://localhost:8000///"), "http://localhost:8000");
});

test("readinessTone maps regulatory readiness scores cleanly", () => {
  assert.equal(readinessTone(100), "ready");
  assert.equal(readinessTone(75), "warn");
  assert.equal(readinessTone(25), "blocked");
});
