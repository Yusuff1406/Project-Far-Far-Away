// Original 0x13B8C registration/class-9 routes and activation 0x13A54.
#include <cstdint>
#include <algorithm>
using Fetch=int(*)(uint32_t,int32_t*,int,void*);
using Registry=void(*)(int,void*);
extern "C" void s2_vm_push(uint32_t,int32_t*);
extern "C" int s2_generic_message(int32_t*,int,int,int32_t,int32_t,Fetch,void*);
// Shared external/internal opcode 2 behavior, including full-stack refusal.
extern "C" int s2_vm_call(uint32_t program,int32_t* vm){
 if(!vm||vm[2]<-1||vm[2]>9)return -1;s2_vm_push(program,vm);vm[9+vm[2]*5]=0;return 0;
}
// 72 words: counts[2], activation byte, last payload/class, tag, reserved[2],
// 16 contact pairs at word 8, 8 safe broadcast pairs at word 40; tail reserved.
extern "C" void s2_reactions_init(int32_t tag,int32_t* r){if(!r)return;std::fill(r,r+72,0);r[5]=tag;}
static bool valid(const int32_t* r){return r&&r[0]>=0&&r[0]<=16&&r[1]>=0&&r[1]<=8;}
static int remove(int32_t* r,int which,int id,Registry registry,void* context){
 int32_t* list=r+(which?40:8);int n=r[which];
 for(int i=0;i<n;i++)if(list[i*2]==id){r[which]=--n;list[i*2]=list[n*2];list[i*2+1]=list[n*2+1];if(which&&!n)registry(0,context);return 1;}return 0;
}
extern "C" int s2_generic_event(int32_t* actor,int32_t* vm,int32_t* r,const int32_t* event,int32_t tick,Fetch fetch,Registry registry,void* context){
 if(!actor||!vm||!event||!fetch||!valid(r)||vm[2]<-1||vm[2]>9)return -1;
 int cls=event[0],id=event[1];int32_t arg=event[2];
 if(cls==9){
  if(arg&&arg!=r[5])return 0;
  for(int i=0;i<r[1];i++)if(r[40+i*2]==id)return s2_vm_call(uint32_t(r[41+i*2]),vm);return 0;
 }
 if(cls!=8)return -4;
 if(id>=12&&id<=15){
  int which=id>=14;if(which&&!registry)return -1;
  if(id==13||id==15){remove(r,which,arg,registry,context);return 0;}
  int32_t pair[2];if(!fetch(uint32_t(arg),pair,2,context))return -2;
  if(which&&r[1]==8){bool match=false;for(int i=0;i<8;i++)if(r[40+i*2]==pair[0])match=true;if(!match)return -4;}
  remove(r,which,pair[0],registry,context);int n=r[which];if(n==16)return 0;
  if(which&&!n)registry(1,context);int32_t* p=r+(which?40:8)+n*2;p[0]=pair[0];p[1]=pair[1];r[which]=n+1;return 0;
 }
 return s2_generic_message(actor,cls,id,arg,tick,fetch,context);
}
extern "C" int s2_generic_activate(int32_t* vm,int32_t* r,const int32_t* event){
 if(!vm||!event||!valid(r)||vm[2]<-1||vm[2]>9)return -1;
 if(r[2]&255)return 0;
 for(int i=0;i<r[0];i++)if(r[8+i*2]==event[1]){
  r[3]=event[2];r[4]=event[0];int e=s2_vm_call(uint32_t(r[9+i*2]),vm);if(e)return e;r[2]=1;r[3]=event[2];return 1;
 }return 0;
}
extern "C" void s2_generic_reaction_frame_end(int32_t* r){if(r)r[2]=0;}
