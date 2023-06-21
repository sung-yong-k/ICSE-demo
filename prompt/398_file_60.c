
#include <stdio.h>
#include <limits.h>

int third_largest(int arr[], int n) {
    if (n < 3) {
        return INT_MIN; // error value, array size is less than 3
    }

    int max1 = INT_MIN, max2 = INT_MIN, max3 = INT_MIN;

    for (int i = 0; i < n; i++) {
        if (arr[i] > max1) {
            max3 = max2;
            max2 = max1;
            max1 = arr[i];
        } else if (arr[i] > max2 && arr[i] != max1) {
            max3 = max2;
            max2 = arr[i];
        } else if (arr[i] > max3 && arr[i] != max2 && arr[i] != max1) {
            max3 = arr[i];
        }
    }

    return max3;
}

int main() {
    int arr[] = {10, 20, 30, 40, 50};
    int n = sizeof(arr) / sizeof(arr[0]);

    int third_largest_val = third_largest(arr, n);

    if (third_largest_val != INT_MIN) {
        printf("The 3rd largest value is: %d\n", third_largest_val);
    } else {
        printf("The array does not have 3 unique elements.\n");
    }

    return 0;
}
