// Builds the static site Vercel serves: every Markdown file in the hub becomes a page under public/, and the raw
// files the skills point to (SKILL.md files, AGENTS.md) are copied as they are. `npm run build`.
import { marked } from "marked";
import fs from "node:fs";
import path from "node:path";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1")), "..");
const OUT = path.join(ROOT, "public");
const REPO = "https://github.com/multiplayereverything/flash-multiplayer-skill";
const SKIP = new Set([".git", "node_modules", "public", "site", ".vercel"]);

const NAV = [
  ["Home", "index.html"],
  ["Agent guide", "AGENTS.html"],
  ["Directory", "DIRECTORY.html"],
  ["Umbrella skill", "SKILL.html"],
  ["Your relay", "relay/README.html"],
  ["mods-info kit", "modsinfo/README.html"],
  ["Templates", "templates/README.html"],
];

function mdFiles(dir, rel = "") {
  let out = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (SKIP.has(e.name)) continue;
    const r = rel ? rel + "/" + e.name : e.name;
    if (e.isDirectory()) out = out.concat(mdFiles(path.join(dir, e.name), r));
    else if (e.name.endsWith(".md")) out.push(r);
  }
  return out;
}

const pages = mdFiles(ROOT);
const pageSet = new Set(pages);
const htmlName = (rel) => (rel === "README.md" ? "index.html" : rel.replace(/\.md$/, ".html"));

// Links between Markdown files become links between pages; links to anything else go to the file on GitHub.
function fixLink(href, fromRel) {
  if (/^([a-z]+:|#|\/\/)/i.test(href)) return href;
  const [p, hash] = href.split("#");
  const target = path.posix.normalize(path.posix.join(path.posix.dirname(fromRel), p));
  const tail = hash ? "#" + hash : "";
  const depth = fromRel.split("/").length - 1;
  const up = "../".repeat(depth);
  if (pageSet.has(target)) return up + htmlName(target) + tail;
  if (pageSet.has(target + "/README.md")) return up + htmlName(target + "/README.md") + tail;
  const exists = fs.existsSync(path.join(ROOT, target));
  const isDir = exists && fs.statSync(path.join(ROOT, target)).isDirectory();
  return `${REPO}/${isDir ? "tree" : "blob"}/main/${target}${tail}`;
}

function titleOf(md, rel) {
  const m = md.match(/^#\s+(.+)$/m);
  return m ? m[1].replace(/[`*]/g, "") : rel;
}

function page(rel, md) {
  const body = md.replace(/^---\n[\s\S]*?\n---\n/, ""); // SKILL.md frontmatter
  const renderer = new marked.Renderer();
  const link = renderer.link.bind(renderer);
  renderer.link = (tok) => link({ ...tok, href: fixLink(tok.href, rel) });
  // raw HTML in the Markdown (the README's <details> blocks) keeps its own links: fix the .md ones too
  const html = marked.parse(body, { renderer, gfm: true })
    .replace(/href="([^":#]+\.md)(#[^"]*)?"/g, (m, p, h) => `href="${fixLink(p + (h || ""), rel)}"`);
  const depth = rel.split("/").length - 1;
  const up = "../".repeat(depth);
  const nav = NAV.map(([t, h]) => `<a href="${up}${h}"${htmlName(rel) === h ? ' aria-current="page"' : ""}>${t}</a>`).join("");
  const title = titleOf(body, rel);
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${title === "Flash Multiplayer" ? title : title + " · Flash Multiplayer"}</title>
<link rel="stylesheet" href="${up}style.css">
</head>
<body>
<header><a class="brand" href="${up}index.html">Flash Multiplayer</a><nav>${nav}</nav>
<a class="gh" href="${REPO}/blob/main/${rel}">Source</a></header>
<main>${html}</main>
<footer>Install: <code>npx skills add multiplayereverything/flash-multiplayer-skill</code></footer>
</body>
</html>
`;
}

fs.rmSync(OUT, { recursive: true, force: true });
for (const rel of pages) {
  const md = fs.readFileSync(path.join(ROOT, rel), "utf8").replace(/\r\n/g, "\n");
  const dest = path.join(OUT, htmlName(rel));
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.writeFileSync(dest, page(rel, md));
  fs.copyFileSync(path.join(ROOT, rel), path.join(OUT, rel)); // the raw file too, e.g. /SKILL.md
}
fs.copyFileSync(path.join(ROOT, "site", "style.css"), path.join(OUT, "style.css"));
console.log(`site: ${pages.length} pages in public/`);
