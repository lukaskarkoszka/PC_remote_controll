import numpy as np
import cv2
import aioconsole
import asyncio
import zmq.asyncio
import pygame
import json
import platform
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


    async def sendMsg(self, msg=None):
        self.footage_socket.send_string(str(msg))

    async def console_sender(self):
        while True:
            msg = await aioconsole.ainput("write msg: ")
            self.footage_socket.send_string(msg)

    async def run(self):
        await asyncio.gather(self.readMsg(), self.sendMsg())

class XboxController:
    def __init__(self, chat_client: ChatClient, deadzone=1/30):
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            raise RuntimeError("Brak podłączonego kontrolera Xbox")
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        self.chat_client = chat_client
        self.deadzone = deadzone
        self.last_x = None
        self.last_y = None

    async def poll(self):
        while True:
            pygame.event.pump()
            axis_x = self.joystick.get_axis(1)
            axis_y = self.joystick.get_axis(2)

            axis_x = 0.0 if abs(axis_x) < self.deadzone else round(axis_x, 3)
            axis_y = 0.0 if abs(axis_y) < self.deadzone else round(axis_y, 3)

            if axis_x != self.last_x or axis_y != self.last_y:
                payload = {
                    "type": "AXIS",
                    "motor": axis_x,
                    "dir": axis_y
                }
                data = json.dumps(payload)
                await self.chat_client.sendMsg(data)

                self.last_x, self.last_y = axis_x, axis_y

            await asyncio.sleep(1/30)

async def main():
    client = ChatClient()
    viewer = Viewer()
    xbox = XboxController(client)
    try:
        await asyncio.gather(client.run(), viewer.run(), xbox.poll())

    except asyncio.CancelledError:
        print("main task cancelled")

if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted by user")






