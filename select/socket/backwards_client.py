import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 50000))
s.sendall(b'Hello, world')
data = True
while data:
    data = s.recv(3)
    print(data)
s.close()
