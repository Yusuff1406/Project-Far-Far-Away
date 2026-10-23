#include "../native/native_session.cpp"
#include <iostream>
int main(){
 int32_t error=0;auto* raw=s2_session_create_level("android/app/src/main/assets/session/resources.s2pk","extracted/scene_29/scene.s2lv","collision/scene_29/scene.s2cl","android/app/src/main/assets/session/sprites","objects/scene_29/scene.s2ob",&error);if(!raw)return 1;
 auto& s=*static_cast<OwnedSession*>(raw);SessionCollisionScope scope(s.decodedCollision.get());auto a=std::find_if(s.actors.begin(),s.actors.end(),[](auto& a){return a.spawn[0]==95;});if(a==s.actors.end())return 2;
 // Run the unmodified source bowman script until reaction registrations exist.
 for(int t=1;t<=3;t++){s.tick=t;s.currentActor=a->spawn[0];error=s2_generic_runtime_step_target(s.collision.c_str(),a->pose(),a->vm(),t,s.worldWidth*256,s.worldHeight*256,fetch,randomValue,&s,4096,a->reactions(),registry,sink,s.player(),&a->auxiliary);if(error)return 3;}
 s.projectiles.clear();SessionProjectile p;p.type=67;int32_t xy[2]={a->state[0]+40*256,a->state[1]};s.tick=20;error=s2_projectile_init(s.collision.c_str(),67,xy,0,s.tick,fetch,sink,&s,p.pose,&p.deadline);if(error)return 4;
 int32_t parry[3]={1,5,2};error=s2_projectile_receive(67,p.pose,&p.deadline,parry,s.tick,fetch,sink,&s);if(error||p.pose[42]!=13||p.pose[5]>=0)return 5;s.projectiles.push_back(p);
 // Keep the hero clear; the reflected arrow must reach the bowman's own boxes.
 s.player()[0]=a->state[0]+140*256;
 bool hit=false;for(int t=21;t<70;t++){s.tick=t;auto& shot=s.projectiles[0];error=s2_projectile_step(s.collision.c_str(),67,shot.pose,t,fetch,sink,&s);if(error)return 6;error=heroContacts(s,false);if(error){std::cerr<<"contact "<<error;return 7;}if(shot.pose[40]&16){hit=true;break;}}
 if(!hit)return 8;
 for(int t=70;t<170&&!(a->state[40]&1);t++){s.tick=t;s.currentActor=a->spawn[0];error=s2_generic_runtime_step_target(s.collision.c_str(),a->pose(),a->vm(),t,s.worldWidth*256,s.worldHeight*256,fetch,randomValue,&s,4096,a->reactions(),registry,sink,s.player(),&a->auxiliary);if(error)return 9;}
 std::cout<<"arrow_hit="<<hit<<" archer_removed="<<bool(a->state[40]&1)<<"\n";if(!(a->state[40]&1))return 10;
 s2_session_destroy(raw);return 0;
}
