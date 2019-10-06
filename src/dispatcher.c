#include <stdio.h>

#include "simulator.h"
#include "dispatcher.h"
#include "process.h"
#include "macros.h"

typedef void (*scheduler)(dispatcher);

/* gonna keep these in here for now... might move them later */
void SimpleRoundRobin(dispatcher d);

struct dispatch_struct {
    queue       ready;  // adding more in the future obv
    queue       wait_io;
    process     current_proc;
    bool        io;
    scheduler   sch;
    int         quantum;
    int         quant_left;
    bool        idle;
};

dispatcher dis_init(int quant, char **filelist, int fl_len) {
    dispatcher d = malloc(sizeof(struct dispatch_struct));

    d->read = q_init();
    d->wait_io = q_init();
    for (int i = 0; i < fl_len; i++)
        dis_createProcess(d, filelist[i]);

    d->io = false;
    d->quantum = d->quant_left = quant;
    d->scheduler = SimpleRoundRobin;

    DEBUG_PRINT("[Dispatcher] Successfully initialized!");

    return d;
}

void dis_schedule(dispatcher d) {
    d->sch(d);
}

void dis_createProcess(dispatcher d, char *filename) {
    process p = p_init(filename);
    q_add(d->ready, p);
}

void dis_isIdle(dispatcher d) {
    return q_isEmpty(d->ready) && q_isEmpty(d->wait_io);
}

int dis_runCurrentProcess(dispatcher d) {
    /*  todo:
     *  - detect which queue is currently in play
     *    this will make more sense to do once
     *    multi level queues are added
     *  - uh... that might be it actually 
     */
    INSTR_ENUM ins = pr_run(current_proc);
    switch (ins) {
        case OUT:
            pr_ezprint(current_proc);
            break;
        case EXE:
            q_remove(d->ready, current_proc);
            q_remove(d->wait_io, current_proc); // lol I wrote the ADT I can be lazy if I want
            pr_terminate(current_proc);
        case END:
        case YIELD:
            
            return KERNAL_MODE;
        case IO:
            if (!d->io) {
                q_remove(d->ready, current_proc); // lazy logic
                q_add(d->wait_io, current_proc); // but I'll fix it
                d->sch(d);                      // later...
                return USER_MODE;
            }
        default:
            if (--d->quant_left == 0)
                return KERNAL_MODE;
            else
                return USER_MODE;
    }
}

void dis_io(dispatcher d, bool flag) {
    d->io = flag;
    d->sch(d);
    DEBUG_PRINT("[Dispatcher] IO mode is on.");
}


/*  schedulers  */

void SimpleRoundRobin(dispatcher d) {
    queue q = d->io ? d->wait_io : d->ready;

    TRY(process p = q_pop(q));
    q_add(q, p);

    d->quant_left = d->quantum;

    DEBUG_PRINT("[Dispatcher] Ran SimpleRoundRobin.");

    CATCH (
        d->idle = true;
        DEBUG_PRINT("[Dispatcher] Ran SimpleRoundRobin, is idle.");
    )
}