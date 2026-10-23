#include "carry_policy.h"
// Selected original Shrek entries plus state8 F1E4 / D5E0 pending-byte reset.
#include <cstdint>
#include <algorithm>
using Fetch=int(*)(uint32_t,int32_t*,int,void*);
extern "C" void s2_animation_step(int,int,int,int32_t,int32_t*);
extern "C" void s2_animation_restart(int,int,int,int32_t,int32_t*);
extern "C" int s2_apply_axis_triple(int32_t*,const int32_t*,int,int);
// Book8: +260 motion cache, +25C sound, +1DC idle tick, +204 saved Y,
// reserved[4]. Pose80/extra8/status8 keep the existing layouts.
static int record(uint32_t table,int id,Fetch fetch,void* ctx,int32_t* row,uint32_t& address){
 address=table;for(int i=0;i<40;i++,address+=40){if(!fetch(address,row,10,ctx))return -2;if(row[0]==id)return 0;if(row[0]==999)break;}return -2;
}
static int restart(int32_t* s,const int32_t* row,uint32_t address,int32_t tick,int32_t* book,Fetch fetch,void* ctx){
 int32_t h[6];if(!fetch(uint32_t(row[1]),h,6,ctx))return -2;uint32_t b=uint32_t(h[3]),d=uint32_t(h[4]),a=uint32_t(h[5]);
 s[47]=row[1];s[72]=int16_t(b);s[73]=int16_t(b>>16);s[74]=d&255;s[75]=(d>>8)&255;s[76]=a&255;s[77]=(a>>8)&255;s[78]=(a>>16)&255;s2_animation_restart(s[76],s[77],0,tick,s+20);book[0]=int32_t(address);book[1]=row[9];return 0;
}
extern "C" int s2_shrek_locomotion_enter(int32_t* s,int32_t* extra,int32_t* status,int32_t* book,int action,int held,int32_t worldTick,int32_t animationTick,uint32_t table,const int32_t* locomotionEvent,Fetch fetch,void* ctx){
 if(!s||!extra||!status||!book||!fetch)return -1;int id;
 switch(action){case 0x158:id=status[3]?14:1;break;case 0x1a0:id=12;break;case 0x1a8:id=status[3]?14:13;break;case 0x198:id=11;break;case 0x10022:id=25;break;case 0x150:id=2;break;case 0x160:id=3;break;case 0x168:id=4;break;case 0x170:case 0x1d0:id=5;break;case 0x188:id=(held&64)?9:8;break;case 0x10008:id=8;break;case 0x10009:id=9;break;default:return -4;}
 if(action==0x158||action==0x150){if(!locomotionEvent)return -1;std::copy_n(locomotionEvent,3,s+41);}
 int32_t row[10];uint32_t address;int e=record(table,id,fetch,ctx,row,address);if(e)return e;e=restart(s,row,address,animationTick,book,fetch,ctx);if(e)return e;
 if(action==0x158||action==0x150){
  // Idle selects special animation14 but still applies motion1 triples.
  int32_t physics[10];uint32_t physicalAddress;e=record(table,action==0x158?1:2,fetch,ctx,physics,physicalAddress);if(e)return e;
  s2_apply_axis_triple(s+2,physics+2,0,(held>>5)&1);s2_apply_axis_triple(s+2,physics+5,1,0);book[0]=int32_t(physicalAddress);
  if(action==0x158){book[2]=worldTick;extra[0]=0;}else{s[18]=(held>>5)&1;extra[0]=1;}
 }else if(action==0x1a8){extra[0]=11;if(status[3]){int32_t idle[10];uint32_t idleAddress;e=record(table,1,fetch,ctx,idle,idleAddress);if(e)return e;s2_apply_axis_triple(s+2,idle+2,0,0);book[0]=int32_t(idleAddress);}}else if(action==0x198){extra[0]=9;}else if(action==0x10022){extra[0]=22;}else if(action==0x1a0){extra[0]=10;}else if(action==0x188){
  // D170: outgoing ID13, idle X with no reflection, attack8/9, state7.
  // Y, owner and event class/payload stay unchanged.
  int32_t idle[10];uint32_t idleAddress;e=record(table,1,fetch,ctx,idle,idleAddress);if(e)return e;
  s[42]=13;s2_apply_axis_triple(s+2,idle+2,0,0);extra[0]=7;
 }else if(action==0x10008||action==0x10009)extra[0]=16; // D1B8 animation/state only
 else if(action==0x160){int32_t y[3]={row[5],row[6],row[7]};if(extra[1]==4)y[0]/=2;s2_apply_axis_triple(s+2,y,1,0);extra[0]=2;}
 else if(action==0x168)extra[0]=3;
 else{book[3]=s[1];extra[0]=4;if(action==0x1d0)s2_apply_axis_triple(s+2,row+5,1,0);}
 return 0;
}
extern "C" int s2_shrek_grab_decide(int finished,uint32_t carriedId,int mode){return (finished&255)&&(!carriedId||mode!=0)?0x158:0;}
extern "C" int s2_shrek_attack_behavior(int32_t* s,int32_t* extra,int32_t* status,int32_t* book,int held,int32_t worldTick,int32_t animationTick,uint32_t table,const int32_t* locomotionEvent,Fetch fetch,void* ctx){
 if(!s||!extra||!status||!book)return -1;if(extra[0]!=7)return -4;
 if(s[20]&255){s[42]=0;int e=s2_shrek_locomotion_enter(s,extra,status,book,0x158,held,worldTick,animationTick,table,locomotionEvent,fetch,ctx);if(e)return e;}
 status[3]=0;return 0;
}
using Sink=int(*)(int,uint32_t,int32_t,void*);
// F030: animation ID6 and its optional heavy-landing sound. The original
// table includes ID0; packed native tables begin at ID1, so use the ID6 row,
// then idle motion ID1. Signed wrapped fall distance, strict > threshold.
extern "C" int s2_shrek_landing_enter(int32_t* s,int32_t* extra,int32_t* book,int held,int32_t animationTick,uint32_t table,uint32_t thresholdAddress,Fetch fetch,Sink sink,void* ctx){
 if(!s||!extra||!book||!fetch)return -1;
 int32_t row[10],threshold;uint32_t address;int e=record(table,6,fetch,ctx,row,address);if(e)return e;
 e=restart(s,row,address,animationTick,book,fetch,ctx);if(e)return e;
 if(!fetch(thresholdAddress,&threshold,1,ctx))return -2;
 int32_t distance=int32_t(uint32_t(s[1])-uint32_t(book[3]));
 if(distance>int32_t(uint32_t(threshold)<<8)){
  if(row[9]){if(!sink)return -4;e=sink(11,uint32_t(row[9]),256,ctx);if(e)return e;}
 }
 e=record(table,1,fetch,ctx,row,address);if(e)return e;
 s2_apply_axis_triple(s+2,row+2,0,(held>>5)&1);s2_apply_axis_triple(s+2,row+5,1,0);
 book[0]=int32_t(address);extra[0]=5;return 0;
}
// F600 clears the outgoing base-contact event ID; it is not carry release.
extern "C" int s2_shrek_clear_contact_event(int32_t* s){if(!s)return -1;s[42]=0;return 0;}
extern "C" int s2_shrek_grab_behavior(int32_t* s,int32_t* extra,int32_t* status,int32_t* book,int held,int32_t worldTick,int32_t animationTick,uint32_t table,const int32_t* locomotionEvent,Fetch fetch,void* ctx){
 if(!s||!extra||!status||!book)return -1;if(extra[0]!=8)return -4;
 int action=s2_shrek_grab_decide(s[20],uint32_t(extra[3]),extra[1]);int e=0;
 if(action)e=s2_shrek_locomotion_enter(s,extra,status,book,action,held,worldTick,animationTick,table,locomotionEvent,fetch,ctx);
 if(e)return e;status[3]=0;return 0; // D5E0 clears +20C after selected behavior
}

