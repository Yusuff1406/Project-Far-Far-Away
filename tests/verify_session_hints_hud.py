#!/usr/bin/env python3
"""Four recovered plain source actors, default HUD, remote enemies and falling defeat."""
import ctypes,json,struct,sys,tempfile
from PIL import Image
from verify_generic_runtime import *
from session_fixtures import without_intro
I=ctypes.c_int32

def main():
 r=Rom(sys.argv[1]);l=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));c=l.s2_session_create_level;c.argtypes=[ctypes.c_char_p]*5+[IP];c.restype=ctypes.c_void_p;l.s2_session_set_auto_restart.argtypes=[ctypes.c_void_p,I]
 for name,args in [('s2_session_destroy',[ctypes.c_void_p]),('s2_session_reset',[ctypes.c_void_p]),('s2_session_health',[ctypes.c_void_p]),('s2_session_actor_snapshot',[ctypes.c_void_p,ctypes.c_int,IP]),('s2_session_snapshot',[ctypes.c_void_p,IP]),('s2_session_set_viewport',[ctypes.c_void_p,ctypes.c_int,ctypes.c_int]),('s2_session_step',[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_size_t,IP])]:getattr(l,name).argtypes=args
 paths=[ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites'];raw=(ROOT/'objects/scene_00/scene.s2ob').read_bytes();rows=json.loads((ROOT/'objects/scene_00/objects.json').read_text())['objects'];hints=[x for x in rows if x['type']in[120,121,122,130]];factory=json.loads((ROOT/'docs/object_factory_traces.json').read_text())['types'];count=0;results=[];info=(I*8)();state=(I*216)();hero=(I*320)();images=[]
 with tempfile.TemporaryDirectory()as tmp:
  path=Path(tmp)/'fixture.s2ob';path.write_bytes(without_intro(raw));e=I();h=c(*[str(p).encode()for p in paths],str(path).encode(),ctypes.byref(e));assert h,e.value;l.s2_session_set_auto_restart(h,0);pix=(ctypes.c_uint32*38400)();originals={};remote={}
  try:
   assert l.s2_session_health(h)==6
   for row in hints:
    o=Original(r);u=o.u;xy=[v*256 for v in row['anchor_px']];anim=factory[row['type']]['calls'][0]['registers'][1];u.mem_write(0x2007000,struct.pack('<2i',*xy));u.mem_write(0x203f000,struct.pack('<I',0));o.call(0x80180b0,o.actor,anim,0x2007000,0);originals[row['instance_id']]=o
   for id in [9,10,31,59,61,62,63]:assert l.s2_session_actor_snapshot(h,id,state)==0;remote[id]=bytes(state)
   for t in range(1,361):
    assert l.s2_session_step(h,0,pix,len(pix),info)==0
    for id,o in originals.items():
     if t>240:continue
     u=o.u;u.mem_write(0x200324c,struct.pack('<i',t));u.mem_write(0x20033e0,struct.pack('<i',t));o.call(0x8018208,o.actor);assert l.s2_session_actor_snapshot(h,id,state)==0;sp=struct.unpack('<I',u.mem_read(o.actor+0x1c0,4))[0];expected=[*struct.unpack('<2i',u.mem_read(o.actor+0x178,8)),u.mem_read(sp,1)[0],*struct.unpack('<4i',u.mem_read(sp+4,16))];assert [*state[:2],state[20],state[21],state[47],state[22],state[23]]==expected,(id,t);count+=1
    for id,initial in remote.items():assert l.s2_session_actor_snapshot(h,id,state)==0 and bytes(state)==initial,(t,id,'remote enemy moved')
   assert l.s2_session_reset(h)==0 and l.s2_session_health(h)==6
  finally:l.s2_session_destroy(h)
  # Native previews at source hint positions; only player spawn is relocated.
  for row in hints:
   b=without_intro(raw);struct.pack_into('<HH',b,18+69*44,row['anchor_px'][0],min(350,row['anchor_px'][1]+45));path.write_bytes(b);h=c(*[str(p).encode()for p in paths],str(path).encode(),ctypes.byref(e));assert h
   try:
    for t in range(1,49):
     assert l.s2_session_step(h,0,pix,len(pix),info)==0
     if row['type']==120 and t%3==0:images.append(Image.frombytes('RGBA',(240,160),bytes(pix),'raw','BGRA').convert('RGB').resize((960,640),Image.Resampling.NEAREST))
    Image.frombytes('RGBA',(240,160),bytes(pix),'raw','BGRA').convert('RGB').resize((960,640),Image.Resampling.NEAREST).save(ROOT/f"previews/native_hint_{row['type']}.png")
   finally:l.s2_session_destroy(h)
  # Actual bottomless water/gap columns: stationary controller, no injected defeat event.
  for x in [1700,2300,2990]:
   reference=None
   for width in [240,480]:
    b=without_intro(raw);struct.pack_into('<HH',b,18+69*44,x,340);path.write_bytes(b);h=c(*[str(p).encode()for p in paths],str(path).encode(),ctypes.byref(e));assert h;l.s2_session_set_auto_restart(h,0);assert l.s2_session_set_viewport(h,width,160)==0;pixels=(ctypes.c_uint32*(width*160))()
    try:
     for replay in range(2):
      if replay:assert l.s2_session_reset(h)==0
      dead=None
      for t in range(1,91):
       assert l.s2_session_step(h,0,pixels,len(pixels),info)==0;l.s2_session_snapshot(h,hero)
       if hero[80]==13 and dead is None:dead=t;assert l.s2_session_health(h)==0
      assert dead is not None,(x,width)
      if reference is None:reference=dead;results.append({'x':x,'death_tick':dead})
      else:assert reference==dead
    finally:l.s2_session_destroy(h)
 images[0].save(ROOT/'previews/native_hints_hud.gif',save_all=True,append_images=images[1:],duration=50,loop=0,optimize=False,disposal=2)
 report={'original_plain_actor_frames':count,'source_hint_types':[x['type']for x in hints],'initial_health':6,'remote_enemy_frames_frozen':360*7,'fall_cases':results,'mismatches':0,'scope':'Original180B0/18208 source hint/horse animations at original positions/flags. Native viewport/HUD preview. Seven untouched source enemies remain byte-identical while distant for360 frames. Player moved only in gap/preview fixtures; physical fall crosses source world bound, defeats and resets at240/480. Actual water surface splash, game-over manager and Android excluded.'};(ROOT/'docs/session_hints_hud_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
