import asyncio
import zmq.asyncio
import cv2
import aioconsole

class Streamer:
    context = zmq.asyncio.Context()
    footage_socket = context.socket(zmq.DEALER)

    def __init__(self):
        self.footage_socket.connect('tcp://localhost:5556')

    async def video(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            _, buffer = cv2.imencode('.jpg', frame)
            buffer_byte = buffer.tobytes()
            await self.footage_socket.send(buffer_byte)
            await asyncio.sleep(1/30)  # 30fps

    async def run(self):
        await asyncio.gather(self.video())

class ChatClient:
    context = zmq.asyncio.Context()
    footage_socket = context.socket(zmq.DEALER)

    def __init__(self):
        self.footage_socket.connect('tcp://localhost:5555')
        self.registration_msg()

    async def readMsg(self):
        while True:
            message = await self.footage_socket.recv()
            if isinstance(message, bytes):
                print(" text:", message.decode('utf-8'))

    def registration_msg(self):
        print("registration")
        self.footage_socket.send_string("")

    async def sendMsg(self):
        while True:
            msg = await aioconsole.ainput("write msg: ")
            self.footage_socket.send_string(msg)

    async def run(self):
        await asyncio.gather(self.readMsg(), self.sendMsg())

async def main():
    client = ChatClient()
    streamer = Streamer()
    try:
        await asyncio.gather(client.run(), streamer.run())
    except asyncio.CancelledError:
        print("main task cancelled")

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted by user")