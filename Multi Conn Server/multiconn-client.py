import sys
import socket
import selectors
import types

sel = selectors.DefaultSelector()
messages = [b"Message 1 from client.", b"Message 2 from client."]

def start_connections(host, port, num_conns):
    server_addr = (host, port)
    for i in range(0, num_conns):
        connid = i + 1
        print(f"Starting connection {connid} to {server_addr}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(
            connid=connid,
            msg_total=sum(len(m) for m in messages),
            recv_total=0,
            messages=messages.copy(),
            outb=b"",
        )
        sel.register(sock, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            print(f"Received {recv_data!r} from connection {data.connid}")
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.msg_total:
            print(f"Closing connection {data.connid}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print(f"Sending {data.outb!r} to connection {data.connid}")
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

# Add argument validation
if len(sys.argv) != 4:
    print("Usage: python multiconn-client.py <host> <port> <num_connections>")
    print("Example: python multiconn-client.py localhost 8080 3")
    sys.exit(1)

try:
    host, port, num_conns = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
except ValueError:
    print("Error: Port and num_connections must be valid integers")
    sys.exit(1)

# Validate inputs
if not (1 <= port <= 65535):
    print("Error: Port must be between 1 and 65535")
    sys.exit(1)

if not (1 <= num_conns <= 100):  # Reasonable limit
    print("Error: Number of connections must be between 1 and 100")
    sys.exit(1)

start_connections(host, port, num_conns)

try:
    while True:
        # Check if all connections are done before calling select
        if not sel.get_map():
            print("All connections completed, exiting")
            break
            
        events = sel.select(timeout=1)
        for key, mask in events:
            service_connection(key, mask)
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()