extern "C" int s2_actor_current_frame(const int32_t*,Fetch,void*,int32_t*);
// D1E8 state16 -> CF8C: recovery uses actor delta-Y (+18C).
extern "C" int s2_shrek_air_attack_behavior(int32_t* s,int32_t* extra,int32_t* status,int32_t* book,int held,int32_t worldTick,int32_t animationTick,uint32_t table,const int32_t* locomotionEvent,Fetch fetch,Sink sink,void* ctx){
 if(!s||!extra||!status||!book||!fetch)return -1;if(extra[0]!=16)return -4;
 if(uint32_t(s[47])!=0x0834f304&&uint32_t(s[47])!=0x0834f31c)return -4;
 int32_t pulse=int32_t(uint32_t(s[23])-uint32_t(animationTick));
 if(pulse<=1){int32_t frame[11],metadata;int e=s2_actor_current_frame(s,fetch,ctx,frame);if(e)return e;if(!fetch(uint32_t(frame[5]),&metadata,1,ctx))return -2;if((uint32_t(metadata)>>16)&255)return -4;}
 if(!(s[20]&255))return 0;
 int32_t thresholds[2];if(!fetch(0x0804b6ec,thresholds,2,ctx))return -2;int e;
 if(s[61]<thresholds[0]){int32_t row[10];uint32_t address;e=record(table,3,fetch,ctx,row,address);if(e)return e;e=restart(s,row,address,animationTick,book,fetch,ctx);if(e)return e;extra[0]=2;}
 if(s[61]>thresholds[0]){e=s2_shrek_locomotion_enter(s,extra,status,book,0x168,held,worldTick,animationTick,table,locomotionEvent,fetch,ctx);if(e)return e;}
 if(s[61]>thresholds[1]){e=s2_shrek_locomotion_enter(s,extra,status,book,0x170,held,worldTick,animationTick,table,locomotionEvent,fetch,ctx);if(e)return e;}
 if(s[14]||s[64]){e=s2_shrek_landing_enter(s,extra,book,held,animationTick,table,0x0804b708,fetch,sink,ctx);if(e)return e;}
 // CF8C bypasses D5E0: pending +20C stays unchanged.
 return 0;
}

