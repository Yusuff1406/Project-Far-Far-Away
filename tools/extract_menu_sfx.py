#!/usr/bin/env python3
import sys,wave,json,hashlib,struct
from extract import Rom
from extract_session_sfx import GaxOracle,ROOT
r=Rom(sys.argv[1]);items=[]
for addr in [0x8054008,0x8053ff0]:
 sound,priority,gain=struct.unpack_from('<3i',r.data,addr-0x8000000);o=GaxOracle(r.data,rate=31537);pcm,ticks=o.render(sound);p=ROOT/f'android/app/src/main/assets/frontend/sfx_{sound}.wav'
 with wave.open(str(p),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(o.rate);w.writeframes(pcm)
 items.append(dict(address=hex(addr),sound=sound,priority=priority,gain=gain,samples=len(pcm)//2,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(ROOT/'docs/frontend_sound_resources.json').write_text(json.dumps(dict(resources=items,source='158E8 cancel + horizontal selection handler, descriptors08054008/08053FF0',rom_sha256=r.sha256),indent=2)+'\n');print(items)
