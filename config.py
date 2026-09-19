""" Config.py: The Settingss for 1 of the experiments run
Will connect the server and client """

PROFILE = "clean"
PARAMS = {}
SEED = 1
TIMEOUT = 0.1 
PACKETS = 1000
INTERVAL = 0.01
SERVER = "127.0.0.1"
PORT = 9999



# PROFILE             PARAMS                                    TIMEOUT
# clean               {}                                        0.1
# latency-ladder      {"delay_ms": 50}  (0,50,100,150,200,250)  1.0
# jitter              {"mean_ms": 100, "sd_ms": 30}             1.0
# bernoulli-loss      {"loss_rate": 0.10}                       0.1
# gilbert-elliott     {"loss_rate": 0.10, "mean_burst": 5}      0.1