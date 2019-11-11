#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "simulator.h"
#include "dispatcher.h"
#include "process.h"
#include "macros.h"
#include "queue.h"
#include "monitor.h"

typedef void (*scheduler)(dispatcher);

/* gonna keep these in here for now... might move them later */
void SimpleRoundRobin(dispatcher d);

struct dispatch_struct {
    queue           ready;  // adding more in the future obv
    queue           wait_io;
    queue           wait_mem; // holds strings, not processes
    process         current_proc;
    bool            io;
    scheduler       sch;
    int             quantum;
    int             quant_left;
    bool            idle;
    unsigned int    next_pid;
    struct {
        monitor     a, b, c;
    }               mutexes;
};

dispatcher dis_yieldCurrProcess(dispatcher d) {
    if (d->current_proc) {
        q_add(pr_getCurrentInstr(d->current_proc) == IO ? d->wait_io : d->ready, d->current_proc);   // ugly way to
        d->current_proc = NULL;                                 // handle this
    }
}

dispatcher dis_init(int quant, char **filelist, int fl_len) {
    dispatcher d = malloc(sizeof(struct dispatch_struct));

    d->next_pid = 1;
    d->ready = q_init();
    d->wait_io = q_init();
    for (int i = 0; i < fl_len; i++) {
        int x = (rand() % 4) + 1;    // temp hardcoding of random processes
        DEBUG_PRINT("[Dispatcher] Initializing %d copies of %s...", x, filelist[i]);
        for (int j = 0; j < x ; j++) {
            dis_createProcess(d, filelist[i]);
        }
    }

    d->io = false;
    d->quantum = d->quant_left = quant;

    d->mutexes.a = mon_init(MONITOR_A);
    d->mutexes.b = mon_init(MONITOR_B);
    d->mutexes.c = mon_init(MONITOR_C);

    d->current_proc = NULL; // about to be initialized by d->sch
    d->sch = SimpleRoundRobin;

    DEBUG_PRINT("[Dispatcher] Successfully initialized!");

    return d;
}

void dis_schedule(dispatcher d) {
    d->sch(d);
}

void dis_createProcess(dispatcher d, char *filename) {
    int mem;

    process p = pr_init(filename, d->next_pid++, &mem);
    if (!p) {
        if (mem) {
            char *new_str = malloc(sizeof(char) * strlen(filename));
            strcpy(new_str, filename);
            q_add(d->wait_mem, new_str);
        }
    }
    else
        q_add(d->ready, p);
}

bool dis_isIdle(dispatcher d) {
    return q_isEmpty(d->ready) && q_isEmpty(d->wait_io);
}

void dis_addWaitingProcesses(dispatcher d) {
    int len = q_size(d->wait_mem);
    for (int i = 0; i < len; i++) {
        char *filename = q_pop(d->wait_mem);
        dis_createProcess(d, filename);
    }
}

static monitor monitorTable(dispatcher d, int mutex) {
    switch (mutex) {
        default: case MONITOR_A: return d->mutexes.a;
        case MONITOR_B: return d->mutexes.b;
        case MONITOR_C: return d->mutexes.c;
    }
}

static void monitorRelease(dispatcher d, int mon_num) { 
    if (pr_hasMutex(d->current_proc, mon_num)) {
        monitor m = monitorTable(d, mon_num);
        process p = mon_release(m);
        if (p) 
            q_add(d->ready, p);
    }
}

int dis_runCurrentProcess(dispatcher d) {
    /*  todo:
     *  - detect which queue is currently in play
     *    this will make more sense to do once
     *    multi level queues are added
     *  - uh... that might be it actually 
     */
    monitor m;
    if (d->current_proc == NULL) // safety check
        return KERNAL_MODE;     // since I got a bit careless

    pr_ezprint(d->current_proc);
    INSTR_ENUM ins = pr_getCurrentInstr(d->current_proc);
    switch (ins) {
        case ACQUIRE:
            m = monitorTable(d, pr_getInstrArg(d->current_proc));
            pr_incrementPC(d->current_proc);
            if (mon_acquire(m, d->current_proc))
                return USER_MODE;
            else {
                d->current_proc = NULL;
                return KERNAL_MODE;
            }
        case RELEASE:
            pr_incrementPC(d->current_proc);
            monitorRelease(d, pr_getInstrArg(d->current_proc));
            return KERNAL_MODE;
        case OUT:
            pr_ezprint(d->current_proc);
            pr_incrementPC(d->current_proc);
            return USER_MODE;
        case EXE:
            q_remove(d->ready, d->current_proc);
            q_remove(d->wait_io, d->current_proc); // lol I wrote the ADT I can be lazy if I want
            monitorRelease(d, MONITOR_A);
            monitorRelease(d, MONITOR_B);
            monitorRelease(d, MONITOR_C);
            pr_terminate(d->current_proc);
            d->current_proc = NULL;
            dis_addWaitingProcesses(d);
            return KERNAL_MODE;
        case YIELD:
            pr_incrementPC(d->current_proc);
            dis_yieldCurrProcess(d);
            return KERNAL_MODE;
        case IO:
            if (!d->io) {
                q_add(d->wait_io, d->current_proc); // lazy logic
                d->current_proc = NULL;            // but I'll fix it
                d->sch(d);                        // later...
                return USER_MODE;
            }
            if (d->io) {
                if (!pr_run(d->current_proc)) {
                    q_add(d->ready, d->current_proc);
                    d->current_proc = NULL;
                    return KERNAL_MODE;
                }
                else if (--d->quant_left == 0)
                    return KERNAL_MODE;
                else 
                    return USER_MODE;
            }
        case CALCULATE: default:
            if (!pr_run(d->current_proc) || --d->quant_left == 0)
                return KERNAL_MODE;
            else
                return USER_MODE;
    }
}

void dis_io(dispatcher d, bool flag) {
    d->io = flag;
    dis_yieldCurrProcess(d);
    d->sch(d);                        
    DEBUG_PRINT("[Dispatcher] IO mode is %s.", flag ? "on" : "off");
}


/*  schedulers  */

void SimpleRoundRobin(dispatcher d) {
    process p;
    queue q = !d->io ? d->ready : q_isEmpty(d->wait_io) ? d->ready : d->wait_io;

    if (d->current_proc)
        q_add(q, d->current_proc);
    TRY(p = q_pop(q));
    d->current_proc = p;

    d->quant_left = d->quantum;

    DEBUG_PRINT("[Dispatcher] Ran SimpleRoundRobin.");
    return;

    CATCH (
        d->idle = true;
        DEBUG_PRINT("[Dispatcher] Ran SimpleRoundRobin, is idle.");
    )
}