#!/usr/bin/env python3
"""Additional original spell-enemy effects56/58, precise source GAX PCM16."""
import hashlib,json,sys,wave
from extract_session_sfx import GaxOracle,ROOT
from extract import Rom
r=Rom(sys.argv[1]);items=[]
for id in [56,58]:
 o=GaxOracle(r.data,rate=31537);pcm,ticks=o.render(id);other=GaxOracle(r.data,rate=31537);assert other.render(id,1)==(pcm,ticks)
 p=ROOT/f'android/app/src/main/assets/session/audio/sfx_{id}.wav'
 with wave.open(str(p),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(o.rate);w.writeframes(pcm)
 items.append(dict(sound_id=id,file=p.name,samples=len(pcm)//2,driver_ticks=ticks,sample_rate=o.rate,pcm_sha256=hashlib.sha256(pcm).hexdigest(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
report=dict(effects=items,rom_sha256=r.sha256,scope='Original offline GAX, both slots compared,31537Hz before final quantizer. Android plays WAV; no device listening validation.')
(ROOT/'docs/world67_sfx_resources.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
