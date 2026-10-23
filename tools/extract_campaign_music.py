#!/usr/bin/env python3
"""Offline original GAX compositions for all 30 map descriptors, deduplicated."""
import argparse,json,struct,wave,hashlib
from pathlib import Path
from extract import Rom
from extract_session_sfx import GaxOracle
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();r=Rom(a.rom)
 songs=sorted(set(x['music_song']for x in json.loads((ROOT/'objects/campaign_catalog.json').read_text())['records']));reports=[];out=ROOT/'android/app/src/main/assets/campaign/music';out.mkdir(parents=True,exist_ok=True)
 for song in songs:
  o=GaxOracle(r.data,rate=31537,song=song);o.call(0x0801d428,-1,256);ctx=o.word(o.manager+0x18);blocks=[];first={};start=end=None
  for tick in range(24000):
   pcm=o.mix_precise();order,row=struct.unpack('<2H',o.u.mem_read(ctx+12,4));marker=o.u.mem_read(ctx+25,1)[0];key=(order,row)
   if marker and key in first:start=first[key];end=tick;break
   first.setdefault(key,tick);blocks.append(pcm)
  assert start is not None and end is not None,(hex(song),len(blocks))
  resources=[]
  for suffix,data in [('intro',b''.join(blocks[:start])),('loop',b''.join(blocks[start:end]))]:
   p=out/f'song_{song:08x}_{suffix}.wav'
   with wave.open(str(p),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(o.rate);w.writeframes(data)
   resources.append(dict(file=p.name,samples=len(data)//2,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
  reports.append(dict(song=hex(song),loop_start_tick=start,loop_end_tick=end,resources=resources));print(hex(song),start,end,flush=True)
 (ROOT/'docs/campaign_music_resources.json').write_text(json.dumps(dict(songs=reports,count=len(reports),rom_sha256=r.sha256,device_tested=False),indent=2)+'\n')
if __name__=='__main__':main()
