#!/usr/bin/env python3
"""Hash-locked carry tail, detach/throw, bitmap and flashing constants."""
import argparse,json,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
from extract import Rom,ROM_BASE
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();r=Rom(a.rom)
 def ptr(off):return struct.unpack_from('<I',r.data,off)[0]
 def words(addr,n):return list(struct.unpack_from('<'+'i'*n,r.data,addr-ROM_BASE))
 result={'carry_tail_entry':0x0800d4b8,'detach_entry':0x0800dc5c,'throw_entry':0x0800ea98,'mark_removed_entry':0x08005168,'bitmap_set_entry':0x08009cc0,'bitmap_pointer_global':ptr(0x9ce0),'instance_id_offset':0x160,'pending_removal_flag_mask':1,'same_height_modes':[4,5,7],'position_delta_divisor':4,'detach_event_actor_offset':0x234,'detach_mode_jump_targets':list(struct.unpack_from('<8I',r.data,0xdc88)),'throw_event':words(ptr(0xead0),3),'idle_animation':ptr(0xea24),'action_animation':ptr(0xea28),'flashing_period_address':ptr(0xd5d8),'flashing_period':words(ptr(0xd5d8),1)[0],'flashing_sound_address':ptr(0xd5dc),'flashing_sound':words(ptr(0xd5dc),3),'next_sound_tick_offset':0x208,'flashing_byte_offset':0x1c8,'scope':'Selected carry tail after actor update, local detach/throw, pending-removal bitmap and mode6 callback integration. Full subtype scripts, player entry states and world destructor/unregistration remain separate.'}
 assert result['throw_event']==[0,29,0] and result['flashing_period']==40 and result['idle_animation']==0x08342dcc and result['action_animation']==0x08342db4
 (ROOT/'docs/shrek_carry_layout.json').write_text(json.dumps(result,indent=2)+'\n');c=Cs(CS_ARCH_ARM,CS_MODE_THUMB);c.skipdata=True;lines=[]
 for x,y in [(0xd484,0xd5e0),(0xdc5c,0xdcf8),(0xe788,0xe9ec),(0xe9ec,0xeaec),(0xed6c,0xee20),(0x5168,0x518c),(0x9cc0,0x9ce4)]:
  lines.append(f'; {x:06x}..{y:06x}; literal pools may decode as instructions');lines.extend(f'{i.address:08x}: {i.mnemonic} {i.op_str}' for i in c.disasm(r.data[x:y],ROM_BASE+x))
 (ROOT/'docs/original_shrek_carry.asm').write_text('\n'.join(lines)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
