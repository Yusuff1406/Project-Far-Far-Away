#include "../native/native_session.cpp"
#include <cassert>
#include <iostream>
#include <set>
#include <fstream>
static OwnedSession* create(int id){char scene[160],collision[160],objects[160];snprintf(scene,sizeof(scene),"extracted/scene_%02d/scene.s2lv",id);snprintf(collision,sizeof(collision),"collision/scene_%02d/scene.s2cl",id);snprintf(objects,sizeof(objects),"objects/scene_%02d/scene.s2ob",id);int error=0;auto* h=static_cast<OwnedSession*>(s2_session_create_level("android/app/src/main/assets/session/resources.s2pk",scene,collision,"android/app/src/main/assets/session/sprites",objects,&error));assert(h);return h;}
static uint32_t pixels[38400];static int32_t info[8];
static void step(OwnedSession* s,int b=0){int e=s2_session_step(s,b,pixels,38400,info);if(e)std::cerr<<"session error "<<e<<" tick "<<s->tick<<"\n";assert(!e);}
static void quiet(OwnedSession& s){for(auto& a:s.actors)if(a.spawn[1]==151)a.state[40]|=1;}
int main(){
 // Visible source Shrek and mouse sprites in the actual first mini arena.
 {auto*h=create(26);auto&s=*h;for(int t=0;t<60;t++)step(h);std::vector<uint32_t> visible(pixels,pixels+38400);int flags=s.player()[40];s.player()[40]|=1;assert(!render(s,pixels));int different=0;for(int i=0;i<38400;i++)different+=pixels[i]!=visible[i];assert(different>80);s.player()[40]=flags;assert(std::any_of(s.actors.begin(),s.actors.end(),[](auto&a){return a.spawn[1]==140&&!(a.state[40]&1);}));std::cout<<"mini Shrek pixels "<<different<<"\n";s2_session_destroy(h);}
 // Flame traversal is superseded by the moving-fire fixture in Stage94.
 // Holding physical B must not send a second detach on the translated Select.
 for(int held:{1,75}){auto*h=create(5);auto&s=*h;quiet(s);auto&cat=s.actors[0];s.tick=150;s.status()[4]=10000;
 for(int capture=1;capture<=3;capture++){s.extra()[3]=0;s.extra()[1]=0;s.contextB=false;s.rawButtons=0;s.book()[4]=0;int32_t idle[3]={1,7,0};assert(!s2_shrek_locomotion_enter(s.player(),s.extra(),s.status(),s.book(),0x158,0,s.tick,s.tick,s.motionTable(),idle,fetch,&s));assert(!s2_generic_message(cat.pose(),8,4,0x08344e2c,s.tick,fetch,&s));cat.subtype[0]=3;cat.subtype[4]=s.tick+1000;std::fill_n(cat.pose()+2,12,0);cat.state[0]=s.state[0];cat.state[1]=s.state[1]+12*256;
 for(int t=0;t<80&&!s.dialogue[64];t++){step(h,t<held?2:0);if(t<45)assert(s.book()[6]==cat.spawn[0]);}
 assert(cat.subtype[6]==capture);if(capture<3)assert(cat.subtype[0]!=4&&s.extra()[3]==0);else assert(cat.subtype[0]==5&&s.dialogue[64]);}
 s2_session_destroy(h);}
 // Joint B is resolved independently, with Shrek either selected or a partner.
 for(int scene:{2,4})for(bool shrekSelected:{false,true}){auto*h=create(scene);auto&s=*h;quiet(s);for(auto&a:s.actors)a.state[40]|=1;
 auto heroFor=[&](int type){if(s.playerType==type)return s.state;for(auto&p:s.party)if(p.type==type)return p.state;return static_cast<int32_t*>(nullptr);};
 if(!shrekSelected)while(s.playerType!=6){s.partyHeld=0;switchPartner(s,512);switchPartner(s,0);}s.partyHeld=0;
 auto*hero=heroFor(3);int y=hero[1];for(auto&p:s.party)if(p.type!=3){auto*other=heroFor(p.type);other[0]=(180+p.type*10)*256;other[1]=y;other[36]=other[0];other[37]=other[1];}
 auto&item=s.actors[0];item.spawn[1]=16;int32_t xy[2]={100*256,y};assert(!s2_generic_runtime_init(xy,0,actorAnimation(16),0,fetch,&s,item.pose()));s2_reactions_init(0,item.reactions());s2_vm_start(actorScript(16),item.vm());hero[0]=xy[0];hero[1]=xy[1];hero[14]=1;
 for(int t=0;t<26;t++)step(h,768|(t<4?2:0));assert(heroFor(3)[102]==item.spawn[0]);s2_session_destroy(h);}
 // Expanded source activation includes offscreen actors, never the whole map.
 for(int width:{240,356}){auto*h=create(0);auto&s=*h;s.width=width;s.cameraWindow[0]=500*256;s.cameraWindow[1]=100*256;s.cameraWindow[2]=width*256;s.cameraWindow[3]=160*256;auto&a=s.actors[0];a.spawn[1]=53;a.state[0]=(500+width+120)*256;a.state[1]=200*256;assert(enemyVisible(s,a));a.state[0]=(500+width+400)*256;assert(!enemyVisible(s,a));s2_session_destroy(h);}
 // A waiting hero still receives actual enemy contact far beyond the viewport.
 {auto*h=create(2);auto&s=*h;s.tick=20;s.cameraWindow[0]=2900*256;s.cameraWindow[1]=0;s.cameraWindow[2]=240*256;s.cameraWindow[3]=160*256;auto&waiting=s.party[s.partyIndex==0?1:0];auto&enemy=s.actors[0];for(auto&a:s.actors)a.state[40]|=1;enemy.spawn[1]=57;enemy.state[40]=2;enemy.state[41]=1;enemy.state[42]=38;enemy.state[0]=waiting.state[0];enemy.state[1]=waiting.state[1];enemy.state[30]=enemy.state[31]=40;int hp=waiting.state[89];assert(enemyVisible(s,enemy));assert(!stepPartners(s,0)&&waiting.state[89]<hp);s2_session_destroy(h);}
 // Pit loss is immediate, silent, and applies to all five heroes.
 for(int id:{0,1,3,23,29}){auto*h=create(id);auto&s=*h;quiet(s);s.fades=true;s.fade[0]=0;for(auto&a:s.actors)a.state[40]|=1;s.tick=100;s.state[0]=80*256;s.state[1]=(s.worldHeight+100)*256;s.state[36]=s.state[0];s.state[37]=s.state[1];s.state[32]=s.state[0]-s.state[30]*128;s.state[33]=s.state[1]-s.state[31]*128;s.book()[1]=0;s.requests.clear();step(h);std::cerr<<"pit "<<id<<" tick "<<s.tick<<" state "<<s.extra()[0]<<" death "<<s.deathReturning<<" book "<<s.book()[1]<<" diag "<<s.dialogue[64]<<"\n";assert(s.deathReturning&&s.book()[1]==0);size_t before=s.requests.size();for(int t=0;t<8;t++)step(h);assert(std::none_of(s.requests.begin()+before,s.requests.end(),[](auto&q){return q.row[1]==11;}));s2_session_destroy(h);}
 // In-world return uses mosaic; standalone loss retains its black fade.
 {auto*h=create(0);auto&s=*h;s.mini.reset(create(7));s.mini->miniFailed=true;s.fades=true;s.fade[0]=0;step(h);assert(s.mosaic&&s.miniReturning&&s.fade[0]==4);s2_session_destroy(h);auto*b=create(7);b->fades=true;b->miniFailed=true;step(b);assert(!b->mosaic&&b->fade[0]==4);s2_session_destroy(b);}
 // Arrival movement and final timing are covered by Stage94.
 std::cout<<"PASS Stage93: mini visibility, boss captures6 including held B, joint pickups4, activation2, silent pits5, transition contexts2\n";return 0;
}
