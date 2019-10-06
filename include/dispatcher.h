#pragma once

typedef struct dispatch_struct *dispatcher;

dispatcher dis_init(int quant, char**, int fl_len);
void dis_createProcess(dispatcher, char*);
void dis_isIdle(dispatcher d);
bool dis_runCurrentProcess(dispatcher);
void dis_io(dispatcher, bool);
void dis_schedule(dispatcher);