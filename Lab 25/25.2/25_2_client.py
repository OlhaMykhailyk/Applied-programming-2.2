import socket

HOST = '127.0.0.1'
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((HOST, PORT))

expr = input("Введіть арифметичний вираз: ")

client.send(expr.encode())

data = client.recv(1024).decode()

print("Відповідь сервера:", data)

client.close()