
#include <stdio.h>
#include <stdlib.h>
#include <dirent.h>
#include <sys/stat.h>
#include <string.h>

void search_dir(char *path);

int main()
{
    char path[100];

    // Prompt user for the drive path to search
    printf("Enter drive path to search: ");
    scanf("%s", path);

    // Call search_dir function with specified path
    search_dir(path);

    return 0;
}

void search_dir(char *path)
{
    struct dirent *dp;
    struct stat st;
    DIR *dir = opendir(path);

    // Check if directory can be opened
    if (!dir) {
        printf("Error opening directory: %s\n", path);
        return;
    }

    // Loop through directory entries
    while ((dp = readdir(dir)) != NULL) {
        // Skip "." and ".." entries
        if (strcmp(dp->d_name, ".") == 0 || strcmp(dp->d_name, "..") == 0) {
            continue;
        }

        // Build the full path of the entry
        char full_path[200];
        sprintf(full_path, "%s/%s", path, dp->d_name);

        // Check the type of entry
        if (stat(full_path, &st) == -1) {
            printf("Error getting file status: %s\n", full_path);
            continue;
        }

        if (S_ISDIR(st.st_mode)) {
            // Recursively search subdirectories
            search_dir(full_path);
        } else {
            // Print the file name
            printf("%s\n", full_path);
        }
    }

    closedir(dir);
}
