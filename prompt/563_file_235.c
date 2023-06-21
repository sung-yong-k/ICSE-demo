
#include <stdio.h>
#include <stdarg.h>

int main() {
    int fd = 1; // file descriptor for stdout (1 is standard output)
    const char* format = "This is a %s with %d arguments.\n";
    const char* arg1 = "test";
    int arg2 = 2;
    
    vdprintf(fd, format, va_start((char *) &arg1, arg2));
    
    return 0;
}
