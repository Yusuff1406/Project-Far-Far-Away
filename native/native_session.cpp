#include "carry_policy.h"
#include "attack_damage.h"
// Small owned scene fixture, shared by host tests and Android JNI.
#include "native_session.h"
#include "dialogue_presentation.h"
#include <algorithm>
#include <fstream>
#include <iterator>
#include <memory>
#include <string>
#include <vector>
#include <cstring>
#include <map>
#include <unordered_map>
extern "C" int s2_scene_render_editor(void*,int,int,int,int,uint32_t*,size_t);
extern "C" int s2_scene_composite_front(void*,int,int,int,int,uint32_t*,size_t);
using Fetch=int(*)(uint32_t,int32_t*,int,void*);
extern "C" int s2_actor_move_file(const char*,int32_t*,int32_t*,int32_t*,int32_t*,int,int,int,int32_t*,int32_t*);
extern "C" int s2_apply_axis_triple(int32_t*,const int32_t*,int,int);
extern "C" int s2_generic_message(int32_t*,int,int,int32_t,int32_t,Fetch,void*);
using Random=int32_t(*)(void*);
using Registry=void(*)(int,void*);
using Sink=int(*)(int,uint32_t,int32_t,void*);
using Dispatch=int(*)(uint32_t,const int32_t*,void*);
using Reply=int(*)(const int32_t*,void*);
extern "C" int s2_generic_runtime_init(const int32_t*,int,uint32_t,int32_t,Fetch,void*,int32_t*);
extern "C" int s2_shrek_reactions_init(int32_t*,int32_t*,int32_t*,int,int32_t);
extern "C" void s2_vm_start(uint32_t,int32_t*);
extern "C" int s2_shrek_locomotion_enter(int32_t*,int32_t*,int32_t*,int32_t*,int,int,int32_t,int32_t,uint32_t,const int32_t*,Fetch,void*);
extern "C" int s2_shrek_player_step_empty_dynamic(const char*,int32_t*,int32_t*,int32_t*,int32_t*,int,int32_t,int32_t,const int32_t*,const int32_t*,uint32_t,uint32_t,Fetch,Sink,Dispatch,void*);
extern "C" int s2_generic_runtime_step_empty_dynamic(const char*,int32_t*,int32_t*,int32_t,int32_t,int32_t,Fetch,Random,void*,int,int32_t*,Registry,Sink);
extern "C" int s2_shrek_contact_pair(int32_t*,int32_t*,int32_t,uint32_t,int,int32_t*,int32_t*,int32_t*,Fetch,void*,int32_t*);
extern "C" int s2_generic_contact_pair(int32_t*,int32_t*,int32_t*,int32_t*,Fetch,void*,int32_t*);
extern "C" int s2_generic_contact_pair_receiver(int32_t*,int32_t*,Fetch,Reply,void*,int32_t*);
extern "C" int s2_shrek_carry_follow(const int32_t*,int32_t*,int32_t*,int32_t*,int32_t,int32_t,Fetch,Sink,Dispatch,void*);
extern "C" int s2_generic_activate(int32_t*,int32_t*,const int32_t*);
extern "C" int s2_shrek_receive(int32_t*,int32_t*,const int32_t*,int32_t);
extern "C" void* s2_scene_create(const char*);
extern "C" void s2_scene_destroy(void*);
extern "C" int s2_scene_render(void*,int,int,int,int,uint32_t*,size_t);
extern "C" int s2_scene_camera_bottom(void*,int);
extern "C" int s2_scene_render_front(void*,int,int,int,int,uint8_t*,size_t);
extern "C" int s2_scene_camera_right(void*,int);
extern "C" void* s2_collision_create(const char*);
extern "C" void s2_collision_destroy(void*);
extern "C" void* s2_collision_bind(void*);
struct SessionSceneDeleter{void operator()(void* p)const{s2_scene_destroy(p);}};
struct SessionCollisionDeleter{void operator()(void* p)const{s2_collision_destroy(p);}};
struct SessionCollisionScope{void* previous;explicit SessionCollisionScope(void* p):previous(s2_collision_bind(p)){}~SessionCollisionScope(){s2_collision_bind(previous);}};
extern "C" int s2_render_file_foreground(const char*,int,int,int,int,uint8_t*,size_t);
extern "C" int s2_render_file(const char*,int,int,int,int,int,uint8_t*,size_t);
extern "C" int s2_render_file_background_repeat(const char*,int,int,int,int,int,int,uint8_t*,size_t);
extern "C" int s2_sprite_render_file(const char*,int,int,int,int,int,int,int,uint8_t*,size_t);
extern "C" void* s2_sprite_bank_create(const char*);
extern "C" void s2_sprite_bank_destroy(void*);
extern "C" int s2_sprite_composite_bank(void*,int,int,int,int,int,int,int,uint32_t*,size_t);
extern "C" int s2_sprite_composite_bank_palette(void*,int,int,int,int,int,int,int,uint32_t*,size_t,int);
extern "C" int s2_shrek_fire_enter(int32_t*,int32_t*,int32_t*,int32_t,Fetch,void*);
extern "C" int s2_shrek_water_enter(int32_t*,int32_t*,int32_t*,int32_t,Fetch,void*);
extern "C" void s2_actor_anchor_q8(const int32_t*,const int32_t*,int,int,int32_t*);
extern "C" int s2_camera_effect_step(int32_t*,const int32_t*,const int32_t*,int32_t*);
extern "C" int s2_screen_effect_step(int32_t*);
extern "C" int s2_screen_effect_argb(const int32_t*,uint32_t*,size_t);
extern "C" int s2_camera_effect_begin(int32_t*,const int32_t*);
extern "C" int s2_screen_effect_begin(int32_t*,int32_t);
extern "C" int s2_actor_mark_removed(int32_t*,int32_t,uint32_t*,size_t);
extern "C" uint32_t s2_audio_descriptor_gain(uint32_t,int32_t,int32_t);
extern "C" uint32_t s2_audio_volume_byte(uint32_t);
extern "C" int s2_scene_spawn_plan_file(const char*,const uint32_t*,size_t,int32_t*,size_t);
extern "C" int s2_object_category(int);
extern "C" void s2_reactions_init(int32_t,int32_t*);
extern "C" int s2_static_probe_q8(const char*,int,int32_t,int32_t,int32_t,int32_t);
extern "C" int s2_shrek_scene_bounce_receive(int32_t*,int32_t*,int32_t*,int32_t*,const int32_t*,int32_t,int32_t,uint32_t,int,Fetch,void*);
extern "C" int s2_shrek_coin_receive(const int32_t*,const int32_t*,int32_t*,Sink,void*);
extern "C" int s2_dynamic_surfaces(const int32_t*,int,int,int32_t*,const int32_t*,int,int32_t*);
extern "C" int s2_actor_probe_file(const char*,int,int32_t,int32_t,int32_t,int32_t,const int32_t*,int);
extern "C" int s2_shrek_player_step_dynamic(const char*,int32_t*,int32_t*,int32_t*,int32_t*,int,int32_t,int32_t,const int32_t*,const int32_t*,uint32_t,uint32_t,Fetch,Sink,Dispatch,void*,const int32_t*,int);
extern "C" int s2_shrek_contact_pair_resolved_carry(int32_t*,int32_t*,int32_t,uint32_t,int,int32_t*,int32_t*,int32_t*,Fetch,void*,int32_t*,int(*)(void*));
extern "C" int s2_shrek_player_step_scene(const char*,int32_t*,int32_t*,int32_t*,int32_t*,int,int32_t,int32_t,const int32_t*,const int32_t*,uint32_t,uint32_t,Fetch,Sink,Dispatch,void*,const int32_t*,int);
extern "C" int s2_shrek_lift_enter(int32_t*,int32_t*,int32_t*,int,int32_t,uint32_t,Fetch,void*);
extern "C" int s2_shrek_lift_position(const int32_t*,int32_t*,int32_t*,int32_t*,Fetch,void*);
extern "C" int s2_shrek_hurt_receive(int32_t*,int32_t*,int32_t*,int32_t*,const int32_t*,int32_t,int32_t,uint32_t,Fetch,void*);
extern "C" int s2_generic_event(int32_t*,int32_t*,int32_t*,const int32_t*,int32_t,Fetch,Registry,void*);
extern "C" int s2_actor_spawn_point_q8(const int32_t*,Fetch,void*,int32_t*);
extern "C" int s2_plain_runtime_init(const int32_t*,int,uint32_t,int32_t,Fetch,void*,int32_t*);
extern "C" int s2_plain_runtime_step(int32_t*,int32_t);
extern "C" int s2_generic_runtime_step_target(const char*,int32_t*,int32_t*,int32_t,int32_t,int32_t,Fetch,Random,void*,int,int32_t*,Registry,Sink,const int32_t*,bool*);
extern "C" int s2_spawner_init(const int32_t*,int32_t*);
extern "C" int s2_spawner_can_create(const int32_t*);
extern "C" int s2_spawner_created(int32_t*);
extern "C" int s2_spawner_notice(int32_t*,int32_t,const int32_t*);
extern "C" int32_t s2_spawner_tag(int32_t,int32_t);
extern "C" int s2_scene_object_params_file(const char*,int,int32_t*);
extern "C" int s2_generic_runtime_step_spawner(const char*,int32_t*,int32_t*,int32_t,int32_t,int32_t,Fetch,Random,void*,int,int32_t*,Registry,Sink,const int32_t*,bool*,const int32_t*);
extern "C" int s2_smoke_runtime_init(const char*,const int32_t*,int,int32_t,Fetch,void*,int32_t*);
extern "C" int s2_smoke_runtime_step(const char*,int32_t*,int32_t);
extern "C" int s2_dialogue_lookup(int32_t,Fetch,void*,uint32_t*);
extern "C" int s2_dialogue_start(uint32_t,int32_t*);
extern "C" int s2_dialogue_step(int32_t*,int32_t,int,int,Fetch,void*);
extern "C" int s2_shrek_talk_receive(int32_t*,int32_t*,int32_t*,int32_t*,int,int32_t,Fetch,void*);
extern "C" int s2_actor_camera_active(const int32_t*,const int32_t*);
extern "C" int s2_actor_envelope_q8(const int32_t*,Fetch,void*,int32_t*);
extern "C" int s2_actor_outside_world(const int32_t*,int32_t,int32_t);
extern "C" int s2_shrek_fall_death(int32_t*,int32_t*,int32_t*,int32_t,Fetch,void*);
extern "C" int s2_dialogue_trigger_init(const int32_t*,Fetch,void*,int32_t*);
extern "C" int s2_dialogue_trigger_contact(const int32_t*,const int32_t*,int,int,Fetch,void*,int32_t*);
extern "C" int s2_bonus_rewards(int,int,Fetch,void*,int32_t*);
extern "C" int s2_shrek_finish_enter(int32_t*,int32_t*,int32_t*,int32_t,Fetch,void*);
extern "C" int s2_shrek_finish_step(int32_t*,const int32_t*,int32_t,Fetch,Sink,void*);
extern "C" int s2_fade_step(int32_t*);
extern "C" int s2_fade_argb(int,uint32_t*,size_t);
extern "C" int s2_mosaic_argb(int,uint32_t*,int,int);
extern "C" int s2_actor_contact_rects(const int32_t*,int,Fetch,void*,int32_t*,int);
extern "C" int s2_rect_overlap_xywh(const int32_t*,const int32_t*);
extern "C" int s2_shrek_carry_release(int32_t*,int32_t*,int32_t,const int32_t*,Dispatch,void*);
extern "C" int s2_donkey_player_step_scene(const char*,int32_t*,int32_t*,int32_t*,int32_t*,int,int32_t,int32_t,const int32_t*,const int32_t*,uint32_t,uint32_t,Fetch,Sink,Dispatch,void*,const int32_t*,int);
extern "C" int s2_character_terminal_enter(uint32_t,int,int32_t*,int32_t*,int32_t*,int32_t,Fetch,void*);
extern "C" int s2_donkey_terminal_enter(int,int32_t*,int32_t*,int32_t*,int32_t,Fetch,void*);
extern "C" int s2_shrek_bounce_receive(int32_t*,int32_t*,int32_t*,int32_t*,const int32_t*,int32_t,int32_t,uint32_t,int,Fetch,void*);
extern "C" int s2_puss_gate_init(const int32_t*,int,int32_t,Fetch,void*,int32_t*,int32_t*);
extern "C" int s2_puss_gate_contact(int32_t*,int32_t*,const int32_t*,int,int32_t,Fetch,Sink,void*);
extern "C" int s2_cake_init(const int32_t*,Fetch,void*,int32_t*,int32_t*,int32_t*);
extern "C" int s2_cake_receive(int32_t*,int32_t*,const int32_t*,int32_t,Sink,void*);
extern "C" int s2_cake_step(int32_t*,int32_t*,int32_t*,int32_t,int32_t,Sink,void*);
extern "C" int s2_fairy155_init(const int32_t*,Fetch,void*,int32_t*,int32_t*);
extern "C" int s2_fairy155_receive(int32_t*,int32_t*,const int32_t*,int,Fetch,Sink,void*);
extern "C" int s2_fairy155_step(int32_t*,int32_t*,const int32_t*,const int32_t*,int,int,Fetch,Sink,void*);
extern "C" int s2_fairy156_init(const int32_t*,Fetch,void*,int32_t*,int32_t*,int32_t*);
extern "C" int s2_fairy156_receive(int32_t*,int32_t*,int32_t*,const int32_t*,int,Fetch,Sink,void*);
extern "C" int s2_fairy156_step(int32_t*,int32_t*,int32_t*,const int32_t*,const int32_t*,int,int,int,Fetch,Sink,void*);
static bool fairyType(int t){return t==155||t==156;}
extern "C" int s2_puss_boss_init(const int32_t*,Fetch,void*,int32_t*,int32_t*);
extern "C" int s2_puss_boss_receive(int32_t*,int32_t*,const int32_t*,int,int,Fetch,Sink,void*);
extern "C" int s2_puss_boss_step(const char*,int32_t*,int32_t*,int,int,Fetch,Sink,void*);
struct ActorBinding{int type;uint32_t animation,script;int kind;};
static const ActorBinding extraBindings[]={
#include "campaign_actor_bindings.inc"
};
static const ActorBinding* extraBinding(int t){for(auto& b:extraBindings)if(b.type==t)return &b;return nullptr;}
extern "C" int s2_donkey_balance_step(const char*,int32_t*,int32_t*,int32_t,int32_t,int32_t,Fetch,Random,void*,int,int32_t*,Registry,Sink);
extern "C" int32_t s2_source_random(uint32_t*);
extern "C" int s2_slope_runtime_init(const int32_t*,int,uint32_t,int32_t,Fetch,void*,int32_t*,int32_t*);
extern "C" int s2_slope_surfaces(const int32_t*,int,int32_t*,int32_t*);
static bool storyScene(int scene){switch(scene){case 0:case 1:case 2:case 13:case 17:case 25:case 14:case 9:case 11:case 8:case 4:case 10:case 23:case 21:case 29:case 24:case 3:case 19:case 22:case 28:case 12:case 20:case 15:case 16:case 5:return true;default:return false;}}
static bool liftableProp(int t){return t>=13&&t<=17;}
static bool pushBlock(int t){return t>=31&&t<=34;}
static bool specialExit(int t){return t==149||t==150||t==152;}
static uint32_t heroTable(int t){return t==4?0x0804c4fc:t==5?0x0804be94:t==6?0x0804c1b4:t==7?0x0804bb4c:0x0804b73c;}
static uint32_t heroAnimation(int t){return t==4?0x08344c1c:t==5?0x08337334:t==6?0x0832ff2c:t==7?0x08355b74:0x0834f25c;}
static uint32_t heroHealth(int t){return t==3||t==7?0x083283f8:t==5?0x083283c8:0x083283e0;}
static uint32_t heroIcon(int t){return t==4?0x08328368:t==5?0x08328338:t==6?0x08328308:t==7?0x08328410:0x08328398;}
static bool plateType(int t){return t==27||t==28||t==29;}
static bool spawnerType(int t){return t==45||t==46||t==49||t==50;}
static bool slopeType(int t){return t==23||t==24;}
static bool markerType(int t){return t>=63&&t<=66;}
static bool rewardType(int type){return type>=81&&type<=85;}
static bool npcType(int type){const auto* b=extraBinding(type);return type==94||type==92||type==100||type==101||(b&&b->kind==2);}
static uint32_t word(const uint8_t* p){return uint32_t(p[0])|(uint32_t(p[1])<<8)|(uint32_t(p[2])<<16)|(uint32_t(p[3])<<24);}
extern "C" int s2_generic_runtime_step_dynamic(const char*,int32_t*,int32_t*,int32_t,int32_t,int32_t,Fetch,int32_t(*)(void*),void*,int,int32_t*,void(*)(int,void*),Sink,const int32_t*,int);
extern "C" int s2_generic_runtime_step_target_dynamic(const char*,int32_t*,int32_t*,int32_t,int32_t,int32_t,Fetch,int32_t(*)(void*),void*,int,int32_t*,void(*)(int,void*),Sink,const int32_t*,bool*,const int32_t*,int);
extern "C" int s2_generic_runtime_step_spawner_dynamic(const char*,int32_t*,int32_t*,int32_t,int32_t,int32_t,Fetch,int32_t(*)(void*),void*,int,int32_t*,void(*)(int,void*),Sink,const int32_t*,bool*,const int32_t*,const int32_t*,int);
struct SessionBlock{uint32_t address;size_t offset,size;};
struct SessionAnimation{uint32_t address,index;std::string path;void* bank=nullptr;};
struct SessionWorldRequest{int32_t row[8];};
extern "C" int s2_scene_dimensions_file(const char*,int32_t*);
struct SessionLevelActor{bool registered=false,auxiliary=false,spawnSettled=false,editorDeleted=false;int32_t aux[80]={};int32_t spawn[8]={};int32_t state[216]={};int32_t params[8]={},subtype[16]={};int32_t* pose(){return state;}int32_t* vm(){return state+80;}int32_t* reactions(){return state+144;}};
static uint32_t actorAnimation(int type){if(const auto* b=extraBinding(type))return b->animation;switch(type){case 81:return 0x08342e14;case 82:return 0x08342de4;case 83:return 0x08342e2c;case 84:return 0x08342e44;case 85:return 0x08342e5c;case 94:return 0x0833d6dc;case 139:return 0x0833ce8c;case 138:return 0x0834abf8;case 140:return 0x0833ced4;case 39:return 0x0831ddb8;case 120:return 0x0832a6ec;case 121:return 0x0832a704;case 122:return 0x0832a71c;case 130:return 0x0832a77c;case 134:return 0x0832a794;case 135:return 0x0832a7ac;case 92:return 0x0833d6ac;case 100:return 0x0833d7b4;case 101:return 0x0833d7fc;case 46:return 0x0831df38;case 57:return 0x0831e0b8;case 53:return 0x0831de48;case 90:case 89:return 0x0832eb84;case 10:return 0x0834ad30;case 14:return 0x0834acb8;case 16:return 0x0834abc8;default:return 0x0834ab98;}}
static uint32_t actorScript(int type){if(const auto* b=extraBinding(type))return b->script;switch(type){case 81:return 0x0804d324;case 82:return 0x0804d164;case 83:return 0x0804d37c;case 84:return 0x0804d42c;case 85:return 0x0804d4dc;case 94:return 0x08025078;case 138:return 0x0804a530;case 140:return 0x0804a5bc;case 39:return 0x0804f650;case 92:case 100:case 101:return 0x08025000;case 46:return 0x0804efa0;case 57:return 0x0804e22c;case 53:return 0x0804dd74;case 90:return 0x08051a44;case 89:return 0x08051ad8;case 10:return 0x08051d70;case 14:return 0x08052714;case 16:return 0x080528e0;default:return 0x08052c28;}}
extern "C" int s2_projectile_init(const char*,int,const int32_t*,int,int32_t,Fetch,Sink,void*,int32_t*,int32_t*);
extern "C" int s2_projectile_step(const char*,int,int32_t*,int32_t,Fetch,Sink,void*);
extern "C" int s2_projectile_receive(int,int32_t*,int32_t*,const int32_t*,int32_t,Fetch,Sink,void*);
struct SessionProjectile{int type=0,deadline=0,damageUnits=0;int32_t pose[80]={};uint64_t renderId=0;};
struct SessionSmoke{int32_t pose[80]={};uint64_t renderId=0;};
static bool ambientType(int type){const auto* b=extraBinding(type);return (!plateType(type)&&!pushBlock(type))&&((b&&b->kind==1)||type==134||type==135||type==120||type==121||type==122||type==130);}
struct SessionBankDeleter{void operator()(void* p)const{s2_sprite_bank_destroy(p);}};
struct SessionPartner{int type=3,rawButtons=0;bool contextB=false;int32_t spawn[8]={},state[320]={};};
struct RenderPoint{uint64_t key;int32_t x,y;bool visible;};
struct OwnedSession{
 std::vector<int32_t*> drawActors,drawFront,drawDepth;std::vector<uint32_t> childCanvas;std::unordered_map<uint32_t,size_t> animationLookup;
 std::vector<RenderPoint> previousRender;std::vector<std::pair<const int32_t*,uint64_t>> renderKeys;uint64_t nextRenderId=1;int drawTick=0,drawFade=0;bool drawMosaic=false,displayCaptured=false;bool cameraReady=false,historyReady=false;int lastRenderX=0,lastRenderY=0,previousRenderX=0,previousRenderY=0;
 bool deferRender=false;int heroPower[5]={-1,-1,-1,-1,-1};int trainerFlags=0,heroSpeed[5]={100,100,100,100,100},heroJump[5]={100,100,100,100,100};
 std::vector<SessionPartner> party;int partyIndex=0,partyHeld=0;bool jointControl=false;int cameraX=0,cameraY=0,cameraBlend=0;int32_t cameraFocus[2]={};
 int32_t fairyMarkers[8]={};int specialDeadline=1800;bool forceBossDrop=false;bool autoRestart=true,deathReturning=false,finishStarted=false,finishDone=false;bool finishHeroDone[3]={},finishWaiting[3]={};int deathRestarts=0;
 bool mosaic=false,bonusResults=false,contextB=false,pussDoubleJump=false;int rawButtons=0;
 bool fades=false,miniReturning=false,levelEnding=false,levelComplete=false;int32_t fade[2]={};int presentationTick=0,lastBonusScore=0,bestBonusScore=0,rewardCount=0;int32_t rewardTypes[4]={};
 std::unique_ptr<void,SessionSceneDeleter> decodedScene;std::unique_ptr<void,SessionCollisionDeleter> decodedCollision;
 std::unique_ptr<OwnedSession> mini;bool bonus=false,miniPending=false,miniFailed=false;int miniCursor=0;int32_t mouseSpawner[2]={};std::string package,objects;
 std::map<std::string,std::unique_ptr<void,SessionBankDeleter>> spriteBanks;
 std::vector<uint8_t> bytes;std::vector<SessionBlock> blocks;std::unordered_map<uint64_t,size_t> fetchBlocks;std::vector<SessionAnimation> animations;
 std::vector<SessionProjectile> projectiles;
 std::vector<SessionSmoke> smoke;std::vector<SessionWorldRequest> requests;int32_t effects[9]={};uint32_t removed[4]={};
 std::string scene,collision,sprites;int worldWidth=3200,worldHeight=400;int32_t state[320]={};int32_t tick=0,sounds=0,error=0;int width=240,height=160;
 int32_t dialogue[80]={};int dialogueTick=0,dialogueHeld=0,dialogueSerial=0,dialoguePage=0,blockedButtons=0,pressedButtons=0;std::vector<std::string> dialogueLines;
 int cameraWindow[4]={};
 uint32_t balanceRandomState=1;
 int bonusIndex()const{return playerType==7?4:playerType==5?3:playerType==4?2:playerType==6?1:0;}
 bool introDialogue=false;bool bonusUnavailable=false;int sceneId=0,playerType=3;uint32_t motionTable()const{return heroTable(playerType);}
 bool level=false;int32_t playerSpawn[8]={};int rowCount=0,currentActor=0;int32_t coins=0,coinTarget=40;std::vector<SessionLevelActor> actors,pending;int nextSpawnId=72;int32_t surfaces[16*9]={};int surfaceCount=0;int comboPhase=0,comboFrames=0;bool comboHeld=false;
 int32_t* player(){return state;}int32_t* extra(){return state+80;}int32_t* status(){return state+88;}int32_t* book(){return state+96;}int32_t* item(){return state+104;}int32_t* vm(){return state+184;}int32_t* reactions(){return state+248;}
};
// Presentation-only IDs and points are deliberately absent from save-state data.
static void renderKeys(OwnedSession&s){s.renderKeys.clear();s.renderKeys.emplace_back(s.state,0x100000000ull+s.playerType);for(size_t i=0;i<s.party.size();i++)if(int(i)!=s.partyIndex)s.renderKeys.emplace_back(s.party[i].state,0x100000000ull+s.party[i].type);if(!s.level)s.renderKeys.emplace_back(s.item(),0x200000000ull);for(auto&a:s.actors){uint64_t key=(uint64_t(uint32_t(a.spawn[0]))<<16)|uint16_t(a.spawn[1]);s.renderKeys.emplace_back(a.pose(),0x300000000ull+key);s.renderKeys.emplace_back(a.aux,0x400000000ull+key);}for(auto&p:s.projectiles){if(!p.renderId)p.renderId=s.nextRenderId++;s.renderKeys.emplace_back(p.pose,0x500000000ull+p.renderId);}for(auto&p:s.smoke){if(!p.renderId)p.renderId=s.nextRenderId++;s.renderKeys.emplace_back(p.pose,0x500000000ull+p.renderId);}}
static void beginPresentation(OwnedSession&s){renderKeys(s);s.previousRender.clear();for(auto&entry:s.renderKeys){const auto*p=entry.first;s.previousRender.push_back(RenderPoint{entry.second,p[0],p[1],!(p[40]&1)});}s.previousRenderX=s.lastRenderX;s.previousRenderY=s.lastRenderY;s.historyReady=s.cameraReady;}
static int interpolateCoordinate(int old,int now,int alpha,int limit){return std::abs(int64_t(now)-old)>limit?now:int(int64_t(old)+(int64_t(now)-old)*alpha/256);}
static bool enemyVisible(const OwnedSession& s,const SessionLevelActor& a){
 if(a.spawn[1]!=46&&(a.spawn[1]<53||a.spawn[1]>62))return true;
 int64_t x=a.state[0],y=a.state[1];
 int32_t expanded[4]={s.cameraWindow[0]-240*256,s.cameraWindow[1]-160*256,s.cameraWindow[2]+480*256,s.cameraWindow[3]+320*256};
 if(s2_actor_camera_active(a.state,expanded)>0)return true;
 // An offscreen waiting hero remains part of the world and can be attacked.
 for(size_t i=0;i<s.party.size();i++)if(int(i)!=s.partyIndex){const auto* h=s.party[i].state;if(h[89]>0&&std::abs(x-h[0])<(s.width/2+240)*256&&std::abs(y-h[1])<240*256)return true;}
 return false;
}
static int reserve_spawn_id(OwnedSession& s){
 for(const auto& a:s.actors)if(a.spawn[0]>s.rowCount&&(a.state[40]&1)&&std::none_of(s.pending.begin(),s.pending.end(),[&](const SessionLevelActor& p){return p.spawn[0]==a.spawn[0];}))return a.spawn[0];
 return s.nextSpawnId<128?s.nextSpawnId++:-3;
}
static int fetch(uint32_t address,int32_t* out,int n,void* ctx){
 if(n<0||n>4096)return 0;auto& s=*static_cast<OwnedSession*>(ctx);size_t count=size_t(n)*4;
 // Cache the first containing block, preserving package overlap precedence.
 uint64_t key=(uint64_t(address)<<13)|uint32_t(n);auto cached=s.fetchBlocks.find(key);size_t first=cached==s.fetchBlocks.end()?0:cached->second;
 for(size_t bi=first;bi<s.blocks.size();bi++){const auto& b=s.blocks[bi];uint64_t off=uint64_t(address)-b.address;if(address>=b.address&&off<=b.size&&count<=b.size-off){if(cached==s.fetchBlocks.end())s.fetchBlocks.emplace(key,bi);for(int i=0;i<n;i++)out[i]=int32_t(word(s.bytes.data()+b.offset+off+size_t(i)*4));if(n==10)for(int t=3;t<=7;t++){uint32_t table=heroTable(t),end=table+1600;for(int u=3;u<=7;u++)if(heroTable(u)>table)end=std::min(end,heroTable(u));if(address>=table&&address<end&&(address-table)%40==0){for(int j=2;j<=4;j++)out[j]=int32_t(int64_t(out[j])*s.heroSpeed[t-3]/100);if(out[5]<0)out[5]=int32_t(int64_t(out[5])*s.heroJump[t-3]/100);break;}}return 1;}}return 0;
}
// Generic query66 and conditional audio use the current camera visibility byte.
// Source18208 tests the union of body and frame, expanded by4px.
static int updateActorVisibility(OwnedSession& s,int32_t* pose){
 int32_t bounds[4];int e=s2_actor_envelope_q8(pose,fetch,&s,bounds);if(e)return e;
 int64_t right=int64_t(s.cameraWindow[0])+s.cameraWindow[2],bottom=int64_t(s.cameraWindow[1])+s.cameraWindow[3];
 pose[56]=bounds[0]<right&&s.cameraWindow[0]<bounds[2]&&bounds[1]<bottom&&s.cameraWindow[1]<bounds[3];return 0;
}
// Source078CC nearest registry and149E4/14A0C exclusion predicates.
// Camera focus and L/R control do not choose the enemy's target.
static const int32_t* nearestHero(const OwnedSession& s,const SessionLevelActor& a){
 const int32_t* selected=nullptr;int64_t best=INT64_MAX;
 auto consider=[&](const int32_t* h){if(h[81]==5||(a.state[53]&&h[90])||h[80]==13||h[80]==14||h[80]==15)return;int64_t dx=(a.state[0]>>8)-(h[0]>>8),dy=(a.state[1]>>8)-(h[1]>>8),d=dx*dx+dy*dy;if(d<=best){best=d;selected=h;}};
 if(s.party.empty())consider(s.state);else for(size_t i=0;i<s.party.size();i++)consider(int(i)==s.partyIndex?s.state:s.party[i].state);return selected;
}
static int32_t randomValue(void* ctx){auto& s=*static_cast<OwnedSession*>(ctx);return (s.sceneId==20||s.sceneId==18||s.sceneId==27)?s2_source_random(&s.balanceRandomState):37;}
static int32_t balanceRandomValue(void* ctx){return s2_source_random(&static_cast<OwnedSession*>(ctx)->balanceRandomState);}
static void registry(int enabled,void* ctx){auto& s=*static_cast<OwnedSession*>(ctx);auto a=std::find_if(s.actors.begin(),s.actors.end(),[&](const SessionLevelActor& x){return x.spawn[0]==s.currentActor;});if(!s.level||a==s.actors.end()){s.error=-4;return;}a->registered=enabled!=0;}
extern "C" int s2_target_generator_init(const int32_t*,int,int32_t*,int32_t*);
extern "C" int s2_target_generator_step(int32_t*);
extern "C" int s2_target_generator_notice(int32_t*,const int32_t*);
static int sink(int kind,uint32_t address,int32_t scale,void* ctx){
 auto& s=*static_cast<OwnedSession*>(ctx);SessionWorldRequest q{{s.tick,kind,int32_t(address),scale,0,0,0,0}};int e=0;
 if(kind==35){s.forceBossDrop=true;}else if(kind==31){auto a=std::find_if(s.actors.begin(),s.actors.end(),[&](const SessionLevelActor& v){return v.spawn[0]==s.currentActor;});if(a==s.actors.end()||address!=157)return -4;if(s.projectiles.size()>=256)return 0;SessionProjectile p;p.type=157;int32_t xy[2];e=s2_actor_spawn_point_q8(a->pose(),fetch,&s,xy);if(!e)e=s2_projectile_init(s.collision.c_str(),157,xy,a->state[18],s.tick,fetch,sink,&s,p.pose,&p.deadline);if(e)return e;s.projectiles.push_back(p);q.row[4]=157;q.row[5]=xy[0];q.row[6]=xy[1];}
 else if(kind==32){for(auto& p:s.projectiles)p.pose[40]|=1;}
 else if(kind==11){
 // Book1 chapter5 starts with silent red guards; their initial alert sample
 // must not occupy a mixer voice before the first actual attack.
 if(s.sceneId==17&&s.tick==1&&address==0x08053f24)return 0;
 s.sounds++;
 }
 else if(kind==29){if(!s.bonus)return -4;s.coins++;const int32_t notice[3]={2,3,0};for(auto& a:s.actors)if(a.spawn[1]==144&&a.registered)s2_target_generator_notice(a.subtype,notice);}
 else if(kind==30){
  auto source=std::find_if(s.actors.begin(),s.actors.end(),[&](const SessionLevelActor& a){return a.spawn[0]==s.currentActor;});if(source==s.actors.end())return -4;
  for(int i=0;i<s.rewardCount;i++){int id=reserve_spawn_id(s);if(id<0)return 0;SessionLevelActor a;int32_t row[8]={id,s.rewardTypes[i],source->state[0],source->state[1],0,0,0,0};std::copy_n(row,8,a.spawn);s.pending.push_back(a);q.row[4+i]=s.rewardTypes[i];}s.rewardCount=0;
 }
 else if(kind==1){if(!fetch(address,q.row+4,4,ctx))return -2;if(q.row[4]==0&&q.row[5]==24){if(s.bonus){s.miniFailed=true;s.mosaic=false;s.fade[1]=64;}else if(s.sceneId==20)s.deathReturning=true;}
  if(q.row[4]==0&&q.row[5]==25)s.deathReturning=true;if(s.level&&q.row[4]==9){if(q.row[5]==2)for(auto& a:s.actors){if(a.spawn[1]==150){int total=int(std::count_if(s.actors.begin(),s.actors.end(),[](const SessionLevelActor& v){return v.spawn[1]==73;}));if(++a.subtype[0]>=total)a.subtype[1]=1;}if(a.spawn[1]==72&&(!q.row[6]||q.row[6]==a.spawn[6]))a.state[40]|=1;}int saved=s.currentActor;for(auto& a:s.actors){if(!a.registered||(a.state[40]&1))continue;s.currentActor=a.spawn[0];e=s2_generic_event(a.pose(),a.vm(),a.reactions(),q.row+4,s.tick,fetch,registry,ctx);if(e||s.error)break;}s.currentActor=saved;}
 } // Queued global packet, not applied by a fabricated manager.
 else if(kind==16){if(!fetch(address,q.row+4,3,ctx))return -2;e=s2_camera_effect_begin(s.effects,q.row+4);}
 else if(kind==21){auto a=std::find_if(s.actors.begin(),s.actors.end(),[&](const SessionLevelActor& x){return uint32_t(x.spawn[0])==address;});if(!s.level||a==s.actors.end()||(a->state[40]&1))return -4;int32_t event[3]={0,11,0};int accepted=s2_generic_activate(a->vm(),a->reactions(),event);if(accepted<0)return accepted;q.row[4]=int32_t(address);q.row[5]=11;s.requests.push_back(q);return accepted;}
 else if(kind==20){q.row[4]=int32_t(address);q.row[5]=3;q.row[6]=scale;e=s2_camera_effect_begin(s.effects,q.row+4);s.effects[4]=2;}
 else if(kind==17){e=s2_screen_effect_begin(s.effects+5,int32_t(address));std::copy_n(s.effects+5,4,q.row+4);}
 else if(kind==19){if(!s.level){e=s2_actor_mark_removed(s.item(),77,s.removed,4);q.row[4]=77;}else{auto a=std::find_if(s.actors.begin(),s.actors.end(),[&](const SessionLevelActor& x){return x.spawn[0]==s.currentActor;});if(a==s.actors.end())return -4;e=s2_actor_mark_removed(a->pose(),s.currentActor,s.removed,4);q.row[4]=s.currentActor;}}
 else if(kind==22){
  auto source=std::find_if(s.actors.begin(),s.actors.end(),[&](const SessionLevelActor& a){return a.spawn[0]==s.currentActor;});if(source==s.actors.end()||!fetch(address,q.row+4,2,ctx))return -2;
  q.row[6]=source->reactions()[5];q.row[7]=s.currentActor;int saved=s.currentActor;int32_t packet[3]={q.row[4],q.row[5],q.row[6]};
  if(packet[0]==9&&packet[1]==2)for(auto& a:s.actors){if(a.spawn[1]==150){int total=int(std::count_if(s.actors.begin(),s.actors.end(),[](const SessionLevelActor& v){return v.spawn[1]==73;}));if(++a.subtype[0]>=total)a.subtype[1]=1;}if(a.spawn[1]==72&&(!packet[2]||packet[2]==a.spawn[6]))a.state[40]|=1;}
  // Source listener10F20 handles packet11/0 with state22 / motion25.
  if(source->spawn[1]==9&&packet[0]==11&&packet[1]==0){int32_t* h=s.playerType==3?s.state:nullptr;for(auto& p:s.party)if(p.type==3&&s.playerType!=3)h=p.state;if(h&&h[80]!=6&&h[80]!=12&&h[80]!=13&&h[80]!=14)e=s2_shrek_locomotion_enter(h,h+80,h+88,h+96,0x10022,0,s.tick,s.tick,0x0804b73c,nullptr,fetch,ctx);}
  for(auto& a:s.actors){if(e||!a.registered||(a.state[40]&1)||packet[0]!=9)continue;s.currentActor=a.spawn[0];if(spawnerType(a.spawn[1])&&packet[0]==9&&packet[1]==4){e=s2_spawner_notice(a.subtype,a.reactions()[5],packet);if(e>=0)e=0;}else e=s2_generic_event(a.pose(),a.vm(),a.reactions(),packet,s.tick,fetch,registry,ctx);if(e||s.error)break;}s.currentActor=saved;
 }else if(kind==23){
  auto source=std::find_if(s.actors.begin(),s.actors.end(),[&](const SessionLevelActor& a){return a.spawn[0]==s.currentActor;});if(source==s.actors.end())return -4;
  if(spawnerType(source->spawn[1])&&!s2_spawner_can_create(source->subtype))return 0;
  int32_t descriptor[5],xy[2];if(!fetch(address,descriptor,5,ctx))return -2;int type=spawnerType(source->spawn[1])&&source->subtype[6]?source->subtype[6]:descriptor[0];
  if(type!=67&&type!=68&&type!=69&&type!=146&&type!=71&&(!spawnerType(source->spawn[1])||type<53||type>62))return -4;e=s2_actor_spawn_point_q8(source->pose(),fetch,ctx,xy);if(e)return e;
  q.row[4]=type;q.row[5]=xy[0];q.row[6]=xy[1];q.row[7]=descriptor[1];
  if(type>=53&&type<=62){int id=reserve_spawn_id(s);if(id<0)return 0;SessionLevelActor a;int32_t row[8]={id,type,xy[0],xy[1],0,descriptor[1]&255,int32_t(uint32_t(source->reactions()[5])+1000u),int16_t(uint32_t(descriptor[4]))};std::copy_n(row,8,a.spawn);s.pending.push_back(a);e=s2_spawner_created(source->subtype);q.row[7]=id;}
  if(type==67||type==68||type==69||type==146){if(s.projectiles.size()>=256)return 0;SessionProjectile p;p.type=type;e=s2_projectile_init(s.collision.c_str(),type,xy,descriptor[1]&3,s.tick,fetch,sink,&s,p.pose,&p.deadline);if(e)return e;s.projectiles.push_back(p);}
  if(type==71){SessionSmoke puff;e=s2_smoke_runtime_init(s.collision.c_str(),xy,descriptor[1]&3,s.tick,fetch,ctx,puff.pose);if(e)return e;s.smoke.push_back(puff);}
 }else if(kind==26){
  if(s.dialogue[64])return 0;for(auto& a:s.actors)if(a.spawn[1]==149&&a.params[4]==int32_t(address))a.subtype[0]=1;uint32_t script;e=s2_dialogue_lookup(int32_t(address),fetch,ctx,&script);if(e)return e;
  e=s2_dialogue_start(script,s.dialogue);if(e)return e;s.dialogue[78]=int32_t(address);s.dialogueTick=0;s.dialogueHeld=s.book()[4];s.comboPhase=s.comboFrames=0;s.comboHeld=false;s.dialogueSerial=0;s.dialoguePage=0;s.dialogueLines.clear();
  e=s2_dialogue_step(s.dialogue,0,0,0,fetch,ctx);q.row[4]=int32_t(address);q.row[5]=int32_t(script);
 }else if(kind==24){
  if(address!=77&&address!=89&&address!=90&&!rewardType(int(address)))return -4;auto source=std::find_if(s.actors.begin(),s.actors.end(),[&](const SessionLevelActor& a){return a.spawn[0]==s.currentActor;});if(source==s.actors.end())return -4;
  int id=reserve_spawn_id(s);if(id<0)return 0;SessionLevelActor a;int32_t row[8]={id,int32_t(address),source->state[0],source->state[1],0,0,0,0};std::copy_n(row,8,a.spawn);s.pending.push_back(a);q.row[4]=int32_t(address);q.row[5]=row[2];q.row[6]=row[3];q.row[7]=row[0];
 }else if(kind==25){
  auto a=std::find_if(s.actors.begin(),s.actors.end(),[&](const SessionLevelActor& x){return x.spawn[0]==s.currentActor;});if(a==s.actors.end())return -4;
  a->auxiliary=false;std::fill_n(a->aux,80,0);q.row[4]=s.currentActor;
  if(address){int32_t xy[2];e=s2_actor_spawn_point_q8(a->pose(),fetch,ctx,xy);if(e)return e;e=s2_plain_runtime_init(xy,(a->state[38]&1)<<1,address,s.tick,fetch,ctx,a->aux);if(e)return e;a->auxiliary=true;}
 }else return -4;
 if(e)return e;s.requests.push_back(q);return 0;
}
struct SessionGenericReceiver{int32_t* vm;int32_t* reactions;Fetch fetch;void* ctx;};
static int genericReply(const int32_t* event,void* ctx){auto* r=static_cast<SessionGenericReceiver*>(ctx);return s2_generic_activate(r->vm,r->reactions,event);}
static int genericFetch(uint32_t a,int32_t* out,int n,void* ctx){auto* r=static_cast<SessionGenericReceiver*>(ctx);return r->fetch(a,out,n,r->ctx);}
static int s2_session_mushroom_mouse_contact(int32_t* source,int32_t* target,int32_t* vm,int32_t* reactions,Fetch f,void* ctx){SessionGenericReceiver r{vm,reactions,f,ctx};int32_t diag[8];return s2_generic_contact_pair_receiver(source,target,genericFetch,genericReply,&r,diag);}
extern "C" int s2_mouse_spawn_step(int32_t*,int);
extern "C" void s2_mouse_wrap(int32_t*);
static int dispatch(uint32_t id,const int32_t* event,void* ctx){auto& s=*static_cast<OwnedSession*>(ctx);int accepted;if(!s.level){if(id!=77)return -4;accepted=s2_generic_activate(s.vm(),s.reactions(),event);}else{auto a=std::find_if(s.actors.begin(),s.actors.end(),[&](const SessionLevelActor& x){return uint32_t(x.spawn[0])==id;});if(a==s.actors.end()||(a->state[40]&1))return -4;accepted=a->spawn[1]==74?s2_puss_boss_receive(a->pose(),a->subtype,event,a->spawn[6],s.tick,fetch,sink,&s):s2_generic_activate(a->vm(),a->reactions(),event);}return accepted<0?accepted:0;}
static int consumeKey(void* ctx){auto& s=*static_cast<OwnedSession*>(ctx);int id=s.extra()[3];auto a=std::find_if(s.actors.begin(),s.actors.end(),[&](const SessionLevelActor& a){return a.spawn[0]==id;});if(a==s.actors.end())return -4;const int32_t event[3]={0,11,0};int e=s2_shrek_carry_release(s.extra(),s.status(),s.tick,event,dispatch,ctx);return e?e:s2_actor_mark_removed(a->pose(),id,s.removed,4);}
static bool talkRange(OwnedSession& s){int32_t body[1020],targets[1020];int n=s2_actor_contact_rects(s.player(),0,fetch,&s,body,255);if(n<=0)return false;for(auto& a:s.actors){if(!npcType(a.spawn[1])||(a.state[40]&1)||a.state[42]!=30)continue;int k=s2_actor_contact_rects(a.pose(),1,fetch,&s,targets,255);for(int i=0;i<n;i++)for(int j=0;j<k;j++)if(s2_rect_overlap_xywh(body+i*4,targets+j*4))return true;}return false;}
static int reply(const int32_t* event,void* ctx){auto& s=*static_cast<OwnedSession*>(ctx);if((s.trainerFlags&1)&&((event[1]>=37&&event[1]<=41)||event[1]==31))return 0;if(s.bonus&&s.miniFailed)return 0;if(s.bonus&&(s.playerType==4||s.playerType==7)&&event[1]>=37&&event[1]<=41){int32_t hurt[3]={0,event[1]==41?38:event[1],event[2]};return s2_shrek_hurt_receive(s.player(),s.extra(),s.status(),s.book(),hurt,s.tick,s.tick,s.motionTable(),fetch,&s);}if(s.bonus&&((event[1]>=37&&event[1]<=41)||event[1]==31)){if(s.extra()[0]==6||s.status()[4]>s.tick)return 0;int e=sink(1,0x08024bbc,0,&s);return e?e:1;}if(s.level&&(s.extra()[0]==13||s.extra()[0]==14))return 0;if(s.level&&event[1]==31){if(s.extra()[1]==5||s.extra()[0]==6)return 0;s.deathReturning=true;return 1;}if(s.level&&event[1]==40){int e=(s.playerType!=3?s2_character_terminal_enter(s.motionTable(),14,s.player(),s.extra(),s.book(),s.tick,fetch,&s):s2_shrek_water_enter(s.player(),s.extra(),s.book(),s.tick,fetch,&s));if(e)return e;if(s.book()[6]){int released=sink(21,uint32_t(s.book()[6]),0,&s);if(released<0)return released;if(released)s.book()[6]=0;}s.comboPhase=s.comboFrames=0;s.comboHeld=false;return 1;}if(s.level&&event[1]==30&&s.playerType!=3){if(!(s.pressedButtons&2)||s.extra()[0]==6||s.extra()[0]==12)return 0;const int32_t idle[3]={1,7,0};int e=s2_shrek_locomotion_enter(s.player(),s.extra(),s.status(),s.book(),0x158,s.extra()[2],s.tick,s.tick,s.motionTable(),idle,fetch,&s);return e?e:1;}if(s.level&&event[1]==30)return s2_shrek_talk_receive(s.player(),s.extra(),s.status(),s.book(),s.pressedButtons,s.tick,fetch,&s);if(s.level&&event[1]==41&&s.extra()[1]!=7){if(s.extra()[0]==6||s.status()[4]>s.tick)return 0;int e=s.playerType==3?s2_shrek_fire_enter(s.player(),s.extra(),s.book(),s.tick,fetch,&s):s2_character_terminal_enter(s.motionTable(),15,s.player(),s.extra(),s.book(),s.tick,fetch,&s);return e?e:1;}if(s.level&&((event[1]>=37&&event[1]<=39)||(event[1]==41&&s.extra()[1]==7))){int carried=s.extra()[3],mode=s.extra()[1];bool bonusCarry=carried&&(mode==5||mode==7);int32_t damage[3]={event[0],event[1]==41?38:event[1],event[2]};if(bonusCarry){s.extra()[3]=0;if(mode==7)damage[0]=0;}
 if(s.playerType==6&&carried&&!bonusCarry&&s.extra()[0]!=6&&s.status()[4]<=s.tick){const int32_t detach[3]={0,11,0};int e=s2_shrek_carry_release(s.extra(),s.status(),s.tick,detach,dispatch,&s);if(e)return e;}int accepted=s2_shrek_hurt_receive(s.player(),s.extra(),s.status(),s.book(),damage,s.tick,s.tick,s.motionTable(),fetch,&s);
 if(bonusCarry){s.extra()[3]=carried;if(accepted>0){const int32_t detach[3]={0,11,0};int e=s2_shrek_carry_release(s.extra(),s.status(),s.tick,detach,dispatch,&s);if(e)return e;auto a=std::find_if(s.actors.begin(),s.actors.end(),[&](const SessionLevelActor& v){return v.spawn[0]==carried;});if(a==s.actors.end())return -4;e=s2_actor_mark_removed(a->pose(),carried,s.removed,4);if(e)return e;}}if(accepted>0&&s.book()[6]){int released=sink(21,uint32_t(s.book()[6]),0,&s);if(released<0)return released;if(released)s.book()[6]=0;}return accepted;}if(s.level&&event[1]==24){int32_t heal[3]={0,22,0};return s2_shrek_receive(s.extra(),s.status(),heal,s.tick);}if(s.level&&event[1]==32)return s2_shrek_coin_receive(s.extra(),event,&s.coins,sink,&s);if(s.level&&event[1]==28){int clear=0;if(s.extra()[0]==20||(s.extra()[0]!=6&&s.player()[11]>0&&!s.player()[62])){int w=(s.player()[30]&255)*256,h=(s.player()[31]&255)*256;int32_t x=int32_t(uint32_t(s.player()[0])-uint32_t(w/2)),y=int32_t(uint32_t(s.player()[1])-uint32_t(h/2)-256u);int hit=s2_actor_probe_file(s.collision.c_str(),5,x,y,w,h,s.surfaces,s.surfaceCount);if(hit<0)return hit;clear=hit==0;}int accepted=(s.playerType!=3?s2_shrek_bounce_receive:s2_shrek_scene_bounce_receive)(s.player(),s.extra(),s.status(),s.book(),event,s.tick,s.tick,s.motionTable(),clear,fetch,&s);if(accepted>0&&s.book()[6]){int released=sink(21,uint32_t(s.book()[6]),0,&s);if(released<0)return released;if(released)s.book()[6]=0;}return accepted;}return s2_shrek_receive(s.extra(),s.status(),event,s.tick);}
