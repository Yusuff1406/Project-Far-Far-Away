#!/usr/bin/env python3
"""Isolated original B67C/B624 plus initialized movie scripts; no device/game execution."""
import sys,ctypes,struct,json,random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from extract import Rom
from extract_session_sfx import GaxOracle
rom=Rom(sys.argv[1]);o=GaxOracle(rom.data);lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));I=ctypes.c_int32
lib.s2_menu_line_begin.argtypes=[ctypes.POINTER(I),I,I,I,I];lib.s2_menu_line_step.argtypes=[ctypes.POINTER(I)]
rng=random.Random(60);pairs=[(0,0,0,0),(40,68,178,115),(178,115,40,68)]+[tuple(rng.randrange(-40,241)for _ in range(4))for _ in range(200)];steps=0
for x,y,tx,ty in pairs:
 state=(I*10)();lib.s2_menu_line_begin(state,x,y,tx,ty);base=0x02030000;o.u.mem_write(base,bytes(40));o.u.mem_write(base+0x100,struct.pack('<4i',x,y,tx,ty));o.call(0x0800b67c,base,base+0x100,base+0x108)
 # Original dominant flag is a byte; the unused padding is initialized to zero.
 assert bytes(state)==bytes(o.u.mem_read(base,40)),(x,y,tx,ty,list(state),struct.unpack('<10i',o.u.mem_read(base,40)))
 for _ in range(max(abs(tx-x),abs(ty-y))):
  o.call(0x0800b624,base);lib.s2_menu_line_step(state);assert bytes(state)==bytes(o.u.mem_read(base,40));steps+=1
 assert list(state)[:2]==[tx,ty];before=bytes(state);assert lib.s2_menu_line_step(state)==1 and bytes(state)==before
# Compare resources to the original initialized cutscene records, not guessed FLC names.
o.call(0x08019f94);ram=bytes(o.u.mem_read(0x02000000,0x40000));meta=json.loads((ROOT/'docs/frontend_resources.json').read_text());boot=[];story=[]
for at in range(0x44b8,0x45d8,12):
 command,arg,pointer=struct.unpack_from('<3I',ram,at)
 if command==3 and arg==0:boot.append(pointer)
for at in range(0x4104,0x4224,12):
 command,arg,pointer=struct.unpack_from('<3I',ram,at)
 if command==3:story.append(pointer)
assert boot==[int(row['address'],16)for row in meta['images'][9:13]],boot
assert story==[int(row['address'],16)for row in meta['images'][13:17]],story
report=dict(original_motion_cases=len(pairs),original_motion_steps=steps,original_boot_movie_addresses=[hex(v)for v in boot],original_story_image_addresses=[hex(v)for v in story],mismatches=0,device_tested=False,scope='Isolated original Thumb helpers and script initializer under Unicorn. Native navigation and timing are touch adaptations, not full game emulation.')
(ROOT/'docs/frontend_original_motion_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