// Actual scene00 type3 subclass (111CC/vtable02001E6C), not base D24C.
extern "C" int s2_shrek_stomp_enter(int32_t* s,int32_t* extra,int32_t* book,int32_t tick,uint32_t table,Fetch fetch,void* ctx){
 if(!s||!extra||!book||!fetch)return -1;if(!shrekAirAttackAllowed(extra[3],extra[1]))return -4;
 int32_t row[10];uint32_t address;int e=record(table,23,fetch,ctx,row,address);if(e)return e;
 e=restart(s,row,address,tick,book,fetch,ctx);if(e)return e;
 const int32_t freeze[3]={0,1,0};s2_apply_axis_triple(s+2,freeze,0,0);s2_apply_axis_triple(s+2,freeze,1,0);extra[0]=19;s[42]=0;return 0;
}
extern "C" int s2_shrek_stomp_behavior(int32_t* s,int32_t* extra,int32_t* status,int32_t* book,int held,int32_t wt,int32_t at,uint32_t table,const int32_t* events,Fetch fetch,Sink sink,void* ctx){
 if(!s||!extra||!status||!book||!fetch)return -1;int state=extra[0];int32_t row[10];uint32_t address;int e;
 if(state==19){if(!(s[20]&255))return 0;e=record(table,23,fetch,ctx,row,address);if(e)return e;s2_apply_axis_triple(s+2,row+5,1,0);book[0]=int32_t(address);extra[0]=20;s[41]=10;s[42]=9;return 0;}
 if(state==20){if(!(s[14]||s[64]))return 0;if(!sink)return -4;e=sink(20,1024,128,ctx);if(e)return e;e=record(table,24,fetch,ctx,row,address);if(e)return e;e=restart(s,row,address,at,book,fetch,ctx);if(e)return e;s2_apply_axis_triple(s+2,row+5,1,0);extra[0]=21;book[5]=int32_t(uint32_t(wt)+60u);return 0;}
 if(state==21){if(s[14]||s[64]){s[41]=3;return s2_shrek_locomotion_enter(s,extra,status,book,0x158,held,wt,at,table,events,fetch,ctx);}return 0;}
 return -4;
}
// F7D0/FA4C: metadata byte4 sound cue before subclass behavior.
extern "C" int s2_shrek_stomp_audio(const int32_t* s,const int32_t* book,int32_t tick,Fetch fetch,Sink sink,void* ctx){
 if(!s||!book||!fetch||!sink)return -1;if(int32_t(uint32_t(s[23])-uint32_t(tick))>1)return 0;
 int32_t frame[11],metadata[2];int e=s2_actor_current_frame(s,fetch,ctx,frame);if(e)return e;if(!fetch(uint32_t(frame[5]),metadata,2,ctx))return -2;
 return (uint32_t(metadata[1])&255)&&book[1]?sink(11,uint32_t(book[1]),256,ctx):0;
}

