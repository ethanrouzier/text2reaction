import re
from typing import List, Tuple

# Heuristics: find Experimental-like sections and return (title, text)
HEADERS = [
    r"Experimental",
    r"Experimental Section",
    r"General Experimental",
    r"Materials and Methods",
    r"Procedure",
    r"Synthesis of[\s\S]*?\n",
]

HEADER_RE = re.compile(rf"^(?:{'|'.join(HEADERS)})\b.*$", re.IGNORECASE | re.MULTILINE)

# naive next-header matcher: if we detect a header at span A..B, take until next header or end

def find_sections(full_text: str, max_sections: int = 3) -> list[tuple[str, str]]:
    matches = list(HEADER_RE.finditer(full_text))
    sections: List[Tuple[str, str]] = []
    if not matches:
        # fallback: search for the word Experimental and take a window
        idx = full_text.lower().find("experimental")
        if idx != -1:
            start = max(0, idx - 200)
            end = min(len(full_text), idx + 6000)
            sections.append(("Experimental (window)", full_text[start:end]))
        return sections

    for i, m in enumerate(matches[:max_sections]):
        title = m.group(0).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
        body = full_text[start:end].strip()
        sections.append((title, body))
    return sections
