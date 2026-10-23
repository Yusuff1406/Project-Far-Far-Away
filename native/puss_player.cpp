// Original Puss103B8 attack,10470 wall hold and FED8 wall jump.
#include <cstdint>
#include <algorithm>
#include <cmath>
using Fetch=int(*)(uint32_t,int32_t*,int,void*);
using Sink=int(*)(int,uint32_t,int32_t,void*);
extern "C" int s2_generic_message(int32_t*,int,int,int32_t,int32_t,Fetch,void*);
extern "C" int s2_shrek_locomotion_enter(int32_t*,int32_t*,int32_t*,int32_t*,int,int,int32_t,int32_t,uint32_t,const int32_t*,Fetch,void*);
extern "C" int s2_campaign_locomotion_enter(int,int,int,int32_t,int32_t*,int32_t*,int32_t*,Fetch,void*);
extern "C" int s2_apply_axis_triple(int32_t*,const int32_t*,int,int);
static int select(int id,int32_t* s,int32_t* b,int32_t tick,Fetch f,void* ctx){
 for(int i=0;i<40;i++){uint32_t address=0x0804c4fc+i*40;int32_t r[10];if(!f(address,r,10,ctx))return -2;if(r[0]==999)break;if(r[0]!=id)continue;int e=s2_generic_message(s,8,4,r[1],tick,f,ctx);if(e)return e;b[0]=int32_t(address);b[1]=r[9];return 0;}return -2;
}
extern "C" int s2_puss_locomotion_enter(int action,int held,int32_t tick,int32_t* s,int32_t* e,int32_t* status,int32_t* b,const int32_t* event,Fetch f,void* ctx){
 int previous=e[0];int v=s2_shrek_locomotion_enter(s,e,status,b,action,held,tick,tick,0x0804c4fc,event,f,ctx);if(v)return v;
 if((action==0x150&&previous==0)||(action==0x158&&previous==1)){v=select(action==0x150?25:26,s,b,tick,f,ctx);if(v)return v;e[0]=action==0x150?20:21;}return 0;
}
static int physics(int id,int axis,int flip,int32_t* s,int32_t* b,Fetch f,void* ctx){
 for(int i=0;i<40;i++){uint32_t address=0x0804c4fc+i*40;int32_t r[10];if(!f(address,r,10,ctx))return -2;if(r[0]==999)break;if(r[0]!=id)continue;b[0]=int32_t(address);return s2_apply_axis_triple(s+2,r+(axis?5:2),axis,flip);}return -2;
}
extern "C" int s2_puss_wall_enter(int32_t* s,int32_t* e,int32_t* b,int32_t tick,Fetch f,Sink sink,void* ctx){
 if(!s||!e||!b||!f||!sink)return -1;int v=sink(11,0x08054044,256,ctx);if(v)return v;v=physics(20,0,0,s,b,f,ctx);if(v)return v;v=physics(20,1,0,s,b,f,ctx);if(v)return v;v=select(20,s,b,tick,f,ctx);if(v)return v;e[0]=16;return 0;
}
extern "C" int s2_puss_wall_jump(int32_t* s,int32_t* e,int32_t* status,int32_t* b,int held,int32_t tick,const int32_t* event,Fetch f,void* ctx){
 int v=s2_puss_locomotion_enter(held&112?0x160:0x170,held,tick,s,e,status,b,event,f,ctx);if(v)return v;
 if(!(held&112)){const int32_t fall[3]={0,49,1792};return s2_apply_axis_triple(s+2,fall,1,0);}
 v=physics(23,1,0,s,b,f,ctx);if(v)return v;
 if(((held&32)&&!s[18])||((held&16)&&s[18]))return physics(23,0,s[18]^1,s,b,f,ctx);return 0;
}
extern "C" int s2_puss_air_enter(int32_t* s,int32_t* e,int32_t* b,int32_t tick,Fetch f,void* ctx){
 if(!s||!e||!b||!f)return -1;int v=select(24,s,b,tick,f,ctx);if(v)return v;e[0]=19;const int32_t event[3]={2,3,0};std::copy_n(event,3,s+41);return 0;
}
extern "C" int s2_puss_air_behavior(int32_t* s,int32_t* e,int32_t* status,int32_t* b,int held,int grounded,int32_t tick,const int32_t* event,Fetch f,void* ctx){
 if(!s||!e||!b||!f||e[0]!=19)return -1;
 if(s[20]&255){if(grounded)return s2_puss_locomotion_enter(0x158,held,tick,s,e,status,b,event,f,ctx);int32_t thresholds[2];if(!f(0x0804b6ec,thresholds,2,ctx))return -2;
  if(s[11]>thresholds[0])return s2_shrek_locomotion_enter(s,e,status,b,0x168,held,tick,tick,0x0804c4fc,event,f,ctx);
  if(s[11]>thresholds[1])return s2_shrek_locomotion_enter(s,e,status,b,0x170,held,tick,tick,0x0804c4fc,event,f,ctx);
  int v=select(3,s,b,tick,f,ctx);if(v)return v;e[0]=2;return 0;
 }
 if(grounded){int32_t row[10];if(!f(0x0804c4fc,row,10,ctx))return -2;b[0]=0x0804c4fc;return s2_apply_axis_triple(s+2,row+2,0,0);}return 0;
}

