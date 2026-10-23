"""Pixel overlap fixtures for props and two formerly background enemy classes."""
from session75_fixtures import *
import numpy as np
from PIL import Image
raw=(R/'android/app/src/main/assets/session/resources.s2pk').read_bytes();_,_,nb,na=struct.unpack_from('<4s3I',raw);at=16
for _ in range(nb):_,n=struct.unpack_from('<2I',raw,at);at+=8+n
animations={}
for _ in range(na):a,i,n=struct.unpack_from('<3I',raw,at);at+=12;animations[a]=(i,raw[at:at+n].decode());at+=n
l.s2_sprite_bank_create.argtypes=[C.c_char_p];l.s2_sprite_bank_create.restype=P;l.s2_sprite_bank_destroy.argtypes=[P];l.s2_actor_anchor_q8.argtypes=[IP,IP,I,I,IP];l.s2_sprite_composite_bank.argtypes=[P]+[I]*7+[P,C.c_size_t]
def sprite(pose,camera):
 state=(I*320)(*pose);anchor=(I*2)();l.s2_actor_anchor_q8(C.cast(C.byref(state,72*4),IP),state,state[18],state[38],anchor)
 idx,name=animations[state[47]];bank=l.s2_sprite_bank_create(str(R/'android/app/src/main/assets/session/sprites'/name).encode());assert bank;out=(C.c_uint32*38400)()
 try:assert l.s2_sprite_composite_bank(bank,idx,state[22],state[18],240,160,(anchor[0]>>8)-camera[0],(anchor[1]>>8)-camera[1],out,len(out))==0
 finally:l.s2_sprite_bank_destroy(bank)
 return np.frombuffer(bytes(out),dtype=np.uint32).reshape(160,240)
runs=[]
for scene,hero,obj in [(0,70,44),(3,95,41),(23,10,24)]:
 rows=json.loads((R/f'objects/scene_{scene:02}/objects.json').read_text())['objects'];h=next(r for r in rows if r['instance_id']==hero);intro=next(r for r in rows if r['type']==151);xy=tuple(h['anchor_px']);s=Scene(scene,{hero:xy,obj:xy,intro['instance_id']:xy});s.step();assert l.s2_session_dialogue_active(s.h)
 a=s.actor(obj);hero_pixels=sprite(s.hero(),s.camera());actor_pixels=sprite(a+[0]*104,s.camera());mask=(hero_pixels>>24!=0)&(actor_pixels>>24!=0);mask[:85]=False
 assert np.count_nonzero(mask)>0,(scene,obj,'no overlapping pixels')
 actual=np.frombuffer(bytes(s.pix),dtype=np.uint32).reshape(160,240);assert np.array_equal(actual[mask],actor_pixels[mask]),(scene,obj,'foreground wrong')
 Image.frombytes('RGBA',(240,160),bytes(s.pix),'raw','BGRA').resize((720,480),Image.Resampling.NEAREST).save(R/f'previews/stage90_layer_{scene}_{obj}.png');runs.append(dict(scene=scene,type=next(r['type']for r in rows if r['instance_id']==obj),overlap_pixels=int(np.count_nonzero(mask))));s.close()
(R/'docs/stage90_layers_validation.json').write_text(json.dumps(dict(cases=runs,device_tested=False,scope='Source sprites independently composited at actual native poses, overlapping hero pixels. Modal intro holds poses still; verifies native foreground order, not a full original render-order oracle.'),indent=2)+'\n');print(runs)
