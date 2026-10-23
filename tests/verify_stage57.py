#!/usr/bin/env python3
"""Physical prop layering/body contact, death lifecycle and source victory timing."""
import ctypes,json,struct,tempfile,sys
from pathlib import Path
from PIL import Image
from session_fixtures import without_intro
from verify_generic_runtime import Original,Rom,FC,IP
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_PC,UC_ARM_REG_LR
ROOT=Path(__file__).resolve().parents[1];I=ctypes.c_int32
SINK=ctypes.CFUNCTYPE(ctypes.c_int,I,ctypes.c_uint32,I,ctypes.c_void_p)
def main():
 r=Rom(sys.argv[1]);l=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));c=l.s2_session_create_level;c.argtypes=[ctypes.c_char_p]*5+[IP];c.restype=ctypes.c_void_p
 for name,args in [('destroy',[ctypes.c_void_p]),('snapshot',[ctypes.c_void_p,IP]),('actor_snapshot',[ctypes.c_void_p,I,IP]),('set_viewport',[ctypes.c_void_p,I,I]),('set_transitions',[ctypes.c_void_p,I]),('player_event',[ctypes.c_void_p,IP]),('health',[ctypes.c_void_p]),('coin_count',[ctypes.c_void_p]),('death_restarts',[ctypes.c_void_p]),('dialogue_active',[ctypes.c_void_p]),('level_complete',[ctypes.c_void_p]),('transition_snapshot',[ctypes.c_void_p,IP]),('requests',[ctypes.c_void_p,IP,ctypes.c_size_t]),('step',[ctypes.c_void_p,I,ctypes.c_void_p,ctypes.c_size_t,IP])]:getattr(l,'s2_session_'+name).argtypes=args
 assets=ROOT/'android/app/src/main/assets/session';paths=[assets/'resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',assets/'sprites'];raw=without_intro((ROOT/'objects/scene_00/scene.s2ob').read_bytes());info=(I*8)();hero=(I*320)();a=(I*216)();tr=(I*8)();err=I();cases=[]
 with tempfile.TemporaryDirectory()as td:
  f=Path(td)/'scene.s2ob'
  def open_(data,w=240):
   f.write_bytes(data);h=c(*[str(p).encode()for p in paths],str(f).encode(),ctypes.byref(err));assert h,err.value;l.s2_session_set_viewport(h,w,160);return h,(ctypes.c_uint32*(w*160))()
  # Body contact before the first spawned pumpkin cannot damage Shrek.
  for w in [240,480]:
   data=bytearray(raw);struct.pack_into('<HH',data,18+30*44,35,350);h,pix=open_(data,w);firstHurt=None;firstSpawn=None
   try:
    for t in range(1,181):
     assert l.s2_session_step(h,0,pix,len(pix),info)==0;l.s2_session_actor_snapshot(h,31,a)
     child=(I*216)();hasChild=l.s2_session_actor_snapshot(h,72,child)==0
     if hasChild and firstSpawn is None:firstSpawn=t
     if l.s2_session_health(h)<6 and firstHurt is None:firstHurt=t
     if not firstSpawn:assert l.s2_session_health(h)==6,(w,t,'peasant body caused damage',a[42])
    assert firstSpawn and firstHurt and firstHurt>firstSpawn,(w,firstSpawn,firstHurt)
    cases.append(dict(kind='peasant',width=w,first_pumpkin=firstSpawn,first_damage=firstHurt))
   finally:l.s2_session_destroy(h)
  for kind in ['water','fall','health','intro_health']:
   for w in [240,480]:
    data=bytearray((ROOT/'objects/scene_00/scene.s2ob').read_bytes()if kind=='intro_health'else raw)
    if kind in ['water','fall']:struct.pack_into('<HH',data,18+69*44,2415 if kind=='water'else 2300,150 if kind=='water'else 340)
    coinId=next(x['instance_id']for x in json.loads((ROOT/'objects/scene_00/objects.json').read_text())['objects']if x['type']==89)
    if kind.endswith('health'):struct.pack_into('<HH',data,18+(coinId-1)*44,35,350)
    h,pix=open_(data,w);l.s2_session_actor_snapshot(h,coinId,a);coinInitial=bytes(a);l.s2_session_set_transitions(h,1);frames=[];death=None;finished=None;restarted=None;black=False;phases=[]
    try:
     for t in range(1,1101):
      b=64 if l.s2_session_dialogue_active(h)else 3 if death else 0
      if kind.endswith('health') and t in [120,240,360,480,600,720]:assert l.s2_session_player_event(h,(I*3)(1,38,1))==1
      assert l.s2_session_step(h,b,pix,len(pix),info)==0,(kind,w,t,list(info));l.s2_session_snapshot(h,hero);l.s2_session_transition_snapshot(h,tr)
      if not phases or phases[-1][1]!=hero[80]:phases.append([t,hero[80]])
      if hero[80]in[13,14]:
       if death is None:
        death=t
        if kind.endswith('health'):assert l.s2_session_coin_count(h)>=1
       if hero[20]&255 and finished is None:finished=t
      if death and all(x==0xff000000 for x in pix):black=True
      if death and w==240 and t%2==0:frames.append(Image.frombytes('RGBA',(w,160),bytes(pix),'raw','BGRA').convert('RGB').resize((720,480),Image.Resampling.NEAREST))
      if l.s2_session_death_restarts(h):
       restarted=t;assert l.s2_session_health(h)==6 and hero[80]==0 and hero[102]==0 and hero[83]==0 and black
       assert restarted>finished>=death;assert info[0]==0;assert l.s2_session_coin_count(h)==0
       if kind.endswith('health'):l.s2_session_actor_snapshot(h,coinId,a);assert bytes(a)==coinInitial,(kind,w,list(a[:2]),list(a[39:44]))
       if kind=='intro_health':
        for n in range(25):
         assert l.s2_session_step(h,3 if n<5 else 0,pix,len(pix),info)==0
         if n>5:assert l.s2_session_dialogue_active(h)
         l.s2_session_snapshot(h,hero);assert hero[80]==0
        l.s2_session_transition_snapshot(h,tr);assert tr[0]==0 and l.s2_session_health(h)==6 and any(x!=0xff000000 for x in pix)
       break
     assert restarted,(kind,w,phases)
     if frames:frames[0].save(ROOT/f'previews/native_restart_{kind}.gif',save_all=True,append_images=frames[1:],duration=33,loop=0)
     cases.append(dict(kind=kind,width=w,death=death,animation_finished=finished,restarted=restarted,black_before_restart=black,phases=phases))
    finally:l.s2_session_destroy(h)
  for w in [240,480]:
   data=bytearray(raw);struct.pack_into('<HH',data,18+2*44,40,350);h,pix=open_(data,w);l.s2_session_set_transitions(h,1);start=None;indices=set();frames=[];done=None
   try:
    for t in range(1,501):
     assert l.s2_session_step(h,1 if t>=40 and t%12==4 else 0,pix,len(pix),info)==0;l.s2_session_snapshot(h,hero)
     if hero[80]==12:
      if start is None:start=info[0]-1
      assert hero[47]==0x834f334;indices.add(hero[22])
      if w==240 and t%2==0:frames.append(Image.frombytes('RGBA',(w,160),bytes(pix),'raw','BGRA').convert('RGB').resize((720,480),Image.Resampling.NEAREST))
     if l.s2_session_level_complete(h):done=t;break
    assert done and len(indices)==44,(w,start,done,sorted(indices))
    if frames:frames[0].save(ROOT/'previews/native_level_victory.gif',save_all=True,append_images=frames[1:],duration=33,loop=0)
    cases.append(dict(kind='victory',width=w,distinct_animation_frames=len(indices),complete=done))
   finally:l.s2_session_destroy(h)
 # Original F554 and F45C, with only manager and held-input calls intercepted.
 o=Original(r);u=o.u;binding=json.loads((ROOT/'docs/object_sprite_bindings.json').read_text())['types']['18'];o.ctor(binding['definition']);actor=o.actor;sp=o.sprite;packets=[]
 def hook(uc,addr,size,ctx):
  if addr==0x0800bec0:packets.append(list(struct.unpack('<3i',uc.mem_read(uc.reg_read(UC_ARM_REG_R0),12))))
  if addr in [0x08003a2c,0x0800fadc,0x0800bec0]:uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook);u.mem_write(actor,struct.pack('<I',0x020017cc));u.mem_write(actor+0x1e8,struct.pack('<I',0x0804b73c));u.mem_write(actor+0x228,struct.pack('<3i',1,7,0));u.mem_write(actor+0x20c,bytes(4));u.mem_write(actor+0x260,bytes(4))
 @FC
 def fetch(addr,out,n,ctx):
  try:b=u.mem_read(addr,n*4)
  except Exception:return 0
  for i,x in enumerate(struct.unpack('<'+'i'*n,b)):out[i]=x
  return 1
 @SINK
 def sink(kind,address,scale,ctx):return 0
 s=(I*80)();extra=(I*8)();book=(I*8)();l.s2_shrek_finish_enter.argtypes=[IP,IP,IP,I,FC,ctypes.c_void_p];l.s2_shrek_finish_step.argtypes=[IP,IP,I,FC,SINK,ctypes.c_void_p]
 o.call(0x0800f554,actor);assert l.s2_shrek_finish_enter(s,extra,book,0,fetch,None)==0 and extra[0]==12
 assert s[47]==struct.unpack('<I',u.mem_read(sp+8,4))[0]==0x834f334;sourceDone=nativeDone=None
 for tick in range(1,177):
  u.mem_write(0x0200324c,struct.pack('<i',tick));o.call(0x0801682c,sp);o.call(0x0800f45c,actor)
  done=l.s2_shrek_finish_step(s,book,tick,fetch,sink,None);assert done>=0
  assert [s[20],s[21],s[22],s[23]]==[u.mem_read(sp,1)[0],*struct.unpack('<i',u.mem_read(sp+4,4)),*struct.unpack('<2i',u.mem_read(sp+12,8))]
  if packets and sourceDone is None:sourceDone=tick;assert packets[0]==[0,22,0]
  if done and nativeDone is None:nativeDone=tick
 assert sourceDone==nativeDone==175,(sourceDone,nativeDone)
 report=dict(cases=cases,original_victory_frames_compared=176,source_completion_tick=sourceDone,collected_coin_restored_byte_identically=True,held_buttons_suppressed=True,music_contract_report="death_music_validation.json",mismatches=0,device_tested=False);(ROOT/'docs/stage57_integration_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
