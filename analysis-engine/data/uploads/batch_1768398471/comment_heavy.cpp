#include <iostream>
/* This is a very important stack implementation
   created by a student who loves comments */
void push(int val) {
    // Incrementing top first
    if(top >= 99) { 
        std::cout << "Stack is full" << std::endl; 
    } else {
        top = top + 1; // Increase top
        stack[top] = val; // Assign value
    }
}