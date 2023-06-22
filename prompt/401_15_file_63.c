
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char** parse_string(const char* input, const char* delimiters, int* token_count) {
    char* str = strdup(input);
    char* token;
    int count = 0;
    char** tokens = NULL;

    token = strtok(str, delimiters);
    while (token != NULL) {
        ++count;
        tokens = realloc(tokens, count * sizeof(char*));
        tokens[count - 1] = strdup(token);
        token = strtok(NULL, delimiters);
    }

    free(str);
    *token_count = count;
    return tokens;
}

void free_tokens(char** tokens, int count) {
    for (int i = 0; i < count; ++i) {
        free(tokens[i]);
    }
    free(tokens);
}

int main() {
    const char* input = "This is a sample string, with some delimiters!";
    const char* delimiters = " ,!";
    int token_count;

    char** tokens = parse_string(input, delimiters, &token_count);

    for (int i = 0; i < token_count; ++i) {
        printf("Token %d: %s\n", i + 1, tokens[i]);
    }

    free_tokens(tokens, token_count);

    return 0;
}
