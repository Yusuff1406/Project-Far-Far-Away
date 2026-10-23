// Original grab entry F224 (Shrek virtual slot 190), selected hash-locked table.
#include <cstdint>
#include <algorithm>
using Fetch=int(*)(uint32_t,int32_t*,int,void*);
using Dispatch=int(*)(uint32_t,const int32_t*,void*);
extern "C" int s2_shrek_carry_release(int32_t*,int32_t*,int32_t,const int32_t*,Dispatch,void*);
extern "C" void s2_animation_restart(int,int,int,int32_t,int32_t*);
extern "C" int s2_apply_axis_triple(int32_t*,const int32_t*,int,int);
// Source80 is the shared pose ABI, extra/status are the existing eight words.
// Grab/detach events are the actual mutable +240/+234 triples. Out2 contains
// motion-table record address (+260) and current sound descriptor (+25C).
extern "C" int s2_shrek_grab_enter(int32_t* source,int32_t* extra,int32_t* status,int32_t worldTick,int32_t animationTick,uint32_t table,const int32_t* grabEvent,const int32_t* detachEvent,Fetch fetch,Dispatch dispatch,void* ctx,int32_t* out){
 if(!source||!extra||!status||!grabEvent||!fetch||!out)return -1;
 int e=s2_shrek_carry_release(extra,status,worldTick,detachEvent,dispatch,ctx);if(e)return e;
 std::copy_n(grabEvent,3,source+41);int32_t record[10];uint32_t address=table;bool found=false;
 for(int i=0;i<24;i++,address+=40){if(!fetch(address,record,10,ctx))return -2;if(record[0]==999)break;if(record[0]==10){found=true;break;}}
 if(!found)return -2;int32_t header[6];if(!fetch(uint32_t(record[1]),header,6,ctx))return -2;
 const uint32_t b=uint32_t(header[3]),d=uint32_t(header[4]),a=uint32_t(header[5]);source[47]=record[1];source[72]=int16_t(b);source[73]=int16_t(b>>16);source[74]=d&255;source[75]=(d>>8)&255;source[76]=a&255;source[77]=(a>>8)&255;source[78]=(a>>16)&255;
 s2_animation_restart(source[76],source[77],0,animationTick,source+20);
 s2_apply_axis_triple(source+2,record+2,0,0);extra[0]=8;out[0]=int32_t(address);out[1]=record[9];return 0;
}
