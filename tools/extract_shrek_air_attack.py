#!/usr/bin/env python3
"""Confirm ogre attack frames have no projectile marker; retain branch evidence."""
import argparse,json,struct
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
from replay_generic_actor import ROOT
from extract import Rom
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');args=ap.parse_args();rom=Rom(args.rom);r=rom.data;frames=[]
 for animation in [0x0834f304,0x0834f31c]:
  root,seq=struct.unpack_from('<2I',r,animation-0x08000000);frameTable=struct.unpack_from('<I',r,root-0x08000000+4)[0];count=r[animation-0x08000000+21]
  for i in range(count):
   index=struct.unpack_from('<H',r,seq-0x08000000+i*2)[0];address=frameTable+index*44;metadata=struct.unpack_from('<I',r,address-0x08000000+0x14)[0];marker=r[metadata-0x08000000+2];assert marker==0;frames.append({'animation':animation,'sequence':i,'frame_address':address,'metadata':metadata,'spawn_marker':marker})
 thresholds=list(struct.unpack_from('<2i',r,0x4b6ec));assert thresholds==[-698,0]
 report={'entry':0x0800d1b8,'behavior_wrapper':0x0800d1e8,'state16_behavior':0x0800cf8c,'delta_y_offset':0x18c,'thresholds_q8':thresholds,'pending_byte_20c':'preserved by CF8C','ogre_frames':frames,'other_forms_projectile_handler':0x0800ced4,'scope':'Ogre motion8/9 only; other forms with spawn markers need an owned projectile backend.'};(ROOT/'docs/shrek_air_attack_layout.json').write_text(json.dumps(report,indent=2)+'\n')
 c=Cs(CS_ARCH_ARM,CS_MODE_THUMB);c.skipdata=True;lines=[]
 for x,y in [(0xd1b8,0xd24c),(0xcf8c,0xd05c),(0xced4,0xcf8c),(0x169cc,0x169e8)]:
  lines.append(f'; {x:06x}..{y:06x}; literal pools may decode as instructions');lines.extend(f'{i.address:08x}: {i.mnemonic} {i.op_str}' for i in c.disasm(r[x:y],0x08000000+x))
 (ROOT/'docs/original_shrek_air_attack.asm').write_text('\n'.join(lines)+'\n');print(json.dumps({'frames_without_spawn_marker':len(frames),'thresholds_q8':thresholds}))
if __name__=='__main__':main()
