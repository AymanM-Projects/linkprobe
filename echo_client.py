"""Echo Client: sends packets to the server. """
#rtt is round trip time, the time it takes for a packet to go from the client to the server and back to the client.

import socket # creates a network for sending and receiving data, in our case we will use udp
import struct # converts numbers to bytes and back
import time # for sleep and time
from collections import Counter # makes dictionaries that count the number of occurrences of each element in a list
import statistics # mean, median, max, min etc
import csv #makes a csv file to save the data 
from datetime import datetime # tells me current date and tiem
import os # for file path manipulation basically making a file or directory if it doesn't exist. os is specifially for folders and file paths
import sys # used for sys.exit (stops program with control-c)
from config import INTERVAL, SERVER, PORT # interval - gap between packets, server - server address, port - server port
from config import load # loads the configuration from command-line arguments

args = load() # reads the flags that run_all.py passed in 
PROFILE = args.profile
SEED = args.seed
PARAMS = args.params
PACKETS = args.packets
TIMEOUT = args.timeout
LOC = args.outdir # which folder to save the results in
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # create a UDP socket
sent = 0 # used to count the number of packets sent
lost = 0 # used to count the number of packets lost
late = 0 # used to count the number of late replies
current_run = 0 # length of the current burst of lost packets
runs = [] # list of all burst lengths
rtts = [] # list of all round trip times


os.makedirs(LOC, exist_ok=True) # this creates the output folder if it doesn't already exist


timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") # creates a timestamp string for the filename

param_text = "_".join(f"{key}{value}" for key, value in PARAMS.items()) # creates a string representation of the parameters for the filename that comes from the command-line arguments in run_all.py
parts = [PROFILE, param_text, f"seed{SEED}", timestamp] # list of parts for the filename
name = "_".join(part for part in parts if part) # join the parts with underscores to form the filename
filename = os.path.join(LOC, name + ".csv") # full path to the CSV file where results will be saved
print(f"Run: profile={PROFILE}  params={PARAMS}  seed={SEED}  packets={PACKETS}  timeout={TIMEOUT}  interval={INTERVAL}")
print(f"Saving to {filename}")
packet_file = open(filename, "w", newline="") # open a csv file to save the data
packet_writer = csv.writer(packet_file) # turns python list into one correctly formatted CSV row
packet_writer.writerow(["seq", "times_elapsed_secs", "rtt_ms", "lost"]) # write the header row
t_start = time.perf_counter() # record the start time of the experiment
try:  # run everhting below, if user presses Ctrl C jump to lin 112 and exit. Ensures proper csv closure.
    for seq in range(PACKETS): # runs once per packet. seq is the sequence number of the current packet
        rtt= "" # this helps in csv file to know if the packet was lost or not, if it was lost, the rtt will be empty string. this also makes the program assume that the packet is lost until proven that it was received and came back
        is_lost = 0  # can be changed by line 88 if packet is loss(always either 0 or 1)
        t_send= time.perf_counter() # a timeperf_counter() is a function that returns the value (in fractional seconds) of a performance counter.You subtract two readings to get a duration. in this instance it is the packet send time
        p = struct.pack("!Qd", seq , t_send) # packs the packet into 16 bytes (8 for seq, 8 for t_send)
        sock.sendto(p, (SERVER, PORT)) # send the packed packet to the server
        sent += 1 # increment the count of sent packets



        Deadline = t_send + TIMEOUT # the deadline makes sure a late reply isn't mistaken for this packet, and that no packet waits longer than TIMEOUT in total
        got_reply = False # flag to indicate if a reply was received for the current packet
        while True: # keep checking until break
            remaining = Deadline - time.perf_counter() # remaining time until the deadline is reached, used to set the socket timeout
            if remaining <= 0: # if the remaining time is less than or equal to 0, break the loop
                break
            sock.settimeout(remaining) # set the socket timeout to the remaining time. this tells the socket to wait at most remaining seconds for the next packet
            try: 
                data, addr = sock.recvfrom(1024) # receive data from the server, 1024 is the buffer size. this stops or pauses the program until a packet arrives or the timeout is reached.
            except TimeoutError:
                break # now the packet is lost because the timeout was reached before receiving a reply
            t_check = time.perf_counter() # time replay came back from the server
            seq_back, t_back = struct.unpack("!Qd", data) # unpack the received packet into sequence number and timestamp reverse of line 52
            if seq_back == seq: # ask if this is the packet we are currently waiting on
                rtt = (t_check - t_back) * 1000 # calculate the round-trip time in milliseconds
                got_reply = True # mark that a reply was received
                break # exit the loop since we got the expected reply
            late += 1 # this only happens if the sequence number of the received packet does not match the one we are waiting on
            print(f"Late reply for seq {seq_back} (was waiting on {seq})") # print a message indicating a late reply

        if got_reply: # if a reply was received for the current sequence number
            rtts.append(rtt) # add the round-trip time to the list of RTTs
            print(f"seq: {seq_back}, rtt: {rtt:.4f} ms") # print the sequence number and the time it took in milliseconds
            if current_run > 0: # then we append the current run to the list of runs and reset the current run to 0
                runs.append(current_run)
                current_run = 0
            assert sum(runs) == lost, "burst lengths don't add up to the loss count" # assert basically means it checks the sum of the runs and then if it is false then it prints our error message. all lost have to be in runs
        else:
            lost += 1
            current_run += 1 # if a packet is lost, we increment the current run of lost packets
            is_lost = 1
            print("Lost packet, seq:", seq)
        packet_writer.writerow([seq, t_send-t_start, rtt, is_lost]) # write the data to the csv file
        time.sleep(INTERVAL) # wait interval seconds before sending the next packet

    total_Runtime = time.perf_counter() - t_start  # calculate the total runtime in seconds
    
    packet_file.close() # close the csv file
    if current_run > 0:
        runs.append(current_run) # this is if the run ended with a sequence of lost packets(burst)

    print(f"Sent: {sent}, Lost: {lost}, Late: {late}, Loss rate: {lost/sent*100:.2f}%") # prints how many were sent, how many were lost, and the loss rate in percentage
    if rtts: # empty list check, only print RTT statistics if there are any RTTs recorded 
        print(f"Average RTT: {statistics.mean(rtts):.4f} ms, Min RTT: {min(rtts):.4f} ms, Max RTT: {max(rtts):.4f} ms, Median RTT: {statistics.median(rtts):.4f} ms") # prints the average, minimum, median , and maximum round trip time in milliseconds
    print(f"Run times: {Counter(runs)}") # prints how many times a packet was lost in a row
    # counter is a class that counts the number of occurrences of each element in a list, and returns a dictionary with the element as the key and the number of occurrences as the value.
    # for example a counter of [1, 2, 2, 3, 3, 3] would return {1: 1, 2: 2, 3: 3}
    print(f"Total runtime: {total_Runtime:.2f} s ({total_Runtime/60:.1f} min)") # prints the total time it took to send all the packets
    print(f"Actual send rate: {sent/total_Runtime:.1f} packets/s") # how many packets were sent over total time 
    if late > 0:
        print(f"WARNING: {late} late replies. In a loss profile this should be 0, so TIMEOUT may be too short.")



except KeyboardInterrupt:
    print("Interrupted by user")
    packet_file.close()
    sys.exit(0) # closes csv and exits the program