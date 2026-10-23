#include "attack_damage.h"
// Selected effects of generic handler 0x08013B8C and update 0x08018208.
// State layout and intentionally unsupported routes: docs/generic_runtime.md.
#include <cstdint>
#ifdef S2_TRACE
#include <cstdio>
#endif
#include <algorithm>
using Fetch=int(*)(uint32_t,int32_t*,int,void*);
using Query=void(*)(int,int32_t,int32_t,int32_t,int32_t*,void*);
using Effect=void(*)(int,const int32_t*,void*);
using Random=int32_t(*)(void*);
using Registry=void(*)(int,void*);
using Sink=int(*)(int,uint32_t,int32_t,void*);
extern "C" int s2_generic_world_message(int32_t*,int,int,int32_t,Fetch,Sink,void*);
extern "C" int s2_generic_audio_message(int32_t*,int,int,int32_t,Sink,void*);
extern "C" int s2_generic_event(int32_t*,int32_t*,int32_t*,const int32_t*,int32_t,Fetch,Registry,void*);
extern "C" void s2_generic_reaction_frame_end(int32_t*);
extern "C" int s2_generic_actor_init(const int32_t*,const int32_t*,int,int,int,int,int32_t,int32_t*);
extern "C" void s2_animation_restart(int,int,int,int32_t,int32_t*);
extern "C" void s2_animation_step(int,int,int,int32_t,int32_t*);
extern "C" int s2_apply_axis_triple(int32_t*,const int32_t*,int,int);
extern "C" int s2_actor_move_file(const char*,int32_t*,int32_t*,int32_t*,int32_t*,int,int,int,int32_t*,int32_t*);
extern "C" int s2_actor_move_dynamic_file(const char*,int32_t*,int32_t*,int32_t*,int32_t*,int,int,const int32_t*,int,int32_t*,int32_t*,int32_t*);
extern "C" void s2_preserve_bottom(int,const int32_t*,int,int32_t*);
extern "C" int s2_vm_step(int32_t*,int32_t,Fetch,Query,Effect,Random,void*,int);
static int32_t add(int32_t a,int32_t b){return int32_t(uint32_t(a)+uint32_t(b));}
static int metadata(uint32_t address,int32_t* s,Fetch fetch,void* ctx){
 int32_t a[6];if(!fetch||!fetch(address,a,6,ctx))return -2;
 s[72]=int16_t(uint32_t(a[3]));s[73]=int16_t(uint32_t(a[3])>>16);s[74]=uint32_t(a[4])&255;s[75]=(uint32_t(a[4])>>8)&255;
 s[76]=uint32_t(a[5])&255;s[77]=(uint32_t(a[5])>>8)&255;s[78]=(uint32_t(a[5])>>16)&255;return s[77]?0:-2;
}
extern "C" int s2_generic_runtime_init(const int32_t* anchor,int flips,uint32_t animation,int32_t tick,Fetch fetch,void* ctx,int32_t* s){
 if(!anchor||!s)return -1;std::fill(s,s+80,0);int e=metadata(animation,s,fetch,ctx);if(e)return e;
 e=s2_generic_actor_init(s+72,anchor,flips,0,s[76],s[77],tick,s);if(e)return e;
 s[26]=s[72];s[27]=s[73];s[40]=8;s[47]=int32_t(animation);s[52]=1;s[56]=1;s[58]=s[59]=0x08053c6c;return 0;
}
// Plain animated180B0 actor: no script VM, local reactions or motion component.
extern "C" int s2_plain_runtime_init(const int32_t* anchor,int flips,uint32_t animation,int32_t tick,Fetch fetch,void* ctx,int32_t* s){
 int e=s2_generic_runtime_init(anchor,flips,animation,tick,fetch,ctx,s);if(e)return e;s[52]=0;s[58]=s[59]=0;return 0;
}
extern "C" int s2_plain_runtime_step(int32_t* s,int32_t tick){
 if(!s||s[77]<1)return -1;s[24]=tick;s2_animation_step(s[76],s[77],s[78],tick,s+20);
 std::copy_n(s+72,2,s+26);std::copy_n(s+74,2,s+30);
 for(int i=0;i<2;i++){s[60+i]=int32_t(uint32_t(s[i])-uint32_t(s[36+i]));s[36+i]=s[i];}
 s[32]=int32_t(uint32_t(s[0])-uint32_t(s[30]*128));s[33]=int32_t(uint32_t(s[1])-uint32_t(s[31]*128));s[34]=s[30]*256;s[35]=s[31]*256;return 0;
}
static int change_animation(int32_t* s,uint32_t animation,int direction,int32_t tick,Fetch fetch,void* ctx){
 if(animation){int e=metadata(animation,s,fetch,ctx);if(e)return e;s[47]=int32_t(animation);}
 s2_animation_restart(s[76],s[77],direction,tick,s+20);return 0;
}
// Original 0x080168B4 gates direction changes on finished != 0.
static void change_direction(int32_t* s,int d,int32_t tick){
 if(!s[20]){s[21]=d;return;}int old=s[21];
 if((d==0&&old==1)||(d==1&&old==0)){s[23]=add(add(tick,tick),add(-uint32_t(s[23]),s[76]+1));s[20]=0;}
 else if((d==0||d==1)&&old==2)s[23]=add(s[23],int32_t(uint32_t(tick)-uint32_t(s[57])));
 else if(d==2&&old!=2)s[57]=tick;s[21]=d;
}
extern "C" int s2_generic_message(int32_t* s,int cls,int id,int32_t payload,int32_t tick,Fetch fetch,void* ctx){
 if(!s||!fetch)return -1;if(cls!=8)return -4;int32_t a[3];
 auto read=[&](){return fetch(uint32_t(payload),a,3,ctx)?0:-2;};
 switch(id){
 case 0:s[18]=payload!=0;break;case 1:s[38]=payload!=0;break;case 3:break;
 case 4:case 5:case 6:if(!payload)change_direction(s,id-4,tick);else{s[48]=s[47];s[49]=s[22];return change_animation(s,uint32_t(payload),id-4,tick,fetch,ctx);}break;
 case 7:s[55]=1;break;case 8:s[55]=0;break;
 case 10:s[25]=uint32_t(payload)&255;break; // 052D0: packed header +6 bits6..13, normalized mask only.
 case 19:return s2_apply_axis_triple(s+2,s+44,0,0);
 case 20:a[0]=s[44];a[1]=s[45];a[2]=int32_t(0u-uint32_t(s[46]));return s2_apply_axis_triple(s+2,a,0,0);
 case 21:case 22:if(read())return -2;return s2_apply_axis_triple(s+2,a,id-21,0);
 case 23:s[5]=payload;break;case 24:s[11]=payload;break;
 case 25:case 26:case 27:case 28:{int bit=id==25?1:id==26?16:id==27?2:4;s[39]=(s[39]&~bit)|(payload?bit:0);break;}
 case 29:case 30:{int bit=id==29?4:2;s[40]=(s[40]&~bit)|(payload?bit:0);break;}
 case 31:if(read())return -2;std::copy(a,a+3,s+41);break;
 case 32:s[54]=1;break;case 33:s[54]=0;break;
 case 40:if(payload)s[50]=payload;break;case 41:if(payload)s[51]=payload;break;
 case 42:if(read())return -2;std::copy(a,a+3,s+44);break;
 case 43:{int e=change_animation(s,uint32_t(s[50]),0,tick,fetch,ctx);if(e)return e;s[48]=s[47];s[49]=s[22];break;}
 case 44:s[48]=s[47];s[49]=s[22];return change_animation(s,uint32_t(s[51]),0,tick,fetch,ctx);
 case 45:{int e=change_animation(s,uint32_t(s[48]),0,tick,fetch,ctx);if(e)return e;s[22]=s[49];break;}
 case 49:if(s[79])return -4;break; // Original auxiliary spawn type zero does nothing.
 case 55:if(payload)return -4;break; // No auxiliary child: zero request is a no-op.
 case 51:s[52]=add(s[52],-1);if(s[52]<0)s[52]=0;break;
 case 52:s[52]=add(s[52],1);break;case 53:s[52]=payload;break;case 54:s[53]=payload!=0;break;
 default:return -4;
 }return 0;
}
extern "C" int s2_generic_query(const int32_t* s,int cls,int id,int32_t* out){
 if(!s||!out)return -1;if(cls!=8)return -4;
 switch(id){
 case 59:*out=s[20]&255;break;case 60:*out=(s[40]>>4)&1;break;
 case 61:*out=bool(s[15]||s[65]||s[16]||s[66]);break;case 62:*out=bool(s[15]||s[65]);break;case 63:*out=bool(s[16]||s[66]);break;
 case 64:*out=bool(s[14]||s[64]);break;case 65:*out=bool(s[17]||s[67]);break;
 case 66:*out=s[56]&255;break;case 67:*out=s[39]&1;break;case 68:*out=(s[39]>>1)&1;break;case 69:*out=(s[39]>>2)&1;break;
 case 70:*out=s[18]&255;break;case 73:*out=s[52];break;case 75:*out=s[5];break;case 76:*out=s[11];break;default:return -4;
 }return 0;
}
extern "C" int s2_actor_target_query(const int32_t*,const int32_t*,int,int32_t*);
extern "C" int s2_spawner_can_create(const int32_t*);
extern "C" int s2_actor_current_frame(const int32_t*,Fetch,void*,int32_t*);
// Original1460E query74: current frame attack-rectangle count, not a timer.
extern "C" int s2_generic_frame_query(const int32_t* s,Fetch fetch,void* ctx,int32_t* out){
 if(!s||!fetch||!out)return -1;int32_t frame[11],metadata;int e=s2_actor_current_frame(s,fetch,ctx,frame);if(e)return e;if(!fetch(uint32_t(frame[5]),&metadata,1,ctx))return -2;*out=((uint32_t(metadata)>>16)&255)!=0;return 0;
}
struct Context{const int32_t* spawner;bool* auxiliary;const int32_t* target;bool targetSupplied;int32_t* s;Fetch fetch;Random random;void* ctx;int error;int32_t* vm;int32_t* reactions;Registry registry;Sink sink;};
static int get(uint32_t p,int32_t* out,int n,void* v){auto* c=static_cast<Context*>(v);return c->fetch(p,out,n,c->ctx);}
static void query(int,int32_t cls,int32_t id,int32_t,int32_t* out,void* v){auto* c=static_cast<Context*>(v);if(cls==8&&id==74){int e=s2_generic_frame_query(c->s,c->fetch,c->ctx,out);if(e)c->error=e;return;}if(cls==8&&id==77&&c->spawner){*out=s2_spawner_can_create(c->spawner);return;}if(cls==8&&(id==71||id==72)&&c->targetSupplied){int e=s2_actor_target_query(c->s,c->target,id,out);if(e)c->error=e;return;}if(cls==8&&(id==57||id==58)&&c->reactions){*out=c->reactions[id-54];return;}int e=s2_generic_query(c->s,cls,id,out);if(e){
#ifdef S2_TRACE
std::fprintf(stderr,"query %d/%d error %d\n",cls,id,e);
#endif
c->error=e;}}
static void effect(int kind,const int32_t* cmd,void* v){
 auto* c=static_cast<Context*>(v);if(c->error)return;int e;
 if(!kind&&cmd[0]==8&&cmd[1]==18)e=c->sink?c->sink(29,0,0,c->ctx):-4;
 else if(!kind&&cmd[0]==8&&cmd[1]==50)e=c->sink?c->sink(30,0,0,c->ctx):-4;
 else if(!kind&&cmd[0]==8&&cmd[1]==17)e=(c->sink&&c->reactions)?c->sink(26,uint32_t(c->reactions[5]),0,c->ctx):-4;
 else if(!kind&&cmd[0]==8&&cmd[1]==51&&applyAttackDamage(c->s,c->reactions,c->vm))e=0;
 else if(kind)e=c->sink?c->sink(kind,uint32_t(cmd[2]),kind==11?256:0,c->ctx):-4;
 else if(cmd[0]==8&&(cmd[1]==11||cmd[1]==16||cmd[1]==46||cmd[1]==47||cmd[1]==48||cmd[1]==49||(cmd[1]==55&&(cmd[2]||(c->auxiliary&&*c->auxiliary)))))e=s2_generic_world_message(c->s,cmd[0],cmd[1],cmd[2],c->fetch,c->sink,c->ctx);
 else if(cmd[0]==8&&((cmd[1]>=34&&cmd[1]<=39)||cmd[1]==56))e=s2_generic_audio_message(c->s,cmd[0],cmd[1],cmd[2],c->sink,c->ctx);
 else e=c->reactions?s2_generic_event(c->s,c->vm,c->reactions,cmd,c->s[24],c->fetch,c->registry,c->ctx):s2_generic_message(c->s,cmd[0],cmd[1],cmd[2],c->s[24],c->fetch,c->ctx);
 if(e){
#ifdef S2_TRACE
std::fprintf(stderr,"effect %d: %d/%d/%d error %d\n",kind,cmd[0],cmd[1],cmd[2],e);
#endif
c->error=e;}
}
static int32_t random_value(void* v){auto* c=static_cast<Context*>(v);return c->random?c->random(c->ctx):0;}
extern "C" int s2_donkey_balance_behavior(int32_t*,Random,Sink,void*);
// Static physics + VM + body; world dimensions supplied as Q8.
static int runtime_step(const char* collision,int32_t* s,int32_t* vm,int32_t tick,int32_t worldWidth,int32_t worldHeight,Fetch fetch,Random random,void* ctx,int budget,int32_t* reactions,Registry registry,Sink sink,bool emptyDynamic=false,const int32_t* target=nullptr,bool targetSupplied=false,bool* auxiliary=nullptr,const int32_t* spawner=nullptr,bool balance=false,const int32_t* surfaces=nullptr,int surfaceCount=0){
 if(!s||!vm||!fetch||!collision||budget<1)return -1;
 if(((s[40]&4)&&!emptyDynamic&&!surfaces)||s[54])return -4;
 if(emptyDynamic)std::fill(s+64,s+68,0); // caller explicitly supplies zero dynamic candidates
 s[24]=tick;s2_animation_step(s[76],s[77],s[78],tick,s+20);s[39]&=~8;
 int32_t previous[2]={s[36],s[37]};int accepted[16];int ground=(surfaces&&(s[40]&4))?s2_actor_move_dynamic_file(collision,s+2,s,s+32,s+36,s[30],s[31],surfaces,surfaceCount,s+14,s+64,accepted):s2_actor_move_file(collision,s+2,s,s+32,s+36,s[30],s[31],s[40],s+14,s+60);if(ground<0)return ground;s[62]=ground;
 if(surfaces&&(s[40]&4)){s[60]=int32_t(uint32_t(s[0])-uint32_t(previous[0]));s[61]=int32_t(uint32_t(s[1])-uint32_t(previous[1]));}
 for(int i=0;i<4;i++)s[68+i]=s[14+i]+(surfaces?s[64+i]:0);if(s[14]||(surfaces&&s[64]))std::copy(s+8,s+11,s+11); // 0x002D0 restores configured Y triple
 if(balance){int e=s2_donkey_balance_behavior(s,random,sink,ctx);if(e)return e;}
 Context c{spawner,auxiliary,target,targetSupplied,s,fetch,random,ctx,0,vm,reactions,registry,sink};int e=s2_vm_step(vm,tick,get,query,effect,random_value,&c,budget);if(e<0)return e;if(c.error)return c.error;
 s[40]&=~16;if(reactions){if(reactions[56]&&!attackReactionActive(reactions,vm))reactions[56]=0;s2_generic_reaction_frame_end(reactions);}
 if(add(s[1],-s[31]*128)>worldHeight||add(s[0],-s[30]*128)>worldWidth||add(s[0],s[30]*128)<0){if(!sink)return -4;int removed=sink(19,0,0,ctx);if(removed)return removed;} // Original138C8 ->5168, owned removal only.
 s[26]=s[72];s[27]=s[73];s[30]=s[74];s[31]=s[75];s2_preserve_bottom(ground,s+32,s[31],s);
 std::fill(s+14,s+18,0);std::fill(s+64,s+68,0);return 0;
}

