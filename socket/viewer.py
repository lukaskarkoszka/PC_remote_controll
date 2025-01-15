import threading
import zmq
import base64
import numpy as np
import cv2
import asyncio
import zmq.asyncio
import aioconsole
# class Viewer:
#     context = zmq.Context()
#     footage_socket = context.socket(zmq.DEALER)
#
#     def __init__(self, address):
#         self.footage_socket.connect('tcp://' + address + ':5555')
#
#     def video(self):
#         while True:
#             try:
#                 frame = self.footage_socket.recv_string()
#                 img = base64.b64decode(frame)
#                 npimg = np.fromstring(img, dtype=np.uint8)
#                 source = cv2.imdecode(npimg, 1)
#                 cv2.imshow("Stream", source)
#                 cv2.waitKey(1)
#
#             except KeyboardInterrupt:
#                 cv2.destroyAllWindows()
#                 break
#
#     def run(self):
#         videoThread = threading.Thread(target=self.video)
#         videoThread.daemon = True
#         videoThread.start()

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
    await asyncio.gather(client.run())

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())





