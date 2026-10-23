#include <jni.h>
#include <cstdint>
#include <cstdio>
#include <vector>
#include "../../../../../native/native_session.h"
namespace {
void fail(JNIEnv* env,const char* message){env->ThrowNew(env->FindClass("java/lang/IllegalStateException"),message);}
struct Utf {JNIEnv* env;jstring value;const char* text;Utf(JNIEnv* e,jstring v):env(e),value(v),text(v?e->GetStringUTFChars(v,nullptr):nullptr){}~Utf(){if(text)env->ReleaseStringUTFChars(value,text);}};
void* handle(jlong value){return reinterpret_cast<void*>(static_cast<intptr_t>(value));}
}
extern "C" JNIEXPORT jlong JNICALL Java_org_shrek2_research_SessionActivity_createSession(JNIEnv* env,jclass,jstring package,jstring scene,jstring collision,jstring sprites){
 Utf p(env,package),s(env,scene),c(env,collision),b(env,sprites);if(!p.text||!s.text||!c.text||!b.text){if(!env->ExceptionCheck())fail(env,"Could not load or update game resources");return 0;}
 int32_t error=0;void* session=s2_session_create(p.text,s.text,c.text,b.text,&error);if(!session){fail(env,"Could not load or update game resources");return 0;}return static_cast<jlong>(reinterpret_cast<intptr_t>(session));
}
extern "C" JNIEXPORT void JNICALL Java_org_shrek2_research_SessionActivity_destroySession(JNIEnv*,jclass,jlong session){s2_session_destroy(handle(session));}
extern "C" JNIEXPORT jlong JNICALL Java_org_shrek2_research_SessionActivity_createWorldSession(JNIEnv* env,jclass,jstring package,jstring scene,jstring collision,jstring sprites,jstring objects){
 Utf p(env,package),s(env,scene),c(env,collision),b(env,sprites),o(env,objects);if(!p.text||!s.text||!c.text||!b.text||!o.text){if(!env->ExceptionCheck())fail(env,"Could not load or update game resources");return 0;}
 int32_t error=0;void* session=s2_session_create_level(p.text,s.text,c.text,b.text,o.text,&error);if(!session){fail(env,"Could not load or update game resources");return 0;}s2_session_set_transitions(session,1);return static_cast<jlong>(reinterpret_cast<intptr_t>(session));
}
extern "C" JNIEXPORT void JNICALL Java_org_shrek2_research_SessionActivity_restartSession(JNIEnv* env,jclass,jlong session){if(s2_session_reset(handle(session)))fail(env,"Could not load or update game resources");}
extern "C" JNIEXPORT jintArray JNICALL Java_org_shrek2_research_SessionActivity_readSessionSounds(JNIEnv* env,jclass,jlong session,jint cursor){
 int32_t rows[256*3],next=0;int count=s2_session_audio_since(handle(session),cursor,rows,256,&next);if(count<0){fail(env,"Could not load or update game resources");return nullptr;}
 jintArray out=env->NewIntArray(1+count*3);if(!out)return nullptr;env->SetIntArrayRegion(out,0,1,&next);if(count&&!env->ExceptionCheck())env->SetIntArrayRegion(out,1,count*3,rows);return out;
}
extern "C" JNIEXPORT jintArray JNICALL Java_org_shrek2_research_SessionActivity_advanceSession(JNIEnv* env,jclass,jlong session,jint buttons,jint width,jint height,jintArray info){
 if(!session||!info||env->GetArrayLength(info)!=8){fail(env,"Could not load or update game resources");return nullptr;}
 // Allocate Java output first; a failed allocation must not consume a frame.
 if(width<240||width>640||height!=160){fail(env,"Could not load or update game resources");return nullptr;}
 jintArray out=env->NewIntArray(width*height);if(!out)return nullptr;std::vector<uint32_t> pixels(size_t(width)*height);int32_t status[8]={};int code=s2_session_set_viewport(handle(session),width,height);if(!code)code=s2_session_step(handle(session),buttons,pixels.data(),pixels.size(),status);
 if(code){char message[256];std::snprintf(message,sizeof(message),"Native error %d, frame %d, state %d, item %d. Restart in QoL.",code,status[0],status[1],status[3]);fail(env,message);return nullptr;}
 env->SetIntArrayRegion(info,0,8,reinterpret_cast<const jint*>(status));if(env->ExceptionCheck())return nullptr;
 env->SetIntArrayRegion(out,0,width*height,reinterpret_cast<const jint*>(pixels.data()));return out;
}