extern "C" int s2_generic_runtime_step(const char* p,int32_t* s,int32_t* vm,int32_t tick,int32_t w,int32_t h,Fetch fetch,Random random,void* ctx,int budget){return runtime_step(p,s,vm,tick,w,h,fetch,random,ctx,budget,nullptr,nullptr,nullptr);}
extern "C" int s2_generic_runtime_step_events(const char* p,int32_t* s,int32_t* vm,int32_t tick,int32_t w,int32_t h,Fetch fetch,Random random,void* ctx,int budget,int32_t* reactions,Registry registry){
 if(!reactions||!registry||reactions[0]<0||reactions[0]>16||reactions[1]<0||reactions[1]>8)return -1;return runtime_step(p,s,vm,tick,w,h,fetch,random,ctx,budget,reactions,registry,nullptr);}

extern "C" int s2_generic_runtime_step_effects(const char* p,int32_t* s,int32_t* vm,int32_t tick,int32_t w,int32_t h,Fetch fetch,Random random,void* ctx,int budget,int32_t* reactions,Registry registry,Sink sink){
 if(!reactions||!registry||!sink||reactions[0]<0||reactions[0]>16||reactions[1]<0||reactions[1]>8)return -1;return runtime_step(p,s,vm,tick,w,h,fetch,random,ctx,budget,reactions,registry,sink);}
