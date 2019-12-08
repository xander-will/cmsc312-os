#include <time.h>
#include <stdbool.h>
#include <stdio.h>

#include "memory.h"
#include "list.h"
#include "macros.h"

#define PHYSICAL 1
#define VIRTUAL -1
#define NOT_IN_MEM 0 

struct page {
    time_t      counter;
    int         location;
    int         index;
};

static struct page page_table[TOTAL_MEM] = {{0}};
static struct page *phys_mem[PHYSICAL_MEM] = {NULL};
static struct page *virt_mem[VIRTUAL_MEM] = {NULL};

static int mem_remaining = TOTAL_MEM;

bool mem_check(int size) {
    return size < mem_remaining;
}

list mem_allocate(int size) {
    DEBUG_PRINT("[Memory] Entering memory alloc");
    if (size > mem_remaining)
        return NULL;

    list page_list = l_init();

    DEBUG_PRINT("[Memory] List initialized");
    for (int i = 0; i < TOTAL_MEM; i++) {
        if (!page_table[i].location) {
            DEBUG_PRINT("[Memory] Found page");
            page_table[i].index = -1;
            for (int j = 0; j < PHYSICAL_MEM; j++) {
                if (!phys_mem[j]) {
                    DEBUG_PRINT("[Memory] Allocating in physical memory");
                    phys_mem[j] = &page_table[i];
                    page_table[i].index = j;
                    page_table[i].location = PHYSICAL;
                    break;
                }
            }
            if (page_table[i].index == -1) {
                for (int j = 0; j < VIRTUAL_MEM; j++) {
                    if (!virt_mem[j]) {
                        DEBUG_PRINT("[Memory] Allocating in virtual memory");
                        virt_mem[j] = &page_table[i];
                        page_table[i].index = j;
                        page_table[i].location = VIRTUAL;
                        break;
                    }
                }
            }
            page_table[i].counter = time(0);
            l_add(page_list, &page_table[i]);
            mem_remaining--;
            if (l_size(page_list) == size)
                break;
        }
    }

    return page_list;
}

void mem_deallocate(list page_list) {
    //DEBUG_PRINT("[Memory] Deallocating memory");
    for (int i = 0; i < l_size(page_list); i++) {
        struct page *p = l_get(page_list, i);
        if (p->location == PHYSICAL) {
            phys_mem[p->index] == NULL;
        }
        else {
            virt_mem[p->index] == NULL;
        }

        p->location = NOT_IN_MEM;
        mem_remaining++;
    }
}

static struct page *findLeastUsed() {
    int lu_ind;
    time_t min;
    bool first_time = true;

    for (int i = 0; i < PHYSICAL_MEM; i++) {
        if (phys_mem[i]) {
            if (first_time) {
                min = phys_mem[i]->counter;
                lu_ind = i;
                first_time = false;
            }
            else {
                if (phys_mem[i]->counter < min) {
                    min = phys_mem[i]->counter;
                    lu_ind = i;
                }
            }
        }
    }

    return phys_mem[lu_ind];
}

void mem_access(list page_list) {
    for (int i = 0; i < l_size(page_list); i++) {
        struct page *p = l_get(page_list, i);

        if (p->location == VIRTUAL) {
            struct page *swap_p = findLeastUsed();
            DEBUG_PRINT("[Memory] Swapping page into slot %d", swap_p->index);
            phys_mem[swap_p->index] = p;
            virt_mem[p->index] = swap_p;

            int temp = p->index;
            p->index = swap_p->index;
            swap_p->index = temp;
        }

        p->counter = time(0);
    }
}