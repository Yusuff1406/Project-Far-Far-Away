#!/usr/bin/env python3
"""Correct prior climbing assumption; check source RNG recurrence."""
import ctypes as C,json,random,struct,sys
from verify_generic_runtime import Original,Rom,ROOT,IP
from unicorn.arm_const import UC_ARM_REG_R0
lib=C.CDLL(str(ROOT/'native/build/libshrek_scene.so'));I=C.c_int32;u32=C.c_uint32;o=Original(Rom(sys.argv[1]));u=o.u;rng=random.Random(66)
lib.s2_source_random.argtypes=[C.POINTER(u32)];lib.s2_shrek_receive.argtypes=[IP,IP,IP,I]
for t in range(4000):
 seed=rng.getrandbits(32);s=u32(seed);u.mem_write(0x02000000,struct.pack('<I',seed));o.call(0x0800021a);actual=lib.s2_source_random(C.byref(s));assert actual==u.reg_read(UC_ARM_REG_R0);assert s.value==struct.unpack('<I',u.mem_read(0x02000000,4))[0]
ignored=0
for state in range(22):
 for eventId in range(33,37):
  actor=o.actor;u.mem_write(actor+0x1d8,struct.pack('<i',state));event=(I*3)(0,eventId,0);u.mem_write(0x02007200,struct.pack('<3i',*event));before=bytes(u.mem_read(actor,0x270));o.call(0x0800e3a0,actor,0x02007200);assert u.reg_read(UC_ARM_REG_R0)==0 and bytes(u.mem_read(actor,0x270))==before
  e=(I*8)(state);status=(I*8)();assert lib.s2_shrek_receive(e,status,event,0)==0 and e[0]==state;ignored+=1
report=dict(source_random_cases=4000,original_ignored_marker_events=ignored,states=list(range(22)),event_ids=[33,34,35,36],mismatches=0,scope='Original Donkey vtable receive5C=E3A0 explicitly ignores marker events in every state; climbing was incorrectly listed as a missing Donkey action. No invented climbing action added. Source0021A RNG is exact; bonus owner uses its own seed from parent tick, not a whole-ROM RNG stream.')
(ROOT/'docs/donkey_source_edges_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
