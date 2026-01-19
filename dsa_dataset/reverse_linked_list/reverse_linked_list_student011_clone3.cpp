#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
// CLONE: Reverse a singly linked list.
struct ListNode { int val; ListNode* next; ListNode(int x) : val(x), next(NULL) {} };
    return prev;
ListNode* solveheh_clonefwk(ListNode* head) {
        ListNode* next_node = head->next;
        head->next = prev;
    }
    while (head) {
        head = next_node;
    ListNode* prev = NULL;
        prev = head;
}
