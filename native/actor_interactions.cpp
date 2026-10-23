// Original overlap 0x07E0, intersection center 0x0708, box transform 0x18460,
// and selected generic slot-0x48 / slot-0x60 / slot-0x58 interaction chain.
#include <cstdint>
#include <algorithm>
using Fetch=int(*)(uint32_t,int32_t*,int,void*);
extern "C" int s2_generic_activate(int32_t*,int32_t*,const int32_t*);
static int32_t add(int32_t a,int32_t b){return int32_t(uint32_t(a)+uint32_t(b));}
static int32_t sub(int32_t a,int32_t b){return int32_t(uint32_t(a)-uint32_t(b));}
extern "C" int s2_rect_overlap_xywh(const int32_t* a,const int32_t* b){
 if(!a||!b)return -1;return a[0]<add(b[0],b[2])&&b[0]<add(a[0],a[2])&&a[1]<add(b[1],b[3])&&b[1]<add(a[1],a[3]);
}
extern "C" void s2_rect_intersection_center(const int32_t* a,const int32_t* b,int32_t* p){
 if(!a||!b||!p)return;p[0]=add(std::max(a[0],b[0]),std::min(add(a[0],a[2]),add(b[0],b[2])))/2;p[1]=add(std::max(a[1],b[1]),std::min(add(a[1],a[3]),add(b[1],b[3])))/2;
}
extern "C" int s2_actor_box_q8(const int32_t* actor,const int32_t* box,int32_t* out){
 if(!actor||!box||!out)return -1;
 int32_t offsetX=add(int32_t(uint32_t(int16_t(actor[26]))<<8),(actor[30]&255)*128),offsetY=add(int32_t(uint32_t(int16_t(actor[27]))<<8),(actor[31]&255)*128);
 out[0]=sub(add(actor[0],int32_t(uint32_t(int16_t(box[0]))<<8)),offsetX);out[1]=sub(add(actor[1],int32_t(uint32_t(int16_t(box[1]))<<8)),offsetY);out[2]=(box[2]&255)*256;out[3]=(box[3]&255)*256;
 if(actor[18]&255)out[0]=sub(add(actor[0],actor[0]),add(out[0],out[2]));if(actor[38]&255)out[1]=sub(add(actor[1],actor[1]),add(out[1],out[3]));return 0;
}
extern "C" int s2_actor_current_frame(const int32_t* actor,Fetch fetch,void* ctx,int32_t* frame){
 if(!actor||!fetch||!frame)return -1;int32_t animation[6],root[2],sequence;
 if(!fetch(uint32_t(actor[47]),animation,6,ctx)||actor[22]<0||actor[22]>=int((uint32_t(animation[5])>>8)&255))return -2;
 if(!fetch(uint32_t(animation[0]),root,2,ctx)||!fetch(uint32_t(animation[1])+uint32_t(actor[22])*2u,&sequence,1,ctx))return -2;
 return fetch(uint32_t(root[1])+(uint32_t(sequence)&65535)*44u,frame,11,ctx)?0:-2;
}
// which 0: defender/hurt boxes (metadata byte 0, frame+0x18),
// which 1: attacker/interaction boxes (byte 1, frame+0x1C).
extern "C" int s2_actor_contact_rects(const int32_t* actor,int which,Fetch fetch,void* ctx,int32_t* out,int capacity){
 if(!actor||!fetch||(which!=0&&which!=1)||capacity<0||(!out&&capacity))return -1;
 if(!(actor[40]&8)){
  if(capacity){out[0]=sub(actor[0],(actor[30]&255)*128);out[1]=sub(actor[1],(actor[31]&255)*128);out[2]=(actor[30]&255)*256;out[3]=(actor[31]&255)*256;}return 1;
 }
 int32_t frame[11],counts;int error=s2_actor_current_frame(actor,fetch,ctx,frame);if(error)return error;
 if(!fetch(uint32_t(frame[5]),&counts,1,ctx))return -2;
 int count=(uint32_t(counts)>>(which*8))&255;
 for(int i=0;i<std::min(count,capacity);i++){
  int32_t packed[2],box[4];if(!fetch(uint32_t(frame[6+which])+uint32_t(i)*8u,packed,2,ctx))return -2;
  box[0]=int16_t(uint32_t(packed[0]));box[1]=int16_t(uint32_t(packed[0])>>16);box[2]=uint32_t(packed[1])&255;box[3]=(uint32_t(packed[1])>>8)&255;s2_actor_box_q8(actor,box,out+i*4);
 }return count;
}
// Stable candidate pair only: no world broadphase or dynamic-surface append.
// Diagnostics[4]: overlap, activation, last intersection-center X/Y Q8.
extern "C" int s2_generic_contact_pair(int32_t* source,int32_t* target,int32_t* targetVm,int32_t* targetReactions,Fetch fetch,void* ctx,int32_t* diagnostics){
 if(!source||!target||!targetVm||!targetReactions||!fetch||!diagnostics)return -1;
 std::fill(diagnostics,diagnostics+4,0);if(source[40]&4)return -4;
 if(!source[42]||(source[40]&16))return 0;
 int32_t attacks[255*4],defenses[255*4];int na=s2_actor_contact_rects(source,1,fetch,ctx,attacks,255);if(na<0)return na;if(!na)return 0;int nd=s2_actor_contact_rects(target,0,fetch,ctx,defenses,255);if(nd<0)return nd;
 for(int a=0;a<na;a++)for(int d=0;d<nd;d++)if(s2_rect_overlap_xywh(attacks+a*4,defenses+d*4)){
  diagnostics[0]=1;s2_rect_intersection_center(attacks+a*4,defenses+d*4,diagnostics+2);target[28]=diagnostics[2];target[29]=diagnostics[3];source[43]=target[0]<source[0]?2:1;
  int32_t event[3]={source[41],source[42],source[43]};int activated=s2_generic_activate(targetVm,targetReactions,event);if(activated<0)return activated;diagnostics[1]=activated;if(activated)source[40]|=16;return 0;
 }return 0;
}
// Generic outgoing event to a receiver override (e.g. Shrek E3A0). Target uses
// the recovered base hit-query geometry. Dynamic append is absent only when
// the target's +15D surface flags bits0..2 are all clear.
using Receiver=int(*)(const int32_t*,void*);
extern "C" int s2_generic_contact_pair_receiver(int32_t* source,int32_t* target,Fetch fetch,Receiver receiver,void* ctx,int32_t* diag){
 if(!source||!target||!fetch||!receiver||!diag)return -1;
 if((source[40]&4)&&(target[39]&7))return -4;std::fill(diag,diag+4,0);
 if(!source[42]||(source[40]&16))return 0;
 int32_t attacks[255*4],defenses[255*4];int na=s2_actor_contact_rects(source,1,fetch,ctx,attacks,255);if(na<0)return na;if(!na)return 0;int nd=s2_actor_contact_rects(target,0,fetch,ctx,defenses,255);if(nd<0)return nd;
 for(int a=0;a<na;a++)for(int d=0;d<nd;d++)if(s2_rect_overlap_xywh(attacks+a*4,defenses+d*4)){
  diag[0]=1;s2_rect_intersection_center(attacks+a*4,defenses+d*4,diag+2);target[28]=diag[2];target[29]=diag[3];source[43]=target[0]<source[0]?2:1;int32_t event[3]={source[41],source[42],source[43]};int result=receiver(event,ctx);if(result<0)return result;diag[1]=result&255;if(diag[1])source[40]|=16;return 0;
 }return 0;
}
