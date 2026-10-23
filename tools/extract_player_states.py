#!/usr/bin/env python3
"""Export recovered locomotion entry/update slots and source disassembly."""
import argparse,json,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
from extract import Rom
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();r=Rom(a.rom);base=0x708bdc+0x17cc
 slots={f'0x{slot:03X}':{'this_adjust':struct.unpack_from('<h',r.data,base+slot)[0],'thumb_function':f'0x{struct.unpack_from("<I",r.data,base+slot+4)[0]:08X}'} for slot in range(0xd0,0x1e0,8)}
 info={'vtable':'0x020017CC','vtable_rom_offset':base,'slots':slots,'logical_states':{'0':'idle','1':'walk','2':'rise','3':'apex','4':'fall','5':'landing'},'rise_to_apex_velocity_q8':struct.unpack_from('<i',r.data,0x4b6ec)[0],'apex_to_fall_velocity_q8':struct.unpack_from('<i',r.data,0x4b6f0)[0],'scope':'Locomotion subset. Logical state differs from motion-table ID. Remaining callback names not asserted.'}
 (ROOT/'docs/player_state_map.json').write_text(json.dumps(info,indent=2)+'\n')
 c=Cs(CS_ARCH_ARM,CS_MODE_THUMB);c.skipdata=True;lines=[]
 for a,b in [(0xd0a4,0xd170),(0xd5e0,0xd8cc),(0xda7c,0xdc4a),(0xdcf8,0xdd74),(0xdf9c,0xdffc),(0xf00c,0xf1d0),(0xf368,0xf440),(0xf600,0xf60c)]:
  lines.append(f'; range 0x{a:06X}..0x{b:06X} (literal pools may decode as instructions)')
  lines.extend(f'{i.address:08x}: {i.mnemonic} {i.op_str}' for i in c.disasm(r.data[a:b],0x08000000+a))
 (ROOT/'docs/original_player_states.asm').write_text('\n'.join(lines)+'\n')
 print(json.dumps({'slots':len(slots),'states':6,'rise_to_apex_q8':info['rise_to_apex_velocity_q8']}))
if __name__=='__main__':main()