static bool load(OwnedSession& s,const char* path){
 std::ifstream f(path,std::ios::binary|std::ios::ate);if(!f)return false;auto length=f.tellg();if(length<16||length>64*1024*1024)return false;f.seekg(0);s.bytes.resize(size_t(length));if(!f.read(reinterpret_cast<char*>(s.bytes.data()),length))return false;
 auto* p=s.bytes.data();if(std::memcmp(p,"S2PK",4)||word(p+4)!=1)return false;uint32_t blocks=word(p+8),animations=word(p+12);if(blocks>20000||animations>4096)return false;size_t at=16;
 auto available=[&](size_t n){return at<=s.bytes.size()&&n<=s.bytes.size()-at;};
 for(uint32_t i=0;i<blocks;i++){if(!available(8))return false;uint32_t addr=word(p+at),n=word(p+at+4);at+=8;if(!available(n)||uint64_t(addr)+n>0x100000000ull)return false;s.blocks.push_back({addr,at,n});at+=n;}
 for(uint32_t i=0;i<animations;i++){if(!available(12))return false;uint32_t addr=word(p+at),index=word(p+at+4),n=word(p+at+8);at+=12;if(n==0||n>256||!available(n))return false;std::string name(reinterpret_cast<char*>(p+at),n);at+=n;if(name.front()=='/'||name.find("..")!=std::string::npos||name.find_first_not_of("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_./")!=std::string::npos)return false;s.animationLookup.emplace(addr,s.animations.size());s.animations.push_back({addr,index,name});}
 return at==s.bytes.size();
}
// Immutable resource caches; excluded from quick states and moved with the scene.
static SessionAnimation* animationFor(OwnedSession&s,uint32_t address){auto i=s.animationLookup.find(address);return i==s.animationLookup.end()?nullptr:&s.animations[i->second];}
static void* bankFor(OwnedSession&s,SessionAnimation&a){if(a.bank)return a.bank;std::string path=s.sprites+"/"+a.path;auto bank=s.spriteBanks.find(path);if(bank==s.spriteBanks.end()){std::unique_ptr<void,SessionBankDeleter> loaded(s2_sprite_bank_create(path.c_str()));if(!loaded)return nullptr;bank=s.spriteBanks.emplace(std::move(path),std::move(loaded)).first;}return a.bank=bank->second.get();}
extern "C" int s2_camera_follow_step(int32_t*,const int32_t*);
// Joint input and framing are independent. An entirely offscreen partner
// stops anchoring the camera until the group comes back into view.
static bool partyVisible(const OwnedSession& s){if(s.party.size()<2)return false;for(size_t i=0;i<s.party.size();i++){const auto* h=int(i)==s.partyIndex?s.state:s.party[i].state;int64_t x=h[0],y=h[1],hw=h[30]*128,hh=h[31]*128;if(x+hw<=s.cameraX*256||x-hw>=(s.cameraX+s.width)*256||y+hh<=s.cameraY*256||y-hh>=(s.cameraY+160)*256)return false;}return true;}
static bool sharedCamera(const OwnedSession& s){return s.jointControl&&partyVisible(s);}
static void cameraFocusTarget(const OwnedSession& s,int32_t* target){
 int64_t x=s.state[0],feet=int64_t(s.state[1])+s.state[31]*128;int n=1;
 if(sharedCamera(s))for(size_t i=0;i<s.party.size();i++)if(int(i)!=s.partyIndex){auto* p=s.party[i].state;x+=p[0];feet+=int64_t(p[1])+p[31]*128;++n;}
 target[0]=int32_t(x/n);target[1]=int32_t(feet/n)-40*256;
}
static int cameraRight(const OwnedSession& s){return s.sceneId==1&&s.decodedScene?std::min(std::max(0,s.worldWidth-s.width),s2_scene_camera_right(s.decodedScene.get(),s.width)):std::max(0,s.worldWidth-s.width);}
static int cameraBottom(const OwnedSession& s){int bottom=std::max(0,s.worldHeight-160-((s.sceneId==8||s.sceneId==23)?8:0));return (s.sceneId==21||s.sceneId==11)&&s.decodedScene?std::min(bottom,s2_scene_camera_bottom(s.decodedScene.get(),160)):bottom;}
static int timedSeconds(int scene){return scene==21?115:scene==22?120:scene==20?30:scene==16?45:0;}
static void projectPartyCamera(OwnedSession& s){s.cameraX=std::clamp((s.cameraFocus[0]>>8)-s.width/2,0,cameraRight(s));s.cameraY=std::clamp((s.cameraFocus[1]>>8)-80,0,cameraBottom(s));}
static void cameraTarget(const OwnedSession& s,int& x,int& y){
 const int32_t* h=s.state;int64_t px=h[0],feet=int64_t(h[1])+h[31]*128;int n=1;
 if(sharedCamera(s))for(size_t i=0;i<s.party.size();i++)if(int(i)!=s.partyIndex){const auto* p=s.party[i].state;px+=p[0];feet+=int64_t(p[1])+p[31]*128;++n;}
 x=std::clamp(int(px/n/256)-s.width/2,0,cameraRight(s));y=std::clamp(s.party.size()>1?int(feet/n/256)-120:(h[1]>>8)-95,0,cameraBottom(s));
}
static void beginCameraSwitch(OwnedSession& s){int32_t target[2];cameraFocusTarget(s,target);s.cameraBlend=int(std::max((std::abs(int64_t(target[0])-s.cameraFocus[0])+1279)/1280,(std::abs(int64_t(target[1])-s.cameraFocus[1])+1791)/1792));}
static int activateHeroSound(OwnedSession& s,int type){if(type<3||type>7)return 0;return sink(11,type==4?0x08053e58:type==5?0x08053dd4:type==6?0x08053d5c:0x08053cf0,256,&s);}

