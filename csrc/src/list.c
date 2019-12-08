#include <stdlib.h>
#include <stdbool.h>
#include <stdio.h>

#include "list.h"
#include "macros.h"

/* nodes */
struct node {
    void*           data;
    struct node*    next;
};

static struct node *createNode(void *p) {
    struct node *n = malloc(sizeof(struct node));
    n->data = p;
    n->next = NULL;

    return n;
}

static void destroyList(struct node *n) {
    DEBUG_PRINT("[List] Entering destroy list");
    if (n) {
        destroyList(n->next);
        free(n);
    }
    DEBUG_PRINT("[List] Entering destroy list");
}

static void removeNext(struct node *n) {
    struct node *temp = n->next;
    n->next = temp->next;
    free(temp);
}

/* list */
struct list_struct {
    size_t          size;
    struct node*    head;
    struct node*    tail;
};

list l_init() {
    DEBUG_PRINT("[List] Entering list init");
    list l = malloc(sizeof(struct list_struct));
    DEBUG_PRINT("[List] Successfully malloc'd");
    l->size = 0;
    l->head = NULL;

    DEBUG_PRINT("[List] Exiting list init");
    return l;
}

void l_free(list l) {
    destroyList(l->head);
    free(l);
}

void l_empty(list l) {
    destroyList(l->head);
    l->size = 0;
}

size_t l_size(list l) {
    return l->size;
}

void l_add(list l, void *p) {
    struct node *n = createNode(p);

    if (!l->head)
        l->head = l->tail = n;
    else
        l->tail = l->tail->next = n;

    l->size++;
}

void l_remove(list l, void *p) {
    struct node *n = l->head;

    if (n) {
        if (l->head->data == p) {
            free(l->head);
            l->head = n->next;
            l->size--;
        }
        else {
            while(n->next && n->next->data != p)
                n = n->next;
            if (n->next) {
                removeNext(n);
                l->size--;
                if (!n->next)
                    l->tail = n;
            }
        }
    }
}

bool l_contains(list l, void *p) {
    struct node *n = l->head;

    if (n) {
        do {
            if (n->data == p)
                return true;
        } while (n = n->next);
    }

    return false;
}

void *l_get(list l, int index) {
    struct node *n = l->head;

    if (index < 0 || l->size <= index)
        return NULL;

    for (int i = 0; i < index; i++)
        n = n->next;

    return n->data;
}
