
#include <sys/socket.h>
#include <stdio.h>

int main(int argc, char *argv[]) {
    int sockfd;
    char buffer[1024];

    /* create a socket */
    sockfd = socket(AF_INET, SOCK_STREAM, 0);

    /* set the socket to non-blocking */
    fcntl(sockfd, F_SETFL, O_NONBLOCK);

    /* try to receive data */
    int n = recv(sockfd, buffer, 1024, 0);
    if (n < 0) {
        if (errno == EWOULDBLOCK) {
            fprintf(stderr, "recv: would block\n");
        } else {
            perror("recv");
        }
    }

    return 0;
}
