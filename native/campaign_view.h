#pragma once
#include <cstdint>
#include <cstddef>
extern "C" {
void* s2_campaign_create(const char* root);
void s2_campaign_destroy(void*);
int s2_campaign_select_scene(void*,int sceneId);
int s2_campaign_navigate(void*,int delta);
// mode: 0 original map placements; 1 sprite gallery; 2 static-world traversal.
int s2_campaign_mode(void*,int mode);
int s2_campaign_bank(void*,int delta);
int s2_campaign_animation(void*,int delta);
int s2_campaign_pan(void*,int dx,int dy);
// option: 0 pause, 1 mirror X, 2 placements, 3 gallery scale 1..4.
int s2_campaign_option(void*,int option,int value);
int s2_campaign_can_walk(void*);
int s2_campaign_input(void*,int held);
int s2_campaign_character(void*,int type);
int s2_campaign_walk_info(void*,int32_t* info10);
int s2_campaign_walk_save(void*,int32_t* state100);
int s2_campaign_walk_restore(void*,const int32_t* state100);
int s2_campaign_step(void*,int ticks);
// info16: mode,scene,order,width,height,placements,bound,bank,animation,
// animationCount,sequenceCount,sequenceIndex,tick,song,cameraX,cameraY.
int s2_campaign_info(void*,int32_t* info16);
// Exact browser state12; independent of campaign save progress.
int s2_campaign_save(void*,int32_t* state12);
int s2_campaign_restore(void*,const int32_t* state12);
int s2_campaign_render(void*,int width,uint32_t*,size_t);
}
