# linkprobe
 A codebase that will measure what a network does to messages between two machines: round-trip time, packet loss, and how long losses run in a row. Then degrades the link on purpose through five named profiles, one command each. Built for latency-sensitive robotics work, used as part of experimental methodology layer in robotics research . 


## Why

Often when networks transfer packets from machines, they lose packets and extra run time and add delay, or drop them in unnecessary bursts. Most current work assumes losses are independent. Through linkprobe, observations of what happens during packet loss and creating a formula to identify and combat that is the main goal. 

## What it measures

- Round trip time per message(seconds of how long packets take from one machine to another)
- packet sequence gaps(packet loss)
- Run length(how many packets were lost back to back)

## The profiles
   "A profile will show the type of degradability during packet tranfers in this experiment"
| Profile | What it does | 
| -------- | -------- |
| clean | Baseline - No loss or damage| 
| latency-ladder | a fixed delay, stepped: 0, 50, 100, 150, 200, 250 ms | 
| jitter | varying delay - mean 100ms|
| bernoulli-loss | packets get dropped independently with a probability of p, common assumption in modern network research |
| gilbert-elliott | losses arrives in bursts - many packets loss at one |


## Install

<!-- fill in once there's something to install -->

## Status

### Day 1 — Sept 3: setup
Created the README, GitHub repo, and Hackatime and Stardance accounts. Did beginning research on packet loss in networks.

### Day 2 — Sept 13: the measurement loop
- Built `echo_server.py` (UDP, sends every packet straight back unchanged) and `echo_client.py` (sends numbered, timestamped packets). RTT is computed from the send time carried inside the reply, so only the client's clock is ever read and no clock synchronization is needed.
- Added timeout-based loss detection and burst run-length tracking. Verified by killing and restarting the server on purpose: the client recovered bursts of 5 and 8, then 7, 7 and 11.
- Per-packet results saved to CSV in `results/`. Lost packets get an empty RTT, not 0, so they can't pull the average down.
- Finding: baseline RTT depends on send rate (median ~0.06 ms when sending as fast as possible vs ~0.44 ms with a 10 ms gap), so the send interval is now a fixed, recorded parameter.
- Observations: 97,137 packets over loopback with zero loss; latency spikes come in clusters (seqs 16–30) rather than at random; one 14.3 ms stall from the operating system.

### Day 3 — Sept 14: late replies
- Found and fixed a bug where a reply that arrived after the timeout was recorded as the *next* packet's reply, shifting every later measurement by one sequence number. The client now waits for the reply with its own sequence number until a per-packet deadline, and counts replies for older packets as "late". Verified by making the server hold one reply for 1.5 s: 1 lost, 1 late, and every packet after it correct.
- Added total runtime and actual send rate to the summary.
- Cleaned up the repo (`.gitignore`, removed invalid test CSVs).

### Day 4 — Sept 16: impairment models
- Learned the Gilbert-Elliott burst-loss model from Pieper & Voran (NTIA/ITS TM-23-565) and Haßlinger & Hohlfeld.
- Wrote `channel.py`: five profiles (clean, latency-ladder, jitter, bernoulli-loss, gilbert-elliott). Each one answers the same question for every packet — send it back, and after how long? — using its own seeded random generator. Gilbert-Elliott settings are computed from a target loss rate and average burst length (two-parameter model, k = 1, h = 0).
- Generator self-test, 1,000,000 packets each, matched the theory:
  - Bernoulli: loss 9.97%, average burst 1.110 (theory 1.111)
  - Gilbert-Elliott: loss 9.95%, average burst 4.971 (theory 5.0)
  - At the same ~10% loss, bursts of 5 lost packets in a row happened 6 times under Bernoulli and 1,704 times under Gilbert-Elliott.

### Day 5 — Sept 18: first network runs
- Added `config.py` so the client and server always read the same profile, settings and seed. The server now runs every packet through the channel, and CSV filenames record the profile, settings and seed.
- Timeout set to 0.1 s for loss profiles (1.0 s for delay profiles, which must be longer than the largest injected delay).
- First Gilbert-Elliott runs over loopback (1,000 packets, seed 1): the client's recorded losses matched the channel's injected drop pattern exactly, packet for packet, across 2,000 packets.
- Found that the server must be restarted before every run: without a restart, the second run continued the seed-1 sequence from packet 1,000 instead of starting over.
- Two 1,000-packet samples of the same 10% channel measured 18.3% and 10.3% loss, so the real runs will use 10,000 packets and 3 seeds per model.

### Next
- 10,000-packet runs: Bernoulli and Gilbert-Elliott (seeds 1–3), a clean baseline, the latency ladder and jitter
- A launcher script that restarts the server automatically for every run
- `summary.csv` and `analyze.py` to produce the burst-length figure

## citations and resoruces:
https://people.computing.clemson.edu/~jmarty/projects/lowLatencyNetworking/papers/APPFEC/GEModelForLossinTheRTInternet.pdf 
https://its.ntia.gov/umbraco/surface/download/publication?reportNumber=TM-23-565.pdf


## Results
<!-- what i actually delivered-->

---
Built during the NASA x Hack Club Stardance Challenge, 2026.
