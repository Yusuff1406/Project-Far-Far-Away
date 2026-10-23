"""Regression fixtures for Stage91 reports, using the real session."""
from session75_fixtures import *
for name,args in [('player_event',[P,IP]),('minigame_state',[P]),('set_transitions',[P,I]),('projectile_snapshot',[P,I,IP]),('set_viewport',[P,I,I])]:getattr(l,'s2_session_'+name).argtypes=args
runs=[]
# Cat and human bonus damage does not invoke loss; both retain zero-damage hurt.
for scene in [6,27]:
 s=Scene(scene);l.s2_session_set_transitions(s.h,1)
 for _ in range(25):s.step()
 hp=s.hero()[89];assert l.s2_session_player_event(s.h,(I*3)(1,38,1))==1
 assert s.hero()[80]==6 and s.hero()[89]==hp and l.s2_session_minigame_state(s.h)==1
 for _ in range(3):s.step();assert l.s2_session_minigame_state(s.h)==1
 runs.append(dict(kind='bonus_hit_survives',scene=scene));s.close()
# Every reported introduction queues exactly one active hero reaction.
for scene,descriptor in [(17,0x08053cf0),(5,0x08053cf0),(10,0x08053e58),(20,0x08053dd4),(15,0x08053cf0),(16,0x08053cf0)]:
 s=Scene(scene)
 for _ in range(40):s.step(64 if l.s2_session_dialogue_active(s.h)else 0)
 cues=[q for q in s.requests()if q[1]==11 and q[2]==descriptor];assert len(cues)==1,(scene,cues)
 if scene==17:
  assert not any(q[1]==11 and q[2]==0x08053f24 and q[0]==1 for q in s.requests())
  assert any(q[1]==11 and q[2]==0x08054080 for q in s.requests())
 runs.append(dict(kind='intro_voice',scene=scene,descriptor=hex(descriptor)));s.close()
# Right boundary fits every finite parallax layer, for normal and wide widths.
for width in [240,356]:
 s=Scene(1);assert l.s2_session_set_viewport(s.h,width,160)==0
 pix=(C.c_uint32*(width*160))();info=(I*8)();assert l.s2_session_step(s.h,0,pix,len(pix),info)==0
 cam=s.camera();assert cam[0]<3432-width,(width,cam)
 assert not any(p==0xff181818 for y in range(85,159)for p in list(pix)[y*width+width-7:(y+1)*width]),(width,'exposed edge')
 runs.append(dict(kind='donkey_right_edge',width=width,camera=cam[:2]));s.close()
# Active sessions own immutable scene/collision resources after initial decoding.
# Removing the temporary source copies must not trigger per-frame disk reads.
with tempfile.TemporaryDirectory()as directory:
 root=Path(directory);scene=root/'scene.s2lv';collision=root/'scene.s2cl'
 scene.write_bytes((R/'extracted/scene_23/scene.s2lv').read_bytes());collision.write_bytes((R/'collision/scene_23/scene.s2cl').read_bytes());err=I()
 paths=[R/'android/app/src/main/assets/session/resources.s2pk',scene,collision,R/'android/app/src/main/assets/session/sprites',R/'objects/scene_23/scene.s2ob'];h=l.s2_session_create_level(*[str(x).encode()for x in paths],C.byref(err));assert h,err.value
 scene.unlink();collision.unlink();pixels=(C.c_uint32*38400)();info=(I*8)()
 try:
  for t in range(60):assert l.s2_session_step(h,64 if l.s2_session_dialogue_active(h)else 0,pixels,len(pixels),info)==0
 finally:l.s2_session_destroy(h)
 runs.append(dict(kind='decoded_resources_survive_source_unlink',frames=60))
(R/'docs/stage91_validation.json').write_text(json.dumps(dict(cases=runs,device_tested=False),indent=2)+'\n');print('PASS Stage91',len(runs),'cases')
