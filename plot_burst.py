import csv
import matplotlib.pyplot as plt 
import os




KEEP = ("bernoulli-loss", "gilbert-elliott")
COLORS  = {"bernoulli-loss": "tab:blue", "gilbert-elliott" : "tab:orange"}

groups = {}
with open("burst_lengths.csv") as f:
    for row in csv.DictReader(f):
        if row["profile"] not in KEEP:
            continue
        key = (row["profile"], int(row["seed"]))
        groups.setdefault(key, {})[int(row["burst_len"])] = int(row["count"])
fig, ax = plt.subplots()

for key, counts in groups.items():
    profile, seed = key 
    total = sum(counts.values())
    remaining = total
    label = profile if seed == 1 else "_nolegend_"     
    ks = []
    ps = []
    for k in range(1, (max(counts)+1)):
            ks.append(k)
            ps.append(remaining/total)
            remaining = remaining - counts.get(k,0)
    ax.plot(ks,ps,color = COLORS[profile], linewidth =1, drawstyle ="steps-post", label = label )
ax.set_yscale("log")
ax.set_xlabel("burst length k (consecutive lost packets)")
ax.set_ylabel("fraction of loss bursts with length >= k")
ax.legend()
os.makedirs("figures", exist_ok=True)
fig.savefig("figures/burst_ccdf.png", dpi=300, bbox_inches="tight")
fig.savefig("figures/burst_ccdf.pdf", dpi=300, bbox_inches="tight")


