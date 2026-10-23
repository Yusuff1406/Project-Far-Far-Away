// Donkey source F25C event [3,2,0] and shared terminal entries.
#include <cstdint>
#include <algorithm>
using Fetch=int(*)(uint32_t,int32_t*,int,void*);
extern "C" int s2_generic_message(int32_t*,int,int,int32_t,int32_t,Fetch,void*);
extern "C" int s2_apply_axis_triple(int32_t*,const int32_t*,int,int);
static int row(uint32_t table,int id,int32_t* out,uint32_t& address,Fetch f,void* ctx){for(int i=0;i<40;i++){address=table+i*40;if(!f(address,out,10,ctx))return -2;if(out[0]==id)return 0;if(out[0]==999)break;}return -2;}
static int select(uint32_t table,int id,int32_t* s,int32_t* b,int32_t tick,Fetch f,void* ctx){int32_t r[10];uint32_t address;int e=row(table,id,r,address,f,ctx);if(e)return e;e=s2_generic_message(s,8,4,r[1],tick,f,ctx);if(e)return e;b[0]=int32_t(address);b[1]=r[9];return 0;}
extern "C" int s2_character_ground_attack(uint32_t table,int32_t* s,int32_t* e,int32_t* b,int32_t tick,Fetch f,void* ctx){if(!s||!e||!b||!f)return -1;s[19]=int32_t(uint32_t(s[19])+1u);bool gingy=table==0x0804be94,human=table==0x0804bb4c,puss=table==0x0804c4fc;int32_t event[3]={gingy?1:(human||puss)?2:3,gingy?13:human?5:puss?3:2,0};std::copy_n(event,3,s+41);int32_t r[10];uint32_t address;int result=row(table,1,r,address,f,ctx);if(result)return result;s2_apply_axis_triple(s+2,r+2,0,0);result=select(table,gingy?((b[4]&64)?9:8):(s[19]&1)?9:8,s,b,tick,f,ctx);if(result)return result;if(gingy)b[5]=0;e[0]=7;return 0;}
extern "C" int s2_character_terminal_enter(uint32_t table,int state,int32_t* s,int32_t* e,int32_t* b,int32_t tick,Fetch f,void* ctx){if(!s||!e||!b||!f||(state!=12&&state!=13&&state!=14&&state!=15))return -1;int32_t r[10];uint32_t address;int result=row(table,1,r,address,f,ctx);if(result)return result;s2_apply_axis_triple(s+2,r+2,0,0);if(state==12){s2_apply_axis_triple(s+2,r+5,1,0);const int32_t idle[3]={1,7,0};std::copy_n(idle,3,s+41);b[2]=tick;}
 result=select(table,state==12?14:state==13?15:state==15?18:17,s,b,tick,f,ctx);if(result)return result;if(state==14||state==15){result=row(table,1,r,address,f,ctx);if(result)return result;s2_apply_axis_triple(s+2,r+5,1,0);b[0]=int32_t(address);}if(state==13){b[6]=0;e[3]=0;}e[0]=state;return 0;}

extern "C" int s2_donkey_ground_attack(int32_t* s,int32_t* e,int32_t* b,int32_t tick,Fetch f,void* ctx){return s2_character_ground_attack(0x0804c1b4,s,e,b,tick,f,ctx);}
extern "C" int s2_donkey_terminal_enter(int state,int32_t* s,int32_t* e,int32_t* b,int32_t tick,Fetch f,void* ctx){return s2_character_terminal_enter(0x0804c1b4,state,s,e,b,tick,f,ctx);}
