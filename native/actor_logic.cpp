// Direct translations of original Thumb routines at 0x0801682C and 0x080002DC.
#include <cstdint>
extern "C" void s2_animation_step(int rate,int count,int flags,int32_t now,int32_t* state){
 // state = finished byte (stored as int), direction (0 forward,1 reverse),
 // sequence index, next deadline. The caller owns stopping on finished.
 if(!state||count<=0||rate<0||rate>255||now<state[3])return;
 const int32_t direction=state[1];if(direction!=0&&direction!=1)return;
 if(direction==0){if(state[2]==count-1){if(flags&1)state[2]=0;else state[0]=1;}else state[2]+=1;}
 else{if(state[2]==0){if(flags&1)state[2]=count-1;else state[0]=1;}else state[2]-=1;}
 const int32_t interval=rate+1;state[3]=int32_t(uint32_t(state[3])+uint32_t(interval));
 if(now>state[3])state[3]=int32_t(uint32_t(now)+uint32_t(interval));
}
extern "C" int32_t s2_approach_step(int32_t current,int32_t step,int32_t target){
 if(current<target){int32_t result=int32_t(uint32_t(current)+uint32_t(step));return result>target?target:result;}
 if(current>target){int32_t result=int32_t(uint32_t(current)-uint32_t(step));return result<target?target:result;}
 return current;
}
// Original 0x0800B96C: step both parameter axes, then integrate their values.
extern "C" void s2_motion_step(int32_t* parameters,int32_t* position){
 if(!parameters||!position)return;
 parameters[3]=s2_approach_step(parameters[3],parameters[4],parameters[5]);position[0]=int32_t(uint32_t(position[0])+uint32_t(parameters[3]));
 parameters[9]=s2_approach_step(parameters[9],parameters[10],parameters[11]);position[1]=int32_t(uint32_t(position[1])+uint32_t(parameters[9]));
}
// Original state-axis application (0x0800EC3C / 0x0800EC94 after lookup).
extern "C" int s2_apply_axis_triple(int32_t* parameters,const int32_t* triple,int axis,int reflect){
 if(!parameters||!triple||(axis!=0&&axis!=1))return -1;int32_t* p=parameters+axis*6;
 int32_t initial=triple[0],step=triple[1],target=triple[2];if(reflect&255){initial=int32_t(0u-uint32_t(initial));target=int32_t(0u-uint32_t(target));}
 p[0]=p[3]=initial;p[1]=p[4]=step;p[2]=p[5]=target;return 0;
}
