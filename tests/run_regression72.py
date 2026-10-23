#!/usr/bin/env python3
import argparse,concurrent.futures,json,subprocess,time,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];base=R.parent
parser=argparse.ArgumentParser();parser.add_argument('rom',type=Path);parser.add_argument('--jdk',type=Path,required=True);parser.add_argument('--jobs',type=int,default=3);options=parser.parse_args();rom=str(options.rom.resolve());jdk=str(options.jdk.resolve())
skip={'frontend','frontend62','frontend70','stage71_fixes','stage70_fixes','unified_activity','death_music'}
tests=[r['test'] for r in json.loads((R/'docs/stage71_regression_validation.json').read_text())['tests'] if r['test'] not in skip]
logs=R/'docs/stage72_test_logs';logs.mkdir(exist_ok=True)
def run(name):
 if name.endswith('_music_loop'):
  script=R/'tests/verify_music_loop.py';args=['--jdk',jdk]+([]if name=='main_music_loop'else ['--'+name.split('_')[0]])
 else:
  script=R/f'tests/verify_{name}.py';txt=script.read_text();args=[]
  if "add_argument('rom'" in txt or 'add_argument("rom"' in txt or "sys.argv[1]" in txt:args.append(rom)
  if "add_argument('--jdk'" in txt:args+=['--jdk',jdk]
 started=time.monotonic()
 with (logs/f'{name}.log').open('w')as f:p=subprocess.run([sys.executable,str(script),*args],stdout=f,stderr=subprocess.STDOUT)
 row=dict(test=name,passed=p.returncode==0,seconds=round(time.monotonic()-started,2),log=str((logs/f'{name}.log').relative_to(R)))
 print(name,'PASS'if row['passed']else 'FAIL',flush=True);return row
with concurrent.futures.ThreadPoolExecutor(max(1,min(4,options.jobs)))as ex:rows=list(ex.map(run,tests))
report=dict(total=len(rows),passed=sum(x['passed']for x in rows),tests=rows,device_tested=False)
(R/'docs/stage72_regression_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report['passed'],report['total'])

assert report['passed']==report['total'],[x['test']for x in rows if not x['passed']]
