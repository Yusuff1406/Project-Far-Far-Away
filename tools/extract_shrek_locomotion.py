#!/usr/bin/env python3
"""Hash-locked ogre state8 route and selected locomotion entry fields."""
import argparse,json,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
from extract import Rom,ROM_BASE
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();r=Rom(a.rom);base=0x708bdc+0x17cc;slots={hex(s):struct.unpack_from('<I',r.data,base+s+4)[0] for s in [0x110,0x150,0x158,0x160,0x168,0x170,0x1d0]};assert slots['0x110']==0x0800f1e5
 records=[]
 for i in range(24):
  off=0x4b73c+i*40;v=list(struct.unpack_from('<10i',r.data,off))
  if v[0] in [1,2,3,4,5,14]:records.append({'address':ROM_BASE+off,'words':v})
 info={'ogre_vtable':0x020017cc,'state8_dispatch_jump_target':struct.unpack_from('<I',r.data,0xd604+8*4)[0],'slots':slots,'state8_behavior':0x0800f1e4,'idle_event_offset':0x228,'pending_special_byte':0x20c,'motion_cache_offset':0x260,'current_sound_offset':0x25c,'idle_tick_offset':0x1dc,'saved_y_offset':0x204,'records':records,'state8_exit_condition':'finished-byte != 0 AND (carried-pointer == 0 OR mode != 0)','scope':'Final ogre vtable, not the shared base/form-specific vtable. Selected entry effects and state8 behavior; full per-frame player/world loop remains separate.'};(ROOT/'docs/shrek_locomotion_layout.json').write_text(json.dumps(info,indent=2)+'\n')
 c=Cs(CS_ARCH_ARM,CS_MODE_THUMB);c.skipdata=True;lines=[]
 for x,y in [(0xf1e4,0xf224),(0xf158,0xf1d0),(0xdcf8,0xdd74),(0xf00c,0xf030),(0xf0b8,0xf158),(0xd5e0,0xd6e0)]:
  lines.append(f'; {x:06x}..{y:06x}; literal pools may decode as instructions');lines.extend(f'{i.address:08x}: {i.mnemonic} {i.op_str}' for i in c.disasm(r.data[x:y],ROM_BASE+x))
 (ROOT/'docs/original_shrek_locomotion.asm').write_text('\n'.join(lines)+'\n');print(json.dumps({'slots':slots,'state8_behavior':info['state8_behavior'],'records':len(records)},indent=2))
if __name__=='__main__':main()
