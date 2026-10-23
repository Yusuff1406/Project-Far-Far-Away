#!/usr/bin/env python3
"""Physical overlaps: Donkey/door/Pinocchio, and inactive Donkey/horse."""
import ctypes as C,json,struct,tempfile,numpy as np
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1];l=C.CDLL(str(R/'native/build/libshrek_scene.so'));I=C.c_int32;IP=C.POINTER(I);P=C.c_void_p
l.s2_session_party_snapshot.argtypes=[P,I,IP];l.s2_session_camera_snapshot.argtypes=[P,IP]
l.s2_session_create_level.argtypes=[C.c_char_p]*5+[IP];l.s2_session_create_level.restype=P
for n,args in [('destroy',[P]),('step',[P,I,P,C.c_size_t,IP]),('snapshot',[P,IP]),('actor_snapshot',[P,I,IP]),('world_size',[P,IP])]:getattr(l,'s2_session_'+n).argtypes=args
l.s2_sprite_render_file.argtypes=[C.c_char_p]+[I]*7+[P,C.c_size_t];l.s2_actor_anchor_q8.argtypes=[IP,IP,I,I,IP]
raw=(R/'android/app/src/main/assets/session/resources.s2pk').read_bytes();_,_,nb,na=struct.unpack_from('<4s3I',raw);at=16
for _ in range(nb):_,n=struct.unpack_from('<2I',raw,at);at+=8+n
animations={}
for _ in range(na):a,i,n=struct.unpack_from('<3I',raw,at);at+=12;animations[a]=(i,raw[at:at+n].decode());at+=n
pix=(C.c_uint32*38400)();info=(I*8)();hero=(I*320)();actor=(I*216)();results=[]
def sprite(state,cx,cy):
 s=(I*len(state))(*state);anchor=(I*2)();l.s2_actor_anchor_q8(C.cast(C.byref(s,72*4),IP),s,s[18],s[38],anchor);idx,name=animations[s[47]];out=(C.c_uint8*(38400*4))();assert l.s2_sprite_render_file(str(R/'android/app/src/main/assets/session/sprites'/name).encode(),idx,s[22],s[18],240,160,(anchor[0]>>8)-cx,(anchor[1]>>8)-cy,out,len(out))==0;return np.frombuffer(bytes(out),dtype=np.uint8).reshape(160,240,4)
def compare(session,body,target,exclude=None):
 l.s2_session_snapshot(session,hero);size=(I*2)();l.s2_session_world_size(session,size);cx=max(0,min((hero[0]>>8)-120,size[0]-240));cy=max(0,min((hero[1]>>8)-95,size[1]-160));camera=(I*4)();l.s2_session_camera_snapshot(session,camera);cx=camera[0];cy=camera[1];a=sprite(body,cx,cy);b=sprite(target,cx,cy);mask=(a[:,:,3]>0)&(b[:,:,3]>0)&np.any(a[:,:,:3]!=b[:,:,:3],axis=2)
 if exclude is not None:mask&=sprite(exclude,cx,cy)[:,:,3]==0
 expected=0xff000000|(a[:,:,0].astype(np.uint32)<<16)|(a[:,:,1].astype(np.uint32)<<8)|a[:,:,2];actual=np.frombuffer(bytes(pix),dtype=np.uint32).reshape(160,240);assert mask.sum()>5,('no physical overlap',int(mask.sum()));assert np.array_equal(actual[mask],expected[mask]),('wrong layer',int((actual[mask]!=expected[mask]).sum()));return int(mask.sum())
