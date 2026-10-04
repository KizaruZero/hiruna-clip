import argparse
from pathlib import Path
from .pipeline import run

def main():
    p=argparse.ArgumentParser(description="Hiruna Clip deterministic YouTube evidence discovery.")
    p.add_argument("url"); p.add_argument("-o","--output",default="artifacts")
    a=p.parse_args(); transcript,audio=run(a.url,Path(a.output))
    print(f"Transcript segments: {len(transcript['segments'])}")
    print(f"Audio events: {len(audio['events'])}")
    print(f"Artifacts written to: {Path(a.output).resolve()}")
