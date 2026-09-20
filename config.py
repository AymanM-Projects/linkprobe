""" Config.py: The Settingss for 1 of the experiments run
Will connect the server and client """


import argparse # helps work with sys inputs
import json # used for formating and converting bytes of datra

TIMEOUT = 0.1 
PACKETS = 1000
INTERVAL = 0.01
SERVER = "127.0.0.1"
PORT = 9999
OUTDIR = "results" 
def load():
    link_parser = argparse.ArgumentParser()
    link_parser.add_argument("--seed", type=int, required=True) # adds seed as a required argument and converts to int
    link_parser.add_argument("--profile", choices=["clean", "latency-ladder", "jitter", "bernoulli-loss", "gilbert-elliott"  ], required=True)
    link_parser.add_argument("--params",type=json.loads, default={})
    link_parser.add_argument("--timeout", type=float, default=TIMEOUT)
    link_parser.add_argument("--packets", type=int, default=PACKETS)
    link_parser.add_argument("--outdir", type=str, default = OUTDIR)
    return link_parser.parse_args()
# a namespace in pythons is system where every objejcts has a unique name ot call opne instaed of using index numebrs 

if __name__ == "__main__":
    print(load())

# PROFILE             PARAMS                                    TIMEOUT
# clean               {}                                        0.1
# latency-ladder      {"delay_ms": 50}  (0,50,100,150,200,250)  1.0
# jitter              {"mean_ms": 100, "sd_ms": 30}             1.0
# bernoulli-loss      {"loss_rate": 0.10}                       0.1
# gilbert-elliott     {"loss_rate": 0.10, "mean_burst": 5}      0.1