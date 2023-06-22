#include <stdio.h>
#include <stdlib.h>

typedef struct linkedList
{
    int first;
    struct linkedList* rest; // change to struct linkedList*
} linkedList;

linkedList makeList(int a, int b, int c);
void addToList(linkedList* ll, int a);

int main()
{
    linkedList ll = makeList(1, 3, 5);
    addToList(&ll, 7);
    addToList(&ll, 9);
    return 0;
}

linkedList makeList(int a, int b, int c)
{
    linkedList* first = (linkedList*)malloc(sizeof(linkedList));
    first->first = a;
    linkedList* second = (linkedList*)malloc(sizeof(linkedList));
    second->first = b;
    linkedList* third = (linkedList*)malloc(sizeof(linkedList));
    third->first = c;
    third->rest = NULL;
    second->rest = third;
    first->rest = second;
    return *first; // changed to dereference first
}

void addToList(linkedList* ll, int a)
{
    while (ll->rest) // check for ll->rest instead of *ll
    {
        ll = ll->rest;
    }

    linkedList *newL = (linkedList*)malloc(sizeof(linkedList));
    newL->first = a;
    newL->rest = NULL;
    ll->rest = newL;
}