extern "C" JNIEXPORT jint JNICALL Java_org_shrek2_research_SessionActivity_readCoinCount(JNIEnv*,jclass,jlong session){return s2_session_coin_count(handle(session));}

extern "C" JNIEXPORT jint JNICALL Java_org_shrek2_research_SessionActivity_readHealth(JNIEnv*,jclass,jlong session){return s2_session_health(handle(session));}

extern "C" JNIEXPORT jboolean JNICALL Java_org_shrek2_research_SessionActivity_isDialogueActive(JNIEnv*,jclass,jlong session){return s2_session_dialogue_active(handle(session))?JNI_TRUE:JNI_FALSE;}

extern "C" JNIEXPORT jint JNICALL Java_org_shrek2_research_SessionActivity_readMinigameState(JNIEnv*,jclass,jlong session){return s2_session_minigame_state(handle(session));}

extern "C" JNIEXPORT jint JNICALL Java_org_shrek2_research_SessionActivity_readBonusBest(JNIEnv*,jclass,jlong h){return s2_session_bonus_best(handle(h));}
extern "C" JNIEXPORT void JNICALL Java_org_shrek2_research_SessionActivity_setBonusBest(JNIEnv*,jclass,jlong h,jint best){s2_session_set_bonus_best(handle(h),best);}
extern "C" JNIEXPORT jboolean JNICALL Java_org_shrek2_research_SessionActivity_isLevelComplete(JNIEnv*,jclass,jlong h){return s2_session_level_complete(handle(h))?JNI_TRUE:JNI_FALSE;}

extern "C" JNIEXPORT void JNICALL Java_org_shrek2_research_SessionActivity_setBonusResults(JNIEnv*,jclass,jlong h,jboolean enabled){s2_session_set_bonus_results(handle(h),enabled==JNI_TRUE);}

extern "C" JNIEXPORT jint JNICALL Java_org_shrek2_research_SessionActivity_readDeathRestarts(JNIEnv*,jclass,jlong h){return s2_session_death_restarts(handle(h));}

extern "C" JNIEXPORT void JNICALL Java_org_shrek2_research_SessionActivity_loadWorldSession(JNIEnv* env,jclass,jlong h,jstring package,jstring scene,jstring collision,jstring sprites,jstring objects){Utf p(env,package),s(env,scene),c(env,collision),b(env,sprites),o(env,objects);if(!p.text||!s.text||!c.text||!b.text||!o.text)return;int result=s2_session_load_level(handle(h),p.text,s.text,c.text,b.text,o.text);if(result)fail(env,"Could not load or update game resources");}

extern "C" JNIEXPORT jint JNICALL Java_org_shrek2_research_SessionActivity_readBonusIndex(JNIEnv*,jclass,jlong session){return s2_session_bonus_index(handle(session));}

