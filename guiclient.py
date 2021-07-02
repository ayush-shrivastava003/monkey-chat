import socket
import select
import errno
import sys
import threading
import tkinter as tk
import tkinter.font as tkFont
import datetime

HEADERSIZE = 10
IP = "127.0.0.1"
PORT = 1234

myUsername = input("username ->")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((IP, PORT))
client.setblocking(0)

username = myUsername.encode("utf-8")
usernameHeader = f"{len(username):<{HEADERSIZE}}".encode("utf-8")
client.send(usernameHeader + username)

class gui():
    def __init__(self, root):
        bgcol = '#333333'
        lightcol = '#EEEEEE'

        root.configure(bg = bgcol)
        root.geometry('500x500')
        root.title('monkeychat')

        title = tk.Label(root, text = 'monkeychat', font = tkFont.Font(family="Roboto Light", size=40), fg = "#e2b714", bg = bgcol)
        title.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

        historyText = tk.Label(root, font=tkFont.Font(family="Roboto Light"), bg=bgcol, fg="#FFF")
        historyText.configure(text="Message History")
        historyText.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

        self.messageHistory = tk.Label(root, font=tkFont.Font(family="Roboto Light", size=11), fg="#FFF", bg=bgcol, width=500)
        self.messageHistory.configure(text=datetime.date.today())
        self.messageHistory.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.entry = tk.Entry(root, font=tkFont.Font(family="Roboto Light"))
        self.entry.bind("<Return>", self.sendMSG)
        # self.button = tk.Button(root, text="SEND", command=self.sendMSG)
        # self.button.grid(row=5, column=3)
        self.entry.place(relx=0.5, rely=0.65, anchor=tk.CENTER)

    def sendMSG(self, event):
        try:
            msg = self.entry.get()
            if msg == "":
                return

            self.messageHistory.configure(text=f"{self.messageHistory['text']}\n{myUsername} -> {msg}")
            print("msg:", msg)
            msg = msg.encode("utf-8")
            msgHeader = f"{len(msg):<{HEADERSIZE}}".encode("utf-8")
            client.send(msgHeader + msg)
            self.entry.delete(0, "end")

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print("reading error", str(e))
                sys.exit()

        except Exception as e:
            print("Other error:", e)
            sys.exit()

    def receiveMessage(self):
        try:
            usernameHeader = client.recv(HEADERSIZE)

            if not len(usernameHeader):
                print("connection closed by server.")
                sys.exit()

            usernameLength = int(usernameHeader.decode("utf-8").strip())
            username = client.recv(usernameLength).decode("utf-8")

            msgHeader = client.recv(HEADERSIZE)
            msgLength = int(msgHeader.decode("utf-8").strip())
            msg = client.recv(msgLength).decode("utf-8")

            print("recvd msg:", msg)

            self.messageHistory.configure(text=f"{self.messageHistory['text']}\n{username} -> {msg}")

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print("reading error", str(e))
                sys.exit()

        except Exception as e:
            print("Other error:", e)
            sys.exit()

root = tk.Tk()
g = gui(root)
while True:
    g.receiveMessage()
    root.update()