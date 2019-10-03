#include "simulator.h"

struct sim_struct {
    int     mode;
};

simulator sim_init() {
    simulator s = malloc(sizeof(struct sim_struct));
    s->sim_mode = KERNAL_MODE;
}