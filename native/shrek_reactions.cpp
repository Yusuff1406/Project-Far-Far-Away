// Selected constructor effects D24C/D294 and local incoming handler E3A0.
// Virtual action entries, broadcasts and carry lifetime are separate modules.
#include <cstdint>
#include <algorithm>
using Fetch=int(*)(uint32_t,int32_t*,int,void*);
extern "C" int s2_shrek_locomotion_enter(int32_t*,int32_t*,int32_t*,int32_t*,int,int,int32_t,int32_t,uint32_t,const int32_t*,Fetch,void*);
// E3A0/E4E6 event28. The world supplies the original DF9C ceiling-query answer.
extern "C" int s2_shrek_bounce_receive(int32_t* source,int32_t* extra,int32_t* status,int32_t* book,const int32_t* event,int32_t worldTick,int32_t animationTick,uint32_t table,int ceilingClear,Fetch fetch,void* ctx){
 if(!source||!extra||!status||!book||!event||!fetch)return -1;if(event[1]!=28)return -4;
 if(extra[0]==6||source[11]<=0||source[62]||!ceilingClear)return 0;
 int e=s2_shrek_locomotion_enter(source,extra,status,book,0x160,extra[2],worldTick,animationTick,table,nullptr,fetch,ctx);if(e)return e;
 source[11]=int32_t(0u-uint32_t(event[0]));return 1;
}
// Actual type3 incoming override10C08: downward strike receives boosted bounce.
extern "C" int s2_shrek_scene_bounce_receive(int32_t* source,int32_t* extra,int32_t* status,int32_t* book,const int32_t* event,int32_t wt,int32_t at,uint32_t table,int clear,Fetch fetch,void* ctx){
 if(!source||!extra||!status||!book||!event||!fetch)return -1;
 if(extra[0]==20&&event[1]==28&&clear){int e=s2_shrek_locomotion_enter(source,extra,status,book,0x160,extra[2],wt,at,table,nullptr,fetch,ctx);if(e)return e;double velocity=double(int32_t(0u-uint32_t(event[0])))*1.2;source[11]=int32_t(std::max(velocity,-2048.0));return 1;}
 return s2_shrek_bounce_receive(source,extra,status,book,event,wt,at,table,clear,fetch,ctx);
}
extern "C" int s2_shrek_event_defaults(int32_t* out){
 if(!out)return -1;const int32_t events[18]={1,0,0, 0,8,0, 1,7,0, 0,11,0, 0,12,0, 0,4,0};std::copy_n(events,18,out);return 0;
}
// Source is the generic 80-word pose, extra is the Stage-15 eight-word ABI.
// Status[8]: max/current life counter, bytes +1E4/+20C, immunity deadline
// (+1D0), byte +1C8, carry SFX deadline (+208), one reserved word. lifeCount is descriptor byte +15.
extern "C" int s2_shrek_reactions_init(int32_t* source,int32_t* extra,int32_t* status,int lifeCount,int32_t tick){
 if(!source||!extra||!status||lifeCount<0||lifeCount>255)return -1;
 int32_t events[18];s2_shrek_event_defaults(events);std::copy_n(events,3,source+41);
 std::fill(extra,extra+8,0);std::copy_n(events+3,3,extra+4);
 std::fill(status,status+8,0);status[0]=lifeCount-1;status[1]=lifeCount-1;status[4]=tick;return 0;
}
// Return 1 accepted, 0 refused/ignored, -4 for an action needing an unported
// backend. Event class/payload are ignored by the selected original branches.
extern "C" int s2_shrek_receive(int32_t* extra,int32_t* status,const int32_t* event,int32_t tick){
 if(!extra||!status||!event)return -1;const int32_t id=event[1],state=extra[0];
 // Event 40 bypasses the original state-6 gate and calls virtual slot 1C0.
 if(id==40)return -4;if(state==6)return 0;
 if(id<15||id>41)return 0;
 if(id>=15&&id<=21){
  if(state!=8||!extra[3])return 0;const int32_t modes[7]={6,2,3,1,7,4,5};extra[1]=modes[id-15];
  if(id==20)status[4]=INT32_MAX;if(id==21)status[5]=1;return 1;
 }
 if(id==22||id==23){
  if(state==13)return 0;if(id==22)status[1]=status[0];else if(status[1]<status[0])status[1]=int32_t(uint32_t(status[1])+1u);return 1;
 }
 if(id==25){status[3]=1;return uint32_t(state)<=1u||state==9||state==10||state==11;}
 if(id==27||id==29||(id>=33&&id<=36))return 0;
 if((id==24&&state==13)||(id==26&&state==12)||(id==31&&extra[1]==5))return 0;
 if((id==37||id==38||id==39||id==41)&&status[4]>tick)return 0;
 return -4;
}

// E3A0 event32: pickup SFX, wrapped manager counter and original update packet.
using PickupSink=int(*)(int,uint32_t,int32_t,void*);
extern "C" int s2_shrek_coin_receive(const int32_t* extra,const int32_t* event,int32_t* count,PickupSink sink,void* ctx){
 if(!extra||!event||!count||!sink)return -1;if(event[1]!=32)return -4;if(extra[0]==6)return 0;
 int e=sink(11,0x08053e7c,256,ctx);if(e)return e;*count=int32_t(uint32_t(*count)+1u);
 e=sink(1,0x08024cdc,0,ctx);return e?e:1;
}

// E3A0/E74C: B edge from FB2C input+8, excluding hurt6 and hanging12.
extern "C" int s2_shrek_talk_receive(int32_t* s,int32_t* extra,int32_t* status,int32_t* book,int pressed,int32_t tick,Fetch fetch,void* ctx){
 if(!s||!extra||!status||!book||!fetch)return -1;if(extra[0]==6||extra[0]==12||!(pressed&2))return 0;
 const int32_t event[3]={1,7,0};int e=s2_shrek_locomotion_enter(s,extra,status,book,0x158,extra[2],tick,tick,0x0804b73c,event,fetch,ctx);return e?e:1;
}
