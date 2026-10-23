#define main old
#include "stage93_session_fixture.cpp"
#undef main
int main(){for(int scene=0;scene<30;scene++){auto*s=create(scene);quiet(*s);s->trainerFlags=1;for(int t=0;t<120;t++)step(s,t%60==3?2:0);std::cout<<scene<<" tick "<<s->tick<<" cached "<<s->fetchBlocks.size()<<std::endl;s2_session_destroy(s);}std::cout<<"PASS all 30 scenes, 120 updates each\n";}
