#!/usr/bin/env python3
"""Bundle already extracted ROM resource blocks for the native session loader."""
import hashlib,json,shutil,struct
from replay_generic_actor import ROOT,Resources
def main():
 res=Resources();pickup=json.loads((ROOT/'objects/coin_pickup_resources.json').read_text());res.blocks.update({int(a):bytes.fromhex(raw) for a,raw in pickup['blocks'].items()});out=ROOT/'android/app/src/main/assets/session';out.mkdir(parents=True,exist_ok=True)
 font=json.loads((ROOT/'objects/dialogue_font_resources.json').read_text());res.blocks={**{int(a):bytes.fromhex(raw)for a,raw in font['blocks'].items()},**res.blocks}
 raw=bytearray(struct.pack('<4sIII',b'S2PK',1,len(res.blocks),len(res.animations)))
 for address,data in res.blocks.items():raw+=struct.pack('<II',address,len(data))+data
 banks=set()
 for a in res.animations:
  name=(a['bank']+'/bank.s2sp').encode('ascii');raw+=struct.pack('<III',a['address'],a['index'],len(name))+name;banks.add(a['bank'])
 for bank in sorted(banks):
  target=out/'sprites'/bank;target.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'sprites'/bank/'bank.s2sp',target/'bank.s2sp')
 (out/'resources.s2pk').write_bytes(raw)
 # First leprechaun bonus uses original scene26, not story cutscene05.
 for target in [out/'minigame_00',ROOT/'extracted/scene_00/minigame_00']:
  target.mkdir(parents=True,exist_ok=True)
  for source in [ROOT/'extracted/scene_26/scene.s2lv',ROOT/'collision/scene_26/scene.s2cl',ROOT/'objects/scene_26/scene.s2ob',ROOT/'objects/scene_26/objects.json']:
   shutil.copyfile(source,target/source.name)
 for target in [out/'minigame_01',*[ROOT/f'extracted/scene_{scene:02}/minigame_01'for scene in [1,14,21]]]:
  target.mkdir(parents=True,exist_ok=True)
  for source in [ROOT/'extracted/scene_07/scene.s2lv',ROOT/'collision/scene_07/scene.s2cl',ROOT/'objects/scene_07/scene.s2ob',ROOT/'objects/scene_07/objects.json']:
   shutil.copyfile(source,target/source.name)
 for target in [out/'minigame_02',ROOT/'extracted/scene_23/minigame_02']:
  target.mkdir(parents=True,exist_ok=True)
  for source in [ROOT/'extracted/scene_06/scene.s2lv',ROOT/'collision/scene_06/scene.s2cl',ROOT/'objects/scene_06/scene.s2ob',ROOT/'objects/scene_06/objects.json']:shutil.copyfile(source,target/source.name)
 for index,scene in [(3,18),(4,27)]:
  for target in [out/f'minigame_{index:02}',*[ROOT/f'extracted/scene_{world:02}/minigame_{index:02}'for world in [3,19,22,29,28,12,15]]]:
   target.mkdir(parents=True,exist_ok=True)
   for source in [ROOT/f'extracted/scene_{scene:02}/scene.s2lv',ROOT/f'collision/scene_{scene:02}/scene.s2cl',ROOT/f'objects/scene_{scene:02}/scene.s2ob',ROOT/f'objects/scene_{scene:02}/objects.json']:shutil.copyfile(source,target/source.name)
 report={'version':1,'blocks':len(res.blocks),'animations':len(res.animations),'sprite_banks':len(banks),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'scope':'Previously extracted script, animation, frame and contact blocks. No complete ROM.'}
 (ROOT/'docs/native_session_package.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
