#pragma once
// Passive bonuses stay attached while unarmed attacks run. Apple/key handling
// keeps its own throw/consume path; a key must not block Shrek's stomp.
// Lifted props keep their lift rules.
inline bool passiveCarryAttack(int mode){return mode==2||mode==3||mode==4||mode==5||mode==7;}
inline bool shrekAirAttackAllowed(int carried,int mode){return !carried||mode==6||passiveCarryAttack(mode);}
