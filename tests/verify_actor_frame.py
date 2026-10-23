#!/usr/bin/env python3
"""Original Thumb fixtures: contacts, dynamic surfaces, anchor and frame order."""
import argparse,ctypes,itertools,json,random,struct,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from extract import Rom,ROM_BASE
from extract_collision import scene_collision

def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();r=Rom(a.rom);u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
 u.mem_map(ROM_BASE,len(r.data));u.mem_write(ROM_BASE,r.data);u.mem_map(0x02000000,0x40000);u.mem_write(0x02000000,r.data[0x708bdc:0x70b990]);u.mem_map(0x03000000,0x2000);u.mem_write(0x03000000,r.data[0x707dd8:0x708bdc])
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));ip=ctypes.POINTER(ctypes.c_int32)
 contact=lib.s2_contact_actions;contact.argtypes=[ctypes.c_int,ip,ip,ip];contact.restype=ctypes.c_int
 surfaces=lib.s2_dynamic_surfaces;surfaces.argtypes=[ip,ctypes.c_int,ctypes.c_int,ip,ip,ctypes.c_int,ip];surfaces.restype=ctypes.c_int
 anchor=lib.s2_actor_anchor_q8;anchor.argtypes=[ip,ip,ctypes.c_int,ctypes.c_int,ip];anchor.restype=None
 boundsfn=lib.s2_sprite_bounds;boundsfn.argtypes=[ctypes.c_char_p,ctypes.c_int,ip];boundsfn.restype=ctypes.c_int
 move=lib.s2_actor_move_file;move.argtypes=[ctypes.c_char_p,ip,ip,ip,ip,ctypes.c_int,ctypes.c_int,ctypes.c_int,ip,ip];move.restype=ctypes.c_int
 actor=0x02004000;component=0x02008000;sprite=0x02009000;svtable=0x02009100;surfaceList=0x0200a000;heap=0x02010000;mode='contacts';actions=[];trace=[];draw=None
 def hook(uc,address,size,data):
  nonlocal heap,draw
  ret=None
  if mode=='contacts':
   if address in [0x03001100,0x03001120]:
    slot=0x1d0 if address==0x03001100 else 0x178;actions.append(slot);uc.mem_write(actor+0x1d8,struct.pack('<i',4 if slot==0x1d0 else 5));ret=0
  elif mode=='surfaces' and address==0x0801bc5c:
   ret=heap;size=uc.reg_read(UC_ARM_REG_R0);uc.mem_write(heap,bytes(size));heap+=size
  elif mode=='anchor':
   if address in [0x08015030,0x0801501c]:ret=0
   elif address==0x03001140:
    draw=struct.unpack('<2i',uc.mem_read(uc.reg_read(UC_ARM_REG_R1),8));ret=0
  elif mode=='frame':
   names={0x0801682c:'animation',0x08018870:'timer',0x0800518c:'motion_callback',0x0800b96c:'integrate',0x08004098:'static_contacts',0x03001160:'contact_response',0x03001180:'behavior',0x030011a0:'body_update'}
   if address in names:trace.append(names[address])
   if address in [0x0801682c,0x08018870,0x03001160,0x03001180,0x030011a0]:ret=0
   elif address==0x08018928:
    pos=struct.unpack('<2i',uc.mem_read(actor+0x178,8));w,h=uc.mem_read(actor+0x174,2);uc.mem_write(uc.reg_read(UC_ARM_REG_R0),struct.pack('<4i',pos[0]-w*128,pos[1]-h*128,w*256,h*256));ret=0
   elif address==0x080007e0:ret=0 # off-screen fixture skips presentation priority
  if ret is not None:uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 def run(addr,r1=0):
  u.reg_write(UC_ARM_REG_R0,actor);u.reg_write(UC_ARM_REG_R1,r1);u.reg_write(UC_ARM_REG_SP,0x0203f000);u.reg_write(UC_ARM_REG_LR,0x03001001);u.emu_start(addr|1,0x03001000,count=300000)
  if u.reg_read(UC_ARM_REG_PC)!=0x03001000:raise AssertionError('Original did not return')
 def setup():
  u.mem_write(actor,bytes(0x400));u.mem_write(actor,struct.pack('<I',0x020017cc));u.mem_write(actor+0x1bc,struct.pack('<I',component));u.mem_write(actor+0x1c0,struct.pack('<I',sprite));u.mem_write(sprite,bytes(0x40));u.mem_write(sprite+0x2c,struct.pack('<I',svtable));u.mem_write(svtable+0x10,struct.pack('<2I',0,0x03001141))
 for off,ptr in [(0x1d0,0x03001101),(0x178,0x03001121)]:u.mem_write(0x020017cc+off+4,struct.pack('<I',ptr))
 contacts=0
 for state,sm,dm in itertools.product(range(18),range(16),range(16)):
  setup();stat=[(sm>>i)&1 for i in range(4)];dyn=[(dm>>i)&1 for i in range(4)];u.mem_write(actor+0xa8,struct.pack('<4i',*stat));u.mem_write(actor+0x14c,struct.pack('<4i',*dyn));u.mem_write(actor+0x1d8,struct.pack('<i',state));actions=[];run(0x0800efe4);out=(ctypes.c_int32*2)();n=contact(state,(ctypes.c_int32*4)(*stat),(ctypes.c_int32*4)(*dyn),out)
  assert list(out[:n])==actions,(state,sm,dm,list(out[:n]),actions);contacts+=1
 mode='surfaces';rng=random.Random(202606);surfaceCases=0
 for flags,existing in itertools.product(range(64),[0,13,14,15,16]):
  for _ in range(12):
   setup();heap=0x02010000;pos=[rng.randint(-1000000,1000000) for _ in range(2)];w,h=rng.randint(0,255),rng.randint(0,255);delta=[rng.randint(-10000,10000) for _ in range(2)];u.mem_write(actor+0x174,bytes([w,h]));u.mem_write(actor+0x178,struct.pack('<2i',*pos));u.mem_write(actor+0x188,struct.pack('<2i',*delta));u.mem_write(actor+0x15d,bytes([flags]));u.mem_write(surfaceList,bytes(0x100));u.mem_write(surfaceList+0x90,struct.pack('<i',existing));run(0x08004ce4,surfaceList)
   n=struct.unpack('<i',u.mem_read(surfaceList+0x90,4))[0]-existing;expected=[]
   for i in range(existing,existing+n):
    ptr,owner=struct.unpack('<2I',u.mem_read(surfaceList+i*8,8));assert owner==actor;values=list(struct.unpack('<6i',u.mem_read(ptr,24)));aux=values.pop();expected.extend(values+[bool(aux)]+(list(struct.unpack('<2i',u.mem_read(aux,8)))+[u.mem_read(aux+8,1)[0]] if aux else [0,0,0]))
   out=(ctypes.c_int32*36)();nf=(ctypes.c_int32*1)(flags);count=surfaces((ctypes.c_int32*2)(*pos),w,h,nf,(ctypes.c_int32*2)(*delta),existing,out)
   assert count==n and list(out[:count*9])==expected and nf[0]==u.mem_read(actor+0x15d,1)[0],(flags,existing,expected,list(out[:count*9]));surfaceCases+=1
 mode='anchor';anchorCases=0;bank=json.loads((ROOT/'sprites/shrek_ogre/bank.json').read_text());sp=str(ROOT/'sprites/shrek_ogre/bank.s2sp').encode();u.mem_write(0x20031e8,struct.pack('<I',0x0200b000));u.mem_write(0x0200b000+8,struct.pack('<2i',0,256))
 for a in bank['animations']:
  b=a['bounds'];nb=(ctypes.c_int32*4)();assert boundsfn(sp,a['index'],nb)==0 and list(nb)==b
  for fx,fy in itertools.product(range(2),repeat=2):
   for _ in range(10):
    setup();pos=[rng.randint(-1000000,1000000) for _ in range(2)];u.mem_write(actor+0x170,struct.pack('<hhBBH',*b,0));u.mem_write(actor+0x178,struct.pack('<2i',*pos));u.mem_write(sprite+0x28,bytes([fx,fy]));draw=None;run(0x08018328);out=(ctypes.c_int32*2)();anchor(nb,(ctypes.c_int32*2)(*pos),fx,fy,out)
    assert tuple(x>>8 for x in out)==draw,(b,pos,fx,fy,list(out),draw);anchorCases+=1
 preserve=lib.s2_preserve_bottom;preserve.argtypes=[ctypes.c_int,ip,ctypes.c_int,ip];preserve.restype=None
 mode='body';bodyCases=0
 for ground,oldh,newh in itertools.product([0,1,3,4],[16,32,50,64],[16,32,50,64]):
  for _ in range(12):
   setup();pos=[rng.randint(-1000000,1000000) for _ in range(2)];old=[pos[0]-2048,pos[1]-oldh*128+1024,4096,oldh*256];u.mem_write(actor+0x174,bytes([16,newh]));u.mem_write(actor+0x178,struct.pack('<2i',*pos));u.mem_write(actor+0x190,struct.pack('<4i',*old));u.mem_write(actor+0x16c,struct.pack('<i',ground));run(0x0800403c);out=(ctypes.c_int32*2)(*pos);preserve(ground,(ctypes.c_int32*4)(*old),newh,out);assert tuple(out)==struct.unpack('<2i',u.mem_read(actor+0x178,8));bodyCases+=1
 restart=lib.s2_animation_restart;restart.argtypes=[ctypes.c_int]*4+[ip];restart.restype=None;restartCases=0;mode='restart'
 for _ in range(1000):
  setup();rate=rng.randint(0,255);count=rng.randint(1,255);direction=rng.choice([-1,0,1,2,3]);tick=rng.randint(-1000000,1000000);initial=[1,1,rng.randint(0,count-1),rng.randint(-1000,1000)];u.mem_write(actor,struct.pack('<5i',initial[0],initial[1],0x0200c000,initial[2],initial[3]));u.mem_write(0x0200c000,bytes(24));u.mem_write(0x0200c000+20,bytes([rate,count]));u.mem_write(0x0200324c,struct.pack('<i',tick));u.reg_write(UC_ARM_REG_R2,direction&0xffffffff);run(0x08016960,0x0200c000);raw=struct.unpack('<5i',u.mem_read(actor,20));expected=[raw[0],raw[1],raw[3],raw[4]];out=(ctypes.c_int32*4)(*initial);restart(rate,count,direction,tick,out);assert list(out)==expected;restartCases+=1
 mode='frame';frameCases=0
 for off,ptr in [(0x70,0x03001161),(0x78,0x03001181),(0x80,0x030011a1)]:u.mem_write(0x020017cc+off+4,struct.pack('<I',ptr))
 expectedTrace=['animation','timer','motion_callback','integrate','static_contacts','contact_response','behavior','body_update']
 for scene in range(30):
  d=scene_collision(r,scene);u.mem_write(0x02000800,struct.pack('<I',ROM_BASE+d['root_offset']));u.mem_write(0x02003254,struct.pack('<I',0x02000800));path=str(ROOT/f'collision/scene_{scene:02d}/scene.s2cl').encode();points=[]
  for seg in d['segments']:
   x1,y1,x2,y2=seg['endpoints'];kind=seg['type'];pos=[(x1+x2)*128,(y1+y2)*128];w,h=16,50
   if kind in [3,4]:pos[1]-=h*128+256
   elif kind==5:pos[1]+=h*128+256
   elif kind==1:pos[0]+=w*128+256
   elif kind==2:pos[0]-=w*128+256
   points.append(pos)
  for pos in points[:120]:
   setup();values=[0,0,0,rng.randint(-1200,1200),0,0,256,49,1792,rng.randint(-1200,1200),49,1792];old=[pos[0]-16*128,pos[1]-50*128,16*256,50*256];prev=[pos[0]+rng.randint(-500,500),pos[1]+rng.randint(-500,500)];u.mem_write(component,struct.pack('<12i',*values));u.mem_write(actor+0x174,bytes([16,50]));u.mem_write(actor+0x178,struct.pack('<2i',*pos));u.mem_write(actor+0x180,struct.pack('<2i',*prev));u.mem_write(actor+0x190,struct.pack('<4i',*old));u.mem_write(actor+0x15c,bytes([2]));trace=[];run(0x08018208)
   assert trace==expectedTrace,trace
   p=(ctypes.c_int32*12)(*values);xy=(ctypes.c_int32*2)(*pos);rect=(ctypes.c_int32*4)(*old);prevpos=(ctypes.c_int32*2)(*prev);counts=(ctypes.c_int32*4)();delta=(ctypes.c_int32*2)();ground=move(path,p,xy,rect,prevpos,16,50,2,counts,delta)
   for native,off,length in [(p,0,12),(xy,0x178,2),(rect,0x190,4),(prevpos,0x180,2),(counts,0xa8,4),(delta,0x188,2)]:
    expect=struct.unpack('<'+'i'*length,u.mem_read(component if off==0 else actor+off,length*4));assert tuple(native)==expect,(scene,hex(off),tuple(native),expect)
   assert ground==struct.unpack('<i',u.mem_read(actor+0x16c,4))[0];frameCases+=1
 result={'contact_dispatch_cases':contacts,'dynamic_surface_cases':surfaceCases,'anchor_cases':anchorCases,'bottom_preservation_cases':bodyCases,'animation_restart_cases':restartCases,'frame_cases':frameCases,'mismatches':0,'frame_order':expectedTrace,'scope':'Original actor base update and static-world motion/contact path; animation/timer, post-contact/behavior/body callbacks and camera presentation are fixtures. Dynamic surface allocator mocked; normalized segments/aux data compared. No complete world scheduler or dynamic actor collision response.'}
 (ROOT/'docs/actor_frame_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
