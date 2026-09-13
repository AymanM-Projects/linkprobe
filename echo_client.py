"""Echo Client: sends packets to the server. """

import socket # makes udp
import struct # turns bites to strings and back
import time # for sleep and time
from collections import Counter # makes dictionaries that count the number of occurrences of each element in a list
import statistics # mean, median, max, min etc
import csv #makes a csv file to save the data 
from datetime import datetime # tells me current date and tiem
import os # for file path manipulation bascailly making a file  python cant do it 

PROFILE = "clean"
SERVER = "127.0.0.1"
PACKETS = 1000
TIMEOUT = 1.0 
INTERVAL = 0.05 # seconds
PORT = 9999
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # create a UDP socket
sock.settimeout(TIMEOUT)
sent = 0
lost = 0
current_run = 0
runs = []
rtts = []


os.makedirs("results", exist_ok=True)


timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

filename = f"results/{PROFILE}_{timestamp}.csv"
packet_file = open(filename, "w", newline="") # open a csv file to save the data
packet_writer = csv.writer(packet_file) # create a csv writer object[
packet_writer.writerow(["seq", "timestamp", "rtt_ms", "lost"]) # write the header row
t_start = time.perf_counter()

for seq in range(PACKETS):
    rtt= "" # this helps in csv file to know if the packet was lost or not, if it was lost, the rtt will be empty
    is_lost = 0 # same with this 
    t_send= time.perf_counter()
    # a timeperf_counter() is a function that returns the value (in fractional seconds) of a performance counter, or in simpleier worsds, 
        #subtracts two arbtirary times to get difference
    p = struct.pack("!Qd", seq , t_send)
    sock.sendto(p, (SERVER, PORT)) # send data to the server
    sent += 1
    try:
        data, addr = sock.recvfrom(1024) # receive data from the server, 1024 is the buffer size
        t_check = time.perf_counter()
        seq_back, t_back = struct.unpack("!Qd", data)
        if seq_back != seq:
            print(f"Sequence number mismatch: sent {seq}, received {seq_back}")
        rtt = (t_check - t_back)*1000
        is_lost = 0
        rtts.append(rtt)
        print(f"seq: {seq_back}, rtt: {rtt:.4f} ms") # print the sequence number and the time it took in milliseconds
        if current_run > 0: # then we append the current run to the list of runs and reset the current run to 0
                    runs.append(current_run)
                    current_run = 0
    except TimeoutError:
        lost += 1
        current_run += 1 # if a packet is lost, we increment the current run of lost packets
        is_lost = 1
        print("Lost packet, seq:", seq)
    time.sleep(INTERVAL) # wait 0.05 seconds before sending the next packet
    packet_writer.writerow([seq, t_send-t_start, rtt, is_lost]) # write the data to the csv file


packet_file.close() # close the csv file
if current_run > 0:
    runs.append(current_run)

print(f"Sent: {sent}, Lost: {lost}, Loss rate: {lost/sent*100:.2f}%") # prints how many were sent, how many were lost, and the loss rate in percentage
if rtts:
    print(f"Average RTT: {statistics.mean(rtts):.4f} ms, Min RTT: {min(rtts):.4f} ms, Max RTT: {max(rtts):.4f} ms, Median RTT: {statistics.median(rtts):.4f} ms") # prints the average, minimum, and maximum round trip time in milliseconds

print(f"Run times: {Counter(runs)}") # prints how many times a packet was lost in a row
# counter is a class that counts the number of occurrences of each element in a list, and returns a dictionary with the element as the key and the number of occurrences as the value.
# for example a counter of [1, 2, 2, 3, 3, 3] would return {1: 1, 2: 2, 3: 3}

