import asyncio
import zmq.asyncio
import zmq
from aiohttp import web

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

    async def html_content(self):
        async def handle(request):
            html = open('vrVideo.html', 'r', encoding='utf-8').read()
            return web.Response(text=html, content_type='text/html')
        async def video_feed(request):
            response = web.StreamResponse(
                status=200,
                reason='OK',
                headers={
                    'Content-Type': 'multipart/x-mixed-replace; boundary=frame'
                }
            )
            await response.prepare(request)

            while True:
                try:
                    frame = await self.dealer_video_socket.recv()
                    await response.write(
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n" +
                        frame +
                        b"\r\n"
                    )
                except Exception as e:
                    print("Stream error:", e)
                    break
            return

        app = web.Application()
        app.router.add_get('/', handle)
        app.router.add_get('/video', video_feed)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 80)
        await site.start()

async def main():
    chat_server = CHATSERVER()
    video_server = VIDEOSERVER()
    await asyncio.gather(
        chat_server.run_chat(),
        video_server.run_video(),
        video_server.html_content()
    )

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted by user")

