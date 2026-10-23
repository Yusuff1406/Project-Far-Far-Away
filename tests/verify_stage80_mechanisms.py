from session75_fixtures import *
from PIL import Image
l.s2_session_level_complete.argtypes=[P]
results=[]
# Required-three push block: preserve source hero anchor differences.
for joint in[False,True]:
 s=Scene(4,{67:(139,344),68:(139,352),69:(139,342),62:(160,344)})
 try:
  for _ in range(20):s.step()
  x=s.actor(62)[0]
  for _ in range(60):s.step(16|(768 if joint else 0))
  distance=(s.actor(62)[0]-x)/256;assert (distance>30 if joint else abs(distance)<1),(joint,distance)
  results.append(dict(three_hero_block_joint=joint,distance=distance))
 finally:s.close()
# Three-weight plate retains all original actors; a linked gate only opens with three.
for all_three in[False,True]:
 pos={48:(1047,473),47:(1143,455),69:(1046,453),70:(1047,448)}
 if all_three:pos[67]=(1048,442)
 s=Scene(12,pos)
 try:
  for _ in range(100):s.step()
  notices=[q for q in s.requests()if q[1]==1 and q[4:7]==[9,3,2]]
  assert bool(notices)==all_three and bool(s.actor(47)[39]&3)!=all_three,(all_three,notices,s.actor(47)[39])
  results.append(dict(three_weight_plate=all_three,notices=len(notices)))
 finally:s.close()
# Source finite spawners + actual Shrek attacks close the first arena.
s=Scene(17,{9:(99,142),2:(140,75),11:(140,75),3:(140,119),12:(140,119),4:(130,149),6:(130,149)})
try:
 for t in range(2600):
  hero=s.hero();targets=[]
  for id in range(1,30):
   actor=(I*216)()
   if l.s2_session_actor_snapshot(s.h,id,actor)==0 and not(actor[40]&1) and actor[42]in[37,38,39]:targets.append(list(actor))
  target=min(targets,key=lambda a:abs(a[0]-hero[0]))if targets else None
  direction=(16 if target[0]>hero[0]else 32)if target and abs(target[0]-hero[0])>20*256 else 0
  s.step((64 if t%2 else 0)if l.s2_session_dialogue_active(s.h)else (direction|(2 if t%25==0 else 0)|(1 if t%65==0 else 0)))
  if l.s2_session_level_complete(s.h):break
 assert l.s2_session_level_complete(s.h),(t,s.hero()[80:96]);assert any(q[1]==26 and q[4]==10 for q in s.requests());results.append(dict(arena_frames=t))
finally:s.close()
# Render HUD for every new hero and a three-hero party.
for scene in[29,3,12]:
 s=Scene(scene)
 try:
  for t in range(120):s.step(64 if t%2 else 0)
  Image.frombytes('RGBA',(240,160),bytes(s.pix),'raw','BGRA').resize((720,480),Image.Resampling.NEAREST).save(R/f'previews/stage80_hud_{scene:02}.png')
  for typ,maxhp in({7:6}if scene==29 else{5:3}if scene==3 else{7:6,5:3,4:4}).items():assert s.hero(typ)[89]==maxhp,(scene,typ,s.hero(typ)[88:96])
 finally:s.close()
(R/'docs/stage80_mechanisms_validation.json').write_text(json.dumps(dict(cases=results,device_tested=False,full_routes_tested=False),indent=2)+'\n');print(results)