extern "C" JNIEXPORT void JNICALL Java_org_shrek2_research_SessionActivity_setPussDoubleJump(JNIEnv*,jclass,jlong h,jboolean enabled){s2_session_set_puss_double_jump(handle(h),enabled);}
extern "C" JNIEXPORT jint JNICALL Java_org_shrek2_research_SessionActivity_saveQuickState(JNIEnv*e,jclass,jlong h,jstring path){Utf p(e,path);return p.text?s2_session_save_state(handle(h),p.text):-1;}
extern "C" JNIEXPORT jint JNICALL Java_org_shrek2_research_SessionActivity_quickStateScene(JNIEnv*e,jclass,jstring path){Utf p(e,path);return p.text?s2_session_saved_scene(p.text):-1;}
extern "C" JNIEXPORT jint JNICALL Java_org_shrek2_research_SessionActivity_loadQuickState(JNIEnv*e,jclass,jlong h,jstring path){Utf p(e,path);return p.text?s2_session_load_state(handle(h),p.text):-1;}
extern "C" JNIEXPORT jintArray JNICALL Java_org_shrek2_research_SessionActivity_debugInfo(JNIEnv*e,jclass,jlong h){int32_t a[14]={};if(s2_session_debug_info(handle(h),a))return nullptr;auto r=e->NewIntArray(14);if(r)e->SetIntArrayRegion(r,0,14,a);return r;}
extern "C" JNIEXPORT jint JNICALL Java_org_shrek2_research_SessionActivity_debugEdit(JNIEnv*,jclass,jlong h,jint cmd,jint a,jint b,jint c){int result=s2_session_debug_edit(handle(h),cmd,a,b,c);if(result>=0)s2_session_reset_presentation(handle(h));return result;}
extern "C" JNIEXPORT jintArray JNICALL Java_org_shrek2_research_SessionActivity_debugActors(JNIEnv*e,jclass,jlong h){int n=s2_session_debug_actors(handle(h),nullptr,0);if(n<0||n>256)return nullptr;std::vector<int32_t>a(n*4);s2_session_debug_actors(handle(h),a.data(),n);auto r=e->NewIntArray(n*4);if(r&&n)e->SetIntArrayRegion(r,0,n*4,a.data());return r;}
extern "C" JNIEXPORT jintArray JNICALL Java_org_shrek2_research_SessionActivity_advanceFast(JNIEnv*env,jclass,jlong h,jint buttons,jint width,jint height,jintArray info,jint steps){
 if(!h||!info||env->GetArrayLength(info)!=8||steps<0||steps>4||width<240||width>640||height!=160){fail(env,"Invalid frame request");return nullptr;}auto out=env->NewIntArray(width*height);if(!out)return nullptr;std::vector<uint32_t>p(size_t(width)*height);int32_t status[8]={};int e=s2_session_set_viewport(handle(h),width,height);if(!e&&steps==0)e=s2_session_render_current(handle(h),p.data(),p.size(),status);if(!e&&steps>0)e=s2_session_batch(handle(h),buttons,p.data(),p.size(),status,steps);if(e){fail(env,"Game update failed. Restart or load a state in QoL.");return nullptr;}env->SetIntArrayRegion(info,0,8,status);env->SetIntArrayRegion(out,0,width*height,reinterpret_cast<jint*>(p.data()));return out;
}

extern "C" JNIEXPORT jintArray JNICALL Java_org_shrek2_research_SessionActivity_pauseFrame(JNIEnv*e,jclass,jlong h,jint width,jboolean hide){if(!h||width<240||width>640){fail(e,"Invalid paused scene");return nullptr;}auto out=e->NewIntArray(width*160);if(!out)return nullptr;std::vector<uint32_t>p(size_t(width)*160);int result=s2_session_set_viewport(handle(h),width,160);if(!result)result=s2_session_pause_frame(handle(h),hide==JNI_TRUE,p.data(),p.size());if(result){fail(e,"Could not draw paused scene");return nullptr;}e->SetIntArrayRegion(out,0,width*160,reinterpret_cast<jint*>(p.data()));return out;}

extern "C" JNIEXPORT jint JNICALL Java_org_shrek2_research_SessionActivity_soundHead(JNIEnv*,jclass,jlong h){return s2_session_sound_head(handle(h));}

extern "C" JNIEXPORT jint JNICALL Java_org_shrek2_research_SessionActivity_musicHint(JNIEnv*,jclass,jlong h){return s2_session_music_hint(handle(h));}

