import asyncio
import zmq.asyncio
import cv2
import aioconsole
import json
from gpiozero.pins.mock import MockFactory
from gpiozero import OutputDevice, Servo, Device
import platform

if platform.system() == "Windows":
    Device.pin_factory = MockFactory()
    class MockServo:
        def __init__(self, *a, **k): pass
        def mid(self): pass
        def max(self): pass
        def min(self): pass
    ServoClass = MockServo
else:
    ServoClass = Servo
class GPIOServer:
    def __init__(self):
        self.motor_pin_a = OutputDevice(19)   # DIR (fiz. pin 35)
        self.motor_pin_b = OutputDevice(13)   # STEP (fiz. pin 33)
        self.servo = ServoClass(12)           # Servo (fiz. pin 32)
        self._motor_task = None               # referencja do async taska
        self._running = False

    async def motor_task(self, x_val):
        delay = max(0.0005, 0.005 * (1 - abs(x_val)))
        self.motor_pin_a.value = 1 if x_val > 0 else 0
        while self._running and abs(x_val) > 0:
            self.motor_pin_b.on()
            await asyncio.sleep(delay)
            self.motor_pin_b.off()
            await asyncio.sleep(delay)

    def handle_axis(self, x_val, y_val):
        self.servo.value = max(-1.0, min(1.0, y_val))
        self._running = False

        if x_val != 0:
            self._running = True
            if self._motor_task is None or self._motor_task.done():
                self._motor_task = asyncio.create_task(self.motor_task(x_val))

        # print(f"DIR={self.motor_pin_a.value}, STEP freq≈{1/(max(0.0005, 0.005*(1-abs(x_val)))*2):.1f}Hz")
        # print(Device.pin_factory.pins)


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

    def __init__(self, gpio_server: GPIOServer):
        self.footage_socket.connect('tcp://localhost:5555')
        self.registration_msg()
        self.gpio_server = gpio_server

    async def readMsg(self):
        while True:
            message = await self.footage_socket.recv()
            if isinstance(message, bytes):
                text = message.decode('utf-8')
                print("text:", text)
                try:
                    data = json.loads(text)
                    if data.get("type") == "AXIS":
                        self.gpio_server.handle_axis(
                            data.get("motor", 0.0),
                            data.get("dir", 0.0)
                        )
                except json.JSONDecodeError:
                    pass

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
    gpio_server = GPIOServer()
    client = ChatClient(gpio_server)
    streamer = Streamer()
    try:
        await asyncio.gather(client.run(), streamer.run())
    except asyncio.CancelledError:
        print("main task cancelled")

if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted by user")