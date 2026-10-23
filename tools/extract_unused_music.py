"""Offline PCM extraction of an original GAX composition outside the scene/menu bindings."""
import sys,struct,json,wave,hashlib
from extract import Rom
from extract_session_sfx import GaxOracle,ROOT
r=Rom(sys.argv[1]);song=int(sys.argv[2],0);o=GaxOracle(r.data,rate=31537,song=song);o.call(0x0801d428,-1,256);ctx=o.word(o.manager+0x18);blocks=[];first={};start=end=None
for tick in range(24000):
 pcm=o.mix_precise();order,row=struct.unpack('<2H',o.u.mem_read(ctx+12,4));marker=o.u.mem_read(ctx+25,1)[0];key=(order,row)
 if marker and key in first:start=first[key];end=tick;break
 first.setdefault(key,tick);blocks.append(pcm)
assert start is not None and end is not None
resources=[]
for suffix,data in [('intro',b''.join(blocks[:start])),('loop',b''.join(blocks[start:end]))]:
 p=ROOT/f'android/app/src/main/assets/campaign/music/song_{song:08x}_{suffix}.wav'
 with wave.open(str(p),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(o.rate);w.writeframes(data)
 resources.append(dict(file=p.name,samples=len(data)//2,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(ROOT/('docs/unused_music_'+hex(song)+'.json')).write_text(json.dumps(dict(song=hex(song),source='GAX song headers absent from map and frontend song bindings',start_tick=start,end_tick=end,resources=resources,rom_sha256=r.sha256),indent=2)+'\n');print('PASS unused music',hex(song),start,end)
