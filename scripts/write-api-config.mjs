/**
 * Vercel build: writes frontend/api-config.js from BACKEND_URL.
 * Paths are resolved from this file so the repo root is correct even if cwd varies.
 */
import { writeFileSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = join(__dirname, "..");
const out = join(repoRoot, "frontend", "api-config.js");
const url = (process.env.BACKEND_URL || "").trim().replace(/\/+$/, "");

writeFileSync(
  out,
  "/** Injected at Vercel build from BACKEND_URL. */\n" +
    `window.__API_BASE__ = ${JSON.stringify(url)};\n`,
  "utf8",
);
console.log(`Wrote ${out} (BACKEND_URL length ${url.length})`);
