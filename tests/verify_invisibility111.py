"""Original Thumb predicates and incoming damage routing, with a virtual hurt stub."""
import sys,struct,json
from pathlib import Path
from verify_generic_runtime import Original,Rom
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_PC,UC_ARM_REG_LR
r=Path(__file__).resolve().parents[1];o=Original(Rom(sys.argv[1]));u=o.u;stub=0x03000f00;calls=[]
u.mem_write(stub,b'\x70\x47')
def hook(uc,a,size,data):
 if a==stub:calls.append(a);uc.reg_write(UC_ARM_REG_R0,1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
u.hook_add(UC_HOOK_CODE,hook)
rows=[]
for mode in range(8):
 u.mem_write(o.actor,bytes(0x1000));u.mem_write(o.actor+0x258,struct.pack('<i',mode));o.call(0x0800ed9c,o.actor);excluded=u.reg_read(UC_ARM_REG_R0);assert excluded==int(mode==5)
 for immune in [0,0x7fffffff]:
  vtable=0x02010000;u.mem_write(vtable,bytes(0x400));u.mem_write(vtable+0x1c8,struct.pack('<II',0,stub|1));u.mem_write(vtable+0x180,struct.pack('<II',0,stub|1));u.mem_write(o.actor,struct.pack('<I',vtable));u.mem_write(o.actor+0x1d0,struct.pack('<i',immune));u.mem_write(0x020033e0,struct.pack('<i',100));u.mem_write(0x02007300,struct.pack('<3i',1,37,1));calls.clear();o.call(0x0800e3a0,o.actor,0x02007300);assert bool(calls)==(immune<=100),(mode,immune,calls)
  rows.append(dict(mode=mode,immunity_deadline=immune,excluded_from_target=excluded,damage_delivered=bool(calls)))
(r/'docs/invisibility111_original.json').write_text(json.dumps({'cases':rows,'scope':'Original ED9C/E3A0 Thumb executed with a virtual hurt-handler stub; proves filtering and damage dispatch, not every enemy AI sequence or device playback.'},indent=2)+'\n')
print('PASS original ROM: mode5 invisible target predicate; damage still dispatched without a separate immunity deadline (16 cases)')
