#!/usr/bin/env python3
"""Render every nonzero source effect, with both original GAX slots compared."""
import argparse,hashlib,json,struct,wave
from extract_session_sfx import GaxOracle,ROOT
from extract import Rom

def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();r=Rom(a.rom)
 # Contiguous pointer table:104 instrument definitions, followed by80808080.
 table=0x08056c48;end=0x08056de8
 pointers=struct.unpack_from('<104I',r.data,table-0x08000000)
 assert pointers==tuple(0x080550bc+68*i for i in range(104))
 assert struct.unpack_from('<I',r.data,end-0x08000000)[0]==0x80808080
 out=ROOT/'android/app/src/main/assets/session/audio';out.mkdir(parents=True,exist_ok=True);items=[]
 for sound in range(1,len(pointers)):
  o=GaxOracle(r.data,rate=31537);pcm,ticks=o.render(sound)
  other=GaxOracle(r.data,rate=31537);assert other.render(sound,1)==(pcm,ticks)
  p=out/f'sfx_{sound}.wav'
  with wave.open(str(p),'wb')as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(o.rate);w.writeframes(pcm)
  items.append(dict(sound_id=sound,instrument=pointers[sound],file=p.name,sample_rate=o.rate,samples=len(pcm)//2,driver_ticks=ticks,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),pcm_sha256=hashlib.sha256(pcm).hexdigest()))
 report=dict(effects=items,rom_sha256=r.sha256,instrument_pointer_table=table,instrument_pointer_table_end=end,instrument_count=len(pointers),excluded_ids=[0],excluded_reason='Source sound descriptor0 is the no-effect sentinel; instrument0 does not terminate. Native request filtering already suppresses ID0.',scope='All103 nonzero source FX instruments. Original offline GAX at31537Hz before final8-bit quantizer; both source slots compared byte for byte. WAV playback uses Android SoundPool; original triggers only where corresponding mechanics are ported. No device listening test.')
 (ROOT/'docs/complete_sfx_resources.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(dict(effects=len(items),both_slots_equal=True,total_samples=sum(x['samples']for x in items))))
if __name__=='__main__':main()
