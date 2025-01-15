import asyncio
import zmq
import zmq.asyncio
import base64
import cv2
import socket

class Streamer:
    context = zmq.asyncio.Context()
    footage_socket = context.socket(zmq.PUB)
    camera = cv2.VideoCapture(0)

    def __init__(self, address):
        self.footage_socket.bind('tcp://' + address + ':5555')

    async def video(self):
        while True:
            try:
                grabbed, frame = self.camera.read()  # grab the current frame
                frame = cv2.resize(frame, (640, 480))  # resize the frame
                encoded, buffer = cv2.imencode('.jpg', frame)
                jpg_as_text = base64.b64encode(buffer)
                await self.footage_socket.send(jpg_as_text)

            except KeyboardInterrupt:
                self.camera.release()
                cv2.destroyAllWindows()
                break

    async def run(self):
        await asyncio.gather(self.video())

class ChatClient:
    context = zmq.Context()
    socket = context.socket(zmq.SUB)

    def __init__(self, address, user_name):
        self.socket.connect("tcp://localhost:5555")
        self.socket.setsockopt(zmq.SUBSCRIBE, b"A")
        self.user_name = user_name
        self.address = address

    async def sendMsg(self):
        loop = asyncio.get_event_loop()
        while True:
            msg = await loop.run_in_executor(None, input, "")
            self.socket.send(bytes(self.user_name + "\t: " + msg, 'utf-8'))

    async def run(self):
        await asyncio.gather(self.sendMsg())

async def main(address, user_name):
    # streamer = Streamer(address)
    # await asyncio.gather(streamer.run())
    client = ChatClient(address, user_name)
    await asyncio.gather(client.run())

if __name__ == "__main__":
    import sys
    address = sys.argv[1]
    user_name = sys.argv[2]
    asyncio.run(main(address, user_name))
