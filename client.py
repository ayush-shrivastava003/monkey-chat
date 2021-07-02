import socket
import select
import errno
import sys
import threading

HEADERSIZE = 10
IP = "127.0.0.1"
PORT = 1234

myUsername = input("username ->")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((IP, PORT))
client.setblocking(False)

username = myUsername.encode("utf-8")
usernameHeader = f"{len(username):<{HEADERSIZE}}".encode("utf-8")
client.send(usernameHeader + username)

def receiveMessage():
    while True:
        usernameHeader = client.recv(HEADERSIZE)

        if not len(usernameHeader):
            print("connection closed by server.")
            sys.exit()

        usernameLength = int(usernameHeader.decode("utf-8").strip())
        username = client.recv(usernameLength).decode("utf-8")

        msgHeader = client.recv(HEADERSIZE)
        msgLength = int(msgHeader.decode("utf-8").strip())
        msg = client.recv(msgLength).decode("utf-8")

        print(f"{username} -> {msg}")

while True:
    msg = input(f"{myUsername} -> ")

    if msg:
        msg = msg.encode("utf-8")
        msgHeader = f"{len(msg):<{HEADERSIZE}}".encode("utf-8")
        client.send(msgHeader + msg)

    try:
        t = threading.Thread(receiveMessage())
        t.start()
    
    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print("reading error", str(e))
            sys.exit()
        continue

    except Exception as e:
        print("Other error:", e)
        sys.exit()