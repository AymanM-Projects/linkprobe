"""Echo Server: receives packets from the client and returns the same packets."""

# udp : user data protocals, send data packets fast without waiting for a response or checking if the data was received.
# tcp : transmission control protocol, send data packets and wait for a response to ensure the data was received.

# in this case, we are using UDP because we want to measure the package loss and latency of the network.

# local host : 127.0.0.1
# port = 9999

import sys
import socket
import time
from channel import make_channel
from config import SERVER, PORT, PROFILE, SEED, PARAMS

channel = make_channel(PROFILE, SEED, **PARAMS)
print(f"Server on {SERVER}:{PORT} Profile={PROFILE} params = {PARAMS} seed ={SEED}")

sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # create a UDP socket
#AF_INET — use IPv4 addresses (the 127.0.0.1 style) 
#datagram — use UDP packets (as opposed to TCP streams) Sock_streams = tcp 
sock.bind((SERVER, PORT)) # the adress of the server, with port 9999, the server will listen for incoming packets on this port.


try:
    while True:
        data, addr = sock.recvfrom(1024) # receive data from the client, 1024 is the buffer size
        forward, delay = channel.decide(data)
        if not forward:
            continue
        if delay > 0:
            time.sleep(delay)
        sock.sendto(data, addr) # send the same data back to the client
        
except KeyboardInterrupt:
    print("Interrupted by user")
    sock.close()
    sys.exit(0)


