"""Real native sessions with temporary scene-object placement fixtures."""
import ctypes as C,json,struct,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];I=C.c_int32;P=C.c_void_p;IP=C.POINTER(I);l=C.CDLL(str(R/'native/build/libshrek_scene.so'))
l.s2_session_create_level.argtypes=[C.c_char_p]*5+[IP];l.s2_session_create_level.restype=P
for n,a in [('set_auto_restart',[P,I]),('destroy',[P]),('step',[P,I,P,C.c_size_t,IP]),('snapshot',[P,IP]),('actor_snapshot',[P,I,IP]),('party_snapshot',[P,I,IP]),('camera_snapshot',[P,IP]),('requests',[P,IP,C.c_size_t]),('player_type',[P]),('dialogue_active',[P])]:getattr(l,'s2_session_'+n).argtypes=a
class Scene:
 def __init__(self,scene=2,placements=None):
  self.tmp=tempfile.TemporaryDirectory();self.pix=(C.c_uint32*38400)();self.info=(I*8)();self.rows=json.loads((R/f'objects/scene_{scene:02}/objects.json').read_text())['objects'];obj=R/f'objects/scene_{scene:02}/scene.s2ob'
  if placements is not None:
   d=bytearray(obj.read_bytes())
   for row in self.rows:
    xy=placements.get(row['instance_id'],(7500,0)if row['type']in[3,4,5,6,7]else(7000,0));struct.pack_into('<HH',d,18+(row['instance_id']-1)*44,*xy)
   obj=Path(self.tmp.name)/'fixture.s2ob';obj.write_bytes(d)
  paths=[R/'android/app/src/main/assets/session/resources.s2pk',R/f'extracted/scene_{scene:02}/scene.s2lv',R/f'collision/scene_{scene:02}/scene.s2cl',R/'android/app/src/main/assets/session/sprites',obj];err=I();self.h=l.s2_session_create_level(*[str(x).encode()for x in paths],C.byref(err));assert self.h,(scene,err.value)
  if placements is not None and any(row['type']in[3,4,5,6,7]and row['instance_id']not in placements for row in self.rows):
   l.s2_session_set_auto_restart(self.h,0) # Explicit off-map partner isolation.
 def step(self,b=0):
  e=l.s2_session_step(self.h,b,self.pix,len(self.pix),self.info);assert e==0,(b,e,list(self.info));return self.hero()
 def hero(self,typ=None):
  s=(I*320)();e=l.s2_session_snapshot(self.h,s)if typ is None else l.s2_session_party_snapshot(self.h,typ,s);assert e==0;return list(s)
 def actor(self,id):
  s=(I*216)();assert l.s2_session_actor_snapshot(self.h,id,s)==0;return list(s)
 def camera(self):
  s=(I*4)();assert l.s2_session_camera_snapshot(self.h,s)==0;return list(s)
 def requests(self):
  s=(I*(8192*8))();n=l.s2_session_requests(self.h,s,8192);assert n>=0;return[list(s[i*8:i*8+8])for i in range(n)]
 def close(self):l.s2_session_destroy(self.h);self.tmp.cleanup()
