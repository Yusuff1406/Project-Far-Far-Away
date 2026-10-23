#!/usr/bin/env python3
"""Original credits movie script 02004224 selects composition08209428."""
import sys,struct,json,wave,hashlib
from pathlib import Path
from extract import Rom
from extract_session_sfx import GaxOracle,ROOT
r=Rom(sys.argv[1]);song=0x08209428;o=GaxOracle(r.data,rate=31537,song=song);o.call(0x0801d428,-1,256);ctx=o.word(o.manager+0x18);blocks=[];states=[];first={};end=None;start=None
for tick in range(24000):
 pcm=o.mix_precise();order,row=struct.unpack('<2H',o.u.mem_read(ctx+12,4));marker=o.u.mem_read(ctx+25,1)[0];key=(order,row)
 if marker and key in first:start=first[key];end=tick;break
 if key not in first:first[key]=tick
 blocks.append(pcm);states.append(key)
assert end is not None and start is not None,(song,len(blocks));out=ROOT/'android/app/src/main/assets/frontend';resources=[]
for name,data in [('credits_intro.wav',b''.join(blocks[:start])),('credits_loop.wav',b''.join(blocks[start:end]))]:
 # MusicPcm accepts empty intro, while loop must be nonempty.
 p=out/name
 with wave.open(str(p),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(o.rate);w.writeframes(data)
 resources.append(dict(file=name,samples=len(data)//2,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
report=dict(song_address=hex(song),source='credits movie initializer08019F94, command5/12 at02004230',start_tick=start,end_tick=end,sample_rate=o.rate,resources=resources,rom_sha256=r.sha256,device_tested=False);(ROOT/'docs/credits_music_resources.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
