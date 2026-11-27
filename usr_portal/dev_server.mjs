/**
 * Zero-dependency local development server mimicking Vercel Serverless Functions + static public/.
 * Usage:
 *   SUPABASE_SOURCES_JSON='[...]' node dev_server.mjs
 */
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import studentsHandler from "./api/students.js";
import usrHandler from "./api/usr.js";
import jadeedPagesHandler from "./api/jadeed-pages.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PORT = Number(process.env.PORT || 3030);

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".json": "application/manifest+json; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
};

function wrapRes(nodeRes) {
  const res = {
    statusCode: 200,
    setHeader: (k, v) => nodeRes.setHeader(k, v),
    status(code) {
      this.statusCode = code;
      nodeRes.statusCode = code;
      return this;
    },
    json(obj) {
      if (!nodeRes.headersSent) nodeRes.setHeader("Content-Type", "application/json; charset=utf-8");
      nodeRes.end(JSON.stringify(obj));
    },
    end(body) {
      nodeRes.end(body);
    },
  };
  return res;
}

const server = http.createServer(async (req, nodeRes) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  req.query = Object.fromEntries(url.searchParams.entries());
  const res = wrapRes(nodeRes);

  if (url.pathname === "/api/students") return studentsHandler(req, res);
  if (url.pathname === "/api/usr") return usrHandler(req, res);
  if (url.pathname === "/api/jadeed-pages") return jadeedPagesHandler(req, res);

  const rel = url.pathname === "/" ? "index.html" : url.pathname.replace(/^\/+/, "");
  const filePath = path.join(__dirname, "public", rel);
  if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
    const ext = path.extname(filePath);
    nodeRes.setHeader("Content-Type", MIME[ext] || "application/octet-stream");
    fs.createReadStream(filePath).pipe(nodeRes);
    return;
  }

  nodeRes.statusCode = 404;
  nodeRes.end("Not found");
});

server.listen(PORT, () => {
  console.log(`MSB Collective USR local server running at http://localhost:${PORT}`);
});
