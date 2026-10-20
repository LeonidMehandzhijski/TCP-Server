import socket
import sys

host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.settimeout(2)
client.sendto(b"hello", (host, 5001))
try:
    reply, _ = client.recvfrom(1024)
    print(reply)
except socket.timeout:
    print("Timeout: no reply (lost, dropped, or host down)")
except ConnectionResetError:
    print("Reset: host is up, but nothing is listening on that port")