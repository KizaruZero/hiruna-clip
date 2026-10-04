import math, shutil, subprocess, wave, array
from pathlib import Path
from .models import AudioEvent
from .timecode import seconds_to_timecode

def extract_wav(url: str, output: Path):
    for binary in ("yt-dlp","ffmpeg"):
        if shutil.which(binary) is None: raise RuntimeError(f"Required executable '{binary}' was not found on PATH.")
    output.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen(["yt-dlp","-f","bestaudio/best","-o","-","--no-warnings",url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ff = subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i","pipe:0","-ac","1","-ar","16000","-f","wav",str(output)], stdin=proc.stdout, capture_output=True, text=True)
    proc.stdout.close(); err=proc.stderr.read().decode(errors="replace"); rc=proc.wait()
    if rc != 0: raise RuntimeError(f"yt-dlp audio extraction failed: {err[-1000:]}")
    if ff.returncode != 0: raise RuntimeError(f"ffmpeg audio extraction failed: {ff.stderr[-1000:]}")

def analyze_wav(path: Path, window_seconds=2.0, hop_seconds=1.0):
    with wave.open(str(path),"rb") as wav:
        rate, channels, width, frames = wav.getframerate(), wav.getnchannels(), wav.getsampwidth(), wav.getnframes()
        raw=wav.readframes(frames)
    if channels != 1 or width != 2: raise RuntimeError("Expected mono 16-bit PCM WAV.")
    samples=array.array("h"); samples.frombytes(raw)
    win=max(1,int(rate*window_seconds)); hop=max(1,int(rate*hop_seconds))
    energies=[]; timestamps=[]
    for start in range(0,max(1,len(samples)-win+1),hop):
        chunk=samples[start:start+win]
        if chunk:
            energies.append(math.sqrt(sum(float(x)*float(x) for x in chunk)/len(chunk))); timestamps.append(start/rate)
    if not energies: return []
    baseline=sorted(energies)[len(energies)//2] or 1.0; peak=max(energies) or 1.0
    events=[]
    for i,e in enumerate(energies):
        local=energies[max(0,i-5):min(len(energies),i+6)]; lb=sum(local)/len(local)
        rel=e/max(lb,1e-9); strength=min(1.0,max(0.0,e/peak))
        if rel >= 1.8: typ="energy_spike"; value=strength
        elif e >= peak*0.85: typ="volume_peak"; value=strength
        elif e <= baseline*0.18: typ="low_energy"; value=1-strength
        else: continue
        event=AudioEvent(seconds_to_timecode(timestamps[i]),typ,round(value,4))
        if not events or events[-1].type != event.type: events.append(event)
    return events
