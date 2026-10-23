#define main old
#include "stage93_session_fixture.cpp"
#undef main
static OwnedSession* props(int scene){auto*s=create(scene);quiet(*s);s->trainerFlags=1;for(auto&a:s->actors)if(!liftableProp(a.spawn[1]))a.state[40]|=1;for(int t=0;t<100;t++)step(s);return s;}
static void enter(OwnedSession*s,int action){int32_t ev[3]={1,7,0};assert(!s2_shrek_locomotion_enter(s->state,s->extra(),s->status(),s->book(),action,0,s->tick,s->tick,s->motionTable(),ev,fetch,s));s->rawButtons=s->book()[4]=0;s->contextB=false;}
static SessionLevelActor& prop(OwnedSession*s,int type,int nth=0){for(auto&a:s->actors)if(a.spawn[1]==type&&!nth--)return a;std::abort();}
int main(){std::cout.setf(std::ios::unitbuf);
 int stands=0;
 // Original five crates in2-3 and both stumps in2-4, without changing their flags.
 for(int scene:{9,11}){auto*s=props(scene);int type=scene==9?13:14;for(auto&a:s->actors)if(a.spawn[1]==type){qPlace(s->state,a.state[0]/256,a.state[1]/256-70);enter(s,0x170);for(int t=0;t<60;t++)step(s);int foot=s->state[1]+s->state[31]*128,top=a.state[1]-a.state[31]*128;assert(std::abs(foot-top)<=256);stands++;}s2_session_destroy(s);}
 assert(stands==7);std::cout<<"PASS stand on all seven original crates/stumps in scenes9/11\n";
 for(int scene:{9,11}){auto*s=props(scene);int type=scene==9?13:14;auto&bottom=prop(s,type);auto&top=prop(s,type,1);
  qPlace(s->state,top.state[0]/256+11,(top.state[1]+top.state[31]*128-s->state[31]*128)/256);enter(s,0x158);for(int t=0;t<35;t++)step(s,t==0?2:0);assert(s->book()[6]==top.spawn[0]);
  // Move a genuinely carried prop to the first source prop and physically drop it.
  // Relocation is fixture-only, to avoid encoding a full platforming route.
  qPlace(s->state,bottom.state[0]/256,(bottom.state[1]-bottom.state[31]*128-s->state[31]*128)/256-1);for(int t=0;t<5;t++)step(s);
  for(int t=0;t<100;t++)step(s,t==1?2:0);assert(!s->book()[6]);assert(std::abs(bottom.state[0]-top.state[0])<=256);int gap=bottom.state[1]-bottom.state[31]*128-top.state[1]-top.state[31]*128;assert(gap>=0&&gap<=256);
  // Old sweep coordinates must not send the released prop back through a wall.
  assert(std::abs(top.state[36]-top.state[0])<=256);assert(top.state[39]&1);
  qPlace(s->state,top.state[0]/256,top.state[1]/256-70);enter(s,0x170);for(int t=0;t<60;t++)step(s);assert(std::abs(s->state[1]+s->state[31]*128-top.state[1]+top.state[31]*128)<=256);
  std::cout<<"PASS B pickup / carry / B drop / stack / stand atop stack scene "<<scene<<"\n";s2_session_destroy(s);
 }
 for(int scene:{9,11})for(int facing:{0,1}){auto*s=props(scene);int type=scene==9?13:14;auto&a=prop(s,type,(scene==9&&facing==0)?4:0);while(s->playerType!=6){s->partyHeld=0;switchPartner(*s,512);switchPartner(*s,0);}qPlace(s->state,a.state[0]/256+(facing?18:-18),(a.state[1]+a.state[31]*128-s->state[31]*128)/256);s->state[18]=facing;enter(s,0x158);int x=a.state[0],motion=0;for(int t=0;t<25;t++){step(s,t==1?2:0);motion=std::max(motion,std::abs(a.state[0]-x));}if(motion<=8*256)std::cerr<<"kick blocked? scene "<<scene<<" facing "<<facing<<" pos "<<a.state[0]/256<<","<<a.state[1]/256<<" motion "<<motion<<" vx "<<a.state[5]<<"\n";assert(motion>8*256);std::cout<<"PASS real Donkey B kick scene "<<scene<<" facing "<<facing<<"\n";s2_session_destroy(s);}
 // A partner-held prop is now a one-way platform (Stage109). Ordinary support still exists after release.
 {auto*s=props(9);auto&a=prop(s,13);auto&other=s->party[s->partyIndex==0?1:0];other.state[102]=a.spawn[0];qPlace(s->state,a.state[0]/256,a.state[1]/256-20);assert(!collectSurfaces(*s));int n=s->surfaceCount;other.state[102]=0;assert(!collectSurfaces(*s));assert(s->surfaceCount>=n);s2_session_destroy(s);}
 std::cout<<"PASS released prop support candidates (held partner platforms checked by Stage109)\n";
}
