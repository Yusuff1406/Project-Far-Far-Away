#!/usr/bin/env python3
"""Record selected descriptor/request routes; this does not extract PCM samples."""
import argparse,json,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
from extract import Rom,ROM_BASE
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('rom');a=p.parse_args();r=Rom(a.rom);descriptors=[]
 for offset in [0x53c6c,0x53fb4,0x53fe4]:
  key,priority,volume=struct.unpack_from('<3i',r.data,offset);descriptors.append({'address':ROM_BASE+offset,'sound_id':key,'priority':priority,'volume_q8':volume})
 result={'descriptors':descriptors,'actor_sound_slots':[0x2b4,0x2b8,0x2bc],'audio_manager_pointer_global':0x02003210,'alternating_channel_global':0x0200032c,'request_function':0x080163ac,'low_level_start_function':0x0801d234,'low_level_volume_function':0x0801da20,'scope':'IDs/priorities/volume descriptors and request functions only. No sound bank lookup, PCM/ADPCM extraction, mixer, music playback or hardware audio output.'};(ROOT/'docs/audio_request_resources.json').write_text(json.dumps(result,indent=2)+'\n')
 c=Cs(CS_ARCH_ARM,CS_MODE_THUMB);c.skipdata=True;lines=[]
 for x,y in [(0x163ac,0x1643c),(0x1652c,0x16538),(0x1da20,0x1da88),(0x143fa,0x1445a),(0x143ca,0x143da)]:
  lines.append(f'; {x:06x}..{y:06x}; literal pools may decode as instructions');lines.extend(f'{i.address:08x}: {i.mnemonic} {i.op_str}' for i in c.disasm(r.data[x:y],ROM_BASE+x))
 (ROOT/'docs/original_audio_requests.asm').write_text('\n'.join(lines)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
