#!/usr/bin/env python3
"""Shipping type6 slopes do not depend on BIOS-angle boundary rounding."""
import ctypes,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];l=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));f=l.s2_puss_rail_angle;f.argtypes=[ctypes.c_int,ctypes.c_int];rows=[];slopes=set();margins=[]
for p in sorted((ROOT/'collision').glob('scene_*/collision.json')):
 for s in json.loads(p.read_text())['segments']:
  if s['type']!=6:continue
  a,b,c,d=s['endpoints'];dx,dy=c-a,d-b;assert dx>0;angle=f(dx,dy);distance=min(abs(angle-512),abs(angle-3584));expected=21 if abs(dy)==dx else 22;assert(21 if distance<128 else 22)==expected
  margin=abs(distance-128);assert margin>32,(p.name,s,angle);margins.append(margin);slopes.add((dx,dy));rows.append(dict(scene=p.parent.name,segment=s['index'],angle=angle,motion=expected))
report=dict(segments=len(rows),distinct_slopes=len(slopes),minimum_selection_boundary_margin=min(margins),mismatches=0,scope='Native-angle animation classification on all shipped type6 segments, independent source-data diagonal classification. This is not a BIOS ArcTan2 bit-exact comparison.',rows=rows)
(ROOT/'docs/puss_rail_geometry_validation.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items()if k!='rows'})
