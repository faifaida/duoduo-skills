#!/usr/bin/env python3
"""Parse each labelled Chinese podcast turn. Usage: script.py input.txt manifest.json"""
import json
import re
import sys
from pathlib import Path

if len(sys.argv) != 3:
    raise SystemExit("usage: parse_turn_manifest.py SCRIPT.txt MANIFEST.json")

src, dest = map(Path, sys.argv[1:])
text = src.read_text(encoding="utf-8")
pattern = re.compile(r"(?mi)^\s*SPEAKER_([AB])\s*[:：]\s*")
matches = list(pattern.finditer(text))
turns = []
for n, m in enumerate(matches, 1):
    end = matches[n].start() if n < len(matches) else len(text)
    spoken = text[m.end():end].strip()
    if not spoken:
        raise ValueError(f"empty speaker turn {n}")
    parts = [x.strip() for x in re.split(r"(?<=[。！？!?])", spoken) if x.strip()]
    turns.append({
        "turn_id": f"T{n:03}", "speaker": m.group(1), "text": spoken,
        "sentence_parts": parts, "render_paths": [], "duration_seconds": None,
        "qc_status": "pending"
    })
dest.write_text(json.dumps({"source": str(src), "turn_count": len(turns), "turns": turns}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"wrote {len(turns)} turns: {dest}")
