"""linkprobe: single entry point, used for the packaged executable.

    linkprobe demo                     Bernoulli vs Gilbert-Elliott at 10% loss, side by side
    linkprobe demo --profile jitter --params '{"mean_ms": 100, "sd_ms": 30}' --timeout 1.0
    linkprobe server --profile clean --seed 1
    linkprobe client --profile clean --seed 1
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile

USAGE = __doc__



def self_cmd(sub):
    """Command that re-runs this program with a subcommand (works frozen or as a script)."""
    if getattr(sys, "frozen", False):  # PyInstaller executable
        return [sys.executable, sub]
    return [sys.executable, os.path.abspath(__file__), sub]


def run_server(argv):
    sys.argv = ["linkprobe server"] + argv
    import echo_server  # noqa: F401  (the module runs on import)


def run_client(argv):
    sys.argv = ["linkprobe client"] + argv
    import echo_client  # noqa: F401


def one_run(profile, seed, params, packets, timeout, outdir):
    flags = ["--profile", profile, "--seed", str(seed), "--params", json.dumps(params),
             "--packets", str(packets), "--timeout", str(timeout), "--outdir", outdir]
    server = subprocess.Popen(self_cmd("server") + flags, stdout=subprocess.PIPE, text=True)
    try:
        line = server.stdout.readline()
        if not line.startswith("Server on"):
            sys.exit(f"server failed to start: {line!r}")
        with tempfile.TemporaryFile("w+") as log:
            result = subprocess.run(self_cmd("client") + flags, stdout=log, text=True)
            log.seek(0)
            out = log.read().splitlines()
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
    if result.returncode != 0:
        sys.exit(f"client failed for profile {profile}")
    keep = ("Saving to", "Sent:", "Average RTT", "Run times", "Total runtime", "WARNING")
    return [l for l in out if l.startswith(keep)]


def demo(argv):
    p = argparse.ArgumentParser(prog="linkprobe demo")
    p.add_argument("--profile", choices=["clean", "latency-ladder", "jitter", "bernoulli-loss", "gilbert-elliott"],
                   help="run one profile instead of the default Bernoulli vs Gilbert-Elliott comparison")
    p.add_argument("--params", type=json.loads, default={})
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--packets", type=int, default=1000)
    p.add_argument("--timeout", type=float, default=0.1)
    p.add_argument("--outdir", default="linkprobe_results")
    a = p.parse_args(argv)

    if a.profile:
        runs = [(a.profile, a.params)]
    else:
        runs = [("bernoulli-loss", {"loss_rate": 0.1}),
                ("gilbert-elliott", {"loss_rate": 0.1, "mean_burst": 5})]
        print("linkprobe demo: same 10% loss rate, independent vs bursty losses, over loopback.")
    print(f"{a.packets} packets per run at 100 packets/s (about {a.packets / 100 * len(runs):.0f} s total).\n")

    for profile, params in runs:
        print(f"== {profile} {params or ''}".rstrip(), flush=True)
        for line in one_run(profile, a.seed, params, a.packets, a.timeout, a.outdir):
            print("   " + line)
        print(flush=True)
    if not a.profile:
        print("'Run times' maps burst length -> count. Same loss rate, but Gilbert-Elliott losses")
        print("arrive in much longer runs: that is the effect linkprobe was built to show.")


def main():
    if len(sys.argv) < 2:  # double-clicked or run bare: run the demo
        demo([])
        if getattr(sys, "frozen", False) and sys.stdin and sys.stdin.isatty():
            input("\nPress Enter to exit...")
        return
    if sys.argv[1] in ("-h", "--help"):
        print(USAGE)
        return
    sub, rest = sys.argv[1], sys.argv[2:]
    if sub == "demo":
        demo(rest)
    elif sub == "server":
        run_server(rest)
    elif sub == "client":
        run_client(rest)
    else:
        sys.exit(f"unknown command {sub!r}\n{USAGE}")


if __name__ == "__main__":
    main()
