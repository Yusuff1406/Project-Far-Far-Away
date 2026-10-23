// Recovered contact-state dispatch and dynamic-surface construction.
#include <cstdint>
static int32_t add(int32_t a,int32_t b){return int32_t(uint32_t(a)+uint32_t(b));}
static int32_t sub(int32_t a,int32_t b){return int32_t(uint32_t(a)-uint32_t(b));}
// 0x0800EFE4: ceiling changes logical 2/3 to 4 before the floor check.
extern "C" int s2_contact_actions(int state,const int32_t* stat,const int32_t* dyn,int32_t* actions){
 if(!stat||!dyn||!actions)return -1;int n=0;
 if((stat[3]||dyn[3])&&state>=2&&state<=3){actions[n++]=0x1d0;state=4;}
 if((stat[0]||dyn[0])&&state>=2&&state<=4)actions[n++]=0x178;
 return n;
}
// 0x0800403C: preserve previous bottom when grounded and body height changes.
extern "C" void s2_preserve_bottom(int groundMode,const int32_t* previous,int height,int32_t* position){
 if(previous&&position&&groundMode==3&&previous[3]!=height*256)position[1]=sub(add(previous[1],previous[3]),height*128);
}
// 0x08004CE4 normalized output: each segment has 9 words:
// x1,y1,x2,y2,type,auxPresent,deltaXQ8,deltaYQ8,auxFlag.
// Existing count limits appends to 16. Emission order top,left,right,bottom.
extern "C" int s2_dynamic_surfaces(const int32_t* position,int width,int height,int32_t* flags,const int32_t* delta,int existing,int32_t* out){
 if(!position||!flags||!delta||!out||width<0||width>255||height<0||height>255||existing<0||existing>16)return -1;
 *flags=(*flags&255)|8;int f=*flags,n=0;
 int32_t x1=sub(position[0],width*128)>>8,y1=sub(position[1],height*128)>>8;
 int32_t x2=add(sub(position[0],width*128),width*256)>>8,y2=add(sub(position[1],height*128),height*256)>>8;
 auto emit=[&](int32_t a,int32_t b,int32_t c,int32_t d,int kind,int aux){
  if(existing+n>=16)return;int32_t* s=out+n*9;s[0]=a;s[1]=b;s[2]=c;s[3]=d;s[4]=kind;s[5]=aux;s[6]=aux?delta[0]:0;s[7]=aux?delta[1]:0;s[8]=aux?((f>>4)&1):0;n++;
 };
 if(f&1)emit(x1,y1,x2,y1,3,1);
 if(f&2){emit(x1,y1,x1,y2,2,0);emit(x2,y1,x2,y2,1,0);}
 if(f&4)emit(x1,y2,x2,y2,5,0);
 return n;
}
// Drawing anchor from body metadata (0x08018328, before camera/zoom).
extern "C" void s2_actor_anchor_q8(const int32_t* bounds,const int32_t* pos,int flipX,int flipY,int32_t* out){
 if(!bounds||!pos||!out)return;int32_t x=add(int32_t(uint32_t(bounds[0])<<8),bounds[2]*128),y=add(int32_t(uint32_t(bounds[1])<<8),bounds[3]*128);
 out[0]=flipX?add(pos[0],x):sub(pos[0],x);out[1]=flipY?add(pos[1],y):sub(pos[1],y);
}
extern "C" void s2_motion_step(int32_t*,int32_t*);
extern "C" int s2_resolve_static_file(const char*,const int32_t*,int32_t*,int,int,int32_t*);
// Static-world part of 0x08003D80/0x08003FB0; external virtual callbacks follow.
extern "C" int s2_actor_move_file(const char* path,int32_t* p,int32_t* pos,int32_t* previousRect,int32_t* previousPos,int width,int height,int flags,int32_t* counts,int32_t* delta){
 if(!path||!p||!pos||!previousRect||!previousPos||!counts||!delta||width<0||width>255||height<0||height>255)return -1;
 s2_motion_step(p,pos);for(int i=0;i<4;i++)counts[i]=0;
 if(flags&2){int c=s2_resolve_static_file(path,previousRect,pos,width,height,counts);if(c)return c;}
 previousRect[0]=sub(pos[0],width*128);previousRect[1]=sub(pos[1],height*128);previousRect[2]=width*256;previousRect[3]=height*256;
 delta[0]=sub(pos[0],previousPos[0]);delta[1]=sub(pos[1],previousPos[1]);previousPos[0]=pos[0];previousPos[1]=pos[1];return counts[0]?3:0;
}
// 0x08016960, with animation pointer represented separately by the caller.
extern "C" void s2_animation_restart(int rate,int count,int direction,int32_t tick,int32_t* state){
 if(!state||rate<0||rate>255||count<1||count>255)return;state[0]=0;state[1]=direction;
 if(direction==0||direction==2)state[2]=0;else if(direction==1)state[2]=count-1;
 state[3]=add(tick,rate+1);
}

// Original1730/17C8 special surface actors23/24; includes source flip and16-row cap.
using SlopeFetch=int(*)(uint32_t,int32_t*,int,void*);
extern "C" int s2_generic_runtime_init(const int32_t*,int,uint32_t,int32_t,SlopeFetch,void*,int32_t*);
extern "C" int s2_generic_message(int32_t*,int,int,int32_t,int32_t,SlopeFetch,void*);
extern "C" void s2_vm_start(uint32_t,int32_t*);
extern "C" int s2_slope_runtime_init(const int32_t* anchor,int flips,uint32_t definition,int32_t tick,SlopeFetch fetch,void* ctx,int32_t* s,int32_t* vm){
 int32_t base[2],config[2];if(!fetch||!s||!vm||!fetch(0x08051c34,base,2,ctx)||!fetch(definition,config,2,ctx))return -2;
 int e=s2_generic_runtime_init(anchor,flips,uint32_t(base[0]),tick,fetch,ctx,s);if(e)return e;
 int32_t old[2]={s[48],s[49]};e=s2_generic_message(s,8,4,config[0],tick,fetch,ctx);if(e)return e;s[48]=old[0];s[49]=old[1];s[22]=s[77]-1;s[39]=(s[39]&~3)|(config[0]==config[1]?2:1)|8;s2_vm_start(uint32_t(base[1]),vm);return 0;
}
extern "C" int s2_slope_surfaces(const int32_t* s,int existing,int32_t* flags,int32_t* out){
 if(!s||!flags||!out||existing<0||existing>16||s[30]<0||s[30]>255||s[31]<0||s[31]>255)return -1;
 *flags=(*flags&255)|8;int f=*flags,n=0;
 int32_t left=sub(s[0],s[30]*128)>>8,top=sub(s[1],s[31]*128)>>8,right=add(sub(s[0],s[30]*128),s[30]*256)>>8,bottom=add(sub(s[1],s[31]*128),s[31]*256)>>8;
 auto emit=[&](int x1,int y1,int x2,int y2,int type,int aux){if(existing+n>=16)return;int32_t* p=out+n++*9;p[0]=x1;p[1]=y1;p[2]=x2;p[3]=y2;p[4]=type;p[5]=aux;p[6]=aux?s[60]:0;p[7]=aux?s[61]:0;p[8]=aux?((f>>4)&1):0;};
 if(f&2){if(s[18])left=right-s[31];else right=left+s[31];top=bottom-s[30];emit(left,top,right,top,3,1);emit(left,top,left,bottom,2,0);emit(right,top,right,bottom,1,0);}
 else{emit(left,top,right,top,3,1);emit(left,bottom,right,bottom,5,0);}return n;
}
