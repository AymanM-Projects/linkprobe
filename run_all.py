import sys  # for sys.excutable
import json # for json
import subprocess  # statrs other programs and talks to them
import argparse
import os 
import time



def make_flags(run, outdir): 
    flags = []
    for key, value in run.items():
        flag = "--"+str(key) 
        if flag == "--params":
            fly = json.dumps(value)
        else:
            fly = str(value)
        flags.append(flag)
        flags.append(fly)
    flags.append("--outdir")
    flags.append(outdir)
    return flags 


def make_matrix():
    MATRIX = []
    MATRIX.append({"profile": "clean", "seed": 1, "params": {}, "packets": 10000, "timeout": 0.1})
    for n in (1,2,3):
        MATRIX.append({"profile": "bernoulli-loss", "seed": n, "params": {"loss_rate": 0.1, }, "packets": 10000, "timeout": 0.1})
        MATRIX.append({"profile": "gilbert-elliott", "seed": n, "params": {"loss_rate": 0.1, "mean_burst": 5}, "packets": 10000, "timeout": 0.1})
    MATRIX.append({"profile": "jitter", "seed": 1, "params": {"mean_ms": 100, "sd_ms": 30}, "packets": 10000, "timeout": 1.0})
    for delay in range(0,251,50):
        MATRIX.append({"profile": "latency-ladder", "seed": 1, "params": {"delay_ms": delay}, "packets": 1000, "timeout": 1.0})
    return MATRIX



def run_one(run, outdir, log_file):
    flags = make_flags(run, outdir)
    server_cmd = [sys.executable, "echo_server.py"] + flags # so this will run pythone3 echo_server.py with the arguement
    client_cmd = [sys.executable, "echo_client.py"] + flags
    server = subprocess.Popen(server_cmd, stdout=subprocess.PIPE, text=True) # it starts teh server as a child process and returns immediatly, sends it to a pipe, and the end of pipe is server.stdout, text=True, means reads strings,
    try:
        line = server.stdout.readline() # waits for server to print and flush oe full line, uses flush=true
        if not line.startswith("Server on"):
            sys.exit(f"server failed to start: {line!r}")
        result= subprocess.run(client_cmd, stdout=log_file)
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait()

    if result.returncode !=0:
        sys.exit(f"client failed: {run['profile']} seed {run['seed']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser() # 1. an empty description of what flags this program takes
    parser.add_argument("--smoke", action="store_true")   # 2. declare one flag: a switch, no value after it
    args = parser.parse_args()       # 3. read sys.argv now; args.smoke is True or False
    matrix = make_matrix()
    outdir = "results/test" if args.smoke else "results"
    if args.smoke:
        for run in matrix:
            run["packets"] = 50
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "client.log"), "w") as log_file:
        for i, run in enumerate(matrix, start=1):
            print(f"[{i}/{len(matrix)}] {run['profile']} seed {run['seed']}", flush=True)
            t0=time.perf_counter ()
            run_one(run,outdir, log_file)
            t = time.perf_counter() - t0
            print(f" Done in {t:.1f}", flush=True)
    print("matrix finished")

