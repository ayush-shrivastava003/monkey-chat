import socket
import select

HEADERSIZE = 10
IP = "0.0.0.0"
PORT = 1234

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.bind((IP, PORT))
s.listen()

socketsList = [s]

clients = {}


def receiveMessage(clientSocket):
    try:
        msgHeader = clientSocket.recv(HEADERSIZE)
        
        if not len(msgHeader):
            return False

        msgLength = int(msgHeader.decode("utf-8").strip())
        return {"header": msgHeader, "data": clientSocket.recv(msgLength)}

    except:
        return False


while True:
    try:
        readSockets, _, exceptionSockets = select.select(socketsList, [], socketsList)

        for notifiedSocket in readSockets:
            if notifiedSocket == s:
                clientSocket, clientAddr = s.accept()

                user = receiveMessage(clientSocket)
                if user is False:
                    continue

                socketsList.append(clientSocket)
                clients[clientSocket] = user

                print("Accepted new connection from {0}:{1}. username: {2}".format(clientAddr[0], clientAddr[1], user["data"].decode("utf-8")))

            else:
                msg = receiveMessage(notifiedSocket)

                if msg is False:
                    print("Closed connection from {}".format(clients[notifiedSocket]["data"].decode("utf-8")))
                    socketsList.remove(notifiedSocket)
                    del clients[notifiedSocket]
                    continue

                user = clients[notifiedSocket]
                print("Received message from {}:".format(user["data"].decode("utf-8")))
                print(msg["data"].decode("utf-8"))

                for clientSocket in clients:
                    if clientSocket != notifiedSocket:
                        clientSocket.send(user["header"] + user["data"] + msg["header"] + msg["data"])
                
        for notifiedSocket in exceptionSockets:
            socketsList.remove(notifiedSocket)
            del clients[notifiedSocket]

    except KeyboardInterrupt:
        print("keyboard interrupt")
        s.shutdown(s.SHUTDOWN_RWDR)
        s.close()