from pathlib import Path
exec((Path(__file__).parent/'verify_fairy155.py').read_text().split("compare('ctor')")[0])
step=l.s2_fairy155_step;step.argtypes=[IP,IP,IP,IP,I,I,FC,SINK,P]
for tick in range(1,501):
 fx.clear();orig.clear();u.mem_write(0x020033e0,struct.pack('<i',tick));u.mem_write(0x0200324c,struct.pack('<i',tick));o.call(0x08018208,o.actor);assert step(p,s,markers,target,1,tick,fetch,sink,None)==0;compare(('frame',tick));xy=struct.unpack('<2i',u.mem_read(o.actor+0x178,8));assert list(p[:2])==list(xy),(tick,list(p[:2]),xy)
report=dict(full_frames=tick,mismatches=0,scope='Original18208 update, full position/physics/animation/behavior of155, no hero damage.');(ROOT/'docs/fairy155_frames_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
