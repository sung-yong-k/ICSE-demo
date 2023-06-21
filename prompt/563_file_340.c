
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/syscall.h>

#define __NR_cp_range 285

int main() {
    int size = 10;
    int str_len = 32;
    char *array = malloc(size * str_len * sizeof(char));

    // Initialize the array with strings
    for (int i = 0; i < size; i++) {
        snprintf(array + i * str_len, str_len, "Original string %d", i);
    }

    // Take the first checkpoint
    syscall(__NR_cp_range, array, array + size * str_len - 1);

    // Modify data in the array
    for (int i = 0; i < size; i++) {
        snprintf(array + i * str_len, str_len, "Modified string %d", i);
    }

    // Take the second checkpoint
    syscall(__NR_cp_range, array, array + size * str_len - 1);

    // Free the allocated memory
    free(array);

    return 0;
}