// Selected actor update with an explicitly empty dynamic candidate list. This
// does not discover or ignore candidates from a populated world registry.
extern "C" int s2_generic_runtime_step_empty_dynamic(const char* p,int32_t* s,int32_t* vm,int32_t tick,int32_t w,int32_t h,Fetch fetch,Random random,void* ctx,int budget,int32_t* reactions,Registry registry,Sink sink){
 if(!reactions||!registry||!sink||reactions[0]<0||reactions[0]>16||reactions[1]<0||reactions[1]>8)return -1;return runtime_step(p,s,vm,tick,w,h,fetch,random,ctx,budget,reactions,registry,sink,true);}

// Explicit owner selection; this helper does not invent a world registry.
extern "C" int s2_generic_runtime_step_target(const char* p,int32_t* s,int32_t* vm,int32_t tick,int32_t w,int32_t h,Fetch fetch,Random random,void* ctx,int budget,int32_t* reactions,Registry registry,Sink sink,const int32_t* target,bool* auxiliary){
 if(!reactions||!registry||!sink||reactions[0]<0||reactions[0]>16||reactions[1]<0||reactions[1]>8)return -1;
 return runtime_step(p,s,vm,tick,w,h,fetch,random,ctx,budget,reactions,registry,sink,true,target,true,auxiliary);
}

