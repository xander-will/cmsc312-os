#pragma once

#define PHYSICAL_MEM 4096
#define VIRTUAL_MEM 8192

#define TOTAL_MEM PHYSICAL_MEM + VIRTUAL_MEM

#include "list.h"
bool mem_check(int size);
list mem_allocate(int size);
void mem_deallocate(list);
void mem_access(list);