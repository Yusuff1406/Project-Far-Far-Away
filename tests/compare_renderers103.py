#!/usr/bin/env python3
"""Compare real old/new ARGB outputs for sprite palettes, flips and clipping."""
import argparse,ctypes as C,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('previous',type=Path);a.add_argument('current',type=Path);args=a.parse_args()
libs=[C.CDLL(str(p.resolve())) for p in [args.previous,args.current]]
for l in libs:
 l.s2_sprite_bank_create.argtypes=[C.c_char_p];l.s2_sprite_bank_create.restype=C.c_void_p
 l.s2_sprite_bank_destroy.argtypes=[C.c_void_p]
 l.s2_sprite_bank_info.argtypes=[C.c_void_p,C.c_int,C.POINTER(C.c_int32)]
 l.s2_sprite_composite_bank_palette.argtypes=[C.c_void_p]+[C.c_int]*7+[C.c_void_p,C.c_size_t,C.c_int]
 l.s2_sprite_composite_transform.argtypes=[C.c_void_p]+[C.c_int]*7+[C.c_void_p,C.c_size_t]
count=0;buffers=[(C.c_uint32*(240*160))() for l in libs]
for path in sorted((R/'android/app/src/main/assets/session/sprites').rglob('*.s2sp')):
 handles=[l.s2_sprite_bank_create(str(path).encode()) for l in libs];assert all(handles);row=(C.c_int32*8)();libs[0].s2_sprite_bank_info(handles[0],0,row);animations=row[0]
 for animation in range(animations):
  assert libs[0].s2_sprite_bank_info(handles[0],animation,row)==0
  for seq in {0,row[1]//2,row[1]-1}:
   for mirror in range(4):
    for x,y in [(120,80),(-4,3),(239,158)]:
     for i,l in enumerate(libs):
      C.memset(buffers[i],37,C.sizeof(buffers[i]));assert l.s2_sprite_composite_transform(handles[i],animation,seq,mirror,240,160,x,y,buffers[i],38400)==0
     assert bytes(buffers[0])==bytes(buffers[1]),(path,animation,seq,mirror,x,y);count+=1
   for palette in {0,animation,animations-1}:
    for i,l in enumerate(libs):
     C.memset(buffers[i],11,C.sizeof(buffers[i]));assert l.s2_sprite_composite_bank_palette(handles[i],animation,seq,1,240,160,120,80,buffers[i],38400,palette)==0
    assert bytes(buffers[0])==bytes(buffers[1]),(path,animation,seq,palette);count+=1
 for l,h in zip(libs,handles):l.s2_sprite_bank_destroy(h)
print(json.dumps({'sprite_comparisons':count,'exact_ARGB':True}))
