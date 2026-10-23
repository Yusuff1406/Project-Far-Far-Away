#define main old
#include "stage93_session_fixture.cpp"
#undef main
#include <chrono>
static std::vector<uint8_t> stateBytes(OwnedSession&s){QState q;qTransfer(q,s);return q.bytes;}
int main(){
 uint32_t reference[38400],shown[38400];int32_t status[8];
 for(int scene=0;scene<30;scene++){
  auto*a=create(scene);auto*b=create(scene);quiet(*a);quiet(*b);a->trainerFlags=b->trainerFlags=1;s2_session_set_transitions(a,1);s2_session_set_transitions(b,1);
  for(int t=0;t<90;t++){
   int buttons=(t%60<20?16:0)|(t%60==30?2:0);assert(!s2_session_step(a,buttons,reference,38400,status));assert(!s2_session_update(b,buttons,shown,38400,status,1));assert(!s2_session_present(b,256,shown,38400));
   if(!std::equal(reference,reference+38400,shown)){std::cerr<<"pixel mismatch scene "<<scene<<" frame "<<t<<std::endl;return 1;}
   assert(stateBytes(*a)==stateBytes(*b));
   if(t%10==0){auto before=stateBytes(*b);for(int alpha:{0,64,128,192,256}){assert(!s2_session_present(b,alpha,shown,38400));assert(before==stateBytes(*b));}}
  }
  s2_session_destroy(a);s2_session_destroy(b);std::cout<<"exact update/present scene "<<scene<<std::endl;
 }
 // Intermediate images genuinely move; interpolation is bounded and never runs physics.
 {auto*s=create(0);quiet(*s);for(auto&a:s->actors)a.state[40]|=1;for(int t=0;t<50;t++)step(s);qPlace(s->state,100,350);for(int t=0;t<40;t++)step(s);for(int t=0;t<10;t++)assert(!s2_session_update(s,16,shown,38400,status,1));auto before=stateBytes(*s);assert(!s2_session_present(s,0,reference,38400));assert(!s2_session_present(s,256,shown,38400));assert(!std::equal(reference,reference+38400,shown));assert(before==stateBytes(*s));assert(interpolateCoordinate(0,2560,128,16384)==1280);assert(interpolateCoordinate(0,25600,128,16384)==25600);s2_session_destroy(s);}
 // Camera shakes advance only at simulation rate, never with extra redraws.
 {auto*s=create(13);quiet(*s);int32_t effect[3]={16*256,0,1};assert(!s2_camera_effect_begin(s->effects,effect));assert(!s2_session_update(s,16,shown,38400,status,1));auto before=stateBytes(*s);for(int i=0;i<12;i++)assert(!s2_session_present(s,i*20,shown,38400));assert(before==stateBytes(*s));s2_session_destroy(s);}
 std::cout<<"PASS Stage103: 30 scenes x90 exact physics and ARGB, read-only interpolated frames, visible intermediate motion, teleport clamp, camera shake independence\n";
}
