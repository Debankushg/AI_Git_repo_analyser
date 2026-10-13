import hljs from "highlight.js/lib/common";
import { useMemo } from "react";
import { splitHighlightedLines } from "../../utils/fileUtils";

interface Props {
  code: string;
  language: string;
  wrap: boolean;
}

const MAX_HIGHLIGHT_CHARS = 300_000;

export default function CodeView({ code, language, wrap }: Props) {
  const lines = useMemo(() => {
    const text = code.replace(/\n$/, "");
    if (text.length > MAX_HIGHLIGHT_CHARS || !hljs.getLanguage(language)) {
      return text.split("\n").map((l) => l.replace(/&/g, "&amp;").replace(/</g, "&lt;"));
    }
    return splitHighlightedLines(hljs.highlight(text, { language, ignoreIllegals: true }).value);
  }, [code, language]);

  return (
    <div className="overflow-auto rounded-xl border border-gold/30 bg-subtle font-mono text-xs leading-6">
      <table className="w-full border-collapse">
        <tbody>
          {lines.map((html, i) => (
            <tr key={i} className="hover:bg-gold/10">
              <td className="sticky left-0 w-10 select-none border-r border-line bg-subtle px-2 text-right align-top text-muted">{i + 1}</td>
              <td className={`px-3 align-top ${wrap ? "whitespace-pre-wrap break-all" : "whitespace-pre"}`} dangerouslySetInnerHTML={{ __html: html || " " }} />
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
