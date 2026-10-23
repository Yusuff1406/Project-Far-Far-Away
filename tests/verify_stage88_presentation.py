"""Bonus book records, five native HUDs and timed black return.
Native execution only; no Android device or full game emulator.
"""
import sys,ast
from session75_fixtures import *
from PIL import Image
for n,a in [('frontend_create',[C.c_char_p]*2),('frontend_destroy',[P]),('frontend_restore',[P,IP]),('frontend_open',[P,I,I]),('frontend_bonus_bests',[P,IP]),('frontend_chapter_coins',[P,IP]),('frontend_snapshot',[P,IP]),('frontend_render',[P,P,C.c_size_t]),('session_set_transitions',[P,I]),('session_minigame_state',[P]),('session_transition_snapshot',[P,IP]),('session_coin_count',[P]),('session_projectile_snapshot',[P,I,IP]),('session_minigame_actor_snapshot',[P,I,IP])]:getattr(l,'s2_'+n).argtypes=a
l.s2_frontend_create.restype=P
h=l.s2_frontend_create(str(R/'android/app/src/main/assets/frontend/menu.s2ui').encode(),str(R/'sprites/bank_328294/bank.s2sp').encode());assert h
scores=[111,222,333,444,555];l.s2_frontend_bonus_bests(h,(I*5)(*scores));l.s2_frontend_chapter_coins(h,(I*75)(*([17]*75)))
tree=ast.parse((R/'tests/verify_five_bonuses.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['actor','gingy','human']],type_ignores=[]),'bonus_inputs','exec'))
canvas=Image.new('RGB',(720,480*5));pix=(C.c_uint32*38400)();state=(I*9)()
for i in range(5):
 l.s2_frontend_restore(h,(I*9)(4,i,5,0,0));l.s2_frontend_open(h,4,i);l.s2_frontend_snapshot(h,state);assert state[8]==scores[i]
 assert l.s2_frontend_render(h,pix,38400)==0
 im=Image.frombytes('RGBA',(240,160),bytes(pix),'raw','BGRA');canvas.paste(im.resize((720,480),Image.Resampling.NEAREST),(0,480*i))
# Story count remains isolated from bonus bests.
l.s2_frontend_restore(h,(I*9)(4,0,0,0,0));l.s2_frontend_snapshot(h,state);assert state[8]==17
l.s2_frontend_destroy(h);canvas.save(R/'previews/stage88_bonus_book.png')
portraits=Image.new('RGB',(720,480*5));loss=[]
# Shrek, Donkey, Cat, Gingy and human Shrek, original scene/objects.
for i,scene in enumerate([26,7,6,18,27]):
 s=Scene(scene);s.step();portraits.paste(Image.frombytes('RGBA',(240,160),bytes(s.pix),'raw','BGRA').resize((720,480),Image.Resampling.NEAREST),(0,480*i))
 assert len(set(s.pix[y*240+x]for y in range(4,25)for x in range(4,25)))>12,'portrait missing'
 # Every original bonus ends naturally with no buttons; then blackens and
 # reports return-ready without any result confirmation input.
 l.s2_session_set_transitions(s.h,1);failed=None;partial=False
 for t in range(1600):
  buttons=gingy(s,s.hero(),t,l.s2_session_coin_count(s.h)) if scene==18 else human(s,s.hero(),t) if scene==27 else 0
  s.step(buttons);mode=l.s2_session_minigame_state(s.h)
  if mode==2 and failed is None:failed=t
  tr=(I*8)();l.s2_session_transition_snapshot(s.h,tr)
  if failed is not None and 0<tr[0]<64:partial=True
  if mode==4:
   assert failed is not None and t>failed and partial
   assert all(c==0xff000000 for c in s.pix),'return before black frame'
   loss.append(dict(scene=scene,failed=failed,black=t));break
 else:raise AssertionError(('bonus did not end',scene))
 s.close()
portraits.save(R/'previews/stage88_bonus_hud.png')
report=dict(bonus_bests=scores,story_coins=17,natural_losses=loss,device_tested=False)
(R/'docs/stage88_presentation_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
