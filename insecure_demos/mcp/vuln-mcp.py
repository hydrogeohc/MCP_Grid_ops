import socket

# 🚨 This server executes arbitrary Python code sent by the client!
HOST = '0.0.0.0'
PORT = 5002

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Vulnerable MCP server listening on {HOST}:{PORT}")
    while True:
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            data = conn.recv(1024)
            try:
                # 🚨 RCE vulnerability
                exec(data.decode())
                conn.sendall(b"Executed command.")
            except Exception as e:
                conn.sendall(str(e).encode())
