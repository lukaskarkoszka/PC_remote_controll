import threading
import zmq
import base64
import numpy as np
import cv2
import aioconsole
import asyncio
import zmq.asyncio
import matplotlib.pyplot as plt

class Viewer:
    context = zmq.asyncio.Context()
    footage_socket = context.socket(zmq.DEALER)

    def __init__(self):
        self.footage_socket.connect('tcp://localhost:5556')
        self.registration_msg()

    async def video(self):
        while True:
            try:
                frame = await asyncio.wait_for(self.footage_socket.recv(), timeout=5.0)
                if frame != b'':
                    np_frame = np.frombuffer(frame, dtype=np.uint8)
                    source = cv2.imdecode(np_frame, 1)
                    if source is not None:
                        cv2.imshow("Stream", source)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
            except asyncio.TimeoutError:
                print("Timeout while waiting for frame")
        cv2.destroyAllWindows()

    def registration_msg(self):
        print("registration")
        self.footage_socket.send_string("")

    async def run(self):
        await asyncio.gather(self.video())

class ChatClient:
    context = zmq.asyncio.Context()
    footage_socket = context.socket(zmq.DEALER)

    def __init__(self):
        self.footage_socket.connect('tcp://localhost:5555')
        self.registrationMsg()

    async def readMsg(self):
        while True:
            message = await self.footage_socket.recv()
            if isinstance(message, bytes):
                print(" text:", message.decode('utf-8'))

    def registrationMsg(self):
        print("registration")
        self.footage_socket.send_string("Connected")

    async def sendMsg(self):
        while True:
            msg = await aioconsole.ainput("write msg: ")
            self.footage_socket.send_string(msg)

    async def run(self):
        await asyncio.gather(self.readMsg(), self.sendMsg())

async def main():
    client = ChatClient()
    viewer = Viewer()
    try:
        await asyncio.gather(client.run(), viewer.run())

    except asyncio.CancelledError:
        print("main task cancelled")

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted by user")






