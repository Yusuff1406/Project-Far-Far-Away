#!/usr/bin/env python3
"""Record world query/sweep entry points and data layout from hash-locked ROM."""
import argparse,json,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
from extract import Rom,ROM_BASE
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('rom');a=p.parse_args();r=Rom(a.rom);result={'world_pointer_global':struct.unpack_from('<I',r.data,0x75f4)[0],'nearest_entry':0x08007580,'nearest_category_jump_targets':list(struct.unpack_from('<12I',r.data,0x75a4)),'native_nearest_list_slots':[4,8,12,16,24,20,28,28,32,36],'excluded_distance_sentinel':struct.unpack_from('<I',r.data,0x76bc)[0],'endpoint_pointer_global':struct.unpack_from('<I',r.data,0x15c8c)[0],'endpoint_count_global':struct.unpack_from('<I',r.data,0x15c88)[0],'maximum_endpoint_rows':128,'active_scratch_capacity':16,'active_scratch_address':0x020031f0,'actor_envelope_fields':[0x1ac,0x1b0,0x1b4,0x1b8],'envelope_pad_q8':1024,'scope':'Stable-frame sweep/query routes and supplied generic callback dispatch. Category active/inactive management, full world update, removal/destructor lifecycle and subtype behavior remain separate.'};(ROOT/'docs/world_query_layout.json').write_text(json.dumps(result,indent=2)+'\n')
 c=Cs(CS_ARCH_ARM,CS_MODE_THUMB);c.skipdata=True;lines=[]
 for x,y in [(0x7580,0x76c0),(0x78cc,0x78ec),(0x15c24,0x15f24),(0x15f50,0x15fc0),(0x7d28,0x7d54)]:
  lines.append(f'; {x:06x}..{y:06x}; literal pools may decode as instructions');lines.extend(f'{i.address:08x}: {i.mnemonic} {i.op_str}' for i in c.disasm(r.data[x:y],ROM_BASE+x))
 (ROOT/'docs/original_world_queries.asm').write_text('\n'.join(lines)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
