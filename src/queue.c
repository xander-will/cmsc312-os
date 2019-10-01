#include <stdlib.h>

#include "queue.h"

#define INITIAL_SIZE 25
#define CHUNK 15

struct queue_struct {
    void    *a;
    int     len;
    int     space;
};

queue q_createQueue() {
    queue q = malloc(sizeof(struct queue_struct));
    q->space = INITIAL_SIZE;
    q->a = malloc(sizeof(void*) * q->space);
    q->len = 0;

    return q;
}

void q_add(queue q, void *item) {
    if (q->space <= q->len) {
        q->space += CHUNK;
        void *temp = realloc(sizeof(void*), q->space);
        free(q->a);
        q->a = temp;
    }

    q->a[q->len++] = item;
}

void q_remove(queue q, void *item) {
    for (int i = 0; i < q->len; i++)
        if (q[i] == item)
            memcpy(q+i, q+i+1, sizeof(void*) * (q->len-i-1));

    int overage = q->space - 2*CHUNK;
    if (overage > s->) // to-do: finish realloc coding
}

void q_clear(queue q) {
    q->len = 0;
}

void q_map(queue q, void (*cb)(void*)) {
    for (int i = 0; i < q->len; i++)
        cb(q[i]);
}

void q_sort(queue q, int (*cb)(void*, void*)) {
    qsort(q->a, q->len, sizeof(void*), cb);
}


void *q_pop(queue q) {
    /* still deciding whether I want to
        make this return/remove the top or just
        return it */
    q->a[0];
}