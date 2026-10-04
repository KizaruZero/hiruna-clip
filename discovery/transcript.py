import re
from pathlib import Path
from .models import TranscriptSegment
from .timecode import seconds_to_timecode

TIMING_RE = re.compile(r"^(\\d{2}:\\d{2}:\\d{2}(?:[.,]\\d{3})?)\\s*-->\\s*(\\d{2}:\\d{2}:\\d{2}(?:[.,]\\d{3})?)")
TAG_RE = re.compile(r"<[^>]+>")

def _parse(value):
    value = value.replace(",", ".")
    h, m, s = value.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)

def _clean(text):
    text = TAG_RE.sub("", text)
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"\\s+", " ", text).strip()

def parse_vtt(content: str) -> list[TranscriptSegment]:
    lines = content.replace("\\r\\n", "\\n").replace("\\r", "\\n").lstrip("\\ufeff").split("\\n")
    raw, i = [], 0
    while i < len(lines):
        match = TIMING_RE.match(lines[i].strip())
        if not match:
            i += 1; continue
        start, end = _parse(match.group(1)), _parse(match.group(2))
        i += 1; text_lines = []
        while i < len(lines) and lines[i].strip() and not TIMING_RE.match(lines[i].strip()):
            if not lines[i].strip().startswith(("NOTE", "STYLE", "REGION")): text_lines.append(lines[i].strip())
            i += 1
        text = _clean(" ".join(text_lines))
        if text: raw.append((start, end, text))
        i += 1
    result, previous = [], None
    for start, end, text in raw:
        if text == previous: continue
        result.append(TranscriptSegment(f"seg_{len(result)+1:04d}", seconds_to_timecode(start), seconds_to_timecode(end), text))
        previous = text
    return result

def load_vtt(path: Path):
    return parse_vtt(path.read_text(encoding="utf-8-sig"))