namespace {thread_local std::vector<uint32_t> displayBuffer;}
extern "C" JNIEXPORT void JNICALL Java_org_shrek2_research_SessionActivity_updateSession(JNIEnv*e,jclass,jlong h,jint buttons,jint width,jintArray info,jint steps){if(!h||!info||e->GetArrayLength(info)!=8||width<240||width>640||steps<1||steps>4){fail(e,"Invalid update");return;}displayBuffer.resize(size_t(width)*160);int32_t state[8]={};int code=s2_session_set_viewport(handle(h),width,160);if(!code)code=s2_session_update(handle(h),buttons,displayBuffer.data(),displayBuffer.size(),state,steps);if(code){fail(e,"Game update failed");return;}e->SetIntArrayRegion(info,0,8,state);}
extern "C" JNIEXPORT void JNICALL Java_org_shrek2_research_SessionActivity_presentSession(JNIEnv*e,jclass,jlong h,jint width,jint alpha,jintArray pixels){if(!h||!pixels||width<240||width>640||e->GetArrayLength(pixels)!=width*160){fail(e,"Invalid display buffer");return;}displayBuffer.resize(size_t(width)*160);int code=s2_session_set_viewport(handle(h),width,160);if(!code)code=s2_session_present(handle(h),alpha,displayBuffer.data(),displayBuffer.size());if(code){fail(e,"Could not draw scene");return;}e->SetIntArrayRegion(pixels,0,width*160,reinterpret_cast<jint*>(displayBuffer.data()));}

extern "C" JNIEXPORT void JNICALL Java_org_shrek2_research_SessionActivity_resetPresentation(JNIEnv*,jclass,jlong h){s2_session_reset_presentation(handle(h));}

extern "C" JNIEXPORT jintArray JNICALL Java_org_shrek2_research_SessionActivity_editorEntities(JNIEnv*e,jclass,jlong h){int n=s2_session_editor_entities(handle(h),nullptr,0);if(n<0||n>259){fail(e,"Could not list scene objects");return nullptr;}std::vector<int32_t> rows(n*6);s2_session_editor_entities(handle(h),rows.data(),n);auto a=e->NewIntArray(n*6);if(a)e->SetIntArrayRegion(a,0,n*6,rows.data());return a;}
extern "C" JNIEXPORT void JNICALL Java_org_shrek2_research_SessionActivity_editorFrame(JNIEnv*e,jclass,jlong h,jint w,jint x,jint y,jintArray out){if(!out||e->GetArrayLength(out)!=w*160){fail(e,"Invalid editor buffer");return;}displayBuffer.resize(size_t(w)*160);if(s2_session_editor_frame(handle(h),w,x,y,displayBuffer.data(),displayBuffer.size())){fail(e,"Could not draw editor");return;}e->SetIntArrayRegion(out,0,w*160,reinterpret_cast<jint*>(displayBuffer.data()));}

extern "C" JNIEXPORT jintArray JNICALL Java_org_shrek2_research_SessionActivity_editorThumbnail(JNIEnv*e,jclass,jlong h,jint type){uint32_t pixels[4096];if(s2_session_editor_thumbnail(handle(h),type,pixels,4096)){fail(e,"Could not draw object preview");return nullptr;}auto a=e->NewIntArray(4096);if(a)e->SetIntArrayRegion(a,0,4096,reinterpret_cast<jint*>(pixels));return a;}

extern "C" JNIEXPORT void JNICALL Java_org_shrek2_research_SessionActivity_editorView(JNIEnv*e,jclass,jlong h,jint w,jint height,jint x,jint y,jint id,jint px,jint py,jintArray out){if(!h||w<60||w>1280||height<40||height>640||!out||e->GetArrayLength(out)!=w*height){fail(e,"Invalid editor view");return;}displayBuffer.resize(size_t(w)*height);if(s2_session_editor_view(handle(h),w,height,x,y,id,px,py,displayBuffer.data(),displayBuffer.size())){fail(e,"Could not draw edit preview");return;}e->SetIntArrayRegion(out,0,w*height,reinterpret_cast<jint*>(displayBuffer.data()));}

extern "C" JNIEXPORT void JNICALL Java_org_shrek2_research_SessionActivity_cancelShoulderGesture(JNIEnv*,jclass,jlong h){s2_session_cancel_shoulders(handle(h));}
