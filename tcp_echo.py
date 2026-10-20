import socket
import threading

HOST = "127.0.0.1"
PORT = 5000

def handle_client(conn, addr):
    print(f"Connected by {addr[0]}:{addr[1]}")
    while True:
        data = conn.recv(1024)
        if not data:
            break
        conn.sendall(data)
    conn.close()
    print(f"Caller {addr[0]}:{addr[1]} hung up")


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()
print(f"Listening on {HOST}:{PORT}")

while True:
    conn, addr = server.accept()
    worker = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
    worker.start()