#!/usr/bin/env python3
"""Render scene00 music using the original GAX init/mix/IRQ and loop marker."""
import argparse,hashlib,json,struct,wave,array,sys
from pathlib import Path
from extract_session_sfx import GaxOracle,ROOT
from extract import Rom

def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();rom=Rom(a.rom).data
 # Original 19648 initializes first level at02003710 with scene8028D94.
 # At1966A/1966C it loads the first pointer from804B6C4 into level+1C.
 song=struct.unpack_from('<I',rom,0x4b6c4)[0];assert song==0x0820dc94
 oracle=GaxOracle(rom,rate=31537,song=song);oracle.call(0x0801d428,-1,256);ctx=oracle.word(oracle.manager+0x18);assert oracle.word(ctx)==song
 intro=bytearray();loop=bytearray();loopStart=None;loopEnd=None;orders=[];previousOrder=-1
 for tick in range(24000):
  pcm=oracle.mix_precise()
  order,row=struct.unpack('<2H',oracle.u.mem_read(ctx+0xc,4));marker=oracle.u.mem_read(ctx+0x19,1)[0]
  if order!=previousOrder:orders.append([tick,order,row]);previousOrder=order
  if loopStart is None and order==1 and row==0:loopStart=tick
  if loopStart is not None and marker and order==1 and row==0:loopEnd=tick;break
  (intro if loopStart is None else loop).extend(pcm)
 assert loopStart is not None and loopEnd is not None and len(loop)>10000,(loopStart,loopEnd)
 assert max(loop)-min(loop)>32
 out=ROOT/'android/app/src/main/assets/session/music';out.mkdir(parents=True,exist_ok=True);resources=[]
 for name,pcm in [('scene_00_intro.wav',intro),('scene_00_loop.wav',loop)]:
  p=out/name
  with wave.open(str(p),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(oracle.rate);w.writeframes(pcm)
  resources.append({'file':name,'samples':len(pcm)//2,'seconds':len(pcm)/2/oracle.rate,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 report={'song_address':song,'song_address_hex':hex(song),'level_initializer':'0x08019648 -> level02003710 +1C from [0804B6C4]','music_start_route':'0x080082B2/82BE -> 0x080161B0','loop_start_driver_tick':loopStart,'loop_end_driver_tick':loopEnd,'order_transitions':orders,'sample_rate':oracle.rate,'format':'PCM16LE from precise original mixer accumulator before final8-bit quantization','resources':resources,'rom_sha256':hashlib.sha256(rom).hexdigest(),'scope':'Original music driver rendered offline. Intro separated from loop order1 using original context+19 loop marker. WAV loop may retain sample-phase differences at seam; Android playback, full adaptive music and real-time native mixing not validated.'};(ROOT/'docs/scene_music_resources.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
