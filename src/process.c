#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "process.h"
#include "macros.h"
#include "list.h"
#include "memory.h"

#define STR_BUFFER_SIZE 250

/* instructions */
typedef struct {
    INSTR_ENUM      type;
    int             cycles;
    list            memory;
} instruction;

instruction *ins_init(INSTR_ENUM t, int c, int mem_size) {
    instruction *ins = malloc(sizeof(instruction*));
    ins->type = t;
    ins->cycles = c;
    ins->memory = mem_allocate(mem_size);

    return ins;
}


/* processes */
struct pcb_struct {
    int             pc;     // program counter
    instruction**   text;   // list of instructions
    int             text_len;
    int             memory; // memory allocated
    char*           name;   
    int             cycles_left; // cycles left in the quantum
    int             time;   // how long it's been running
    int             priority;
    unsigned int    pid;
};

static char *INSTR_NAME_TABLE[] = { 
                                    "EXE", 
                                    "CALCULATE",
                                    "IO",
                                    "YIELD",
                                    "OUT"
                                  };

process pr_init(char *filename, unsigned int pid, int *memory) {
    int i, num_instr;
    byte a[3], buffer[STR_BUFFER_SIZE];
    FILE *fp = fopen(filename, "rb");
    *memory = 0;

    process p = malloc(sizeof(struct pcb_struct));
    p->text = NULL; p->name = NULL;
    p->text_len = 0;

    TRY(fread(a, 1, 2, fp) == 2);  // sanity check: first two
    TRY(a[0] == 'p' && a[1] == 'f'); // bytes should be 'pf'

    for (i = 0; i < STR_BUFFER_SIZE; i++) { // filename
        TRY(fread(a, 1, 1, fp) == 1);
        if ((buffer[i] = a[0]) == '\0')
            break;
    }
    p->name = malloc(sizeof(char)*(i+1));
    strcpy(p->name, buffer);

    TRY(fread(a, 1, 2, fp) == 2);    // memory requirements
    p->memory = (a[0] << 8) | a[1];
    if (!mem_check(p->memory)) {
        *memory = p->memory;
        TRY(THROW);
    }
    
    TRY(fread(a, 1, 1, fp) == 1);    // instruction count
    i = a[0];
    p->text = malloc(sizeof(instruction*) * i);
    for (p->text_len = 0; p->text_len < i; p->text_len++) {
        TRY(fread(a, 1, 1, fp) == 1);
        if (a[0] == CALCULATE || a[0] == IO) {
            TRY(fread(a+1, 1, 1, fp) == 1);
            if (a[1] == 255)
                a[1] = (rand() % 5) + 10; // random value
        }
        else
            a[1] = 1;
        TRY(fread(a+2, 1, 1, fp) == 1);
        p->text[p->text_len] = ins_init(a[0], a[1], a[2]);        
    }
    fclose(fp);

    p->pc = p->priority = p->time = 0;
    p->cycles_left = p->text[0]->cycles;
    p->pid = pid;
    DEBUG_PRINT("[Process] Successfully opened %s (PID %d)!", filename, p->pid);
    return p;

    // FILE CLEANUP ON ERROR
    CATCH (
        fclose(fp);
        pr_terminate(p);
        if (*memory)
            printf("[Process] Error opening %s\n", filename);
        else
            printf("[Process] Not enough memory for %s\n", filename);
        return NULL;
    )
}

void pr_terminate(process p) {
    DEBUG_PRINT("[Process] Terminating PID %d.", p->pid);
    for (int i = 0; i < p->text_len; i++) {
        mem_deallocate(p->text[i]->memory);
        l_free(p->text[i]->memory);
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
    p->cycles_left--;
    p->time++;
    mem_access(p->text[p->pc]->memory);
    if (p->cycles_left == 0) {
        DEBUG_PRINT("[Process] PID %d just ended %s.", p->pid, INSTR_NAME_TABLE[pr_getCurrentInstr(p)]);
        p->cycles_left = p->text[++p->pc]->cycles;
        return false;
    }
    else {
        DEBUG_PRINT("[Process] PID %d just ran %s.", p->pid, INSTR_NAME_TABLE[pr_getCurrentInstr(p)]);
        return true; 
    }
}

INSTR_ENUM pr_getCurrentInstr(process p) {
    return p->text[p->pc]->type;
}

void pr_incrementPC(process p) {
    p->cycles_left = p->text[++p->pc]->cycles;
}

void pr_print(process p, FILE *fp, bool header) {
    if (header)
        fprintf(fp, "-------------\n");
    fprintf(fp, "Process ID %d:\n", p->pid);
    fprintf(fp, "\tName: %s\n", p->name);
    fprintf(fp, "\tMemory: %d bytes\n", p->memory);
    fprintf(fp, "\tElapsed time: %d cycles\n", p->time);
    fprintf(fp, "\tText section: %d instructions\n", p->text_len);
    fprintf(fp, "\tCurrent instruction: %s\n", INSTR_NAME_TABLE[p->text[p->pc]->type]);
    fprintf(fp, "\tTime left in current instruction: %d cycles\n", p->cycles_left);
    if (header)
        fprintf(fp, "-------------\n");
}