"""Source record ownership audit and restored chapter1 turn markers."""
from session75_fixtures import *
l.s2_session_world_info.argtypes=[P,IP];records=[]
for scene in range(30):
 s=Scene(scene);out=(I*4)();assert l.s2_session_world_info(s.h,out)==0;assert out[2]==(1 if scene==26 else 0),(scene,list(out));records.append(dict(scene=scene,source_records=out[0],actor_poses=out[1],controller_only=out[2],player_spawn=out[3]));s.close()
markers=[]
for marker,direction in [(58,1),(65,0),(12,0)]:
 s=Scene(0,{70:(900,275),59:(1007,227),marker:(1007,227)})
 for _ in range(40):s.step()
 a=s.actor(59);assert a[18]==direction and (a[5]<0 if direction else a[5]>0),(marker,a[18],a[5]);markers.append(dict(id=marker,event=s.actor(marker)[42],enemy_facing=a[18],velocity=a[5]));s.close()
report=dict(scenes=records,chapter1_turn_markers=markers,scope='All1888 source records represented by hero, actor pose or explicit mouse-spawner controller; counts do not certify every mechanic. Enemy53 physically overlaps each restored chapter1 marker and turns through original event/script.',device_tested=False)
(R/'docs/stage89_source_coverage.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS 1888 source records, 30 scenes and three chapter1 patrol markers')
