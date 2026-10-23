// Original121A4/123DC/12470/12568, source types67 and69 (no homing).
#include <cstdint>
#include <algorithm>
using Fetch=int(*)(uint32_t,int32_t*,int,void*);
using Sink=int(*)(int,uint32_t,int32_t,void*);
extern "C" int s2_plain_runtime_init(const int32_t*,int,uint32_t,int32_t,Fetch,void*,int32_t*);
extern "C" int s2_generic_message(int32_t*,int,int,int32_t,int32_t,Fetch,void*);
extern "C" int s2_apply_axis_triple(int32_t*,const int32_t*,int,int);
extern "C" int s2_actor_probe_file(const char*,int,int32_t,int32_t,int32_t,int32_t,const int32_t*,int);
extern "C" int s2_actor_move_file(const char*,int32_t*,int32_t*,int32_t*,int32_t*,int,int,int,int32_t*,int32_t*);
extern "C" void s2_animation_step(int,int,int,int32_t,int32_t*);
extern "C" void s2_preserve_bottom(int,const int32_t*,int,int32_t*);
static uint32_t definition(int type){return type==146?0x0804d6e8:type==157?0x0804d7b8:type==68?0x0804d784:type==160?0x0804d64c:type==161?0x0804d680:type==67?0x0804d6b4:type==69?0x0804d71c:0;}
static int select(int32_t* s,uint32_t anim,int32_t tick,Fetch f,void* ctx){int32_t old[2]={s[48],s[49]};int e=s2_generic_message(s,8,4,int32_t(anim),tick,f,ctx);s[48]=old[0];s[49]=old[1];return e;}
static int end(int32_t* s,const int32_t* d,int32_t tick,Fetch f,Sink sink,void* ctx){if(!d[1]){s[40]|=1;return 0;}int e=sink(11,uint32_t(d[2]),256,ctx);if(e)return e;e=select(s,uint32_t(d[1]),tick,f,ctx);if(e)return e;s[40]&=~2;const int32_t zero[3]={};s2_apply_axis_triple(s+2,zero,0,0);s2_apply_axis_triple(s+2,zero,1,0);return 0;}
extern "C" int s2_projectile_init(const char* collision,int type,const int32_t* anchor,int flips,int32_t tick,Fetch f,Sink sink,void* ctx,int32_t* s,int32_t* deadline){
 if(!collision||!f||!sink||!s||!deadline||!definition(type))return -1;int32_t d[13];if(!f(definition(type),d,13,ctx))return -2;
 int e=s2_plain_runtime_init(anchor,flips,uint32_t(d[0]),tick,f,ctx,s);if(e)return e;s[40]=0x4a;*deadline=0;std::copy_n(d+3,3,s+41);s2_apply_axis_triple(s+2,d+6,0,0);s2_apply_axis_triple(s+2,d+9,1,0);
 if(flips&1){s[5]=int32_t(0u-uint32_t(d[6]));s[7]=int32_t(0u-uint32_t(d[8]));}if(flips&2){s[11]=int32_t(0u-uint32_t(d[9]));s[13]=int32_t(0u-uint32_t(d[11]));}
 for(int type_=1;type_<=2;type_++){int hit=s2_actor_probe_file(collision,type_,s[32],s[33],s[34],s[35],nullptr,0);if(hit<0)return hit;if(hit)return end(s,d,tick,f,sink,ctx);}return 0;
}
extern "C" int s2_projectile_step(const char* collision,int type,int32_t* s,int32_t tick,Fetch f,Sink sink,void* ctx){
 if(!collision||!s||!f||!sink||!definition(type))return -1;if(s[40]&1)return 0;int32_t d[13];if(!f(definition(type),d,13,ctx))return -2;
 s[24]=tick;s2_animation_step(s[76],s[77],s[78],tick,s+20);int ground=s2_actor_move_file(collision,s+2,s,s+32,s+36,s[30],s[31],s[40],s+14,s+60);if(ground<0)return ground;
 int e=0;if(!s[56])s[40]|=1;else if(s[47]==d[1]){if(s[20])s[40]|=1;}else if((s[40]&16)||s[14]||s[15]||s[16]||s[17])e=end(s,d,tick,f,sink,ctx);
 if(e)return e;std::copy_n(s+72,2,s+26);std::copy_n(s+74,2,s+30);s2_preserve_bottom(ground,s+32,s[31],s);std::fill_n(s+14,4,0);std::fill_n(s+64,4,0);return 0;
}
extern "C" int s2_projectile_receive(int type,int32_t* s,int32_t* deadline,const int32_t* event,int32_t tick,Fetch f,Sink sink,void* ctx){
 if(!s||!deadline||!event||!f||!sink||!definition(type))return -1;int32_t d[13];if(!f(definition(type),d,13,ctx))return -2;
 if(event[1]==5){if(uint32_t(d[12])&255){int e=end(s,d,tick,f,sink,ctx);return e?e:1;}if(*deadline>=tick)return 0;
  if((event[2]==2&&!s[18])||(event[2]==1&&s[18])){s[2]=s[5]=int32_t(0u-uint32_t(s[5]));s[3]=s[6]=d[7];s[4]=s[7]=int32_t(0u-uint32_t(s[7]));s[18]^=1;const int32_t reflected[3]={101,13,0};std::copy_n(reflected,3,s+41);*deadline=int32_t(uint32_t(tick)+10u);}return 0;
 }
 if((uint32_t(d[12])>>16)&255){int e=end(s,d,tick,f,sink,ctx);return e?e:1;}return 0;
}
// Source12308: homing changes axis targets after movement, retaining current
// speed and sprite flip. A target inside an axis body span leaves that axis.
extern "C" int s2_projectile_target(int type,int32_t* p,const int32_t* hero,Fetch f,void* ctx){
 if(!p||!hero||!f||!definition(type))return -1;int32_t d[13];if(!f(definition(type),d,13,ctx))return -2;
 if((p[40]&1)||p[47]==d[1]||!((uint32_t(d[12])>>8)&255))return 0;
 int64_t left=int64_t(p[0])-p[30]*128,top=int64_t(p[1])-p[31]*128;
 int x=d[8]<0?-d[8]:d[8],y=d[11]<0?-d[11]:d[11];
 if(left+p[30]*256<hero[0])p[7]=x;else if(left>hero[0])p[7]=-x;
 if(top+p[31]*256<hero[1])p[13]=y;else if(top>hero[1])p[13]=-y;return 0;
}
