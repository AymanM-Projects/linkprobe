import csv
import glob
from channel import make_channel
profiles =[
    {"profile": "bernoulli-loss", "params": {"loss_rate": 0.1, }},
    {"profile": "gilbert-elliott", "params": {"loss_rate": 0.1, "mean_burst": 5} }
]

total_mismatch = 0
total_packets = 0


for run in profiles:
    for n in (1,2,3):
        matches = glob.glob(f"results/{run['profile']}_*_seed{n}_*.csv")
        path = matches[0]
        channel = make_channel(run['profile'], n, **run['params'])
        run_mismatch =0 
        run_packets = 0
        with open(path) as f:
            for row in csv.DictReader(f):
                run_packets += 1
                forward, _ = channel.decide(b"")
                if forward:
                    predicted = 0
                else:
                    predicted = 1
                recorder = int(row["lost"])
                if predicted != recorder:
                    print(f"Mismatch found in {path}: predicted={predicted}, recorder={recorder}, profile={run['profile']}, seed={n}, row['seq']={row['seq']}")
                    run_mismatch += 1
        print(f"Profile: {run['profile']}, Seed: {n}, Mismatches: {run_mismatch}, Packets: {run_packets}")
        total_mismatch += run_mismatch
        total_packets += run_packets

print(f"Total mismatches: {total_mismatch}, Total packets: {total_packets}")