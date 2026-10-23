#!/usr/bin/env python3
"""Focused Stage82 host native/Java checks; no Android device execution."""
import argparse,concurrent.futures,json,subprocess,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom',type=Path);ap.add_argument('--jdk',type=Path,required=True);ap.add_argument('--jobs',type=int,default=3);ap.add_argument('--rerun-failed',action='store_true');a=ap.parse_args();rom=str(a.rom.resolve());jdk=str(a.jdk.resolve())
 plain=['stage73','stage75_layers','dialogue_audio_exit','session_intro','session_dialogues','donkey_chapter','stage72_actors','stage74_mushrooms','stage74_ownership','stage75_coop','stage75_jump','stage72_stress','stage76_additions','stage76_party','session_hurt','puss_world','stage79_layers']
 jobs=[(n,[sys.executable,str(R/'tests'/('verify_'+n+'.py'))])for n in plain]
 jobs +=[(n,[sys.executable,str(R/'tests'/('verify_'+n+'.py')),rom])for n in ['stage74_captions','session_lift','session_world','puss_actions','puss_rail_actions','enemy_scripts','new_world_actor_scripts','stage77','stage78','stage79']]
 jobs.append(('unified_activity75',[sys.executable,str(R/'tests/verify_unified_activity75.py'),'--jdk',jdk]))
 for n,flags in [('shrek_landing',[]),('donkey_landing',['--donkey'])]:jobs.append((n,[sys.executable,str(R/'tests/verify_shrek_locomotion.py'),rom,'--landing',*flags]))
 jobs.append(('shrek_fire',[sys.executable,str(R/'tests/verify_shrek_locomotion.py'),rom,'--fire']))
 jobs.append(('stage80',[sys.executable,str(R/'tests/verify_stage80.py')]))
 jobs.append(('projectile_actors',[sys.executable,str(R/'tests/verify_projectile_actors.py'),rom]))
 jobs.append(('stage80_mechanisms',[sys.executable,str(R/'tests/verify_stage80_mechanisms.py')]))
 jobs.append(('stage80_exits',[sys.executable,str(R/'tests/verify_stage80_exits.py')]))
 for name in ['target_generator','bonus_actor_scripts','cake_controller','fairy155','fairy156','puss_boss','puss_boss_frames','fairy155_frames','fairy156_frames']:jobs.append((name,[sys.executable,str(R/'tests'/('verify_'+name+'.py')),rom]))
 jobs.append(('five_bonuses',[sys.executable,str(R/'tests/verify_five_bonuses.py'),rom]))
 jobs.append(('new_world_bonus',[sys.executable,str(R/'tests/verify_new_world_bonus.py'),rom]))
 jobs.append(('special_chapters',[sys.executable,str(R/'tests/verify_special_chapters.py')]))
 logs=R/'docs/stage82_test_logs';logs.mkdir(exist_ok=True)
 previous=[]
 if a.rerun_failed:
  previous=json.loads((R/'docs/stage82_regression_validation.json').read_text())['tests'];failed={x['test']for x in previous if not x['passed']};known={x['test']for x in previous};jobs=[job for job in jobs if job[0]in failed or job[0]not in known]
 def run(job):
  name,cmd=job;start=time.monotonic();target=logs/(name+'.log')
  with target.open('w')as f:code=subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT).returncode
  row=dict(test=name,passed=code==0,seconds=round(time.monotonic()-start,2),log=str(target.relative_to(R)));print(json.dumps(row),flush=True);return row
 with concurrent.futures.ThreadPoolExecutor(max(1,min(4,a.jobs)))as pool:rows=list(pool.map(run,jobs))
 if previous:
  updates={x['test']:x for x in rows};known={x['test']for x in previous};rows=[updates.get(x['test'],x)for x in previous]+[x for n,x in updates.items()if n not in known]
 report=dict(total=len(rows),passed=sum(x['passed']for x in rows),tests=rows,device_tested=False);(R/'docs/stage82_regression_validation.json').write_text(json.dumps(report,indent=2)+'\n');assert report['total']==report['passed'],[x for x in rows if not x['passed']]
if __name__=='__main__':main()
