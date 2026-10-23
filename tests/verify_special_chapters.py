"""Session integration; short object-placement fixtures are explicitly scoped.
No actor HP, phase or completion flag is injected. This is not a full route bot.
"""
from session75_fixtures import *
from PIL import Image
l.s2_session_level_complete.argtypes=[P]
l.s2_session_special_snapshot.argtypes=[P,I,IP]
l.s2_session_death_restarts.argtypes=[P]

def special(s,id):
 out=(I*16)();assert l.s2_session_special_snapshot(s.h,id,out)==0;return list(out)
def skip(s,t):return 64 if l.s2_session_dialogue_active(s.h)and t%2 else 0
def original_positions(scene):return {r['instance_id']:tuple(r['anchor_px'])for r in json.loads((R/f'objects/scene_{scene:02}/objects.json').read_text())['objects']}
def image(s,name):Image.frombytes('RGBA',(240,160),bytes(s.pix),'raw','BGRA').resize((720,480),Image.Resampling.NEAREST).save(R/'previews'/name)

# Unmodified object files: all four start, retain every record, and render.
for scene in[5,20,15,16]:
 s=Scene(scene)
 for row in s.rows:
  if row['type']not in[3,4,5,6,7]:s.actor(row['instance_id'])
 for t in range(20):s.step(skip(s,t))
 assert not l.s2_session_level_complete(s.h)
 image(s,f'stage81_scene_{scene:02}.png');s.close()

# Puss: real Select contact, carry ownership and source-triggered release.
# Original arena, no placement changes. Nine wall turns precede the window.
s=Scene(5);direction=0;captures=0
for t in range(1100):
 h=s.hero();boss=s.actor(1);st=special(s,1);dx=boss[0]-h[0]
 if l.s2_session_dialogue_active(s.h):b=skip(s,t)
 elif h[83]:b=0
 elif st[0]==3:
  b=(16 if dx>0 else 32)if abs(dx)>12*256 else 0
  if abs(dx)<30*256 and t%8==0:b|=4
 else:
  if h[80]in[0,1]:
   direction=16 if dx>0 else 32
   b=(direction|1)if dx*boss[5]<0 and abs(dx)<60*256 else 0
  else:b=direction
 s.step(b);captures=max(captures,special(s,1)[6])
 if captures and any(q[1]==35 for q in s.requests()):break
assert captures==1 and not l.s2_session_level_complete(s.h)
assert any(q[1]==35 for q in s.requests())and not s.hero()[83]
puss_frames=t+1;s.close()

# Cake: original moving generator damages it and causes a real restart.
s=Scene(20);damaged=False;moving=False
for t in range(700):
 s.step(skip(s,t));damaged|=special(s,6)[1]<11;moving|=s.actor(4)[0]!=35*256
 assert not l.s2_session_level_complete(s.h)
assert damaged and moving and l.s2_session_death_restarts(s.h)>0;s.close()
# Defense fixture narrows only the generator's two movement-marker positions.
# All original objects, original timer/HP/projectile definitions and input remain.
pos=original_positions(20);pos.update({1:(90,7),5:(70,7),2:(80,141)})
s=Scene(20,pos)
for t in range(2300):
 s.step(skip(s,t)if l.s2_session_dialogue_active(s.h)else 64|(2 if t%15==0 else 0))
 if l.s2_session_level_complete(s.h):break
assert l.s2_session_level_complete(s.h)and special(s,6)[1]==11
assert any(q[1]==26 and q[2]==42 for q in s.requests());cake_frames=t+1;s.close()

# First Fairy: relocated boss/flight markers beside original party, no removed
# world objects. Real hero switching and cookies deliver all three hits.
pos=original_positions(15);pos[46]=(100,280)
rows=json.loads((R/'objects/scene_15/objects.json').read_text())['objects']
for row in rows:
 if row['type']==153:pos[row['instance_id']]=(100,280)
s=Scene(15,pos)
for t in range(700):
 b=skip(s,t)if l.s2_session_dialogue_active(s.h)else (256 if l.s2_session_player_type(s.h)!=5 and t%2 else (2 if t%30==0 else 0))
 s.step(b)
 if l.s2_session_level_complete(s.h):break
assert l.s2_session_level_complete(s.h)and special(s,46)[0]==0
assert {90,91,48}<={q[2]for q in s.requests()if q[1]==26}
assert all(s.hero(typ)[80]==12 for typ in[4,5,7]);first_fairy_frames=t+1;s.close()

# Final Fairy timer/ending fixture: retain all objects but put the boss and
# all flight markers outside the combat arena to isolate the complete countdown from damage.
pos=original_positions(16)
for row in json.loads((R/'objects/scene_16/objects.json').read_text())['objects']:
 if row['type']in[153,156]:pos[row['instance_id']]=(7000,20)
s=Scene(16,pos)
for t in range(3300):
 s.step(skip(s,t))
 if l.s2_session_level_complete(s.h):break
assert l.s2_session_level_complete(s.h)and special(s,4)[5]==4
assert any(q[1]==26 and q[2]==50 for q in s.requests())
assert t>=2699 and s.hero()[89]>0;final_fairy_frames=t+1;s.close()
report=dict(original_scenes_started=[5,20,15,16],puss_first_capture_and_release_frames=puss_frames,cake_defended_fixture_frames=cake_frames,fairy155_cookie_fixture_frames=first_fairy_frames,fairy156_timer_fixture_frames=final_fairy_frames,full_campaign_route_certified=False,device_tested=False,scope='Real session buttons. Original Puss first capture/release and cake failure; relocated-object cake defense, Fairy hits/party finish and final timer fixtures. Source controller tests cover three Puss captures separately.')
(R/'docs/special_chapters_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
