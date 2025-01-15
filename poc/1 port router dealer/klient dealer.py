import zmq
import cv2
import numpy as np
import time

# Inicjalizacja kontekstu ZMQ
context = zmq.Context()

# Tworzenie socketu typu DEALER do odbierania i wysyłania danych
dealer_socket = context.socket(zmq.DEALER)
dealer_socket.connect("tcp://localhost:5555")

# Funkcja do wysyłania obrazu
def send_image(image_path):
    image = cv2.imread(image_path)
    _, buffer = cv2.imencode('.jpg', image)
    dealer_socket.send(buffer.tobytes())

# Funkcja do wysyłania tekstu
def send_text(text):
    dealer_socket.send_string(text)

# Funkcja do odbierania danych
def receive_data():
    while True:
        message = dealer_socket.recv()
        if isinstance(message, bytes):
            print("Received text:", message.decode('utf-8'))

# Przykładowe użycie
if __name__ == "__main__":
    import threading
    threading.Thread(target=receive_data).start()
    while True:
        # send_text("Hello, server!")
        # send_image("2.jpg")
        time.sleep(1)
