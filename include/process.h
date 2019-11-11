#pragma once

#include <stdio.h>

typedef unsigned char byte;

typedef enum {
    END         = -1, // this exists to signal the end of an instruction
    EXE         = 0,
    CALCULATE   = 1,
    IO          = 2,
    YIELD       = 3,
    OUT         = 4
} INSTR_ENUM;

typedef struct pcb_struct *process;

process pr_init(char *filename, unsigned int pid, int *memory);
void pr_terminate(process p);
bool pr_run(process p);
void pr_print(process p, FILE *fp, bool header);
INSTR_ENUM pr_getCurrentInstr(process p);
void pr_incrementPC(process p);
#define pr_ezprint(p) pr_print(p, stdout, true)