static int initPartners(OwnedSession& s){s.partyHeld=0;s.jointControl=false;s.cameraBlend=0;s.cameraX=std::clamp((s.player()[0]>>8)-s.width/2,0,cameraRight(s));s.cameraY=std::clamp((s.player()[1]>>8)-95,0,cameraBottom(s));for(size_t i=0;i<s.party.size();i++){auto& p=s.party[i];p.rawButtons=0;p.contextB=false;if(int(i)==s.partyIndex){std::copy_n(s.state,320,p.state);continue;}std::fill_n(p.state,320,0);int32_t xy[2]={p.spawn[2],p.spawn[3]};int e=s2_generic_runtime_init(xy,p.spawn[5]&3,heroAnimation(p.type),0,fetch,&s,p.state);if(e)return e;int32_t header[6];if(!fetch(heroHealth(p.type),header,6,&s))return -2;e=s2_shrek_reactions_init(p.state,p.state+80,p.state+88,(uint32_t(header[5])>>8)&255,0);if(e)return e;p.state[40]|=6;if(p.type==6||p.type==7)p.state[90]=1;int32_t event[3]={1,7,0};e=s2_shrek_locomotion_enter(p.state,p.state+80,p.state+88,p.state+96,0x158,0,0,0,heroTable(p.type),event,fetch,&s);if(e)return e;}cameraFocusTarget(s,s.cameraFocus);projectPartyCamera(s);return 0;}
static void switchPartner(OwnedSession& s,int buttons){
 // Parent control state and activation audio stay frozen during child worlds
 // and their entry/return fades, just like the parent simulation.
 if(s.mini||s.miniPending||s.miniReturning)return;
 // A single shoulder gesture commits only when both shoulders are released.
 // Bit10 remembers an L+R chord until its final release; staggered Android
 // pointer/key events therefore cannot insert an extra single-character switch.
 constexpr int chordFlag=1024;int selection=buttons&768,previous=s.partyHeld&768;
 bool chord=(s.partyHeld&chordFlag)||previous==768||selection==768;
 bool singleRelease=previous!=0&&selection==0&&!chord;
 s.partyHeld=selection|((selection&&chord)?chordFlag:0);
 bool wasJoint=s.jointControl;s.jointControl=selection&&chord&&partyVisible(s);
 if(s.party.size()>1&&wasJoint!=s.jointControl){beginCameraSwitch(s);if(s.jointControl&&!s.dialogue[64])for(size_t i=0;i<s.party.size();i++)if(int(i)!=s.partyIndex){int e=activateHeroSound(s,s.party[i].type);if(e)s.error=e;}}
 if(s.party.size()<2||s.jointControl||((s.extra()[0]>=13&&s.extra()[0]<=15)||(s.extra()[0]==12&&s.levelEnding))||(s.player()[40]&1)||s.dialogue[64]||s.mini||!singleRelease)return;
 // Both shoulder buttons cycle forward; neither names a particular hero.
 int target=(s.partyIndex+1)%int(s.party.size());
 if(target==s.partyIndex)return;std::copy_n(s.state,320,s.party[s.partyIndex].state);s.party[s.partyIndex].rawButtons=s.rawButtons;s.party[s.partyIndex].contextB=s.contextB;s.partyIndex=target;auto& p=s.party[target];s.rawButtons=p.rawButtons;s.contextB=p.contextB;std::copy_n(p.state,320,s.state);std::copy_n(p.spawn,8,s.playerSpawn);s.playerType=p.type;s.book()[2]=s.tick;s.comboPhase=s.comboFrames=0;s.comboHeld=false;if(!wasJoint){int e=activateHeroSound(s,s.playerType);if(e)s.error=e;}beginCameraSwitch(s);
}
// Focus/menu/lifecycle cancellation is not a physical shoulder release.
extern "C" void s2_session_cancel_shoulders(void*h){if(!h)return;auto&s=*static_cast<OwnedSession*>(h);s.partyHeld=0;if(s.jointControl){s.jointControl=false;beginCameraSwitch(s);}}
extern "C" int s2_session_reset(void* handle){
 if(!handle)return -1;auto& s=*static_cast<OwnedSession*>(handle);std::fill_n(s.fairyMarkers,8,0);s.forceBossDrop=false;s.previousRender.clear();s.renderKeys.clear();s.cameraReady=s.historyReady=s.displayCaptured=false;s.nextRenderId=1;s.mini.reset();s.deathReturning=s.finishStarted=s.finishDone=false;std::fill_n(s.finishHeroDone,3,false);std::fill_n(s.finishWaiting,3,false);s.mosaic=s.contextB=false;s.rawButtons=0;s.miniReturning=s.levelEnding=s.levelComplete=false;s.fade[0]=s.fades?64:0;s.fade[1]=0;s.presentationTick=s.lastBonusScore=s.rewardCount=0;std::fill_n(s.rewardTypes,4,0);s.bonusUnavailable=s.introDialogue=false;s.balanceRandomState=1;s.miniPending=s.miniFailed=false;s.miniCursor=0;std::fill_n(s.mouseSpawner,2,0);std::fill_n(s.state,320,0);s.tick=s.sounds=s.error=0;s.requests.clear();s.smoke.clear();s.projectiles.clear();std::fill_n(s.dialogue,80,0);s.dialogueTick=s.dialogueHeld=s.dialogueSerial=s.dialoguePage=s.blockedButtons=s.pressedButtons=0;s.dialogueLines.clear();std::fill_n(s.effects,9,0);std::fill_n(s.removed,4,0);
 s.actors.erase(std::remove_if(s.actors.begin(),s.actors.end(),[&](const SessionLevelActor& a){return a.spawn[0]>s.rowCount;}),s.actors.end());s.pending.clear();s.nextSpawnId=s.rowCount+1;s.coinTarget=40-int(std::count_if(s.actors.begin(),s.actors.end(),[](auto&a){return a.editorDeleted&&a.spawn[1]==89;}));
 s.specialDeadline=(timedSeconds(s.sceneId)?timedSeconds(s.sceneId):30)*60;s.currentActor=0;s.coins=0;s.surfaceCount=0;s.comboPhase=0;s.comboFrames=0;s.comboHeld=false;int32_t playerXY[2]={s.level?s.playerSpawn[2]:123*256,s.level?s.playerSpawn[3]:349*256},itemXY[2]={120*256,340*256};int e=s2_generic_runtime_init(playerXY,s.level?(s.playerSpawn[5]&3):0,(heroAnimation(s.playerType)),0,fetch,&s,s.player());if(e)return e;
 if(!s.level){e=s2_generic_runtime_init(itemXY,0,0x08342dcc,0,fetch,&s,s.item());if(e)return e;s2_vm_start(0x0804d084,s.vm());}
 else for(auto& actor:s.actors){actor.registered=false;actor.auxiliary=false;actor.spawnSettled=false;std::fill_n(actor.subtype,8,0);if(spawnerType(actor.spawn[1])){e=s2_spawner_init(actor.params,actor.subtype);if(e)return e;}std::fill_n(actor.aux,80,0);std::fill_n(actor.state,216,0);if(actor.editorDeleted){actor.state[40]=1;continue;}int32_t xy[2]={actor.spawn[2],actor.spawn[3]};if(actor.spawn[1]==144){e=s2_target_generator_init(xy,actor.spawn[5]&1,actor.pose(),actor.subtype);actor.registered=(actor.spawn[5]&1)!=0;if(e)return e;continue;}if(actor.spawn[1]==74){e=s2_puss_boss_init(xy,fetch,&s,actor.pose(),actor.subtype);if(e)return e;continue;}if(actor.spawn[1]==153){int index=actor.spawn[6];if(index>=0&&index<4){s.fairyMarkers[index*2]=xy[0];s.fairyMarkers[index*2+1]=xy[1];}continue;}if(actor.spawn[1]==156){e=s2_fairy156_init(xy,fetch,&s,actor.pose(),actor.subtype,actor.aux);if(e)return e;continue;}if(actor.spawn[1]==155){e=s2_fairy155_init(xy,fetch,&s,actor.pose(),actor.subtype);if(e)return e;continue;}if(actor.spawn[1]==154){e=s2_cake_init(xy,fetch,&s,actor.pose(),actor.aux,actor.subtype);if(e)return e;actor.auxiliary=true;continue;}if(actor.spawn[1]==149||actor.spawn[1]==150){e=s2_dialogue_trigger_init(xy,fetch,&s,actor.pose());if(e)return e;continue;}if(actor.spawn[1]==152){actor.state[0]=xy[0];actor.state[1]=xy[1];continue;}if(actor.spawn[1]==148){actor.state[0]=xy[0];actor.state[1]=xy[1];actor.state[30]=64;actor.state[31]=128;continue;}if(actor.spawn[1]==139){e=s2_puss_gate_init(xy,actor.spawn[5]&3,0,fetch,&s,actor.pose(),actor.subtype);if(e)return e;continue;}if(markerType(actor.spawn[1])){actor.state[0]=xy[0];actor.state[1]=xy[1];actor.state[30]=actor.state[31]=16;actor.state[42]=actor.spawn[1]-30;continue;}if(slopeType(actor.spawn[1])){e=s2_slope_runtime_init(xy,actor.spawn[5]&3,actor.spawn[1]==23?0x08024ab8:0x08024ac4,0,fetch,&s,actor.pose(),actor.vm());if(e)return e;s2_reactions_init(actor.spawn[6],actor.reactions());continue;}if(actor.spawn[1]==151){e=s2_dialogue_trigger_init(xy,fetch,&s,actor.pose());if(e)return e;continue;}e=(ambientType(actor.spawn[1])?s2_plain_runtime_init:s2_generic_runtime_init)(xy,actor.spawn[5]&3,actorAnimation(actor.spawn[1]),0,fetch,&s,actor.pose());if(e)return e;if(actor.spawn[1]==72){actor.state[40]=8;const int32_t ev[3]={1,31,0};std::copy_n(ev,3,actor.state+41);}if(ambientType(actor.spawn[1]))continue;actor.state[79]=actor.spawn[7];s2_reactions_init(actor.spawn[6],actor.reactions());s2_vm_start(actorScript(actor.spawn[1]),actor.vm());if(actor.spawn[1]==138)actor.state[6]=25;if(plateType(actor.spawn[1])||pushBlock(actor.spawn[1])){actor.state[39]=3;actor.state[40]|=6;actor.state[36]=actor.state[0];actor.state[37]=actor.state[1];if(plateType(actor.spawn[1]))actor.state[21]=2;else{const int32_t x[3]={0,51,0},y[3]={256,49,1792};s2_apply_axis_triple(actor.pose()+2,x,0,0);s2_apply_axis_triple(actor.pose()+2,y,1,0);}}if(npcType(actor.spawn[1])){e=s2_plain_runtime_init(xy,0,0x0833d79c,0,fetch,&s,actor.aux);if(e)return e;}}
 int32_t healthHeader[6];if(!fetch(heroHealth(s.playerType),healthHeader,6,&s))return -2;int lifeCount=s.level?int((uint32_t(healthHeader[5])>>8)&255):4;e=s2_shrek_reactions_init(s.player(),s.extra(),s.status(),lifeCount,0);if(e)return e;s.player()[40]|=s.level?6:2;if(s.playerType==6||s.playerType==7)s.status()[2]=1;int32_t event[3]={1,7,0};e=s2_shrek_locomotion_enter(s.player(),s.extra(),s.status(),s.book(),0x158,0,0,0,s.motionTable(),event,fetch,&s);return e?e:initPartners(s);
}
extern "C" void* s2_session_create(const char* package,const char* scene,const char* collision,const char* sprites,int32_t* error){
 if(error)*error=-1;if(!package||!scene||!collision||!sprites)return nullptr;auto s=std::make_unique<OwnedSession>();s->package=package;s->scene=scene;s->collision=collision;s->sprites=sprites;int32_t dimensions[2];if(s2_scene_dimensions_file(scene,dimensions)){if(error)*error=-2;return nullptr;}s->worldWidth=dimensions[0];s->worldHeight=dimensions[1];s->decodedScene.reset(s2_scene_create(scene));s->decodedCollision.reset(s2_collision_create(collision));if(!s->decodedScene||!s->decodedCollision){if(error)*error=-2;return nullptr;}if(!load(*s,package)){if(error)*error=-2;return nullptr;}int e=s2_session_reset(s.get());if(error)*error=e;if(e)return nullptr;return s.release();
}
extern "C" void s2_session_destroy(void* s){delete static_cast<OwnedSession*>(s);}
extern "C" void* s2_session_create_level(const char* package,const char* scene,const char* collision,const char* sprites,const char* objects,int32_t* error){
 if(error)*error=-1;if(!objects)return nullptr;auto s=std::unique_ptr<OwnedSession>(static_cast<OwnedSession*>(s2_session_create(package,scene,collision,sprites,error)));if(!s)return nullptr;
 std::ifstream objectFile(objects,std::ios::binary);uint8_t objectHeader[16]={};if(!objectFile.read(reinterpret_cast<char*>(objectHeader),16)){if(error)*error=-2;return nullptr;}s->sceneId=int(word(objectHeader+12));
 int32_t rows[128*8];int n=s2_scene_spawn_plan_file(objects,nullptr,0,rows,128);if(n<1||n>127){if(error)*error=-2;return nullptr;}s->level=true;s->bonus=(n==3&&rows[1]==16&&rows[9]==141&&rows[17]==3)||(s->sceneId==7&&n==2&&rows[1]==6&&rows[9]==138)||(s->sceneId==6&&n==4&&rows[9]==147&&rows[17]==139&&rows[25]==4)||(s->sceneId==18&&n==3)||(s->sceneId==27&&n==5);s->objects=objects;s->rowCount=n;s->actors.reserve(128);int players=0;
 for(int i=0;i<n;i++){auto* row=rows+i*8;if(row[1]>=3&&row[1]<=7){std::copy_n(row,8,s->playerSpawn);s->playerType=row[1];SessionPartner partner;partner.type=row[1];std::copy_n(row,8,partner.spawn);s->party.push_back(partner);s->partyIndex=players++;}else if(s->bonus&&row[1]==141){std::copy_n(row+2,2,s->mouseSpawner);}else if((s->bonus&&(row[1]==144||row[1]==145||row[1]==11||row[1]==138||row[1]==139||row[1]==147||markerType(row[1])))||rewardType(row[1])||row[1]==148||row[1]==74||row[1]==153||fairyType(row[1])||row[1]==154||specialExit(row[1])||row[1]==39||row[1]==18||row[1]==89||row[1]==10||row[1]==14||row[1]==16||row[1]==53||row[1]==57||spawnerType(row[1])||ambientType(row[1])||npcType(row[1])||row[1]==151||markerType(row[1])||(s->sceneId!=0&&storyScene(s->sceneId)&&(extraBinding(row[1])||markerType(row[1])||slopeType(row[1])))){SessionLevelActor a;std::copy_n(row,8,a.spawn);if((spawnerType(row[1])||specialExit(row[1]))&&s2_scene_object_params_file(objects,row[0],a.params)){if(error)*error=-2;return nullptr;}s->actors.push_back(a);}}
 if((players<1||players>3)||(!storyScene(s->sceneId)&&!s->bonus)||(!s->bonus&&s->actors.size()!=size_t(n-players))||(s->bonus&&s->actors.size()!=size_t(s->playerType==7?4:s->playerType==5?2:s->playerType==4?3:1))){if(error)*error=-4;return nullptr;}int e=s2_session_reset(s.get());if(error)*error=e;if(e)return nullptr;return s.release();
}
extern "C" int s2_session_world_size(void* h,int32_t* out){if(!h||!out)return -1;auto& s=*static_cast<OwnedSession*>(h);out[0]=s.worldWidth;out[1]=s.worldHeight;return 0;}
extern "C" int s2_session_world_info(void* handle,int32_t* out){if(!handle||!out)return -1;auto& s=*static_cast<OwnedSession*>(handle);int sourceCount=int(std::count_if(s.actors.begin(),s.actors.end(),[&](const SessionLevelActor& a){return a.spawn[0]<=s.rowCount;}));int32_t info[4]={s.rowCount,sourceCount,s.level?s.rowCount-sourceCount-int(s.party.size()):0,s.playerSpawn[0]};std::copy_n(info,4,out);return 0;}
extern "C" int s2_session_actor_snapshot(void* handle,int id,int32_t* out){if(!handle||!out)return -1;auto& s=*static_cast<OwnedSession*>(handle);auto a=std::find_if(s.actors.begin(),s.actors.end(),[&](const SessionLevelActor& x){return x.spawn[0]==id;});if(a==s.actors.end())return -2;std::copy_n(a->state,216,out);return 0;}
extern "C" int s2_session_party_snapshot(void* h,int type,int32_t* out){if(!h||!out)return -1;auto& s=*static_cast<OwnedSession*>(h);if(type==s.playerType){std::copy_n(s.state,320,out);return 0;}for(auto& p:s.party)if(p.type==type){std::copy_n(p.state,320,out);return 0;}return -2;}
extern "C" int s2_session_camera_snapshot(void* h,int32_t* out){if(!h||!out)return -1;auto& s=*static_cast<OwnedSession*>(h);int x=s.cameraX,y=s.cameraY;if(s.party.size()<2)cameraTarget(s,x,y);out[0]=x;out[1]=y;out[2]=s.cameraBlend;out[3]=s.jointControl;return 0;}
extern "C" int s2_session_set_viewport(void* handle,int width,int height){if(!handle||width<240||width>640||height!=160)return -1;auto& s=*static_cast<OwnedSession*>(handle);bool changed=s.width!=width||s.height!=height;s.width=width;s.height=height;if(changed){s.cameraReady=s.historyReady=false;}if(changed&&s.party.size()>1){s.cameraBlend=0;projectPartyCamera(s);}return 0;}
extern "C" int s2_session_snapshot(void* handle,int32_t* out){if(!handle||!out)return -1;std::copy_n(static_cast<OwnedSession*>(handle)->state,320,out);return 0;}
// During partner updates s.state temporarily contains that partner. Inspect the
// current pose first, then the synchronized stored poses of the other heroes.
static const int32_t* liftedOwner(const OwnedSession&s,int id){if(s.state[102]==id)return s.state;for(auto&p:s.party)if(p.type!=s.playerType&&p.state[102]==id)return p.state;return nullptr;}
// Sort heroes and movable props by their interpolated vertical base, rather than
// changing a whole prop's layer when its collision box touches another prop.
// Hints are always underneath this group, and held props use the same rule.
static int propDepth(const OwnedSession&s,const int32_t*p,int alpha){
 int y=p[1];if(s.historyReady&&alpha<256){auto k=std::find_if(s.renderKeys.begin(),s.renderKeys.end(),[&](auto&k){return k.first==p;});if(k!=s.renderKeys.end()){auto old=std::find_if(s.previousRender.begin(),s.previousRender.end(),[&](auto&v){return v.key==k->second;});if(old!=s.previousRender.end()&&old->visible)y=interpolateCoordinate(old->y,y,alpha,64*256);}}
 bool hero=p==s.state;for(size_t i=0;i<s.party.size()&&!hero;i++)if(int(i)!=s.partyIndex&&p==s.party[i].state)hero=true;
 int depth=y+p[31]*128-(hero?256:0);
 if(!hero)for(auto&a:s.actors)if(a.state==p){if(auto*owner=liftedOwner(s,a.spawn[0]))return std::max(depth,propDepth(s,owner,alpha)+512);break;}
 return depth;
}
static int render(OwnedSession& s,uint32_t* out,bool terrainOnly=false,int alpha=256,bool presentationOnly=false,const int* editorCamera=nullptr){
 int w=s.width,h=s.height,half=w/2;size_t pixels=size_t(w)*h;
 int cx=std::clamp((s.player()[0]>>8)-half,0,cameraRight(s)),cy=std::clamp((s.player()[1]>>8)-95,0,cameraBottom(s));if(s.party.size()>1){cx=s.cameraX;cy=s.cameraY;}int32_t base[2]={(cx+half)*256,(cy+80)*256},bounds[4]={half*256,80*256,(cameraRight(s)+half)*256,(cameraBottom(s)+80)*256},position[2]={base[0],base[1]};int cameraCode=1;if(!presentationOnly)cameraCode=s2_camera_effect_step(s.effects,base,bounds,position);else if(s.cameraReady){position[0]=(s.lastRenderX+half)*256;position[1]=(s.lastRenderY+80)*256;}if(cameraCode<0)return cameraCode;cx=(position[0]>>8)-half;cy=(position[1]>>8)-80;if(!presentationOnly){s.lastRenderX=cx;s.lastRenderY=cy;s.cameraReady=true;}if(presentationOnly&&s.historyReady&&alpha<256){cx=interpolateCoordinate(s.previousRenderX,cx,alpha,96);cy=interpolateCoordinate(s.previousRenderY,cy,alpha,96);renderKeys(s);}if(editorCamera){cx=editorCamera[0];cy=editorCamera[1];}if(s.deferRender){if(s.dialogue[64]&&s.dialogueSerial!=s.dialogue[67]){int e=s2_dialogue_lines(uint32_t(s.dialogue[66]),fetch,&s,s.dialogueLines);if(e)return e;s.dialogueSerial=s.dialogue[67];s.dialoguePage=0;}return 0;}int e=(editorCamera?s2_scene_render_editor:s2_scene_render)(s.decodedScene.get(),cx,cy,w,h,out,pixels);if(e)return e;
 if(terrainOnly){if(!s.bonus){e=s2_scene_composite_front(s.decodedScene.get(),cx,cy,w,h,out,pixels);if(e)return e;}return 0;}
 // World hints/NPCs/decor remain behind all heroes, including the inactive partner.
 // Enemy bodies and attached props retain their foreground layer.
 auto& visible=s.drawActors;auto& front=s.drawFront;auto& depth=s.drawDepth;visible.clear();front.clear();depth.clear();if(!s.level)front.push_back(s.item());else for(auto& a:s.actors){bool carried=a.spawn[0]==s.extra()[3];for(size_t i=0;i<s.party.size();i++)if(int(i)!=s.partyIndex&&(a.spawn[0]==s.party[i].state[83]||a.spawn[0]==s.party[i].state[102]))carried=true;bool foreground=(a.spawn[1]==89||a.spawn[1]==90)||a.spawn[1]==16||a.spawn[1]==17||(a.spawn[1]>=52&&a.spawn[1]<=62)||(spawnerType(a.spawn[1])&&a.spawn[1]!=45)||a.spawn[1]==74||a.spawn[1]==140||a.spawn[1]==76||a.spawn[1]==78||a.spawn[0]==s.book()[6]||carried;if(a.spawn[1]>=76&&a.spawn[1]<=82)foreground=true;auto& layer=(a.spawn[1]>=13&&a.spawn[1]<=15)?depth:foreground?front:visible;if(a.spawn[1]!=144&&a.spawn[1]!=153&&a.spawn[1]!=151&&a.spawn[1]!=148&&!specialExit(a.spawn[1])&&!markerType(a.spawn[1]))layer.push_back(a.pose());if(a.auxiliary&&!(a.state[40]&1))layer.push_back(a.aux);}
 for(size_t i=0;i<s.party.size();i++)if(int(i)!=s.partyIndex)depth.push_back(s.party[i].state);
 depth.push_back(s.player());int depthAlpha=presentationOnly&&s.historyReady?alpha:256;
 std::sort(depth.begin(),depth.end(),[&](const int32_t*a,const int32_t*b){int da=propDepth(s,a,depthAlpha),db=propDepth(s,b,depthAlpha);return da!=db?da<db:std::less<const int32_t*>{}(a,b);});
 visible.insert(visible.end(),depth.begin(),depth.end());visible.insert(visible.end(),front.begin(),front.end());for(auto& puff:s.smoke)visible.push_back(puff.pose);for(auto& p:s.projectiles)visible.push_back(p.pose);
 for(auto* actor:visible){
  if(actor[40]&1)continue;
  // Original 18328 skips sprite submission while byte +1C8 is set.
  // Carry mode5 toggles that byte once per simulation update (D5BE).
  bool hero=actor==s.player();for(size_t i=0;i<s.party.size()&&!hero;i++)if(int(i)!=s.partyIndex&&actor==s.party[i].state)hero=true;
  if(hero&&(actor[93]&255)&&!editorCamera)continue;
  auto* a=animationFor(s,uint32_t(actor[47]));if(!a)return -2;int32_t anchor[2];s2_actor_anchor_q8(actor+72,actor,actor[18],actor[38],anchor);if(presentationOnly&&s.historyReady&&alpha<256){auto key=std::find_if(s.renderKeys.begin(),s.renderKeys.end(),[&](auto&k){return k.first==actor;});if(key!=s.renderKeys.end()){auto before=std::find_if(s.previousRender.begin(),s.previousRender.end(),[&](auto&p){return p.key==key->second;});if(before!=s.previousRender.end()&&before->visible){anchor[0]+=interpolateCoordinate(before->x,actor[0],alpha,64*256)-actor[0];anchor[1]+=interpolateCoordinate(before->y,actor[1],alpha,64*256)-actor[1];}}}
  void* bank=bankFor(s,*a);if(!bank)return -2;
  int actorHero=actor==s.player()?s.playerType:0;for(size_t i=0;i<s.party.size();i++)if(int(i)!=s.partyIndex&&actor==s.party[i].state)actorHero=s.party[i].type;
  int palette=-1;if(actorHero&&s.level){int32_t duration;if(!fetch(0x0804b6e4,&duration,1,&s))return -2;int start=actor[92]-duration;if(actor[92]>s.tick&&s.tick>=start&&s.tick<start+4){auto red=std::find_if(s.animations.begin(),s.animations.end(),[&](const SessionAnimation& v){return v.address==(actorHero==4?0x08344d24u:actorHero==5?0x0833746cu:actorHero==6?0x08330034u:actorHero==7?0x08355cdcu:0x0834f43cu)&&v.path==a->path;});if(red==s.animations.end())return -2;palette=int(red->index);}}
  e=s2_sprite_composite_bank_palette(bank,int(a->index),actor[22],actor[18],w,h,(anchor[0]>>8)-cx,(anchor[1]>>8)-cy,out,pixels,palette);if(e)return e;
 }
 if(!s.bonus){e=s2_scene_composite_front(s.decodedScene.get(),cx,cy,w,h,out,pixels);if(e)return e;}
 if(editorCamera)return 0;
 auto drawUI=[&](uint32_t address,int frame,int x,int y,bool centered=true)->int{auto* a=animationFor(s,address);if(!a)return -2;void* bank=bankFor(s,*a);if(!bank)return -2;return s2_sprite_composite_bank(bank,int(a->index),frame,0,w,h,x+(centered?(w-240)/2:0),y,out,pixels);};
 if(s.level&&!s.bonus&&!s.dialogue[64]){auto drawHeroHUD=[&](int type,const int32_t* state,int x,bool active){uint32_t icon=heroIcon(type);int code=drawUI(icon+(active?0u:24u),0,x,4,false);if(code)return code;return drawUI(heroHealth(type),std::clamp(state[89],0,type==3||type==7?6:type==5?3:4),x,4,false);};if(s.party.size()>1){int x=4;for(int type:{6,3,4,5,7})for(size_t i=0;i<s.party.size();i++)if(s.party[i].type==type){const auto* pose=int(i)==s.partyIndex?s.state:s.party[i].state;e=drawHeroHUD(type,pose,x,sharedCamera(s)||int(i)==s.partyIndex);if(e)return e;x+=28;}}else{e=drawHeroHUD(s.playerType,s.state,4,true);if(e)return e;}bool timed=s.sceneId==20||s.sceneId==16;int32_t coinHeader[6];if(!fetch(0x0832eb84,coinHeader,6,&s))return -2;int period=(coinHeader[5]&255)+1,frames=(uint32_t(coinHeader[5])>>8)&255;if(!frames)return -2;if(!timed)e=drawUI(0x0832eb84,((presentationOnly&&s.displayCaptured?s.drawTick:s.presentationTick)/period)%frames,w-9,12,false);if(e)return e;std::string counter=timed?std::to_string((std::max(0,s.specialDeadline-s.tick)+59)/60):std::to_string(s.coins)+"/"+std::to_string(s.coinTarget);int labelWidth=s2_dialogue_label_width(counter,fetch,&s);if(labelWidth<0)return labelWidth;e=s2_dialogue_draw_label(counter,w-20-labelWidth,4,w,out,fetch,&s);if(e)return e;}
 if((s.sceneId==21||s.sceneId==22)&&!s.dialogue[64]){int seconds=(std::max(0,s.specialDeadline-s.tick)+59)/60;std::string label=(seconds/60<10?"0":"")+std::to_string(seconds/60)+":"+(seconds%60<10?"0":"")+std::to_string(seconds%60);int width=s2_dialogue_label_width(label,fetch,&s);if(width<0)return width;e=s2_dialogue_draw_label(label,(w-width)/2,4,w,out,fetch,&s);if(e)return e;}
 // Bonus HUD uses the hero portrait without story health pips and a bare score.
 if(s.bonus){e=drawUI(heroIcon(s.playerType),0,4,4,false);if(e)return e;std::string score=std::to_string(s.coins);int labelWidth=s2_dialogue_label_width(score,fetch,&s);if(labelWidth<0)return labelWidth;e=s2_dialogue_draw_label(score,w-40-labelWidth,4,w,out,fetch,&s);if(e)return e;}
 if(s.dialogue[64]){
  if(s.dialogueSerial!=s.dialogue[67]){e=s2_dialogue_lines(uint32_t(s.dialogue[66]),fetch,&s,s.dialogueLines);if(e)return e;s.dialogueSerial=s.dialogue[67];s.dialoguePage=0;}

  e=drawUI(0x083282c0,0,0,0);if(e)return e;if(s.dialogue[65]&&!s.dialogue[79]){e=drawUI(uint32_t(s.dialogue[65]),0,33,40);if(e)return e;}
  e=s2_dialogue_draw_text(s.dialogueLines,s.dialoguePage,w,out,fetch,&s);if(e)return e;e=drawUI(0x083282d8,(s.dialogueTick/12)%2,221,60);if(e)return e;
 }return s2_screen_effect_argb(s.effects+5,out,pixels);
}
static void sessionInfo(OwnedSession& s,int32_t* info){int32_t summary[8]={s.tick,s.extra()[0],s.extra()[1],s.level&&s.book()[6]?s.book()[6]:s.extra()[3],s.player()[0],s.player()[1],s.sounds,s.error};std::copy_n(summary,8,info);}
static int collectSurfacesFor(OwnedSession& s,const int32_t* subject,int excludedId){int e=0;
 s.surfaceCount=0;
 if(s.level&&!e&&!s.error)for(auto& a:s.actors){
  int type=a.spawn[1];if(s.sceneId<=1){if(type!=9&&type!=10&&!liftableProp(type)&&type!=22&&type!=138)continue;}else if(type!=138&&!plateType(type)&&!liftableProp(type)&&s2_object_category(type)!=3)continue;
  const int32_t*owner=liftedOwner(s,a.spawn[0]);
  if(s.sceneId>1&&!(a.state[39]&7)&&type!=138&&!owner)continue;
  if((a.state[40]&1)||a.spawn[0]==excludedId||owner==subject)continue;
  // Held bounce objects must deliver event28 before the jumper is grounded.
  if(owner&&(type==16||type==17))continue;
  int heldFlags=1;int32_t candidate[36];int n=slopeType(type)?s2_slope_surfaces(a.pose(),0,a.pose()+39,candidate):s2_dynamic_surfaces(a.pose(),a.state[30],a.state[31],owner?&heldFlags:a.pose()+39,a.pose()+60,0,candidate);if(n<0){e=n;break;}
  // Conservative body sweep plus4px includes both the current and predicted
  // position; candidate filtering changes no surface geometry or motion.
  int64_t px=subject[0],py=subject[1],w=subject[30]*128+1024,h=subject[31]*128+1024;
  int64_t dx=subject[5],dy=subject[11];w+=std::abs(dx)+std::abs(int64_t(a.state[60]));h+=std::abs(dy)+std::abs(int64_t(a.state[61]));
  if(!n)continue;int64_t left=candidate[0],top=std::min(candidate[1],candidate[3]),right=candidate[2],bottom=std::max(candidate[1],candidate[3]);
  for(int i=1;i<n;i++){auto* c=candidate+i*9;left=std::min(left,int64_t(c[0]));right=std::max(right,int64_t(c[2]));top=std::min(top,int64_t(std::min(c[1],c[3])));bottom=std::max(bottom,int64_t(std::max(c[1],c[3])));}
  if(right*256+1024<px-w||left*256-1024>px+w||bottom*256+1024<py-h||top*256-1024>py+h)continue;
  for(int i=0;i<n&&s.surfaceCount<16;i++)std::copy_n(candidate+i*9,9,s.surfaces+s.surfaceCount++*9);
 }
 return e;}
