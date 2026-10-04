import json, tempfile
from pathlib import Path
from .audio import analyze_wav, extract_wav
from .transcript import load_vtt
from .youtube import fetch_metadata, fetch_subtitles

def _duration(value):
    total=int(round(float(value or 0))); h,rem=divmod(total,3600); m,s=divmod(rem,60); return f"{h:02d}:{m:02d}:{s:02d}"

def _write(path,payload): path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\\n",encoding="utf-8")

def run(url: str, output_dir: Path):
    output_dir.mkdir(parents=True,exist_ok=True); metadata=fetch_metadata(url)
    with tempfile.TemporaryDirectory(prefix="hiruna-discovery-") as tmp:
        tmp=Path(tmp); subtitle=fetch_subtitles(url,tmp); segments=load_vtt(subtitle); wav=tmp/"audio.wav"; extract_wav(url,wav); events=analyze_wav(wav)
    source={"url":url,"title":metadata.get("title") or "Unknown title","language":metadata.get("language") or metadata.get("original_language") or "unknown","duration":_duration(metadata.get("duration"))}
    transcript={"schema_version":"1.0","source":source,"segments":[s.to_dict() for s in segments]}
    audio={"schema_version":"1.0","source":{"url":url,"duration":source["duration"]},"analysis_window_ms":2000,"events":[e.to_dict() for e in events]}
    _write(output_dir/"transcript.json",transcript); _write(output_dir/"audio_events.json",audio); _write(output_dir/"metadata.json",metadata)
    return transcript,audio
