// Original type141 026B8 and type140 horizontal seam02650.
#include <cstdint>
extern "C" int s2_mouse_spawn_step(int32_t* state,int score){
 if(!state)return -1;int created=state[0],spawn=0;
 if(created<=2&&(state[1]==created*450||score==created*4)){state[0]++;spawn=1;}
 state[1]=int32_t(uint32_t(state[1])+1u);return spawn;
}
extern "C" void s2_mouse_wrap(int32_t* xy){
 if(!xy)return;if(xy[0]<0)xy[0]=int32_t(uint32_t(xy[0])+240u*256u);else if(xy[0]>240*256)xy[0]=int32_t(uint32_t(xy[0])-240u*256u);
}

// Original type138 behavior9D84. Called after physics, before139B8 scripts.
// A received foot strike sets pose40 bit16; it awards once on the next update.
using BalanceRandom=int32_t(*)(void*);
using BalanceSink=int(*)(int,uint32_t,int32_t,void*);
extern "C" int s2_donkey_balance_behavior(int32_t* s,BalanceRandom random,BalanceSink sink,void* ctx){
 if(!s||!random||!sink)return -1;
 if(s[40]&16){
  int e=sink(29,0,0,ctx);if(e)return e;int32_t target=s[7];
  if(target<0&&target>-448)s[7]=int32_t(uint32_t(target)-28u);
  if(uint32_t(target)-1u<=446u)s[7]=int32_t(uint32_t(target)+28u);
  if(target==0)s[7]=(random(ctx)&256)?25:-25;
 }
 if(s[15]||s[65]||s[16]||s[66]){s[5]=0;s[7]=int32_t(0u-uint32_t(s[7]));}
 return 0;
}

// Original0021A recurrence, scoped to the owned bonus session.
extern "C" int32_t s2_source_random(uint32_t* state){
 if(!state)return 0;*state=*state*0x41c64e6du+0x3039u;return int32_t(*state>>17);
}

// Original target controller144:16EDC/16E08/16E80. State5 holds the
// source horizontal triple1C0..1C8, countdown1CC and variant byte1D0.
extern "C" int s2_target_generator_init(const int32_t* anchor,int variant,int32_t* xy,int32_t* state){
 if(!anchor||!xy||!state)return -1;variant=uint8_t(variant);xy[0]=variant?240*256:0;xy[1]=anchor[1];state[0]=0;state[1]=state[2]=256;state[3]=1;state[4]=variant;return 0;
}
extern "C" int s2_target_generator_step(int32_t* state){
 if(!state)return -1;state[3]=int32_t(uint32_t(state[3])-1u);if(state[3])return 0;state[3]=60;return state[4]?143:142;
}
extern "C" int s2_target_generator_notice(int32_t* state,const int32_t* packet){
 if(!state||!packet)return -1;if(packet[0]==2&&packet[1]==3&&state[2]<=639)state[2]=int32_t(uint32_t(state[2])+12u);return 0;
}
