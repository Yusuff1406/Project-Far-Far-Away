// Original first Fairy Godmother controller155:2760/28D0/2968/2B34/2C24.
#include <cstdint>
#include <algorithm>
using Fetch=int(*)(uint32_t,int32_t*,int,void*);
using Sink=int(*)(int,uint32_t,int32_t,void*);
extern "C" int s2_plain_runtime_init(const int32_t*,int,uint32_t,int32_t,Fetch,void*,int32_t*);
extern "C" int s2_plain_runtime_step(int32_t*,int32_t);
extern "C" int s2_generic_message(int32_t*,int,int,int32_t,int32_t,Fetch,void*);
extern "C" int s2_apply_axis_triple(int32_t*,const int32_t*,int,int);
extern "C" void s2_motion_step(int32_t*,int32_t*);
// State8: HP,maxHP,marker,reserved,deadline,phase,unused,finishQueued.
static int animation(int32_t* p,uint32_t a,int tick,Fetch f,void* ctx){return s2_generic_message(p,8,4,int32_t(a),tick,f,ctx);}
static int stop(int32_t* p,Fetch f,void* ctx){int32_t zero[3];if(!f(0x08024aec,zero,3,ctx))return -2;s2_apply_axis_triple(p+2,zero,0,0);return s2_apply_axis_triple(p+2,zero,1,0);}
extern "C" int s2_fairy155_init(const int32_t* xy,Fetch f,void* ctx,int32_t* p,int32_t* s){int e=s2_plain_runtime_init(xy,1,0x0831e1a8,0,f,ctx,p);if(e)return e;e=stop(p,f,ctx);if(e)return e;std::fill_n(s,8,0);s[0]=s[1]=3;return 0;}
extern "C" int s2_fairy155_receive(int32_t* p,int32_t* s,const int32_t* event,int tick,Fetch f,Sink sink,void* ctx){
 if(!p||!s||!event||!f||!sink)return -1;int id=event[1];if(s[4]>=tick||(id!=13&&id!=3&&id!=5&&id!=1&&id!=2)||s[5]==4)return 0;int e=0;
 if(s[0]==3){e=sink(26,90,0,ctx);if(!e)e=sink(1,0x08024af8,0,ctx);}else if(s[0]==2){e=sink(26,91,0,ctx);if(!e)e=sink(1,0x08024b04,0,ctx);}if(e)return e;
 --s[0];s[4]=tick+15;
 if(!s[0]){e=sink(32,0,0,ctx);if(!e)e=sink(11,0x08053eb8,256,ctx);if(!e)e=animation(p,0x0831e1c0,tick,f,ctx);s[5]=4;s[4]=tick+120;return e?e:0;}
 e=sink(11,0x08053eac,256,ctx);if(!e)e=animation(p,0x0831e190,tick,f,ctx);s[5]=1;if(++s[2]==4)s[2]=0;return e?e:1;
}
extern "C" int s2_fairy155_behavior(int32_t* p,int32_t* s,const int32_t* markers,const int32_t* target,int visible,int tick,Fetch f,Sink sink,void* ctx){
 if(!p||!s||!markers||!target||!f||!sink)return -1;int e=0;
 if(s[5]==0){if(tick%30)p[18]=p[0]>target[0];if(tick%120==0){if(visible)e=sink(11,0x08053ec4,256,ctx);s[5]=2;if(!e)e=animation(p,0x0831e178,tick,f,ctx);}}
 else if(s[5]==1){int32_t dx=int32_t(uint32_t(markers[(s[2]&3)*2])-uint32_t(p[0]))>>8,dy=int32_t(uint32_t(markers[(s[2]&3)*2+1])-uint32_t(p[1]))>>8;p[18]=p[0]>target[0];if(int64_t(dx)*dx+int64_t(dy)*dy<100){e=animation(p,0x0831e1a8,tick,f,ctx);if(!e)e=stop(p,f,ctx);s[5]=0;}else{if(dx>5)p[5]=768;else if(dx< -5)p[5]=-768;if(dy>5)p[11]=768;else if(dy< -5)p[11]=-768;}}
 else if(s[5]==2&&(p[20]&255)){e=sink(31,157,0,ctx);if(!e)e=animation(p,0x0831e1a8,tick,f,ctx);s[5]=1;}
 else if(s[5]==4){if(tick==s[4]&&!s[7]){s[7]=1;e=sink(26,48,0,ctx);}else if(tick>s[4]&&!s[7])e=sink(1,0x08024be0,0,ctx);}
 return e;
}
extern "C" int s2_fairy155_step(int32_t* p,int32_t* s,const int32_t* markers,const int32_t* target,int visible,int tick,Fetch f,Sink sink,void* ctx){s2_motion_step(p+2,p);int e=s2_plain_runtime_step(p,tick);return e?e:s2_fairy155_behavior(p,s,markers,target,visible,tick,f,sink,ctx);}
// Final controller156: 2DDC/2E70/2F00/2FB4/31D0/3224/33D8.
static int finalEnd(int32_t* p,int32_t* s,int32_t* aux,int tick,Fetch f,Sink sink,void* ctx){int e=sink(11,0x08053ed0,256,ctx);if(!e)e=animation(p,0x0831e1d8,tick,f,ctx);s[5]=4;s[4]=tick+30;int32_t xy[2]={p[0],p[1]};if(!e)e=s2_plain_runtime_init(xy,p[38]?2:0,0x0831e1f0,tick,f,ctx,aux);return e;}
extern "C" int s2_fairy156_init(const int32_t* xy,Fetch f,void* ctx,int32_t* p,int32_t* s,int32_t* aux){std::fill_n(aux,80,0);int e=s2_fairy155_init(xy,f,ctx,p,s);s[6]=156;return e;}
extern "C" int s2_fairy156_receive(int32_t* p,int32_t* s,int32_t* aux,const int32_t* event,int tick,Fetch f,Sink sink,void* ctx){int id=event[1];if(s[4]>=tick||(id!=13&&id!=3&&id!=5&&id!=1&&id!=2)||s[5]==4)return 0;int e=0;if(s[0]==3)e=sink(1,0x08024b28,0,ctx);else if(s[0]==2)e=sink(1,0x08024b34,0,ctx);if(e)return e;--s[0];s[4]=tick+15;if(!s[0]){e=finalEnd(p,s,aux,tick,f,sink,ctx);return e?e:0;}e=animation(p,0x0831e190,tick,f,ctx);s[5]=1;if(++s[2]==4)s[2]=0;return e?e:1;}
extern "C" int s2_fairy156_behavior(int32_t* p,int32_t* s,int32_t* aux,const int32_t* markers,const int32_t* target,int tick,int remaining,int random,Fetch f,Sink sink,void* ctx){
 int e=0;if(remaining==31)e=finalEnd(p,s,aux,tick,f,sink,ctx);if(e)return e;
 if(s[5]==0){if(tick%30)p[18]=p[0]>target[0];if(tick%120==0){s[5]=2;if(random%3==0)e=sink(11,0x08053ec4,256,ctx);if(!e)e=sink(11,0x08054050,256,ctx);if(!e)e=animation(p,0x0831e178,tick,f,ctx);}}
 else if(s[5]==1){int32_t dx=int32_t(uint32_t(markers[(s[2]&3)*2])-uint32_t(p[0]))>>8,dy=int32_t(uint32_t(markers[(s[2]&3)*2+1])-uint32_t(p[1]))>>8;p[18]=p[0]>target[0];if(int64_t(dx)*dx+int64_t(dy)*dy<100){e=animation(p,0x0831e1a8,tick,f,ctx);if(!e)e=stop(p,f,ctx);s[5]=0;}else{if(dx>5)p[5]=256;else if(dx< -5)p[5]=-256;if(dy>5)p[11]=256;else if(dy< -5)p[11]=-256;}}
 else if(s[5]==2&&(p[20]&255)){e=sink(31,157,0,ctx);if(!e)e=animation(p,0x0831e1a8,tick,f,ctx);if(!e)e=animation(p,0x0831e190,tick,f,ctx);s[5]=1;if(++s[2]==4)s[2]=0;}
 else if(s[5]==4){if(tick==s[4]&&!s[7]){s[7]=1;e=sink(26,50,0,ctx);}else if(tick>s[4]&&!s[7])e=sink(1,0x08024be0,0,ctx);}return e;
}
extern "C" int s2_fairy156_step(int32_t* p,int32_t* s,int32_t* aux,const int32_t* markers,const int32_t* target,int tick,int remaining,int random,Fetch f,Sink sink,void* ctx){if(aux[56]){int e=s2_plain_runtime_step(aux,tick);if(e)return e;}s2_motion_step(p+2,p);int e=s2_plain_runtime_step(p,tick);return e?e:s2_fairy156_behavior(p,s,aux,markers,target,tick,remaining,random,f,sink,ctx);}
