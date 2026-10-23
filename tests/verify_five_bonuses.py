"""Original new bonus arenas and scoped parent entry/award/resume fixtures."""
import struct,sys
from session75_fixtures import *
from PIL import Image
for name,args in [('minigame_state',[P]),('coin_count',[P]),('bonus_index',[P]),('bonus_best',[P]),('set_bonus_best',[P,I]),('set_bonus_results',[P,I]),('set_transitions',[P,I]),('minigame_snapshot',[P,IP]),('minigame_actor_snapshot',[P,I,IP]),('projectile_snapshot',[P,I,IP]),('target_generator_snapshot',[P,I,IP]),('transition_snapshot',[P,IP])]:getattr(l,'s2_session_'+name).argtypes=args

def mini(s):
 out=(I*320)();assert l.s2_session_minigame_snapshot(s.h,out)==0;return list(out)
def actor(s,id,child=False):
 out=(I*216)();result=(l.s2_session_minigame_actor_snapshot if child else l.s2_session_actor_snapshot)(s.h,id,out);return None if result else list(out)
def gingy(s,h,age,score,child=False):
 b=16 if h[0]<180*256 else 32 if h[0]>184*256 else 0;elves=[];pumpkins=[]
 for id in range(4,30):
  a=actor(s,id,child)
  if a is None or a[40]&1:continue
  if a[47]in[0x0831de90,0x0831de60]:elves.append(a)
  elif a[47]==0x08342d6c:pumpkins.append(a)
 target=any(abs(a[0]+a[5]*30-h[0])<12*256 for a in elves)
 safe=not any(abs(a[0]+a[5]*20-h[0])<30*256 for a in pumpkins)
 # After the reward threshold, intentionally finish through the original pumpkin.
 if ((target and safe)or score>=3)and age%2==0:b|=64|2
 return b

def human(s,h,age):
 # A short original-arena run: dodge/counter until the source fall-death ends it.
 bolts=[];out=(I*82)()
 for i in range(l.s2_session_projectile_snapshot(s.h,-1,out)):
  l.s2_session_projectile_snapshot(s.h,i,out)
  if out[0]==146 and out[44]==38:bolts.append((abs(out[2]-h[0]),out[2]-h[0]))
 b=0
 if bolts:
  distance,dx=min(bolts)
  if distance<75*256:b|=16 if dx>0 else 32
  if distance<55*256 and age%2==0:b|=2
 if age%50==0:b|=1
 return b

# Five source scenes retain every source record, their own bonus indices/records.
starts=[]
for scene,index in[(26,0),(7,1),(6,2),(18,3),(27,4)]:
 s=Scene(scene);assert l.s2_session_bonus_index(s.h)==index
 assert l.s2_session_set_bonus_best(s.h,10+index)==0
 assert l.s2_session_bonus_best(s.h)==10+index
 for t in range(12):s.step()
 assert l.s2_session_minigame_state(s.h)==1
 if index>=3:
  for row in s.rows:
   if row['type']not in[5,7]:s.actor(row['instance_id'])
  Image.frombytes('RGBA',(240,160),bytes(s.pix),'raw','BGRA').resize((720,480),Image.Resampling.NEAREST).save(R/f'previews/stage82_bonus_{index:02}.png')
 starts.append(dict(scene=scene,index=index,source_rows=len(s.rows)));s.close()

# Unmodified Gingy arena: real movement/up+B, score, source acceleration and
# pumpkin failure. No actor HP/phase/score/completion mutation.
s=Scene(18)
for t in range(700):
 h=s.hero();score=l.s2_session_coin_count(s.h);s.step(gingy(s,h,t,score))
 if l.s2_session_minigame_state(s.h)==2:break
score=l.s2_session_coin_count(s.h);assert score>=3 and l.s2_session_minigame_state(s.h)==2 and s.hero()[89]==3
out=(I*5)();assert l.s2_session_target_generator_snapshot(s.h,1,out)==0
assert out[2]==256+score*12
assert l.s2_session_target_generator_snapshot(s.h,3,out)==0 and out[2]==256
assert any(q[1]==1 and q[4:6]==[0,24]for q in s.requests());gingy_score=score;gingy_frames=t+1;s.close()

