import csv
import os
import matplotlib.pyplot as plt


def read_rtts(path):
    rtts = []
    with open(path) as f:
        for row in csv.DictReader(f):
            if row["lost"] == "1":
                rtts.append(float("inf"))
            else:
                rtts.append(float(row["rtt_ms"]))
    return rtts

def miss_percentage(rtts, deadline_ms):
    missed = 0
    for rtt in rtts:
        if rtt > deadline_ms:
            missed += 1
    return missed / len(rtts) * 100

RUNS = {
    "0 ms fixed":   "results/latency-ladder_delay_ms0_seed1_20260920_114854.csv",
    "50 ms fixed":  "results/latency-ladder_delay_ms50_seed1_20260920_114906.csv",
    "100 ms fixed": "results/latency-ladder_delay_ms100_seed1_20260920_115013.csv",
    "150 ms fixed": "results/latency-ladder_delay_ms150_seed1_20260920_115209.csv",
    "200 ms fixed": "results/latency-ladder_delay_ms200_seed1_20260920_115456.csv",
    "250 ms fixed": "results/latency-ladder_delay_ms250_seed1_20260920_115833.csv",
    "jitter (mean 100, sd 30)": "results/jitter_mean_ms100_sd_ms30_seed1_20260920_112911.csv",
}

deadlines = list(range(0,301))

fig, ax = plt.subplots()
for label, path in RUNS.items():
    rtts = read_rtts(path)
    miss_pcts = []
    for deadline in deadlines:
        miss_pcts.append(miss_percentage(rtts, deadline))
    ax.plot(deadlines, miss_pcts,  label=label)
ax.set_xlabel("Deadline (ms)")
ax.set_ylabel("Packets missed deadline percentage (%)")
ax.axvline(50, color="gray", linestyle=":", linewidth=0.8, label="analyze.py deadline (50 ms)")
ax.legend()
os.makedirs("figures", exist_ok=True)
fig.savefig("figures/deadline_sweep.png", dpi=350, bbox_inches="tight")
fig.savefig("figures/deadline_sweep.pdf", dpi=350, bbox_inches="tight")
ax.set_title("Deadline Sweep: Missed Deadline Percentage vs Deadline (ms)")
fig.savefig("figures/deadline_sweep_titled.png", dpi=350, bbox_inches="tight")
fig.savefig("figures/deadline_sweep_titled.pdf", dpi=350, bbox_inches="tight")