#!/usr/bin/env python3
"""Real B contacts and Stage57 baseline: preserve source HP, restore normal damage."""
import argparse,ctypes,json,struct,tempfile
from pathlib import Path
from PIL import Image
from session_fixtures import without_intro
ROOT=Path(__file__).resolve().parents[1];I=ctypes.c_int32;IP=ctypes.POINTER(I)
def bind(path):
 l=ctypes.CDLL(str(path));c=l.s2_session_create_level;c.argtypes=[ctypes.c_char_p]*5+[IP];c.restype=ctypes.c_void_p
 for n,a in [('destroy',[ctypes.c_void_p]),('reset',[ctypes.c_void_p]),('actor_snapshot',[ctypes.c_void_p,I,IP]),('snapshot',[ctypes.c_void_p,IP]),('set_viewport',[ctypes.c_void_p,I,I]),('set_auto_restart',[ctypes.c_void_p,I]),('step',[ctypes.c_void_p,I,ctypes.c_void_p,ctypes.c_size_t,IP])]:getattr(l,'s2_session_'+n).argtypes=a
 return l,c
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--baseline',type=Path);args=ap.parse_args();versions=[('current',*bind(ROOT/'native/build/libshrek_scene.so'))]
 if args.baseline:versions.append(('Stage57',*bind(args.baseline.resolve())))
 assets=ROOT/'android/app/src/main/assets/session';paths=[assets/'resources.s2pk',ROOT/'extracted/scene_00/scene.s2lv',ROOT/'collision/scene_00/scene.s2cl',assets/'sprites'];raw=without_intro((ROOT/'objects/scene_00/scene.s2ob').read_bytes());results=[]
 with tempfile.TemporaryDirectory()as td:
  for version,l,c in versions:
   for ident,name,initial,hits in [(31,'peasant',3,1),(9,'bandit',6,2)]:
    for side in [1,2]:
     for w in ([240,480]if version=='current'else[240]):
      data=bytearray(raw);struct.pack_into('<HH',data,18+(ident-1)*44,60,350)
      if side==2:struct.pack_into('<HH',data,18+69*44,90,350);struct.pack_into('<I',data,28+69*44,1)
      f=Path(td)/'scene.s2ob';f.write_bytes(data);err=I();h=c(*[str(p).encode()for p in paths],str(f).encode(),ctypes.byref(err));assert h,err.value;l.s2_session_set_viewport(h,w,160);l.s2_session_set_auto_restart(h,0)
      try:
       pix=(ctypes.c_uint32*(w*160))();info=(I*8)();s=(I*320)();a=(I*216)();lastB=-100;hp=[];drops=[];presses=[];frames=[];trace=[]
       for t in range(1,501):
        b=2 if t==1 else 0
        if version=='current' and t>1 and a[52]>0 and not(a[40]&1):
         dx=a[0]-s[0];dy=a[1]-s[1]
         if abs(dx)<30*256 and abs(dy)<25*256 and s[80]<=1 and t-lastB>28:b=2
         elif abs(dx)>24*256:b=16 if dx>0 else 32
        if b==2:lastB=t;presses.append(t)
        assert l.s2_session_step(h,b,pix,len(pix),info)==0,(version,ident,side,w,t,list(info));l.s2_session_actor_snapshot(h,ident,a);l.s2_session_snapshot(h,s);trace.append([*s,*a])
        if not hp:hp.append(a[52]);assert hp[0]==initial
        elif a[52]<hp[-1]:
         assert s[42]==(1 if version=='current'else 13) and s[41]==(3 if version=='current'else 1)
         drops.append(dict(tick=t,before=hp[-1],after=a[52],impulse_x_q8=a[5],side=s[43]));hp.append(a[52])
         if version=='current' and side==1 and w==240:Image.frombytes('RGBA',(w,160),bytes(pix),'raw','BGRA').resize((960,640),Image.Resampling.NEAREST).save(ROOT/f'previews/native_normal_punch_{name}.png')
        if version=='current' and side==1 and w==240 and t%3==0:frames.append(Image.frombytes('RGBA',(w,160),bytes(pix),'raw','BGRA').convert('RGB').resize((720,480),Image.Resampling.NEAREST))
        if (version=='Stage57' and drops and t>=drops[0]['tick']+20)or(a[40]&1):break
       if version=='current':
        assert hp==([3,0]if ident==31 else[6,3,0]),(ident,side,w,hp,presses)
        assert len(drops)==hits and a[40]&1,(ident,side,w,hp,a[40]);assert len(presses)==hits,(ident,side,w,presses)
        assert all(abs(d['impulse_x_q8'])==640 and d['side']==side for d in drops),drops
        # Reset must replay exactly the same B/movement inputs and physical actor states.
        assert l.s2_session_reset(h)==0
        for t,expected in enumerate(trace,1):
         b=2 if t in presses else 0
         if t not in presses and t>1:
          dx=a[0]-s[0];dy=a[1]-s[1]
          # Reuse recorded held input, which lives in Shrek extra[2].
          b=expected[82]
         assert l.s2_session_step(h,b,pix,len(pix),info)==0;l.s2_session_snapshot(h,s);l.s2_session_actor_snapshot(h,ident,a);assert [*s,*a]==expected,(ident,side,w,t,'reset replay')
       else:assert hp==[initial,initial-1],(name,side,hp)
       if frames:frames[0].save(ROOT/f'previews/native_normal_punch_{name}.gif',save_all=True,append_images=frames[1:],duration=50,loop=0)
       results.append(dict(version=version,enemy=name,width=w,side=side,initial_internal_health=initial,hp_path=hp,B_presses=presses,accepted_hits=drops,removed=bool(a[40]&1)))
      finally:l.s2_session_destroy(h)
 report=dict(runs=results,mismatches=0,forced_damage_events=0,scope='Temporary original type46/type57 near spawn; real player B plus chase contacts, two viewports/facings, exact reset replay. Optional Stage57 host library rebuilt from delivered source ZIP; same assets. No HP overrides, enemy event injection, Android or emulator execution.');(ROOT/'docs/stage58_combat_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
