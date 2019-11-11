#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#include "queue.h"
#include "macros.h"

#define INITIAL_SIZE 25
#define CHUNK 15

struct queue_struct {
    void    **a;
    int     len;
    int     space;
};

queue q_init() {
    queue q = malloc(sizeof(struct queue_struct));
    q->space = INITIAL_SIZE;
    q->a = malloc(sizeof(void*) * q->space);
    q->len = 0;

    return q;
}

void q_add(queue q, void *item) {
    if (q->space <= q->len) {
        q->space += CHUNK;
        void **temp = realloc(q->a, sizeof(void*) * q->space);
        free(q->a);
        q->a = temp;
    }

    q->a[q->len++] = item;
}

void q_remove(queue q, void *item) {
    for (int i = 0; i < q->len; i++)
        if (q->a[i] == item) {
            memcpy(q->a+i, q->a+i+1, sizeof(void*) * --q->len-i);
        }

    int overage = q->space - 2*CHUNK;
    if (overage > q->len && overage > INITIAL_SIZE) {
        q->space += CHUNK;
        void **temp = realloc(q->a, sizeof(void*) * q->space);
        free(q->a);
        q->a = temp;
    }
}

void q_clear(queue q) {
    q->len = 0;
}

size_t q_size(queue q) {
    return q->len;
}

bool q_isEmpty(queue q) {
    return q->len == 0;
}

void q_map(queue q, void (*cb)(void*)) {
    for (int i = 0; i < q->len; i++)
        cb(q->a[i]);
}

void q_sort(queue q, int (*cb)(const void*, const void*)) {
    qsort(q->a, q->len, sizeof(void*), cb);
}

void *q_pop(queue q) {
    if (q_isEmpty(q))
        return NULL;
    void *ret_val = q->a[0];
    memcpy(q->a, q->a+1, sizeof(void*) * --q->len);
    return ret_val;
}

void *q_index(queue q, int index) {
    if (index < 0 || index > q->len)
        return NULL;
    else
        return q->a[index];
}