#include <jni.h>
#include <cstdint>
#include <vector>
#include "../../../../../native/frontend.h"
namespace {void* h(jlong v){return reinterpret_cast<void*>(static_cast<intptr_t>(v));}
void fail(JNIEnv* e){e->ThrowNew(e->FindClass("java/lang/IllegalStateException"),"Could not load or update game resources");}}
extern "C" JNIEXPORT jlong JNICALL Java_org_shrek2_research_OriginalMenu_create(JNIEnv* e,jclass,jstring file,jstring sprites){if(!file||!sprites){fail(e);return 0;}const char* f=e->GetStringUTFChars(file,nullptr);if(!f)return 0;const char* s=e->GetStringUTFChars(sprites,nullptr);void* p=s?s2_frontend_create(f,s):nullptr;if(s)e->ReleaseStringUTFChars(sprites,s);e->ReleaseStringUTFChars(file,f);if(!p)fail(e);return static_cast<jlong>(reinterpret_cast<intptr_t>(p));}
extern "C" JNIEXPORT void JNICALL Java_org_shrek2_research_OriginalMenu_destroy(JNIEnv*,jclass,jlong v){s2_frontend_destroy(h(v));}
extern "C" JNIEXPORT void JNICALL Java_org_shrek2_research_OriginalMenu_open(JNIEnv* e,jclass,jlong v,jint p,jint c){if(s2_frontend_open(h(v),p,c))fail(e);}
extern "C" JNIEXPORT void JNICALL Java_org_shrek2_research_OriginalMenu_progress(JNIEnv* e,jclass,jlong v,jintArray p){if(!p||e->GetArrayLength(p)!=7){fail(e);return;}int32_t a[7];e->GetIntArrayRegion(p,0,7,a);if(!e->ExceptionCheck()&&s2_frontend_progress(h(v),a))fail(e);}
extern "C" JNIEXPORT void JNICALL Java_org_shrek2_research_OriginalMenu_step(JNIEnv* e,jclass,jlong v,jint b){if(s2_frontend_step(h(v),b))fail(e);}
extern "C" JNIEXPORT void JNICALL Java_org_shrek2_research_OriginalMenu_touch(JNIEnv* e,jclass,jlong v,jint x,jint y){if(s2_frontend_touch(h(v),x,y))fail(e);}
extern "C" JNIEXPORT jint JNICALL Java_org_shrek2_research_OriginalMenu_action(JNIEnv*,jclass,jlong v){return s2_frontend_action(h(v));}
extern "C" JNIEXPORT jintArray JNICALL Java_org_shrek2_research_OriginalMenu_snapshot(JNIEnv* e,jclass,jlong v){int32_t a[9];if(s2_frontend_snapshot(h(v),a)){fail(e);return nullptr;}auto out=e->NewIntArray(9);if(out)e->SetIntArrayRegion(out,0,9,a);return out;}
extern "C" JNIEXPORT jintArray JNICALL Java_org_shrek2_research_OriginalMenu_render(JNIEnv* e,jclass,jlong v){std::vector<uint32_t> a(38400);if(s2_frontend_render(h(v),a.data(),a.size())){fail(e);return nullptr;}auto out=e->NewIntArray(38400);if(out)e->SetIntArrayRegion(out,0,38400,reinterpret_cast<const jint*>(a.data()));return out;}

extern "C" JNIEXPORT void JNICALL Java_org_shrek2_research_OriginalMenu_restore(JNIEnv* e,jclass,jlong v,jintArray p){if(!p||e->GetArrayLength(p)!=9){fail(e);return;}int32_t a[9];e->GetIntArrayRegion(p,0,9,a);if(!e->ExceptionCheck()&&s2_frontend_restore(h(v),a))fail(e);}

extern "C" JNIEXPORT jint JNICALL Java_org_shrek2_research_OriginalMenu_sound(JNIEnv*,jclass,jlong v){return s2_frontend_sound(h(v));}

extern "C" JNIEXPORT jintArray JNICALL Java_org_shrek2_research_OriginalMenu_presentation(JNIEnv* e,jclass,jlong v){int32_t p[8];if(s2_frontend_presentation(h(v),p)){fail(e);return nullptr;}auto out=e->NewIntArray(8);if(out)e->SetIntArrayRegion(out,0,8,p);return out;}

extern "C" JNIEXPORT void JNICALL Java_org_shrek2_research_OriginalMenu_names(JNIEnv* e,jclass,jlong v,jstring names){if(!names){fail(e);return;}const char* p=e->GetStringUTFChars(names,nullptr);if(p){int r=s2_frontend_names(h(v),p);e->ReleaseStringUTFChars(names,p);if(r)fail(e);}}
extern "C" JNIEXPORT jstring JNICALL Java_org_shrek2_research_OriginalMenu_initials(JNIEnv* e,jclass,jlong v,jint slot){char p[4];if(s2_frontend_initials(h(v),slot,p)){fail(e);return nullptr;}return e->NewStringUTF(p);}

extern "C" JNIEXPORT void JNICALL Java_org_shrek2_research_OriginalMenu_testBooks(JNIEnv* e,jclass,jlong v,jboolean enabled){if(s2_frontend_test_books(h(v),enabled))fail(e);}

extern "C" JNIEXPORT void JNICALL Java_org_shrek2_research_OriginalMenu_chapterCoins(JNIEnv* e,jclass,jlong v,jintArray p){if(!p||e->GetArrayLength(p)!=75){fail(e);return;}int32_t a[75];e->GetIntArrayRegion(p,0,75,a);if(!e->ExceptionCheck()&&s2_frontend_chapter_coins(h(v),a))fail(e);}

extern "C" JNIEXPORT void JNICALL Java_org_shrek2_research_OriginalMenu_startupFade(JNIEnv* e,jclass,jlong v){if(s2_frontend_startup_fade(h(v)))fail(e);}

extern "C" JNIEXPORT void JNICALL Java_org_shrek2_research_OriginalMenu_bonusBests(JNIEnv* e,jclass,jlong v,jintArray p){if(!p||e->GetArrayLength(p)!=5){fail(e);return;}int32_t a[5];e->GetIntArrayRegion(p,0,5,a);if(!e->ExceptionCheck()&&s2_frontend_bonus_bests(h(v),a))fail(e);}

extern "C" JNIEXPORT jint JNICALL Java_org_shrek2_research_OriginalMenu_epilogue(JNIEnv*,jclass,jlong v,jint scene){return s2_frontend_epilogue(h(v),scene);}
