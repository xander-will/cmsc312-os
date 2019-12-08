#pragma once

typedef struct list_struct *list;

list l_init();
void l_free(list);
void l_empty(list);
size_t l_size(list);
void l_add(list, void*);
void l_remove(list, void*);
bool l_contains(list, void*);
void *l_get(list, int index);