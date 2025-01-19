import asyncio
import zmq.asyncio
import zmq

class CHATSERVER:
    context = zmq.asyncio.Context()
    router_chat_socket = context.socket(zmq.ROUTER)

    def __init__(self):
        self.router_chat_socket.bind("tcp://*:5555")
        print("runChat")

    async def run_chat(self):
        clients = set()
        while True:
            print("message send?")
            client_id, message = await self.router_chat_socket.recv_multipart()
            clients.add(client_id)
            if isinstance(message, bytes):
                text = message.decode('utf-8')
                print("Received text:", text)
                for client in clients:
                    await self.router_chat_socket.send_multipart([client, text.encode('utf-8')])


class VIDEOSERVER:
    context = zmq.asyncio.Context()
    dealer_video_socket = context.socket(zmq.DEALER)

    def __init__(self):
        self.dealer_video_socket.bind("tcp://*:5556")
        print("runVideo")

    async def run_video(self):
        while True:
            message = await self.dealer_video_socket.recv()
            await self.dealer_video_socket.send(message)

async def main():
    chat_server = CHATSERVER()
    video_server = VIDEOSERVER()
    await asyncio.gather(
        chat_server.run_chat(),
        video_server.run_video()
    )

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted by user")

