// Original generic commands46/47 initiate global camera/screen effects.
// Delivery and removal remain owned by caller; no implicit world manager.
#include <cstdint>
#include <algorithm>
#include <cstddef>
using Fetch=int(*)(uint32_t,int32_t*,int,void*);
using Sink=int(*)(int,uint32_t,int32_t,void*);
extern "C" int s2_camera_effect_begin(int32_t* state5,const int32_t* parameters3){
 if(!state5||!parameters3)return -1;std::copy_n(parameters3,3,state5);state5[3]=0;state5[4]=1;return 0;
}
extern "C" int s2_screen_effect_begin(int32_t* state4,int32_t parameter){
 if(!state4)return -1;state4[0]=0;state4[1]=parameter;state4[2]=3;state4[3]=64;return 0;
}
extern "C" int s2_generic_world_message(int32_t* actor,int cls,int id,int32_t payload,Fetch fetch,Sink sink,void* ctx){
 if(!actor||!fetch||!sink)return -1;if(cls!=8)return -4;
 if(id==46){int32_t p[3];if(!fetch(uint32_t(payload),p,3,ctx))return -2;return sink(16,uint32_t(payload),0,ctx);}
 if(id==47)return sink(17,uint32_t(payload),0,ctx);
 if(id==11)return sink(19,0,0,ctx); // Owner must mark/remove current actor.
 // Enemy scripts delegate global ownership to the caller. These requests
 // alone do not enroll recipients or instantiate an actor in a scene.
 if(id==16){int32_t packet[2];if(!fetch(uint32_t(payload),packet,2,ctx))return -2;return sink(22,uint32_t(payload),0,ctx);}
 if(id==48){int32_t descriptor[5];if(!fetch(uint32_t(payload),descriptor,5,ctx))return -2;return sink(23,uint32_t(payload),0,ctx);}
 if(id==55)return sink(25,uint32_t(payload),0,ctx);
 if(id==49)return actor[79]?sink(24,uint32_t(actor[79]),0,ctx):0;
 return -4;
}
static int32_t add(int32_t a,int32_t b){return int32_t(uint32_t(a)+uint32_t(b));}
static int32_t sub(int32_t a,int32_t b){return int32_t(uint32_t(a)-uint32_t(b));}
// Camera tail0962: state5 amplitude,bitmask,decay,counter,axis.
// Return1 if the renderer position was set,0 if the original did not set it.
extern "C" int s2_camera_effect_step(int32_t* s,const int32_t* base,const int32_t* bounds,int32_t* out){
 if(!s||!base||!bounds||!out)return -1;int32_t x=base[0],y=base[1],amplitude=s[0];
 if(amplitude<=0){out[0]=x;out[1]=y;return 1;}
 int32_t offset=amplitude;
 if(!(uint32_t(s[1])&uint32_t(s[3]))){offset=int32_t(0u-uint32_t(amplitude));s[0]=sub(amplitude,s[2]);}
 s[3]=add(s[3],1);
 if(s[4]==1){if(x<add(bounds[0],s[0]))x=add(bounds[0],s[0]);if(x>sub(bounds[2],s[0]))x=sub(bounds[2],s[0]);out[0]=add(x,offset);out[1]=y;return 1;}
 if(s[4]==2){if(y<add(bounds[1],s[0]))y=add(bounds[1],s[0]);if(y>sub(bounds[3],s[0]))y=sub(bounds[3],s[0]);out[0]=x;out[1]=add(y,offset);return 1;}
 return 0;
}
// Screen state4: target,step,mode,current. Original1ADA0.
extern "C" int s2_screen_effect_step(int32_t* s){
 if(!s)return -1;if(s[2]<1||s[2]>3)return 0;
 if(s[3]<s[0]){s[3]=add(s[3],s[1]);if(s[3]>s[0])s[3]=s[0];}
 if(s[3]>s[0]){s[3]=sub(s[3],s[1]);if(s[3]<s[0])s[3]=s[0];}
 if(!s[3])s[2]=0;return 0;
}
// Mode3 of1ADFC, raw RGB555; bit15 and R/B pass through unchanged.
extern "C" int s2_screen_effect_rgb555(const int32_t* s,const uint16_t* input,uint16_t* output,size_t count){
 if(!s||(!input&&count)||(!output&&count)||count>1048576)return -1;if(s[2]!=0&&s[2]!=3)return -4;
 for(size_t i=0;i<count;i++){uint32_t c=input[i];if(s[2]==3){uint32_t g=(c>>5)&31;g+=((31-g)*uint32_t(s[3]))>>6;c=(c&0xfc1f)|(g<<5);}output[i]=uint16_t(c);}return 0;
}
// Renderer adapter: original palette channels are expanded as component*255/31.
extern "C" int s2_screen_effect_argb(const int32_t* s,uint32_t* pixels,size_t count){
 if(!s||(!pixels&&count)||count>1048576)return -1;if(s[2]==0)return 0;if(s[2]!=3||s[3]<0||s[3]>64)return -4;
 for(size_t i=0;i<count;i++){uint32_t c=pixels[i],g=(((c>>8)&255)*31+127)/255;g+=((31-g)*uint32_t(s[3]))>>6;pixels[i]=(c&0xffff00ff)|(((g&31)*255/31)<<8);}return 0;
}

// Original0824 follow core090A..0960, signed Q8, maximum5px X/7px Y.
extern "C" int s2_camera_follow_step(int32_t* current,const int32_t* target){
 if(!current||!target)return -1;
 for(int i=0;i<2;i++){int32_t d=int32_t(uint32_t(target[i])-uint32_t(current[i]));int limit=i?1792:1280;current[i]=int32_t(uint32_t(current[i])+uint32_t(std::clamp(d,-limit,limit)));}return 0;
}
