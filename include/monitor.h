#pragma once

typedef struct monitor_struct *monitor;

#define MONITOR_A 1
#define MONITOR_B 2
#define MONITOR_C 4

monitor mon_init();
bool mon_get(monitor);
void mon_set(monitor, bool);
bool mon_acquire(monitor, process);
process mon_release(monitor);