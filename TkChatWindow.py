import tkinter as tk
from tkinter import scrolledtext
import Chat as ch
import asyncio
import random


def essai(chatWindow, arguments):
    chatWindow.send_data(chatWindow, event='#disconnected ' + arguments[2])


def majUsers(chatWindow):
    chatWindow.utilisateurs['state'] = 'normal'
    chatWindow.utilisateurs.delete('1.0', 'end')
    print(chatWindow.users)
    for elt in chatWindow.users:
        chatWindow.utilisateurs.insert("end", elt + "\n")
    chatWindow.utilisateurs['state'] = 'disabled'


def connected(chatWindow, arguments):
    Adj = ["soudainement", "brusquement", "discrètement", "lentement", "finalement", "", "enfin", "encore"]
    chatWindow.messages['state'] = 'normal'
    chatWindow.messages.insert('end', f"{arguments[2]} apparait {random.choices(Adj)[0]} sur le serveur !\n\n")
    chatWindow.messages['state'] = 'disabled'
    chatWindow.users.append(arguments[2])
    majUsers(chatWindow)


def listing(chatWindow, arguments):
    chatWindow.messages['state'] = 'normal'
    chatWindow.users = []
    if len(arguments) > 2:
        for elt in arguments:
            if elt != "#list" and elt != ' ':
                chatWindow.messages.insert('end', elt + ' ')
                chatWindow.users.append(elt)
        chatWindow.messages.insert('end', "sont connectés sur le serveur actuellement !\n\n")
        majUsers(chatWindow)
    else:
        chatWindow.messages.insert('end', "Personne n'est connecté sur le serveur actuellement.\n\n")
    chatWindow.messages['state'] = 'disabled'


def alias(chatWindow, arguments):
    chatWindow.messages['state'] = 'normal'
    chatWindow.messages.insert('end', f"Bienvenue {arguments[2]} ! Vous êtes bien connecté(e) sur le serveur "
                                      f"ChatText.\n\n")
    chatWindow.messages['state'] = 'disabled'
    chatWindow.users.append(arguments[2])
    majUsers(chatWindow)


class privateWindow:
    def __init__(self, chatWindow, arguments):
        self.root = chatWindow.root
        self.user = arguments[2]
        self.window = tk.Toplevel(self.root)
        self.window.grab_set()
        pro = Processor(self.window)
        self.window.title('Chat with ' + self.user)
        self.window.protocol("WM_DELETE_WINDOW", lambda: self.window.destroy())
        self.window.geometry("200x400")
        self.messages = scrolledtext.ScrolledText(self.window)
        self.messages.tag_configure('bold', font='TkDefaultFont 9 bold')
        self.messages['state'] = 'disabled'
        self.inputing = tk.Entry(self.window)
        self.inputing.bind('<Return>', lambda e: send_private_data(chatWindow, self.inputing.get(), self.user))
        self.send = tk.Button(self.window, text='Send', command=send_private_data)
        self.messages.grid(row=0, column=0, sticky="nsew")
        self.inputing.grid(row=1, column=0, sticky="we")
        self.window.columnconfigure(0, weight=0)
        self.root.columnconfigure(0, weight=0)
        self.window.rowconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.messages['state'] = 'normal'
        self.messages.insert('end', f"{arguments[2]} : {arguments[4]}\n")
        self.messages['state'] = 'disabled'

    def insert(self, arguments):
        self.messages['state'] = 'normal'
        self.messages.insert('end', f"{arguments[2]} : {arguments[4]}\n")
        self.messages['state'] = 'disabled'


def private(chatWindow, arguments):
    res = False
    for elt in chatWindow.privates:
        if elt.user == arguments[2]:
            elt.insert(arguments)
            res = True
    if not res:
        chatWindow.privates.append(privateWindow(chatWindow, arguments))


def send_private_data(chatWindow, inputing, user):
    #print(f"/private {user} {inputing}\n")
    chatWindow.chat.transport.write(f"/private {user} {inputing}\n".encode())


def renamed(chatWindow, arguments):
    chatWindow.messages['state'] = 'normal'
    chatWindow.messages.insert('end', f"{arguments[2]} vient de se renommer en {arguments[4]}.\n\n")
    chatWindow.messages['state'] = 'disabled'
    chatWindow.users.pop(chatWindow.users.index(arguments[2]))
    chatWindow.users.append(arguments[3])
    majUsers(chatWindow)


