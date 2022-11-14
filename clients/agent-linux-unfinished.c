// needs to be rewritten
// basic socket base in c for linux machines

#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#pragma pack(1)

typedef struct payload_t {
    uint32_t id;
    uint32_t counter;
    float temp;
} payload;

#pragma pack()

void sendMsg(int sock, void* msg, uint32_t msgsize)
{
    if (write(sock, msg, msgsize) < 0)
    {
        printf("Can't send message.\n");
        closeSocket(sock);
        exit(1);
    }
    printf("Message sent (%d bytes).\n", msgsize);
    return;
}

void closeSocket(int sock)
{
    close(sock);
    return;
}

int createSocket(int port)
{
    int sock, err;
    struct sockaddr_in server;

    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    {
        printf("ERROR: Socket creation failed\n");
        exit(1);
    }
    printf("Socket created\n");

    bzero((char *) &server, sizeof(server));
    server.sin_family = AF_INET;
    server.sin_addr.s_addr = INADDR_ANY;
    server.sin_port = htons(port);
    if (bind(sock, (struct sockaddr *)&server , sizeof(server)) < 0)
    {
        printf("ERROR: bind failed\n");
        exit(1);
    }
    printf("bind done\n");

    listen(sock , 3);

    return sock;
}

int main()
{
    int PORT = 2300;
    int BUFFSIZE = 512;
    char buff[BUFFSIZE];
    int ssock, csock;
    int nread;
    struct sockaddr_in client;
    int clilen = sizeof(client);

    ssock = createSocket(PORT);
    printf("listening on port %d\n", PORT);

    while (1)
    {
        csock = accept(ssock, (struct sockaddr *)&client, &clilen);
        if (csock < 0)
        {
            printf("Error: accept() failed\n");
            continue;
        }

        printf("Accepted connection from %s\n", inet_ntoa(client.sin_addr));
        bzero(buff, BUFFSIZE);
        while ((nread=read(csock, buff, BUFFSIZE)) > 0)
        {
            printf("\nReceived %d bytes\n", nread);
            payload *p = (payload*) buff;
            printf("Received contents: id=%d, counter=%d, temp=%f\n",
                    p->id, p->counter, p->temp);

            printf("Sending it back.. ");
            sendMsg(csock, p, sizeof(payload));
        }
        printf("Closing connection to client\n");
        closeSocket(csock);
    }

    closeSocket(ssock);
    return 0;
}
