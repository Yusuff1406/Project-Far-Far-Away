#!/usr/bin/env python3
"""Original command/effect resources required by the selected item action."""
import argparse,json,struct
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
from replay_generic_actor import ROOT
from extract import Rom
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');args=ap.parse_args();r=Rom(args.rom).data;targets=struct.unpack_from('<78I',r,0x13c64);packet=struct.unpack_from('<I',r,0x4d5d4+8)[0];camera=struct.unpack_from('<I',r,0x4d5f8+8)[0]
 report={'handler':0x08013b8c,'command_targets':{str(i):targets[i] for i in [11,46,47,49]},'camera_initializer':0x08000a68,'camera_global':struct.unpack_from('<I',r,0xa7c)[0],'camera_field_offsets':[32,36,40,44,48],'screen_initializer':0x0801af44,'screen_globals':[struct.unpack_from('<I',r,a)[0] for a in [0x1af5c,0x1af60,0x1af64,0x1af68]],'actor_auxiliary_spawn_offset':0x2dc,'carried_action_animation':0x08342db4,'action_rate':r[0x342db4+20],'action_frame_count':r[0x342db4+21],'type77_action_script':0x0804d598,'global_packet_address':packet,'global_packet':list(struct.unpack_from('<4i',r,packet-0x08000000)),'camera_parameters_address':camera,'camera_parameters':list(struct.unpack_from('<3i',r,camera-0x08000000)),'scope':'Resource/function evidence. Effects are initialized/queued; global game handler and camera/fade progression not executed.'};(ROOT/'docs/item_action_layout.json').write_text(json.dumps(report,indent=2)+'\n')
 c=Cs(CS_ARCH_ARM,CS_MODE_THUMB);c.skipdata=True;lines=[]
 for x,y in [(0xa68,0xa80),(0x1af44,0x1af6c),(0x141ac,0x141b4),(0x143e4,0x143fa),(0x146cc,0x146f0),(0x13774,0x13782)]:
  lines.append(f'; {x:06x}..{y:06x}; literal pools may decode as instructions');lines.extend(f'{i.address:08x}: {i.mnemonic} {i.op_str}' for i in c.disasm(r[x:y],0x08000000+x))
 (ROOT/'docs/original_item_world_effects.asm').write_text('\n'.join(lines)+'\n');print(json.dumps({'global_packet':report['global_packet'],'camera_parameters':report['camera_parameters'],'action_animation_ticks':(report['action_rate']+1)*report['action_frame_count']}))
if __name__=='__main__':main()
