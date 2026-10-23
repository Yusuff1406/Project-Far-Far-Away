#!/usr/bin/env python3
"""Extract data-only motion tables and animation headers for the five protagonists."""
import argparse,json,struct,shutil
from pathlib import Path
from extract import Rom
ROOT=Path(__file__).resolve().parents[1]
TABLES={3:0x0804b73c,4:0x0804c4fc,5:0x0804be94,6:0x0804c1b4,7:0x0804bb4c}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();r=Rom(a.rom);blocks={};report=[]
 for kind,table in TABLES.items():
  motions=[]
  for i in range(40):
   address=table+i*40;v=struct.unpack_from('<10i',r.data,address-0x08000000)
   if v[0]==999:break
   assert 1<=v[0]<=40
   motions.append({'id':v[0],'animation':v[1],'x':v[2:5],'y':v[5:8]});blocks[v[1]]=r.data[v[1]-0x08000000:v[1]-0x08000000+24]
  else:raise AssertionError('missing table sentinel')
  blocks[table]=r.data[table-0x08000000:table-0x08000000+(len(motions)+1)*40]
  report.append(dict(type=kind,table=hex(table),motions=motions))
 blocks[0x0804b6ec]=r.data[0x4b6ec:0x4b6f4];blocks[0x0804b708]=r.data[0x4b708:0x4b70c]
 out=ROOT/'android/app/src/main/assets/campaign';raw=bytearray(struct.pack('<4sII',b'S2PM',1,len(blocks)))
 for address,data in sorted(blocks.items()):raw+=struct.pack('<II',address,len(data))+data
 (out/'player.s2pm').write_bytes(raw)
 for scene in range(30):shutil.copyfile(ROOT/f'android/app/src/main/assets/collision/scene_{scene:02}.s2cl',out/f'scenes/scene_{scene:02}.s2cl')
 (ROOT/'docs/campaign_player_resources.json').write_text(json.dumps(dict(rom_sha256=r.sha256,bytes=len(raw),tables=report,scope='Data only. Shared walk/jump states and Donkey air kick; no executable ROM code.'),indent=2)+'\n');print(len(raw),'bytes',len(blocks),'blocks')
if __name__=='__main__':main()