def disconnected(chatWindow, arguments):
    chatWindow.messages['state'] = 'normal'
    chatWindow.messages.insert('end', arguments[2] + " est parti ! (Enfin...)\n\n")
    chatWindow.messages['state'] = 'disabled'
    if arguments[2] in chatWindow.users:
        chatWindow.users.pop(chatWindow.users.index(arguments[2]))
    majUsers(chatWindow)


def command_decode(message: str):
    message_decode = [elt for elt in message.partition(' ')]
    if ' ' in message_decode[2]:
        message_decode = [message_decode[0], message_decode[1]] + command_decode(message_decode[2])
    if '\n' in message_decode[len(message_decode) - 1]:
        message_decode[len(message_decode) - 1] = message_decode[len(message_decode) - 1].partition('\n')[0]
    return message_decode


class Processor:
    """
  Classe utilisée par une connexion pour traiter les messages reçus du serveur
  """

    def error(self, chatWindow, arguments):
        arg = str(arguments[1])
        chatWindow.messages['state'] = 'normal'
        chatWindow.messages.insert('end', f"ERROR : {arg}")
        chatWindow.messages['state'] = 'disabled'

    def __init__(self, chatWindow):
        self.chatWindow = chatWindow
        self.server_commands = {'#error': self.error, '#alias': alias, '#list': listing,
                                '#connected': connected, '#private': private, '#renamed': renamed,
                                '#disconnected': disconnected, '#test': essai}

    def process_message(self, message: str):
        if message.startswith("#"):
            message_decode = command_decode(message)
            if message_decode[0] in self.server_commands.keys():
                self.server_commands[message_decode[0]](self.chatWindow, message_decode)
        else:
            message = message.partition(' ')
            message = message[0] + "# " + message[2]
            self.chatWindow.messages['state'] = 'normal'
            self.chatWindow.messages.insert('end', message + '\n')
            self.chatWindow.messages['state'] = 'disabled'
            #print(message)


class TkChatWindow(tk.Frame, Processor):
    def __init__(self, root):
        self.privates = []
        tk.Frame.__init__(self, root)
        Processor.__init__(self, self)
        root.title('Chat')
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.geometry("800x600")
        self.CLOSE = False
        self.users = []
        self.root = root

        self.utilisateurs = scrolledtext.ScrolledText(self)
        self.utilisateurs.tag_configure('bold', font='TkDefaultFont 9 bold')
        self.utilisateurs['state'] = 'disabled'
        self.messages = scrolledtext.ScrolledText(self)
        self.messages.tag_configure('bold', font='TkDefaultFont 9 bold')
        self.messages.insert('end', 'connecting...\n')
        self.messages['state'] = 'disabled'
        self.input = tk.Entry(self)
        self.input.bind('<Return>', self.send_data)
        self.send = tk.Button(self, text='Send', command=self.send_data)
        self.utilisateurs.bind('<Double-Button-1>', self.private)

        self.grid(column=0, row=0, sticky="nsew")
        self.messages.grid(row=0, column=0, sticky="nsew")
        self.utilisateurs.grid(row=0, column=1, sticky="nsew")
        self.input.grid(row=1, column=0, sticky="we")
        self.send.grid(row=1, column=1, sticky="we")

        self.columnconfigure(0, weight=0)
        root.columnconfigure(0, weight=0)
        self.rowconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.chat = ch.Chat('127.0.0.1', 8888, self)  # self.chat = ch.Chat('linux', 3101, self)  #

    def private(self, arg):
        private(self, ['', '', 'hello', arg])

    def close(self):
        self.CLOSE = True

    def message_received(self, msg):
        self.messages['state'] = 'normal'
        self.messages.insert('end', msg)
        self.messages['state'] = 'disabled'

    def connection_made(self):
        self.messages['state'] = 'normal'
        self.messages.insert('end', 'Vous êtes connecté.e ! \nChoisissez votre login :\n')
        self.messages['state'] = 'disabled'

    def error(self, chatWindow, err):
        chatWindow.messages['state'] = 'normal'
        chatWindow.messages.insert('end', err)
        chatWindow.messages['state'] = 'disabled'

    def send_data(self, event=None):
        event = self.input.get()
        self.chat.transport.write(f"{event}\n".encode())

    def connection_lost(self):
        self.close()


async def main():
    root = tk.Tk()
    cw = TkChatWindow(root)
    on_con_lost = asyncio.get_running_loop().create_future()
    await cw.chat.create_connection(on_con_lost)
    while not cw.CLOSE:
        root.update()
        await asyncio.sleep(0.01)

if __name__ == '__main__':
    asyncio.run(main())
