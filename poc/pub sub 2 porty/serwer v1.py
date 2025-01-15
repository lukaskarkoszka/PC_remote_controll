import zmq
import cv2
import numpy as np
import time

# Inicjalizacja kontekstu ZMQ
context = zmq.Context()

# Tworzenie socketu typu PUB
pub_socket = context.socket(zmq.PUB)
pub_socket.bind("tcp://*:5555")

# Tworzenie socketu typu SUB
sub_socket = context.socket(zmq.SUB)
sub_socket.connect("tcp://localhost:5556")
sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")

# Funkcja do przesyłania obrazu
def send_image(image_path):
    image = cv2.imread(image_path)
    _, buffer = cv2.imencode('.jpg', image)
    pub_socket.send(buffer.tobytes())

# Funkcja do przesyłania tekstu
def send_text(text):
    pub_socket.send_string(text)

# Funkcja do odbierania danych
def receive_data():
    while True:
        message = sub_socket.recv()
        if isinstance(message, bytes):
            # Odbieranie obrazu
            nparr = np.frombuffer(message, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            cv2.imshow('Received Image', image)
            cv2.waitKey(1)
        else:
            # Odbieranie tekstu
            print("Received text:", message.decode('utf-8'))

# Przykładowe użycie
if __name__ == "__main__":
    import threading
    threading.Thread(target=receive_data).start()
    while True:
        send_text("Hello, clients!")
        # send_image(r"C:\Users\Łukasz\Pictures\Bez nazwy-1.png")
        time.sleep(1)
