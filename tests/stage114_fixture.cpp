#define main oldmain113
#include "stage93_session_fixture.cpp"
#undef main
#include "../native/frontend.cpp"
static void prepareCapture(OwnedSession*s,int phase,int facing){quiet(*s);s->tick=150;s->trainerFlags=0;s->status()[4]=0;s->state[90]=0;s->rawButtons=s->book()[4]=0;s->state[18]=facing;const int32_t idle[3]={1,7,0};assert(!s2_shrek_locomotion_enter(s->player(),s->extra(),s->status(),s->book(),0x158,0,s->tick,s->tick,s->motionTable(),idle,fetch,s));auto&cat=s->actors[0];assert(!s2_generic_message(cat.pose(),8,4,0x08344e2c,s->tick,fetch,s));cat.subtype[0]=3;cat.subtype[2]=phase;cat.subtype[6]=phase;cat.subtype[4]=s->tick+1000;std::fill_n(cat.pose()+2,12,0);cat.state[0]=s->state[0];cat.state[1]=s->state[1]+12*256;}
int main(){std::cout.setf(std::ios::unitbuf);
 for(int phase:{0,1,2})for(int facing:{0,1})for(int hold:{1,75}){auto*s=create(5);prepareCapture(s,phase,facing);auto&cat=s->actors[0];int hp=s->status()[1];std::set<int> frames;uint32_t grabAnimation=0;int32_t row[10];for(int i=0;i<40;i++){assert(fetch(s->motionTable()+i*40,row,10,s));if(row[0]==20){grabAnimation=row[1];break;}}assert(grabAnimation);
  for(int t=0;t<90&&!s->dialogue[64];t++){step(s,t<hold?2:0);assert(s->status()[1]==hp);assert(!s->extra()[3]);if(t<45){assert(s->book()[6]==cat.spawn[0]);assert(s->extra()[0]>=16&&s->extra()[0]<=18);if(t==0)assert(uint32_t(s->state[47])==grabAnimation);frames.insert(s->state[22]);int32_t target[80];std::copy_n(cat.pose(),80,target);assert(!s2_shrek_lift_position(s->player(),target,s->book(),s->extra(),fetch,s));assert(target[0]==cat.state[0]&&target[1]==cat.state[1]);}}
  assert(frames.size()>1);assert(cat.subtype[6]==phase+1);if(phase<2)assert(!s->book()[6]&&cat.subtype[0]!=4);else assert(cat.subtype[0]==5&&s->dialogue[64]);s2_session_destroy(s);
 }std::cout<<"PASS12 real B lifts: source motion20, multiple frames, exact frame-marker attachment, no Select carry, all three rounds and both facings, release and HP preserved\n";
 {auto*s=create(5);prepareCapture(s,0,0);step(s,4);assert(s->actors[0].subtype[6]==0&&!s->book()[6]&&!s->extra()[3]);s2_session_destroy(s);}std::cout<<"PASS Select does not capture Puss\n";
}
