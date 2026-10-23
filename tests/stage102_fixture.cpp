#define main old
#include "stage93_session_fixture.cpp"
#undef main
#include <chrono>
int main(){
 // First-containing-block precedence matters: the package has overlapping ranges.
 {auto*s=create(0);int32_t got[12];for(auto&b:s->blocks)for(int offset:{0,4,8})for(int n:{1,3,10}){uint32_t addr=b.address+offset;const SessionBlock* ref=nullptr;for(auto&r:s->blocks)if(addr>=r.address&&uint64_t(addr)-r.address<=r.size&&size_t(n*4)<=r.size-(uint64_t(addr)-r.address)){ref=&r;break;}int result=fetch(addr,got,n,s);assert(bool(result)==bool(ref));if(ref){assert(fetch(addr,got,n,s));for(int i=0;i<n;i++){int32_t expected=int32_t(word(s->bytes.data()+ref->offset+addr-ref->address+i*4));assert(got[i]==expected);}}}assert(s->fetchBlocks.size()>5000);s2_session_destroy(s);}
 // Completed terminal animations must never wrap/reemit cues during fade-out.
 for(int scene:{0,1,3,23,29,2}){auto*s=create(scene);quiet(*s);s->levelEnding=true;s->fades=true;s->fade[0]=0;int finishedFrame=-1;bool reached=false;for(int t=0;t<500&&!s->levelComplete;t++){step(s);if(s->finishHeroDone[s->partyIndex]){if(finishedFrame<0)finishedFrame=s->player()[22];assert(s->player()[22]==finishedFrame);reached=true;}}std::cerr<<"finish "<<scene<<" reached "<<reached<<" done "<<s->levelComplete<<" frame "<<s->player()[22]<<" count "<<s->player()[77]<<" tick "<<s->tick<<" dialogue "<<s->dialogue[64]<<std::endl;assert((reached||s->finishDone)&&s->levelComplete);std::map<uint32_t,int> counts;for(auto&r:s->requests)if(r.row[1]==11)counts[uint32_t(r.row[2])]++;for(auto&p:counts)assert(p.second==1);s2_session_destroy(s);}
 // Finite artwork has 416px of foreground, versus the 424px logical world.
 for(int width:{240,356,640}){auto*s=create(11);assert(!s2_session_set_viewport(s,width,160));assert(s->worldHeight==424&&cameraBottom(*s)==256);qPlace(s->state,1500,423);int x=0,y=0;cameraTarget(*s,x,y);assert(y<=256);s2_session_destroy(s);}
 // Install the source clover attachment reply, then route physical B end to end.
 for(int hero:{3,6}){auto*s=create(0);quiet(*s);for(auto&a:s->actors)a.state[40]|=1;for(int t=0;t<20;t++)step(s);s->trainerFlags=1;assert(!s2_session_debug_edit(s,3,hero,0,0));int id=s2_session_debug_edit(s,4,80,s->player()[0]>>8,s->player()[1]>>8);assert(id>0);for(int t=0;t<60;t++)step(s);s->extra()[0]=8;s->extra()[3]=id;int32_t clover[3]={0,17,0};assert(s2_shrek_receive(s->extra(),s->status(),clover,s->tick)==1);const int32_t idle[3]={1,7,0};assert(!s2_shrek_locomotion_enter(s->player(),s->extra(),s->status(),s->book(),0x158,0,s->tick,s->tick,s->motionTable(),idle,fetch,s));std::cout<<"clover hero "<<hero<<" mode "<<s->extra()[1]<<" item "<<s->extra()[3]<<" state "<<s->extra()[0]<<std::endl;
 assert(s->extra()[1]==3&&s->extra()[3]==id);for(int t=0;t<40;t++)step(s);bool attacked=false;for(int t=0;t<30;t++){step(s,t==1?2:0);assert(s->extra()[3]==id);attacked=attacked||s->extra()[0]==7;}assert(attacked);s2_session_destroy(s);}
 for(int id:{15,16}){auto*s=create(id);assert(s2_session_music_hint(s)==0);s->dialogue[78]=50;assert(s2_session_music_hint(s)==(id==16));s2_session_destroy(s);}
 std::cout<<"PASS Stage102 resource cache precedence, six terminal sequences, bottom clamp3, clover attachment/B2, finale music hint\n";
}
