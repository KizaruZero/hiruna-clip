from pathlib import Path
import math,wave
from discovery.audio import analyze_wav

def test_audio_analysis(tmp_path: Path):
    path=tmp_path/"tone.wav"; rate=16000; frames=bytearray()
    for i in range(rate*3):
        amp=3000 if i<rate else 12000 if i<rate*2 else 3000
        frames.extend(int(amp*math.sin(2*math.pi*440*i/rate)).to_bytes(2,"little",signed=True))
    with wave.open(str(path),"wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(frames)
    events=analyze_wav(path); assert events; assert all(0<=e.strength<=1 for e in events)
