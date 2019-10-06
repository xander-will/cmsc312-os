#pragma once

#define KERNAL_MODE 0 // need to turn these // also need to spell this right..... :(
#define USER_MODE   1 // into an enum...

#define D_MODE_PAUSE    0
#define D_MODE_DELAY    1

typedef struct sim_struct *simulator;

simulator sim_init(int delay_mode, int delay, int quantum, char**, int fl_len);
void sim_run(simulator s);