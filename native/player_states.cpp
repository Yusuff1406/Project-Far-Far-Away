// Recovered Shrek locomotion decisions. Callback order is significant.
#include <cstdint>
extern "C" int s2_apply_axis_triple(int32_t*,const int32_t*,int,int);
// in: held, pressed, ground, leftWall, rightWall, leftAllowed,
// rightAllowed, facing, inputActive, jumpClear, dropEligible,
// timerExpired, animationFinished, carriedState, vyQ8.
// out is an ordered list of original vtable slots; 0x10000 = horizontal update,
// 0x10001 = drop-through contact operation. Predicates are sampled by caller.
extern "C" int s2_player_decide(int state,const int32_t* in,int32_t* out,int32_t* face){
 if(!in||!out||!face)return -1;int n=0;auto emit=[&](int a){out[n++]=a;};
 int held=in[0],pressed=in[1];*face=in[7];
 if(state==0){
  if(held&32){*face=1;if(in[5])emit(0x150);}
  if(held&16){*face=0;if(in[6])emit(0x150);}
  if(pressed&2)emit(0x188);if(pressed&4)emit(0x190);
  if(!in[2]){emit(0x1d8);emit(0x1d0);}
  if((pressed&1)&&(held&128)&&in[10])emit(0x10001);
  else if((pressed&1)&&in[9]){emit(0x1d8);emit(0x160);}
  else if(!in[8])emit(0x1a8);else if(in[11])emit(0x1a0);
 }else if(state==1){
  if(in[7]?(!(held&32)||in[3]):(!(held&16)||in[4]))emit(0x158);
  if(pressed&4)emit(0x190);
  if((pressed&1)&&in[9]){emit(0x1d8);emit(0x160);}
  else if(!in[2]){emit(0x1d8);emit(0x1d0);}
  else if(pressed&2)emit(0x188);
 }else if(state>=2&&state<=4){
  // D12C / D0E8 / D0A4 wrappers: attack takes precedence over locomotion.
  if(pressed&2)emit((held&64)?0x10009:0x10008);
  else{emit(0x10000);if(state==2&&in[14]>-698)emit(0x168);
   if(state==3&&in[14]>0)emit(0x170);
   if(state==4&&in[2])emit(0x178);}
 }else if(state==5){emit(0x10000);if(in[12])emit(0x158);else if((pressed&1)&&in[9])emit(0x160);else if(pressed&2)emit(0x188);}
 else return -2;
 return n;
}
// out: logical state, animation index, saved landing-start Y. Supported entry
// routines retain the original distinction between logical state and table ID.
extern "C" int s2_player_enter(int action,int buttons,int carriedState,int32_t y,int32_t* p,int32_t* out){
 if(!p||!out)return -1;const int32_t idle[3]={0,0,0},fall[3]={256,49,1792},walk[3]={384,51,435};
 switch(action){
 case 0x150:s2_apply_axis_triple(p,walk,0,(buttons>>5)&1);s2_apply_axis_triple(p,fall,1,0);out[0]=1;out[1]=1;break;
 case 0x158:s2_apply_axis_triple(p,idle,0,(buttons>>5)&1);s2_apply_axis_triple(p,fall,1,0);out[0]=0;out[1]=0;break;
 case 0x160:{int32_t jump[3]={carriedState==4?-505:-1011,49,1792};s2_apply_axis_triple(p,jump,1,0);out[0]=2;out[1]=2;break;}
 case 0x168:out[0]=3;out[1]=3;break;
 case 0x170:out[0]=4;out[1]=4;out[2]=y;break;
 case 0x1d0:out[0]=4;out[1]=4;out[2]=y;s2_apply_axis_triple(p,fall,1,0);break;
 case 0x178:s2_apply_axis_triple(p,idle,0,(buttons>>5)&1);s2_apply_axis_triple(p,fall,1,0);out[0]=5;out[1]=6;break;
 default:return -2;
 }return 0;
}
