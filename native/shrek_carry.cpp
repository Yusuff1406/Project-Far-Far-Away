// Original D484 post-update carry positioning, DC5C detach and EA98 throw.
// Actor ownership and target virtual-message delivery remain caller supplied.
#include <cstdint>
#include <cstddef>
using Fetch=int(*)(uint32_t,int32_t*,int,void*);
using Sink=int(*)(int,uint32_t,int32_t,void*);
using Dispatch=int(*)(uint32_t,const int32_t*,void*);
extern "C" void s2_animation_restart(int,int,int,int32_t,int32_t*);
static int32_t add(int32_t a,int32_t b){return int32_t(uint32_t(a)+uint32_t(b));}
static int32_t sub(int32_t a,int32_t b){return int32_t(uint32_t(a)-uint32_t(b));}
// Base 5168/9CC0: pending-removal bit plus scene instance bitmap. This marks an
// actor, not its destructor. Nonpositive scene IDs do not update the bitmap.
extern "C" int s2_actor_mark_removed(int32_t* actor,int32_t instanceId,uint32_t* removed,size_t words){
 if(!actor)return -1;if(instanceId>0&&(!removed||uint32_t(instanceId)/32u>=words))return -1;
 actor[40]|=1;if(instanceId>0)removed[uint32_t(instanceId)/32u]|=1u<<(uint32_t(instanceId)%32u);return 0;
}
// Dispatch returns backend status (0 success), NOT the target's reaction result.
// The original clears ownership even when the target refuses the delivered event.
extern "C" int s2_shrek_carry_release(int32_t* extra,int32_t* status,int32_t tick,const int32_t* detachEvent,Dispatch dispatch,void* ctx){
 if(!extra||!status)return -1;if(!extra[3])return 0;if(!detachEvent||!dispatch)return -1;
 if(extra[1]==4)status[4]=add(tick,1);else if(extra[1]==5)status[5]=0;
 int c=dispatch(uint32_t(extra[3]),detachEvent,ctx);if(c)return c;extra[3]=0;extra[1]=0;return 0;
}
extern "C" int s2_shrek_carry_throw(int32_t* extra,Dispatch dispatch,void* ctx){
 if(!extra)return -1;if(!extra[3]||!dispatch)return -1;const int32_t event[3]={0,29,0};
 int c=dispatch(uint32_t(extra[3]),event,ctx);if(c)return c;extra[3]=0;extra[1]=0;return 0;
}
static int animation(int32_t* target,uint32_t address,int32_t tick,Fetch fetch,void* ctx){
 int32_t raw[6];if(!fetch||!fetch(address,raw,6,ctx))return -2;
 const uint32_t b=uint32_t(raw[3]),d=uint32_t(raw[4]),a=uint32_t(raw[5]);target[47]=int32_t(address);
 target[72]=int16_t(b);target[73]=int16_t(b>>16);target[74]=d&255;target[75]=(d>>8)&255;target[76]=a&255;target[77]=(a>>8)&255;target[78]=(a>>16)&255;
 s2_animation_restart(target[76],target[77],0,tick,target+20);return 0;
}
// Position/facing plus mode-1 weapon animation and mode-5 flashing/SFX. This is
// the D484 tail AFTER the player's base update. Status word 6 is actor +208.
// Animation and world ticks are deliberately separate original globals.
extern "C" int s2_shrek_carry_follow(const int32_t* source,int32_t* extra,int32_t* status,int32_t* target,int32_t worldTick,int32_t animationTick,Fetch fetch,Sink sink,Dispatch dispatch,void* ctx){
 if(!source||!extra||!status)return -1;if(!extra[3])return 0;if(!target)return -1;
 int32_t goalY=source[1];if(extra[1]!=4&&extra[1]!=5&&extra[1]!=7)goalY=sub(sub(goalY,(source[31]&255)*128),(target[31]&255)*128);
 target[0]=add(target[0],sub(source[0],target[0])/4);target[1]=add(target[1],sub(goalY,target[1])/4);target[18]=source[18]&255;
 if(extra[1]==1){
  const uint32_t idle=0x08342dcc,attack=0x08342db4;int c=0;
  if(extra[2]&2){if(uint32_t(target[47])==idle)c=animation(target,attack,animationTick,fetch,ctx);else if(target[20]&255)c=s2_shrek_carry_throw(extra,dispatch,ctx);}
  else if(uint32_t(target[47])==attack)c=animation(target,idle,animationTick,fetch,ctx);
  if(c)return c;
 }
 if(extra[1]==5){
  if(status[6]<worldTick){int32_t period;if(!fetch||!fetch(0x0804b710,&period,1,ctx))return -2;if(!sink)return -4;status[6]=add(worldTick,period);int c=sink(11,0x0805402c,256,ctx);if(c)return c;}
  status[5]=(status[5]^1)&255;
 }return 0;
}
