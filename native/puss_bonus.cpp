// Source139 constructor0CFC/contact0C28: one score per body crossing.
#include <cstdint>
#include <algorithm>
using Fetch=int(*)(uint32_t,int32_t*,int,void*);
using Sink=int(*)(int,uint32_t,int32_t,void*);
extern "C" int s2_plain_runtime_init(const int32_t*,int,uint32_t,int32_t,Fetch,void*,int32_t*);
extern "C" int s2_generic_message(int32_t*,int,int,int32_t,int32_t,Fetch,void*);
extern "C" int s2_actor_contact_rects(const int32_t*,int,Fetch,void*,int32_t*,int);
extern "C" int s2_rect_overlap_xywh(const int32_t*,const int32_t*);
extern "C" int s2_puss_gate_init(const int32_t* anchor,int flips,int32_t tick,Fetch fetch,void* ctx,int32_t* s,int32_t* state){
 if(!state)return -1;int e=s2_plain_runtime_init(anchor,flips,0x0833ce8c,tick,fetch,ctx,s);if(e)return e;state[0]=state[1]=0;s[41]=0;s[42]=39;s[43]=0;return 0;
}
extern "C" int s2_puss_gate_contact(int32_t* s,int32_t* state,const int32_t* player,int blocked,int32_t tick,Fetch fetch,Sink sink,void* ctx){
 if(!s||!state||!player||!fetch||!sink)return -1;s[40]&=~16;if(blocked)return 0;
 int32_t body[4]={int32_t(uint32_t(s[0])-uint32_t(s[30]*128)),int32_t(uint32_t(s[1])-uint32_t(s[31]*128)),s[30]*256,s[31]*256},rects[255*4];int n=s2_actor_contact_rects(player,0,fetch,ctx,rects,255);if(n<0)return n;bool overlap=false;
 for(int i=0;i<n;i++)if(s2_rect_overlap_xywh(body,rects+i*4)){overlap=true;break;}
 if(!overlap){state[0]=0;return 0;}if(state[0])return 0;state[0]=1;int e=sink(29,0,0,ctx);if(e)return e;e=sink(1,0x08024cdc,0,ctx);if(e)return e;state[1]=int32_t(uint32_t(state[1])+1u);
 uint32_t animation=state[1]==8?0x0833cea4:state[1]==16?0x0833cebc:0;if(animation){int32_t old[2]={s[48],s[49]};e=s2_generic_message(s,8,4,int32_t(animation),tick,fetch,ctx);s[48]=old[0];s[49]=old[1];if(e)return e;}return 0;
}
