#pragma once
#include <cstdint>
#include <cstddef>
extern "C" {
int s2_session_load_level(void*,const char*,const char*,const char*,const char*,const char*);
int s2_session_unported_markers(void*);
int s2_session_scene_id(void*);
int s2_session_player_type(void*);
int s2_session_party_snapshot(void*,int,int32_t*);
int s2_session_enemy_target_snapshot(void*,int,int32_t*); // type,XQ8,YQ8; zero if none
int s2_session_camera_snapshot(void*,int32_t*);
void* s2_session_create(const char* package,const char* scene,const char* collision,const char* spriteRoot,int32_t* error);
void* s2_session_create_level(const char* package,const char* scene,const char* collision,const char* spriteRoot,const char* objects,int32_t* error);
// info4: original row count, supported actors, skipped rows, player spawn ID.
int s2_session_world_info(void* session,int32_t* info4);
int s2_session_world_size(void* session,int32_t* widthHeight);
// Original ID -> pose80 + VM64 + reactions72.
int s2_session_actor_snapshot(void* session,int id,int32_t* state216);
int s2_session_spawner_snapshot(void* session,int id,int32_t* state8);
// Snapshot words74..77: native text page, page count, UI tick, previous buttons.
int s2_session_dialogue_snapshot(void* session,int32_t* state80);
int s2_session_dialogue_active(void* session);
// 0 main world, 1 bonus active, 2 failed/fading, 3 unavailable,
// 4 standalone bonus return-ready after a fully black frame.
int s2_session_minigame_state(void* session);
// Child state320, words312..316: score, failed, created mice, spawn timer, scene tick.
int s2_session_minigame_snapshot(void* session,int32_t* state320);
// Smoke index<0 returns live count; otherwise copies one pose80.
// Projectile index<0 returns count; otherwise type, reflection deadline and pose80.
int s2_session_projectile_snapshot(void* session,int index,int32_t* state82);
int s2_session_smoke_snapshot(void* session,int index,int32_t* state80);
int s2_session_aux_snapshot(void* session,int id,int32_t* state80);
// Explicit owner delivery for tests and future character/world event routes.
int s2_session_actor_event(void* session,int id,const int32_t* event3);
int s2_session_coin_count(void* session);
int s2_session_health(void* session);
// Owner event route, also used by enemy contacts. Returns accepted 0/1 or error.
int s2_session_player_event(void* session,const int32_t* event3);
int s2_session_set_puss_double_jump(void*,int);
int s2_session_set_transitions(void*,int);
int s2_session_death_restarts(void*);
// Disable only for isolated death-animation inspection; production defaults on.
int s2_session_set_auto_restart(void*,int);
int s2_session_set_bonus_results(void*,int);
int s2_session_level_complete(void*);
int s2_session_bonus_index(void*);
int s2_session_bonus_best(void*);
int s2_session_set_bonus_best(void*,int);
int s2_session_minigame_actor_snapshot(void*,int,int32_t*);
int s2_session_transition_snapshot(void*,int32_t*);
void s2_session_destroy(void* session);
int s2_session_reset(void* session);
// Presentation only. Width 240..640, height 160; invalid sizes leave state untouched.
int s2_session_set_viewport(void* session,int width,int height);
int s2_session_step(void* session,int buttons,uint32_t* argb,size_t pixelCount,int32_t* info8);
int s2_session_snapshot(void* session,int32_t* state320);
int s2_session_effect_state(void* session,int32_t* state9);
// Nondestructive request rows8: tick,kind,address,scale,parameters[4].
int s2_session_requests(void* session,int32_t* rows8,size_t capacity);
// Nondestructive audio view of request history. rows3: sound ID, priority, gain byte.
// nextCursor counts all world requests, not just sounds. Never advances the scene.
int s2_session_audio_since(void* session,int cursor,int32_t* rows3,size_t capacity,int32_t* nextCursor);
}

extern "C" {
int s2_session_save_state(void*,const char*);
int s2_session_load_state(void*,const char*);
int s2_session_saved_scene(const char*);
int s2_session_debug_info(void*,int32_t*);
int s2_session_debug_edit(void*,int,int,int,int);
int s2_session_debug_actors(void*,int32_t*,size_t);
int s2_session_render_current(void*,uint32_t*,size_t,int32_t*);
}

extern "C" int s2_session_pause_frame(void*,int,uint32_t*,size_t);

extern "C" {int s2_session_sound_head(void*);int s2_session_finishing(void*);int s2_session_batch(void*,int,uint32_t*,size_t,int32_t*,int);}

extern "C" int s2_session_music_hint(void*);

extern "C" {int s2_session_present(void*,int,uint32_t*,size_t);int s2_session_update(void*,int,uint32_t*,size_t,int32_t*,int);}

extern "C" void s2_session_reset_presentation(void*);

extern "C" {int s2_session_editor_entities(void*,int32_t*,size_t);int s2_session_editor_frame(void*,int,int,int,uint32_t*,size_t);}

extern "C" int s2_session_editor_thumbnail(void*,int,uint32_t*,size_t);

extern "C" int s2_session_editor_view(void*,int,int,int,int,int,int,int,uint32_t*,size_t);

extern "C" void s2_session_cancel_shoulders(void*);
