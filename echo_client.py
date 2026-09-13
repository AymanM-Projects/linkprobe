"""Echo Client: sends packets to the server. """

import socket
import struct
import time
from collections import Counter
import statistics

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # create a UDP socket
sock.settimeout(1.0)

SERVER = "127.0.0.1"
PACKETS = 1000
TIMEOUT = 1.0 
INTERVAL = 0.05 # seconds


sent = 0
lost = 0
current_run = 0
runs = []
rtts = []

for seq in range(1000):
    t_send= time.perf_counter()
    p = struct.pack("!Qd", seq , t_send)
    sock.sendto(p, ("127.0.0.1", 9999)) # send data to the server
    sent += 1
    try:
        data, addr = sock.recvfrom(1024) # receive data from the server, 1024 is the buffer size
        t_check = time.perf_counter()
        seq_back, t_back = struct.unpack("!Qd", data)
        if seq_back != seq:
            print(f"Sequence number mismatch: sent {seq}, received {seq_back}")
        rtt = (t_check - t_back)*1000
        rtts.append(rtt)
        print(f"seq: {seq_back}, rtt: {rtt:.4f} ms") # print the sequence number and the time it took in milliseconds
        if current_run > 0: # then we append the current run to the list of runs and reset the current run to 0
                    runs.append(current_run)
                    current_run = 0
    except TimeoutError:
        lost += 1
        current_run += 1 # if a packet is lost, we increment the current run of lost packets
        print("Lost packet, seq:", seq)
    time.sleep(0.05) # wait 0.1 seconds before sending the next packet
if current_run > 0:
    runs.append(current_run)

print(f"Sent: {sent}, Lost: {lost}, Loss rate: {lost/sent*100:.2f}%") # prints how many were sent, how many were lost, and the loss rate in percentage
if rtts:
    print(f"Average RTT: {statistics.mean(rtts):.4f} ms, Min RTT: {min(rtts):.4f} ms, Max RTT: {max(rtts):.4f} ms, Median RTT: {statistics.median(rtts):.4f} ms") # prints the average, minimum, and maximum round trip time in milliseconds

print(f"Run times: {Counter(runs)}") # prints how many times a packet was lost in a row
# counter is a class that counts the number of occurrences of each element in a list, and returns a dictionary with the element as the key and the number of occurrences as the value.
# for example a counter of [1, 2, 2, 3, 3, 3] would return {1: 1, 2: 2, 3: 3}

# a timeperf_counter() is a function that returns the value (in fractional seconds) of a performance counter, or in simpleier worsds, 
    # subtracts two arbtirary times to get difference