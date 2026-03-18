import socket

HOST = '127.0.0.1'
PORT = 5002

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((HOST, PORT))

server.listen(2)

print("Очікування двох клієнтів...")

conn1, addr1 = server.accept()
print("Клієнт 1 підключився:", addr1)

conn1.send("Ви клієнт 1. Очікуйте другого.".encode())

conn2, addr2 = server.accept()
print("Клієнт 2 підключився:", addr2)

conn2.send("Ви клієнт 2.".encode())

conn1.send("Другий клієнт підключився. Можете почати чат.".encode())
conn2.send("Можете почати чат.".encode())

while True:

    msg1 = conn1.recv(1024)

    if not msg1:
        break

    print("Клієнт 1:", msg1.decode())

    conn2.send(msg1)

    msg2 = conn2.recv(1024)

    if not msg2:
        break

    print("Клієнт 2:", msg2.decode())

    conn1.send(msg2)

conn1.close()
conn2.close()
server.close()