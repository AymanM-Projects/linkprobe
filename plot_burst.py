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

theory_ks = []
ge_ps = []
bern_ps = []
for k in range(1, 31):
    theory_ks.append(k)
    ge_ps.append(0.8 ** (k - 1))
    bern_ps.append(0.1 ** (k - 1))
ax.plot(theory_ks, ge_ps, color = COLORS["gilbert-elliott"], linestyle="--", linewidth=0.8, label= "Gilbert-Elliott theory")
ax.plot(theory_ks, bern_ps, color = COLORS["bernoulli-loss"], linestyle="--", linewidth=0.8, label= "Bernoulli-loss theory")
ax.set_yscale("log")
ax.set_yticks([1, 0.1, 0.01, 0.001])
ax.set_yticklabels(["1", "0.1", "0.01", "0.001"])
ax.set_ylim(0.0005, 1.5)

ax.set_xlabel("burst length k (consecutive lost packets)")
ax.set_ylabel("fraction of loss bursts with length ≥ k")
ax.legend()
os.makedirs("figures", exist_ok=True)
fig.savefig("figures/burst_ccdf.png", dpi=300, bbox_inches="tight")
fig.savefig("figures/burst_ccdf.pdf", dpi=300, bbox_inches="tight")
ax.set_title("Burst-length CCDF: Bernoulli vs Gilbert-Elliott at 10% loss") 
 # ccdf stand for complementary cumulative distribution function
fig.savefig("figures/burst_ccdf_titled.png", dpi=300, bbox_inches="tight")
fig.savefig("figures/burst_ccdf_titled.pdf", dpi=300, bbox_inches="tight")
