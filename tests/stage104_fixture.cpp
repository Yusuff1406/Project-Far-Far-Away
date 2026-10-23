#define main old
#include "stage93_session_fixture.cpp"
#undef main
static OwnedSession* pickup(int hero,int type){for(int dy:{-16,0,-24})for(int dx:{-16,0,16,-24,24}){auto*s=create(0);quiet(*s);for(auto&a:s->actors)a.state[40]|=1;for(int t=0;t<30;t++)step(s);assert(!s2_session_debug_edit(s,3,hero,0,0));qPlace(s->state,200,300);s->state[18]=dx>0?1:0;for(int t=0;t<60;t++)step(s);int x=s->state[0]/256,y=s->state[1]/256;int id=s2_session_debug_edit(s,4,type,x-dx,y+dy);assert(id>0);for(int t=0;t<80;t++)step(s);for(int t=0;t<90;t++)step(s,t==2?4:0);if(s->extra()[3]==id&&s->extra()[1])return s;s2_session_destroy(s);}return nullptr;}
static std::vector<uint8_t> bytes104(OwnedSession&s){QState q;qTransfer(q,s);return q.bytes;}
int main(){
 for(int hero:{3,4,5,6,7})for(int type:{79,80,81,82}){
  auto*s=pickup(hero,type);if(!s){std::cerr<<"pickup failed "<<hero<<" "<<type<<std::endl;return 1;}int mode=type==79?3:type==80?4:type==81?5:7,id=s->extra()[3];assert(s->extra()[1]==mode);s->trainerFlags=1;
  step(s,2);assert(s->extra()[0]==7&&s->extra()[3]==id);for(int t=0;t<70;t++)step(s);
  // Landed enemy is a real generic actor; the attack must reach its HP logic.
  int eid=s2_session_debug_edit(s,4,53,(s->state[0]/256)+20,s->state[1]/256);assert(eid>0);for(int t=0;t<3;t++)step(s);auto&enemy=*std::find_if(s->actors.begin(),s->actors.end(),[&](auto&a){return a.spawn[0]==eid;});enemy.state[52]=40;
  for(int t=0;t<65&&enemy.state[52]==40;t++){qPlace(enemy.state,s->state[0]/256+20,s->state[1]/256);step(s,t==1?2:0);assert(s->extra()[3]==id);}if(enemy.state[52]>=40){std::cerr<<"no damage "<<hero<<" "<<type<<std::endl;return 1;}enemy.state[40]|=1;for(int t=0;t<70;t++)step(s);
  step(s,1);bool airborne=false,attack=false;for(int t=0;t<70;t++){int state=s->extra()[0];bool press=(hero==3?(state==3||state==4):(state>=2&&state<=4));step(s,press&&!airborne?2:0);if(press)airborne=true;int next=s->extra()[0];attack=attack||(hero==3?(next>=19&&next<=21):(hero==4||hero==7?next==19:next==16));assert(s->extra()[3]==id);}if(!attack){std::cerr<<"no air attack "<<hero<<" "<<type<<std::endl;return 1;}
  if(type==81){s->status()[5]=0;assert(!render(*s,pixels));std::vector<uint32_t> visible(pixels,pixels+38400);int flags=s->state[40];s->state[40]|=1;assert(!render(*s,pixels));std::vector<uint32_t> hidden(pixels,pixels+38400);assert(visible!=hidden);s->state[40]=flags;s->status()[5]=1;assert(!render(*s,pixels));assert(std::equal(hidden.begin(),hidden.end(),pixels));auto before=bytes104(*s);uint32_t out[38400];for(int i=0;i<4;i++)assert(!s2_session_present(s,128,out,38400));assert(before==bytes104(*s));for(int t=0;t<4;t++){int phase=s->status()[5];step(s);assert(s->status()[5]==(phase^1));}}
  std::cout<<"PASS physical pickup/B/damage/air hero "<<hero<<" item "<<type<<" mode "<<mode<<std::endl;s2_session_destroy(s);
 }
 for(int type:{80,81}){auto*s=pickup(3,type);assert(s);int id=s->extra()[3];bool attack=false;for(int t=0;t<100;t++){step(s,t<2?3:0);attack=attack||(s->extra()[0]>=19&&s->extra()[0]<=21);assert(s->extra()[3]==id);}assert(attack);s2_session_destroy(s);}std::cout<<"PASS Shrek A+B with real clover and invisibility pickups\n";

}
