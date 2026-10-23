// Selected Shrek E788 / EBC0 routes. Optional carried-actor removal/detach
// callback for mode 6; dynamic-surface registration remains separate.
#include <cstdint>
#include <algorithm>
using Fetch=int(*)(uint32_t,int32_t*,int,void*);
using Consume=int(*)(void*);
extern "C" int s2_actor_contact_rects(const int32_t*,int,Fetch,void*,int32_t*,int);
extern "C" int s2_rect_overlap_xywh(const int32_t*,const int32_t*);
extern "C" void s2_rect_intersection_center(const int32_t*,const int32_t*,int32_t*);
extern "C" int s2_generic_activate(int32_t*,int32_t*,const int32_t*);
static int32_t add(int32_t a,int32_t b){return int32_t(uint32_t(a)+uint32_t(b));}
static int32_t sub(int32_t a,int32_t b){return int32_t(uint32_t(a)-uint32_t(b));}
// Original generic target slot 0x50: first hurt-box hit writes the point even
// when the later event is refused by the per-frame reaction guard.
static int hit(int32_t* target,const int32_t* rect,Fetch fetch,void* ctx){
 int32_t boxes[255*4];int count=s2_actor_contact_rects(target,0,fetch,ctx,boxes,255);if(count<0)return count;
 for(int i=0;i<count;i++)if(s2_rect_overlap_xywh(rect,boxes+i*4)){
  s2_rect_intersection_center(rect,boxes+i*4,target+28);return 1;
 }return 0;
}
static int deliver(int32_t* target,int32_t* vm,int32_t* reactions,const int32_t* rect,const int32_t* event,Fetch fetch,void* ctx,int32_t* diag){
 int h=hit(target,rect,fetch,ctx);if(h<0)return h;diag[0]=h;if(h){int a=s2_generic_activate(vm,reactions,event);if(a<0)return a;diag[1]=a;}return 0;
}
// Source/target use the generic 80-word pose ABI. Extra[8]: logical state,
// opaque mode (+258), held buttons, carried actor ID (zero = none), foot event
// class/id/payload (+21C), reserved. dy is the original +18C movement delta,
// supplied separately because the 40-word locomotion harness has another ABI.
// diag[8] is hit/activation for base, left strip, right strip, falling strip.
static int pair(int32_t* source,int32_t* extra,int32_t dy,uint32_t targetId,int targetCategory,int32_t* target,int32_t* vm,int32_t* reactions,Fetch fetch,void* ctx,int32_t* diag,Consume consume,int32_t* consumeDiag,bool dynamicResolved=false){
 if(!source||!extra||!targetId||!target||!vm||!reactions||!fetch||!diag)return -1;
 if(((source[40]&4)&&!dynamicResolved)||(extra[1]==6&&targetCategory==3&&!consume))return -4;
 std::fill(diag,diag+8,0);
 if(consumeDiag){consumeDiag[0]=0;consumeDiag[1]=0;}
 if(source[42]&&!(source[40]&16)){
  int32_t attacks[255*4];int count=s2_actor_contact_rects(source,1,fetch,ctx,attacks,255);if(count<0)return count;
  for(int i=0;i<count;i++){
   int h=hit(target,attacks+i*4,fetch,ctx);if(h<0)return h;if(!h)continue;diag[0]=1;
   // EBC0: state 8 refuses another capture while already carrying an actor.
   if(extra[0]!=8||!extra[3]){
    source[43]=target[0]<source[0]?2:1;int32_t event[3]={source[41],source[42],source[43]};
    int a=s2_generic_activate(vm,reactions,event);if(a<0)return a;diag[1]=a;
    if(a){source[40]|=16;if(extra[0]==8)extra[3]=int32_t(targetId);}
   }break;
  }
 }
 const int32_t width=(source[30]&255)*256,height=(source[31]&255)*256;
 const int32_t left=sub(source[0],width/2),top=sub(source[1],height/2);
 if(!(source[40]&16)&&targetCategory==3){
  if(extra[1]==6){
   int32_t rect[4]={sub(left,512),top,add(width,1024),height},event[3]={0,15,0},d[2]={0,0};
   int c=deliver(target,vm,reactions,rect,event,fetch,ctx,d);if(consumeDiag)std::copy_n(d,2,consumeDiag);if(c)return c;
   if(d[1]){c=consume(ctx);if(c)return c;}
  }
  if(extra[2]&32){int32_t rect[4]={sub(left,1024),top,1024,height},event[3]={0,6,2};int c=deliver(target,vm,reactions,rect,event,fetch,ctx,diag+2);if(c)return c;}
  // Both buttons are processed in original left-then-right order.
  if(extra[2]&16){int32_t rect[4]={add(left,width),top,1024,height},event[3]={0,6,1};int c=deliver(target,vm,reactions,rect,event,fetch,ctx,diag+4);if(c)return c;}
 }
 // This route runs independently of the base success flag and target category.
 if(dy>0&&extra[5]){int32_t rect[4]={left,sub(add(top,height),dy),width,dy};return deliver(target,vm,reactions,rect,extra+4,fetch,ctx,diag+6);}
 return 0;
}
// Stage-15 ABI keeps refusing the mode-6 route without an ownership backend.
extern "C" int s2_shrek_contact_pair(int32_t* source,int32_t* extra,int32_t dy,uint32_t targetId,int targetCategory,int32_t* target,int32_t* vm,int32_t* reactions,Fetch fetch,void* ctx,int32_t* diag){
 return pair(source,extra,dy,targetId,targetCategory,target,vm,reactions,fetch,ctx,diag,nullptr,nullptr);
}
// Consume must mark the CURRENT carried actor (not the collision target) for
// removal, update its scene bitmap, then perform DC5C detach. Stable lifetimes
// are required throughout callbacks. consumeDiag[2]: expanded hit/activation.
extern "C" int s2_shrek_contact_pair_carry(int32_t* source,int32_t* extra,int32_t dy,uint32_t targetId,int targetCategory,int32_t* target,int32_t* vm,int32_t* reactions,Fetch fetch,void* ctx,int32_t* diag,Consume consume,int32_t* consumeDiag){
 if(!consumeDiag)return -1;return pair(source,extra,dy,targetId,targetCategory,target,vm,reactions,fetch,ctx,diag,consume,consumeDiag);
}

// Owner has already collected and supplied dynamic surfaces to the player frame.
extern "C" int s2_shrek_contact_pair_resolved_dynamic(int32_t* source,int32_t* extra,int32_t dy,uint32_t targetId,int category,int32_t* target,int32_t* vm,int32_t* reactions,Fetch fetch,void* ctx,int32_t* diag){return pair(source,extra,dy,targetId,category,target,vm,reactions,fetch,ctx,diag,nullptr,nullptr,true);}

extern "C" int s2_shrek_contact_pair_resolved_carry(int32_t* source,int32_t* extra,int32_t dy,uint32_t id,int category,int32_t* target,int32_t* vm,int32_t* reactions,Fetch fetch,void* ctx,int32_t* diag,Consume consume){int32_t consumed[2];return pair(source,extra,dy,id,category,target,vm,reactions,fetch,ctx,diag,consume,consumed,true);}
