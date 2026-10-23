// Original19024 dialogue lookup, script interpreter and selected UI messages.
#include <cstdint>
#include <algorithm>
using Fetch=int(*)(uint32_t,int32_t*,int,void*);
using Query=void(*)(int,int32_t,int32_t,int32_t,int32_t*,void*);
using Effect=void(*)(int,const int32_t*,void*);
using Random=int32_t(*)(void*);
extern "C" void s2_vm_start(uint32_t,int32_t*);
extern "C" int s2_vm_step(int32_t*,int32_t,Fetch,Query,Effect,Random,void*,int);
extern "C" int s2_dialogue_lookup(int32_t id,Fetch fetch,void* ctx,uint32_t* out){
 if(!fetch||!out)return -1;*out=0x0802558c;
 for(int i=0;i<=90;i++){int32_t row[2];if(!fetch(0x080255c8+uint32_t(i)*8,row,2,ctx))return -2;if(row[0]==id){*out=uint32_t(row[1]);break;}}return 0;
}
// 80 words: VM64; active,portrait,text resource,serial,text done,input,error,
// script71,finish-text requests72, bonus-index-plus-one request73; presentation74..77, owning dialogue tag78; portrait-hidden79.
extern "C" int s2_dialogue_start(uint32_t script,int32_t* s){if(!s||!script)return -1;std::fill_n(s,80,0);s[64]=1;s[71]=int32_t(script);s2_vm_start(script,s);return 0;}
struct DialogueContext{int32_t* s;Fetch fetch;void* ctx;};
static int get(uint32_t p,int32_t* out,int n,void* v){auto& c=*static_cast<DialogueContext*>(v);return c.fetch(p,out,n,c.ctx);}
static void query(int,int32_t cls,int32_t id,int32_t,int32_t* out,void* v){auto& c=*static_cast<DialogueContext*>(v);if(cls==4&&id==1)*out=c.s[69];else if(cls==7&&id==5)*out=c.s[68];else c.s[70]=-4;}
static void effect(int kind,const int32_t* cmd,void* v){auto& c=*static_cast<DialogueContext*>(v);auto* s=c.s;if(s[70])return;if(kind==1){int32_t packet[3];if(!c.fetch(uint32_t(cmd[2]),packet,3,c.ctx)){s[70]=-2;return;}if(packet[0]==0&&packet[1]==13&&packet[2]>=0&&packet[2]<=4)s[73]=packet[2]+1;else s[70]=-4;return;}if(kind){s[70]=-4;return;}
 if(cmd[0]==10&&(cmd[1]==0||cmd[1]==1)){if(!cmd[1])s[65]=cmd[2];s[79]=cmd[1];}
 else if(cmd[0]==7&&cmd[1]==2){s[66]=cmd[2];s[67]++;s[68]=0;}
 else if(cmd[0]==7&&cmd[1]==3)s[72]++;
 else s[70]=-4;
}
extern "C" int s2_dialogue_step(int32_t* s,int32_t tick,int pressed,int textDone,Fetch fetch,void* ctx){
 if(!s||!fetch||pressed<0||pressed>1023)return -1;if(!s[64])return 0;s[68]=textDone!=0;s[69]=pressed;s[70]=0;DialogueContext c{s,fetch,ctx};int e=s2_vm_step(s,tick,get,query,effect,nullptr,&c,4096);if(e<0)return e;if(s[70])return s[70];if(s[2]<0)s[64]=0;return 0;
}

// Type151 ctor01688 and contact0159C: invisible64x128 one-shot dialogue zone.
// The source descriptor gives dimensions; anchor denotes the top-left corner.
extern "C" int s2_dialogue_trigger_init(const int32_t* xy,Fetch fetch,void* ctx,int32_t* s){
 if(!xy||!fetch||!s)return -1;int32_t d[5];if(!fetch(0x08024aa4,d,5,ctx))return -2;
 std::fill_n(s,80,0);s[30]=d[3]&255;s[31]=d[4]&255;
 s[0]=int32_t(uint32_t(xy[0])+uint32_t(s[30]*128));s[1]=int32_t(uint32_t(xy[1])+uint32_t(s[31]*128));return 0;
}
extern "C" int s2_rect_overlap_xywh(const int32_t*,const int32_t*);
extern "C" int s2_dialogue_trigger_contact(const int32_t* trigger,const int32_t* target,int category,int tag,Fetch fetch,void* ctx,int32_t* packet){
 if(!trigger||!target||!fetch||!packet)return -1;if(category||trigger[40]&1)return 0;
 int32_t boxes[8];const int32_t* actors[2]={target,trigger};
 for(int i=0;i<2;i++){const auto* a=actors[i];int w=(a[30]&255)*256,h=(a[31]&255)*256;boxes[i*4]=int32_t(uint32_t(a[0])-uint32_t(w/2));boxes[i*4+1]=int32_t(uint32_t(a[1])-uint32_t(h/2));boxes[i*4+2]=w;boxes[i*4+3]=h;}
 if(!s2_rect_overlap_xywh(boxes,boxes+4))return 0;uint32_t script;int e=s2_dialogue_lookup(tag,fetch,ctx,&script);if(e)return e;packet[0]=0;packet[1]=3;packet[2]=int32_t(script);return 1;
}
