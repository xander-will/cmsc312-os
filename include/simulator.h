#pragma once

#define KERNAL_MODE 0
#define USER_MODE   1

#define D_MODE_PAUSE    0
#define D_MODE_RUN      1

typedef struct sim_struct *simulator;

simulator sim_init(int delay_mode, int delay, int quantum) {
void sim_run(simulator s);