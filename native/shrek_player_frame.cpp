#include "carry_policy.h"
// Selected Shrek frame: supplied dynamic surfaces, states0..5/7/8/16.
// World contacts, carry tail and object scheduling run separately.
#include <cstdint>
#include <algorithm>
using Fetch=int(*)(uint32_t,int32_t*,int,void*);
extern "C" int s2_generic_message(int32_t*,int,int,int32_t,int32_t,Fetch,void*);
using Sink=int(*)(int,uint32_t,int32_t,void*);
using Dispatch=int(*)(uint32_t,const int32_t*,void*);
extern "C" void s2_animation_step(int,int,int,int32_t,int32_t*);
extern "C" int s2_actor_move_file(const char*,int32_t*,int32_t*,int32_t*,int32_t*,int,int,int,int32_t*,int32_t*);
extern "C" int s2_contact_actions(int,const int32_t*,const int32_t*,int32_t*);
extern "C" int s2_static_probe_q8(const char*,int,int32_t,int32_t,int32_t,int32_t);
extern "C" int s2_player_decide(int,const int32_t*,int32_t*,int32_t*);
extern "C" int s2_horizontal_input_file(const char*,int,const int32_t*,int,int,int32_t*,const int32_t*,int32_t*);
extern "C" int s2_shrek_scene_attack_enter(int32_t*,int32_t*,int32_t*,int32_t,uint32_t,Fetch,void*);
extern "C" int s2_shrek_locomotion_enter(int32_t*,int32_t*,int32_t*,int32_t*,int,int,int32_t,int32_t,uint32_t,const int32_t*,Fetch,void*);
extern "C" int s2_shrek_grab_enter(int32_t*,int32_t*,int32_t*,int32_t,int32_t,uint32_t,const int32_t*,const int32_t*,Fetch,Dispatch,void*,int32_t*);
extern "C" int s2_shrek_landing_enter(int32_t*,int32_t*,int32_t*,int,int32_t,uint32_t,uint32_t,Fetch,Sink,void*);
extern "C" int s2_shrek_clear_contact_event(int32_t*);
extern "C" int s2_shrek_grab_behavior(int32_t*,int32_t*,int32_t*,int32_t*,int,int32_t,int32_t,uint32_t,const int32_t*,Fetch,void*);
extern "C" int s2_shrek_attack_behavior(int32_t*,int32_t*,int32_t*,int32_t*,int,int32_t,int32_t,uint32_t,const int32_t*,Fetch,void*);
extern "C" int s2_shrek_air_attack_behavior(int32_t*,int32_t*,int32_t*,int32_t*,int,int32_t,int32_t,uint32_t,const int32_t*,Fetch,Sink,void*);
extern "C" void s2_preserve_bottom(int,const int32_t*,int,int32_t*);
extern "C" int s2_actor_move_dynamic_file(const char*,int32_t*,int32_t*,int32_t*,int32_t*,int,int,const int32_t*,int,int32_t*,int32_t*,int32_t*);
extern "C" int s2_actor_probe_file(const char*,int,int32_t,int32_t,int32_t,int32_t,const int32_t*,int);
extern "C" int s2_horizontal_input_dynamic_file(const char*,int,const int32_t*,int,int,int32_t*,const int32_t*,int32_t*,const int32_t*,int);
extern "C" int s2_shrek_stomp_enter(int32_t*,int32_t*,int32_t*,int32_t,uint32_t,Fetch,void*);
extern "C" int s2_shrek_stomp_behavior(int32_t*,int32_t*,int32_t*,int32_t*,int,int32_t,int32_t,uint32_t,const int32_t*,Fetch,Sink,void*);
extern "C" int s2_shrek_stomp_audio(const int32_t*,const int32_t*,int32_t,Fetch,Sink,void*);
extern "C" int s2_shrek_lift_behavior(int32_t*,int32_t*,int32_t*,int32_t*,int,int,int,int,int32_t,int32_t,uint32_t,const int32_t*,Fetch,Sink,void*);
extern "C" int s2_shrek_hurt_behavior(int32_t*,int32_t*,int32_t*,int32_t*,int,int32_t,int32_t,uint32_t,const int32_t*,Fetch,void*);
static int32_t add(int32_t a,uint32_t b){return int32_t(uint32_t(a)+b);}
// Control3: inputActive, dropEligible, idleTimerExpired. Events9:
// actual mutable locomotion(+228), grab(+240), detach(+234) triples.
// Book[4] stores previous held buttons. This is not the full D484 ABI.
extern "C" int s2_apply_axis_triple(int32_t*,const int32_t*,int,int);
extern "C" int s2_donkey_ground_attack(int32_t*,int32_t*,int32_t*,int32_t,Fetch,void*);
extern "C" int s2_donkey_air_enter(int32_t*,int32_t*,int32_t*,int32_t,Fetch,void*);
extern "C" int s2_donkey_air_behavior(int32_t*,int32_t*,int32_t*,int,int32_t,Fetch,void*);
extern "C" int s2_character_ground_attack(uint32_t,int32_t*,int32_t*,int32_t*,int32_t,Fetch,void*);
extern "C" int s2_puss_wall_query_file(const char*,const int32_t*,int,const int32_t*,int);
extern "C" int s2_puss_air_enter(int32_t*,int32_t*,int32_t*,int32_t,Fetch,void*);
extern "C" int s2_puss_air_behavior(int32_t*,int32_t*,int32_t*,int32_t*,int,int,int32_t,const int32_t*,Fetch,void*);
extern "C" int s2_puss_locomotion_enter(int,int,int32_t,int32_t*,int32_t*,int32_t*,int32_t*,const int32_t*,Fetch,void*);
extern "C" int s2_puss_wall_enter(int32_t*,int32_t*,int32_t*,int32_t,Fetch,Sink,void*);
extern "C" int s2_puss_wall_jump(int32_t*,int32_t*,int32_t*,int32_t*,int,int32_t,const int32_t*,Fetch,void*);
extern "C" int s2_puss_motion_finish(int32_t*,int32_t*,int32_t*,int32_t,Fetch,void*);
extern "C" int s2_campaign_locomotion_enter(int,int,int,int32_t,int32_t*,int32_t*,int32_t*,Fetch,void*);
extern "C" int s2_actor_move_puss_file(const char*,int32_t*,const int32_t*,int,int32_t*,int);
extern "C" int s2_puss_rail_angle(int,int);
extern "C" int s2_puss_rail_enter(int32_t*,int32_t*,int32_t*,int,int,int32_t,Fetch,void*);
extern "C" int s2_puss_rail_behavior(int32_t*,int32_t*,int32_t*,int32_t*,int,int,int,int,int32_t,const int32_t*,Fetch,Sink,void*);
static int player_frame(const char* collision,int32_t* s,int32_t* extra,int32_t* status,int32_t* book,int held,int32_t worldTick,int32_t animationTick,const int32_t* control,const int32_t* events,uint32_t table,uint32_t threshold,Fetch fetch,Sink sink,Dispatch dispatch,void* ctx,const int32_t* surfaces,int surfaceCount,bool sceneShrek,bool donkey=false){
 if(surfaceCount<0||surfaceCount>16||(!surfaces&&surfaceCount))return -1;
 if(!collision||!s||!extra||!status||!book||!control||!events||!fetch)return -1;
 if(s[30]<1||s[30]>255||s[31]<1||s[31]>255||s[77]<1||s[77]>255||s[76]<0||s[76]>255)return -1;
 if(surfaceCount&&(s[40]&6)!=6)return -4;
 int32_t totalContacts[4]={};
 auto probe=[&](int type,int32_t x,int32_t y,int32_t w,int32_t h){return s2_actor_probe_file(collision,type,x,y,w,h,surfaces,surfaceCount);};
 bool puss=table==0x0804c4fc,gingy=table==0x0804be94,human=table==0x0804bb4c,shared=gingy||human;bool airJumpUsed=(uint32_t(book[4])&0x10000u)!=0;
 auto wallAllowed=[&](int direction){return s2_puss_wall_query_file(collision,s,direction,surfaces,surfaceCount);};
 int state=extra[0],pressed=held&~book[4];
 // Reject unsupported branches before advancing the frame.
 if(!((state>=0&&state<=5)||state==7||state==8||state==9||state==10||state==11||state==16||(puss&&state==18)||(sceneShrek&&(state==6||state==13||state==14||(state==15)||(state>=19&&state<=22)||(book[6]&&state>=16&&state<=18))))||s[54]||(s[40]&1))return -4;
 if((pressed&2)&&extra[3]&&extra[1]!=1&&extra[1]!=6&&!passiveCarryAttack(extra[1])){held&=~2;pressed&=~2;}

 if((state==0||state==1)&&(pressed&1)&&(held&128)&&control[1])return -4;
 auto apply=[&](int action)->int{
  if((puss||shared)&&action==0x188){if(gingy)book[4]=(book[4]&~64)|(held&64);return s2_character_ground_attack(table,s,extra,book,animationTick,fetch,ctx);}
  if(puss&&action==0x10025)return s2_puss_wall_enter(s,extra,book,animationTick,fetch,sink,ctx);
  if(puss&&action==0x10024)return s2_puss_air_enter(s,extra,book,animationTick,fetch,ctx);
  if(puss&&(action==0x158||action==0x150))return s2_puss_locomotion_enter(action,held,animationTick,s,extra,status,book,events,fetch,ctx);
  if(donkey&&action==0x188)return s2_donkey_ground_attack(s,extra,book,animationTick,fetch,ctx);
  if(action==0x10020)return s2_donkey_air_enter(s,extra,book,animationTick,fetch,ctx);
  if(action==0x10030){int e=s2_shrek_locomotion_enter(s,extra,status,book,(held&64)?0x10009:0x10008,held,worldTick,animationTick,table,events,fetch,ctx);extra[0]=16;book[5]=0;return e;}
  if(action==0x10031){int e=s2_generic_message(s,8,4,0x08355cc4,animationTick,fetch,ctx);if(e)return e;book[0]=table+18*40;book[1]=0x08053d08;extra[0]=19;int32_t ev[3]={2,5,0};std::copy_n(ev,3,s+41);return 0;}
  if(sceneShrek&&action==0x188)return s2_shrek_scene_attack_enter(s,extra,book,animationTick,table,fetch,ctx);
  if(action==0x10019)return s2_shrek_stomp_enter(s,extra,book,animationTick,table,fetch,ctx);
  if(action==0x1d8)return s2_shrek_clear_contact_event(s);
  if(action==0x178)return s2_shrek_landing_enter(s,extra,book,held,animationTick,table,threshold,fetch,sink,ctx);
  if(action==0x190)return s2_shrek_grab_enter(s,extra,status,worldTick,animationTick,table,events+3,events+6,fetch,dispatch,ctx,book);
  if(action==0x10000){
   // DE8C always looks up motion2, even when no direction is held.
   // A blocked direction (or wall contact without input) then selects1.
   int id=2,w=s[30],h=s[31];int32_t top=add(s[1],-uint32_t(h*128));
   if(held&32){int hit=probe(1,add(s[0],-uint32_t(w*128)-256u),top,256,h*256);if(hit<0)return hit;if(hit)id=1;}
   else if(held&16){int hit=probe(2,add(s[0],uint32_t(w*128)),top,256,h*256);if(hit<0)return hit;if(hit)id=1;}
   else if(totalContacts[1]||totalContacts[2])id=1;
   int32_t row[10];uint32_t address=table;bool found=false;
   for(int i=0;i<40;i++,address+=40){if(!fetch(address,row,10,ctx))return -2;if(row[0]==id){found=true;break;}if(row[0]==999)break;}
   if(!found)return -2;book[0]=int32_t(address);
   return s2_horizontal_input_dynamic_file(collision,held,s,w,h,s+2,totalContacts,s+18,surfaces,surfaceCount);
  }
  return s2_shrek_locomotion_enter(s,extra,status,book,action,held,worldTick,animationTick,table,events,fetch,ctx);
 };
 s[40]&=~16;s[24]=animationTick;
 s2_animation_step(s[76],s[77],s[78],animationTick,s+20);
 std::fill_n(s+64,4,0);int ground;int32_t rail[3]={};
 if(puss)ground=s2_actor_move_puss_file(collision,s,surfaces,surfaceCount,rail,status[1]>0&&extra[0]!=6&&extra[0]!=13&&extra[0]!=15);
 else if(surfaceCount){
  int32_t previous[2]={s[36],s[37]},accepted[16];
  ground=s2_actor_move_dynamic_file(collision,s+2,s,s+32,s+36,s[30],s[31],surfaces,surfaceCount,s+14,s+64,accepted);
  if(ground<0)return ground;for(int i=0;i<2;i++)s[60+i]=int32_t(uint32_t(s[i])-uint32_t(previous[i]));
 }else ground=s2_actor_move_file(collision,s+2,s,s+32,s+36,s[30],s[31],s[40],s+14,s+60);
 if(ground<0)return ground;s[62]=ground;if(puss&&ground)airJumpUsed=false;
 for(int i=0;i<4;i++)totalContacts[i]=int32_t(uint32_t(s[14+i])+uint32_t(s[64+i]));
 int32_t actions[16];int n=s2_contact_actions(extra[0],s+14,s+64,actions);if(n<0)return n;
 for(int i=0;i<n;i++){int e=apply(actions[i]);if(e)return e;}
 extra[2]=held;
 if(sceneShrek&&book[1]){int e=s2_shrek_stomp_audio(s,book,animationTick,fetch,sink,ctx);if(e)return e;}
 bool railEntered=false;
 if(puss){book[7]=0;if(rail[0]){if(!fetch(uint32_t(rail[0]),book+5,1,ctx))return -2;book[7]=s2_puss_rail_angle(rail[1],rail[2]);
  int st=extra[0];bool enter=(st<16&&st!=6&&st!=13&&st!=15)||(st==19&&!(s[20]&255));
  if(enter){int e=s2_puss_rail_enter(s,extra,book,book[5],book[7],animationTick,fetch,ctx);if(e)return e;railEntered=true;}
 }}
 if(railEntered){}else if(puss&&extra[0]==18){
  int e=s2_puss_rail_behavior(s,extra,status,book,held,pressed,rail[0]!=0,totalContacts[0]!=0,animationTick,events,fetch,sink,ctx);if(e)return e;
 }else if(sceneShrek&&(extra[0]==6||extra[0]==13||extra[0]==14||(extra[0]==15))){
  if(extra[0]==6){int e=s2_shrek_hurt_behavior(s,extra,status,book,held,worldTick,animationTick,table,events,fetch,ctx);if(e)return e;}
  // State13 advances primary animation/physics; global game-over is separate.
 }else if(sceneShrek&&extra[0]==22){if(s[20]&255){int e=apply(0x158);if(e)return e;}}else if(sceneShrek&&book[6]&&extra[0]>=16&&extra[0]<=18){
  int w=s[30],h=s[31];int32_t top=add(s[1],-uint32_t(h*128));int left=probe(1,add(s[0],-uint32_t(w*128)-256u),top,256,h*256),right=probe(2,add(s[0],uint32_t(w*128)),top,256,h*256);if(left<0||right<0)return -2;
  if(extra[0]==17){left=bool(totalContacts[1]);right=bool(totalContacts[2]);}
  int e=s2_shrek_lift_behavior(s,extra,status,book,held,pressed,left,right,worldTick,animationTick,table,events,fetch,sink,ctx);if(e)return e;
 }else if(puss&&extra[0]==16){int e=0;if(pressed&1)e=s2_puss_wall_jump(s,extra,status,book,held,animationTick,events,fetch,ctx);else{int hit=wallAllowed(s[18]?2:1);if(hit<0)return hit;if(!hit){e=apply(0x170);if(!e){int32_t idle[10],fall[10];if(!fetch(table,idle,10,ctx)||!fetch(table+4*40,fall,10,ctx))return -2;// physics follows source0410
 e=s2_apply_axis_triple(s+2,idle+2,0,0);if(!e)e=s2_apply_axis_triple(s+2,fall+5,1,0);}}}if(e)return e;
 }else if(puss&&extra[0]==19){int e=s2_puss_air_behavior(s,extra,status,book,held,totalContacts[0]!=0,animationTick,events,fetch,ctx);if(e)return e;
 }else if(human&&extra[0]==19){if(s[20]&255){int e=apply(totalContacts[0]?0x158:0x170);if(e)return e;}
 }else if(gingy&&extra[0]==16){if(s[20]&255){int32_t lim[2];if(!fetch(0x0804b6ec,lim,2,ctx))return -2;int e=0;if(s[61]<lim[0])e=s2_generic_message(s,8,4,0x0833731c,animationTick,fetch,ctx),extra[0]=2;else{if(s[61]>lim[0])e=apply(0x168);if(!e&&s[61]>lim[1])e=apply(0x170);}if(e)return e;}
 }else if(sceneShrek&&!puss&&extra[0]>=19&&extra[0]<=21){int e;
  if(extra[0]==21){e=apply(0x10000);if(e)return e;}
  e=s2_shrek_stomp_behavior(s,extra,status,book,held,worldTick,animationTick,table,events,fetch,sink,ctx);if(e)return e;
 }else if(extra[0]==16&&donkey){int e=s2_donkey_air_behavior(s,extra,book,held,animationTick,fetch,ctx);if(e)return e;}else if(extra[0]==16){int e=s2_shrek_air_attack_behavior(s,extra,status,book,held,worldTick,animationTick,table,events,fetch,sink,ctx);if(e)return e;}
 else if(extra[0]==11){if(control[0]){int e=apply(0x158);if(e)return e;}else if(s[20]&255){int e=apply(0x198);if(e)return e;}}
 else if(extra[0]==9){if(control[0]){int e=apply(0x158);if(e)return e;}if(!totalContacts[0]){int e=apply(0x1d8);if(!e)e=apply(0x1d0);if(e)return e;}}
 else if(extra[0]==7){int e=s2_shrek_attack_behavior(s,extra,status,book,held,worldTick,animationTick,table,events,fetch,ctx);if(e)return e;}
 else if(extra[0]==8){int e=s2_shrek_grab_behavior(s,extra,status,book,held,worldTick,animationTick,table,events,fetch,ctx);if(e)return e;}
 else{
  if(extra[0]==10&&(s[20]&255)){int e=apply(0x158);if(e)return e;}
  int w=s[30],h=s[31];int32_t top=add(s[1],-uint32_t(h*128));
  int left=probe(1,add(s[0],-uint32_t(w*128)-256u),top,256,h*256);
  int right=probe(2,add(s[0],uint32_t(w*128)),top,256,h*256);
  int ceiling=probe(5,add(s[0],-uint32_t(w*128)),add(top,-256u),w*256,h*256);
  if(left<0||right<0||ceiling<0)return -2;
  int32_t in[15]={held,pressed,totalContacts[0]!=0,totalContacts[1]!=0,totalContacts[2]!=0,!left,!right,s[18],control[0],!ceiling,control[1],extra[0]==10?0:control[2],s[20],extra[1],s[11]};
  int decisionPressed=in[1];
  if(sceneShrek&&!donkey&&!puss&&!shared&&extra[0]==2)in[1]&=~2; // type3 rising behavior10DDC has no B attack.
  int decisionState=extra[0]==10?0:puss&&extra[0]==20?1:puss&&extra[0]==21?0:extra[0];
  n=s2_player_decide(decisionState,in,actions,s+18);if(n<0)return n;
  if(sceneShrek&&!donkey&&!puss&&!shared&&(extra[0]==3||extra[0]==4)&&(decisionPressed&2)){if(shrekAirAttackAllowed(extra[3],extra[1])){n=1;actions[0]=0x10019;}}
  if(puss&&extra[0]>=2&&extra[0]<=4&&(decisionPressed&2)){n=1;actions[0]=0x10024;}
  if(shared&&extra[0]>=2&&extra[0]<=4&&(decisionPressed&2)){n=1;actions[0]=gingy?0x10030:0x10031;}
  if(donkey&&extra[0]>=2&&extra[0]<=4&&(decisionPressed&2)){n=1;actions[0]=0x10020;}
  // Air-jump flag uses bit16 of previous-button bookkeeping. Status[7]
  // remains exclusively the hurt recovery deadline.
  // One additional A edge in flight; reuse the original Puss jump row/physics.
  // Landings replenish it; held A and further edges do not create extra jumps.
  if(puss&&(uint32_t(book[4])&0x20000u)&&extra[0]>=2&&extra[0]<=4&&(decisionPressed&1)&&!(decisionPressed&2)&&!airJumpUsed&&!ceiling){n=1;actions[0]=0x160;airJumpUsed=true;}
  if(puss&&extra[0]==4&&!(decisionPressed&1)){int hit=wallAllowed((held&16)?1:(held&32)?2:0);if(hit<0)return hit;if(hit){n=1;actions[0]=0x10025;}}
  for(int i=0;i<n;i++){int e=apply(actions[i]);if(e)return e;}status[3]=0;
 }
 if(extra[0]==4&&extra[1]==2&&(held&1)){int32_t velocity,period;if(!fetch(0x0804b6f4,&velocity,1,ctx)||!fetch(0x0804b70c,&period,1,ctx))return -2;s[11]=velocity;book[3]=s[1];if(status[6]<worldTick){status[6]=int32_t(uint32_t(worldTick)+uint32_t(period));if(sink){int e=sink(11,0x08054020,256,ctx);if(e)return e;}}}
 if(puss){int e=s2_puss_motion_finish(s,extra,book,animationTick,fetch,ctx);if(e)return e;}
 std::copy_n(s+72,2,s+26);std::copy_n(s+74,2,s+30);s2_preserve_bottom(ground,s+32,s[31],s);
 book[4]=(book[4]&0x20000)|held|(puss&&airJumpUsed?0x10000:0);return 0;
}

