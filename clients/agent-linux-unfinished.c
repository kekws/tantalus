// updated the linux agent becuz the project seemed cool and I need to get better at C fr

// idk if this works or not yet try it out or something

// tell me if this works or not idk

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>

#pragma pack(1)
typedef struct payload_t {
  uint32_t id;
  uint32_t counter;
  float temp;
} payload;

#pragma pack()

void closeSocket(int sock) {
  close(sock);
}

int createSocket(int port) {
  int sock, err;
  struct sockaddr_in server;
  sock = socket(AF_INET, SOCK_STREAM, 0);
  if (sock < 0) {
    perror("ERROR: Socket creation failed");
    exit(1);
  }
  printf("Socket created\n");
  memset((char*)&server, 0, sizeof(server));
  server.sin_family = AF_INET;
  server.sin_addr.s_addr = INADDR_ANY;
  server.sin_port = htons(port);
  if (bind(sock, (struct sockaddr *)&server , sizeof(server)) < 0) {
    perror("ERROR: Bind failed");
    closeSocket(sock);
    exit(1);
  }
  printf("Bind done\n");
  if (listen(sock , 3) < 0) {
    perror("ERROR: Listen failed");
    closeSocket(sock);
    exit(1);
  }
  return sock;
}
void sendMsg(int sock, void* msg, uint32_t msgsize) {
  
  if (write(sock, msg, msgsize) <= 0) {
    perror("Can't send message.");
    closeSocket(sock);
    exit(1);
  }
  printf("Message sent (%d bytes).\n", msgsize);
}
int main() {
  int PORT = 2300;
  
  int BUFFSIZE = 512;
  
  char buff[BUFFSIZE];
  int ssock, csock;
  int nread;
  struct sockaddr_in client;
  int clilen = sizeof(client);
  ssock = createSocket(PORT);
  printf("listening on port %d\n", PORT);
  while (1) {
    csock = accept(ssock, (struct sockaddr *)&client, &client);
    if (csock < 0) {
      perror("Error: accept() failed");
      continue;
    }
    printf("Accepted connection from %s\n", inet_ntoa(client.sin_addr));
    memset(buff, 0, BUFFSIZE);
    while ((nread=read(csock, buff, BUFFSIZE)) > 0) {
      printf("\nReceived %d bytes\n", nread);
      
      payload *p = (payload*) buff;
      
      printf("Received contents: id=%d, counter=%d, temp=%f\n",
             p->id, p->counter, p->temp);
      printf("Sending it back.. ");
      sendMsg(csock, p, sizeof(payload));
    }
    if (nread < 0) {
      perror("Error: read failed");
    }
    printf("Closing connection to client\n");
    closeSocket(csock);
  }
  closeSocket(ssock);
  return 0;
}
