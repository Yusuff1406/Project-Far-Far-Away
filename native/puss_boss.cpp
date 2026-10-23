// Original Puss encounter74: C3D4/C48C/CAB4. Victory requires three captures.
#include <cstdint>
#include <algorithm>
using Fetch=int(*)(uint32_t,int32_t*,int,void*);using Sink=int(*)(int,uint32_t,int32_t,void*);
extern "C" int s2_plain_runtime_init(const int32_t*,int,uint32_t,int32_t,Fetch,void*,int32_t*);
extern "C" int s2_plain_runtime_step(int32_t*,int32_t);
extern "C" void s2_animation_step(int,int,int,int32_t,int32_t*);
extern "C" int s2_generic_message(int32_t*,int,int,int32_t,int32_t,Fetch,void*);
extern "C" int s2_apply_axis_triple(int32_t*,const int32_t*,int,int);
extern "C" int s2_actor_move_file(const char*,int32_t*,int32_t*,int32_t*,int32_t*,int,int,int,int32_t*,int32_t*);
extern "C" void s2_preserve_bottom(int,const int32_t*,int,int32_t*);
// State9 mirrors contiguous original words1CC..1EC.
static int anim(int32_t* p,uint32_t a,int tick,Fetch f,void* ctx){return s2_generic_message(p,8,4,int32_t(a),tick,f,ctx);}
static int axis(int32_t* p,uint32_t a,int which,int reflect,Fetch f,void* ctx){int32_t t[3];if(!f(a,t,3,ctx))return -2;return s2_apply_axis_triple(p+2,t,which,reflect);}
static int sound(uint32_t a,Sink sink,void* ctx){return sink(11,a,256,ctx);}
static int run(int32_t* p,int32_t* s,int tick,Fetch f,void* ctx){if(s[2]!=2)s[3]=0;int e=anim(p,0x08344e14,tick,f,ctx);if(!e)e=axis(p,0x08025258,1,0,f,ctx);if(!e)e=axis(p,0x08025228,0,p[18],f,ctx);s[0]=1;return e;}
static int jump(int32_t* p,int32_t* s,int tick,Fetch f,Sink sink,void* ctx){if(s[2]!=2)s[3]=0;int e=anim(p,0x08344e14,tick,f,ctx);if(!e)e=axis(p,0x08025234,0,p[18],f,ctx);if(!e)e=axis(p,0x0802524c,1,0,f,ctx);if(!e)e=sound(0x08053c90,sink,ctx);s[0]=2;return e;}
static int restart(int32_t* p,int32_t* s,int tick,Fetch f,Sink sink,void* ctx){int e=0;if(s[1]==0){e=run(p,s,tick,f,ctx);if(!e)e=axis(p,0x0802524c,1,0,f,ctx);if(!e)e=sound(0x08053c90,sink,ctx);}if(!e&&s[1]==1)e=jump(p,s,tick,f,sink,ctx);if(!e&&s[1]>1){s[1]=0;e=run(p,s,tick,f,ctx);if(!e)e=axis(p,0x0802524c,1,0,f,ctx);if(!e)e=sound(0x08053c90,sink,ctx);}if(s[2]==2)s[3]=0;return e;}
static int vulnerable(int32_t* p,int32_t* s,int tick,Fetch f,Sink sink,void* ctx){int e=sound(s[2]<=1?0x08053d98:0x08053e28,sink,ctx);if(!e)e=anim(p,s[2]<=1?0x08344e2c:0x08344de4,tick,f,ctx);if(!e)e=axis(p,0x08025240,0,0,f,ctx);s[0]=3;s[4]=tick+150;return e;}
static int bounce(int32_t* p,Sink sink,void* ctx){int e=sound(0x08053e1c,sink,ctx);p[5]=0;p[7]=-p[7];p[18]=p[7]<0;return e;}
static int finish(int32_t* s,int tag,int tick,Sink sink,void* ctx){int e=sink(26,uint32_t(tag),0,ctx);s[4]=tick+5;s[0]=5;return e;}
extern "C" int s2_puss_boss_init(const int32_t* xy,Fetch f,void* ctx,int32_t* p,int32_t* s){int e=s2_plain_runtime_init(xy,1,0x08344e44,0,f,ctx,p);if(e)return e;p[40]=10;std::fill_n(s,9,0);int32_t event[3];if(!f(0x08025264,event,3,ctx))return -2;std::copy_n(event,3,p+41);return 0;}
extern "C" int s2_puss_boss_receive(int32_t* p,int32_t* s,const int32_t* event,int tag,int tick,Fetch f,Sink sink,void* ctx){
 if(event[1]==10&&s[0]==3){++s[1];int e=axis(p,0x08025240,0,0,f,ctx);if(!e)e=axis(p,0x08025240,1,0,f,ctx);if(s[2]<=1){if(!e)e=sound(0x08053e70,sink,ctx);if(!e)e=anim(p,0x08344dfc,tick,f,ctx);}else if(!e)e=anim(p,0x08344e5c,tick,f,ctx);s[4]=tick+120;s[0]=4;++s[6];s[8]=tick+45;return e?e:1;}
 if(event[1]==11&&s[0]==4){if(s[8]>=tick)return 0;s[5]=tick+60;int e=s[2]>2?finish(s,tag,tick,sink,ctx):restart(p,s,tick,f,sink,ctx);return e?e:1;}return 0;
}
extern "C" int s2_puss_boss_behavior(int32_t* p,int32_t* s,int tag,int tick,Fetch f,Sink sink,void* ctx){int32_t event[3];if(!f(s[5]<tick?0x08025264:0x08025270,event,3,ctx))return -2;std::copy_n(event,3,p+41);int e=0;if(tick==120)e=run(p,s,tick,f,ctx);if(e)return e;
 switch(s[0]){
 case 1:if(p[15]||p[16]||p[65]||p[66]){int old=s[3]++;if(s[2]==2&&s[3]<=8){s[3]=old;e=jump(p,s,tick,f,sink,ctx);}else if(s[3]>8)e=vulnerable(p,s,tick,f,sink,ctx);else e=bounce(p,sink,ctx);}break;
 case 2:if(p[14]||p[64]){if(s[3]>8)e=vulnerable(p,s,tick,f,sink,ctx);else if(s[2]==2)e=run(p,s,tick,f,ctx);else{e=sound(0x08053c90,sink,ctx);if(!e)e=axis(p,0x0802524c,1,0,f,ctx);}}if(!e&&(p[15]||p[16]||p[65]||p[66])){e=bounce(p,sink,ctx);++s[3];}break;
 case 3:if(s[4]<tick){if(s[2]==2)s[3]=-4;e=restart(p,s,tick,f,sink,ctx);}break;
 case 4:if(s[8]<tick){if(s[6]==3)e=finish(s,tag,tick,sink,ctx);else{e=sink(35,0,0,ctx);if(s[2]==2)s[3]=-4;++s[2];}}break;
 case 5:if(s[4]<tick)e=sink(1,0x08024be0,0,ctx);break;default:break;
 }p[40]&=~16;return e;
}
extern "C" int s2_puss_boss_step(const char* path,int32_t* p,int32_t* s,int tag,int tick,Fetch f,Sink sink,void* ctx){std::fill_n(p+64,4,0);p[24]=tick;s2_animation_step(p[76],p[77],p[78],tick,p+20);p[39]&=~8;int ground=s2_actor_move_file(path,p+2,p,p+32,p+36,p[30],p[31],p[40],p+14,p+60);if(ground<0)return ground;int e=s2_puss_boss_behavior(p,s,tag,tick,f,sink,ctx);std::copy_n(p+72,2,p+26);std::copy_n(p+74,2,p+30);s2_preserve_bottom(ground,p+32,p[31],p);std::fill_n(p+14,4,0);return e;}
