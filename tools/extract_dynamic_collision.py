#!/usr/bin/env python3
import argparse,json
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
from extract import Rom
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();r=Rom(a.rom);c=Cs(CS_ARCH_ARM,CS_MODE_THUMB);c.skipdata=True;lines=[]
 for start,end in [(0x4768,0x4ce4),(0x4f28,0x50b0),(0xbccc,0xbd18),(0xbd60,0xbd84)]:
  lines.append(f'; range 0x{start:06X}..0x{end:06X}; literal pools may decode as instructions')
  lines.extend(f'{i.address:08x}: {i.mnemonic} {i.op_str}' for i in c.disasm(r.data[start:end],0x08000000+start))
 (ROOT/'docs/original_dynamic_collision_and_dispatch.asm').write_text('\n'.join(lines)+'\n')
 info={'dynamic_resolution':'0x08004768','actor_dynamic_list_offset':'0xB8','actor_dynamic_count_offset':'0x148','accepted_surface_flags_offset':'0x138','dynamic_contact_counters_offset':'0x14C','pass_order':['ceiling5','floor3','left1','right2'],'sweep_rectangles':'Computed from initial current body rectangle and previous rectangle; unchanged across passes. Projection uses position corrected by earlier contacts.','floor_carriage':'Adds both Q8 displacement components from auxiliary payload after floor correction.','normalized_surface_words':['x1','y1','x2','y2','type','aux_present','delta_x_q8','delta_y_q8','aux_flag'],'probe':'0x08004BE0 static first, then actor dynamic list','broadcast':'0x0800BCF0','broadcast_scope':'Stable listener list; all callbacks invoked, return ignored.','pending_add':'0x0800BCCC','pending_run':'0x0800BC94','pending_capacity':8,'pending_virtual_slot':'0x20','scope':'No original object discovery, mutable receiver list or concrete level event handlers.'}
 (ROOT/'docs/dynamic_collision_map.json').write_text(json.dumps(info,indent=2)+'\n');print(json.dumps({'passes':4,'pending_capacity':8}))
if __name__=='__main__':main()
