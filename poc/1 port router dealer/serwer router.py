import zmq
import cv2
import numpy as np

# Inicjalizacja kontekstu ZMQ
context = zmq.Context()

# Tworzenie socketu typu ROUTER do odbierania i wysyłania danych
router_socket = context.socket(zmq.ROUTER)
router_socket.bind("tcp://*:5555")

# Funkcja do przesyłania obrazu
def send_image(image):
    _, buffer = cv2.imencode('.jpg', image)
    router_socket.send_multipart([b"", buffer.tobytes()])

# Funkcja do przesyłania tekstu
def send_text(text):
    router_socket.send_multipart([b"", text.encode('utf-8')])

# Funkcja do odbierania danych
def receive_data():
    clients = set()
    while True:
        client_id, message = router_socket.recv_multipart()
        clients.add(client_id)
        if isinstance(message, bytes):
        #     # Odbieranie obrazu
        #     nparr = np.frombuffer(message, np.uint8)
        #     image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        #     cv2.imshow('Received Image', image)
        #     cv2.waitKey(1)
        #     # Wysyłanie obrazu do wszystkich klientów
        #     for client in clients:
        #         router_socket.send_multipart([client, buffer.tobytes()])
        # else:
            # Odbieranie tekstu
            text = message.decode('utf-8')
            print("Received text:", text)
            # Wysyłanie tekstu do wszystkich klientów
            for client in clients:
                router_socket.send_multipart([client, text.encode('utf-8')])

# Przykładowe użycie
if __name__ == "__main__":
    receive_data()
