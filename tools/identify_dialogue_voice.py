#!/usr/bin/env python3
"""Compare a user recording with offline original GAX candidates; no game execution."""
import argparse,hashlib,json,subprocess,tempfile,wave
from pathlib import Path
import numpy as np
from scipy import signal
from extract_session_sfx import GaxOracle
ROOT=Path(__file__).resolve().parents[1]
def pcm(path):
 with wave.open(str(path))as w:
  assert(w.getnchannels(),w.getsampwidth(),w.getframerate())==(1,2,31537)
  return np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom',type=Path);ap.add_argument('recording',type=Path);a=ap.parse_args();rom=a.rom.read_bytes();sos=signal.butter(4,[200,8000],fs=31537,btype='bandpass',output='sos');results=[]
 with tempfile.TemporaryDirectory()as td:
  p=Path(td)/'record.wav';subprocess.run(['ffmpeg','-v','error','-i',str(a.recording),'-vn','-ac','1','-ar','31537',str(p)],check=True);record=signal.sosfilt(sos,pcm(p))
  for sid in [49,54,60,86,89,90,100]:
   oracle=GaxOracle(rom,rate=31537);raw,ticks=oracle.render(sid);b=signal.sosfilt(sos,np.frombuffer(raw,dtype='<i2').astype(float));b=b[:np.flatnonzero(abs(b)>max(abs(b))*.01)[-1]+1];best=(0.,0.,1.)
   scales=list(np.arange(.992,.998,.00005))if sid==86 else [1,.99,1.01,.995,1.005,31537/32768,32768/31537]
   for scale in scales:
    bb=signal.resample(b,int(len(b)*scale));corr=signal.correlate(record,bb,mode='valid',method='fft');norm=np.sqrt(np.maximum(signal.convolve(record*record,np.ones(len(bb)),mode='valid',method='fft'),0)*sum(bb*bb));v=abs(corr)/np.maximum(norm,1);i=int(np.argmax(v));best=max(best,(float(v[i]),i/31537,float(scale)))
   results.append(dict(sound_id=sid,correlation=best[0],recording_offset_seconds=best[1],time_scale=best[2]));print(results[-1],flush=True)
 winner=max(results,key=lambda x:x['correlation']);assert winner['sound_id']==86 and winner['correlation']>.8
 descriptor=[int(x)for x in np.frombuffer(rom[0x53cf0:0x53cfc],dtype='<i4')];assert descriptor==[86,-100,200]
 report=dict(recording_sha256=hashlib.sha256(a.recording.read_bytes()).hexdigest(),rom_sha256=hashlib.sha256(rom).hexdigest(),candidates=results,winner=winner,descriptor_address='08053CF0',descriptor=descriptor,scope='Audio waveform comparison in200..8000Hz against original offline GAX effects; recording contains music and lossy AAC. Time scale compensates recording/emulator rate difference. Close occurs around8s in frames. Native first-dialogue completion placement follows recording; original global resume scheduling has not been independently recovered. No Android/device execution.')
 (ROOT/'docs/dialogue_voice_identification.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