static int collectSurfaces(OwnedSession&s){return collectSurfacesFor(s,s.player(),0);}
extern "C" int s2_actor_current_frame(const int32_t*,Fetch,void*,int32_t*);
// Some grounded enemy spawn boxes begin a few pixels through a one-way
// floor. Recover only an initial shallow overlap, before downward movement.
static int settleEnemySpawn(OwnedSession& s,SessionLevelActor& a){int type=a.spawn[1];if(a.spawnSettled||(type!=54&&type!=55&&type!=56&&type!=57&&type!=58&&type!=59&&type!=60)||!(a.state[40]&2))return 0;a.spawnSettled=true;auto* p=a.pose();int32_t left=p[0]-p[30]*128,foot=p[1]+p[31]*128;
 for(int lift=1;lift<=4;lift++){int hit=s2_actor_probe_file(s.collision.c_str(),3,left,foot-lift*256,p[30]*256,255,nullptr,0);if(hit<0)return hit;if(hit){p[1]-=lift*256;p[33]-=lift*256;p[37]=p[1];break;}}return 0;}
static int gingyProjectile(OwnedSession& s){if(s.playerType!=5||(s.extra()[0]!=7&&s.extra()[0]!=16))return 0;int32_t frame[11],meta;int e=s2_actor_current_frame(s.player(),fetch,&s,frame);if(e)return e;if(!fetch(uint32_t(frame[5]),&meta,1,&s))return -2;int key=s.player()[22]+1;if(s.book()[5]==key)return 0;s.book()[5]=key;if(!((uint32_t(meta)>>16)&255)||s.projectiles.size()>=256)return 0;int32_t xy[2];e=s2_actor_spawn_point_q8(s.player(),fetch,&s,xy);if(e)return e;SessionProjectile p;p.type=s.player()[47]==0x083373c4?161:160;e=s2_projectile_init(s.collision.c_str(),p.type,xy,s.player()[18],s.tick,fetch,sink,&s,p.pose,&p.deadline);if(!e){p.damageUnits=attackDamageUnits(s.heroPower[2]);s.projectiles.push_back(p);}return e;}
struct ProjectileReceiver{OwnedSession* session;SessionProjectile* projectile;};
static int projectileFetch(uint32_t a,int32_t* out,int n,void* ctx){return fetch(a,out,n,static_cast<ProjectileReceiver*>(ctx)->session);}
static int projectileSink(int k,uint32_t a,int32_t scale,void* ctx){return sink(k,a,scale,static_cast<ProjectileReceiver*>(ctx)->session);}
static int projectileReply(const int32_t* event,void* ctx){auto* r=static_cast<ProjectileReceiver*>(ctx);auto& p=*r->projectile;int e=s2_projectile_receive(p.type,p.pose,&p.deadline,event,r->session->tick,projectileFetch,projectileSink,ctx);if(!e&&p.pose[42]==13&&event[1]==5)p.damageUnits=attackDamageUnits(r->session->heroPower[r->session->playerType-3]);return e;}
struct CakeReceiver{OwnedSession* session;SessionLevelActor* actor;int damageUnits=-1;};
static int cakeFetch(uint32_t a,int32_t* out,int n,void* ctx){return fetch(a,out,n,static_cast<CakeReceiver*>(ctx)->session);}
static int cakeSink(int k,uint32_t a,int32_t scale,void* ctx){return sink(k,a,scale,static_cast<CakeReceiver*>(ctx)->session);}
static int cakeReply(const int32_t* event,void* ctx){auto* r=static_cast<CakeReceiver*>(ctx);auto& a=*r->actor;auto& s=*r->session;int e;
 if(a.spawn[1]==74){int32_t grab[3]={event[0],event[1],event[2]};if(grab[1]==12&&s.playerType==3&&s.extra()[0]==8)grab[1]=10;e=s2_puss_boss_receive(a.pose(),a.subtype,grab,a.spawn[6],s.tick,cakeFetch,cakeSink,ctx);if(e>0&&grab[1]==10)s.extra()[3]=a.spawn[0];}
 else if(a.spawn[1]==156){int units=r->damageUnits<0?attackDamageUnits(s.heroPower[s.playerType-3]):r->damageUnits;if(units&&s.tick>a.subtype[4]&&a.subtype[5]!=4&&(event[1]==13||event[1]==1||event[1]==2||event[1]==3||event[1]==5)){units+=a.reactions()[57]&1;a.reactions()[57]=units&1;int damage=units/2;if(!damage){a.subtype[4]=s.tick+15;int sound=sink(11,0x08053eac,256,&s);return sound?sound:1;}a.subtype[0]=std::max(1,a.subtype[0]-(damage-1));}e=s2_fairy156_receive(a.pose(),a.subtype,a.aux,event,s.tick,cakeFetch,cakeSink,ctx);a.auxiliary=a.aux[56]!=0;}
 else if(a.spawn[1]==155){int units=r->damageUnits<0?attackDamageUnits(s.heroPower[s.playerType-3]):r->damageUnits;if(units&&s.tick>a.subtype[4]&&a.subtype[5]!=4&&(event[1]==13||event[1]==1||event[1]==2||event[1]==3||event[1]==5)){units+=a.reactions()[57]&1;a.reactions()[57]=units&1;int damage=units/2;if(!damage){a.subtype[4]=s.tick+15;int sound=sink(11,0x08053eac,256,&s);return sound?sound:1;}a.subtype[0]=std::max(1,a.subtype[0]-(damage-1));}e=s2_fairy155_receive(a.pose(),a.subtype,event,s.tick,cakeFetch,cakeSink,ctx);}
 else e=s2_cake_receive(a.pose(),a.subtype,event,s.tick,cakeSink,ctx);return e;}

