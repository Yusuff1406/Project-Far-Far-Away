from pathlib import Path
remaining=2700
prefix=(Path(__file__).parent/'verify_fairy156.py').read_text().split("compare('ctor')")[0]
exec(prefix.replace('elif a==0x08003a9c:ret=1800','elif a==0x08003a9c:ret=remaining'))
step=l.s2_fairy156_step;step.argtypes=[IP,IP,IP,IP,IP,I,I,I,FC,SINK,P]
for tick in range(1,2700):
 remaining=2700-tick
 fx.clear();orig.clear();u.mem_write(0x020033e0,struct.pack('<i',tick));u.mem_write(0x0200324c,struct.pack('<i',tick));o.call(0x08003164,o.actor);assert step(p,s,aux,markers,target,tick,remaining,0,fetch,sink,None)==0;compare(('frame',tick));xy=struct.unpack('<2i',u.mem_read(o.actor+0x178,8));assert list(p[:2])==list(xy),(tick,list(p[:2]),xy)
# The original subclass owns a plain auxiliary actor at+1E0.
aux_actor=struct.unpack('<I',u.mem_read(o.actor+0x1e0,4))[0];assert aux_actor
aux_sprite=struct.unpack('<I',u.mem_read(aux_actor+0x1c0,4))[0]
assert list(aux[:2])==list(struct.unpack('<2i',u.mem_read(aux_actor+0x178,8)))
expected={18:u.mem_read(aux_sprite+0x28,1)[0],38:u.mem_read(aux_sprite+0x29,1)[0],20:u.mem_read(aux_sprite,1)[0],21:struct.unpack('<i',u.mem_read(aux_sprite+4,4))[0],47:struct.unpack('<i',u.mem_read(aux_sprite+8,4))[0],22:struct.unpack('<i',u.mem_read(aux_sprite+12,4))[0],23:struct.unpack('<i',u.mem_read(aux_sprite+16,4))[0]}
assert {i:aux[i]for i in expected}==expected,({i:aux[i]for i in expected},expected)
report=dict(full_frames=tick,mismatches=0,scope='Original18208 update, full position/physics/animation/behavior of156, forced source countdown31, ending dialogue50, no hero damage.');(ROOT/'docs/fairy156_frames_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
