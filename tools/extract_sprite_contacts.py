#!/usr/bin/env python3
"""Export current-frame contact metadata/resources without executable ROM code."""
import argparse,json,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
from extract import Rom,ROM_BASE
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('rom');a=p.parse_args();r=Rom(a.rom);blocks={};frames=[];boxes=[0,0]
 def put(address,size):
  if not size:return
  assert ROM_BASE<=address and address+size<=ROM_BASE+len(r.data)
  key=str(address);raw=r.data[address-ROM_BASE:address-ROM_BASE+size];old=blocks.get(key)
  if old is None or len(bytes.fromhex(old))<size:blocks[key]=raw.hex()
 for path in sorted((ROOT/'sprites').glob('*/bank.json')):
  bank=json.loads(path.read_text());put(ROM_BASE+bank['root_offset'],8)
  for anim in bank['animations']:put(ROM_BASE+anim['sequence_offset'],anim['sequence_count']*2+2)
  for frame in bank['frames']:
   address=ROM_BASE+frame['record_offset'];put(address,44);raw=struct.unpack_from('<11I',r.data,frame['record_offset']);meta=r.data[raw[5]-ROM_BASE:raw[5]-ROM_BASE+8];assert len(meta)==8;put(raw[5],8);put(raw[8],8 if meta[2] else 0);entry={'bank':path.parent.name,'frame_index':frame['index'],'frame_address':address,'defense':[],'attack':[]}
   for which,label in enumerate(['defense','attack']):
    count=meta[which];put(raw[6+which],count*8)
    for i in range(count):
     x,y,w,h,reserved=struct.unpack_from('<hhBBH',r.data,raw[6+which]-ROM_BASE+i*8);entry[label].append([x,y,w,h,reserved]);boxes[which]+=1
   frames.append(entry)
 result={'version':1,'blocks':blocks,'frames':frames,'defense_boxes':boxes[0],'attack_boxes':boxes[1],'scope':'Frame contact metadata bytes 0/1 and corresponding 8-byte box lists, roots and sequences. Sequence records include two following original bytes for 32-bit fetch of a final u16; only low u16 is used. Frame marker byte2 and its first 8-byte attachment rectangle are also exported; other auxiliary metadata is not interpreted.'};(ROOT/'objects/sprite_contact_resources.json').write_text(json.dumps(result,indent=2)+'\n')
 c=Cs(CS_ARCH_ARM,CS_MODE_THUMB);c.skipdata=True;lines=[]
 for x,y in [(0x0708,0x0778),(0x07e0,0x0824),(0x3ec4,0x3fb0),(0x5228,0x52b4),(0x18460,0x186d0),(0x1889c,0x18928)]:
  lines.append(f'; {x:06x}..{y:06x}; literal pools may decode as instructions');lines.extend(f'{i.address:08x}: {i.mnemonic} {i.op_str}' for i in c.disasm(r.data[x:y],ROM_BASE+x))
 (ROOT/'docs/original_actor_interactions.asm').write_text('\n'.join(lines)+'\n');print(json.dumps({'frames':len(frames),'blocks':len(blocks),'defense_boxes':boxes[0],'attack_boxes':boxes[1]}))
if __name__=='__main__':main()