extern "C" int s2_generic_runtime_step_spawner(const char* p,int32_t* s,int32_t* vm,int32_t tick,int32_t w,int32_t h,Fetch fetch,Random random,void* ctx,int budget,int32_t* reactions,Registry registry,Sink sink,const int32_t* target,bool* auxiliary,const int32_t* spawner){
 if(!spawner||!reactions||!registry||!sink||reactions[0]<0||reactions[0]>16||reactions[1]<0||reactions[1]>8)return -1;
 return runtime_step(p,s,vm,tick,w,h,fetch,random,ctx,budget,reactions,registry,sink,true,target,true,auxiliary,spawner);
}

extern "C" int s2_actor_probe_file(const char*,int,int32_t,int32_t,int32_t,int32_t,const int32_t*,int);
int s2_smoke_initial_probe(const char* collision,int32_t* s){
 for(int type=1;type<=2;type++){int hit=s2_actor_probe_file(collision,type,s[32],s[33],s[34],s[35],nullptr,0);if(hit<0)return hit;if(hit){std::fill_n(s+2,12,0);s[40]&=~3;break;}}return 0;
}

// Type71: factory6EB0 -> projectile121A4, definition804D7EC.
// Its initial and terminal animation are identical:123DC removes it on finish.
extern "C" int s2_smoke_runtime_init(const char* collision,const int32_t* anchor,int flips,int32_t tick,Fetch fetch,void* ctx,int32_t* s){
 int32_t def[12];if(!fetch||!fetch(0x0804d7ec,def,12,ctx))return -2;
 int e=s2_plain_runtime_init(anchor,flips,uint32_t(def[0]),tick,fetch,ctx,s);if(e)return e;s[40]=0x4a;
 s2_apply_axis_triple(s+2,def+6,0,0);s2_apply_axis_triple(s+2,def+9,1,0);
 if(flips&1){s[5]=int32_t(0u-uint32_t(def[6]));s[7]=int32_t(0u-uint32_t(def[8]));}
 if(flips&2){s[11]=int32_t(0u-uint32_t(def[9]));s[13]=int32_t(0u-uint32_t(def[11]));}
 // Constructor122A2/122C8: an initial overlap with either wall freezes motion.
 e=s2_smoke_initial_probe(collision,s);if(e)return e;
 return 0;
}
extern "C" int s2_smoke_runtime_step(const char* collision,int32_t* s,int32_t tick){
 if(!collision||!s)return -1;if(s[40]&1)return 0;
 s[24]=tick;s2_animation_step(s[76],s[77],s[78],tick,s+20);
 int e=s2_actor_move_file(collision,s+2,s,s+32,s+36,s[30],s[31],s[40],s+14,s+60);if(e<0)return e;
 if(!s[56]||s[20])s[40]|=1;
 std::fill_n(s+14,4,0);return 0;
}

