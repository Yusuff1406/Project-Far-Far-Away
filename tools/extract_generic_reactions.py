#!/usr/bin/env python3
"""Record original reaction routes, including overlapping broadcast storage."""
import argparse,json
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
from pathlib import Path
from extract import Rom,ROM_BASE
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('rom');a=p.parse_args();r=Rom(a.rom);c=Cs(CS_ARCH_ARM,CS_MODE_THUMB);c.skipdata=True;lines=[]
 for x,y in [(0x14878,0x14994),(0x13a54,0x13b2c),(0x13b8c,0x13c64),(0x13d9c,0x13dec),(0x141b4,0x1434c)]:
  lines.append(f'; {x:06x}..{y:06x}; literal pools may decode as instructions');lines.extend(f'{i.address:08x}: {i.mnemonic} {i.op_str}' for i in c.disasm(r.data[x:y],ROM_BASE+x))
 (ROOT/'docs/original_generic_reactions.asm').write_text('\n'.join(lines)+'\n')
 data={'handler':0x08013b8c,'activation':0x08013a54,'local_table':0x1d0,'local_count':0x250,'local_capacity':16,'broadcast_table':0x258,'broadcast_count':0x298,'safe_broadcast_capacity':8,'original_broadcast_capacity_check':16,'last_activation_payload':0x2a0,'last_activation_class':0x2a4,'guard_byte':0x254,'tag_word':0x164,'scope':'Original field addresses. Ninth broadcast entry overlaps count/neighbor fields; normalized runtime rejects an additional listener before mutation. Actual overlap execution is recorded by verify_generic_reactions.py.'};(ROOT/'docs/generic_reaction_layout.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data,indent=2))
if __name__=='__main__':main()
