#pragma once

typedef unsigned char byte;

typedef enum {
    EXE         0,
    CALCULATE   1,
    IO          2,
    YIELD       3,
    OUT         4
} INSTR_ENUM;

typedef struct pcb_struct *process;