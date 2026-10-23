#!/usr/bin/env python3
from session_fixtures import without_intro,fixture_scene
"""Scene00 registry, original isolated object updates and physical fixture."""
import ctypes,json,struct,sys,tempfile
from pathlib import Path
from PIL import Image
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_PC,UC_ARM_REG_LR
from verify_generic_runtime import Original,Rom,ROOT,IP

def main():
 lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));create=lib.s2_session_create_level;create.argtypes=[ctypes.c_char_p]*5+[IP];create.restype=ctypes.c_void_p
 for name,types in [('s2_session_destroy',[ctypes.c_void_p]),('s2_session_reset',[ctypes.c_void_p]),('s2_session_world_info',[ctypes.c_void_p,IP]),('s2_session_actor_snapshot',[ctypes.c_void_p,ctypes.c_int,IP]),('s2_session_snapshot',[ctypes.c_void_p,IP]),('s2_session_step',[ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(ctypes.c_uint32),ctypes.c_size_t,IP]),('s2_session_requests',[ctypes.c_void_p,IP,ctypes.c_size_t])]:getattr(lib,name).argtypes=types
 paths=[str(x).encode() for x in [ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites']];objects=fixture_scene(ROOT/'objects/scene_00/scene.s2ob');err=ctypes.c_int32()
 h=create(*paths,str(objects).encode(),ctypes.byref(err));assert h and err.value==0
 meta=(ctypes.c_int32*4)();assert lib.s2_session_world_info(h,meta)==0 and list(meta)==[71,70,0,70]
 state=(ctypes.c_int32*320)();actor=(ctypes.c_int32*216)();pixels=(ctypes.c_uint32*38400)();info=(ctypes.c_int32*8)();lib.s2_session_snapshot(h,state);initial=list(state);assert not any(state[104:])
 source=json.loads((ROOT/"objects/scene_00/objects.json").read_text())["objects"];byid={row["instance_id"]:row for row in source};ids=[row["instance_id"] for row in source if row["type"] in (18,89,10,14,16)];saved={};originals={};r=Rom(sys.argv[1])
 def camera_fixture(uc,address,size,o):
  if address==0x080007e0:uc.reg_write(UC_ARM_REG_R0,o.native_visible);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 for id in ids:
  assert lib.s2_session_actor_snapshot(h,id,actor)==0;saved[id]=list(actor);o=Original(r);o.ctor(0x080519e8 if byid[id]["type"]==89 else 0x08051c04 if byid[id]["type"]==10 else 0x080526a4 if byid[id]["type"]==14 else 0x08052684 if byid[id]["type"]==16 else 0x08052694,tuple(actor[:2]),actor[18]);o.u.mem_write(o.actor+0x178,struct.pack("<2i",*actor[:2]));o.u.mem_write(o.actor+0x190,struct.pack("<4i",*actor[32:36]));o.seed(actor);o.call(0x08013344,o.vm,0x08051ad8 if byid[id]["type"]==89 else 0x08051d70 if byid[id]["type"]==10 else 0x08052714 if byid[id]["type"]==14 else 0x080528e0 if byid[id]["type"]==16 else 0x08052c28);o.camera_fixture=False;o.native_visible=0;o.u.hook_add(UC_HOOK_CODE,camera_fixture,o);originals[id]=o
 frames=0
 for tick in range(1,241):
  assert lib.s2_session_step(h,0,pixels,len(pixels),info)==0
  for id,o in originals.items():
   for addr in (0x0200324c,0x020033e0):o.u.mem_write(addr,struct.pack('<i',tick))
   assert lib.s2_session_actor_snapshot(h,id,actor)==0;o.native_visible=actor[56];o.call(0x08018208,o.actor)
   if byid[id]["type"] in (10,14):o.u.mem_write(o.actor+0x15d,bytes([o.u.mem_read(o.actor+0x15d,1)[0]|8]))
   diff={i:(actor[i],v) for i,v in o.snapshot().items() if actor[i]!=v};assert not diff,(tick,id,diff)
   assert list(actor[:2])==list(struct.unpack('<2i',o.u.mem_read(o.actor+0x178,8)))
   assert list(actor[80:84])==list(struct.unpack('<4i',o.u.mem_read(o.vm+4,16)));frames+=1
 assert lib.s2_session_reset(h)==0;lib.s2_session_snapshot(h,state);assert list(state)==initial
 for id in ids:lib.s2_session_actor_snapshot(h,id,actor);assert list(actor)==saved[id]
 actor[0]=123;assert lib.s2_session_actor_snapshot(h,77,actor)==-2 and actor[0]==123;assert lib.s2_session_requests(h,None,0)==0;lib.s2_session_destroy(h)
 raw=objects.read_bytes();activations=[];bounces=[];images=[]
 with tempfile.TemporaryDirectory() as tmp:
  p=Path(tmp)/'fixture.s2ob';data=bytearray(raw);struct.pack_into('<HH',data,18,35,365);p.write_bytes(data);h=create(*paths,str(p).encode(),ctypes.byref(err));assert h
  for tick in range(1,161):
   assert lib.s2_session_step(h,1 if tick in (60,120) else 0,pixels,len(pixels),info)==0
   lib.s2_session_actor_snapshot(h,1,actor);lib.s2_session_snapshot(h,state)
   if actor[146]&255:activations.append(tick)
   if state[11]==-1430 and state[80]==2:bounces.append(tick)
   if tick%4==0:images.append(Image.frombytes('RGBA',(240,160),bytes(pixels),'raw','BGRA').convert('RGB').resize((720,480),Image.Resampling.NEAREST))
  requests=(ctypes.c_int32*(256*8))();count=lib.s2_session_requests(h,requests,256);assert count>=0
  sounds=[list(requests[i*8:i*8+8]) for i in range(count) if requests[i*8+1]==11 and requests[i*8+2]==0x08053fb4];assert activations==[1,96,97,154,155] and bounces==[97,155] and [row[0] for row in sounds]==[2,97,98,155,156];assert all(row[2]==0x08053fb4 for row in sounds);lib.s2_session_destroy(h)
  for malformed in (b'',raw[:16],b'NOPE'+raw[4:]):
   p.write_bytes(malformed);h=create(*paths,str(p).encode(),ctypes.byref(err));assert not h and err.value==-2
 images[0].save(ROOT/'previews/native_world_contact_fixture.gif',save_all=True,append_images=images[1:],duration=67,loop=0,optimize=False,disposal=2);images[10].save(ROOT/'previews/native_world_contact_fixture.png')
 report={'original_scene_rows':71,'supported_actor_ids':sorted(row['instance_id']for row in source if row['type']not in range(3,8)),'baseline_actor_ids':ids,'skipped_rows':0,'player_spawn_id':70,'isolated_original_actor_frames':frames,'reset_verified':True,'fixture_activation_ticks':activations,'fixture_bounce_ticks':bounces,'fixture_sound_requests':sounds,'malformed_object_files_refused':3,'mismatches':0,'scope':'Source camera activity is explicitly supplied by the native owner fixture; visibility geometry is checked separately in Stage87. Original isolated generic actor updates at source positions. Physical integration fixture moves first object to (35,365); production assets keep original positions. Type10/14 surface-emitted flagbit3 supplied as an owner fixture. Type53 is compared separately in verify_enemy_scripts.py. Patrol marker integration is checked in Stage89; full scheduler and Android execution excluded.'}
 (ROOT/'docs/session_world_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
