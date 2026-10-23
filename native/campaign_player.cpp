// Source shared locomotion entries + Donkey CDD4/CD70. Static map traversal;
// world actors, combat delivery, hazards and chapter completion are separate.
#include "campaign_player.h"
#include <algorithm>
extern "C" int s2_generic_runtime_init(const int32_t*,int,uint32_t,int32_t,CampaignFetch,void*,int32_t*);
extern "C" int s2_generic_message(int32_t*,int,int,int32_t,int32_t,CampaignFetch,void*);
extern "C" int s2_shrek_locomotion_enter(int32_t*,int32_t*,int32_t*,int32_t*,int,int,int32_t,int32_t,uint32_t,const int32_t*,CampaignFetch,void*);
using Sink=int(*)(int,uint32_t,int32_t,void*);
extern "C" int s2_shrek_landing_enter(int32_t*,int32_t*,int32_t*,int,int32_t,uint32_t,uint32_t,CampaignFetch,Sink,void*);
extern "C" void s2_animation_step(int,int,int,int32_t,int32_t*);
extern "C" int s2_actor_move_file(const char*,int32_t*,int32_t*,int32_t*,int32_t*,int,int,int,int32_t*,int32_t*);
extern "C" int s2_contact_actions(int,const int32_t*,const int32_t*,int32_t*);
extern "C" int s2_player_decide(int,const int32_t*,int32_t*,int32_t*);
extern "C" int s2_horizontal_input_file(const char*,int,const int32_t*,int,int,int32_t*,const int32_t*,int32_t*);
extern "C" int s2_static_probe_q8(const char*,int,int32_t,int32_t,int32_t,int32_t);
extern "C" void s2_preserve_bottom(int,const int32_t*,int,int32_t*);
extern "C" int s2_apply_axis_triple(int32_t*,const int32_t*,int,int);
extern "C" uint32_t s2_campaign_player_table(int t){switch(t){case 3:return 0x0804b73c;case 4:return 0x0804c4fc;case 5:return 0x0804be94;case 6:return 0x0804c1b4;case 7:return 0x0804bb4c;default:return 0;}}
static int motion(uint32_t table,int id,int32_t* row,uint32_t& address,CampaignFetch f,void* ctx){for(int i=0;i<40;i++){address=table+i*40;if(!f(address,row,10,ctx))return -2;if(row[0]==id)return 0;if(row[0]==999)break;}return -2;}
static int mute(int,uint32_t,int32_t,void*){return 0;}
extern "C" int s2_campaign_locomotion_enter(int t,int action,int held,int32_t tick,int32_t* s,int32_t* e,int32_t* b,CampaignFetch f,void* ctx){int previous=e[0];int32_t status[8]={},event[3]={};uint32_t table=s2_campaign_player_table(t);
 if(action==0x1d8){s[42]=0;return 0;}
 if(action==0x178)return s2_shrek_landing_enter(s,e,b,held,tick,table,0x0804b708,f,mute,ctx);
 int result=s2_shrek_locomotion_enter(s,e,status,b,action,held,tick,tick,table,event,f,ctx);if(result)return result;
 if(t==4&&((action==0x150&&previous==0)||(action==0x158&&previous==1))){int id=action==0x150?25:26;int32_t row[10];uint32_t address;result=motion(table,id,row,address,f,ctx);if(result)return result;result=s2_generic_message(s,8,4,row[1],tick,f,ctx);if(result)return result;b[0]=int32_t(address);b[1]=row[9];e[0]=action==0x150?20:21;}return 0;
}
extern "C" int s2_campaign_player_init(int t,const int32_t* anchor,int flips,int32_t* s,int32_t* e,int32_t* b,CampaignFetch f,void* ctx){if(!s||!e||!b||!anchor||!f||!s2_campaign_player_table(t))return -1;int32_t row[10];uint32_t address;int v=motion(s2_campaign_player_table(t),1,row,address,f,ctx);if(v)return v;v=s2_generic_runtime_init(anchor,flips,uint32_t(row[1]),0,f,ctx,s);if(v)return v;std::fill_n(e,8,0);std::fill_n(b,8,0);s[40]=10;s[36]=s[0];s[37]=s[1];return s2_campaign_locomotion_enter(t,0x158,0,0,s,e,b,f,ctx);}
extern "C" int s2_donkey_air_enter(int32_t* s,int32_t* e,int32_t* b,int32_t tick,CampaignFetch f,void* ctx){if(!s||!e||!b||!f)return -1;int32_t row[10];uint32_t address;int v=motion(s2_campaign_player_table(6),20,row,address,f,ctx);if(v)return v;v=s2_generic_message(s,8,4,row[1],tick,f,ctx);if(v)return v;b[0]=int32_t(address);b[1]=row[9];e[0]=16;const int32_t event[3]={3,2,0};std::copy_n(event,3,s+41);return 0;}
extern "C" int s2_donkey_air_behavior(int32_t* s,int32_t* e,int32_t* b,int held,int32_t tick,CampaignFetch f,void* ctx){if(!s||!e||!b||!f||e[0]!=16)return -1;if(!(s[20]&255))return 0;int32_t thresholds[2];if(!f(0x0804b6ec,thresholds,2,ctx))return -2;
 // Preserve the original CD70 branch order and strict comparisons.
 if(s[11]>thresholds[0])return s2_campaign_locomotion_enter(6,0x168,held,tick,s,e,b,f,ctx);
 if(s[11]>thresholds[1])return s2_campaign_locomotion_enter(6,0x170,held,tick,s,e,b,f,ctx);return 0;
}
extern "C" int s2_puss_motion_finish(int32_t* s,int32_t* e,int32_t* b,int32_t tick,CampaignFetch f,void* ctx){if(!s||!e||!b||!f)return -1;if((e[0]!=20&&e[0]!=21)||!(s[20]&255))return 0;int id=e[0]==20?2:1;int32_t row[10];uint32_t address;int v=motion(s2_campaign_player_table(4),id,row,address,f,ctx);if(v)return v;v=s2_generic_message(s,8,4,row[1],tick,f,ctx);if(v)return v;b[0]=int32_t(address);b[1]=row[9];e[0]=id==2?1:0;return 0;}
extern "C" int s2_campaign_player_step(const char* path,int t,int32_t* s,int32_t* e,int32_t* b,int held,int32_t tick,CampaignFetch f,void* ctx){if(!path||!s||!e||!b||!f||!s2_campaign_player_table(t)||!((e[0]>=0&&e[0]<=5)||(t==6&&e[0]==16)||(t==4&&(e[0]==20||e[0]==21))))return -1;
 held&=t==6?51:49;int pressed=held&~b[4];s[24]=tick;s2_animation_step(s[76],s[77],s[78],tick,s+20);
 int ground=s2_actor_move_file(path,s+2,s,s+32,s+36,s[30],s[31],s[40],s+14,s+60);if(ground<0)return ground;s[62]=ground;
 int32_t actions[16],empty[4]={};int n=s2_contact_actions(e[0],s+14,empty,actions);if(n<0)return n;
 for(int i=0;i<n;i++){int v=s2_campaign_locomotion_enter(t,actions[i],held,tick,s,e,b,f,ctx);if(v)return v;}
 int v=0;
 if(e[0]==16)v=s2_donkey_air_behavior(s,e,b,held,tick,f,ctx);
 else{
  int w=s[30],h=s[31],left=s2_static_probe_q8(path,1,s[0]-w*128-256,s[1]-h*128,256,h*256),right=s2_static_probe_q8(path,2,s[0]+w*128,s[1]-h*128,256,h*256),ceiling=s2_static_probe_q8(path,5,s[0]-w*128,s[1]-h*128-256,w*256,h*256);if(left<0||right<0||ceiling<0)return -2;
  int32_t in[15]={held,pressed&~2,s[14]!=0,s[15]!=0,s[16]!=0,!left,!right,s[18],1,!ceiling,0,0,s[20],0,s[11]};
  if(t==6&&e[0]>=2&&e[0]<=4&&(pressed&2))v=s2_donkey_air_enter(s,e,b,tick,f,ctx);
  else{int behaviorState=t==4&&e[0]==20?1:t==4&&e[0]==21?0:e[0];n=s2_player_decide(behaviorState,in,actions,s+18);if(n<0)return n;for(int i=0;i<n;i++){if(actions[i]==0x10000)v=s2_horizontal_input_file(path,held,s,w,h,s+2,s+14,s+18);else v=s2_campaign_locomotion_enter(t,actions[i],held,tick,s,e,b,f,ctx);if(v)return v;}}
 }
 if(v)return v;if(t==4){v=s2_puss_motion_finish(s,e,b,tick,f,ctx);if(v)return v;}std::copy_n(s+72,2,s+26);std::copy_n(s+74,2,s+30);s2_preserve_bottom(ground,s+32,s[31],s);b[4]=held;return 0;
}
