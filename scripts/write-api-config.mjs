/**
 * Vercel build: writes frontend/static/api-config.js from BACKEND_URL.
 * Paths are resolved from this file so the repo root is correct even if cwd varies.
 */
import { mkdirSync, writeFileSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = join(__dirname, "..");
const out = join(repoRoot, "frontend", "static", "api-config.js");
const url = (process.env.BACKEND_URL || "").trim().replace(/\/+$/, "");

mkdirSync(dirname(out), { recursive: true });
writeFileSync(
  out,
  "/** Injected at Vercel build from BACKEND_URL. */\n" +
    `window.__API_BASE__ = ${JSON.stringify(url)};\n`,
  "utf8",
);
console.log(`Wrote ${out} (BACKEND_URL length ${url.length})`);
