
class Queue {
    int data[100];
    int front = 0, rear = 0;
public:
    void enqueue(int x) { data[rear++] = x; }
    int dequeue() { return data[front++]; }
};
