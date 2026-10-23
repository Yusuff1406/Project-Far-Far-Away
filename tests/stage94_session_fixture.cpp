#define main previous_fixture_main
#include "stage93_session_fixture.cpp"
#undef main
static void place(int32_t*h,int x,int y){h[0]=x*256;h[1]=y*256;h[36]=h[0];h[37]=h[1];h[32]=h[0]-h[30]*128;h[33]=h[1]-h[31]*128;}
int main(){
 // Either shoulder is the same edge-triggered cycle, for real 2/3 hero scenes.
 for(int scene:{2,4})for(int key:{256,512}){auto*h=create(scene);auto&s=*h;quiet(s);int first=s.partyIndex;for(size_t i=0;i<s.party.size()*2;i++){switchPartner(s,0);int was=s.partyIndex;switchPartner(s,key);assert(s.partyIndex==was);for(int t=0;t<12;t++)switchPartner(s,key);assert(s.partyIndex==was);switchPartner(s,0);assert(s.partyIndex==(was+1)%int(s.party.size()));}assert(s.partyIndex==first);s2_session_destroy(h);}
 // Offscreen partners cannot take joint input or show active portraits.
 for(int scene:{2,4})for(int width:{240,356}){auto*h=create(scene);auto&s=*h;quiet(s);s.width=width;s.cameraX=1000-width/2;s.cameraY=100;place(s.state,1000,180);for(size_t i=0;i<s.party.size();i++)if(int(i)!=s.partyIndex)place(s.party[i].state,1030,180);switchPartner(s,768);assert(s.jointControl&&sharedCamera(s));assert(!stepPartners(s,16));for(size_t i=0;i<s.party.size();i++)if(int(i)!=s.partyIndex)assert(s.party[i].state[82]&16);
 for(size_t i=0;i<s.party.size();i++)if(int(i)!=s.partyIndex)place(s.party[i].state,1800,180);switchPartner(s,768);assert(!s.jointControl&&!sharedCamera(s));assert(!stepPartners(s,16));for(size_t i=0;i<s.party.size();i++)if(int(i)!=s.partyIndex)assert(!(s.party[i].state[82]&16));
 std::vector<uint32_t>a(width*160),b(width*160);assert(!render(s,a.data()));s.jointControl=true;assert(!render(s,b.data()));assert(a==b);s.jointControl=false;
 for(size_t i=0;i<s.party.size();i++)if(int(i)!=s.partyIndex)place(s.party[i].state,1030,180);switchPartner(s,768);assert(s.jointControl&&sharedCamera(s));place(s.state,1800,180);switchPartner(s,768);assert(!s.jointControl&&!sharedCamera(s));s2_session_destroy(h);}
 // Original fire script receives both its top-marker and gate turn messages.
 {auto*h=create(6);auto&s=*h;auto&fire=*std::find_if(s.actors.begin(),s.actors.end(),[](auto&a){return a.spawn[1]==147;});int lo=1000,hi=-1000,turns=0,previous=0;for(int t=0;t<3600;t++){place(s.state,30,30);s.state[11]=0;step(h);assert(!s.miniFailed&&!(fire.state[40]&1));int y=fire.state[1]/256;lo=std::min(lo,y);hi=std::max(hi,y);int direction=fire.state[11]<0?-1:fire.state[11]>0?1:0;if(previous&&direction&&direction!=previous)turns++;if(direction)previous=direction;assert(y>=0&&y<140);}assert(hi-lo>50&&turns>=12);std::cerr<<"fire y "<<lo<<".."<<hi<<" turns "<<turns<<"\n";s2_session_destroy(h);}
 // Finite laboratory artwork is eight pixels shorter than world bounds.
 for(int width:{240,356}){auto*h=create(21);auto&s=*h;s.width=width;place(s.state,490,800);s.autoRestart=false;assert(cameraBottom(s)==432);int x,y;cameraTarget(s,x,y);assert(y==432);std::vector<uint32_t>a(width*160);assert(!render(s,a.data()));for(int py=152;py<160;py++)for(int px=0;px<width;px++)assert(a[py*width+px]!=0xff181818);s2_session_destroy(h);}
 // Arriving does not trap a hero in terminal12; walking can leave the zone.
 {auto*h=create(2);auto&s=*h;quiet(s);for(auto&a:s.actors)if(a.spawn[1]!=148)a.state[40]|=1;auto&zone=*std::find_if(s.actors.begin(),s.actors.end(),[](auto&a){return a.spawn[1]==148;});place(s.state,zone.state[0]/256,zone.state[1]/256-40);for(int t=0;t<120&&!s.finishWaiting[s.partyIndex];t++)step(h);assert(s.finishWaiting[s.partyIndex]&&!s.levelEnding&&s.extra()[0]!=12);std::set<int> frames;for(int t=0;t<1000;t++){step(h);frames.insert(s.state[22]);assert(s.extra()[0]!=12&&!s.levelEnding&&uint32_t(s.state[47])==0x0834f334);}assert(frames.size()>10);int x=s.state[0];for(int t=0;t<60;t++)step(h,32);assert(s.state[0]<x-50*256&&!s.finishWaiting[s.partyIndex]&&!s.levelEnding);
 place(s.state,zone.state[0]/256,zone.state[1]/256-40);for(size_t i=0;i<s.party.size();i++)if(int(i)!=s.partyIndex)place(s.party[i].state,zone.state[0]/256+10,zone.state[1]/256-40);
 for(int t=0;t<120&&!s.levelEnding;t++)step(h);assert(s.levelEnding&&s.dialogue[64]);s2_session_destroy(h);}
 // F45C completes on the first finished hero, rather than the longest clip.
 {auto*h=create(2);auto&s=*h;quiet(s);s.levelEnding=true;s.fades=true;s.fade[0]=0;int elapsed=0;for(;elapsed<220&&!s.levelComplete;elapsed++)step(h);assert(s.levelComplete&&elapsed>=65&&elapsed<100);std::cerr<<"final celebration+fade frames "<<elapsed<<"\n";s2_session_destroy(h);}
 std::cout<<"PASS Stage94: shoulders4, visibility/control/HUD4, fire3600, pit camera2, movable arrival, source first-completion timing\n";
}
