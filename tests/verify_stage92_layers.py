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
for scene,hero,obj,intro,expected in [(17,9,3,10,'hero'),(5,2,1,4,'object')]:
 s=Scene(scene,{hero:(100,142),obj:(105,142),intro:(100,103)});s.step();assert l.s2_session_dialogue_active(s.h)
 hp=sprite(s.hero(),s.camera());op=sprite(s.actor(obj)+[0]*104,s.camera());mask=(hp>>24!=0)&(op>>24!=0);mask[:85]=False;assert np.count_nonzero(mask)>0
 actual=np.frombuffer(bytes(s.pix),dtype=np.uint32).reshape(160,240);front=hp if expected=='hero'else op;assert np.array_equal(actual[mask],front[mask]),(scene,'layer')
 runs.append(dict(scene=scene,object=obj,front=expected,pixels=int(np.count_nonzero(mask))));s.close()
(R/'docs/stage92_layers_validation.json').write_text(json.dumps(dict(cases=runs,device_tested=False),indent=2)+'\n');print(runs)
