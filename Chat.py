import asyncio


class ClientProtocol(asyncio.Protocol):
    def __init__(self, on_con_lost, controller):
        #print('ClientProtocol')
        self.on_con_lost = on_con_lost
        self.controller = controller

    def connection_made(self, transport):
        #print('Connecté')
        self.controller.connection_made()

    def data_received(self, data):
        #print("Received:", data.decode())
        self.controller.process_message(data.decode())

    def connection_lost(self, exc):
        #print('The server closed the connection')
        self.controller.connection_lost()
        self.on_con_lost.set_result(True)


class Chat:
    def __init__(self, host, port, controller):
        self.host = host
        self.port = port
        self.controller = controller
        self.transport = None

    async def create_connection(self, on_con_lost):
        #print('connecting')
        #print('avant create_connection', self.host, self.port)
        try:
            self.transport, protocol = await asyncio.get_running_loop().create_connection(
                lambda: ClientProtocol(on_con_lost, self.controller), self.host, self.port)
        except Exception as err:
            print()
            #print(f"Unexpected {err=}, {type(err)=}")
