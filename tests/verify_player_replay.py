#!/usr/bin/env python3
"""Compare locomotion trajectories against original Shrek actor update chain."""
import argparse,ctypes,json,struct,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from extract import Rom,ROM_BASE
from extract_collision import scene_collision

def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('--dynamic',action='store_true');ap.add_argument('--native-frame',action='store_true');a=ap.parse_args();r=Rom(a.rom);u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
 u.mem_map(ROM_BASE,len(r.data));u.mem_write(ROM_BASE,r.data);u.mem_map(0x02000000,0x40000);u.mem_write(0x02000000,r.data[0x708bdc:0x70b990]);u.mem_map(0x03000000,0x2000);u.mem_write(0x03000000,r.data[0x707dd8:0x708bdc])
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));ip=ctypes.POINTER(ctypes.c_int32);init=lib.s2_prototype_init;init.argtypes=[ip];init.restype=None;step=lib.s2_prototype_step;step.argtypes=[ctypes.c_char_p,ctypes.c_char_p,ctypes.c_int,ip];step.restype=ctypes.c_int
 if a.native_frame:
  FC=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_uint32,ip,ctypes.c_int,ctypes.c_void_p);SINK=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_int,ctypes.c_uint32,ctypes.c_int32,ctypes.c_void_p);DSP=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_uint32,ip,ctypes.c_void_p)
  @FC
  def fetch(addr,out,n,ctx):
   try:raw=u.mem_read(addr,n*4)
   except Exception:return 0
   for i,v in enumerate(struct.unpack('<'+'i'*n,raw)):out[i]=v
   return 1
  @SINK
  def sink(kind,resource,scale,ctx):return 0
  @DSP
  def dispatch(ident,event,ctx):raise AssertionError('unexpected carry release')
  frame=lib.s2_shrek_player_step_dynamic if a.dynamic else lib.s2_shrek_player_step_empty_dynamic;frame.argtypes=[ctypes.c_char_p,ip,ip,ip,ip,ctypes.c_int,ctypes.c_int32,ctypes.c_int32,ip,ip,ctypes.c_uint32,ctypes.c_uint32,FC,SINK,DSP,ctypes.c_void_p]+([ip,ctypes.c_int] if a.dynamic else [])
 actor=0x02004000;component=0x02008000;sprite=0x02009000;svtable=0x02009100;inputptr=0x02009200;held=0;contactSnapshot=None;contactParts=None
 u.mem_write(svtable+0x18,struct.pack('<2I',0,0x03001101))
 def hook(uc,address,size,data):
  nonlocal contactSnapshot,contactParts
  ret=None
  if address==0x0800efe4:
   stat=struct.unpack('<4i',uc.mem_read(actor+0xa8,16));dyn=struct.unpack('<4i',uc.mem_read(actor+0x14c,16));contactSnapshot=[x+y for x,y in zip(stat,dyn)];contactParts=(list(stat),list(dyn))
  if address==0x0800fadc:ret=held&48
  elif address==0x0800fb2c:ret=inputptr
  elif address==0x03001100:uc.mem_write(sprite+0x28,bytes([uc.reg_read(UC_ARM_REG_R1)&255]));ret=0
  elif address in [0x0800fa4c,0x0800fa10,0x0800f9e8,0x080052b4,0x0801501c,0x0801bc54,0x080163ac]:ret=0
  elif address==0x080007e0:ret=1 # fixture keeps actor active/on screen
  elif address in [0x0800f5bc,0x0800f584]:ret=0 # idle specials outside locomotion scope
  if ret is not None:uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 root=scene_collision(r,0)['root_offset'];u.mem_write(0x02000800,struct.pack('<3I',ROM_BASE+root,3200*256,400*256));u.mem_write(0x02003254,struct.pack('<I',0x02000800));u.mem_write(0x020031e8,struct.pack('<I',0x0200a000));u.mem_write(0x0200a000,bytes(0x40))
 selector=struct.unpack_from('<I',r.data,0xf854)[0];u.mem_write(selector,struct.pack('<i',0))
 cp=str(ROOT/'collision/scene_00/scene.s2cl').encode();sp=str(ROOT/'sprites/shrek_ogre/bank.s2sp').encode();cases=0;scenarioInfo=[]
 scenarios={
 'idle':lambda t:0,
 'right_jumps':lambda t:(0 if t<30 else 16)|(1 if t in [95,170,245,320,395] else 0),
 'left_wall':lambda t:32,
 'turn_and_release':lambda t:16 if t<100 else 0 if t<140 else 32 if t<260 else 16,
 'held_jump':lambda t:1 if 10<=t<130 else 0,
 'both_directions':lambda t:48|(1 if t in [20,150,300] else 0)}
 if a.native_frame:
  scenarios.update({'grab_then_jump':lambda t:4 if t in [40,220] else 1 if t in [100,300] else 16 if 140<=t<180 else 0,'held_grab':lambda t:4 if 10<=t<130 else 0,'grab_during_jump':lambda t:1 if t in [30,230] else 4 if t in [40,80,120,260] else 0})
 if a.native_frame and not a.dynamic:
  scenarios.update({'ground_attacks':lambda t:2 if t in [40,120,200,280,360] else 0,'walk_attacks':lambda t:16|(2 if t in [40,120,200,280,360] else 0),'alternating_attacks':lambda t:(32 if t<240 else 16)|(66 if t in [40,140,280,380] else 0)})
 if a.native_frame and not a.dynamic:
  scenarios.update({'air_attacks_rise':lambda t:(1 if t in [20,170,320] else 0)|(2 if t in [22,172,322] else 0),'air_attacks_apex':lambda t:(1 if t in [20,170,320] else 0)|(66 if t in [40,190,340] else 0),'air_attacks_fall':lambda t:(1 if t in [20,170,320] else 0)|(2 if t in [50,200,350] else 0)})
 if a.dynamic:
  step=lib.s2_prototype_step_dynamic;step.argtypes=[ctypes.c_char_p,ctypes.c_char_p,ctypes.c_int,ip,ip,ctypes.c_int,ip];step.restype=ctypes.c_int
  build=lib.s2_dynamic_surfaces;build.argtypes=[ip,ctypes.c_int,ctypes.c_int,ip,ip,ctypes.c_int,ip];build.restype=ctypes.c_int
  scenarios={'platform_ride':lambda t:0,'platform_jump':lambda t:1 if t in [40,180,320] else 0,'platform_walk_off':lambda t:16 if 30<=t<200 else 0}
 for name,buttons in scenarios.items():
  s=(ctypes.c_int32*40)();init(s);
  if a.dynamic:s[0]=160*256;s[1]=262*256;s[27]=s[1];s[32]=s[0]-2048;s[33]=s[1]-6400;s[36]=s[0];s[37]=s[1]
  u.mem_write(actor,bytes(0x400));u.mem_write(actor,struct.pack('<I',0x020017cc));u.mem_write(actor+0x170,struct.pack('<hhBBH',-11,-24,16,50,0));u.mem_write(actor+0x178,struct.pack('<4i',s[0],s[1],s[0],s[1]));u.mem_write(actor+0x190,struct.pack('<4i',*s[32:36]));u.mem_write(actor+0x1bc,struct.pack('<I',component));u.mem_write(actor+0x1c0,struct.pack('<I',sprite));u.mem_write(actor+0x1e8,struct.pack('<I',0x0804b73c));u.mem_write(actor+0x1d4,bytes([1]));u.mem_write(actor+0x15c,bytes([6 if a.dynamic else 2]));u.mem_write(actor+0xa8,struct.pack('<4i',1,0,0,0));u.mem_write(component,struct.pack('<12i',*s[2:14]));u.mem_write(sprite,bytes(0x40));u.mem_write(sprite+8,struct.pack('<3I',0x0834f25c,0,4));u.mem_write(sprite+0x2c,struct.pack('<I',svtable));u.mem_write(actor+0x204,struct.pack('<i',s[1]));previous=0
  if a.native_frame:
   pose=(ctypes.c_int32*80)();pose[:24]=s[:24];pose[26:28]=[-11,-24];pose[30:38]=s[30:38];pose[40]=6 if a.dynamic else 2;pose[47]=0x0834f25c;pose[72:76]=[-11,-24,16,50];hdr=r.data[0x34f25c:0x34f274];pose[76:79]=list(hdr[20:23]);extra=(ctypes.c_int32*8)();status=(ctypes.c_int32*8)();book=(ctypes.c_int32*8)();book[3]=s[1];events=(ctypes.c_int32*9)(1,7,0,0,12,0,0,11,0);control=(ctypes.c_int32*3)(1,0,0);u.mem_write(actor+0x228,struct.pack('<3i',1,7,0));u.mem_write(actor+0x240,struct.pack('<3i',0,12,0));u.mem_write(actor+0x234,struct.pack('<3i',0,11,0))
  lastX=160
  for tick in range(1,481):
   contactSnapshot=None
   if a.dynamic:
    phase=tick%160;x=160+(phase if phase<=80 else 160-phase)
    delta=(x-lastX)*256;lastX=x;surfaces=(ctypes.c_int32*36)();flags=(ctypes.c_int32*1)(1);n=build((ctypes.c_int32*2)(x*256,292*256),96,8,flags,(ctypes.c_int32*2)(delta,0),0,surfaces);assert n==1
    ptr=0x0200b000;u.mem_write(ptr,struct.pack('<5iI',*surfaces[:5],ptr+24));u.mem_write(ptr+24,struct.pack('<2iB',*surfaces[6:9]));u.mem_write(actor+0xb8,struct.pack('<2I',ptr,0x0200d000));u.mem_write(actor+0x148,struct.pack('<i',1))
   held=buttons(tick-1);pressed=held&~previous;u.mem_write(inputptr,bytes([held])+bytes(7)+bytes([pressed]));u.mem_write(0x0200324c,struct.pack('<i',tick));u.mem_write(0x020033e0,struct.pack('<i',tick));u.reg_write(UC_ARM_REG_R0,actor);u.reg_write(UC_ARM_REG_SP,0x0203f000);u.reg_write(UC_ARM_REG_LR,0x03001001);u.emu_start(0x0800d485,0x03001000,count=500000)
   if u.reg_read(UC_ARM_REG_PC)!=0x03001000:raise AssertionError('Original chain did not return')
   if a.native_frame:
    assert frame(cp,pose,extra,status,book,held,tick,tick,control,events,0x0804b73c,0x0804b708,fetch,sink,dispatch,None,*([surfaces,n] if a.dynamic else []))==0
    assert (list(pose[14:18]),list(pose[64:68]))==contactParts,(name,tick,'contact-parts')
    assert list(pose[60:62])==list(struct.unpack('<2i',u.mem_read(actor+0x188,8))),(name,tick,'delta')
    assert list(pose[36:38])==list(struct.unpack('<2i',u.mem_read(actor+0x180,8))),(name,tick,'previous-center')
    assert list(pose[26:28])+list(pose[30:32])==list(struct.unpack('<hhBB',u.mem_read(actor+0x170,6))),(name,tick,'body')
    s[:24]=pose[:24];s[14:18]=[pose[14+i]+pose[64+i] for i in range(4)];s[26]=extra[0];s[19]=(pose[47]-0x0834f25c)//24;s[32:36]=pose[32:36]
    assert list(pose[41:44])==list(struct.unpack('<3i',u.mem_read(actor+0x1a0,12))),(name,tick,'event')
    assert list(book[:4])==[struct.unpack('<i',u.mem_read(actor+off,4))[0] for off in [0x260,0x25c,0x1dc,0x204]],(name,tick,'book',list(book[:4]))
   else:assert (step(cp,sp,held,s,surfaces,n,(ctypes.c_int32*4)()) if a.dynamic else step(cp,sp,held,s))==0
   expected={ 'position':list(struct.unpack('<2i',u.mem_read(actor+0x178,8))),'motion':list(struct.unpack('<12i',u.mem_read(component,48))),'contacts':contactSnapshot,'facing':u.mem_read(sprite+0x28,1)[0],'state':struct.unpack('<i',u.mem_read(actor+0x1d8,4))[0],'animation':(struct.unpack('<I',u.mem_read(sprite+8,4))[0]-0x0834f25c)//24,'clock':[u.mem_read(sprite,1)[0],struct.unpack('<i',u.mem_read(sprite+4,4))[0],*struct.unpack('<2i',u.mem_read(sprite+12,8))],'previous_rect':list(struct.unpack('<4i',u.mem_read(actor+0x190,16)))}
   actual={'position':list(s[:2]),'motion':list(s[2:14]),'contacts':list(s[14:18]),'facing':s[18],'state':s[26],'animation':s[19],'clock':list(s[20:24]),'previous_rect':list(s[32:36])}
   if actual!=expected:raise AssertionError((name,tick,held,{k:(actual[k],expected[k]) for k in actual if actual[k]!=expected[k]}))
   previous=held;cases+=1
  scenarioInfo.append({'name':name,'ticks':480,'final_position_q8':list(s[:2])})
 result={'original_actor_update':'0x0800D484','native_player_frame':a.native_frame,'ticks_compared':cases,'native_base_events_and_motion_book_compared':a.native_frame,'scenarios':scenarioInfo,'mismatches':0,'scope':'Original actor update, animation, physics, static contacts, locomotion decisions, entry routines and body update execute together. Input, facing setter, camera/on-screen status, character selection/audio and idle-special helpers are fixtures. Dynamic mode uses a supplied moving-platform fixture; no original object discovery or full ROM game loop.'}
 (ROOT/('docs/shrek_player_dynamic_validation.json' if a.native_frame and a.dynamic else 'docs/shrek_player_frame_validation.json' if a.native_frame else 'docs/dynamic_player_replay_validation.json' if a.dynamic else 'docs/player_replay_validation.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
