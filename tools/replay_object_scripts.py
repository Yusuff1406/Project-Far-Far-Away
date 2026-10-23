#!/usr/bin/env python3
"""Native VM replay from exported resources; actor queries are fixtures."""
import ctypes,json,struct,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 package=(ROOT/'objects/generic_script_resources.s2rs').read_bytes();assert package[:4]==b'S2RS';version,base,size=struct.unpack_from('<3I',package,4);assert version==1 and len(package)==size+16;data=package[16:];lib=ctypes.CDLL(str(ROOT/'native/build/libshrek_scene.so'));ip=ctypes.POINTER(ctypes.c_int32);FC=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_uint32,ip,ctypes.c_int,ctypes.c_void_p);QC=ctypes.CFUNCTYPE(None,ctypes.c_int,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ip,ctypes.c_void_p);EC=ctypes.CFUNCTYPE(None,ctypes.c_int,ip,ctypes.c_void_p);RC=ctypes.CFUNCTYPE(ctypes.c_int32,ctypes.c_void_p);start=lib.s2_vm_start;start.argtypes=[ctypes.c_uint32,ip];start.restype=None;step=lib.s2_vm_step;step.argtypes=[ip,ctypes.c_int32,FC,QC,EC,RC,ctypes.c_void_p,ctypes.c_int];step.restype=ctypes.c_int
 @FC
 def fetch(addr,out,n,context):
  offset=addr-base
  if offset<0 or offset+n*4>size:return 0
  for i,v in enumerate(struct.unpack_from('<'+'i'*n,data,offset)):out[i]=v
  return 1
 @QC
 def query(self,cls,id,payload,out,context):out[0]=0
 events=[];currentType=0;tick=0
 @EC
 def effect(kind,cmd,context):events.append([currentType,tick,kind,*cmd[:3]])
 @RC
 def random(context):return 37
 info=json.loads((ROOT/'docs/generic_script_resources.json').read_text());summary=[]
 for source in info['scripts']:
  if source['type'] not in [18,39,57,89]:continue
  currentType=source['type'];s=(ctypes.c_int32*64)();start(source['script'],s);before=len(events)
  for tick in range(1,181):
   code=step(s,tick,fetch,query,effect,random,None,4096);assert code>=0,(currentType,tick,code)
   if s[2]<0:break
  summary.append({'type':currentType,'ticks':tick,'events':len(events)-before,'remaining_depth':s[2]})
 with (ROOT/'docs/native_object_script_events.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['type','tick','effect_kind','event_class','event_id','payload']);w.writerows(events)
 result={'source_scripts':summary,'event_count':len(events),'scope':'Native interpreter reads exported ROM resource slice. Actor query fixture always returns 0, random fixture returns 37; external messages only logged. No object simulation or visual behavior claim.'};(ROOT/'docs/native_object_script_replay.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
