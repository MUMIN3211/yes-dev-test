import path from "node:path";
import { fileURLToPath } from "node:url";

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Pin the workspace root to this folder (a lockfile higher up confuses Next's detection)
  outputFileTracingRoot: path.dirname(fileURLToPath(import.meta.url)),
  experimental: {
    // Excel import goes through a server action; default limit is 1 MB, backend allows 5 MB
    serverActions: { bodySizeLimit: "6mb" },
  },
};

export default nextConfig;
