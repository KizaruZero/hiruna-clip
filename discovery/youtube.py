import json, shutil, subprocess
from pathlib import Path

def require_binary(name):
    if shutil.which(name) is None: raise RuntimeError(f"Required executable '{name}' was not found on PATH.")

def fetch_metadata(url):
    require_binary("yt-dlp")
    r = subprocess.run(["yt-dlp","--dump-single-json","--skip-download","--no-warnings",url], check=True, capture_output=True, text=True)
    return json.loads(r.stdout)

def fetch_subtitles(url, workdir, preferred_languages=None):
    require_binary("yt-dlp")
    preferred_languages = preferred_languages or ["id","en"]
    workdir.mkdir(parents=True, exist_ok=True)
    subprocess.run(["yt-dlp","--skip-download","--write-auto-subs","--write-subs","--sub-format","vtt","--sub-langs",",".join(preferred_languages),"--no-warnings","-o",str(workdir/"source.%(ext)s"),url], check=True, capture_output=True, text=True)
    candidates = sorted(workdir.glob("source*.vtt"))
    if not candidates: raise RuntimeError("No subtitles/captions were available for this video.")
    def rank(p):
        n=p.name.lower()
        return (0,n) if ".id." in n else (1,n) if ".en." in n else (2,n)
    return sorted(candidates,key=rank)[0]
