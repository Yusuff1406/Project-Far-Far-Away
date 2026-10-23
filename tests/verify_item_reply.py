#!/usr/bin/env python3
"""Original generic pair -> Shrek incoming override with no surface append."""
import argparse,ctypes,json,random,struct
from verify_generic_runtime import Original,ROOT,IP,FC,Rom
RECEIVE=ctypes.CFUNCTYPE(ctypes.c_int,IP,ctypes.c_void_p)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();o=Original(Rom(a.rom));u=o.u;lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));rng=random.Random(1818)
 pair=lib.s2_generic_contact_pair_receiver;pair.argtypes=[IP,IP,FC,RECEIVE,ctypes.c_void_p,IP];receive=lib.s2_shrek_receive;receive.argtypes=[IP,IP,IP,ctypes.c_int32];source=0x02005000;target=0x02004000;sourceSprite=0x0200d000;targetSprite=0x0200e000;o.camera_fixture=False
 @FC
 def fetch(addr,out,n,ctx):
  try:raw=u.mem_read(addr,n*4)
  except Exception:return 0
  for i,v in enumerate(struct.unpack('<'+'i'*n,raw)):out[i]=v
  return 1
 def seed(addr,sprite,s,vt):
  u.mem_write(addr,struct.pack('<I',vt));u.mem_write(addr+0x15c,bytes([s[40]]));u.mem_write(addr+0x15d,b'\x00');u.mem_write(addr+0x170,struct.pack('<hhBBH',s[26],s[27],s[30],s[31],0));u.mem_write(addr+0x178,struct.pack('<2i',*s[:2]));u.mem_write(addr+8,struct.pack('<2i',*s[28:30]));u.mem_write(addr+0x1a0,struct.pack('<3i',*s[41:44]));u.mem_write(addr+0x1c0,struct.pack('<I',sprite));u.mem_write(sprite+8,struct.pack('<2i',s[47],s[22]));u.mem_write(sprite+0x28,bytes([s[18],s[38]]))
 hits=accepted=0
 for case in range(3000):
  ss=(ctypes.c_int32*80)();ts=(ctypes.c_int32*80)();e=(ctypes.c_int32*8)();status=(ctypes.c_int32*8)();ss[0]=rng.randint(-100000,100000);ss[1]=rng.randint(-100000,100000);ts[0]=ss[0]+rng.randint(-8000,8000);ts[1]=ss[1]+rng.randint(-12000,12000)
  for s,anim in [(ss,0x08342dcc),(ts,0x0834f25c)]:
   raw=bytes(u.mem_read(anim,24));s[26],s[27],s[30],s[31]=struct.unpack_from('<hhBB',raw,12);s[47]=anim;s[22]=0;s[18]=rng.randrange(2);s[38]=rng.randrange(2);s[28:30]=[17,-19]
  ss[40]=rng.choice([0,4,8,12,16,20,24,28]);ts[40]=rng.choice([0,8]);ss[41:44]=[rng.randrange(5),rng.choice(list(range(15,24))+[25,27,29]),-123];e[0]=rng.choice([0,1,6,8,13]);e[1]=rng.randrange(8);e[3]=77 if case%3 else 0;status[0]=3;status[1]=rng.randrange(5);status[3]=rng.randrange(256);status[4]=rng.randint(-10000,10000);status[5]=rng.randrange(256);tick=rng.randint(-10000,10000)
  seed(source,sourceSprite,ss,0x0200268c);seed(target,targetSprite,ts,0x020017cc)
  for off,value in [(0x1d8,e[0]),(0x258,e[1]),(0x1ec,0x02007000 if e[3] else 0),(0x200,status[0]),(0x1fc,status[1]),(0x1d0,status[4])]:u.mem_write(target+off,struct.pack('<i',value))
  u.mem_write(target+0x20c,bytes([status[3]]));u.mem_write(target+0x1c8,bytes([status[5]]));u.mem_write(0x020033e0,struct.pack('<i',tick))
  @RECEIVE
  def reply(event,ctx):return receive(e,status,event,tick)
  o.call(0x080184f8,source,target);d=(ctypes.c_int32*4)();assert pair(ss,ts,fetch,reply,None,d)==0
  actual=[ss[40],ss[43],list(ts[28:30]),e[1],status[1],status[3],status[4],status[5]];expected=[u.mem_read(source+0x15c,1)[0],struct.unpack('<i',u.mem_read(source+0x1a8,4))[0],list(struct.unpack('<2i',u.mem_read(target+8,8))),struct.unpack('<i',u.mem_read(target+0x258,4))[0],struct.unpack('<i',u.mem_read(target+0x1fc,4))[0],u.mem_read(target+0x20c,1)[0],struct.unpack('<i',u.mem_read(target+0x1d0,4))[0],u.mem_read(target+0x1c8,1)[0]];assert actual==expected,(case,actual,expected);hits+=d[0];accepted+=bool(d[1])
 assert hits>accepted>0
 result={'original_pair_to_shrek_cases':3000,'intersections':hits,'accepted_replies':accepted,'mismatches':0,'scope':'Original 184F8 -> generic525C direction -> Shrek E3A0, frame/body hit geometry, selected incoming branches and source success flag. Target surface flags +15D bits0..2 are clear, so original dynamic append is absent even with source dynamic flag. Other target hit-query overrides, unsupported incoming actions and full world scheduling are excluded.'};(ROOT/'docs/item_reply_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
