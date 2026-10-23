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
# The source coin sprite must overlap the hero, as in the original footage.
s=Scene(0,{70:(99,142),35:(99,130),71:(99,142)})
coin=next(r for r in s.rows if r['instance_id']==35);assert coin['type']==89,coin
s.step();assert l.s2_session_dialogue_active(s.h)
a=s.actor(35);hero=sprite(s.hero(),s.camera());front=sprite(a+[0]*104,s.camera());mask=(hero>>24!=0)&(front>>24!=0);mask[:85]=False
assert np.count_nonzero(mask)>0;actual=np.frombuffer(bytes(s.pix),dtype=np.uint32).reshape(160,240);assert np.array_equal(actual[mask],front[mask]);runs.append(dict(kind='coin_front',pixels=int(np.count_nonzero(mask))));s.close()
# Columns belong to the source priority0 tile layer, separate from actor props.
s=Scene(29,{103:(590,430),104:(590,430)});s.step();assert l.s2_session_dialogue_active(s.h)
l.s2_render_file_foreground.argtypes=[C.c_char_p]+[I]*4+[P,C.c_size_t]
rgba=(C.c_uint8*(38400*4))();cx,cy=s.camera()[:2];assert l.s2_render_file_foreground(str(R/'extracted/scene_29/scene.s2lv').encode(),cx,cy,240,160,rgba,len(rgba))==0
color=np.frombuffer(bytes(rgba),dtype=np.uint8).reshape(160,240,4);front=(color[:,:,3].astype(np.uint32)<<24)|(color[:,:,0].astype(np.uint32)<<16)|(color[:,:,1].astype(np.uint32)<<8)|color[:,:,2]
hero=sprite(s.hero(),s.camera());mask=(hero>>24!=0)&(front>>24!=0);mask[:85]=False
assert np.count_nonzero(mask)>0;actual=np.frombuffer(bytes(s.pix),dtype=np.uint32).reshape(160,240);assert np.array_equal(actual[mask],front[mask]);runs.append(dict(kind='column_front',pixels=int(np.count_nonzero(mask))));s.close()
(R/'docs/stage91_layers_validation.json').write_text(json.dumps(dict(cases=runs,device_tested=False),indent=2)+'\n');print(runs)
