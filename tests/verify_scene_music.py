#!/usr/bin/env python3
"""Song selection and rendered intro/loop resource integrity."""
import hashlib,json,struct,sys,wave
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from extract_session_sfx import GaxOracle
from extract import Rom

def main():
 rom=Rom(sys.argv[1]).data;oracle=GaxOracle(rom);oracle.call(0x08019648);song=oracle.word(0x02003710+0x1c);assert oracle.word(0x02003710+4)==0x08028d94 and song==0x0820dc94
 report=json.loads((ROOT/'docs/scene_music_resources.json').read_text());assert song==report['song_address'];assert report['loop_start_driver_tick']==256 and report['loop_end_driver_tick']==3328
 verified=[]
 for entry in report['resources']:
  p=ROOT/'android/app/src/main/assets/session/music'/entry['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256']
  with wave.open(str(p),'rb') as w:assert w.getnchannels()==1 and w.getsampwidth()==2 and w.getframerate()==31537 and w.getnframes()==entry['samples'];pcm=w.readframes(w.getnframes())
  values=np.frombuffer(pcm,dtype="<i2").astype(np.int32)/256;assert np.ptp(values)>32;verified.append({'file':entry['file'],'samples':len(pcm)//2,'rms':float(np.sqrt(np.mean(values.astype(float)**2)))})
 result={'original_level_initializer_song_verified':True,'song':hex(song),'wav_resources':verified,'mismatches':0,'scope':'Original19648 scene selection and deterministic stored music PCM resource hashes, intro/loop lengths. Android AudioTrack hardware lifecycle/timing and audible seam not executed; Java buffer/loop contract checked separately.'};(ROOT/'docs/scene_music_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
if __name__=='__main__':main()
