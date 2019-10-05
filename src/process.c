#include <stdio.h>
#include <stdbool.h>
#include <string.h>

#include "process.h"

#define STR_BUFFER_SIZE 250;

#define TRY(expr) if (!(expr)) goto catch

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
        if (a[0] == CALCULATE || a[0] == IO)
            TRY(fread(a+1, 1, 1, fp) == 1);
        p->text[i] = ins_init(a[0], a[1]);        
    }
    p->text[0]->type 
    close(fp);

    p->pc = p->priority = p->time = 0;
    return p;

    // FILE CLEANUP ON ERROR
    catch:
        close(fp);
        pr_terminate(p);
        printf("Error opening %s\n", filename);
        return NULL;
}

void pr_terminate(process p) {
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

}

// add instructions now?