extern "C" int s2_shrek_lift_enter(int32_t* s,int32_t* extra,int32_t* book,int id,int32_t tick,uint32_t table,Fetch fetch,void* ctx){
 if(!s||!extra||!book||!fetch||id<=0)return -1;if(book[6]||extra[3])return -4;
 int32_t row[10];uint32_t address;int e=record(table,22,fetch,ctx,row,address);if(e)return e;s2_apply_axis_triple(s+2,row+2,0,0);
 e=record(table,20,fetch,ctx,row,address);if(e)return e;e=restart(s,row,address,tick,book,fetch,ctx);if(e)return e;book[6]=id;extra[0]=16;return 0;
}
static int lift_release(int32_t* book,Sink sink,void* ctx){if(!book[6])return 0;if(!sink)return -1;int accepted=sink(21,uint32_t(book[6]),0,ctx);if(accepted<0)return accepted;if(accepted)book[6]=0;return accepted!=0;}
extern "C" int s2_shrek_lift_behavior(int32_t* s,int32_t* extra,int32_t* status,int32_t* book,int held,int pressed,int leftBlocked,int rightBlocked,int32_t wt,int32_t at,uint32_t table,const int32_t* events,Fetch fetch,Sink sink,void* ctx){
 if(!s||!extra||!status||!book||!fetch||!sink)return -1;int state=extra[0],e;int32_t row[10];uint32_t address;
 auto enter=[&](int stateId,int anim,int physics,int flip)->int{int v=record(table,anim,fetch,ctx,row,address);if(v)return v;v=restart(s,row,address,at,book,fetch,ctx);if(v)return v;v=record(table,physics,fetch,ctx,row,address);if(v)return v;s2_apply_axis_triple(s+2,row+2,0,flip);s2_apply_axis_triple(s+2,row+5,1,0);book[0]=int32_t(address);extra[0]=stateId;if(stateId==17)s[42]=7;return 0;};
 auto drop=[&](bool falling)->int{int v=lift_release(book,sink,ctx);if(v<0)return v;if(v)return s2_shrek_locomotion_enter(s,extra,status,book,falling?0x1d0:0x158,held,wt,at,table,events,fetch,ctx);return 0;};
 if(state==16){if(s[20]&255)return enter(18,22,1,0);if(pressed&2)return drop(false);return 0;}
 if(state==18){if((held&32)&&!leftBlocked){s[18]=1;e=enter(17,21,2,(held>>5)&1);if(e)return e;}if((held&16)&&!rightBlocked){s[18]=0;e=enter(17,21,2,(held>>5)&1);if(e)return e;}if(pressed&2)return drop(false);return 0;}
 if(state==17){if(s[18]?(!(held&32)||leftBlocked):(!(held&16)||rightBlocked)){e=enter(18,22,1,0);if(e)return e;}if(!(s[14]||s[64]))return drop(true);if(pressed&2)return drop(false);return 0;}
 return -4;
}
extern "C" int s2_actor_box_q8(const int32_t*,const int32_t*,int32_t*);
// Original10640 attachment: source-frame marker or direct fallback, no smoothing.
extern "C" int s2_shrek_lift_position(const int32_t* source,int32_t* target,int32_t* book,int32_t* extra,Fetch fetch,void* ctx){
 if(!source||!target||!book||!extra||!fetch)return -1;int32_t frame[11],meta[2],xy[2]={source[0],int32_t(uint32_t(source[1])-uint32_t((target[31]&255)*256))};
 int e=s2_actor_current_frame(source,fetch,ctx,frame);if(e)return e;if(!fetch(uint32_t(frame[5]),meta,2,ctx))return -2;
 if((uint32_t(meta[0])>>16)&255){int32_t packed[2],box[4],rect[4];if(!fetch(uint32_t(frame[8]),packed,2,ctx))return -2;box[0]=int16_t(uint32_t(packed[0]));box[1]=int16_t(uint32_t(packed[0])>>16);box[2]=uint32_t(packed[1])&255;box[3]=(uint32_t(packed[1])>>8)&255;e=s2_actor_box_q8(source,box,rect);if(e)return e;xy[1]=int32_t(uint32_t(rect[1])-uint32_t((target[31]&255)*128));}
 target[0]=xy[0];target[1]=xy[1];book[7]=xy[0];extra[7]=xy[1];return 0;
}

