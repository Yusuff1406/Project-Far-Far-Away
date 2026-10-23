#!/usr/bin/env python3
"""Selected chapter01 actors against isolated original generic updates."""
import ctypes as C,json,struct,sys,tempfile
from pathlib import Path
from verify_generic_runtime import Original,Rom,ROOT,IP
from extract_collision import scene_collision
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_PC,UC_ARM_REG_LR
r=Rom(sys.argv[1]);lib=C.CDLL(str(ROOT/'native/build/libshrek_scene.so'));P=C.c_void_p;I=C.c_int32
lib.s2_session_create_level.argtypes=[C.c_char_p]*5+[IP];lib.s2_session_create_level.restype=P
lib.s2_session_step.argtypes=[P,I,C.POINTER(C.c_uint32),C.c_size_t,IP];lib.s2_session_actor_snapshot.argtypes=[P,I,IP];lib.s2_session_destroy.argtypes=[P]
source=json.loads((ROOT/'objects/scene_01/objects.json').read_text())['objects'];bindings={x['type']:x for x in json.loads((ROOT/'docs/generic_script_resources.json').read_text())['scripts']};types=[9,22,38,62,76,78];cases=0
with tempfile.TemporaryDirectory()as td:
 raw=bytearray((ROOT/'objects/scene_01/scene.s2ob').read_bytes());struct.pack_into('<HH',raw,18+44,6000,0);path=Path(td)/'scene.s2ob';path.write_bytes(raw);err=I();h=lib.s2_session_create_level(*[str(x).encode()for x in[ROOT/'android/app/src/main/assets/session/resources.s2pk',ROOT/'extracted/scene_01/scene.s2lv',ROOT/'collision/scene_01/scene.s2cl',ROOT/'android/app/src/main/assets/session/sprites',path]],C.byref(err));assert h,err.value
 try:
  originals={};state=(I*216)();pix=(C.c_uint32*38400)();info=(I*8)()
  for kind in types:
   row=next(x for x in source if x['type']==kind);lib.s2_session_actor_snapshot(h,row['instance_id'],state);o=Original(r)
   o.u.mem_write(0x02000800,struct.pack('<3I',0x08000000+scene_collision(r,1)['root_offset'],3432*256,432*256))
   def hooks(uc,address,size,data):
    if address in [0x080163ac,0x0800bf04,0x0800bee8,0x0800bec0]:uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   o.u.hook_add(UC_HOOK_CODE,hooks);o.ctor(bindings[kind]['definition'],tuple(v*256 for v in row['anchor_px']),row['flags_byte']);o.u.mem_write(o.actor+0x178,struct.pack('<2i',*state[:2]));o.u.mem_write(o.actor+0x190,struct.pack('<4i',*state[32:36]));o.seed(state);o.call(0x08013344,o.vm,bindings[kind]['script']);originals[kind]=(row['instance_id'],o)
  for tick in range(1,91):
   assert lib.s2_session_step(h,0,pix,len(pix),info)==0
   for kind,(id,o)in originals.items():
    for global_ in [0x0200324c,0x020033e0]:o.u.mem_write(global_,struct.pack('<i',tick))
    o.call(0x08018208,o.actor);assert lib.s2_session_actor_snapshot(h,id,state)==0
    if kind in [9,22]:o.u.mem_write(o.actor+0x15d,bytes([o.u.mem_read(o.actor+0x15d,1)[0]|8]))
    diff={i:(state[i],v)for i,v in o.snapshot().items()if state[i]!=v};assert not diff,(kind,tick,diff)
    assert list(state[:2])==list(struct.unpack('<2i',o.u.mem_read(o.actor+0x178,8))),(kind,tick,'position');cases+=1
 finally:lib.s2_session_destroy(h)
report=dict(types=types,original_actor_frames=cases,mismatches=0,scope='Original isolated13714/18208 with chapter01 collision tree. Registry, broadcasts, camera and audio delivery are fixtures;9/22 emitted surface bit supplied. Does not certify inter-object dynamics or climbing.')
(ROOT/'docs/chapter_actor_scripts_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
