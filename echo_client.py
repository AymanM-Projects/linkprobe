"""Echo Client: sends packets to the server. """

import socket
import struct
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # create a UDP socket
sock.settimeout(1.0)



for seq in range(100):
    t_send= time.perf_counter()
    p = struct.pack("!Qd", seq , t_send)
    sock.sendto(p, ("127.0.0.1", 9999)) # send data to the server
    sent = +1
    try:
        data, addr = sock.recvfrom(1024) # receive data from the server, 1024 is the buffer size
        t_check = time.perf_counter()
        seq_back, t_back = struct.unpack("!Qd", data)
        print(f"seq: {seq_back}, rtt: {(t_check-t_back)*1000:.4f} ms") # print the sequence number and the time it took in milliseconds
    except TimeoutError:
        lost = +1
        print("Lost packet, seq:", seq)
# a timeperf_counter() is a function that returns the value (in fractional seconds) of a performance counter, or in simpleier worsds, 
    # subtracts two arbtirary times to get difference