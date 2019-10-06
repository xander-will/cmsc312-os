#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>

#include "simulator.h"
#include "dispatcher.h"
#include "process.h"
#include "macros.h"
#include "queue.h"

typedef void (*scheduler)(dispatcher);

/* gonna keep these in here for now... might move them later */
void SimpleRoundRobin(dispatcher d);

struct dispatch_struct {
    queue           ready;  // adding more in the future obv
    queue           wait_io;
    process         current_proc;
    bool            io;
    scheduler       sch;
    int             quantum;
    int             quant_left;
    bool            idle;
    unsigned int    next_pid;
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

    d->current_proc = NULL; // about to be initialized by d->sch
    d->sch = SimpleRoundRobin;

    DEBUG_PRINT("[Dispatcher] Successfully initialized!");

    return d;
}

void dis_schedule(dispatcher d) {
    d->sch(d);
}

void dis_createProcess(dispatcher d, char *filename) {
    process p = pr_init(filename, d->next_pid++);
    if (p)
        q_add(d->ready, p);
}

bool dis_isIdle(dispatcher d) {
    return q_isEmpty(d->ready) && q_isEmpty(d->wait_io);
}

int dis_runCurrentProcess(dispatcher d) {
    /*  todo:
     *  - detect which queue is currently in play
     *    this will make more sense to do once
     *    multi level queues are added
     *  - uh... that might be it actually 
     */
    
    if (d->current_proc == NULL) // safety check
        return KERNAL_MODE;     // since I got a bit careless

    pr_ezprint(d->current_proc);
    INSTR_ENUM ins = pr_getCurrentInstr(d->current_proc);
    switch (ins) {
        case OUT:
            pr_ezprint(d->current_proc);
            pr_incrementPC(d->current_proc);
            return KERNAL_MODE;
        case EXE:
            q_remove(d->ready, d->current_proc);
            q_remove(d->wait_io, d->current_proc); // lol I wrote the ADT I can be lazy if I want
            pr_terminate(d->current_proc);
            d->current_proc = NULL;
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