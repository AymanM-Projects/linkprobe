"""Echo Client: sends packets to the server. """
#rtt is round trip time, the time it takes for a packet to go from the client to the server and back to the client.

import socket # makes udp
import struct # turns bites to strings and back
import time # for sleep and time
from collections import Counter # makes dictionaries that count the number of occurrences of each element in a list
import statistics # mean, median, max, min etc
import csv #makes a csv file to save the data 
from datetime import datetime # tells me current date and tiem
import os # for file path manipulation bascailly making a file  python cant do it 
import sys


PROFILE = "clean"
SERVER = "127.0.0.1"
PACKETS = 1000
TIMEOUT = 1.0
INTERVAL = 0.01 # seconds
PORT = 9999
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # create a UDP socket
sent = 0
lost = 0
late = 0
current_run = 0
runs = []
rtts = []


os.makedirs("results", exist_ok=True)


timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

filename = f"results/{PROFILE}_{timestamp}.csv"
packet_file = open(filename, "w", newline="") # open a csv file to save the data
packet_writer = csv.writer(packet_file) # create a csv writer object[
packet_writer.writerow(["seq", "times_elapsed_secs", "rtt_ms", "lost"]) # write the header row
t_start = time.perf_counter()
try: 
    for seq in range(PACKETS):
        rtt= "" # this helps in csv file to know if the packet was lost or not, if it was lost, the rtt will be empty
        is_lost = 0 # same with this 
        t_send= time.perf_counter() # a timeperf_counter() is a function that returns the value (in fractional seconds) of a performance counter, or in simpleier worsds, subtracts two arbtirary times to get difference
        p = struct.pack("!Qd", seq , t_send)
        sock.sendto(p, (SERVER, PORT)) # send data to the server
        sent += 1



        Deadline = t_send + TIMEOUT # this is gonna fix an error to actually show a lost packet intead of it coming when the timeout is over, so we can actually see the lost packet in the csv file 
        got_reply = False
        while True:
            remaining = Deadline - time.perf_counter() # remaining time until the deadline is reached
            if remaining <= 0:
                 break
            sock.settimeout(remaining)
            try: 
                data, addr = sock.recvfrom(1024) # receive data from the server, 1024 is the buffer size
            except TimeoutError:
                break
            t_check = time.perf_counter()
            seq_back, t_back = struct.unpack("!Qd", data)
            if seq_back == seq:
                rtt = (t_check - t_back) * 1000
                got_reply = True
                break
            late += 1
            print(f"Late reply for seq {seq_back} (was waiting on {seq})")

        if got_reply:
            rtts.append(rtt)
            print(f"seq: {seq_back}, rtt: {rtt:.4f} ms") # print the sequence number and the time it took in milliseconds
            if current_run > 0: # then we append the current run to the list of runs and reset the current run to 0
                runs.append(current_run)
                current_run = 0
        else:
            lost += 1
            current_run += 1 # if a packet is lost, we increment the current run of lost packets
            is_lost = 1
            print("Lost packet, seq:", seq)
        packet_writer.writerow([seq_back, t_send-t_start, rtt, is_lost]) # write the data to the csv file
        time.sleep(INTERVAL) # wait interval seconds before sending the next packet

    total_Runtime = time.perf_counter() - t_start
    
    packet_file.close() # close the csv file
    if current_run > 0:
        runs.append(current_run)

    print(f"Sent: {sent}, Lost: {lost}, Late {late}, Loss rate: {lost/sent*100:.2f}%") # prints how many were sent, how many were lost, and the loss rate in percentage
    if rtts:
        print(f"Average RTT: {statistics.mean(rtts):.4f} ms, Min RTT: {min(rtts):.4f} ms, Max RTT: {max(rtts):.4f} ms, Median RTT: {statistics.median(rtts):.4f} ms") # prints the average, minimum, and maximum round trip time in milliseconds
    print(f"Run times: {Counter(runs)}") # prints how many times a packet was lost in a row
    # counter is a class that counts the number of occurrences of each element in a list, and returns a dictionary with the element as the key and the number of occurrences as the value.
    # for example a counter of [1, 2, 2, 3, 3, 3] would return {1: 1, 2: 2, 3: 3}
    print(f"Total runtime: {total_Runtime:.2f} s ({total_Runtime/60:.1f} min)") # prints the total time it took to send all the packets
    print(f"Actual send rate: {sent/total_Runtime:.1f} packets/s") # how many packets were sent over total time 



except KeyboardInterrupt:
    print("Interrupted by user")
    packet_file.close()
    sys.exit(0)