extern "C" int s2_shrek_player_step_dynamic(const char* collision,int32_t* s,int32_t* extra,int32_t* status,int32_t* book,int held,int32_t wt,int32_t at,const int32_t* control,const int32_t* events,uint32_t table,uint32_t threshold,Fetch fetch,Sink sink,Dispatch dispatch,void* ctx,const int32_t* surfaces,int count){return player_frame(collision,s,extra,status,book,held,wt,at,control,events,table,threshold,fetch,sink,dispatch,ctx,surfaces,count,false);}
extern "C" int s2_shrek_player_step_scene(const char* collision,int32_t* s,int32_t* extra,int32_t* status,int32_t* book,int held,int32_t wt,int32_t at,const int32_t* control,const int32_t* events,uint32_t table,uint32_t threshold,Fetch fetch,Sink sink,Dispatch dispatch,void* ctx,const int32_t* surfaces,int count){return player_frame(collision,s,extra,status,book,held,wt,at,control,events,table,threshold,fetch,sink,dispatch,ctx,surfaces,count,true);}

// Compatibility API: caller explicitly supplies an empty dynamic world.
extern "C" int s2_shrek_player_step_empty_dynamic(const char* collision,int32_t* s,int32_t* extra,int32_t* status,int32_t* book,int held,int32_t worldTick,int32_t animationTick,const int32_t* control,const int32_t* events,uint32_t table,uint32_t threshold,Fetch fetch,Sink sink,Dispatch dispatch,void* ctx){
 return s2_shrek_player_step_dynamic(collision,s,extra,status,book,held,worldTick,animationTick,control,events,table,threshold,fetch,sink,dispatch,ctx,nullptr,0);
}

extern "C" int s2_donkey_player_step_scene(const char* collision,int32_t* s,int32_t* extra,int32_t* status,int32_t* book,int held,int32_t wt,int32_t at,const int32_t* control,const int32_t* events,uint32_t table,uint32_t threshold,Fetch fetch,Sink sink,Dispatch dispatch,void* ctx,const int32_t* surfaces,int count){return player_frame(collision,s,extra,status,book,held,wt,at,control,events,table,threshold,fetch,sink,dispatch,ctx,surfaces,count,true,true);}
