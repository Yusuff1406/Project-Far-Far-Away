#!/usr/bin/env python3
"""Package original maps, sprite banks and factory-proven visual placements.
This package describes graphics; it never marks missing gameplay as implemented.
"""
import argparse,json,struct,shutil,hashlib
from pathlib import Path
from extract import Rom
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();rom=Rom(a.rom)
 banks={p.parent.name:json.loads(p.read_text())for p in (ROOT/'sprites').glob('*/bank.json')}
 preferred=['shrek_ogre','donkey','puss_in_boots','bank_337308','shrek_human']
 names=preferred+sorted(set(banks)-set(preferred));lookup={}
 for name,b in banks.items():
  for anim in b['animations']:lookup[anim['record_offset']+0x08000000]=(name,anim['index'])
 traces=json.loads((ROOT/'docs/object_factory_traces.json').read_text())['types'];bindings={};evidence=[]
 for row in traces:
  if len(row['calls'])!=1:continue
  c=row['calls'][0];ctor=c['constructor'];definition=c['registers'][1];animation=None;offset=None
  if ctor in[0x08013714,0x080005b4,0x08013600,0x08002690,0x08009e34,0x08001730,0x08011b6c,0x0801271c,0x0801b4a0,0x080121a4]:offset=0
  elif row['type']in[3,4,5,6,7]:offset=4
  elif ctor in[0x080180b0,0x08000cfc]:animation=definition
  if offset is not None and 0x08000000<=definition<0x08000000+len(rom.data)-4-offset:animation=struct.unpack_from('<I',rom.data,definition-0x08000000+offset)[0]
  if animation not in lookup:continue
  name,index=lookup[animation];bindings[row['type']]=(names.index(name),index)
  evidence.append(dict(type=row['type'],constructor=hex(ctor),definition=hex(definition),animation_address=hex(animation),definition_offset=offset,bank=name,animation_index=index))
 # Player definitions have the exact initial animation at +4; generic constructors +0.
 out=ROOT/'android/app/src/main/assets/campaign';out.mkdir(parents=True,exist_ok=True)
 raw=bytearray(struct.pack('<4s3I',b'S2CP',1,len(names),30))
 for name in names:
  encoded=name.encode();raw+=struct.pack('<2I',len(encoded),banks[name]['animation_count'])+encoded
  dest=out/'sprites'/name;dest.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'sprites'/name/'bank.s2sp',dest/'bank.s2sp')
 rows=json.loads((ROOT/'objects/campaign_catalog.json').read_text())['records'];report=[]
 for row in rows:
  scene=row['scene'];objects=json.loads((ROOT/f'objects/scene_{scene:02}/objects.json').read_text())['objects'];spawn=next((x['anchor_px']for x in objects if x['type']in[3,4,5,6,7]),[row['width']//2,row['height']//2])
  raw+=struct.pack('<7I',scene,row['width'],row['height'],row['music_song'],*spawn,len(objects));mapped=0;unknown=[]
  for obj in objects:
   bank,anim=bindings.get(obj['type'],(-1,-1));mapped+=bank>=0
   if bank<0:unknown.append(obj['type'])
   raw+=struct.pack('<7i',obj['instance_id'],obj['type'],*obj['anchor_px'],obj['flags_byte']&3,bank,anim)
  dest=out/'scenes';dest.mkdir(exist_ok=True);shutil.copyfile(ROOT/f'extracted/scene_{scene:02}/scene.s2lv',dest/f'scene_{scene:02}.s2lv')
  report.append(dict(scene=scene,catalog_order=row['thumbnail_order'],width=row['width'],height=row['height'],placements=len(objects),visual_bindings=mapped,unresolved_primary_types=sorted(set(unknown)),music_song=hex(row['music_song']),gameplay_available=scene==0))
 (out/'catalog.s2cp').write_bytes(raw)
 meta=dict(rom_sha256=rom.sha256,banks=names,animation_count=sum(b['animation_count']for b in banks.values()),visual_type_bindings=len(bindings),binding_evidence=evidence,scenes=report,total_placements=sum(x['placements']for x in report),bound_placements=sum(x['visual_bindings']for x in report),catalog_sha256=hashlib.sha256(raw).hexdigest(),scope='Original static placements with initial animations. Actor AI, collision interactions, boss scripts, companion switching and chapter progression are not supplied by this graphics package.')
 (ROOT/'docs/campaign_visual_resources.json').write_text(json.dumps(meta,indent=2)+'\n');print({k:meta[k]for k in['animation_count','visual_type_bindings','total_placements','bound_placements']})
if __name__=='__main__':main()
