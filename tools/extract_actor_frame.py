#!/usr/bin/env python3
"""Export original actor update chain and recovered surface construction."""
import argparse,json
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
from extract import Rom
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();r=Rom(a.rom);c=Cs(CS_ARCH_ARM,CS_MODE_THUMB);c.skipdata=True;lines=[]
 for start,end in [(0xd438,0xd484),(0xd484,0xd5e0),(0xd1e8,0xd24c),(0x18208,0x18328),(0x3d80,0x3ec4),(0x3fb0,0x4098),(0xef8c,0xefe4),(0xefe4,0xf00c),(0x4ce4,0x4e94),(0x18328,0x18408),(0x18968,0x18988),(0x16960,0x169ac)]:
  lines.append(f'; range 0x{start:06X}..0x{end:06X}; literal pools may decode as instructions')
  lines.extend(f'{i.address:08x}: {i.mnemonic} {i.op_str}' for i in c.disasm(r.data[start:end],0x08000000+start))
 (ROOT/'docs/original_actor_frame.asm').write_text('\n'.join(lines)+'\n')
 info={'original_actor_update':'0x0800D484','base_update':'0x08018208','physics_update':'0x08003D80','phases':['animation 0x0801682C','animation timer 0x08018870','motion vtable slot 0x68','dynamic/static contacts 0x08003FB0','record movement delta / previous center','contact response vtable slot 0x70','behavior vtable slot 0x78','body update vtable slot 0x80'],'contact_response':'0x0800EFE4','dynamic_surface_builder':'0x08004CE4','surface_limit':16,'surface_emission_order':['top type3','left type2','right type1','bottom type5'],'sprite_anchor':'0x08018328','grounded_height_adjustment':'0x0800403C','animation_restart':'0x08016960','world_dimensions_unit':'Q8','scope':'Actor-local update order; whole-world iteration, messages, dynamic contact response and actor selection remain incomplete.'}
 (ROOT/'docs/actor_frame_map.json').write_text(json.dumps(info,indent=2)+'\n');print(json.dumps({'phases':len(info['phases']),'surface_limit':16}))
if __name__=='__main__':main()
