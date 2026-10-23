from pathlib import Path
import subprocess,json
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--baseline',type=Path,required=True);args=ap.parse_args()
root=Path(__file__).resolve().parents[1];fixture=(root/'tests/session75_fixtures.py').read_text().replace("str(R/'native/build/libshrek_scene.so')",'str(Path(sys.argv[1]).resolve())')
code='import sys,time,json,hashlib\n__file__='+repr(str(root/'tests/session75_fixtures.py'))+'\n'+fixture+'''
rows=[]
for scene in [0,23,29]:
 s=Scene(scene)
 for _ in range(30):s.step(64 if l.s2_session_dialogue_active(s.h)else 0)
 samples=[]
 for batch in range(3):
  start=time.perf_counter()
  for t in range(150):s.step(0)
  samples.append((time.perf_counter()-start)*1000/150)
 rows.append(dict(scene=scene,ms_per_frame=samples,final_state_sha256=hashlib.sha256(bytes((I*320)(*s.hero()))).hexdigest()));s.close()
print(json.dumps(rows))
'''
results={}
for label,lib in [('before',args.baseline),('after',root/'native/build/libshrek_scene.so')]:results[label]=json.loads(subprocess.check_output(['python3','-c',code,str(Path(lib).resolve())]))
for old,new in zip(results['before'],results['after']):assert old['final_state_sha256']==new['final_state_sha256']
results['scope']='Host CPU, 240x160, stationary heroes, three batches of150 frames per scene after30 warmup frames. Not Android FPS; final hero state after30 warmup+450 timed frames identical to Stage90.'
(root/'docs/stage91_performance.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results))
