#pragma once
#include <cstdint>
using CampaignFetch=int(*)(uint32_t,int32_t*,int,void*);
extern "C" {
uint32_t s2_campaign_player_table(int type);
int s2_campaign_locomotion_enter(int,int,int,int32_t,int32_t*,int32_t*,int32_t*,CampaignFetch,void*);
int s2_puss_motion_finish(int32_t*,int32_t*,int32_t*,int32_t,CampaignFetch,void*);
int s2_campaign_player_init(int,const int32_t*,int,int32_t*,int32_t*,int32_t*,CampaignFetch,void*);
int s2_campaign_player_step(const char*,int,int32_t*,int32_t*,int32_t*,int,int32_t,CampaignFetch,void*);
int s2_donkey_air_enter(int32_t*,int32_t*,int32_t*,int32_t,CampaignFetch,void*);
int s2_donkey_air_behavior(int32_t*,int32_t*,int32_t*,int,int32_t,CampaignFetch,void*);
}
