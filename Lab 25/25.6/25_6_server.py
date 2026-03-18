import socket
import os

HOST = '127.0.0.1'
PORT = 5001

SAVE_DIR = "server_files"

if not os.path.exists(SAVE_DIR):
    os.mkdir(SAVE_DIR)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((HOST, PORT))

server.listen()

print("Сервер очікує підключення...")

while True:

    conn, addr = server.accept()
    print("Підключився:", addr)

    filename = conn.recv(1024).decode()

    filepath = os.path.join(SAVE_DIR, filename)

    file = open(filepath, "wb")

    print("Отримання файлу:", filename)

    while True:

        data = conn.recv(1024)

        if not data:
            break

        file.write(data)

    file.close()

    print("Файл збережено")

    conn.close()