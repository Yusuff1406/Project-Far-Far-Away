#!/usr/bin/env python3
"""Offline original GAX capture for chapter01 protagonist effects."""
import argparse,hashlib,json,wave
from extract_session_sfx import GaxOracle
from extract import Rom
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];IDS=[11,13,14,15,18,19,55,75]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();rom=Rom(a.rom);rows=[];out=ROOT/'android/app/src/main/assets/session/audio'
 for sound in IDS:
  first=GaxOracle(rom.data,rate=31537);pcm,ticks=first.render(sound);other=GaxOracle(rom.data,rate=31537);duplicate,again=other.render(sound,1);assert pcm==duplicate and ticks==again;path=out/f'sfx_{sound}.wav'
  with wave.open(str(path),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(31537);w.writeframes(pcm)
  rows.append(dict(sound_id=sound,file=path.name,samples=len(pcm)//2,driver_ticks=ticks,sample_rate=31537,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),pcm_sha256=hashlib.sha256(pcm).hexdigest()))
 (ROOT/'docs/donkey_sfx_resources.json').write_text(json.dumps(dict(rom_sha256=rom.sha256,effects=rows,scope='Offline precise GAX accumulators; two original effect slots match. Android playback not tested.'),indent=2)+'\n');print('Eight original effects extracted')
if __name__=='__main__':main()
