#!/usr/bin/env python3
"""Regenerate source-evidenced generic/plain/NPC bindings used by chapter01."""
import argparse,json,struct
from pathlib import Path
from extract import Rom
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();rom=Rom(a.rom)
 scripts=json.loads((ROOT/'docs/generic_script_resources.json').read_text())['scripts'];visual=json.loads((ROOT/'docs/campaign_visual_resources.json').read_text())['binding_evidence'];rows={x['type']:(x['initial_animation'],x['script'],0)for x in scripts}
 for x in visual:
  kind=x['type'];ctor=int(x['constructor'],16)
  if kind in rows:continue
  if ctor==0x080180b0:rows[kind]=(int(x['animation_address'],16),0,1)
  if ctor==0x08013600:rows[kind]=(int(x['animation_address'],16),struct.unpack_from('<I',rom.data,int(x['definition'],16)-0x08000000+4)[0],2)
 # Source plate variants27/28/29, two-hero block32, and spawner49.
 # Their specialized native owner logic is in native_session.cpp.
 rows[27]=(0x0834ae20,0,1);rows[28]=(0x0834ae38,0,1);rows[29]=(0x0834ae50,0,1);rows[32]=(0x0834af88,0,1);rows[49]=(0x0831df38,0x0804facc,0)
 rows[33]=(0x0834afa0,0,1);rows[72]=(0x08334994,0,1);rows[45]=(0x0831df80,0x080538dc,0);rows[50]=(0x0831df38,0x0804ff24,0)
 raw=''.join(f'{{{t},0x{a:08x}u,0x{sc:08x}u,{kind}}},\n'for t,(a,sc,kind)in sorted(rows.items()));(ROOT/'native/campaign_actor_bindings.inc').write_text(raw);print(len(rows),'source type bindings')
if __name__=='__main__':main()
