#define main old
#include "stage93_session_fixture.cpp"
#undef main
static SessionLevelActor& prop109(OwnedSession*s,int type){for(auto&a:s->actors)if(a.spawn[1]==type&&!(a.state[40]&1))return a;std::abort();}
static OwnedSession* held109(int scene,int type){auto*s=create(scene);quiet(*s);s->trainerFlags=1;for(auto&a:s->actors)if(!liftableProp(a.spawn[1]))a.state[40]|=1;for(int t=0;t<100;t++)step(s);auto&a=prop109(s,type);qPlace(s->state,a.state[0]/256+11,(a.state[1]+a.state[31]*128-s->state[31]*128)/256);const int32_t ev[3]={1,7,0};assert(!s2_shrek_locomotion_enter(s->state,s->extra(),s->status(),s->book(),0x158,0,s->tick,s->tick,s->motionTable(),ev,fetch,s));s->rawButtons=s->book()[4]=0;for(int t=0;t<90;t++)step(s,t==0?2:0);assert(s->book()[6]==a.spawn[0]);return s;}
int main(){std::cout.setf(std::ios::unitbuf);
 for(int scene:{9,11})for(bool donkeyActive:{false,true}){int type=scene==9?13:14;auto*s=held109(scene,type);int held=s->state[102];auto&a=*std::find_if(s->actors.begin(),s->actors.end(),[&](auto&a){return a.spawn[0]==held;});
 assert(propDepth(*s,a.state,256)>propDepth(*s,s->state,256));
 int top=a.state[1]-a.state[31]*128;int32_t*donkey=nullptr;for(auto&p:s->party)if(p.type==6)donkey=p.state;assert(donkey);qPlace(donkey,a.state[0]/256,top/256-65);const int32_t ev[3]={1,7,0};assert(!s2_shrek_locomotion_enter(donkey,donkey+80,donkey+88,donkey+96,0x170,0,s->tick,s->tick,heroTable(6),ev,fetch,s));
 if(donkeyActive){s->partyHeld=0;switchPartner(*s,512);switchPartner(*s,0);assert(s->playerType==6);donkey=s->state;}
 // Inspect actual candidates from both the owner and the descending partner.
 const int32_t*owner=liftedOwner(*s,held);assert(owner);assert(!collectSurfacesFor(*s,owner,0));int ownerCandidates=s->surfaceCount;assert(!collectSurfacesFor(*s,donkey,0));(void)ownerCandidates;
 bool landed=false;int stable=0;for(int t=0;t<90;t++){step(s);int32_t*d=s->playerType==6?s->state:nullptr;for(auto&p:s->party)if(p.type==6&&s->playerType!=6)d=p.state;top=a.state[1]-a.state[31]*128;int foot=d[1]+d[31]*128;landed|=std::abs(top-foot)<=256;stable=std::abs(top-foot)<=256?stable+1:0;}
 if(!landed||stable<20){std::cerr<<"no landing scene="<<scene<<" selected donkey="<<donkeyActive<<" stump top="<<top/256<<"\n";return 1;}assert(liftedOwner(*s,held));s2_session_destroy(s);
 }std::cout<<"PASS real B pickup: Donkey lands on held crate/stump with Shrek or Donkey selected; held prop depth in front of holder\n";
 {auto*s=create(9);quiet(*s);for(int t=0;t<30;t++)step(s);int id=s2_session_debug_edit(s,4,13,600,220);assert(id>0);QState before;qTransfer(before,*s);std::vector<uint32_t>a(356*160),b(a.size());assert(!s2_session_editor_view(s,356,160,450,120,0,0,0,a.data(),a.size()));assert(!s2_session_editor_view(s,356,160,450,120,id,680,220,b.data(),b.size()));int different=0;for(size_t i=0;i<a.size();i++)different+=a[i]!=b[i];assert(different>300);QState after;qTransfer(after,*s);assert(before.bytes==after.bytes);int copy=s2_session_debug_edit(s,11,id,720,220);assert(copy>0);assert(!s2_session_editor_view(s,356,160,450,120,0,0,0,b.data(),b.size()));int visible=0;for(int y=85;y<115;y++)for(int x=250;x<285;x++)visible+=a[y*356+x]!=b[y*356+x];assert(visible>100);
 QState base;qTransfer(base,*s);for(auto wh:{std::pair<int,int>{60,40},{240,160},{640,320},{1280,320}}){std::vector<uint32_t> p(wh.first*wh.second);assert(!s2_session_editor_view(s,wh.first,wh.second,0,0,0,0,0,p.data(),p.size()));QState end;qTransfer(end,*s);assert(base.bytes==end.bytes);}s2_session_destroy(s);
 }std::cout<<"PASS actual sprite moves during read-only preview, copied sprite visible before simulation; zoom views preserve state\n";
}
