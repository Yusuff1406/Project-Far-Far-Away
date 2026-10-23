#!/usr/bin/env python3
"""Run Stage59 host regression suites; never starts Android or a device."""
import argparse,concurrent.futures,json,subprocess,time,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom',type=Path);ap.add_argument('--jdk',type=Path,required=True);ap.add_argument('--jobs',type=int,default=3);a=ap.parse_args();rom=str(a.rom.resolve());jdk=str(a.jdk.resolve())
 names=['session_world','session_decorations','session_lift','session_stomp','session_enemies','session_bandits','session_peasant','session_hurt','session_bounce_height','session_environment','session_breakables','session_coins','session_audio','dialogue_font','audio_precision','scene_music','session_intro','session_dialogues','dialogue_audio_exit','session_minigame','stage57_presentation','stage57_bonus','session_water_visuals','session_hints_hud','stage57','scene_punch','bandit_strong_scripts','peasant_strong_scripts','player_audio_cues','victory_audio','frontend','frontend_resources']
 jobs=[(n,['python3','tests/verify_'+n+'.py',*([]if n in['dialogue_audio_exit','frontend','audio_precision','session_audio']else[rom])])for n in names]
 jobs +=[(n,['python3','tests/verify_music_loop.py',*flags,'--jdk',jdk])for n,flags in [('main_music_loop',[]),('bonus_music_loop',['--bonus']),('menu_music_loop',['--menu'])]];jobs.append(('death_music',['python3','tests/verify_death_music.py','--jdk',jdk]));logdir=Path(tempfile.mkdtemp(prefix='shrek59-checks-'))
 def run(job):
  name,cmd=job;t=time.monotonic();log=logdir/(name+'.log')
  with log.open('w')as f:p=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
  result=dict(test=name,passed=p.returncode==0,seconds=round(time.monotonic()-t,2),log=str(log));print(json.dumps(result),flush=True);return result
 with concurrent.futures.ThreadPoolExecutor(max(1,min(4,a.jobs)))as pool:rows=list(pool.map(run,jobs))
 report=dict(total=len(rows),passed=sum(x['passed']for x in rows),tests=rows,device_tested=False);(ROOT/'docs/stage59_regression_validation.json').write_text(json.dumps(report,indent=2)+'\n');assert report['passed']==report['total'],[x for x in rows if not x['passed']]
if __name__=='__main__':main()