extern "C" int s2_actor_probe_file(const char*,int,int32_t,int32_t,int32_t,int32_t,const int32_t*,int);
extern "C" int s2_puss_wall_query_file(const char* path,const int32_t* s,int direction,const int32_t* surfaces,int count){
 if(!path||!s||count<0||count>16||(!surfaces&&count))return -1;if(direction!=1&&direction!=2)return 0;
 int w=s[30]*256,h=s[31]*256;int32_t left=int32_t(uint32_t(s[0])-uint32_t(w/2)),top=int32_t(uint32_t(s[1])-uint32_t(h/2));int32_t x=direction==2?int32_t(uint32_t(left)-256u):int32_t(uint32_t(left)+uint32_t(w));
 int hit=s2_actor_probe_file(path,direction==2?1:2,x,top,256,h,surfaces,count);if(hit<=0)return hit;
 for(int type:{3,5,4}){hit=s2_actor_probe_file(path,type,x,top,256,h,surfaces,count);if(hit)return hit<0?hit:0;}return 1;
}

// Source FC8C/FD40. Book5/7 hold +264 speed/+268 angle; extra7 is +26C.
// Native angle only selects21/22; this is not BIOS ArcTan2 bit-exact.
extern "C" int s2_puss_rail_angle(int dx,int dy){return int(std::atan2(double(dy),double(dx))*4096.0/6.2831853071795864769+4096.0)&4095;}
extern "C" int s2_puss_rail_enter(int32_t* s,int32_t* e,int32_t* b,int speed,int angle,int32_t tick,Fetch f,void* ctx){
 if(!s||!e||!b||!f)return -1;b[5]=speed;b[7]=angle;s[5]=s[7]=speed;int v=physics(21,1,0,s,b,f,ctx);if(v)return v;s[18]=speed>0?0:1;
 int a=angle-512;if(a<0)a=512-angle;int c=3584-angle;if(c<0)c=angle-3584;
 v=select(a<128||c<128?21:22,s,b,tick,f,ctx);if(v)return v;e[0]=18;return 0;
}
extern "C" int s2_puss_rail_behavior(int32_t* s,int32_t* e,int32_t* status,int32_t* b,int held,int pressed,int railPresent,int grounded,int32_t tick,const int32_t* event,Fetch f,Sink sink,void* ctx){
 if(!s||!e||!status||!b||!f||!sink||e[0]!=18)return -1;
 if(pressed&1)return s2_puss_locomotion_enter(0x160,held,tick,s,e,status,b,event,f,ctx);
 if(!railPresent){if(grounded)return s2_puss_locomotion_enter(0x158,held,tick,s,e,status,b,event,f,ctx);
  int v=s2_puss_locomotion_enter(0x1d0,held,tick,s,e,status,b,event,f,ctx);
  if(v)return v;s[5]=s[7]=b[5];return 0;
 }
 if(e[7]<tick){int v=sink(11,0x08053e64,256,ctx);if(v)return v;e[7]=int32_t(uint32_t(tick)+7u);}
 int32_t speed=b[5];bool with=((held&32)&&s[18])||((held&16)&&!s[18]);bool against=((held&32)&&!s[18])||((held&16)&&s[18]);
 if(with){speed=int32_t(uint32_t(speed)*3u*128u)>>8;if(speed>2048)speed=2048;}
 else if(against)speed=int32_t(uint32_t(speed)<<6)>>8;
 s[5]=s[7]=speed;return 0;
}
