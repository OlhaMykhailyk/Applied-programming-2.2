import socket
import os

HOST = '127.0.0.1'
PORT = 5001

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((HOST, PORT))

filename = input("Введіть шлях до файлу: ")

name = os.path.basename(filename)

client.send(name.encode())

file = open(filename, "rb")

while True:

    data = file.read(1024)

    if not data:
        break

    client.send(data)

file.close()

client.close()

print("Файл відправлено")