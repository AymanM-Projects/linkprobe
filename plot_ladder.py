import csv
import os
import matplotlib.pyplot as plt


points = []
with open("summary.csv") as f:
    for row in csv.DictReader(f):
        if row["profile"] != "latency-ladder":
            continue
        delay = int(row["param"].replace("delay_ms", ""))
        points.append((delay, float(row["median_rtt_ms"]), float(row["p99_rtt_ms"])))
points = sorted(points)

delays = []
medians = []
p99s = []
for delay, median, p99 in points:
    delays.append(delay)
    medians.append(median)
    p99s.append(p99)
fig, ax = plt.subplots()
ax.plot(delays, medians, marker="o", label="median RTT")
ax.plot(delays, p99s, marker="o", label="p99 RTT")
ax.plot([0,250], [0,250], color="black", linestyle="--", label="RTT = injected delay")
ax.set_xlabel("Injected Delay (ms)")
ax.set_ylabel("Measured RTT (ms)")
ax.legend()
os.makedirs("figures", exist_ok=True)
fig.savefig("figures/latency_ladder.png", dpi=300, bbox_inches="tight")
fig.savefig("figures/latency_ladder.pdf", dpi=300, bbox_inches="tight")
ax.set_title("Latency Ladder: Measured RTT vs Injected Delay")
fig.savefig("figures/latency_ladder_titled.png", dpi=300, bbox_inches="tight")
fig.savefig("figures/latency_ladder_titled.pdf", dpi=300, bbox_inches="tight")