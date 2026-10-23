#!/usr/bin/env python3
"""Resource slice for native script fetches; not a complete game ROM."""
import argparse,json,struct,hashlib
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
from extract import Rom,ROM_BASE
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();r=Rom(a.rom);start,end=0x24000,0x56000;payload=r.data[start:end];path=ROOT/'objects/generic_script_resources.s2rs';path.write_bytes(b'S2RS'+struct.pack('<3I',1,ROM_BASE+start,len(payload))+payload)
 bindings=json.loads((ROOT/'docs/object_sprite_bindings.json').read_text())['types'];scripts=[]
 for typ,info in bindings.items():
  script=struct.unpack_from('<I',r.data,info['definition']-ROM_BASE+4)[0];assert ROM_BASE+start<=script<ROM_BASE+end;scripts.append({'type':int(typ),'definition':info['definition'],'script':script,'initial_animation':info['animation'],'bank':info['bank'],'animation_index':info['index']})
 (ROOT/'docs/generic_script_resources.json').write_text(json.dumps({'resource_base':ROM_BASE+start,'resource_bytes':len(payload),'payload_sha256':hashlib.sha256(payload).hexdigest(),'scripts':scripts,'scope':'Original lower resource tables required by selected script/constructor routes. External actor handlers and sprite pointers may reference other packages. This slice does not implement or describe complete behavior.'},indent=2)+'\n')
 c=Cs(CS_ARCH_ARM,CS_MODE_THUMB);c.skipdata=True;lines=[]
 for x,y in [(0x12f9c,0x13394),(0x13714,0x137f4),(0x180b0,0x18208)]:
  lines.append(f'; {x:06x}..{y:06x}; literal pools may decode as instructions');lines.extend(f'{i.address:08x}: {i.mnemonic} {i.op_str}' for i in c.disasm(r.data[x:y],ROM_BASE+x))
 (ROOT/'docs/original_generic_actor_and_vm.asm').write_text('\n'.join(lines)+'\n');print(json.dumps({'resource_bytes':len(payload),'script_roots':len(scripts)}))
if __name__=='__main__':main()
