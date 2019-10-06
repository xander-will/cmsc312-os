#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <stdbool.h>
#include <string.h>
#include <dirent.h>

#include "simulator.h"
#include "main.h"
#include "macros.h"

#define FILEPATH "./processes/bytecode"

bool delay = false;
bool pause = false;
int quantum = 15;
int delay_time = 5;

int main(int argc, char **argv) {
    int fl_len;

    srand(time(0));
    
    ParseArgs(argc, argv);

    char **proc_files = ScrapeFiles(FILEPATH, &fl_len);

    simulator s = sim_init(delay ? D_MODE_DELAY : D_MODE_PAUSE, delay_time, quantum, proc_files, fl_len);
    while (1)
        sim_run(s);

    return 0; // force of habit lol
}

void ParseArgs(int argc, char **argv) {
    DEBUG_PRINT("Entering ParseArgs");
    int c;
    while ((c = getopt(argc, argv, "dpt:")) != -1) {
        switch (c) {
            case 'd':
                TRY(!pause);
                delay = true;
                break;
            case 'p':
                TRY(!delay);
                pause = true;
                break;
            case 't':
                TRY(delay_time = atoi(optarg));
                break;
            case 'q':
                TRY(quantum = atoi(optarg));
                break;
            case '?':
            default:
                DEBUG_PRINT("%c", c);
                TRY(THROW);
        }
    }
    return;

    CATCH (
        printf("Usage: xos [-d | -p] [-q QUANTUM] [-t DELAY_TIME]\n");
        printf("Flags\n");
        printf("\t-d\tWill cause the simulator to sleep between cycles\n");
        printf("\t-p\tWill cause the simulator to pause between cycles\n");
        printf("\t-q\tSets the time quantum\n");
        printf("\t-t\tEither how many cycles between pauses or how many seconds to sleep\n");
        printf("\nOnly one of either -d or -p can be present at any time");
        exit(EXIT_FAILURE);
    )
}

char **ScrapeFiles(char *folder, int *_len) {
    
    DIR *dr;
    struct dirent *de;
    char **filelist;
    int len;
    TRY(dr = opendir(folder));
    
    while (de = readdir(dr))
        len++;

    *_len = len;
    filelist = malloc(sizeof(char*) * len);
    rewinddir(dr);
    len = 0;
    while (de = readdir(dr)) {
        if (de->d_name[0] != '.') { // still need to figure out how to disable this
            filelist[len] = malloc(sizeof(char)*(strlen(de->d_name)+strlen(folder)+2));
            sprintf(filelist[len++], "%s/%s", folder, de->d_name);
        }
    }
    return filelist;

    CATCH (
        printf("Can't find %s... Now terminating", folder);
        exit(EXIT_FAILURE);
    )
}

/* not gonna worry about this rn but if I need it for later...
bool PFCheck(char *p) {
    do {
        if (p[0] == '.' &&
            p[1] == 'p' &&
            p[2] == 'f')
            return true;
    } while (*p++)

    return false;
} */