from session75_fixtures import *
l.s2_session_level_complete.argtypes=[P]
results=[]
for scene in[4,10,29,3,22,28,12]:
 rows=json.loads((R/f'objects/scene_{scene:02}/objects.json').read_text())['objects'];heroes=[r for r in rows if r['type']in[3,4,5,6,7]];zone=next(r for r in rows if r['type']==148);x,y=zone['anchor_px']
 for together in([False,True]if len(heroes)>1 else[True]):
  placements={zone['instance_id']:(x,y)}
  for i,h in enumerate(heroes):placements[h['instance_id']]=(x-8-i*3 if together or i==0 else x-150,y)
  s=Scene(scene,placements);frames={h['type']:set()for h in heroes}
  try:
   for t in range(550):
    s.step(64 if t%2==0 else 0)
    for h in heroes:
     a=s.hero(h['type'])
     if a[80]==12:frames[h['type']].add(a[22])
    if l.s2_session_level_complete(s.h):break
   assert bool(l.s2_session_level_complete(s.h))==together,(scene,together,s.hero()[80],s.hero()[:2])
   if together:assert all(len(v)>1 for v in frames.values()),(scene,frames)
   results.append(dict(scene=scene,together=together,completed=together));print(results[-1],flush=True)
  finally:s.close()
(R/'docs/stage80_exits_validation.json').write_text(json.dumps(dict(cases=results,device_tested=False,full_routes_tested=False),indent=2)+'\n')
