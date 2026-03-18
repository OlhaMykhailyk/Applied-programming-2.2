import socket
import ast

HOST = '127.0.0.1'
PORT = 5000

def check_expression(expr):
    try:
        ast.parse(expr, mode='eval')
        return "Вираз синтаксично правильний"
    except:
        return "Помилка синтаксису"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

print("Сервер запущено...")

while True:
    conn, addr = server.accept()
    print("Підключено:", addr)

    data = conn.recv(1024).decode()

    if not data:
        break

    print("Отримано:", data)

    result = check_expression(data)

    conn.send(result.encode())

    conn.close()
