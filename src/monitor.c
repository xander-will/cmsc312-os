#include <stdbool.h>

#include "queue.h"

struct monitor_struct {
    bool        val;
    queue       wait;
}

monitor mon_init() {
    monitor m = malloc(sizeof(struct monitor_struct));
    m->val = false;

}