def paths(sc,obj):return [R/'android/app/src/main/assets/session/resources.s2pk',R/f'extracted/scene_{sc:02}/scene.s2lv',R/f'collision/scene_{sc:02}/scene.s2cl',R/'android/app/src/main/assets/session/sprites',obj]
with tempfile.TemporaryDirectory()as td:
 for typ in [22,102,76,78]:
  rows=json.loads((R/'objects/scene_01/objects.json').read_text())['objects'];target=next(x for x in rows if x['type']==typ);d=bytearray((R/'objects/scene_01/scene.s2ob').read_bytes())
  for row in rows:struct.pack_into('<HH',d,18+(row['instance_id']-1)*44,*((2137,211)if row['type']==6 or row['instance_id']==target['instance_id']else(7000,0)))
  p=Path(td)/'layer.s2ob';p.write_bytes(d);e=I();h=l.s2_session_create_level(*[str(x).encode()for x in paths(1,p)],C.byref(e));assert h,e.value
  try:
   assert l.s2_session_step(h,0,pix,len(pix),info)==0;l.s2_session_snapshot(h,hero);l.s2_session_actor_snapshot(h,target['instance_id'],actor);n=compare(h,list(actor),list(hero))if typ in[76,78] else compare(h,list(hero),list(actor));results.append({'scene':1,'actor_type':typ,'hero':'active Donkey','overlap_pixels_verified':n});Image.frombytes('RGBA',(240,160),bytes(pix),'raw','BGRA').resize((960,640),Image.Resampling.NEAREST).save(R/f'previews/stage75_layer_{typ}.png')
  finally:l.s2_session_destroy(h)
 rows=json.loads((R/'objects/scene_02/objects.json').read_text())['objects'];horse=next(x for x in rows if x['type']==130);d=bytearray((R/'objects/scene_02/scene.s2ob').read_bytes())
 for row in rows:
  if row['type']not in[3,6,130]:struct.pack_into('<HH',d,18+(row['instance_id']-1)*44,7000,0)
 p=Path(td)/'pair.s2ob';p.write_bytes(d);e=I();h=l.s2_session_create_level(*[str(x).encode()for x in paths(2,p)],C.byref(e));assert h,e.value
 try:
  assert l.s2_session_step(h,512,pix,len(pix),info)==0;l.s2_session_snapshot(h,hero);donkey=list(hero);assert l.s2_session_step(h,256,pix,len(pix),info)==0;l.s2_session_snapshot(h,hero);l.s2_session_actor_snapshot(h,horse['instance_id'],actor);current=(I*320)();assert l.s2_session_party_snapshot(h,6,current)==0;donkey=list(current);n=compare(h,donkey,list(actor),list(hero));results.append({'scene':2,'actor_type':130,'hero':'inactive Donkey','overlap_pixels_verified':n});Image.frombytes('RGBA',(240,160),bytes(pix),'raw','BGRA').resize((960,640),Image.Resampling.NEAREST).save(R/'previews/stage75_layer_horse.png')
 finally:l.s2_session_destroy(h)
 # Apple uses a source scene02 fixture; scene01 contains no apple instance.
 rows=json.loads((R/'objects/scene_02/objects.json').read_text())['objects'];apple=next(x for x in rows if x['type']==77);d=bytearray((R/'objects/scene_02/scene.s2ob').read_bytes())
 for row in rows:struct.pack_into('<HH',d,18+(row['instance_id']-1)*44,*((85,302)if row['type']==3 or row['instance_id']==apple['instance_id']else(7000,0)))
 p=Path(td)/'apple.s2ob';p.write_bytes(d);e=I();h=l.s2_session_create_level(*[str(x).encode()for x in paths(2,p)],C.byref(e));assert h,e.value
 try:
  assert l.s2_session_step(h,0,pix,len(pix),info)==0;l.s2_session_snapshot(h,hero);l.s2_session_actor_snapshot(h,apple['instance_id'],actor);n=compare(h,list(actor),list(hero));results.append({'scene':2,'actor_type':77,'hero':'active Shrek','overlap_pixels_verified':n})
 finally:l.s2_session_destroy(h)
report={'cases':results,'device_tested':False,'scope':'Physical spawn fixtures; source sprite masks independently rendered and compared at body/NPC/decor intersections. Key foreground is checked independently; NPC/decor remain behind both heroes.'};(R/'docs/stage75_layers_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
