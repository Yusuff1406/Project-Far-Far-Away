#!/usr/bin/env python3
"""Five native bonus starts, scores and two parent entry/return/reward fixtures.
No ROM oracle or Android device is run by this test.
"""
import sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tests'))
source=(R/'tests/verify_five_bonuses.py').read_text().split('# All original reward tables')[0]
exec(compile(source,str(R/'tests/verify_five_bonuses.py'),'exec'))
report=dict(source_scenes=starts,parent_flows=flows,gingy_score=gingy_score,human_reflection_score=human_score,device_tested=False,rom_reward_oracle_run=False,scope='Five original bonus arenas start; real native buttons in Gingy/human scoring and two relocated-parent return/reward fixtures. Java/JNI entry for every hero checked separately in unified_activity75.')
(R/'docs/stage85_bonus_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS five native bonus starts, scoring, reflection and two parent return/reward flows')
