// Original type46: constructor1B4A0, gate1B438, notice1B350, update1B478.
#include <cstdint>
#include <algorithm>
// State8: simultaneous limit, second limit, live count, second count,
// active byte, preserve-live byte, optional signed spawn-type override, reserved.
extern "C" int s2_spawner_init(const int32_t* params,int32_t* s){
 if(!params||!s)return -1;std::fill_n(s,8,0);s[0]=params[4]?params[4]:5;s[1]=params[7];s[4]=(uint32_t(params[0])>>2)&1;s[5]=(uint32_t(params[0])>>3)&1;s[6]=int16_t(uint32_t(params[5]));return 0;
}
extern "C" int s2_spawner_can_create(const int32_t* s){if(!s)return -1;return (s[4]&255)&&s[2]<s[0]&&s[3]<s[1];}
extern "C" int s2_spawner_created(int32_t* s){if(!s)return -1;s[2]=int32_t(uint32_t(s[2])+1u);s[3]=int32_t(uint32_t(s[3])+1u);return 0;}
extern "C" int s2_spawner_notice(int32_t* s,int32_t tag,const int32_t* event){
 if(!s||!event)return -1;if(event[0]!=9||event[1]!=4)return -4;
 if(event[2]!=int32_t(uint32_t(tag)+1000u))return 0;
 if(!(s[4]&255)){s[4]=1;return 1;}
 s[3]=int32_t(uint32_t(s[3])-1u);if(!(s[5]&255))s[2]=int32_t(uint32_t(s[2])-1u);return 1;
}
extern "C" int32_t s2_spawner_tag(int32_t tag,int32_t id){return tag?tag:int32_t(uint32_t(id)+1000u);}
