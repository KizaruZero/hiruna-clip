# Phase 1A — Evidence Layer

Phase 1A is the deterministic foundation of Hiruna Clip. It converts a YouTube URL into structured evidence for Muse.

It does not perform semantic clip selection, ranking, scoring, rendering, or publishing.

## Pipeline

1. Fetch YouTube metadata with yt-dlp.
2. Fetch available ID/EN captions and normalize them into transcript segments.
3. Stream best-available audio through FFmpeg and compute deterministic RMS-based audio events.
4. Write `transcript.json`, `audio_events.json`, and `metadata.json`.

## Run

```bash
pip install -r requirements.txt
# install yt-dlp separately if needed: pip install -U yt-dlp
# install ffmpeg and ensure it is on PATH
python -m discovery "https://www.youtube.com/watch?v=VIDEO_ID"
```

The two evidence contracts intended for Muse are `artifacts/transcript.json` and `artifacts/audio_events.json`. `metadata.json` is a supporting/debug artifact.

## Next phase

Muse consumes these artifacts and performs candidate detection, context expansion, boundary selection, scoring, deduplication, ranking, and Clip Manifest generation.