// Attachment changes position outside the normal movement update. Rebase its
// collision sweep so release cannot collide along the entire carrying route.
static int followLiftedProp(OwnedSession&s,int32_t*p){int e=s2_shrek_lift_position(s.player(),p,s.book(),s.extra(),fetch,&s);if(e)return e;p[32]=p[0]-p[30]*128;p[33]=p[1]-p[31]*128;p[34]=p[30]*256;p[35]=p[31]*256;p[36]=p[0];p[37]=p[1];p[60]=p[61]=0;return 0;}
static int heroContacts(OwnedSession& s,bool grabPressed){int e=gingyProjectile(s);int32_t diag[8];
 // This fixture does not schedule foot attacks: dy=0, like Stage21 demo.
 if(!s.level){
  if(!e&&!s.error&&!(s.item()[40]&1))e=s2_shrek_contact_pair(s.player(),s.extra(),0,77,3,s.item(),s.vm(),s.reactions(),fetch,&s,diag);
  if(!e&&!s.error&&!(s.item()[40]&1))e=s2_generic_contact_pair_receiver(s.item(),s.player(),fetch,reply,&s,diag);
  if(!e&&!s.error)e=s2_shrek_carry_follow(s.player(),s.extra(),s.status(),s.item(),s.tick,s.tick,fetch,sink,dispatch,&s);
 }else{
  for(auto& a:s.actors){if(e||s.error)break;if((a.state[40]&1)||(ambientType(a.spawn[1])&&a.spawn[1]!=72)||a.spawn[1]==144||markerType(a.spawn[1])||a.spawn[1]==151||a.spawn[1]==148||a.spawn[1]==153||specialExit(a.spawn[1])||!enemyVisible(s,a))continue;if(a.spawn[1]==154)continue;if(a.spawn[1]==74||fairyType(a.spawn[1])){CakeReceiver r{&s,&a};s.currentActor=a.spawn[0];e=s2_generic_contact_pair_receiver(s.player(),a.pose(),cakeFetch,cakeReply,&r,diag);if(!e&&(a.spawn[1]!=74||(a.subtype[0]!=3&&a.subtype[0]!=4)))e=s2_generic_contact_pair_receiver(a.pose(),s.player(),fetch,reply,&s,diag);continue;}if(plateType(a.spawn[1])||pushBlock(a.spawn[1]))continue;if(a.spawn[1]==139){e=s2_generic_contact_pair_receiver(a.pose(),s.player(),fetch,reply,&s,diag);if(!e)e=s2_puss_gate_contact(a.pose(),a.subtype,s.player(),0,s.tick,fetch,sink,&s);continue;}if(s.playerType==3&&grabPressed&&liftableProp(a.spawn[1])&&!s.book()[6]&&!s.extra()[3]&&s.extra()[0]==8&&s.player()[42]==12&&s.player()[22]==0&&!(s.player()[40]&16)){
   int64_t dx=int64_t(a.state[0])-s.player()[0],dy=int64_t(a.state[1])-s.player()[1];if(dx>=-11*256&&dx<=11*256&&dy>=-20*256&&dy<=20*256){int w=s.player()[30]*256,h=s.player()[31]*256,th=a.state[31]*256;int clear=s2_actor_probe_file(s.collision.c_str(),5,s.player()[0]-w/2,s.player()[1]-h/2-th,w,h+th,s.surfaces,s.surfaceCount);if(clear<0){e=clear;break;}if(!clear){s.player()[43]=a.state[0]<s.player()[0]?2:1;int32_t pickup[3]={s.player()[41],10,s.player()[43]};int accepted=s2_generic_activate(a.vm(),a.reactions(),pickup);if(accepted<0)e=accepted;else if(accepted){s.player()[40]|=16;e=s2_shrek_lift_enter(s.player(),s.extra(),s.book(),a.spawn[0],s.tick,0x0804b73c,fetch,&s);}}}}
   if(!e&&!(s.contextB&&rewardType(a.spawn[1]))){e=s2_shrek_contact_pair_resolved_carry(s.player(),s.extra(),s.player()[61],uint32_t(a.spawn[0]),s2_object_category(a.spawn[1]),a.pose(),a.vm(),a.reactions(),fetch,&s,diag,consumeKey);if(!e&&s2_object_category(a.spawn[1])==8&&(diag[1]||diag[7]))armAttackDamage(a.reactions(),a.vm(),attackDamageUnits(s.heroPower[s.playerType-3]));}if(!e&&(!npcType(a.spawn[1])||a.reactions()[5])&&!(spawnerType(a.spawn[1])&&a.state[42]>=37&&a.state[42]<=39))e=s2_generic_contact_pair_receiver(a.pose(),s.player(),fetch,reply,&s,diag);if(!e&&npcType(a.spawn[1])&&a.reactions()[5]&&diag[0]){a.auxiliary=true;a.aux[0]=a.state[0];a.aux[1]=a.state[1]-a.state[31]*128-a.aux[31]*128;}}
  for(auto& p:s.projectiles){if(e||s.error)break;if(p.pose[40]&1)continue;if(p.type<160){ProjectileReceiver r{&s,&p};e=s2_generic_contact_pair_receiver(s.player(),p.pose,projectileFetch,projectileReply,&r,diag);if(e)break;}
if(p.type<160&&p.pose[42]==13&&!e){for(auto& a:s.actors)if((a.spawn[1]==145||(a.spawn[1]>=52&&a.spawn[1]<=62))&&!(a.state[40]&1)){s.currentActor=a.spawn[0];e=s2_generic_contact_pair(p.pose,a.pose(),a.vm(),a.reactions(),fetch,&s,diag);if(!e&&diag[1]&&s2_object_category(a.spawn[1])==8)armAttackDamage(a.reactions(),a.vm(),p.damageUnits);if(e)break;}}if(p.type<160&&!e){e=s2_generic_contact_pair_receiver(p.pose,s.player(),fetch,reply,&s,diag);if(!e&&s.sceneId==20)for(auto& a:s.actors)if(a.spawn[1]==154){CakeReceiver r{&s,&a};e=s2_generic_contact_pair_receiver(p.pose,a.pose(),cakeFetch,cakeReply,&r,diag);if(e)break;}}else for(auto& a:s.actors){if((a.state[40]&1)||ambientType(a.spawn[1])||markerType(a.spawn[1])||specialExit(a.spawn[1])||a.spawn[1]==154||a.spawn[1]==153||fairyType(a.spawn[1])||a.spawn[1]==151||a.spawn[1]==148)continue;s.currentActor=a.spawn[0];e=s2_generic_contact_pair(p.pose,a.pose(),a.vm(),a.reactions(),fetch,&s,diag);if(!e&&diag[1]&&s2_object_category(a.spawn[1])==8)armAttackDamage(a.reactions(),a.vm(),p.damageUnits);if(e)break;}}

  if(s.bonus&&!e&&s.book()[6]){auto item=std::find_if(s.actors.begin(),s.actors.end(),[&](const SessionLevelActor& a){return a.spawn[0]==s.book()[6];});if(item==s.actors.end())e=-4;else e=followLiftedProp(s,item->pose());}
  if(s.bonus&&!e)for(auto& mouse:s.actors){if(mouse.spawn[1]!=140||(mouse.state[40]&1))continue;for(auto& mushroom:s.actors){if(mushroom.spawn[1]!=16||(mushroom.state[40]&1))continue;
    // Contact helper shares fetch/receiver context; an adapter keeps both explicit.
    e=s2_session_mushroom_mouse_contact(mouse.pose(),mushroom.pose(),mushroom.vm(),mushroom.reactions(),fetch,&s);if(!e)e=s2_session_mushroom_mouse_contact(mushroom.pose(),mouse.pose(),mouse.vm(),mouse.reactions(),fetch,&s);if(e)break;}(void)mouse;if(e)break;}
  if(!e)for(auto& cookie:s.projectiles){if(cookie.type<160||(cookie.pose[40]&1))continue;for(auto& a:s.actors)if(fairyType(a.spawn[1])&&!(a.state[40]&1)){CakeReceiver r{&s,&a,cookie.damageUnits};s.currentActor=a.spawn[0];e=s2_generic_contact_pair_receiver(cookie.pose,a.pose(),cakeFetch,cakeReply,&r,diag);if(e)break;}if(e)break;for(auto& threat:s.projectiles){if(threat.type>=160||(threat.pose[40]&1))continue;ProjectileReceiver r{&s,&threat};e=s2_generic_contact_pair_receiver(cookie.pose,threat.pose,projectileFetch,projectileReply,&r,diag);if(e)break;}if(e)break;}
  if(!e&&s.book()[6]){auto a=std::find_if(s.actors.begin(),s.actors.end(),[&](const SessionLevelActor& x){return x.spawn[0]==s.book()[6];});if(a==s.actors.end())e=-4;else e=followLiftedProp(s,a->pose());}
  if(!e&&s.extra()[3]){auto a=std::find_if(s.actors.begin(),s.actors.end(),[&](const SessionLevelActor& x){return x.spawn[0]==s.extra()[3];});if(a==s.actors.end())e=-4;else e=s2_shrek_carry_follow(s.player(),s.extra(),s.status(),a->pose(),s.tick,s.tick,fetch,sink,dispatch,&s);}
 }
 return e;}
