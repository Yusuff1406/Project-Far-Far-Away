#define main old
#include "stage93_session_fixture.cpp"
#undef main
#include <chrono>
#include <ctime>
static double micros(){timespec t{};clock_gettime(CLOCK_THREAD_CPUTIME_ID,&t);return t.tv_sec*1e6+t.tv_nsec/1000.0;}
static double percentile(std::vector<double> v,double p){std::sort(v.begin(),v.end());return v[std::min(v.size()-1,size_t(p*(v.size()-1)))];}
int main(){std::cout<<"scene,width,samples,update_p50_us,update_p95_us,render_p50_us,render_p95_us,frame_p95_us,frame_max_us\n";for(int scene=0;scene<30;scene++)for(int width:{240,356,640}){auto*s=create(scene);quiet(*s);s->trainerFlags=1;assert(!s2_session_set_viewport(s,width,160));std::vector<uint32_t> out(size_t(width)*160);int32_t info104[8];std::vector<std::pair<int,int>> locations{{s->state[0]/256,s->state[1]/256}};
 for(auto&a:s->actors)if((a.spawn[1]>=53&&a.spawn[1]<=60)&&locations.size()<4)locations.emplace_back(a.spawn[2]/256+24,a.spawn[3]/256+(a.state[31]-s->state[31])/2);
 std::vector<double>updates,renders,frames;
 for(auto xy:locations){if(!s->bonus){qPlace(s->state,std::clamp(xy.first,20,s->worldWidth-20),std::clamp(xy.second,20,s->worldHeight-20));cameraFocusTarget(*s,s->cameraFocus);projectPartyCamera(*s);s2_session_reset_presentation(s);}for(int t=0;t<200;t++){int buttons=(t%120<70?16:32)|(t%50==20?1:0)|(t%37==10?2:0);double a=micros();int e=s2_session_update(s,buttons,out.data(),out.size(),info104,1);double b=micros();if(!e)e=s2_session_present(s,128,out.data(),out.size());double c=micros();if(e){std::cerr<<"error "<<scene<<" "<<width<<" "<<e<<std::endl;return 1;}if(t>=40){updates.push_back(b-a);renders.push_back(c-b);frames.push_back(c-a);}}}
 std::cout<<scene<<","<<width<<","<<frames.size()<<","<<percentile(updates,.5)<<","<<percentile(updates,.95)<<","<<percentile(renders,.5)<<","<<percentile(renders,.95)<<","<<percentile(frames,.95)<<","<<*std::max_element(frames.begin(),frames.end())<<std::endl;s2_session_destroy(s);}}
