import asyncio
import zmq
import zmq.asyncio
import base64
import cv2
import socket

class ChatClient:
    context = zmq.Context()
    footage_socket = context.socket(zmq.DEALER)

    def __init__(self):
        self.footage_socket.connect('tcp://localhost:5555')
        self.sendMsg()

    async def readMsg(self):
        while True:
            message = self.footage_socket.recv()
            if isinstance(message, bytes):
                print(" text:", message.decode('utf-8'))

    def sendMsg(self):
        print("registration")
        self.footage_socket.send_string("Connected")

    async def run(self):
        await asyncio.gather(self.readMsg())

async def main():
    client = ChatClient()
    await asyncio.gather(client.run())

if __name__ == "__main__":
    asyncio.run(main())