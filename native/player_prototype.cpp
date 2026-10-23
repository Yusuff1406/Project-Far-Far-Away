// 40-word harness state. Recovered actor order: animation, movement/contacts,
// contact responses, behavior, body update. Whole-world scheduling still pending.
#include <cstdint>
#include <algorithm>
extern "C" int s2_apply_axis_triple(int32_t*,const int32_t*,int,int);
extern "C" int s2_horizontal_input_file(const char*,int,const int32_t*,int,int,int32_t*,const int32_t*,int32_t*);
extern "C" int s2_static_probe_q8(const char*,int,int32_t,int32_t,int32_t,int32_t);
extern "C" int s2_sprite_info(const char*,int,int32_t*);
extern "C" int s2_sprite_bounds(const char*,int,int32_t*);
extern "C" void s2_animation_step(int,int,int,int32_t,int32_t*);
extern "C" void s2_animation_restart(int,int,int,int32_t,int32_t*);
extern "C" int s2_player_decide(int,const int32_t*,int32_t*,int32_t*);
extern "C" int s2_player_enter(int,int,int,int32_t,int32_t*,int32_t*);
extern "C" int s2_contact_actions(int,const int32_t*,const int32_t*,int32_t*);
extern "C" int s2_actor_move_file(const char*,int32_t*,int32_t*,int32_t*,int32_t*,int,int,int,int32_t*,int32_t*);
extern "C" void s2_preserve_bottom(int,const int32_t*,int,int32_t*);
extern "C" void s2_actor_anchor_q8(const int32_t*,const int32_t*,int,int,int32_t*);
extern "C" int s2_actor_move_dynamic_file(const char*,int32_t*,int32_t*,int32_t*,int32_t*,int,int,const int32_t*,int,int32_t*,int32_t*,int32_t*);
extern "C" int s2_actor_probe_file(const char*,int,int32_t,int32_t,int32_t,int32_t,const int32_t*,int);
extern "C" int s2_horizontal_input_dynamic_file(const char*,int,const int32_t*,int,int,int32_t*,const int32_t*,int32_t*,const int32_t*,int);
extern "C" void s2_prototype_init(int32_t* s){
 if(!s)return;std::fill(s,s+40,0);s[0]=120*256;s[1]=350*256;const int32_t falling[3]={256,49,1792};s2_apply_axis_triple(s+2,falling,1,0);s[14]=1;s[23]=4;s[27]=s[1];s[30]=16;s[31]=50;s[32]=s[0]-16*128;s[33]=s[1]-50*128;s[34]=16*256;s[35]=50*256;s[36]=s[0];s[37]=s[1];
}
static int enter(const char* sprite,int action,int buttons,int32_t* s){
 int32_t out[3]={s[26],s[19],s[27]};int c=s2_player_enter(action,buttons,0,s[1],s+2,out);if(c==-2)return 0;if(c)return c;
 if(action==0x150)s[18]=(buttons>>5)&1;s[26]=out[0];s[19]=out[1];s[27]=out[2];int32_t info[4];c=s2_sprite_info(sprite,s[19],info);if(c)return c;s2_animation_restart(info[2],info[1],0,s[24],s+20);return 0;
}
extern "C" int s2_prototype_step_dynamic(const char* collision,const char* sprite,int buttons,int32_t* s,const int32_t* surfaces,int count,int32_t* dynamicOut){
 if(!collision||!sprite||!s||count<0||count>16||(!surfaces&&count))return -1;s[24]++;int32_t info[4];int code=s2_sprite_info(sprite,s[19],info);if(code)return code;
 s2_animation_step(info[2],info[1],info[3],s[24],s+20);
 int32_t dynamic[4],accepted[16];int groundMode=s2_actor_move_dynamic_file(collision,s+2,s,s+32,s+36,s[30],s[31],surfaces,count,s+14,dynamic,accepted);if(groundMode<0)return groundMode;
 if(dynamicOut)std::copy_n(dynamic,4,dynamicOut);int32_t actions[16];int n=s2_contact_actions(s[26],s+14,dynamic,actions);for(int i=0;i<4;i++)s[14+i]+=dynamic[i];
 for(int i=0;i<n;i++){code=enter(sprite,actions[i],buttons,s);if(code)return code;}
 int w=s[30],h=s[31];int left=s2_actor_probe_file(collision,1,s[0]-w*128-256,s[1]-h*128,256,h*256,surfaces,count);
 int right=s2_actor_probe_file(collision,2,s[0]+w*128,s[1]-h*128,256,h*256,surfaces,count);
 int ceiling=s2_actor_probe_file(collision,5,s[0]-w*128,s[1]-h*128-256,w*256,h*256,surfaces,count);if(left<0||right<0||ceiling<0)return -2;
 int32_t in[15]={buttons,buttons&~s[25],s[14]!=0,s[15]!=0,s[16]!=0,!left,!right,s[18],1,!ceiling,0,0,s[20],0,s[11]};int32_t face=s[18];n=s2_player_decide(s[26],in,actions,&face);if(n<0)return n;s[18]=face;
 for(int i=0;i<n;i++){
  if(actions[i]==0x10000){code=s2_horizontal_input_dynamic_file(collision,buttons,s,w,h,s+2,s+14,s+18,surfaces,count);if(code)return code;}
  else{code=enter(sprite,actions[i],buttons,s);if(code)return code;}
 }
 int32_t bounds[4];code=s2_sprite_bounds(sprite,s[19],bounds);if(code)return code;s[30]=bounds[2];s[31]=bounds[3];s2_preserve_bottom(groundMode,s+32,s[31],s);s[25]=buttons;return 0;
}
extern "C" int s2_prototype_anchor(const char* sprite,const int32_t* s,int32_t* out){
 if(!sprite||!s||!out)return -1;int32_t bounds[4];int c=s2_sprite_bounds(sprite,s[19],bounds);if(c)return c;s2_actor_anchor_q8(bounds,s,s[18],0,out);out[0]>>=8;out[1]>>=8;return 0;
}

extern "C" int s2_prototype_step(const char* collision,const char* sprite,int buttons,int32_t* s){return s2_prototype_step_dynamic(collision,sprite,buttons,s,nullptr,0,nullptr);}
