import csv
import os
import statistics
from collections import Counter 
import glob


DEADLINE_MS = 50
def parse_name(path):
    base = os.path.basename(path)
    name = os.path.splitext(base)[0]
    parts = name.split("_")
    profile = parts[0]
    for part in parts:
        if part.startswith("seed"):
           seed = int(part[4:])

    return profile, seed
def read_run(path):
    with open(path) as f:
        lost_flags = []
        rtts = []
        for row in csv.DictReader(f):
            if row["lost"] == "1":
                 lost_flags.append(1)
            else:
                lost_flags.append(0)
                rtts.append(float(row["rtt_ms"]))
    return rtts, lost_flags
def summarize(rtts, lost_flags):

    packets_sent = len(lost_flags) 
    lost = sum(lost_flags)
    loss_pct = lost/packets_sent  * 100
    mean_rtt_ms =statistics.mean(rtts)
    median_rtt_ms = statistics.median(rtts)
    big = 0
    for r in rtts:
        if r > DEADLINE_MS:
            big +=1
    deadline_miss_pct =( lost + big)/packets_sent * 100
    p99_rtt_ms = sorted(rtts)[int(len(rtts)*0.99)]
    return {"packets_sent": packets_sent, "lost": lost, "loss_pct": loss_pct, "mean_rtt_ms": mean_rtt_ms, "median_rtt_ms": median_rtt_ms, "p99_rtt_ms": p99_rtt_ms, "deadline_miss_pct": deadline_miss_pct}
def burst_lengths(lost_flags):
    runs = []
    currentrun = 0
    for flag in lost_flags:
        if flag == 1:
            currentrun += 1
        else:
            if currentrun>0:
                runs.append(currentrun)
                currentrun = 0
    if currentrun >0:
        runs.append(currentrun)
    burst = runs
    return burst


summary_rows = []
burst_rows = []

paths = sorted(glob.glob("results/*.csv"))
for path in paths: 
    profile, seed = parse_name(path)
    rtts, lost_flags = read_run(path)
    b = burst_lengths(lost_flags)
    row = {"profile":profile, "seed":seed}
    row.update(summarize(rtts,  lost_flags))
    if b:
        row["mean_burst_len"] = statistics.mean(b)
        row["max_burst_len"] = max(b)
    else: 
        row["max_burst_len"] = 0
        row["mean_burst_len"] = 0
    summary_rows.append(row)
    for length, count in Counter(b).items():
        burst_rows.append({"profile": profile, "seed": seed,
                       "burst_len": length, "count": count})
with open("results/summary.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["profile", "param", "seed", "packets_sent", "lost", "late", "loss_pct", "mean_rtt_ms", "median_rtt_ms", "p99_rtt_ms", "deadline_miss_pct", "mean_burst_len", "max_burst_len"])
    w.writeheader()
    w.writerows(summary_rows)