extern "C" int s2_donkey_balance_step(const char* p,int32_t* s,int32_t* vm,int32_t tick,int32_t w,int32_t h,Fetch fetch,Random random,void* ctx,int budget,int32_t* reactions,Registry registry,Sink sink){
 if(!reactions||!registry||!sink||!random||reactions[0]<0||reactions[0]>16||reactions[1]<0||reactions[1]>8)return -1;
 return runtime_step(p,s,vm,tick,w,h,fetch,random,ctx,budget,reactions,registry,sink,true,nullptr,false,nullptr,nullptr,true);
}

// Movable props share original VM reactions, including lift, drop and kick.
extern "C" int s2_generic_runtime_step_dynamic(const char*p,int32_t*s,int32_t*vm,int32_t tick,int32_t w,int32_t h,Fetch fetch,Random random,void*ctx,int budget,int32_t*reactions,Registry registry,Sink sink,const int32_t*surfaces,int n){
 if(!surfaces||n<0||n>16||!reactions||!registry||!sink)return -1;
 return runtime_step(p,s,vm,tick,w,h,fetch,random,ctx,budget,reactions,registry,sink,true,nullptr,false,nullptr,nullptr,false,surfaces,n);
}

extern "C" int s2_generic_runtime_step_target_dynamic(const char*p,int32_t*s,int32_t*vm,int32_t tick,int32_t w,int32_t h,Fetch fetch,Random random,void*ctx,int budget,int32_t*reactions,Registry registry,Sink sink,const int32_t*target,bool*aux,const int32_t*surfaces,int n){
 if(!surfaces||n<0||n>16||!reactions||!registry||!sink)return -1;
 return runtime_step(p,s,vm,tick,w,h,fetch,random,ctx,budget,reactions,registry,sink,true,target,true,aux,nullptr,false,surfaces,n);
}

extern "C" int s2_generic_runtime_step_spawner_dynamic(const char*p,int32_t*s,int32_t*vm,int32_t tick,int32_t w,int32_t h,Fetch fetch,Random random,void*ctx,int budget,int32_t*reactions,Registry registry,Sink sink,const int32_t*target,bool*aux,const int32_t*spawner,const int32_t*surfaces,int n){
 if(!surfaces||n<0||n>16||!reactions||!registry||!sink||!spawner)return -1;
 return runtime_step(p,s,vm,tick,w,h,fetch,random,ctx,budget,reactions,registry,sink,true,target,true,aux,spawner,false,surfaces,n);
}
