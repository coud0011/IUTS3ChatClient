import tkinter as tk
from tkinter import scrolledtext
import Chat as ch
import asyncio
from ChatText import Processor, connected, listing, alias, private, renamed, disconnected, command_decode


class TkChatWindow(tk.Frame, Processor):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        Processor.__init__(self)
        root.title('Chat')
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.geometry("800x600")
        self.CLOSE = False

        self.messages = scrolledtext.ScrolledText(self)
        self.messages.tag_configure('bold', font='TkDefaultFont 9 bold')
        self.messages.insert('end', 'connecting...\n')
        self.messages['state'] = 'disabled'
        self.input = tk.Entry(self)
        self.input.bind('<Return>', self.send_data)
        self.send = tk.Button(self, text='send', command=self.send_data)

        self.grid(column=0, row=0, sticky="nsew")
        self.messages.grid(row=0, column=0, sticky="nsew")
        self.input.grid(row=1, column=0, sticky="we")
        self.send.grid(row=1, column=1, sticky="ew")

        self.columnconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        self.chat = ch.Chat('linux', 3101, self)

    def close(self):
        self.CLOSE = True

    def message_received(self, msg):
        # Ajoutez le code ici
        pass

    def connection_made(self):
        self.messages['state'] = 'normal'
        self.messages.insert('end', 'Vous êtes connecté.e ! \nChoisissez votre login :\n')
        self.messages['state'] = 'disabled'

    def error(self, err):
        # Ajoutez le code ici
        pass

    def send_data(self, event):
        # Ajoutez le code ici
        pass

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
