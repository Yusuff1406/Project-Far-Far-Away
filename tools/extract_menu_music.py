#!/usr/bin/env python3
"""Menu source838C/845C/level-select factory selects [0804B6E0]."""
import sys,struct,json,wave,hashlib
from pathlib import Path
from extract import Rom
from extract_session_sfx import GaxOracle,ROOT
r=Rom(sys.argv[1]);song=struct.unpack_from('<I',r.data,0x4b6e0)[0];o=GaxOracle(r.data,rate=31537,song=song);o.call(0x0801d428,-1,256);ctx=o.word(o.manager+0x18);blocks=[];states=[];first={};end=None;start=None
for tick in range(24000):
 pcm=o.mix_precise();order,row=struct.unpack('<2H',o.u.mem_read(ctx+12,4));marker=o.u.mem_read(ctx+25,1)[0];key=(order,row)
 if marker and key in first:start=first[key];end=tick;break
 if key not in first:first[key]=tick
 blocks.append(pcm);states.append(key)
assert end is not None and start is not None,(song,len(blocks));out=ROOT/'android/app/src/main/assets/frontend';resources=[]
for name,data in [('menu_intro.wav',b''.join(blocks[:start])),('menu_loop.wav',b''.join(blocks[start:end]))]:
 # MusicPcm accepts empty intro, while loop must be nonempty.
 p=out/name
 with wave.open(str(p),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(o.rate);w.writeframes(data)
 resources.append(dict(file=name,samples=len(data)//2,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
report=dict(song_address=hex(song),source='menu factories080083FE/08008492 load[0804B6E0], same source track for books/chapters',start_tick=start,end_tick=end,sample_rate=o.rate,resources=resources,rom_sha256=r.sha256,device_tested=False);(ROOT/'docs/menu_music_resources.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
