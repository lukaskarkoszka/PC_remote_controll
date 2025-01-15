import asyncio
import zmq

class SERVER:
    context = zmq.Context()
    routerSocket = context.socket(zmq.ROUTER)

    def __init__(self):
        self.routerSocket.bind("tcp://*:5555")

    def runChat(self):
        clients = set()
        while True:
            client_id, message = self.routerSocket.recv_multipart()
            clients.add(client_id)
            if isinstance(message, bytes):
                text = message.decode('utf-8')
                print("Received text:", text)
                for client in clients:
                    self.routerSocket.send_multipart([client, text.encode('utf-8')])

async def main():
    server = SERVER()
    await asyncio.gather(server.runChat())

if __name__ == "__main__":
    asyncio.run(main())