// Type3 incoming37..39 -> E3A0/DD74. The owner consumes shield/invisibility
// before this call; ordinary carried objects remain attached through damage.
// Status[7] is original+1F0 hurt recovery deadline; Status[4] is+1D0 immunity.
extern "C" int s2_shrek_hurt_receive(int32_t* s,int32_t* extra,int32_t* status,int32_t* book,const int32_t* event,int32_t wt,int32_t at,uint32_t table,Fetch fetch,void* ctx){
 if(!s||!extra||!status||!book||!event||!fetch)return -1;
 if(event[1]<37||event[1]>39)return -4;
 if(extra[0]==6||status[4]>wt)return 0;
 int32_t delay; if(!fetch(0x0804b700,&delay,1,ctx))return -2;
 status[7]=int32_t(uint32_t(wt)+uint32_t(delay));
 int payload=event[2],e;int32_t row[10];uint32_t address;
 if(payload>=0&&payload<=2){
  e=record(table,7,fetch,ctx,row,address);if(e)return e;
  s2_apply_axis_triple(s+2,row+5,1,0);
  s2_apply_axis_triple(s+2,row+2,0,payload==2||(payload==0&&s[60]>0));
  e=restart(s,row,address,at,book,fetch,ctx);if(e)return e;
 }
 status[1]=int32_t(uint32_t(status[1])-uint32_t(event[0]));
 if(!fetch(0x0804b6e4,&delay,1,ctx))return -2;
 status[4]=int32_t(uint32_t(wt)+uint32_t(delay));
 // Original EE94(16) overwrites the motion cache even though animation7 remains.
 e=record(table,16,fetch,ctx,row,address);if(e)return e;book[0]=int32_t(address);
 // The original auxiliary flashing sprite is not rendered by this component.
 extra[0]=6;return 1;
}
extern "C" int s2_shrek_hurt_behavior(int32_t* s,int32_t* extra,int32_t* status,int32_t* book,int held,int32_t wt,int32_t at,uint32_t table,const int32_t* events,Fetch fetch,void* ctx){
 if(!s||!extra||!status||!book||!events||!fetch)return -1;if(extra[0]!=6)return -4;
 if(status[7]&&status[7]<wt&&(s[14]||s[64])){
  if(status[1]>0)return s2_shrek_locomotion_enter(s,extra,status,book,0x158,held,wt,at,table,events,fetch,ctx);
  int32_t row[10];uint32_t address;int e=record(table,1,fetch,ctx,row,address);if(e)return e;
  s2_apply_axis_triple(s+2,row+2,0,0);book[0]=int32_t(address);
  e=record(table,15,fetch,ctx,row,address);if(e)return e;e=restart(s,row,address,at,book,fetch,ctx);if(e)return e;extra[0]=13;return 0;
 }
 if(s[15]||s[65]||s[16]||s[66]){int32_t row[10];uint32_t address;int e=record(table,1,fetch,ctx,row,address);if(e)return e;s2_apply_axis_triple(s+2,row+2,0,0);book[0]=int32_t(address);}
 return 0;
}

