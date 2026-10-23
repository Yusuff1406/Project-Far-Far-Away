#!/usr/bin/env python3
"""Current focused native/Java host regression. No Android device execution."""
import argparse,concurrent.futures,json,subprocess,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom',type=Path);ap.add_argument('--jdk',type=Path,required=True);ap.add_argument('--jobs',type=int,default=3);a=ap.parse_args();rom=str(a.rom.resolve());jdk=str(a.jdk.resolve())
 jobs=[]
 for n in ['stage73','stage73_layers','unified_activity73','dialogue_audio_exit','session_intro','session_dialogues','donkey_chapter','stage72_actors','stage74_captions','stage74_layers','stage74_mushrooms','stage74_ownership','unified_activity74']:
  args=[rom]if n=='stage74_captions'else['--jdk',jdk]if n.startswith('unified_activity')else[];jobs.append((n,[sys.executable,str(R/'tests'/('verify_'+n+'.py')),*args]))
 for name,flags in [('shrek_landing',[]),('donkey_landing',['--donkey'])]:jobs.append((name,[sys.executable,str(R/'tests/verify_shrek_locomotion.py'),rom,'--landing',*flags]))
 logs=R/'docs/stage74_test_logs';logs.mkdir(exist_ok=True)
 def run(job):
  name,cmd=job;start=time.monotonic();p=logs/(name+'.log')
  with p.open('w')as f:code=subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT).returncode
  row=dict(test=name,passed=code==0,seconds=round(time.monotonic()-start,2),log=str(p.relative_to(R)));print(json.dumps(row),flush=True);return row
 with concurrent.futures.ThreadPoolExecutor(max(1,min(4,a.jobs)))as pool:rows=list(pool.map(run,jobs))
 report=dict(total=len(rows),passed=sum(x['passed']for x in rows),tests=rows,device_tested=False);(R/'docs/stage74_regression_validation.json').write_text(json.dumps(report,indent=2)+'\n');assert report['total']==report['passed'],[x for x in rows if not x['passed']]
if __name__=='__main__':main()
