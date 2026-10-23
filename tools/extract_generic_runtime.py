#!/usr/bin/env python3
"""Export animation headers required by pointer-based actor commands."""
import argparse,json,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
from extract import Rom,ROM_BASE
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('rom');a=p.parse_args();r=Rom(a.rom);records=[]
 for file in sorted((ROOT/'sprites').glob('*/bank.json')):
  bank=json.loads(file.read_text())
  for animation in bank['animations']:
   off=animation['record_offset'];records.append({'address':ROM_BASE+off,'bank':file.parent.name,'index':animation['index'],'header_hex':r.data[off:off+24].hex()})
 (ROOT/'objects/generic_animation_headers.json').write_text(json.dumps({'version':1,'animations':records,'scope':'24-byte animation records only. Pixel/frame/sequence data live in sprite packages; no executable ROM code.'},indent=2)+'\n')
 table=struct.unpack_from('<78I',r.data,0x13c64);(ROOT/'docs/generic_message_targets.json').write_text(json.dumps({'handler':0x08013b8c,'class':8,'targets':[{'id':i,'address':v} for i,v in enumerate(table)],'scope':'Original jump targets; listing a target does not imply that its behavior has been ported.'},indent=2)+'\n')
 c=Cs(CS_ARCH_ARM,CS_MODE_THUMB);c.skipdata=True;lines=[]
 for x,y in [(0x13b8c,0x13c64),(0x13d9c,0x14698),(0x139b8,0x13b2c),(0x168b4,0x16960)]:
  lines.append(f'; {x:06x}..{y:06x}; literal pools may decode as instructions');lines.extend(f'{i.address:08x}: {i.mnemonic} {i.op_str}' for i in c.disasm(r.data[x:y],ROM_BASE+x))
 (ROOT/'docs/original_generic_messages.asm').write_text('\n'.join(lines)+'\n');print(json.dumps({'animation_headers':len(records),'message_targets':len(table)}))
if __name__=='__main__':main()
