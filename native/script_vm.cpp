// Original 0x08012F9C / 0x08013028. Addresses remain 32-bit resource IDs.
#include <cstdint>
using Fetch=int(*)(uint32_t,int32_t*,int,void*);
using Query=void(*)(int,int32_t,int32_t,int32_t,int32_t*,void*);
using Effect=void(*)(int,const int32_t*,void*);
using Random=int32_t(*)(void*);
extern "C" int s2_vm_call(uint32_t,int32_t*);
static int32_t wrap_add(int32_t a,int32_t b){return int32_t(uint32_t(a)+uint32_t(b));}
static int32_t* frame(int32_t* s,int i){return s+8+i*5;}
// 64 words: counter, deadline, depth, result, reserved[4], ten five-word frames.
// Frame: script address, index, last predicate byte, name address, interrupt predicate.
extern "C" void s2_vm_push(uint32_t program,int32_t* s){
 if(!s||s[2]<-1||s[2]>8)return;s[2]++;auto* f=frame(s,s[2]);f[0]=int32_t(program);f[1]=0;f[2]=0;f[3]=0x0802547c;f[4]=0;
}
extern "C" void s2_vm_start(uint32_t program,int32_t* s){if(!s)return;s[1]=0;s[2]=-1;s2_vm_push(program,s);}
extern "C" int s2_vm_compare(int32_t value,int mode,int32_t rhs){
 switch(mode){case 0:return value>rhs;case 1:return value<rhs;case 2:return value==rhs;case 3:return value!=rhs;case 4:return (uint32_t(value)&uint32_t(rhs))==uint32_t(rhs);default:return 0;}
}
static int predicate(uint32_t address,int32_t* s,int32_t tick,Fetch fetch,Query query,Random random,void* context){
 int32_t p[5];if(!fetch(address,p,5,context))return -2;int32_t value=int32_t(0xdeadbeefu);if(p[0]==5){if(p[1]==17)value=s[1]>tick?int32_t(uint32_t(s[1])-uint32_t(tick)):0;else if(p[1]==18)value=random?random(context)%256:0;else return -4;}else if(query)query(0,p[0],p[1],p[2],&value,context);s[3]=value;int result=s2_vm_compare(value,p[3],p[4]);if(s[2]>=0)frame(s,s[2])[2]=result;return result;
}
extern "C" int s2_vm_step(int32_t* s,int32_t tick,Fetch fetch,Query query,Effect effect,Random random,void* context,int budget){
 if(!s||!fetch||s[2]<-1||s[2]>9||budget<1)return -1;
 for(int i=0;i<=s[2];i++){auto* f=frame(s,i);if(!f[4])continue;int p=predicate(uint32_t(f[4]),s,tick,fetch,query,random,context);if(p<0)return p;if(p){while(s[2]>=i)s[2]--;break;}}
 int executed=0;
 while(s[2]>=0){
  if(executed>=budget)return -3;auto* f=frame(s,s[2]);uint32_t address=uint32_t(f[0])+uint32_t(f[1])*12u;int32_t cmd[3];if(!fetch(address,cmd,3,context))return -2;f[1]=wrap_add(f[1],1);executed++;
  if(cmd[0]!=5){if(effect)effect(0,cmd,context);}
  else{
   int op=cmd[1];int32_t arg=cmd[2];int p;
   switch(op){
    case 0:if(effect)effect(1,cmd,context);break;
    case 1:f[3]=arg;break;
    case 2:s2_vm_call(uint32_t(arg),s);break;
    case 3:p=predicate(uint32_t(arg),s,tick,fetch,query,random,context);if(p<0)return p;if(!p)f[1]=wrap_add(f[1],1);break;
    case 4:if(f[2]&255)f[1]=wrap_add(f[1],1);break;
    case 5:f[1]=0;break;
    case 6:s[2]--;break;
    case 7:f[4]=arg;break;
    case 8:if(s[0]<arg)f[1]=wrap_add(f[1],-1);break;
    case 9:case 10:p=predicate(uint32_t(arg),s,tick,fetch,query,random,context);if(p<0)return p;if((op==9&&p)||(op==10&&!p))f[1]=wrap_add(f[1],-1);break;
    case 11:case 12:case 13:case 14:case 15:if(effect)effect(op,cmd,context);break;
    case 16:s[1]=wrap_add(tick,arg);break;
    case 17:s[3]=s[1]>tick?int32_t(uint32_t(s[1])-uint32_t(tick)):0;break;
    case 18:s[3]=random?random(context)%256:0;break;
    default:break;
   }
  }
  if(s[2]<0)break;f=frame(s,s[2]);uint32_t next=uint32_t(f[0])+uint32_t(f[1])*12u;
  if(next==address){s[0]=wrap_add(s[0],1);break;}s[0]=0;
 }return executed;
}
