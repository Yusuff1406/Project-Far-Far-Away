#!/usr/bin/env python3
"""Focused Stage73 native and Java/JNI host checks; no Android device execution."""
import argparse,concurrent.futures,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--jdk',type=Path,required=True);ap.add_argument('--jobs',type=int,default=3);a=ap.parse_args();jdk=str(a.jdk.resolve())
 tests=['stage73','stage73_layers','unified_activity73','dialogue_audio_exit','session_intro','session_dialogues','donkey_chapter'];logs=ROOT/'docs/stage73_test_logs';logs.mkdir(exist_ok=True)
 def run(name):
  started=time.monotonic();cmd=[sys.executable,str(ROOT/'tests'/('verify_'+name+'.py'))]+(['--jdk',jdk]if name=='unified_activity73'else[]);target=logs/(name+'.log')
  with target.open('w')as out:result=subprocess.run(cmd,cwd=ROOT,stdout=out,stderr=subprocess.STDOUT)
  row=dict(test=name,passed=result.returncode==0,seconds=round(time.monotonic()-started,2),log=str(target.relative_to(ROOT)));print(json.dumps(row),flush=True);return row
 with concurrent.futures.ThreadPoolExecutor(max(1,min(4,a.jobs)))as pool:rows=list(pool.map(run,tests))
 report=dict(total=len(rows),passed=sum(x['passed']for x in rows),tests=rows,device_tested=False);(ROOT/'docs/stage73_regression_validation.json').write_text(json.dumps(report,indent=2)+'\n');assert report['passed']==report['total'],[x['test']for x in rows if not x['passed']]
if __name__=='__main__':main()
