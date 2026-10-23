#!/usr/bin/env python3
"""Every shipped nonzero effect against both original offline driver slots."""
import argparse,hashlib,json,sys,wave,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from extract_session_sfx import GaxOracle
from extract import Rom
ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();r=Rom(a.rom)
j=json.loads((ROOT/'docs/complete_sfx_resources.json').read_text());assert j['rom_sha256']==r.sha256
assert [x['sound_id']for x in j['effects']]==list(range(1,104))
pointers=struct.unpack_from('<104I',r.data,0x56c48);assert pointers==tuple(0x080550bc+68*i for i in range(104));assert struct.unpack_from('<I',r.data,0x56de8)[0]==0x80808080
for fx in j['effects']:
 p=ROOT/'android/app/src/main/assets/session/audio'/fx['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==fx['sha256']
 with wave.open(str(p),'rb')as w:
  assert (w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes())==(1,2,31537,fx['samples']);pcm=w.readframes(w.getnframes())
 assert hashlib.sha256(pcm).hexdigest()==fx['pcm_sha256']
 for channel in [0,1]:assert GaxOracle(r.data,rate=31537).render(fx['sound_id'],channel)==(pcm,fx['driver_ticks'])
report=dict(effects=103,original_slot_renders=206,missing_nonzero_ids=[],mismatches=0,scope='Exact PCM and duration against original offline GAX, both slots. No Android audible output or unported event-trigger coverage claim.')
(ROOT/'docs/complete_sfx_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
