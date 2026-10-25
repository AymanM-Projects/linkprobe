import csv # read and write CSV files
import os # handle file paths and folders
import statistics # for calculating mean, median, etc.
from collections import Counter # for counting occurrences of elements in a list
import glob # for finding files matching a pattern


DEADLINE_MS = 50 # deadline in milliseconds for considering a packet as over the deadline
def parse_name(path): # uses the filename to extract profile, parameters, and seed value
    base = os.path.basename(path) # removes folder "results"
    name = os.path.splitext(base)[0] # removes the file extension "csv"
    parts = name.split("_") # splits the filename into parts based on the underscore delimiter (parameters, profile, seed)
    profile = parts[0] # the first part of the filename is the profile
    seed_idx = None  
    for i,part in enumerate(parts): # enumerate gives both the index and the value of each part
        if part.startswith("seed"): # ask each part if it starts with "seed" and if found breaks out of the loop
            seed = int(part[4:]) # removes the seed prefix and saves as an integer
            seed_idx = i # saves the index of the seed part
            break
    if seed_idx is None: # if no seed part was found
            raise ValueError(f"no seed value detected in {path}") # raises an error if no seed value is found
    params = "_".join(parts[1:seed_idx]) # joins that parts that include the parameters 
    return profile, params, seed # returns the profile, parameters, and seed value extracted from the filename
def read_run(path):
    with open(path) as f:  # opens a CSV file for a run
        lost_flags = [] #starts as an empty list to store lost flags (1 for lost, 0 for not lost)
        rtts = [] #starts as an empty list to store round-trip times
        for row in csv.DictReader(f):
            if row["lost"] == "1": # csv is in string format, "1" indicates a lost packet
                 lost_flags.append(1) 
            else:
                lost_flags.append(0)
                rtts.append(float(row["rtt_ms"])) # appends the round-trip time to the rtts list
    return rtts, lost_flags # returns both the list for each run
def summarize(rtts, lost_flags): # takes the list of RTTs and lost flags and calculates summary statistics

    packets_sent = len(lost_flags) # total number of packets sent
    lost = sum(lost_flags) # total number of lost packets
    loss_pct = lost/packets_sent  * 100 # percentage of lost packets
    mean_rtt_ms =statistics.mean(rtts) # mean round-trip time. uses statistics module and takes a mean from the list
    median_rtt_ms = statistics.median(rtts) # median round-trip time
    big = 0 # count of packets that exceeded the deadline
    for r in rtts:
        if r > DEADLINE_MS:
            big +=1 # for every packet over the deadline big increases by 1
    deadline_miss_pct =( lost + big)/packets_sent * 100 # percentage of packets that were either lost or exceeded the deadline
    p99_rtt_ms = sorted(rtts)[int(len(rtts)*0.99)] # 99th percentile round-trip time (so the highest times)
    return {"packets_sent": packets_sent, "lost": lost, "loss_pct": loss_pct, "mean_rtt_ms": mean_rtt_ms,"over_deadline": big,  "median_rtt_ms": median_rtt_ms, "p99_rtt_ms": p99_rtt_ms, "deadline_miss_pct": deadline_miss_pct} # makes a dict to return all summary values for each run
def burst_lengths(lost_flags): #takes the amount of consecutive lost packets and returns the lengths of each burst  
    runs = [] # list to store the lengths of each burst
    currentrun = 0 # current length of the ongoing burst
    for flag in lost_flags:
        if flag == 1:
            currentrun += 1 # increment the current burst length
        else:# if the packet is delivered successfully
            if currentrun>0 :# and burst was in progress
                runs.append(currentrun) # append the completed burst to the list
                currentrun = 0 # reset the current burst length
    if currentrun >0: # if the run ends with a burst of lost packets
        runs.append(currentrun) # append the final burst to the list
    burst = runs # assign the list of burst lengths to the variable 'burst'
    return burst # return the list of burst lengths


summary_rows = [] # makes a new list to store the summary rows for each run
burst_rows = [] # makes a new list to store the burst length rows for each run

paths = sorted(glob.glob("results/*.csv")) # find all CSV files in the "results" folder and sort them (alphabetically)
for path in paths:  # loops through each CSV file in the "results" folder
    profile, param, seed = parse_name(path) #reads profile, parameter, and seed from the file name
    rtts, lost_flags = read_run(path) # reads the run data from the CSV file( returns the list of RTTs and the list of lost flags)
    b = burst_lengths(lost_flags) # calculates the lengths of each burst of lost packets
    row = {"profile":profile, "param":param, "seed":seed} # creates a new row for the summary
    row.update(summarize(rtts,  lost_flags)) # merges  the row with the summary statistics(add summarize dict keys into row)
    if b: # if there are any bursts of lost packets
        row["mean_burst_len"] = round(statistics.mean(b), 3) # calculate the mean burst length
        row["max_burst_len"] = max(b) # calculate the maximum burst length

    else: # if there are no bursts of lost packets
        row["max_burst_len"] = "" # set the maximum burst length to empty
        row["mean_burst_len"] = "" # set the mean burst length to empty
    for col in [ "loss_pct", "mean_rtt_ms", "median_rtt_ms", "p99_rtt_ms", "deadline_miss_pct"]: # round the specified columns to 3 decimal places
        row[col] = round(row[col], 3)        
    summary_rows.append(row)  # add all the finishes and processed rows to the summary list
    for length, count in sorted(Counter(b).items()): # used counter to count the occurrences of each burst length. then uses .items to give key,value pairs for each unique burst length and its count and sorts in order
        burst_rows.append({"profile": profile, "param":param,"seed": seed,
                       "burst_len": length, "count": count}) # make one row per run(run, burst length) for example "GE seed 2 had N burst length" this ends up being used in plot burst.py
with open("summary.csv", "w", newline="") as f: # open the summary CSV file for writing(if anything was there before it is wiped)
    w = csv.DictWriter(f, fieldnames=["profile", "param", "seed", "packets_sent", "lost", "over_deadline", "loss_pct", "mean_rtt_ms", "median_rtt_ms", "p99_rtt_ms", "deadline_miss_pct", "mean_burst_len", "max_burst_len"]) # takes a dict and fieldnames is column order. each key in each row must be in this list
    w.writeheader() # write the header row to the CSV file
    w.writerows(summary_rows) # write all the summary rows to the CSV file
with open("burst_lengths.csv", "w", newline="") as f: # open the burst lengths CSV file for writing(if anything was there before it is wiped)
    w = csv.DictWriter(f, fieldnames=["profile", "param", "seed", "burst_len", "count"]) # takes a dict and fieldnames is collumn ordeer. each key in each row must be in this list
    w.writeheader() # write the header row to the CSV file
    w.writerows(burst_rows) # write all the burst length rows to the CSV file