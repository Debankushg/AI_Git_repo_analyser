const LANGUAGES: Record<string, string> = {
  ts: "typescript", tsx: "typescript", js: "javascript", jsx: "javascript", mjs: "javascript", cjs: "javascript",
  py: "python", json: "json", md: "markdown", markdown: "markdown", html: "xml", xml: "xml", svg: "xml",
  css: "css", scss: "scss", sh: "bash", bash: "bash", zsh: "bash", yml: "yaml", yaml: "yaml", toml: "ini", ini: "ini",
  java: "java", go: "go", rs: "rust", rb: "ruby", php: "php", c: "c", h: "c", cpp: "cpp", cs: "csharp", kt: "kotlin",
  swift: "swift", sql: "sql", dockerfile: "dockerfile", vue: "xml", graphql: "graphql", lua: "lua", r: "r",
};

const NAMES: Record<string, string> = { dockerfile: "dockerfile", makefile: "makefile" };

export function fileName(path: string): string {
  return path.split("/").pop() ?? path;
}

export function getLanguage(path: string): string {
  const name = fileName(path).toLowerCase();
  if (NAMES[name]) return NAMES[name];
  const ext = name.includes(".") ? name.split(".").pop()! : "";
  return LANGUAGES[ext] ?? "plaintext";
}

export const isMarkdown = (path: string) => /\.(md|markdown)$/i.test(path);

export function formatBytes(n: number): string {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / 1024 / 1024).toFixed(1)} MB`;
}

/** Split highlight.js HTML into per-line HTML, re-opening spans that cross line breaks. */
export function splitHighlightedLines(html: string): string[] {
  const open: string[] = [];
  return html.split("\n").map((line) => {
    const prefix = open.join("");
    const tags = /<span[^>]*>|<\/span>/g;
    let m: RegExpExecArray | null;
    while ((m = tags.exec(line))) {
      if (m[0] === "</span>") open.pop();
      else open.push(m[0]);
    }
    return prefix + line + "</span>".repeat(open.length);
  });
}
