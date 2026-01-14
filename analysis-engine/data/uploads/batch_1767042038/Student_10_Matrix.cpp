#include <iostream>
using namespace std;

int main() {
    int r1 = 2, c1 = 2, r2 = 2, c2 = 2;
    int m1[2][2] = {{1, 2}, {3, 4}};
    int m2[2][2] = {{5, 6}, {7, 8}};
    int res[2][2];

    // Matrix Multiplication
    for(int i = 0; i < r1; ++i)
        for(int j = 0; j < c2; ++j) {
            res[i][j] = 0;
            for(int k = 0; k < c1; ++k)
                res[i][j] += m1[i][k] * m2[k][j];
        }

    cout << "Output Matrix: " << endl;
    for(int i = 0; i < r1; ++i)
        for(int j = 0; j < c2; ++j)
            cout << res[i][j] << " ";

    return 0;
}