// Evaluate the entire party after all hero physics/contacts have advanced.
// Carried items belong to the hero snapshot, not to the current selection.
static int checkLevelExit(OwnedSession& s,int buttons){
 if(!s.level||s.bonus||s.levelEnding||s.dialogue[64]||s.error)return 0;
 bool paired=s.party.size()>1;for(auto& a:s.actors)if(a.spawn[1]==152&&s.tick>5&&!s.dialogue[64]){bool enemies=false;for(auto& v:s.actors)if(!(v.state[40]&1)&&s2_object_category(v.spawn[1])==8)enemies=true;if(!enemies){if(!a.subtype[0]){a.subtype[0]=1;return sink(26,10,0,&s);}s.levelEnding=true;return 0;}}
 for(auto& zone:s.actors){if((zone.spawn[1]!=148&&zone.spawn[1]!=149&&zone.spawn[1]!=150)||(zone.state[40]&1))continue;if(zone.spawn[1]==149&&!zone.subtype[0])continue;if(zone.spawn[1]==150&&!zone.subtype[1])continue;
  auto ready=[&](const int32_t* h){
   int state=h[80];if(paired){if((h[40]&1)||!(h[14]||h[64])||(state!=0&&state!=1&&state!=9&&state!=10&&state!=11&&state!=17&&state!=18))return false;}else if(state>1)return false;
   int32_t a[4]={h[0]-h[30]*128,h[1]-h[31]*128,h[30]*256,h[31]*256},b[4]={zone.state[0]-32*256,zone.state[1]-64*256,64*256,128*256};return s2_rect_overlap_xywh(a,b)>0;
  };
  bool all=true;for(size_t i=0;i<s.party.size();i++){auto* h=int(i)==s.partyIndex?s.state:s.party[i].state;
   bool arrived=ready(h);all=all&&arrived;
   if(paired){h[91]=arrived?1:0;s.finishWaiting[i]=arrived;if(arrived)h[98]=s.tick;
    if(arrived&&(h[80]==0||h[80]==11)){
     int32_t row[10];uint32_t table=heroTable(s.party[i].type),anim=0;
     for(int j=0;j<40;j++){if(!fetch(table+j*40,row,10,&s))return -2;if(row[0]==14){anim=uint32_t(row[1]);break;}if(row[0]==999)break;}
     if(!anim)return -2;if(uint32_t(h[47])!=anim){const int32_t idle[3]={1,7,0};int e=s2_shrek_locomotion_enter(h,h+80,h+88,h+96,0x158,h[82],s.tick,s.tick,table,idle,fetch,&s);if(e)return e;}
    }
   }
  }
  if(!all)continue;
  int e=sink(26,uint32_t(zone.spawn[6]),0,&s);if(e)return e;zone.state[40]|=1;s.levelEnding=true;s.dialogueHeld=buttons;break;
 }
 return 0;
}
static int contextualButtons(OwnedSession& s,int buttons,int raw){
 bool bEdge=(raw&2)&&!(s.rawButtons&2);s.rawButtons=raw;
 if(!(raw&2))s.contextB=false;
 if(bEdge&&!(raw&1)&&s.playerType==3&&s.level&&!s.book()[6]&&!s.extra()[3]&&s.extra()[0]<=1){
  for(auto& a:s.actors)if(!(a.state[40]&1)&&(liftableProp(a.spawn[1])||(a.spawn[1]==74&&a.subtype[0]==3))&&std::abs(int64_t(a.state[0])-s.player()[0])<=11*256&&std::abs(int64_t(a.state[1])-s.player()[1])<=20*256){s.contextB=true;break;}
 }
 return s.contextB?(buttons&~2)|4:buttons;
}
static int stepPartners(OwnedSession& s,int buttons){
 int32_t active[320],spawn[8];std::copy_n(s.state,320,active);std::copy_n(s.playerSpawn,8,spawn);bool joint=sharedCamera(s);int type=s.playerType,pressed=s.pressedButtons,raw=s.rawButtons;bool context=s.contextB;int result=0;std::copy_n(active,320,s.party[s.partyIndex].state);
 for(size_t i=0;i<s.party.size();i++){if(int(i)==s.partyIndex)continue;auto& p=s.party[i];std::copy_n(p.state,320,s.state);std::copy_n(p.spawn,8,s.playerSpawn);s.playerType=p.type;s.rawButtons=p.rawButtons;s.contextB=p.contextB;
  s.book()[4]=(s.book()[4]&~0x20000)|(s.pussDoubleJump?0x20000:0);int held=joint?buttons:0;held=contextualButtons(s,held,held);s.pressedButtons=held&~s.book()[4];int32_t control[3]={joint?1:0,0,(!s.extra()[3]&&int32_t(uint32_t(s.tick)-uint32_t(s.book()[2]))>600)?1:0},events[9]={1,7,0,0,12,0,0,11,0};
  result=collectSurfaces(s);if(!result)result=(p.type==6?s2_donkey_player_step_scene:s2_shrek_player_step_scene)(s.collision.c_str(),s.player(),s.extra(),s.status(),s.book(),held,s.tick,s.tick,control,events,s.motionTable(),0x0804b708,fetch,sink,dispatch,&s,s.surfaces,s.surfaceCount);
  if(!result&&s.extra()[0]==14&&(s.player()[20]&255))s.status()[1]=0;
  if(!result&&s.extra()[0]!=13&&s.extra()[0]!=14&&s2_actor_outside_world(s.player(),s.worldWidth*256,s.worldHeight*256)){
   result=p.type!=3?s2_character_terminal_enter(s.motionTable(),13,s.player(),s.extra(),s.book(),s.tick,fetch,&s):s2_shrek_fall_death(s.player(),s.extra(),s.book(),s.tick,fetch,&s);s.status()[1]=0;s.book()[1]=0;if(s.autoRestart)s.deathReturning=true;
  }
  if(!result)result=heroContacts(s,(s.pressedButtons&4)!=0);
  if(!result&&s.autoRestart&&(s.extra()[0]==13||s.extra()[0]==14||s.extra()[0]==15)&&(s.player()[20]&255)){s.deathReturning=true;s.mosaic=false;s.fade[1]=64;}
  p.rawButtons=s.rawButtons;p.contextB=s.contextB;std::copy_n(s.state,320,p.state);if(result||s.error)break;
 }
 std::copy_n(active,320,s.state);std::copy_n(spawn,8,s.playerSpawn);s.playerType=type;s.pressedButtons=pressed;s.rawButtons=raw;s.contextB=context;return result;
}
// Source subclasses 11A78 (two weights, latched notice9/3) and127C4
// (two same-direction pushes per frame, +/-512 current X velocity).
static int stepMechanisms(OwnedSession& s){
 for(auto& a:s.actors){int type=a.spawn[1];if((!plateType(type)&&!pushBlock(type))||(a.state[40]&1))continue;int weights=0,pushes=0;
  auto contact=[&](const int32_t* h){if(h[89]<=0||h[80]==6||h[80]==13||h[80]==14||h[80]==15)return;int64_t dx=int64_t(h[0])-a.state[0],dy=int64_t(h[1])-a.state[1];int hw=(h[30]+a.state[30])*128,hh=(h[31]+a.state[31])*128;
   int64_t foot=int64_t(h[1])+h[31]*128,top=int64_t(a.state[1])-a.state[31]*128;
   if(plateType(type)&&std::abs(dx)<hw&&std::abs(foot-top)<=3*256&&h[11]>=0)++weights;
   if(pushBlock(type)&&std::abs(dy)<hh-256&&std::abs(dx)<=hw+4*256){if(dx<0&&(h[82]&16))++pushes;else if(dx>0&&(h[82]&32))--pushes;}
  };
  contact(s.state);for(size_t i=0;i<s.party.size();i++)if(int(i)!=s.partyIndex)contact(s.party[i].state);
  if(pushBlock(type)){a.subtype[0]=pushes;if((a.state[14]||a.state[64])&&std::abs(pushes)==type-30){a.state[5]=pushes>0?512:-512;if(a.subtype[2]<s.tick&&std::abs(a.state[60])>255){int e=sink(11,0x08054014,256,&s);if(e)return e;a.subtype[2]=s.tick+120;}}continue;}
  a.subtype[0]=weights;
  if(a.subtype[1]==0){if(weights>=type-26){a.state[39]=0;int e=s2_generic_message(a.pose(),8,4,0,s.tick,fetch,&s);if(e)return e;a.subtype[1]=1;}else a.state[22]=std::min(weights,a.state[77]-1);}
  else if(a.subtype[1]==1&&(a.state[20]&255)){int32_t packet[3]={9,3,a.spawn[6]};int saved=s.currentActor;
   for(auto& target:s.actors){if(!target.registered||(target.state[40]&1))continue;s.currentActor=target.spawn[0];int e=s2_generic_event(target.pose(),target.vm(),target.reactions(),packet,s.tick,fetch,registry,&s);if(e){s.currentActor=saved;return e;}}s.currentActor=saved;
   s.requests.push_back({{s.tick,1,0,0,9,3,a.spawn[6],0}});int e=sink(11,0x08053f78,256,&s);if(e)return e;a.subtype[1]=2;
  }
 }
 return 0;
}

