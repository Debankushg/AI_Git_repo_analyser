from collections import Counter
from pathlib import PurePosixPath

EXT_LANG = {
    ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript",
    ".java": "Java", ".go": "Go", ".rs": "Rust", ".rb": "Ruby", ".php": "PHP", ".c": "C", ".h": "C",
    ".cpp": "C++", ".cs": "C#", ".kt": "Kotlin", ".swift": "Swift", ".html": "HTML", ".css": "CSS",
    ".scss": "SCSS", ".sh": "Shell", ".vue": "Vue", ".dart": "Dart", ".lua": "Lua", ".r": "R",
}


def detect_language(paths: list[str]) -> str | None:
    """Most common programming language by file extension (cheap heuristic for hosts without an API)."""
    counts = Counter(EXT_LANG[e] for p in paths if (e := PurePosixPath(p).suffix.lower()) in EXT_LANG)
    return counts.most_common(1)[0][0] if counts else None
