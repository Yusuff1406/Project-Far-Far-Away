#pragma once
#include <algorithm>
#include <cstdint>
// Optional editor damage, in half-hit units. Zero leaves original scripts intact.
static inline int attackDamageUnits(int choice){return choice<0?0:choice==0?1:choice==1?2:choice==2?4:8;}
// Reactions[56..59] are reserved in the source ABI and already serialized.
static inline void armAttackDamage(int32_t*r,const int32_t*vm,int units){
 if(units<1||units>8||vm[2]<0||vm[2]>9)return;
 r[56]=units;r[58]=vm[8+vm[2]*5];r[59]=0x53324447;
}
static inline bool attackReactionActive(const int32_t*r,const int32_t*vm){
 if(r[59]!=0x53324447||r[56]<1||r[56]>8)return false;
 for(int i=0;i<=vm[2]&&i<10;i++)if(vm[8+i*5]==r[58])return true;
 return false;
}
static inline bool applyAttackDamage(int32_t*pose,int32_t*r,const int32_t*vm){
 if(!r||!attackReactionActive(r,vm))return false;
 int units=r[56]+(r[57]&1);r[57]=units&1;
 pose[52]=std::max(0,pose[52]-units/2);return true;
}
