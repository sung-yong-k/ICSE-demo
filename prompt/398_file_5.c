
#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <string.h>
#include <unistd.h>
#include <sys/select.h>

#define PORT 8080
#define MAX_CLIENTS 10

int main(int argc, char const *argv[])
{
    int server_fd, new_socket, valread;
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);
    char buffer[1024] = {0};
    char *hello = "Hello from server";
    int client_sockets[MAX_CLIENTS] = {0};
    fd_set readfds;
    int max_sd;

    // Creating socket file descriptor
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0)
    {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    // Forcefully attaching socket to the port 8080
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt)))
    {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    // Forcefully attaching socket to the port 8080
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0)
    {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }
    if (listen(server_fd, 3) < 0)
    {
        perror("listen");
        exit(EXIT_FAILURE);
    }

    // Add the server socket to the set of file descriptors to monitor
    FD_ZERO(&readfds);
    FD_SET(server_fd, &readfds);
    max_sd = server_fd;

    while (1)
    {
        // Wait for activity on any of the monitored file descriptors
        int activity = select(max_sd + 1, &readfds, NULL, NULL, NULL);
        if (activity < 0)
        {
            perror("select error");
            exit(EXIT_FAILURE);
        }

        // If the server socket is ready, accept the new client connection
        if (FD_ISSET(server_fd, &readfds))
        {
            if ((new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen)) < 0)
            {
                perror("accept");
                exit(EXIT_FAILURE);
            }

            // Add the new client socket to the set of file descriptors to monitor
            for (int i = 0; i < MAX_CLIENTS; i++)
            {
                if (client_sockets[i] == 0)
                {
                    client_sockets[i] = new_socket;
                    break;
                }
            }

            // Update the maximum file descriptor number
            if (new_socket > max_sd)
            {
                max_sd = new_socket;
            }

            // Log the new connection
            printf("New client connected: %s:%d\n", inet_ntoa(address.sin_addr), ntohs(address.sin_port));
        }

        // Check all client sockets for incoming data
        for (int i = 0; i < MAX_CLIENTS; i++)
        {
            int sd = client_sockets[i];
            if (FD_ISSET(sd, &readfds))
            {
                valread = read(sd, buffer, 1024);
                if (valread == 0)
                {
                    // Client disconnected
                    printf("Client disconnected
