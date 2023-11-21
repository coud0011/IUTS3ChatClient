import tkinter as tk
from tkinter import scrolledtext
import Chat as ch
import asyncio
import random


def connected(chatWindow, arguments):
    Adj = ["soudainement", "brusquement", "discrètement", "lentement", "finalement", "", "enfin", "encore"]
    chatWindow.messages['state'] = 'normal'
    chatWindow.messages.insert('end', f"{arguments[2]} apparait {random.choices(Adj)[0]} sur le serveur !\n")
    chatWindow.messages['state'] = 'disabled'


def listing(chatWindow, arguments):
    chatWindow.messages['state'] = 'normal'
    if len(arguments) > 2:
        for elt in arguments:
            if elt != "#list" and elt != ' ':
                chatWindow.messages.insert('end', elt + ' ')
        chatWindow.messages.insert('end', "sont connectés sur le serveur actuellement !\n")
    else:
        chatWindow.messages.insert('end', "Personne n'est connecté sur le serveur actuellement.\n")
    chatWindow.messages['state'] = 'disabled'


def alias(chatWindow, arguments):
    chatWindow.messages['state'] = 'normal'
    chatWindow.messages.insert('end',
                               f"Bienvenue {arguments[2]} ! Vous êtes bien connecté(e) sur le serveur ChatText.\n")
    chatWindow.messages['state'] = 'disabled'


def private(chatWindow, arguments):
    chatWindow.messages['state'] = 'normal'
    chatWindow.messages.insert('end', f"{arguments[2]} viens de vous envoyer le message privé :\n{arguments[4]}\n"
                                      f"Pour lui répondre tapez : /private {arguments[2]} message.\n")
    chatWindow.messages['state'] = 'disabled'


def renamed(chatWindow, arguments):
    chatWindow.messages['state'] = 'normal'
    chatWindow.messages.insert('end', f"{arguments[2]} vient de se renommer en {arguments[4]}.\n")
    chatWindow.messages['state'] = 'disabled'


def disconnected(chatWindow, arguments):
    chatWindow.messages['state'] = 'normal'
    chatWindow.messages.insert('end', arguments[2] + " est parti ! (Enfin...)\n")
    chatWindow.messages['state'] = 'disabled'


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
                                '#disconnected': disconnected}

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
            print(message)


class TkChatWindow(tk.Frame, Processor):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        Processor.__init__(self, self)
        root.title('Chat')
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.geometry("800x600")
        self.CLOSE = False

        self.utilisateurs = scrolledtext.ScrolledText(self)
        self.utilisateurs.tag_configure('bold', font='TkDefaultFont 9 bold')
        self.utilisateurs['state'] = 'disabled'
        self.messages = scrolledtext.ScrolledText(self)
        self.messages.tag_configure('bold', font='TkDefaultFont 9 bold')
        self.messages.insert('end', 'connecting...\n')
        self.messages['state'] = 'disabled'
        self.input = tk.Entry(self)
        self.input.bind('<Return>', self.send_data)
        self.send = tk.Button(self, text='send', command=self.send_data)

        self.grid(column=0, row=0, sticky="nsew")
        self.messages.grid(row=0, column=0, sticky="nsew")
        self.utilisateurs.grid(row=0, column=1, sticky="nsew")
        self.input.grid(row=1, column=0, sticky="we")
        self.send.grid(row=1, column=1, sticky="ew")

        self.columnconfigure(0, weight=0)
        root.columnconfigure(0, weight=0)
        self.rowconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        self.chat = ch.Chat('linux', 8888, self)

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
        if event is None:
            event = self.input.get()
        self.chat.transport.write((f"{event}" + '\n').encode())

    def connection_lost(self):
        self.close()


async def main():
    root = tk.Tk()
    cw = TkChatWindow(root)
    on_con_lost = asyncio.get_running_loop().create_future()
    await cw.chat.create_connection(on_con_lost)
    while not cw.CLOSE:
        root.update()
        await asyncio.sleep(0)


if __name__ == '__main__':
    asyncio.run(main())
