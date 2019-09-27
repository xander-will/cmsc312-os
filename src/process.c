#include "process.h"

typedef enum {
    CALC,
    IO,
    YIELD,
    EXE
} INSTR_ENUM;

typedef struct {
    INSTR_ENUM      type;
    int             cycles;
} instruction;

struct pcb_struct {
    int             pc;     // program counter
    instruction*    text;
    int             memory; // memory allocated
    int             cycles; // cycles allotted
};