// F534 primary death entry, used by the native owner after source D438 defeat.
extern "C" int s2_shrek_fall_death(int32_t* s,int32_t* extra,int32_t* book,int32_t tick,Fetch fetch,void* ctx){
 if(!s||!extra||!book||!fetch)return -1;int32_t row[10];uint32_t address;int e=record(0x0804b73c,15,fetch,ctx,row,address);if(e)return e;e=restart(s,row,address,tick,book,fetch,ctx);if(e)return e;s[42]=0;extra[0]=13;book[6]=0;extra[3]=0;return 0;
}

// E168: motion17 presentation followed by motion1 physics; logical water state14.
extern "C" int s2_shrek_water_enter(int32_t* s,int32_t* extra,int32_t* book,int32_t tick,Fetch fetch,void* ctx){
 if(!s||!extra||!book||!fetch)return -1;int32_t row[10];uint32_t address;
 int e=record(0x0804b73c,17,fetch,ctx,row,address);if(e)return e;e=restart(s,row,address,tick,book,fetch,ctx);if(e)return e;
 e=record(0x0804b73c,1,fetch,ctx,row,address);if(e)return e;
 s2_apply_axis_triple(s+2,row+2,0,0);s2_apply_axis_triple(s+2,row+5,1,0);book[0]=int32_t(address);extra[0]=14;return 0;
}

// F554 / F45C: original victory state12, motion14; finish on entry to last frame.
extern "C" int s2_shrek_finish_enter(int32_t* s,int32_t* extra,int32_t* book,int32_t tick,Fetch fetch,void* ctx){
 if(!s||!extra||!book||!fetch)return -1;int32_t row[10];uint32_t address;int e=record(0x0804b73c,1,fetch,ctx,row,address);if(e)return e;
 s2_apply_axis_triple(s+2,row+2,0,0);s2_apply_axis_triple(s+2,row+5,1,0);s[42]=0;
 e=record(0x0804b73c,14,fetch,ctx,row,address);if(e)return e;e=restart(s,row,address,tick,book,fetch,ctx);if(e)return e;extra[0]=12;return 0;
}
extern "C" int s2_shrek_finish_step(int32_t* s,const int32_t* book,int32_t tick,Fetch fetch,Sink sink,void* ctx){
 if(!s||!book)return -1;s[24]=tick;s2_animation_step(s[76],s[77],s[78],tick,s+20);
 int e=s2_shrek_stomp_audio(s,book,tick,fetch,sink,ctx);if(e)return e;
 return s[22]==s[77]-1&&int32_t(uint32_t(s[23])-uint32_t(tick))<=1;
}

// Type3 override F25C, not the shared D170 weak attack. Constructor111CC
// supplies [3,1,0] at+210. +1E0 alternates animations9/8; pose19 stores that
// Shrek-only counter (generic actors leave this compatibility word unused).
extern "C" int s2_shrek_scene_attack_enter(int32_t* s,int32_t* extra,int32_t* book,int32_t tick,uint32_t table,Fetch fetch,void* ctx){
 if(!s||!extra||!book||!fetch)return -1;
 s[19]=int32_t(uint32_t(s[19])+1u);const int32_t punch[3]={3,1,0};std::copy_n(punch,3,s+41);
 int32_t idle[10],row[10];uint32_t address;int e=record(table,1,fetch,ctx,idle,address);if(e)return e;s2_apply_axis_triple(s+2,idle+2,0,0);
 int id=(s[19]&1)?9:8;e=record(table,id,fetch,ctx,row,address);if(e&&id==9)e=record(table,8,fetch,ctx,row,address);if(e)return e;
 e=restart(s,row,address,tick,book,fetch,ctx);if(e)return e;extra[0]=7;return 0;
}
// Original E258: motion18 presentation/sound, motion1 physics/cache.
extern "C" int s2_shrek_fire_enter(int32_t* s,int32_t* extra,int32_t* book,int32_t tick,Fetch fetch,void* ctx){int32_t row[10];uint32_t address;int e=record(0x0804b73c,18,fetch,ctx,row,address);if(e)return e;e=restart(s,row,address,tick,book,fetch,ctx);if(e)return e;e=record(0x0804b73c,1,fetch,ctx,row,address);if(e)return e;s2_apply_axis_triple(s+2,row+2,0,0);s2_apply_axis_triple(s+2,row+5,1,0);book[0]=int32_t(address);extra[0]=15;return 0;}
