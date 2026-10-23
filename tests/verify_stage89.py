"""Book presentation, immediate bonus loss, restart dialogue and enemy registry.
Source assets plus native world integration; physical Android is not run.
"""
import sys,ctypes as C
from session75_fixtures import *
from PIL import Image
for n,a in [('minigame_state',[P]),('player_event',[P,IP]),('set_transitions',[P,I]),('transition_snapshot',[P,IP]),('death_restarts',[P]),('dialogue_snapshot',[P,IP]),('enemy_target_snapshot',[P,I,IP])]:getattr(l,'s2_session_'+n).argtypes=a
runs=[]
# Freeze the bonus hero on accepted failure. No hurt/fall animation may run,
# and no later hero voice requests may leak into the black transition.
for scene in [26,7,18,27]:
 s=Scene(scene);l.s2_session_set_transitions(s.h,1)
 for _ in range(25):s.step()
 before=s.hero();assert l.s2_session_player_event(s.h,(I*3)(1,38,1))==1
 assert l.s2_session_minigame_state(s.h)==2 and s.hero()==before
 requests=len(s.requests());black=None
 for t in range(25):
  s.step();assert s.hero()==before and len(s.requests())==requests
  if l.s2_session_minigame_state(s.h)==4:
   assert all(p==0xff000000 for p in s.pix);black=t;break
 assert black is not None
 runs.append(dict(kind='immediate_bonus_failure',scene=scene,black_frame=black,frozen_hero=True,no_late_SFX=True));s.close()
# An actual source intro, then owner-delivered lethal damage, black restart,
# and the same intro reopens while the scene fades in.
s=Scene(3);l.s2_session_set_transitions(s.h,1)
for _ in range(80):
 s.step()
 if l.s2_session_dialogue_active(s.h):break
assert l.s2_session_dialogue_active(s.h);s.step(64);s.step();assert not l.s2_session_dialogue_active(s.h)
assert l.s2_session_player_event(s.h,(I*3)(100,38,1))==1
for t in range(350):
 s.step()
 if l.s2_session_death_restarts(s.h):break
assert l.s2_session_death_restarts(s.h)==1
opened=None;frames=[]
for t in range(35):
 s.step();tr=(I*8)();l.s2_session_transition_snapshot(s.h,tr)
 if l.s2_session_dialogue_active(s.h) and opened is None:opened=t;assert tr[0]>0
 if t%2==0:frames.append(Image.frombytes('RGBA',(240,160),bytes(s.pix),'raw','BGRA').resize((720,480),Image.Resampling.NEAREST))
assert opened is not None
frames[0].save(R/'previews/stage89_restart_dialogue.gif',save_all=True,append_images=frames[1:],duration=33,loop=0)
runs.append(dict(kind='original_intro_reopens',scene=3,after_restart_frame=opened));s.close()
# Both actors stay at real level-floor coordinates. The enemy must choose
# the nearer eligible hero, including the hero not selected through L/R.
for shrek,donkey,expected in [((400,254),(500,256),3),((500,254),(400,256),6)]:
 s=Scene(13,{79:shrek,78:donkey,70:(430,261)})
 out=(I*3)();assert l.s2_session_enemy_target_snapshot(s.h,70,out)==0 and out[0]==expected,(list(out),expected)
 s.step(512);assert l.s2_session_player_type(s.h)==6
 eligible=3 if s.actor(70)[53] else expected
 assert l.s2_session_enemy_target_snapshot(s.h,70,out)==0 and out[0]==eligible,(list(out),eligible)
 runs.append(dict(kind='enemy_focus_independent',active=6,nearest=eligible));s.close()
# Every enemy kind52..62, with both approach sides:
# source scene/collision and scripts, relocated hero/actor fixture only.
examples={}
for scene in range(30):
 rows=json.loads((R/f'objects/scene_{scene:02}/objects.json').read_text())['objects']
 for row in rows:
  if row['type']in range(52,63):examples.setdefault(row['type'],(scene,row,rows))
assert set(examples)==set(range(52,63))-{58},sorted(examples)
# Type58 is created dynamically by the original spawner, not a placed row.
sc,r,rows=examples[55];r=dict(r);r['type']=58;examples[58]=(sc,r,rows)
l.s2_session_load_level.argtypes=[P]+[C.c_char_p]*5
for kind,(scene,row,rows) in sorted(examples.items()):
 for side in [-1,1]:
  x,y=row['anchor_px'];places={row['instance_id']:(x,y)}
  for hero in rows:
   if hero['type']in range(3,8):places[hero['instance_id']]=(max(1,x+side*40),max(1,y-8))
  s=Scene(scene,places)
  if kind==58:
   obj=Path(s.tmp.name)/'fixture.s2ob';data=bytearray(obj.read_bytes());struct.pack_into('<H',data,16+(row['instance_id']-1)*44,58);obj.write_bytes(data)
   paths=[R/'android/app/src/main/assets/session/resources.s2pk',R/f'extracted/scene_{scene:02}/scene.s2lv',R/f'collision/scene_{scene:02}/scene.s2cl',R/'android/app/src/main/assets/session/sprites',obj];assert l.s2_session_load_level(s.h,*[str(p).encode()for p in paths])==0;l.s2_session_set_auto_restart(s.h,0)
  poses=set();packets=set()
  for t in range(120):
   s.step(64 if l.s2_session_dialogue_active(s.h) and t%2 else 0);a=s.actor(row['instance_id']);poses.add((a[0],a[1],a[47],a[22]));packets.add(a[42])
  assert len(poses)>1,('actor stuck',kind,side)
  runs.append(dict(kind='enemy_world_fixture',type=kind,scene=scene,side=side,poses=len(poses),outgoing_events=sorted(packets)));s.close()
report=dict(cases=runs,device_tested=False,scope='Five direct accepted bonus damage fixtures; real intro/death/restart; dual hero nearest selection; 22 isolated physical enemy/script runs. Not a complete manual campaign or proof of every enemy response.')
(R/'docs/stage89_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
