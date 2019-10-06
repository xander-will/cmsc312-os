#include <stdio.h>
#include <stdbool.h>
#include <string.h>

#include "process.h"
#include "macros.h"

#define STR_BUFFER_SIZE 250;

/* instructions */
typedef struct {
    INSTR_ENUM      type;
    int             cycles;
} instruction;

instruction *ins_init(INSTR_ENUM t, int c) {
    instruction *ins = malloc(sizeof(instruction*));
    ins->type = t;
    ins->cycles = c;

    return ins;
}


/* processes */
struct pcb_struct {
    int             pc;     // program counter
    instruction*    text;   // list of instructions
    int             text_len;
    int             memory; // memory allocated
    char*           name;   
    int             cycles_left; // cycles left in the quantum
    int             time;   // how long it's been running
    int             priority;
};

static char *INSTR_NAME_TABLE["EXE", 
                              "CALCULATE",
                              "IO",
                              "YIELD",
                              "OUT"];

process pr_init(char *filename) {
    int i, num_instr;
    byte a[2], filename[STR_BUFFER_SIZE];
    FILE *fp = fopen(filename, "rb");

    process p = malloc(sizeof(struct pcb_struct));
    p->instruction = p->name = NULL;
    p->text_len = 0;
    
    TRY(fread(a, 1, 2, fp) == 2);  // sanity check: first two
    TRY(a[0] == 'p' && a[1] == 'f'); // bytes should be 'pf'

    for (i = 1; i <= STR_BUFFER_SIZE; i++) { // filename
        TRY(fread(a, 1, 1, fp) == 1);
        if ((filename[0] = a[0]) == '\0')
            break;
    }
    p->name = malloc(sizeof(char)*i);
    strcpy(p->name, filename);

    TRY(fread(a, 1, 2, fp) == 2);    // memory requirements
    p->memory = (a[1] << 8) | a[0];
    
    TRY(fread(a, 1, 1, fp) == 1);    // instruction count
    i = a[0];
    p->text = malloc(sizeof(instruction*) * p->text_len);
    for (p->text_len = 0; p->text_len < i; p->text_len++) {
        TRY(fread(a, 1, 1, fp) == 1);
        if (a[0] == CALCULATE || a[0] == IO) {
            TRY(fread(a+1, 1, 1, fp) == 1);
            if (a[1] == 255)
                a[1] = (rand() % 25) + 25; // random value
        }
        p->text[i] = ins_init(a[0], a[1]);        
    }
    p->text[0]->type 
    close(fp);

    p->pc = p->priority = p->time = 0;
    DEBUG_PRINT("[Process] Successfully opened %s!", filename);
    return p;

    // FILE CLEANUP ON ERROR
    CATCH (
        close(fp);
        pr_terminate(p);
        printf("[Process] Error opening %s\n", filename);
        return NULL;
    )
}

void pr_terminate(process p) {
    DEBUG_PRINT("[Process] Terminating %s.", p->name);
    for (int i = 0; i < p->text_len; i++) {
        free(p->text[i]);
    }
    free(p->text);
    free(p->name);
    free(p);
}

void pr_setTime(process p, int time) {
    p->cycles_left = time;
}

bool pr_run(process p) {
    INSTR_ENUM curr_instr = p->instructions[pc]        
    if (curr_instr == CALCULATE || curr_instr == IO) {
        p->cycles_left--;
        if (p->cycles_left == 0) {
            p->pc++;
            DEBUG_PRINT("[Process] %s just ended %s.", p->name, INSTR_NAME_TABLE[curr_instr]);
            return END;
        }
    }
    else
        p->pc++;

    DEBUG_PRINT("[Process] %s just ran %s.", p->name, INSTR_NAME_TABLE[curr_instr]);
    return curr_instr; 
}

void pr_print(process p, FILE *fp, bool header) {
    if (header)
        fprintf(fp, "-------------\n");
    fprintf(fp, "Process: %s\n", p->name);
    fprintf(fp, "\tMemory = %d bytes\n", p->memory);
    fprintf(fp, "\tElapsed time: %d cycles\n", p->time);
    fprintf(fp, "\tText section: %d instructions", p->text_len);
    fprintf(fp, "\tCurrent instruction: %s\n", INSTR_NAME_TABLE[p->text[pc]->type]);
    if (header)
        fprintf(fp, "-------------\n");
}