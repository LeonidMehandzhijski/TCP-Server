import socket
import sys

host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, 5000))
client.sendall(b"hello")
reply = client.recv(1024)
print(reply)
client.close()