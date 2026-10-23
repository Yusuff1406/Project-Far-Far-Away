#!/usr/bin/env python3
"""Resolve object parameter indirection and trace original factory dispatch."""
import argparse,json,struct,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
from extract import Rom,ROM_BASE
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();r=Rom(a.rom);u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(ROM_BASE,len(r.data));u.mem_write(ROM_BASE,r.data);u.mem_map(0x02000000,0x40000);u.mem_write(0x02000000,r.data[0x708bdc:0x70b990]);u.mem_map(0x03000000,0x2000)
 callTargets=set()
 for off in range(0x59d8,0x6ef2,2):
  x,y=struct.unpack_from('<2H',r.data,off)
  if x&0xf800==0xf000 and y&0xf800==0xf800:
   imm=((x&0x7ff)<<12)|((y&0x7ff)<<1)
   if imm&0x400000:imm-=0x800000
   target=ROM_BASE+off+4+imm
   if not 0x080059d8<=target<0x08006f08 and target not in [0x0801bc5c,0x080222e0]:callTargets.add(target)
 trace=[];alloc=[]
 def hook(uc,address,size,data):
  ret=None
  if address==0x0801bc5c:alloc.append(uc.reg_read(UC_ARM_REG_R0));uc.mem_write(0x02008000,bytes(0x3000));ret=0x02008000
  elif address in callTargets:
   regs=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];trace.append({'constructor':address,'registers':regs,'stack_words':list(struct.unpack('<8I',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),32)))});ret=0x02008000
  if ret is not None:uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 def run(addr,r0,r1=0,r2=0):
  for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],[r0,r1,r2]):u.reg_write(reg,val)
  u.reg_write(UC_ARM_REG_SP,0x0203f000);u.reg_write(UC_ARM_REG_LR,0x03001001);u.emu_start(addr|1,0x03001000,count=200000);assert u.reg_read(UC_ARM_REG_PC)==0x03001000;return u.reg_read(UC_ARM_REG_R0)
 factory=[];categories=[]
 for typ in range(158):
  category=run(0x080072c0,typ);categories.append(category);trace=[];alloc=[];u.mem_write(0x02005000,struct.pack('<2i',120*256,350*256));u.mem_write(0x02006000,bytes(32));result=run(0x080059d8,typ,0x02005000,0x02006000)
  factory.append({'type':typ,'category':category,'route':struct.unpack_from('<I',r.data,0x5a0c+typ*4)[0],'allocation_bytes':alloc,'calls':trace,'result_fixture':result})
 (ROOT/'docs/object_factory_traces.json').write_text(json.dumps({'scope':'Original dispatch and argument setup; allocator and constructor bodies mocked. RAM resource pointers use relocated startup image, not full resource initialization.','types':factory},indent=2)+'\n')
 banks={}
 for path in (ROOT/'sprites').glob('*/bank.json'):
  bank=json.loads(path.read_text())
  for animation in bank['animations']:banks[animation['record_offset']+ROM_BASE]=(path.parent.name,animation['index'])
 bindings={}
 for row in factory:
  if len(row['calls'])!=1:continue
  call=row['calls'][0]
  if call['constructor'] not in [0x08013714,0x080005b4]:continue
  definition=call['registers'][1]
  if not ROM_BASE<=definition<ROM_BASE+len(r.data):continue
  animation=struct.unpack_from('<I',r.data,definition-ROM_BASE)[0]
  if animation in banks:bindings[row['type']]={'definition':definition,'animation':animation,'bank':banks[animation][0],'index':banks[animation][1]}
 (ROOT/'docs/object_sprite_bindings.json').write_text(json.dumps({'scope':'Factory definition pointer and first animation pointer for generic constructor routes; initial artwork only, no behavior or secondary variants.','types':bindings},indent=2)+'\n')
 header='// Generated from original 0x080072C0; do not infer category names.\nstatic constexpr int object_categories[158]={'+','.join(map(str,categories))+'};\n';(ROOT/'native/object_categories.inc').write_text(header)
 total=0;outroot=ROOT/'objects';outroot.mkdir(exist_ok=True)
 for n in range(30):
  desc=struct.unpack_from('<8I',r.data,0x28d94+n*32)[6]-ROM_BASE;count,records,offsets,pool,extra,reserved=struct.unpack_from('<6I',r.data,desc);count&=65535;rows=[];payload=bytearray(b'S2OB'+struct.pack('<3I',1,count,n))
  for i in range(count):
   typ,x,y,index=struct.unpack_from('<4H',r.data,records-ROM_BASE+i*8);delta=struct.unpack_from('<H',r.data,offsets-ROM_BASE+index*2)[0];param=pool+delta;window=r.data[param-ROM_BASE:param-ROM_BASE+32];assert len(window)==32;secondary=struct.unpack_from('<h',window,12)[0];tag=struct.unpack_from('<I',window,8)[0]
   row={'index':i,'instance_id':i+1,'type':typ,'anchor_px':[x,y],'parameter_index':index,'parameter_address':param,'parameter_byte_offset':delta,'parameter_window32_hex':window.hex(),'flags_byte':window[0],'word8_actor_tag':tag,'secondary_type_s16':secondary,'category':categories[typ] if 0<=typ<158 else 11};rows.append(row);payload+=struct.pack('<4H I',typ,x,y,index,param)+window
  path=outroot/f'scene_{n:02d}';path.mkdir(exist_ok=True);(path/'scene.s2ob').write_bytes(payload);(path/'objects.json').write_text(json.dumps({'scene':n,'descriptor_address':ROM_BASE+desc,'parameter_offsets_address':offsets,'parameter_pool_address':pool,'other_pointer':extra,'objects':rows,'scope':'32-byte windows retain neighboring data where the logical parameter block is shorter; block lengths and remaining fields unresolved.'},indent=2)+'\n');total+=count
 c=Cs(CS_ARCH_ARM,CS_MODE_THUMB);c.skipdata=True
 (ROOT/'docs/original_object_spawn.asm').write_text('\n'.join(f'{i.address:08x}: {i.mnemonic} {i.op_str}' for a,b in [(0x59d8,0x5a0c),(0x6ee0,0x7104),(0x72c0,0x757e),(0x9c98,0x9ce4)] for i in c.disasm(r.data[a:b],ROM_BASE+a))+'\n')
 result={'scenes':30,'objects':total,'factory_types_traced':158,'categories':sorted(set(categories)),'scope':'Parameter resolution and route/constructor-call evidence; constructors not implemented.'};(ROOT/'docs/object_extraction_summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
