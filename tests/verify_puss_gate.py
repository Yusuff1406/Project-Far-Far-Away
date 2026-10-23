#!/usr/bin/env python3
"""Actual139 constructor/contact: crossing latch, score and8/16 animations."""
import ctypes as C,json,struct,random,sys
from verify_generic_runtime import Original,Rom,ROOT,IP,FC
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
r=Rom(sys.argv[1]);o=Original(r);o.camera_fixture=False;u=o.u;l=C.CDLL(str(ROOT/'native/build/libshrek_scene.so'));I=C.c_int32
@FC
def fetch(a,out,n,ctx):
 try:raw=u.mem_read(a,n*4)
 except Exception:return 0
 for i,v in enumerate(struct.unpack('<'+'i'*n,raw)):out[i]=v
 return 1
SINK=C.CFUNCTYPE(C.c_int,C.c_int,C.c_uint32,I,C.c_void_p);native=[];source=[]
@SINK
def sink(k,a,v,ctx):native.append([k,a,v]);return 0
def hooks(uc,a,size,ctx):
 if a==0x08009288:source.extend([[29,0,0],[1,0x08024cdc,0]]);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
u.hook_add(UC_HOOK_CODE,hooks)
init=l.s2_puss_gate_init;init.argtypes=[IP,C.c_int,I,FC,C.c_void_p,IP,IP]
contact=l.s2_puss_gate_contact;contact.argtypes=[IP,IP,IP,C.c_int,I,FC,SINK,C.c_void_p]
hero_init=l.s2_generic_runtime_init;hero_init.argtypes=[IP,C.c_int,C.c_uint32,I,FC,C.c_void_p,IP]
s=(I*80)();state=(I*2)();hero=(I*80)();anchor=(I*2)(118*256,108*256);assert init(anchor,0,0,fetch,None,s,state)==0
u.mem_write(0x02007000,struct.pack('<2i',*anchor));o.call(0x08000cfc,o.actor,0x0833ce8c,0x02007000,0);gate_sprite=struct.unpack('<I',u.mem_read(o.actor+0x1c0,4))[0]
binding=json.loads((ROOT/'docs/object_sprite_bindings.json').read_text())['types']['18'];target=0x02008000;u.mem_write(target,bytes(0x1000));u.mem_write(0x02007100,bytes(32));o.call(0x08013714,target,binding['definition'],0x02007000,0x02007100);sp=struct.unpack('<I',u.mem_read(target+0x1c0,4))[0]
rng=random.Random(202669);transitions=[]
for tick in range(1,3001):
 x=119 if tick%4==1 else 210 if tick%4==3 else rng.randrange(240);y=rng.randrange(25,130);blocked=int(tick%17==0)
 assert hero_init((I*2)(x*256,y*256),tick%2,0x08344c1c,tick,fetch,None,hero)==0
 u.mem_write(target+0x170,struct.pack('<hhBBH',hero[26],hero[27],hero[30],hero[31],0));u.mem_write(target+0x178,struct.pack('<2i',*hero[:2]));u.mem_write(target+0x168,struct.pack('<i',blocked));u.mem_write(sp+4,struct.pack('<4I',hero[21],hero[47],hero[22],hero[23]));u.mem_write(sp+0x28,bytes([hero[18],0]));u.mem_write(0x0200324c,struct.pack('<i',tick));source.clear();native.clear()
 o.call(0x08000c28,o.actor,target);assert contact(s,state,hero,blocked,tick,fetch,sink,None)==0
 expected=list(struct.unpack('<2i',u.mem_read(o.actor+0x1cc,8)));assert list(state)==expected,(tick,list(state),expected);assert source==native
 assert s[47]==struct.unpack('<I',u.mem_read(gate_sprite+8,4))[0]
 if state[1]in [8,16]and source:transitions.append([state[1],hex(s[47])])
assert transitions==[[8,'0x833cea4'],[16,'0x833cebc']],transitions
report=dict(original_contact_cases=3000,gate_scores=state[1],threshold_animations=transitions,mismatches=0,scope='Actual0CFC/0C28 and source target hurt-box query. Score manager fixture; no full-route/device claim.')
(ROOT/'docs/puss_gate_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