extern "C" int s2_projectile_target(int,int32_t*,const int32_t*,Fetch,void*);
static int sessionStep(void* handle,int buttons,uint32_t* out,size_t count,int32_t* info){
 if(!handle||!out||!info)return -1;auto& s=*static_cast<OwnedSession*>(handle);if(count!=size_t(s.width)*s.height)return -1;if(s.error)return s.error;switchPartner(s,buttons);buttons&=~768;
 if(s.levelComplete){std::fill_n(out,count,0xff000000u);int e=s2_dialogue_draw_label("Level complete",(s.width-240)/2+45,40,s.width,out,fetch,&s);if(!e)e=s2_dialogue_draw_label("Coins: "+std::to_string(s.coins)+"/"+std::to_string(s.coinTarget),(s.width-240)/2+45,65,s.width,out,fetch,&s);if(!e)e=s2_dialogue_draw_label("A: Retry",(s.width-240)/2+45,100,s.width,out,fetch,&s);bool retry=(buttons&1)&&!(s.book()[4]&1);s.book()[4]=buttons;if(retry)e=s2_session_reset(handle);sessionInfo(s,info);return e;}
 if(s.bonusUnavailable){int e=render(s,out);if(e)return e;for(size_t i=0;i<count;i++)out[i]=0xff000000u|((out[i]>>2)&0x003f3f3fu);e=s2_dialogue_draw_label("Bonus not available yet",(s.width-240)/2+12,55,s.width,out,fetch,&s);if(!e)e=s2_dialogue_draw_label("A / B: Return",(s.width-240)/2+35,80,s.width,out,fetch,&s);int pressed=buttons&~s.book()[4];s.book()[4]=buttons;if(pressed&3){s.bonusUnavailable=false;s.blockedButtons=buttons&3;}sessionInfo(s,info);return e;}
 if(s.deathReturning){
  s.mosaic=false;s.fade[1]=64;
  if(!s.fades||s.fade[0]==64){int e=s2_session_reset(handle);if(e)return e;s.deathRestarts++;s.blockedButtons=buttons&63;int result=render(s,out);sessionInfo(s,info);return result;}
  int e=render(s,out);sessionInfo(s,info);return e;
 }
 if(s.levelEnding&&!s.dialogue[64]){
  // The two Fairy scripts leave directly after dialogue; no generic hero victory.
  if(s.sceneId==15||s.sceneId==16){s.mosaic=false;s.fade[1]=64;if(!s.fades||s.fade[0]==64){s.levelComplete=true;s.fade[0]=s.fade[1]=0;return sessionStep(handle,buttons,out,count,info);}int e=render(s,out);sessionInfo(s,info);return e;}
  s.mosaic=false;int e=0;if(!s.finishStarted){
   e=s.playerType!=3?s2_character_terminal_enter(s.motionTable(),12,s.player(),s.extra(),s.book(),s.tick,fetch,&s):s2_shrek_finish_enter(s.player(),s.extra(),s.book(),s.tick,fetch,&s);if(e)return s.error=e;
   for(size_t i=0;i<s.party.size();i++)if(int(i)!=s.partyIndex){auto& p=s.party[i];uint32_t table=heroTable(p.type);e=p.type!=3?s2_character_terminal_enter(table,12,p.state,p.state+80,p.state+96,s.tick,fetch,&s):s2_shrek_finish_enter(p.state,p.state+80,p.state+96,s.tick,fetch,&s);if(e)return s.error=e;}s.finishStarted=true;}
  {++s.tick;int done=0;
   {done=s.finishHeroDone[s.partyIndex]?1:s2_shrek_finish_step(s.player(),s.book(),s.tick,fetch,sink,&s);if(done<0)return s.error=done;s.finishHeroDone[s.partyIndex]=s.finishHeroDone[s.partyIndex]||done!=0;}
   bool any=s.finishHeroDone[s.partyIndex];for(size_t i=0;i<s.party.size();i++)if(int(i)!=s.partyIndex){auto& p=s.party[i];{done=s.finishHeroDone[i]?1:s2_shrek_finish_step(p.state,p.state+96,s.tick,fetch,sink,&s);if(done<0)return s.error=done;s.finishHeroDone[i]=s.finishHeroDone[i]||done!=0;}any=any||s.finishHeroDone[i];}s.finishDone=any;}
  if(s.finishDone){s.fade[1]=64;if(!s.fades||s.fade[0]==64){s.levelComplete=true;s.fade[0]=s.fade[1]=0;return sessionStep(handle,buttons,out,count,info);}}
  e=render(s,out);sessionInfo(s,info);return e;
 }
 if(s.mini){auto& m=*s.mini;bool returnNow=m.miniFailed;
  if(returnNow){s.miniReturning=true;s.mosaic=true;s.fade[1]=64;}
  if(s.miniReturning&&(!s.fades||s.fade[0]==64)){s.lastBonusScore=m.coins;s.bestBonusScore=std::max(s.bestBonusScore,m.coins);s.rewardCount=s2_bonus_rewards(m.bonusIndex(),m.coins,fetch,&s,s.rewardTypes);if(s.rewardCount<0)return s.error=s.rewardCount;s.blockedButtons=buttons&3;s.mini.reset();s.miniReturning=false;s.fade[1]=0;int e=render(s,out);if(e)s.error=e;sessionInfo(s,info);return s.error;}
  auto& canvas=s.childCanvas;canvas.resize(240*160);int e=s2_session_step(&m,buttons,canvas.data(),canvas.size(),info);if(e){s.error=e;return e;}
  for(size_t i=size_t(s.miniCursor);i<m.requests.size();i++)if(m.requests[i].row[1]==11){s.requests.push_back(m.requests[i]);s.sounds++;}s.miniCursor=int(m.requests.size());
  std::fill_n(out,count,0xff181818u);for(int y=0;y<160;y++)std::copy_n(canvas.data()+y*240,240,out+y*s.width+(s.width-240)/2);return 0;
 }
 if(s.miniPending){s.mosaic=true;s.fade[1]=64;if(s.fades&&s.fade[0]<64){int e=render(s,out);sessionInfo(s,info);return e;}int32_t error=0;std::string folder=s.scene.substr(0,s.scene.find_last_of('/'))+("/minigame_0"+std::to_string(s.bonusIndex()));
  auto* child=static_cast<OwnedSession*>(s2_session_create_level(s.package.c_str(),(folder+"/scene.s2lv").c_str(),(folder+"/scene.s2cl").c_str(),s.sprites.c_str(),(folder+"/scene.s2ob").c_str(),&error));
  if(!child)return s.error=error;child->deferRender=s.deferRender;child->balanceRandomState=uint32_t(s.tick);child->blockedButtons=buttons&3;child->bestBonusScore=s.bestBonusScore;child->bonusResults=s.bonusResults;s.fade[1]=0;s.mini.reset(child);s.miniPending=false;s.miniCursor=0;return sessionStep(handle,buttons,out,count,info);
 }
 if(s.bonus&&s.miniFailed){s.mosaic=false;s.fade[1]=64;s.miniReturning=s.fades&&s.fade[0]==64;s.book()[4]=buttons;int e=render(s,out);sessionInfo(s,info);return e;}
 // Exposed buttons are left/right/A/B/Select/menu. Stable single target ID77.
 if(buttons&~(128|64|32|16|1|4|2))return -4;
 if(s.dialogue[64]){int pressed=buttons&~s.dialogueHeld;s.dialogueHeld=buttons;int input=(pressed&63)|((pressed&64)?8:0);
  bool lastPage=(size_t(s.dialoguePage+1)*3>=s.dialogueLines.size());if(input==1&&!lastPage){s.dialoguePage++;input=0;}
  int e=s2_dialogue_step(s.dialogue,++s.dialogueTick,input,lastPage,fetch,&s);if(!e&&!s.dialogue[64]){s.blockedButtons=buttons&3;if(s.dialogue[73]){s.miniPending=true;}else if((s.dialogue[78]==2||s.dialogue[78]==4||s.dialogue[78]==14||s.dialogue[78]==30||(s.sceneId==20&&s.dialogue[78]==42)||(s.sceneId==15&&s.dialogue[78]==48)||(s.sceneId==16&&s.dialogue[78]==50)||(s.sceneId==5&&s.dialogue[78]==20)||(s.playerType==4&&s.dialogue[78]==28))){s.levelEnding=true;if((s.sceneId==15&&s.dialogue[78]==48)||(s.sceneId==16&&s.dialogue[78]==50)){s.finishStarted=s.finishDone=false;std::fill_n(s.finishHeroDone,3,false);s.fade[0]=s.fade[1]=0;}}else if(s.introDialogue||(s.playerType==3&&(s.dialogue[78]==1||s.dialogue[78]==5||s.dialogue[78]==7||s.dialogue[78]==11||s.dialogue[78]==15||s.dialogue[78]==17||s.dialogue[78]==9||s.dialogue[78]==23||s.dialogue[78]==25))||(s.playerType==6&&(s.dialogue[78]==3||s.dialogue[78]==5||s.dialogue[78]==7||s.dialogue[78]==13||s.dialogue[78]==29))||(s.playerType==4&&(s.dialogue[78]==21||s.dialogue[78]==27||s.dialogue[78]==33||s.dialogue[78]==45))||(s.playerType==5&&(s.dialogue[78]==35||s.dialogue[78]==37||s.dialogue[78]==39))||(s.playerType==7&&(s.dialogue[78]==31||s.dialogue[78]==43)))e=activateHeroSound(s,s.playerType);s.introDialogue=false;}if(!e)e=render(s,out);if(e)s.error=e;sessionInfo(s,info);return s.error;
 }
 if(s.level)for(auto& a:s.actors){if(a.spawn[1]!=151)continue;int32_t packet[3];int accepted=s2_dialogue_trigger_contact(a.pose(),s.player(),0,a.spawn[6],fetch,&s,packet);for(size_t i=0;accepted==0&&i<s.party.size();i++)if(int(i)!=s.partyIndex)accepted=s2_dialogue_trigger_contact(a.pose(),s.party[i].state,0,a.spawn[6],fetch,&s,packet);if(accepted<0)s.error=accepted;
  else if(accepted){s.introDialogue=true;int e=sink(26,uint32_t(a.spawn[6]),0,&s);if(!e)e=s2_actor_mark_removed(a.pose(),a.spawn[0],s.removed,4);s.error=e;s.dialogueHeld=buttons;}
  if(s.error||s.dialogue[64]){if(!s.error)s.error=render(s,out);sessionInfo(s,info);return s.error;}
 }
 if(s.playerType!=5)buttons&=~64;s.blockedButtons&=buttons;buttons&=~s.blockedButtons;
 // Donkey puts a held prop down with B; Select also detaches through grab entry.
 int physicalButtons=buttons;bool talkInput=(buttons&2)&&s.extra()[3]&&talkRange(s);
 if(!talkInput&&s.extra()[3]&&s.extra()[1]!=1&&s.extra()[1]!=2&&s.extra()[1]!=3&&s.extra()[1]!=4&&s.extra()[1]!=5&&s.extra()[1]!=6&&s.extra()[1]!=7&&(buttons&2)&&!(s.rawButtons&2)){const int32_t detach[3]={0,11,0};int e=s2_shrek_carry_release(s.extra(),s.status(),s.tick,detach,dispatch,&s);if(e)return s.error=e;buttons&=~2;s.blockedButtons|=2;}
 if(talkInput)buttons&=~2;
 // One rising-edge combo queues ordinary source inputs; no direct pose edits.
 bool bEdge=(physicalButtons&2)&&!(s.rawButtons&2);
 buttons=contextualButtons(s,buttons,talkInput?physicalButtons:buttons);
 bool grabPressed=(buttons&4)&&!(s.book()[4]&4);
 bool combo=s.playerType==3&&(buttons&3)==3;if(combo&&!s.comboHeld&&shrekAirAttackAllowed(s.extra()[3],s.extra()[1])&&(!s.level||!s.book()[6])){int state=s.extra()[0];if((state>=0&&state<=5)||(s.level&&state==7)){s.comboPhase=(s.level&&state==7)?3:(state>=2&&state<=4)?((s.book()[4]&2)?3:1):((s.book()[4]&3)?3:2);s.comboFrames=s.level?64:8;}}s.comboHeld=combo;if((!shrekAirAttackAllowed(s.extra()[3],s.extra()[1]))||(s.level&&s.book()[6])||(s.comboPhase&&s.comboFrames--<=0))s.comboPhase=0;
 if(s.comboPhase==3){buttons&=~3;if(!s.level||s.extra()[0]<=5)s.comboPhase=(s.extra()[0]>=2&&s.extra()[0]<=4)?1:2;}
 else if(s.comboPhase==2){buttons=(buttons&~3)|1;s.comboPhase=1;}
 else if(s.comboPhase==1){if(s.extra()[0]>=(s.level?3:2)&&s.extra()[0]<=4){buttons|=2;s.comboPhase=0;}else if(s.level&&s.extra()[0]==2){buttons&=~2;}else if(s.extra()[0]==0){buttons&=~3;s.comboPhase=2;}else if(s.extra()[0]>5)s.comboPhase=0;}
 int cameraX,cameraY;cameraTarget(s,cameraX,cameraY);if(s.party.size()>1){cameraX=s.cameraX;cameraY=s.cameraY;}int32_t window[4]={cameraX*256,cameraY*256,s.width*256,160*256};std::copy_n(window,4,s.cameraWindow);
 s.pressedButtons=(buttons&~s.book()[4])|((talkInput&&bEdge)?2:0);s.tick=int32_t(uint32_t(s.tick)+1);int32_t control[3]={1,0,(!s.extra()[3]&&int32_t(uint32_t(s.tick)-uint32_t(s.book()[2]))>600)?1:0},events[9]={1,7,0,0,12,0,0,11,0};
 int e=s2_screen_effect_step(s.effects+5);
 if((s.sceneId==21||s.sceneId==22)&&s.tick>=s.specialDeadline){e=sink(1,0x08024bc8,0,&s);if(e<0)return s.error=e;int result=render(s,out);sessionInfo(s,info);return result;}
 if(s.bonus&&s.playerType==3&&!e){int spawn=s2_mouse_spawn_step(s.mouseSpawner,s.coins);if(spawn<0)e=spawn;else if(spawn){SessionLevelActor a;int32_t row[8]={s.nextSpawnId++,140,120*256,0,0,0,0,0};std::copy_n(row,8,a.spawn);s.pending.push_back(a);}}
 for(auto& p:s.projectiles){if(e)break;e=s2_projectile_step(s.collision.c_str(),p.type,p.pose,s.tick,fetch,sink,&s);if(!e&&p.type==157){const int32_t* target=s.player();int64_t best=INT64_MAX;for(auto& h:s.party){const int32_t* hero=h.type==s.playerType?s.state:h.state;int64_t dx=int64_t(hero[0])-p.pose[0],dy=int64_t(hero[1])-p.pose[1],distance=dx*dx+dy*dy;if(distance<best){best=distance;target=hero;}}e=s2_projectile_target(p.type,p.pose,target,fetch,&s);}}
 s.projectiles.erase(std::remove_if(s.projectiles.begin(),s.projectiles.end(),[&](const SessionProjectile& p){// Non-homing shots above the entire map, travelling away with no
 // downward target, cannot return. The source renderer retires offscreen
 // projectiles; keeping these alive forever exhausted the native shot list.
 bool above=p.type!=157&&int64_t(p.pose[1])+p.pose[31]*128<0&&p.pose[11]<=0&&p.pose[13]<=0;
 return above||(p.pose[40]&1)||s2_actor_outside_world(p.pose,s.worldWidth*256,s.worldHeight*256);}),s.projectiles.end());
 for(auto& puff:s.smoke){if(e)break;e=s2_smoke_runtime_step(s.collision.c_str(),puff.pose,s.tick);}
 s.smoke.erase(std::remove_if(s.smoke.begin(),s.smoke.end(),[](const SessionSmoke& p){return p.pose[40]&1;}),s.smoke.end());
 if(!s.level){if(!e&&!(s.item()[40]&1))e=s2_generic_runtime_step_empty_dynamic(s.collision.c_str(),s.item(),s.vm(),s.tick,s.worldWidth*256,s.worldHeight*256,fetch,randomValue,&s,4096,s.reactions(),registry,sink);}
 else for(auto& a:s.actors){if(e||s.error)break;if((s.trainerFlags&2)&&a.spawn[1]>=52&&a.spawn[1]<=62)continue;if((a.state[40]&1)||a.spawn[1]==151||a.spawn[1]==148||a.spawn[1]==153||specialExit(a.spawn[1])||markerType(a.spawn[1]))continue;if(a.spawn[1]!=144){e=updateActorVisibility(s,a.pose());if(e)break;}if(!enemyVisible(s,a))continue;s.currentActor=a.spawn[0];if(a.spawn[1]==144){int type=s2_target_generator_step(a.subtype);if(type<0){e=type;break;}if(type){int id=reserve_spawn_id(s);if(id>0){SessionLevelActor child;int32_t row[8]={id,type,a.state[0],a.state[1],0,a.subtype[4],0,0};std::copy_n(row,8,child.spawn);std::copy_n(a.subtype,3,child.subtype);s.pending.push_back(child);s.requests.push_back({{s.tick,36,type,0,row[2],row[3],a.subtype[2],id}});}}continue;}if(npcType(a.spawn[1])){a.auxiliary=false;e=s2_plain_runtime_step(a.aux,s.tick);if(e)break;}if(a.spawn[1]==74){e=s2_puss_boss_step(s.collision.c_str(),a.pose(),a.subtype,a.spawn[6],s.tick,fetch,sink,&s);}else if(fairyType(a.spawn[1])){const int32_t* target=s.player();int64_t best=INT64_MAX;for(auto& h:s.party){const auto* candidate=h.type==s.playerType?s.state:h.state;int64_t dx=int64_t(candidate[0])-a.state[0],dy=int64_t(candidate[1])-a.state[1],d=dx*dx+dy*dy;if(d<best){best=d;target=candidate;}}if(a.spawn[1]==156){int random=(a.subtype[5]==0&&s.tick%120==0)?balanceRandomValue(&s):0;e=s2_fairy156_step(a.pose(),a.subtype,a.aux,s.fairyMarkers,target,s.tick,std::max(0,s.specialDeadline-s.tick),random,fetch,sink,&s);a.auxiliary=a.aux[56]!=0;}else e=s2_fairy155_step(a.pose(),a.subtype,s.fairyMarkers,target,s2_actor_camera_active(a.pose(),s.cameraWindow),s.tick,fetch,sink,&s);}else if(a.spawn[1]==154){e=s2_cake_step(a.pose(),a.aux,a.subtype,s.tick,std::max(0,s.specialDeadline-s.tick),sink,&s);}else if(plateType(a.spawn[1])||pushBlock(a.spawn[1])){e=s2_plain_runtime_step(a.pose(),s.tick);if(!e&&pushBlock(a.spawn[1]))e=s2_actor_move_file(s.collision.c_str(),a.pose()+2,a.pose(),a.pose()+32,a.pose()+36,a.state[30],a.state[31],6,a.pose()+14,a.pose()+60);if(e>=0){if(pushBlock(a.spawn[1])&&e==3)std::copy_n(a.pose()+8,3,a.pose()+11);e=0;}}else if(a.spawn[1]==138)e=s2_donkey_balance_step(s.collision.c_str(),a.pose(),a.vm(),s.tick,s.worldWidth*256,s.worldHeight*256,fetch,balanceRandomValue,&s,4096,a.reactions(),registry,sink);else if(a.spawn[1]==72){a.state[0]+=a.state[5];a.state[1]+=a.state[11];for(auto& marker:s.actors)if(markerType(marker.spawn[1])){int32_t ar[4]={a.state[0]-a.state[30]*128,a.state[1]-a.state[31]*128,a.state[30]*256,a.state[31]*256},br[4]={marker.state[0]-2048,marker.state[1]-2048,4096,4096};if(s2_rect_overlap_xywh(ar,br)){int t=marker.spawn[1];a.state[5]=t==65?-256:t==66?256:0;a.state[11]=t==63?-256:t==64?256:0;}}e=s2_plain_runtime_step(a.pose(),s.tick);}else if(ambientType(a.spawn[1])||a.spawn[1]==139)e=s2_plain_runtime_step(a.pose(),s.tick);else if(spawnerType(a.spawn[1])){a.reactions()[5]=s2_spawner_tag(a.reactions()[5],a.spawn[0]);const int32_t* target=nearestHero(s,a);e=collectSurfacesFor(s,a.pose(),a.spawn[0]);if(!e)e=s2_generic_runtime_step_spawner_dynamic(s.collision.c_str(),a.pose(),a.vm(),s.tick,s.worldWidth*256,s.worldHeight*256,fetch,randomValue,&s,4096,a.reactions(),registry,sink,target,&a.auxiliary,a.subtype,s.surfaces,s.surfaceCount);}else if(a.spawn[1]>=52&&a.spawn[1]<=62){const int32_t* target=nearestHero(s,a);e=collectSurfacesFor(s,a.pose(),a.spawn[0]);if(!e)e=s2_generic_runtime_step_target_dynamic(s.collision.c_str(),a.pose(),a.vm(),s.tick,s.worldWidth*256,s.worldHeight*256,fetch,randomValue,&s,4096,a.reactions(),registry,sink,target,&a.auxiliary,s.surfaces,s.surfaceCount);}else if(liftableProp(a.spawn[1])||(a.state[40]&6)){e=collectSurfacesFor(s,a.pose(),a.spawn[0]);if(!e)e=s2_generic_runtime_step_dynamic(s.collision.c_str(),a.pose(),a.vm(),s.tick,s.worldWidth*256,s.worldHeight*256,fetch,randomValue,&s,4096,a.reactions(),registry,sink,s.surfaces,s.surfaceCount);}else e=s2_generic_runtime_step_empty_dynamic(s.collision.c_str(),a.pose(),a.vm(),s.tick,s.worldWidth*256,s.worldHeight*256,fetch,randomValue,&s,4096,a.reactions(),registry,sink);
  if(!e)e=settleEnemySpawn(s,a);
  if(!e&&a.auxiliary&&!npcType(a.spawn[1])&&a.spawn[1]!=154&&!fairyType(a.spawn[1])){int32_t xy[2];e=s2_actor_spawn_point_q8(a.pose(),fetch,&s,xy);if(!e){a.aux[0]=xy[0];a.aux[1]=xy[1];e=s2_plain_runtime_step(a.aux,s.tick);}}if(!e&&a.spawn[1]==140)s2_mouse_wrap(a.pose());}s.currentActor=0;
 if(!e&&!s.error)for(auto& a:s.pending){int32_t xy[2]={a.spawn[2],a.spawn[3]};e=s2_generic_runtime_init(xy,(a.spawn[1]==142||a.spawn[1]==143)?0:a.spawn[5]&3,actorAnimation(a.spawn[1]),s.tick,fetch,&s,a.pose());if(e)break;a.state[79]=a.spawn[7];if(a.spawn[1]==142||a.spawn[1]==143){a.state[18]=a.spawn[5]&1;e=s2_apply_axis_triple(a.pose()+2,a.subtype,0,a.spawn[5]&1);}if(e)break;s2_reactions_init(a.spawn[6],a.reactions());s2_vm_start(actorScript(a.spawn[1]),a.vm());auto existing=std::find_if(s.actors.begin(),s.actors.end(),[&](const SessionLevelActor& old){return old.spawn[0]==a.spawn[0];});if(existing==s.actors.end())s.actors.push_back(a);else *existing=a;}s.pending.clear();
 if(s.dialogue[64]){if(!e&&!s.error)e=render(s,out);if(e)s.error=e;sessionInfo(s,info);return s.error;}
 // Source marker63..66: body16x16, outgoing events33..36.
 if(!e&&!s.error)for(auto& marker:s.actors){if(!markerType(marker.spawn[1]))continue;marker.state[40]&=~16;
  for(auto& enemy:s.actors){if((enemy.spawn[1]!=147&&enemy.spawn[1]!=52&&(enemy.spawn[1]<53||enemy.spawn[1]>62))||(enemy.state[40]&1))continue;int32_t diag[4];e=s2_generic_contact_pair(marker.pose(),enemy.pose(),enemy.vm(),enemy.reactions(),fetch,&s,diag);if(e)break;}if(e)break;
 }
 // Source147 alternates event34 (upper marker) and event39 (gate139).
 // The gate must contact the fire as well as the player, or the descending
 // fire never receives its turn-up event and eventually leaves the arena.
 if(!e&&s.bonus&&s.playerType==4)for(auto& gate:s.actors)if(gate.spawn[1]==139)for(auto& fire:s.actors)if(fire.spawn[1]==147&&!(fire.state[40]&1)){int32_t diag[8];e=s2_generic_contact_pair(gate.pose(),fire.pose(),fire.vm(),fire.reactions(),fetch,&s,diag);if(e)break;}
 if(!e&&s.forceBossDrop){s.forceBossDrop=false;if(s.extra()[3]){const int32_t release[3]={0,11,0};e=s2_shrek_carry_release(s.extra(),s.status(),s.tick,release,dispatch,&s);const int32_t idle[3]={1,7,0};if(!e)e=s2_shrek_locomotion_enter(s.player(),s.extra(),s.status(),s.book(),0x158,0,s.tick,s.tick,s.motionTable(),idle,fetch,&s);}}
 if(!e&&!s.error&&s.bonus&&s.miniFailed){s.mosaic=false;s.fade[1]=64;int result=render(s,out);sessionInfo(s,info);return result;}
 e=e?e:collectSurfaces(s);
 s.book()[4]=(s.book()[4]&~0x20000)|(s.pussDoubleJump?0x20000:0);
 if(!e&&!s.error)e=(s.playerType==6?s2_donkey_player_step_scene:s.level?s2_shrek_player_step_scene:s2_shrek_player_step_dynamic)(s.collision.c_str(),s.player(),s.extra(),s.status(),s.book(),buttons,s.tick,s.tick,control,events,s.motionTable(),0x0804b708,fetch,sink,dispatch,&s,s.surfaces,s.surfaceCount);
 if(s.level&&!e&&!s.error&&s.extra()[0]==14&&(s.player()[20]&255))s.status()[1]=0;
 if(s.level&&(!s.bonus||s.playerType!=3)&&!e&&!s.error&&s.extra()[0]!=13&&s.extra()[0]!=14&&s2_actor_outside_world(s.player(),s.worldWidth*256,s.worldHeight*256)){e=s.bonus?sink(1,0x08024bbc,0,&s):s.playerType!=3?s2_character_terminal_enter(s.motionTable(),13,s.player(),s.extra(),s.book(),s.tick,fetch,&s):s2_shrek_fall_death(s.player(),s.extra(),s.book(),s.tick,fetch,&s);s.status()[1]=0;s.book()[1]=0;if(!s.bonus&&s.autoRestart)s.deathReturning=true;s.comboPhase=s.comboFrames=0;s.comboHeld=false;}
 if(s.bonus&&s.playerType!=3&&!e&&!s.error&&s.extra()[0]==13&&(s.player()[20]&255))e=sink(1,0x08024bbc,0,&s);
 if(!e&&!s.error)e=heroContacts(s,grabPressed);
 if(!e&&!s.error&&s.party.size()>1)e=stepPartners(s,physicalButtons);
 if(!e&&!s.error)e=stepMechanisms(s);
 if(!e&&!s.error)e=checkLevelExit(s,buttons);
 if(!e&&!s.error&&s.level&&!s.bonus&&s.autoRestart&&(s.extra()[0]==13||s.extra()[0]==14||s.extra()[0]==15)&&(s.player()[20]&255)){s.deathReturning=true;s.mosaic=false;s.fade[1]=64;}
 if(s.party.size()>1){if(s.jointControl&&!partyVisible(s))s.jointControl=false;int32_t target[2];cameraFocusTarget(s,target);s2_camera_follow_step(s.cameraFocus,target);projectPartyCamera(s);beginCameraSwitch(s);}
 if(!e&&!s.error)e=render(s,out);if(e)s.error=e;
 sessionInfo(s,info);return s.error;
}

