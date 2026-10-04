#!/usr/bin/env python3
"""Hiruna Clip Director — transcript + HD section fetch tool.

Produces schema-conformant artifacts for the Hiruna Clip workflow:
  plan      Download subtitles only -> transcript.json (no video download)
  validate  Validate a JSON artifact against a repo schema
  fetch     Download one clip section from clip_manifest.json in 1080p,
            fullframe 16:9, no crop, no burned captions

Cookies for HD download are NEVER hardcoded. Provide via:
  --cookies /path/to/cookies.txt   (or HIRUNA_COOKIES env var)
Export with the "Get cookies.txt LOCALLY" browser extension.

Prerequisites: yt-dlp, ffmpeg, deno (for YouTube JS challenge),
               python3 -m pip install jsonschema

Usage:
  python3 tools/director.py plan <youtube_url> [--workdir DIR]
  python3 tools/director.py validate <json> <schema-name> [--workdir DIR]
  python3 tools/director.py fetch <clip_id> [--handles N] [--cookies PATH] [--workdir DIR]
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_DIR = os.path.join(REPO_ROOT, "docs", "schemas")

YT_DLP_BASE = ["yt-dlp", "--extractor-args", "youtube:player_client=android"]
HD_FORMAT = ("bv[height<=1080][vcodec^=avc1]+ba/"
             "b[height<=1080][vcodec^=avc1]/"
             "bv[height<=1080]+ba/b[height<=1080]")


def require_binary(name):
    if shutil.which(name) is None:
        sys.exit(f"error: required executable '{name}' was not found on PATH.")


def hms(sec):
    sec = int(sec)
    return f"{sec // 3600:02d}:{(sec % 3600) // 60:02d}:{sec % 60:02d}"


def hms_ms(sec):
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{s:06.3f}"


def parse_vtt_ts(s):
    h, m, sec = s.split(":")
    return int(h) * 3600 + int(m) * 60 + float(sec)


def cmd_plan(url, workdir):
    require_binary("yt-dlp")
    meta = subprocess.run(
        YT_DLP_BASE + ["--print", "%(title)s\t%(duration)s",
                       "--skip-download", url],
        capture_output=True, text=True, cwd=workdir, check=True)
    title, duration_s = meta.stdout.strip().split("\t")
    duration_s = float(duration_s)
    print(f"VIDEO: {title} | {hms(duration_s)}")

    # Subtitles only — never downloads the video.
    subprocess.run(
        YT_DLP_BASE + ["--write-auto-subs", "--sub-langs", "id.*",
                       "--skip-download", "-o", "subs.%(ext)s", url],
        check=True, capture_output=True, cwd=workdir)
    vtt = os.path.join(workdir, "subs.id.vtt")
    with open(vtt) as f:
        content = f.read()
    cues = re.findall(
        r"(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3}).*?\n((?:(?!\n\n).)*)",
        content, re.S)

    # Dedupe rolling captions into clean segments.
    segments, seen_words = [], []
    for a, b, text in cues:
        toks = text.replace("\n", " ").strip().split()
        cut = 0
        for n in range(min(len(toks), 10), 0, -1):
            if seen_words[-n:] == toks[:n]:
                cut = n
                break
        new_toks = toks[cut:]
        seen_words.extend(new_toks)
        if not new_toks:
            continue
        cs, ce = parse_vtt_ts(a), parse_vtt_ts(b)
        if segments and cs - segments[-1]["_ce"] < 1.5 and len(segments[-1]["text"]) < 120:
            segments[-1]["text"] += " " + " ".join(new_toks)
            segments[-1]["_ce"] = ce
            segments[-1]["end"] = hms_ms(ce)
        else:
            segments.append({"id": f"seg-{len(segments):04d}",
                             "start": hms_ms(cs), "end": hms_ms(ce),
                             "text": " ".join(new_toks), "_ce": ce})
    for s in segments:
        del s["_ce"]

    doc = {"schema_version": "1.0",
           "source": {"url": url, "title": title, "language": "id",
                      "duration": hms(duration_s)},
           "segments": segments}
    out = os.path.join(workdir, "transcript.json")
    with open(out, "w") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    print(f"transcript.json: {len(segments)} segments")
    print("Validate with: python3 tools/director.py validate transcript.json transcript.schema.json")


def cmd_validate(json_path, schema_name):
    try:
        import jsonschema
    except ImportError:
        sys.exit("jsonschema not installed; run: pip install jsonschema")
    schema_path = (schema_name if os.path.isabs(schema_name)
                   else os.path.join(SCHEMA_DIR, schema_name))
    with open(json_path) as f:
        doc = json.load(f)
    with open(schema_path) as f:
        schema = json.load(f)
    jsonschema.validate(doc, schema)
    print(f"OK: {json_path} conforms to {schema_path}")


def cmd_fetch(clip_id, handles, cookies, workdir):
    """Download one clip section in HD (1080p), fullframe 16:9.

    Reads clip_manifest.json, downloads only the selected section with
    N-second handles on each side. No crop, no burned captions — the
    human editor handles those on their PC.
    """
    require_binary("yt-dlp")
    require_binary("ffmpeg")
    if not cookies or not os.path.isfile(cookies):
        sys.exit("error: HD fetch needs YouTube cookies. "
                 "Pass --cookies /path/to/cookies.txt or set HIRUNA_COOKIES.")

    with open(os.path.join(workdir, "clip_manifest.json")) as f:
        manifest = json.load(f)
    clip = next((c for c in manifest["clips"] if c["id"] == clip_id), None)
    if not clip:
        sys.exit(f"error: clip '{clip_id}' not found in clip_manifest.json")

    def to_sec(t):
        h, m, s = t.split(":")
        return int(h) * 3600 + int(m) * 60 + float(s)

    def fmt(s):
        return f"{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{int(s % 60):02d}"

    start = max(0, to_sec(clip["start"]) - handles)
    end = to_sec(clip["end"]) + handles
    section = f"*{fmt(start)}-{fmt(end)}"
    out = os.path.join(workdir, "clips", f"{clip_id}_HD.mp4")
    os.makedirs(os.path.join(workdir, "clips"), exist_ok=True)

    # Deno solves YouTube's JS challenge; harmless if already on PATH.
    env = dict(os.environ)
    deno_dir = os.path.expanduser("~/.deno/bin")
    if os.path.isdir(deno_dir) and deno_dir not in env.get("PATH", ""):
        env["PATH"] = deno_dir + ":" + env.get("PATH", "")
    if shutil.which("deno") is None and not shutil.which("deno", path=env["PATH"]):
        print("warning: deno not found on PATH — HD formats may fail "
              "with a bot challenge. Install from https://deno.land/")

    cmd = (["yt-dlp", "--remote-components", "ejs:github",
            "--cookies", cookies]
           + ["--download-sections", section, "-f", HD_FORMAT,
              "--merge-output-format", "mp4", "-o", out,
              manifest["source"]["url"]])
    print(f"Fetching {clip_id}: {fmt(start)} -> {fmt(end)} "
          f"(handles ±{handles}s) in 1080p fullframe...")
    for attempt in range(1, 4):
        try:
            subprocess.run(cmd, check=True, cwd=workdir, env=env)
            break
        except subprocess.CalledProcessError:
            if attempt == 3:
                raise
            wait = 15 * attempt
            print(f"Attempt {attempt} failed (YouTube throttling?) — "
                  f"retrying in {wait}s...")
            time.sleep(wait)

    # Sanity check: audio must span the whole clip, not truncate.
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,duration",
         "-of", "csv=p=0", out],
        capture_output=True, text=True, check=True)
    durations = {}
    for line in probe.stdout.strip().splitlines():
        ctype, dur = line.split(",")
        durations[ctype] = float(dur)
    if durations.get("audio", 0) < durations.get("video", 0) * 0.9:
        print(f"WARNING: audio ({durations.get('audio', 0):.1f}s) is much shorter "
              f"than video ({durations.get('video', 0):.1f}s) — "
              f"the section cut may have truncated the audio stream.")
    print(f"OK -> {out}")


def main():
    p = argparse.ArgumentParser(description="Hiruna Clip Director tool.")
    p.add_argument("--workdir", default=os.getcwd(),
                   help="working directory for artifacts (default: cwd)")
    sub = p.add_subparsers(dest="cmd", required=True)

    pp = sub.add_parser("plan", help="subtitles only -> transcript.json")
    pp.add_argument("url")

    pv = sub.add_parser("validate", help="validate JSON against a schema")
    pv.add_argument("json_path")
    pv.add_argument("schema", help="schema file name or absolute path")

    pf = sub.add_parser("fetch", help="download one clip section in 1080p")
    pf.add_argument("clip_id")
    pf.add_argument("--handles", type=int, default=3)
    pf.add_argument("--cookies", default=os.environ.get("HIRUNA_COOKIES"),
                    help="cookies.txt path (or HIRUNA_COOKIES env var)")

    a = p.parse_args()
    workdir = os.path.abspath(a.workdir)
    os.makedirs(workdir, exist_ok=True)
    if a.cmd == "plan":
        cmd_plan(a.url, workdir)
    elif a.cmd == "validate":
        cmd_validate(a.json_path, a.schema)
    elif a.cmd == "fetch":
        cmd_fetch(a.clip_id, a.handles, a.cookies, workdir)


if __name__ == "__main__":
    main()
