#!/usr/bin/env python3
"""Original 30 song bindings, 13 PCM tracks and Java loop playback contracts."""
import argparse,ast,hashlib,json,struct,subprocess,sys,tempfile,wave
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from extract import Rom
from extract_session_sfx import GaxOracle
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('--jdk',type=Path,required=True);a=ap.parse_args();a.jdk=a.jdk.resolve();r=Rom(a.rom);oracle=GaxOracle(r.data);oracle.call(0x08019648)
 catalog=json.loads((ROOT/'objects/campaign_catalog.json').read_text())['records']
 for row in catalog:assert oracle.word(0x020033f0+row['original_slot']*32+28)==row['music_song']
 meta=json.loads((ROOT/'docs/campaign_music_resources.json').read_text());assert meta['count']==13
 tree=ast.parse((ROOT/'tests/verify_music_loop.py').read_text());stubs=ast.literal_eval(next(n.value for n in ast.walk(tree)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='stubs'for t in n.targets)))
 results=[];precision=0
 with tempfile.TemporaryDirectory()as td:
  folder=Path(td);sources=[]
  for name,body in stubs.items():p=folder/'android/media'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(body);sources.append(str(p))
  for name in['LoopMusic.java','MusicPcm.java']:sources.append(str(ROOT/'android/app/src/main/java/org/shrek2/research'/name))
  sources.append(str(ROOT/'tests/java/org/shrek2/research/MusicLoopTest.java'));subprocess.run([str(a.jdk/'bin/javac'),'-d',td,*sources],check=True)
  for song in meta['songs']:
   address=int(song['song'],16);paths=[];pcm=[]
   for resource in song['resources']:
    path=ROOT/'android/app/src/main/assets/campaign/music'/resource['file'];assert hashlib.sha256(path.read_bytes()).hexdigest()==resource['sha256']
    with wave.open(str(path),'rb')as w:assert(w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes())==(1,2,31537,resource['samples']);data=w.readframes(w.getnframes())
    v=np.frombuffer(data,dtype='<i2').astype(np.int32)
    if v.size:assert np.any(v)and not np.any(v&7)and np.mean((v&255)!=0)>.25;precision+=1
    paths.append(path);pcm.append(data)
   # Independently rerun the source mixer, compare the actual first eight blocks.
   source=GaxOracle(r.data,rate=31537,song=address);source.call(0x0801d428,-1,256);first=b''.join(source.mix_precise()for _ in range(8));assert (pcm[0]+pcm[1])[:len(first)]==first
   output=subprocess.check_output([str(a.jdk/'bin/java'),'-cp',td,'org.shrek2.research.MusicLoopTest',*(str(x)for x in paths)],text=True).strip();results.append(dict(song=song['song'],java=output))
 report=dict(original_song_bindings=30,compositions=len(results),wav_resources=26,nonempty_pcm_precision_checks=precision,original_mixer_blocks_compared=8*13,java_loop_tests=results,mismatches=0,device_tested=False)
 (ROOT/'docs/campaign_audio_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