extern "C" int s2_session_requests(void* handle,int32_t* out,size_t capacity){
 if(!handle||(!out&&capacity))return -1;auto& s=*static_cast<OwnedSession*>(handle);if(capacity<s.requests.size())return -1;
 for(size_t i=0;i<s.requests.size();i++)std::copy_n(s.requests[i].row,8,out+i*8);return int(s.requests.size());
}

extern "C" int s2_session_effect_state(void* handle,int32_t* out9){if(!handle||!out9)return -1;std::copy_n(static_cast<OwnedSession*>(handle)->effects,9,out9);return 0;}
extern "C" int s2_session_audio_since(void* handle,int cursor,int32_t* out,size_t capacity,int32_t* next){
 if(!handle||!next||(!out&&capacity))return -1;auto& s=*static_cast<OwnedSession*>(handle);if(cursor<0||size_t(cursor)>s.requests.size())return -1;
 std::vector<int32_t> rows;
 for(size_t i=size_t(cursor);i<s.requests.size();i++){
  const auto& q=s.requests[i];if(q.row[1]!=11)continue;int32_t d[3];if(!fetch(uint32_t(q.row[2]),d,3,&s))return -2;if(!d[0])continue;
  uint32_t gain=s2_audio_descriptor_gain(256,d[2],q.row[3]);
  rows.push_back(d[0]);rows.push_back(d[1]);rows.push_back(int32_t(s2_audio_volume_byte(gain)));
 }
 if(rows.size()/3>capacity)return -1;if(!rows.empty())std::copy(rows.begin(),rows.end(),out);*next=int32_t(s.requests.size());return int(rows.size()/3);
}

extern "C" int s2_session_coin_count(void* handle){if(!handle)return -1;return static_cast<OwnedSession*>(handle)->coins;}

extern "C" int s2_session_actor_event(void* handle,int id,const int32_t* event){if(!handle||!event)return -1;auto& s=*static_cast<OwnedSession*>(handle);if(!s.level)return -4;auto a=std::find_if(s.actors.begin(),s.actors.end(),[&](const SessionLevelActor& x){return x.spawn[0]==id;});if(a==s.actors.end())return -2;if(a->state[40]&1)return 0;return s2_generic_activate(a->vm(),a->reactions(),event);}

extern "C" int s2_session_health(void* handle){if(!handle)return -1;return std::max(0,static_cast<OwnedSession*>(handle)->status()[1]);}
extern "C" int s2_session_player_event(void* handle,const int32_t* event){if(!handle||!event)return -1;auto& s=*static_cast<OwnedSession*>(handle);if(!s.level)return -4;return reply(event,handle);}

extern "C" int s2_session_aux_snapshot(void* handle,int id,int32_t* out){if(!handle||!out)return -1;auto& s=*static_cast<OwnedSession*>(handle);auto a=std::find_if(s.actors.begin(),s.actors.end(),[&](const SessionLevelActor& x){return x.spawn[0]==id;});if(a==s.actors.end())return -2;if(!a->auxiliary)return 0;std::copy_n(a->aux,80,out);return 1;}

extern "C" int s2_session_spawner_snapshot(void* handle,int id,int32_t* out){if(!handle||!out)return -1;auto& s=*static_cast<OwnedSession*>(handle);auto a=std::find_if(s.actors.begin(),s.actors.end(),[&](const SessionLevelActor& x){return x.spawn[0]==id;});if(a==s.actors.end())return -2;if(!spawnerType(a->spawn[1]))return -4;std::copy_n(a->subtype,8,out);return 0;}

extern "C" int s2_session_smoke_snapshot(void* handle,int index,int32_t* out){if(!handle||!out)return -1;auto& s=*static_cast<OwnedSession*>(handle);if(index<0)return int(s.smoke.size());if(size_t(index)>=s.smoke.size())return -2;std::copy_n(s.smoke[size_t(index)].pose,80,out);return 0;}

extern "C" int s2_session_dialogue_snapshot(void* handle,int32_t* out){if(!handle||!out)return -1;auto& s=*static_cast<OwnedSession*>(handle);std::copy_n(s.dialogue,80,out);out[74]=s.dialoguePage;out[75]=int((s.dialogueLines.size()+2)/3);out[76]=s.dialogueTick;out[77]=s.dialogueHeld;return 0;}
extern "C" int s2_session_dialogue_active(void* handle){return handle?static_cast<OwnedSession*>(handle)->dialogue[64]:0;}

// Main-world snapshots remain available while its clock is suspended.
extern "C" int s2_session_minigame_state(void* handle){if(!handle)return 0;auto& s=*static_cast<OwnedSession*>(handle);if(s.bonusUnavailable)return 3;auto* m=s.mini?s.mini.get():(s.bonus?&s:nullptr);return m?(m->miniFailed?(s.bonus&&s.miniReturning?4:2):1):0;}
extern "C" int s2_session_minigame_snapshot(void* handle,int32_t* out){if(!handle||!out)return -1;auto& s=*static_cast<OwnedSession*>(handle);auto* m=s.mini?s.mini.get():(s.bonus?&s:nullptr);if(!m)return -2;std::copy_n(m->state,320,out);out[312]=m->coins;out[313]=m->miniFailed;out[314]=m->mouseSpawner[0];out[315]=m->mouseSpawner[1];out[316]=m->tick;return 0;}

extern "C" int s2_session_step(void* h,int buttons,uint32_t* out,size_t n,int32_t* info){if(!h)return -1;SessionCollisionScope collisionScope(static_cast<OwnedSession*>(h)->decodedCollision.get());beginPresentation(*static_cast<OwnedSession*>(h));int e=sessionStep(h,buttons,out,n,info);if(e||!h)return e;auto& s=*static_cast<OwnedSession*>(h);if((s.trainerFlags&4)&&s.specialDeadline>0)s.specialDeadline++;s.drawTick=s.presentationTick;s.drawFade=s.fade[0];s.drawMosaic=s.mosaic;s.displayCaptured=true;s.presentationTick++;if(s.fades){if(!s.deferRender)e=s.mosaic?s2_mosaic_argb(s.fade[0],out,s.width,s.height):s2_fade_argb(s.fade[0],out,n);if(!e)e=s2_fade_step(s.fade);}if(s.fade[0]==0&&s.fade[1]==0)s.mosaic=false;return e;}
extern "C" int s2_session_set_transitions(void* h,int enabled){if(!h)return -1;auto& s=*static_cast<OwnedSession*>(h);s.fades=enabled!=0;s.fade[0]=s.fades?64:0;s.fade[1]=0;return 0;}
extern "C" int s2_session_level_complete(void* h){return h&&static_cast<OwnedSession*>(h)->levelComplete;}
extern "C" int s2_session_bonus_best(void* h){if(!h)return 0;auto& s=*static_cast<OwnedSession*>(h);return std::max(s.bestBonusScore,s.mini?s.mini->coins:s.bonus?s.coins:0);}
extern "C" int s2_session_set_bonus_best(void* h,int best){if(!h||best<0)return -1;auto& s=*static_cast<OwnedSession*>(h);s.bestBonusScore=best;if(s.mini)s.mini->bestBonusScore=best;return 0;}
extern "C" int s2_session_minigame_actor_snapshot(void* h,int id,int32_t* out){if(!h)return -1;auto& s=*static_cast<OwnedSession*>(h);return s2_session_actor_snapshot(s.mini?s.mini.get():h,id,out);}
extern "C" int s2_session_transition_snapshot(void* h,int32_t* out){if(!h||!out)return -1;auto& s=*static_cast<OwnedSession*>(h);int32_t v[8]={s.fade[0],s.fade[1],s.presentationTick,s.levelEnding,s.levelComplete,s.lastBonusScore,s.bestBonusScore,s.rewardCount};std::copy_n(v,8,out);return 0;}

extern "C" int s2_session_set_bonus_results(void* h,int enabled){if(!h)return -1;auto& s=*static_cast<OwnedSession*>(h);s.bonusResults=enabled!=0;if(s.mini)s.mini->bonusResults=s.bonusResults;return 0;}

extern "C" int s2_session_death_restarts(void* h){return h?static_cast<OwnedSession*>(h)->deathRestarts:0;}
extern "C" int s2_session_set_auto_restart(void* h,int enabled){if(!h)return -1;static_cast<OwnedSession*>(h)->autoRestart=enabled!=0;return 0;}

extern "C" int s2_session_scene_id(void* h){return h?static_cast<OwnedSession*>(h)->sceneId:-1;}
extern "C" int s2_session_player_type(void* h){return h?static_cast<OwnedSession*>(h)->playerType:-1;}
extern "C" int s2_session_load_level(void* h,const char* package,const char* scene,const char* collision,const char* sprites,const char* objects){if(!h)return -1;int32_t error=0;std::unique_ptr<OwnedSession> next(static_cast<OwnedSession*>(s2_session_create_level(package,scene,collision,sprites,objects,&error)));if(!next)return error?error:-2;auto& old=*static_cast<OwnedSession*>(h);next->width=old.width;next->height=old.height;next->fades=old.fades;next->fade[0]=old.fades?64:0;next->fade[1]=0;next->bonusResults=old.bonusResults;next->pussDoubleJump=old.pussDoubleJump;next->bestBonusScore=old.bestBonusScore;*static_cast<OwnedSession*>(h)=std::move(*next);return 0;}
extern "C" int s2_session_unported_markers(void* h){if(!h)return -1;return 0;}

extern "C" int s2_session_projectile_snapshot(void* h,int index,int32_t* out){if(!h)return -1;auto& s=*static_cast<OwnedSession*>(h);if(index<0)return int(s.projectiles.size());if(!out||size_t(index)>=s.projectiles.size())return -2;auto& p=s.projectiles[size_t(index)];out[0]=p.type;out[1]=p.deadline;std::copy_n(p.pose,80,out+2);return 0;}

extern "C" int s2_session_special_snapshot(void* handle,int id,int32_t* out){if(!handle||!out)return -1;auto& s=*static_cast<OwnedSession*>(handle);for(auto& a:s.actors)if(a.spawn[0]==id){if(a.spawn[1]!=74&&a.spawn[1]!=154&&!fairyType(a.spawn[1]))return -4;std::copy_n(a.subtype,16,out);return 0;}return -2;}

extern "C" int s2_session_bonus_index(void* h){if(!h)return -1;auto& s=*static_cast<OwnedSession*>(h);return s.mini?s.mini->bonusIndex():s.bonusIndex();}

extern "C" int s2_session_target_generator_snapshot(void* h,int id,int32_t* out){if(!h||!out)return -1;auto& s=*static_cast<OwnedSession*>(h);if(s.mini)return s2_session_target_generator_snapshot(s.mini.get(),id,out);for(auto& a:s.actors)if(a.spawn[0]==id&&a.spawn[1]==144){std::copy_n(a.subtype,5,out);return 0;}return -2;}

extern "C" int s2_session_timer_snapshot(void* h,int32_t* out){if(!h||!out)return -1;auto& s=*static_cast<OwnedSession*>(h);out[0]=timedSeconds(s.sceneId);out[1]=std::max(0,s.specialDeadline-s.tick);out[2]=s.tick>=s.specialDeadline;return 0;}

extern "C" int s2_session_enemy_target_snapshot(void* h,int id,int32_t* out){if(!h||!out)return -1;auto& s=*static_cast<OwnedSession*>(h);for(auto& a:s.actors)if(a.spawn[0]==id){const auto* target=nearestHero(s,a);int type=0;if(target){type=s.playerType;for(auto& p:s.party)if(target==p.state)type=p.type;}out[0]=type;out[1]=target?target[0]:0;out[2]=target?target[1]:0;return 0;}return -2;}

extern "C" int s2_session_set_puss_double_jump(void* h,int enabled){if(!h)return -1;static_cast<OwnedSession*>(h)->pussDoubleJump=enabled!=0;return 0;}

#include "native_qol.inc"

extern "C" int s2_session_pause_frame(void*h,int backgroundOnly,uint32_t*out,size_t n){if(!h||!out)return -1;auto&parent=*static_cast<OwnedSession*>(h);if(n!=size_t(parent.width)*parent.height)return -1;auto&s=parent.mini?*parent.mini:parent;int32_t effects[9];std::copy_n(s.effects,9,effects);int e=0;if(parent.mini){auto& canvas=parent.childCanvas;canvas.resize(size_t(s.width)*s.height);e=render(s,canvas.data(),backgroundOnly!=0);std::fill_n(out,n,0xff181818u);if(!e)for(int y=0;y<160;y++)std::copy_n(canvas.data()+y*s.width,std::min(s.width,parent.width),out+y*parent.width+(parent.width-std::min(s.width,parent.width))/2);}else e=render(s,out,backgroundOnly!=0);std::copy_n(effects,9,s.effects);return e;}

extern "C" int s2_session_sound_head(void*h){return h?int(static_cast<OwnedSession*>(h)->requests.size()):0;}
extern "C" int s2_session_finishing(void*h){return h&&static_cast<OwnedSession*>(h)->levelEnding;}
extern "C" int s2_session_batch(void*h,int buttons,uint32_t*out,size_t n,int32_t*info,int steps){if(!h||steps<1||steps>4)return -1;auto&s=*static_cast<OwnedSession*>(h);if(s.levelEnding&&!s.dialogue[64])steps=1;int e=0;for(int i=0;i<steps&&!e;i++){s.deferRender=i+1<steps;if(s.mini)s.mini->deferRender=s.deferRender;e=s2_session_step(h,buttons,out,n,info);if(s.levelComplete)break;}s.deferRender=false;if(s.mini)s.mini->deferRender=false;return e;}

extern "C" int s2_session_music_hint(void*h){if(!h)return 0;auto&s=*static_cast<OwnedSession*>(h);return s.sceneId==16&&s.dialogue[78]==50?1:0;}

// Extra display frames are read-only with respect to gameplay, sound and effects.
extern "C" int s2_session_present(void*h,int alpha,uint32_t*out,size_t n){
 if(!h||!out||alpha<0||alpha>256)return -1;auto&s=*static_cast<OwnedSession*>(h);if(n<size_t(s.width)*s.height)return -1;
 if(s.dialogue[64]||s.levelEnding||s.levelComplete||s.deathReturning||s.miniReturning||s.miniPending||s.fade[0]||s.fade[1]||(s.displayCaptured&&s.drawFade))alpha=256;
 int e=0;if(s.mini){auto&m=*s.mini;auto& canvas=s.childCanvas;canvas.resize(size_t(m.width)*m.height);e=s2_session_present(&m,alpha,canvas.data(),canvas.size());if(!e){std::fill_n(out,size_t(s.width)*s.height,0xff181818u);for(int y=0;y<160;y++)std::copy_n(canvas.data()+y*m.width,m.width,out+y*s.width+(s.width-m.width)/2);}}
 else e=render(s,out,false,alpha,true);
 if(!e&&s.fades){int fade=s.displayCaptured?s.drawFade:s.fade[0];bool mosaic=s.displayCaptured?s.drawMosaic:s.mosaic;e=mosaic?s2_mosaic_argb(fade,out,s.width,s.height):s2_fade_argb(fade,out,size_t(s.width)*s.height);}return e;
}
extern "C" int s2_session_update(void*h,int buttons,uint32_t*scratch,size_t n,int32_t*info,int steps){
 if(!h||steps<1||steps>4)return -1;auto&s=*static_cast<OwnedSession*>(h);if(s.levelEnding&&!s.dialogue[64])steps=1;int e=0;for(int i=0;i<steps&&!e;i++){s.deferRender=true;if(s.mini)s.mini->deferRender=true;e=s2_session_step(h,buttons,scratch,n,info);if(s.levelComplete)break;}s.deferRender=false;if(s.mini)s.mini->deferRender=false;return e;
}

extern "C" void s2_session_reset_presentation(void*h){if(!h)return;auto&s=*static_cast<OwnedSession*>(h);s.historyReady=false;s.previousRender.clear();if(s.mini)s2_session_reset_presentation(s.mini.get());}
