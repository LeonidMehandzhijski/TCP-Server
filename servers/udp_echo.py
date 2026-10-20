import socket

HOST = "0.0.0.0"
PORT = 5001

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, PORT))
print(f"Listening on {HOST}:{PORT}")

while True:
    data, addr = server.recvfrom(1024)
    print(f"Got {data!r} from {addr}")
    server.sendto(data,addr)