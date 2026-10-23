// Native source controller154 (B704/B7C0/B870): timed cake protection.
#include <cstdint>
#include <algorithm>
using Fetch=int(*)(uint32_t,int32_t*,int,void*);
using Sink=int(*)(int,uint32_t,int32_t,void*);
extern "C" int s2_plain_runtime_init(const int32_t*,int,uint32_t,int32_t,Fetch,void*,int32_t*);
extern "C" int s2_plain_runtime_step(int32_t*,int32_t);
extern "C" int s2_cake_init(const int32_t* xy,Fetch f,void* ctx,int32_t* pose,int32_t* aux,int32_t* state){
 if(!xy||!f||!pose||!aux||!state)return -1;int e=s2_plain_runtime_init(xy,0,0x08334a3c,0,f,ctx,pose);if(e)return e;
 int32_t anchor[2];if(!f(0x08024f0c,anchor,2,ctx))return -2;e=s2_plain_runtime_init(anchor,0,0x08334a54,0,f,ctx,aux);if(e)return e;
 pose[21]=2;std::fill_n(state,8,0);state[1]=state[2]=pose[77];return 0;
}
extern "C" int s2_cake_receive(int32_t* pose,int32_t* state,const int32_t* event,int32_t tick,Sink sink,void* ctx){
 if(!pose||!state||!event||!sink)return -1;if(event[1]!=38)return 0;--state[1];int e=0;
 if(!state[1]){e=sink(1,0x08024bbc,0,ctx);state[0]=1;}
 else{e=sink(20,1024,128,ctx);if(!e&&state[3]<tick){state[3]=tick+60;e=sink(11,0x08053f18,256,ctx);}pose[22]=state[2]-state[1];}
 return e?e:1;
}
extern "C" int s2_cake_step(int32_t* pose,int32_t* aux,int32_t* state,int32_t tick,int32_t remaining,Sink sink,void* ctx){
 if(!pose||!aux||!state||!sink)return -1;
 if(!state[0]){if(tick%150==0&&state[1]<state[2])pose[22]=state[2]-state[1];aux[0]=tick*4+0x11800;aux[1]=0x5a00;}
 // Source owner queues the final dialogue when the countdown reaches zero.
 if(!remaining&&!state[0]){state[0]=2;int e=sink(26,42,0,ctx);if(e)return e;}
 int e=s2_plain_runtime_step(pose,tick);return e?e:s2_plain_runtime_step(aux,tick);
}
