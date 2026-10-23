"""Reported Cat bonus, hero filters, optional jump and all six cinematic groups."""
from session75_fixtures import *
from PIL import Image
for n,a in [('player_event',[P,IP]),('minigame_state',[P]),('set_transitions',[P,I]),('set_puss_double_jump',[P,I]),('enemy_target_snapshot',[P,I,IP])]:getattr(l,'s2_session_'+n).argtypes=a
runs=[]
# A hit in Cat's bonus is knockback, not a loss. HP is not a hidden timer.
s=Scene(6);l.s2_session_set_transitions(s.h,1)
for _ in range(25):s.step()
hp=s.hero()[89];assert l.s2_session_player_event(s.h,(I*3)(1,41,1))==1
assert l.s2_session_minigame_state(s.h)==1 and s.hero()[80]==6 and s.hero()[89]==hp
for _ in range(10):s.step();assert l.s2_session_minigame_state(s.h)==1
runs.append(dict(kind='Cat_bonus_hit',hurt_state=True,HP_unchanged=True,bonus_active=True));s.close()
# Original base player ctor D294 clears+1E4. Only Donkey CE80 and human11A0C
# set it. Cat105E4 and GingyD24C inherit zero: the old all-non-Shrek=1
# adaptation made target-filtered enemies ignore them.
for scene,expected in [(0,0),(23,0),(3,0),(1,1),(29,1)]:
 s=Scene(scene);assert s.hero()[90]==expected,(scene,s.hero()[90]);runs.append(dict(kind='hero_filter',type=l.s2_session_player_type(s.h),value=expected));s.close()
# No second jump by default; the opt-in setting retains the former feature.
traces={}
for enabled in [0,1]:
 s=Scene(23,{10:(878,1736)});l.s2_session_set_puss_double_jump(s.h,enabled);trace=[]
 for t in range(55):trace.append(s.step(1 if t in [20,30]else 0))
 traces[enabled]=trace;s.close()
assert not(traces[0][30][100]&0x10000) and traces[1][30][100]&0x10000
assert traces[1][30][11]<traces[0][30][11]
runs.append(dict(kind='Cat_extra_jump',default=False,opt_in=True))
# Source-filtered enemies must see Cat/Gingy after their real script sets53.
for scene,hero,enemy in [(3,95,41),(23,10,24),(24,100,30)]:
 rows=json.loads((R/f'objects/scene_{scene:02}/objects.json').read_text())['objects'];row=next(r for r in rows if r['instance_id']==enemy);x,y=row['anchor_px'];s=Scene(scene,{hero:(x-35,y-8),enemy:(x,y)})
 for _ in range(5):s.step()
 out=(I*3)();assert l.s2_session_enemy_target_snapshot(s.h,enemy,out)==0 and out[0]==l.s2_session_player_type(s.h),(scene,list(out),s.actor(enemy)[53])
 runs.append(dict(kind='enemy_sees_small_hero',scene=scene,hero=out[0],enemy_type=row['type'],source_filter=s.actor(enemy)[53]));s.close()
# Cinematic content and navigation repeat even when progress was saved.
l.s2_frontend_create.argtypes=[C.c_char_p]*2;l.s2_frontend_create.restype=P
for n,a in [('sound',[P]),('epilogue',[P,I]),('step',[P,I]),('snapshot',[P,IP]),('render',[P,P,C.c_size_t]),('destroy',[P])]:getattr(l,'s2_frontend_'+n).argtypes=a
h=l.s2_frontend_create(str(R/'android/app/src/main/assets/frontend/menu.s2ui').encode(),str(R/'sprites/bank_328294/bank.s2sp').encode());assert h
l.s2_frontend_test_books.argtypes=[P,I];l.s2_frontend_test_books(h,1)
pix=(C.c_uint32*38400)();state=(I*9)();panels=[]
for group,scene in enumerate([17,5,21,22,15,16]):
 for repeat in [0,1]:
  assert l.s2_frontend_epilogue(h,scene)==1
  for _ in range(17):l.s2_frontend_step(h,0)
  seen=set();effects=[]
  for _ in range(70):
   l.s2_frontend_snapshot(h,state)
   sound=l.s2_frontend_sound(h)
   if sound:effects.append(sound)
   if state[0]!=14:break
   seen.add(state[1]);assert l.s2_frontend_render(h,pix,38400)==0
   if repeat==0 and state[1]not in [v[1]for v in panels if v[0]==group]:
    Image.frombytes('RGBA',(240,160),bytes(pix),'raw','BGRA').resize((720,480),Image.Resampling.NEAREST).save(R/f'previews/stage90_story_{group}_{state[1]}.png');panels.append((group,state[1]))
   l.s2_frontend_step(h,1);l.s2_frontend_step(h,0)
   for _ in range(33):l.s2_frontend_step(h,0)
  assert len(seen)==[4,3,4,3,2,4][group] and state[0]==4 and state[1]==(3 if scene==15 else 4),(group,list(state),seen)
  assert effects==[[102],[3],[90,83],[84],[100],[26,58,83]][group],(group,effects)
  runs.append(dict(kind='epilogue',scene=scene,repeat=repeat,panels=len(seen)))
l.s2_frontend_destroy(h)
(R/'docs/stage90_validation.json').write_text(json.dumps(dict(cases=runs,device_tested=False,scope='Explicit native damage/jump/target-flag fixtures and actual frontend cinematic navigation; no physical Android or complete boss fights.'),indent=2)+'\n');print('PASS Stage90',len(runs),'cases; 20 original post-book panels twice')