# Original human arena: source146 is reflected (101/13), reaches a145 elf,
# awards the source pair of points, then a normal fall ends this short run.
s=Scene(27);reflected=False
for t in range(800):
 h=s.hero();s.step(human(s,h,t));out=(I*82)()
 for i in range(l.s2_session_projectile_snapshot(s.h,-1,out)):
  l.s2_session_projectile_snapshot(s.h,i,out)
  reflected|=out[0]==146 and out[43]==101 and out[44]==13
 if l.s2_session_minigame_state(s.h)==2:break
assert reflected and l.s2_session_coin_count(s.h)>=2 and l.s2_session_minigame_state(s.h)==2
human_score=l.s2_session_coin_count(s.h);human_frames=t+1;s.close()

# Real B talk and original dialogue65/66. Only the parent NPC/other objects
# are repositioned to isolate entry; bonus arenas keep original object files.
flows=[]
for scene,npc,hero,xy,index in[(3,42,95,(62,285),3),(29,79,103,(93,522),4)]:
 s=Scene(scene,{hero:xy,npc:(xy[0]-10,xy[1]+5)})
 l.s2_session_set_bonus_results(s.h,1);l.s2_session_set_transitions(s.h,1)
 started=failed=returned=None;score=0;frozen=None
 for t in range(1500):
  mode=l.s2_session_minigame_state(s.h);b=2 if t==40 else (64 if t%2 else 0)
  if mode==1:
   h=mini(s);score=h[312]
   b=gingy(s,h,h[316],score,True)if index==3 else (1 if h[316]%50==0 else 0)|(2 if h[316]%20==0 else 0)
  elif mode==2:b=1 if failed is not None and t>failed+25 and t%2 else 0
  s.step(b);mode=l.s2_session_minigame_state(s.h)
  if mode:
   if started is None:started=t;frozen=s.hero()
   assert s.hero()==frozen,'parent simulation advanced during bonus'
   assert l.s2_session_bonus_index(s.h)==index
   if mode==2 and failed is None:failed=t
  elif started is not None:
   returned=t;assert s.hero()==frozen;break
 assert started is not None and failed is not None and returned is not None
 assert returned>failed and l.s2_session_bonus_best(s.h)>=score
 tr=(I*8)();assert l.s2_session_transition_snapshot(s.h,tr)==0 and tr[5]==score
 # The first new mode earns a physical reward; the second short flow may score0.
 if index==3:assert score>=3 and tr[7]>=1
 expected=list(tr[7:8])
 for _ in range(200):s.step()
 rewards=[q for q in s.requests()if q[1]==30]
 assert len(rewards)==1
 if index==3:assert rewards[0][4]==84
 flows.append(dict(scene=scene,bonus_index=index,entered=started,failed=failed,returned=returned,score=score,reward_requests=rewards,parent_frozen=True));s.close()

# All original reward tables and boundary scores, source091A4.
from verify_generic_runtime import Original,Rom,FC
o=Original(Rom(sys.argv[1]));reward=l.s2_bonus_rewards;reward.argtypes=[I,I,FC,P,IP];cases=0
@FC
def fetch(a,out,n,ctx):
 for i,v in enumerate(struct.unpack('<'+'i'*n,o.u.mem_read(a,n*4))):out[i]=v
 return 1
for index in range(5):
 for score in[-2147483648,-1,*range(101),2147483647]:
  o.u.mem_write(o.actor,bytes(40));o.u.mem_write(o.actor+0x18,struct.pack('<2i',index,score));o.call(0x080091a4,o.actor);out=(I*4)();assert reward(index,score,fetch,None,out)>=0 and list(out)==list(struct.unpack('<4i',o.u.mem_read(o.actor+4,16)));cases+=1
report=dict(source_scenes=starts,original_gingy_score=gingy_score,original_gingy_frames=gingy_frames,original_human_reflection_score=human_score,original_human_frames=human_frames,parent_flows=flows,reward_source_cases=cases,mismatches=0,full_routes_tested=False,device_tested=False,scope='Original bonus files and real buttons, generator notices, human reflection and loss, five record indices. Parent NPC/other objects moved only to isolate talk/return/reward. No forced score, HP or phase. Not maximum-score or device certification.')
(R/'docs/five_bonuses_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
