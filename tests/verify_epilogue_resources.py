"""Post-book image/caption/voice records from original script initializer."""
import sys,json,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from extract import Rom
from extract_session_sfx import GaxOracle
from extract_frontend import POST_STORIES
r=Rom(sys.argv[1]);o=GaxOracle(r.data);o.call(0x08019f94);ram=bytes(o.u.mem_read(0x02000000,0x40000));locations=[[0x3ff0,0x4038,0x4074,0x40bc],[0x3f00,0x3f54,0x3f90],[0x3dc8,0x3e1c,0x3e58,0x3ea0],[0x3cd8,0x3d20,0x3d68],[0x3c24,0x3c6c],[0x3ac8,0x3b1c,0x3b7c,0x3bb8]];voices=[]
for group,locs in enumerate(locations):
 for loc,(image,caption)in zip(locs,POST_STORIES[group]):
  assert struct.unpack_from('<3I',ram,loc)==(3,0,image)
  assert struct.pack('<3I',7,2,caption)in ram[loc:loc+96]
for loc in [0x4080,0x3f18,0x3dec,0x3e64,0x3d38,0x3c78]:
 cmd=struct.unpack_from('<3I',ram,loc);assert cmd[:2]==(5,11);effect,priority,gain=struct.unpack_from('<3i',r.data,cmd[2]-0x8000000);assert (R/f'android/app/src/main/assets/session/audio/sfx_{effect}.wav').exists();voices.append(dict(effect=effect,priority=priority,gain=gain,source=hex(0x2000000+loc)))
meta=json.loads((R/'docs/frontend_resources.json').read_text());catalog=json.loads((R/'objects/campaign_catalog.json').read_text())['records'];assert [catalog[i]['scene']for i in [4,9,14,19,24]]==[17,5,21,22,16]
report=dict(panels=sum(map(len,POST_STORIES)),groups=6,source_records=[[hex(0x2000000+x)for x in a]for a in locations],voices=voices,device_tested=False,scope='Original initializer script records and packaged source sprites/fonts/captions; scene routing follows original chapter-book catalog. Does not execute uninterrupted boss fights.')
(R/'docs/epilogue_resource_validation.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS 20 original cinematic image/caption records and six voice descriptors')
