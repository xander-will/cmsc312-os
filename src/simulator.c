#include "simulator.h"
#include "dispatcher.h"
#include "process.h"

struct sim_struct {
    int     mode;
    dispatcher  dis;
    int     delay_mode;
    int     delay;
    int     cycles_since_pause;
    bool    io;
    bool    io_cycles;
    int     total_cycles;
}

simulator sim_init(int delay_mode, int delay, int quantum, char **filelist, int fl_len) {
    simulator s = malloc(sizeof(struct sim_struct));
    s->dis = dis_init(quantum, filelist, fl_len);
    s->sim_mode = KERNAL_MODE;
    s->delay_mode = delay_mode;
    s->delay = (delay > 0) ? delay : 1;
    s->io = false;
    s->total_cycles = 0;

    DEBUG_PRINT("[Simulator] Successfully initialized!");    
    return s;
}

void sim_run(simulator s) {
    s->total_cycles++;
    DEBUG_PRINT("[Simulator] Cycle %d:", s->total_cycles);

    if (!s->io && (rand() % 10) < 3) { // io generation
        DEBUG_PRINT("[Simulator] IO event generated.");
        s->io = true;
        s->io_cycles = (rand() % 25) + 25; // between 25 - 50
        dis_io(s->dis, true);
    }
    else if (s->io) { // set limit on how long io can last
        if (s->io_cycles <= 0) {
            s->io = false;
            dis_io(s->dis, false);
        }
        else
            s->io_cycles--;
    }

    switch (s->mode) {
        case KERNAL_MODE:
            DEBUG_PRINT("[Simulator] In Kernel Mode.");
            dis_schedule(s->dis); 
            s->mode = USER_MODE;
            break;
        case USER_MODE:
            DEBUG_PRINT("[Simulator] In User Mode.");
            s->mode = dis_run(s->dis); 
            break;
    }

    if (s->delay_mode == D_MODE_PAUSE) {
        if (s->cycles_since_pause == s->delay) {
            s->cycles_since_pause = 0;
            system("pause");
        }
        else
            s->cycles_since_pause++;
    }
    else if (delay mode == D_MODE_DELAY)
        sleep(s->delay);
}