// Selected normalized effects of 0x080180B0 / 0x08013714. Resource allocation,
// script VM, event registration and additional original fields are separate.
#include <cstdint>
#include <algorithm>
extern "C" void s2_animation_restart(int,int,int,int32_t,int32_t*);
extern "C" int s2_generic_actor_init(const int32_t* bounds,const int32_t* anchor,int flags,int animation,int rate,int count,int32_t tick,int32_t* s){
 if(!bounds||!anchor||!s||bounds[2]<0||bounds[2]>255||bounds[3]<0||bounds[3]>255||rate<0||rate>255||count<1||count>255)return -1;
 std::fill(s,s+40,0);s[18]=flags&1;s[38]=(flags>>1)&1;s[19]=animation;s[24]=tick;s[30]=bounds[2];s[31]=bounds[3];int32_t x=int32_t((uint32_t(bounds[0])<<8)+uint32_t(bounds[2]*128)),y=int32_t((uint32_t(bounds[1])<<8)+uint32_t(bounds[3]*128));
 s[0]=int32_t(uint32_t(anchor[0])+(s[18]?0u-uint32_t(x):uint32_t(x)));s[1]=int32_t(uint32_t(anchor[1])+(s[38]?0u-uint32_t(y):uint32_t(y)));s[32]=int32_t(uint32_t(s[0])-uint32_t(bounds[2]*128));s[33]=int32_t(uint32_t(s[1])-uint32_t(bounds[3]*128));s[34]=bounds[2]*256;s[35]=bounds[3]*256;s2_animation_restart(rate,count,0,tick,s+20);return 0;
}
