#!/usr/bin/env python3
"""Hash-locked ogre event defaults and incoming dispatcher constants."""
import argparse,json,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
from extract import Rom,ROM_BASE
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');args=ap.parse_args();r=Rom(args.rom)
 def ptr(off):return struct.unpack_from('<I',r.data,off)[0]
 rows=[]
 for off,lit in [(0x210,0xd290),(0x21c,0xd420),(0x228,0xd424),(0x234,0xd428),(0x240,0xd42c),(0x24c,0xd430)]:
  address=ptr(lit);rows.append({'actor_offset':off,'resource_address':address,'event':list(struct.unpack_from('<3i',r.data,address-ROM_BASE))})
 assert [x['event'] for x in rows]==[[1,0,0],[0,8,0],[1,7,0],[0,11,0],[0,12,0],[0,4,0]]
 deadline=struct.unpack_from('<i',r.data,ptr(0xe6d4)-ROM_BASE)[0];assert deadline==2147483647
 result={'ogre_ctor':0x0800d24c,'shared_shrek_ctor':0x0800d294,'incoming_handler':0x0800e3a0,'event_defaults':rows,'base_event_offset':0x1a0,'base_event':[1,0,0],'incoming_jump_table':[{'id':id,'entry':entry} for id,entry in enumerate(struct.unpack_from('<27I',r.data,0xe3e0),15)],'carry_reply_modes':{'15':6,'16':2,'17':3,'18':1,'19':7,'20':4,'21':5},'event20_deadline':deadline,'event21_byte_offset':0x1c8,'event25_byte_offset':0x20c,'maximum_counter_offset':0x200,'current_counter_offset':0x1fc,'counter_descriptor_byte_offset':0x15,'scope':'Selected constructor effects and local incoming mutations. Later virtual action methods, carry release, broadcasts and full actor lifecycle remain separate.'}
 (ROOT/'docs/shrek_reaction_layout.json').write_text(json.dumps(result,indent=2)+'\n')
 c=Cs(CS_ARCH_ARM,CS_MODE_THUMB);c.skipdata=True;lines=[]
 for x,y in [(0xd24c,0xd43c),(0xe3a0,0xe788),(0xeb1c,0xebc0),(0xfb80,0xfba0)]:
  lines.append(f'; {x:06x}..{y:06x}; literal pools may decode as instructions');lines.extend(f'{i.address:08x}: {i.mnemonic} {i.op_str}' for i in c.disasm(r.data[x:y],ROM_BASE+x))
 (ROOT/'docs/original_shrek_reactions.asm').write_text('\n'.join(lines)+'\n');print(json.dumps({'event_defaults':rows,'event20_deadline':deadline,'event21_byte_offset':0x1c8},indent=2))
if __name__=='__main__':main()
