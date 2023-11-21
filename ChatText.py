import socket
import asyncio
from concurrent.futures import ThreadPoolExecutor
import random


async def ainput(prompt: str = "") -> str:
    """
  Méthode asynchrone attendant une saisie clavier
  """
    with ThreadPoolExecutor(1, "AsyncInput") as executor:
        try:
            return await asyncio.get_event_loop().run_in_executor(executor, input, prompt)
        except asyncio.CancelledError:
            print('Bye bye ainput')


def connected(arguments):
    Adj = ["soudainement", "brusquement", "discrètement", "lentement", "finalement", "", "enfin", "encore"]
    print(f"{arguments[2]} apparait {random.choices(Adj)[0]} sur le serveur !")


def listing(arguments):
    if len(arguments) > 1:
        for elt in arguments:
            if elt != "#list" and elt != ' ':
                print(elt, end=' ')
        print("sont connectés sur le serveur actuellement !")
    else:
        print("Personne n'est connecté sur le serveur actuellement.")


def alias(arguments):
    print(f"Bienvenue {arguments[2]} ! Vous êtes bien connecté(e) sur le serveur ChatText.")


def private(arguments):
    print(
        f"{arguments[2]} viens de vous envoyer le message privé :\n{arguments[4]}\nPour lui répondre tapez : /private "
        f"{arguments[2]} message.")


def renamed(arguments):
    print(f"{arguments[2]} vient de se renommer en {arguments[4]}.")


def disconnected(arguments):
    print(arguments[2] + " est parti ! (Enfin...)")


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

    def error(self, arguments):
        arg = str(arguments[1])
        print(f"ERROR : {arg}")

    def __init__(self):
        self.server_commands = {'#error': self.error, '#alias': alias, '#list': listing,
                                '#connected': connected, '#private': private, '#renamed': renamed,
                                '#disconnected': disconnected}

    def process_message(self, message: str):
        if message.startswith("#"):
            message_decode = command_decode(message)
            if message_decode[0] in self.server_commands.keys():
                self.server_commands[message_decode[0]](message_decode)
        else:
            message = message.partition(' ')
            message = message[0]+"# "+message[2]
            print(message)


class ClientProtocol(asyncio.Protocol):
    def __init__(self, on_con_lost, processor):
        print('ClientProtocol')
        self.transport = None
        self.on_con_lost = on_con_lost
        self.processor = processor

    def connection_made(self, transport):
        print('Connecté - Entrez votre login :')
        self.transport = transport

    def data_received(self, data):
        self.processor.process_message(data.decode())

    def connection_lost(self, exc):
        print('The server closed the connection')
        self.on_con_lost.set_result(True)


class ChatText(Processor):
    """
  Interface utilisateur d'un client en mode texte
  """

    def __init__(self, host, port):
        Processor.__init__(self)
        self.host = host
        self.port = port
        self.transport = None
        self.on_con_lost = None

    def error(self, err):
        arg = str(err[2])
        print(f"ERROR : {arg}")

    def message_received(self, msg):
        print(msg)

    async def create_connection(self):
        print('connecting')
        self.on_con_lost = asyncio.get_running_loop().create_future()
        print('avant create_connection', self.host, self.port)
        try:
            self.transport, self.protocol = await asyncio.get_running_loop().create_connection(
                lambda: ClientProtocol(self.on_con_lost, self), self.host, self.port)
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
        login = await ainput()
        self.transport.write((login + '\n').encode())
        await asyncio.sleep(1)

    async def listen(self):
        while not self.on_con_lost.done():
            command = await ainput()
            self.transport.write((command + '\n').encode())
            await asyncio.sleep(1)


async def main():
    chat = ChatText('linux', 8888)
    await chat.create_connection()
    await chat.listen()


if __name__ == '__main__':
    print('Client chat')
    asyncio.run(main())
