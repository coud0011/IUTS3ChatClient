import socket
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def ainput(prompt: str = "") -> str:
  """
  Méthode asynchrone attendant une saisie clavier
  """
  with ThreadPoolExecutor(1, "AsyncInput") as executor:
    try:
      return await asyncio.get_event_loop().run_in_executor(executor, input, prompt)
    except asyncio.CancelledError:
      print('Bye bye ainput')
        
class Processor:
  """
  Classe utilisée par une connexion pour traiter les messages reçus du serveur
  """
  def __init__(self) : 
    self.server_commands={'#error':self.error}

  def process_message(self, message):
    print(message)

class ClientProtocol (asyncio.Protocol):
  def __init__ (self, on_con_lost, processor):
    print('ClientProtocol')
    self.transport = None
    self.on_con_lost = on_con_lost
    self.processor=processor
    
  def connection_made(self, transport):
    print('Connecté - Entrez votre login :')
    self.transport=transport

  def data_received(self, data):
    print("Received:", data.decode())
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
    self.host=host
    self.port=port
    self.transport=None
    self.on_con_lost=None

  def error (self, err):
    print('ERREUR : '+err)
  
  def message_received (self, msg):
    print(msg)

  async def create_connection(self):
    print('connecting')
    self.on_con_lost = asyncio.get_running_loop().create_future()
    print('avant create_connection', self.host, self.port)
    try:
      self.transport, self.protocol = await asyncio.get_running_loop().create_connection(lambda: ClientProtocol(self.on_con_lost, self), self.host, self.port)
    except Exception as err:
      print(f"Unexpected {err=}, {type(err)=}")
    login=await ainput()
    self.transport.write((login+'\n').encode())
    await asyncio.sleep(1)


async def main():
    chat = ChatText('linux', 3101)
    await chat.create_connection()
    #await chat.listen()

if __name__ == '__main__':
  print('Client chat')
  asyncio.run(main())

