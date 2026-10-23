#define main old
#include "stage93_session_fixture.cpp"
#undef main
static void visible110(OwnedSession*s,int width=356){s->width=width;s->cameraX=850;s->cameraY=80;for(size_t i=0;i<s->party.size();i++){auto*p=int(i)==s->partyIndex?s->state:s->party[i].state;qPlace(p,1000+int(i)*30,180);}cameraFocusTarget(*s,s->cameraFocus);projectPartyCamera(*s);quiet(*s);}
int main(){std::cout.setf(std::ios::unitbuf);
 for(int scene:{2,4})for(int key:{256,512}){
 auto*s=create(scene);visible110(s);int start=s->partyIndex;auto sounds=s->requests.size();for(int t=0;t<600;t++)switchPartner(*s,key);assert(s->partyIndex==start&&s->requests.size()==sounds&&!s->jointControl);switchPartner(*s,0);assert(s->partyIndex==(start+1)%int(s->party.size()));int now=s->partyIndex;for(int t=0;t<120;t++)switchPartner(*s,0);assert(s->partyIndex==now);s2_session_destroy(s);
 }std::cout<<"PASS L/R stay on current hero for600 held frames; final release cycles once in two/three-character scenes\n";
 for(int scene:{2,4})for(int first:{256,512})for(int delay:{0,1,2,8})for(int releaseFirst:{256,512}){
 auto*s=create(scene);visible110(s);int start=s->partyIndex;for(int t=0;t<delay;t++)switchPartner(*s,first);switchPartner(*s,768);assert(s->partyIndex==start&&s->jointControl);auto sounds=s->requests.size();for(int t=0;t<60;t++){switchPartner(*s,768);assert(s->jointControl&&s->partyIndex==start);}for(int t=0;t<8;t++){switchPartner(*s,768^releaseFirst);assert(s->jointControl&&s->partyIndex==start);}assert(s->requests.size()==sounds);switchPartner(*s,0);assert(!s->jointControl&&s->partyIndex==start);switchPartner(*s,first);switchPartner(*s,0);assert(s->partyIndex==(start+1)%int(s->party.size()));s2_session_destroy(s);
 }std::cout<<"PASS32 staggered/atomic L+R press/release cases: no intermediate focus, no extra activation sound, no trailing cycle\n";
 {auto*s=create(4);visible110(s);int start=s->partyIndex;switchPartner(*s,256);s2_session_cancel_shoulders(s);switchPartner(*s,0);assert(s->partyIndex==start);switchPartner(*s,768);assert(s->jointControl);assert(!s2_session_save_state(s,"scratch110/chord.s2qs"));assert(!s2_session_load_state(s,"scratch110/chord.s2qs"));switchPartner(*s,256);assert(s->jointControl);switchPartner(*s,0);assert(!s->jointControl&&s->partyIndex==start);assert(!s2_session_debug_edit(s,3,s->party[(start+1)%s->party.size()].type,0,0));assert(s->partyHeld==0);s->extra()[0]=13;int other=s->party[(s->partyIndex+1)%s->party.size()].type;assert(s2_session_debug_edit(s,3,other,0,0)<0);s2_session_destroy(s);}
 std::cout<<"PASS cancellation, chord save/load and trainer selection without a pending release\n";
 {auto*s=create(4);visible110(s,240);for(auto&a:s->actors)a.state[40]|=1;int first=s->partyIndex;for(int t=0;t<20;t++)step(s,256);assert(s->partyIndex==first);step(s,768|16);assert(s->jointControl);for(size_t i=0;i<s->party.size();i++)if(int(i)!=s->partyIndex)assert(s->party[i].state[82]&16);step(s,512|16);assert(s->jointControl&&s->partyIndex==first);step(s,0);assert(!s->jointControl&&s->partyIndex==first);s2_session_destroy(s);}
 std::cout<<"PASS real simulation fans shared movement to every partner in the same frame\n";
}
