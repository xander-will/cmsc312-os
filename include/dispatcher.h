#pragma once

typedef struct dispatch_struct *dispatcher;

dispatcher dis_init(dispatcher, int quant);
bool dis_run(dispatcher);
void dis_io(dispatcher, bool);