#!/usr/bin/env python3
"""Hash-locked grab entry/motion record and source disassembly."""
import argparse,json,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
from extract import Rom,ROM_BASE
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();r=Rom(a.rom);table=0x4b73c;row=None
 for i in range(24):
  offset=table+40*i;data=list(struct.unpack_from('<10i',r.data,offset))
  if data[0]==10:row={'address':ROM_BASE+offset,'words':data};break
 assert row and row['words'][1]==0x0834f454
 info={'entry':0x0800f224,'vtable_slot':0x190,'logical_state':8,'grab_event_field':0x240,'default_grab_event':[0,12,0],'old_carry_release_entry':0x0800dc5c,'motion_record':row,'motion_cache_field':0x260,'current_sound_field':0x25c,'x_only_motion_update':True,'type77_script':0x0804d084,'scope':'Canonical ogre motion table with unique record10. Selected entry and item startup/response; full player state8 update and global world management remain separate.'};(ROOT/'docs/shrek_grab_layout.json').write_text(json.dumps(info,indent=2)+'\n')
 c=Cs(CS_ARCH_ARM,CS_MODE_THUMB);c.skipdata=True;lines=[]
 for x,y in [(0xf224,0xf25c),(0xec94,0xed6c),(0x187cc,0x18838)]:
  lines.append(f'; {x:06x}..{y:06x}; literal pools may decode as instructions');lines.extend(f'{i.address:08x}: {i.mnemonic} {i.op_str}' for i in c.disasm(r.data[x:y],ROM_BASE+x))
 (ROOT/'docs/original_shrek_grab.asm').write_text('\n'.join(lines)+'\n');print(json.dumps(info,indent=2))
if __name__=='__main__':main()
