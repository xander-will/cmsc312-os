#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#include "process.h"
#include "queue.h"
#include "macros.h"
#include "monitor.h"

struct monitor_struct {
    int         id;
    bool        val;
    process     current;
    queue       wait;
};

monitor mon_init(int id) {
    monitor m = malloc(sizeof(struct monitor_struct));
    m->id = id;
    m->val = false;
    m->wait = q_init();
    m->current = NULL;

    return m;
}

bool mon_get(monitor m) {
    return m->val;
}

void mon_set(monitor m, bool b) {
    m->val = b;
}

bool mon_acquire(monitor m, process p) {
    if (m->current) {
        DEBUG_PRINT("[Monitor] Waiting on mutex");
        q_add(m->wait, p);
        return false;
    }
    else {
        DEBUG_PRINT("[Monitor] Acquiring mutex");
        m->current = p;
        pr_setMutex(p, m->id);
        return true;
    }
}

process mon_release(monitor m) {
    DEBUG_PRINT("[Monitor] Releasing mutex");
    pr_unsetMutex(m->current, m->id);
    m->current = q_pop(m->wait);
    if (m->current)
        pr_setMutex(m->current, m->id);
    return m->current;
}


