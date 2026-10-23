#pragma once
// Original chapters 1-5, 2-5, 5-1 and 5-5 have no collectible-coin quota.
inline int levelCoinTarget(int scene){return scene==17||scene==5||scene==20||scene==16?0:40;}
