#pragma once

typedef struct queue_struct *queue;

queue q_createQueue(void);
void q_add(queue, void*);
void q_remove(queue, void*);
void q_clear(queue);
void q_map(queue q, void (*cb)(void*));
void q_sort(queue q, int (*cb)(void*, void*));
void *q_pop(queue q);