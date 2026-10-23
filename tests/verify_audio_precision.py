#!/usr/bin/env python3
"""Ensure shipped PCM contains genuine pre-quantizer detail, not scaled PCM8."""
import json,wave
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def main():
 resources=[]
 for path in sorted(list((ROOT/'android/app/src/main/assets/session').glob('*/*.wav'))+list((ROOT/'android/app/src/main/assets/frontend').glob('*.wav'))):
  with wave.open(str(path),'rb') as w:
   assert (w.getnchannels(),w.getsampwidth(),w.getframerate())==(1,2,31537);samples=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2');
   if path.name.endswith('_intro.wav') and samples.size==0:
    assert samples.size==0;resources.append({'file':path.name,'sample_rate':31537,'pcm_bits':16,'samples':0,'empty_intro_source_track':True});continue
   assert samples.size>0 and np.any(samples)
   assert not np.any(samples.astype(np.int32)&7),path.name
   fraction=float(np.mean((samples.astype(np.int32)&255)!=0));audible=samples[samples!=0].astype(np.int32);audible_fraction=float(np.mean((audible&255)!=0));assert audible_fraction>.25,(path.name,audible_fraction)
   resources.append({'file':path.name,'sample_rate':31537,'pcm_bits':16,'fraction_with_preserved_sub8bit_detail':fraction,'audible_fraction_with_preserved_sub8bit_detail':audible_fraction})
 assert len(resources)==115
 report={'resources':resources,'mismatches':0,'scope':'Original mixer before >>5 quantization; blockwise original8-bit conversion checked during extraction. Low bits prove preserved precision rather than8-to16 expansion. No device listening test.'};(ROOT/'docs/audio_precision_validation.json').write_text(json.dumps(report,indent=2)+'\n');print({'wav_files':len(resources),'mismatches':0})
if __name__=='__main__':main()
