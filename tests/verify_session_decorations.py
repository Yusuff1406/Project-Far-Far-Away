#!/usr/bin/env python3
from session_fixtures import without_intro,fixture_scene
"""Source plain actor frames and owned defeat smoke integration."""
import ctypes,json,struct,sys,tempfile,hashlib
from PIL import Image
from verify_generic_runtime import *
def main():
 l=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));I=ctypes.c_int32
 create=l.s2_session_create_level;create.argtypes=[ctypes.c_char_p]*5+[IP];create.restype=ctypes.c_void_p
 for name,args in [('s2_session_destroy',[ctypes.c_void_p]),('s2_session_reset',[ctypes.c_void_p]),('s2_session_actor_snapshot',[ctypes.c_void_p,ctypes.c_int,IP]),('s2_session_smoke_snapshot',[ctypes.c_void_p,ctypes.c_int,IP]),('s2_session_requests',[ctypes.c_void_p,IP,ctypes.c_size_t]),('s2_session_coin_count',[ctypes.c_void_p]),('s2_session_set_viewport',[ctypes.c_void_p,ctypes.c_int,ctypes.c_int]),('s2_session_step',[ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(ctypes.c_uint32),ctypes.c_size_t,IP])]:getattr(l,name).argtypes=args
 paths=[ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites'];obj=fixture_scene(ROOT/'objects/scene_00/scene.s2ob');r=Rom(sys.argv[1]);rows=json.loads(obj.with_name('objects.json').read_text())['objects'];ambient=[x for x in rows if x['type']in[134,135]];factory=json.loads((ROOT/'docs/object_factory_traces.json').read_text())['types'];originals={};err=I();h=create(*[str(p).encode()for p in paths],str(obj).encode(),ctypes.byref(err));assert h,(err.value,)
 state=(I*216)();pixels=(ctypes.c_uint32*(240*160))();info=(I*8)();sourceframes=0
 try:
  for row in ambient:
   ident=row['instance_id'];assert l.s2_session_actor_snapshot(h,ident,state)==0
   o=Original(r);u=o.u;flags=row['flags_byte'];anim=factory[row['type']]['calls'][0]['registers'][1];assert anim==state[47]
   u.mem_write(0x2007000,struct.pack('<2i',*(v*256 for v in row['anchor_px'])));u.mem_write(0x203f000,struct.pack('<I',(flags>>1)&1));o.call(0x80180b0,o.actor,anim,0x2007000,flags&1);originals[ident]=o
  for t in range(1,241):
   assert l.s2_session_step(h,0,pixels,len(pixels),info)==0
   for ident,o in originals.items():
    u=o.u;u.mem_write(0x200324c,struct.pack('<i',t));u.mem_write(0x20033e0,struct.pack('<i',t));o.call(0x8018208,o.actor);assert l.s2_session_actor_snapshot(h,ident,state)==0;sp=struct.unpack('<I',u.mem_read(o.actor+0x1c0,4))[0]
    expected={0:struct.unpack('<i',u.mem_read(o.actor+0x178,4))[0],1:struct.unpack('<i',u.mem_read(o.actor+0x17c,4))[0],20:u.mem_read(sp,1)[0],21:struct.unpack('<i',u.mem_read(sp+4,4))[0],22:struct.unpack('<i',u.mem_read(sp+12,4))[0],23:struct.unpack('<i',u.mem_read(sp+16,4))[0],18:u.mem_read(sp+0x28,1)[0],38:u.mem_read(sp+0x29,1)[0]}
    assert not {i:(state[i],v)for i,v in expected.items()if state[i]!=v},(ident,t);sourceframes+=1
  assert l.s2_session_smoke_snapshot(h,-1,state)==0
 finally:l.s2_session_destroy(h)
 raw=bytearray(obj.read_bytes());struct.pack_into('<HH',raw,18+62*44,60,350);images=[];traces=[];lifecycle=[]
 with tempfile.TemporaryDirectory()as tmp:
  p=Path(tmp)/'fixture.s2ob';p.write_bytes(raw)
  for width in [240,480]:
   h=create(*[str(p).encode()for p in paths],str(p).encode(),ctypes.byref(err));assert h,err.value;assert l.s2_session_set_viewport(h,width,160)==0
   try:
    for replay in range(2):
     if replay:assert l.s2_session_reset(h)==0
     assert l.s2_session_smoke_snapshot(h,-1,state)==0
     pixels=(ctypes.c_uint32*(width*160))();trace=[];live=[];puff=(I*80)()
     for t in range(1,181):
      buttons=2 if t==1 else 16 if 65<=t<90 else 0
      assert l.s2_session_step(h,buttons,pixels,len(pixels),info)==0,(t,list(info))
      count=l.s2_session_smoke_snapshot(h,-1,puff);assert count in [0,1]
      if count:assert l.s2_session_smoke_snapshot(h,0,puff)==0;live.append(t);assert puff[47]==0x8334a24 and not puff[40]&1
      else:puff[:]=[0]*80
      trace.append([count,*puff])
      if width==240 and replay==0 and t<=90 and t%2==0:images.append(Image.frombytes('RGBA',(240,160),bytes(pixels),'raw','BGRA').convert('RGB').resize((960,640),Image.Resampling.NEAREST))
     assert len(live)==32 and live==list(range(live[0],live[0]+32)),live
     assert l.s2_session_coin_count(h)==1
     if traces:assert trace==traces[0],(width,replay)
     traces.append(trace);lifecycle.append([width,replay,live[0],live[-1]])
     assert l.s2_session_reset(h)==0 and l.s2_session_smoke_snapshot(h,-1,puff)==0
   finally:l.s2_session_destroy(h)
 # View the red butterfly in its original map position; only player start moves.
 with tempfile.TemporaryDirectory()as tmp:
  data=bytearray(obj.read_bytes());struct.pack_into('<HH',data,18+69*44,600,240);p=Path(tmp)/'butterfly.s2ob';p.write_bytes(data)
  h=create(*[str(x).encode()for x in paths],str(p).encode(),ctypes.byref(err));assert h
  try:
   pixels=(ctypes.c_uint32*(240*160))()
   for t in range(1,19):assert l.s2_session_step(h,0,pixels,len(pixels),info)==0
   Image.frombytes('RGBA',(240,160),bytes(pixels),'raw','BGRA').convert('RGB').resize((960,640),Image.Resampling.NEAREST).save(ROOT/'previews/native_butterflies_source_position.png')
  finally:l.s2_session_destroy(h)
 images[0].save(ROOT/'previews/native_butterflies_smoke_fixture.gif',save_all=True,append_images=images[1:],duration=33,loop=0);images[35].save(ROOT/'previews/native_butterflies_smoke_fixture.png')
 report={'ambient_source_frames':sourceframes,'ambient_ids':[x['instance_id']for x in ambient],'smoke_scene_frames':720,'smoke_lifecycle':lifecycle,'reset_viewport_equal':True,'mismatches':0,'scope':'Five original butterfly134/135 actors at original positions/flags, animation against Thumb180B0/18208. Factory animation pointers from startup image. Physical B defeats relocated pumpkin63; source death request creates animated smoke for32 frames, coin pickup unaffected. Phone/world camera activation not validated.'}
 (ROOT/'docs/session_decorations_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
