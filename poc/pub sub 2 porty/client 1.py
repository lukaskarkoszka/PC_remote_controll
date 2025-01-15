import zmq
import cv2
import numpy as np

# Inicjalizacja kontekstu ZMQ
context = zmq.Context()

# Tworzenie socketu typu SUB do odbierania danych od serwera
sub_socket = context.socket(zmq.SUB)
sub_socket.connect("tcp://localhost:5555")
sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")

# Tworzenie socketu typu PUB do wysyłania danych do serwera
pub_socket = context.socket(zmq.PUB)
pub_socket.connect("tcp://localhost:5556")

# Funkcja do odbierania danych
def receive_data():
    while True:
        message = sub_socket.recv()
        if isinstance(message, bytes):
            # # Odbieranie obrazu
            # nparr = np.frombuffer(message, np.uint8)
            # image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            # cv2.imshow('Received Image', image)
            # cv2.waitKey(1)
            # # Wysyłanie obrazu z powrotem do serwera
            # _, buffer = cv2.imencode('.jpg', image)
            # pub_socket.send(buffer.tobytes())
            print("obraz")
        else:
            # Odbieranie tekstu
            text = message.decode('utf-8')
            print("Received text:", text)
            # Wysyłanie tekstu z powrotem do serwera
            pub_socket.send_string(text)

# Przykładowe użycie
if __name__ == "__main__":
    receive_data()
