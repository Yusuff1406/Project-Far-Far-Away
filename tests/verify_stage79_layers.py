#!/usr/bin/env python3
"""Compare actual foreground effect pixels against the independently rendered sprites."""
import verify_stage75_layers as layer
from session75_fixtures import *
runs=[]
for scene,typ,xy in[(14,81,(392,320)),(13,82,(1850,255))]:
 rows=json.loads((R/f'objects/scene_{scene:02}/objects.json').read_text())['objects'];item=next(r['instance_id']for r in rows if r['type']==typ);hero=next(r['instance_id']for r in rows if r['type']==3 or(scene==14 and r['type']==6))
 s=Scene(scene,{hero:xy,item:xy})
 try:
  s.step();layer.pix=s.pix;n=layer.compare(s.h,s.actor(item),s.hero());assert n>5
  runs.append(dict(scene=scene,item_type=typ,foreground_pixels_verified=n))
 finally:s.close()
(R/'docs/stage79_layers_validation.json').write_text(json.dumps(dict(cases=runs,device_tested=False),indent=2)+'\n');print(runs)
