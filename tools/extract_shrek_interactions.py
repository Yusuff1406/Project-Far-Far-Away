#!/usr/bin/env python3
"""Hash-locked original Shrek pair routes and their event constants."""
import argparse,json,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
from extract import Rom,ROM_BASE
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();r=Rom(a.rom)
 def literal(off):return struct.unpack_from('<I',r.data,off)[0]
 def words(addr,n):return list(struct.unpack_from('<'+'i'*n,r.data,addr-ROM_BASE))
 result={'pair_entry':0x0800e788,'outgoing_entry':0x0800ebc0,'foot_event_getter':0x0800eaec,'foot_event_actor_offset':0x21c,'logical_state_offset':0x1d8,'mode_offset':0x258,'carried_actor_offset':0x1ec,'delta_y_offset':0x18c,'target_category_offset':0x168,'side_strip_width_q8':1024,'left_event':words(literal(0xe9e4),3),'right_event':words(literal(0xe9e8),3),'unported_mode6_expand_xy_q8':words(literal(0xe9d8),2),'unported_mode6_event':words(literal(0xe9dc),3),'scope':'Selected outgoing Shrek routes to stable generic targets; foot and base event defaults are caller supplied, not inferred from this handler.'}
 assert result['left_event']==[0,6,2] and result['right_event']==[0,6,1]
 assert r.data[0xeaec:0xeaf4]==bytes.fromhex('8721890040187047')
 c=Cs(CS_ARCH_ARM,CS_MODE_THUMB);c.skipdata=True;lines=[]
 for x,y in [(0xe788,0xe9ec),(0xeaec,0xeaf4),(0xebc0,0xec04)]:
  lines.append(f'; {x:06x}..{y:06x}; literal pools may decode as instructions');lines.extend(f'{i.address:08x}: {i.mnemonic} {i.op_str}' for i in c.disasm(r.data[x:y],ROM_BASE+x))
 (ROOT/'docs/original_shrek_interactions.asm').write_text('\n'.join(lines)+'\n');(ROOT/'docs/shrek_interaction_layout.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
