# linkprobe results 

## 1. Headline result

| profile         | loss % (seed 1 / 2 / 3) | mean burst (seed 1 / 2 / 3) | max burst (seed 1 / 2 / 3) |
|-----------------|-------------------------|-----------------------------|----------------------------|
| bernoulli-loss  | 10.41 / 10.09 / 9.79    | 1.136 / 1.099 / 1.113       | 5 / 3 / 3                  |
| gilbert-elliott | 10.30 / 10.18 / 9.93    | 4.791 / 4.966 / 4.916       | 28 / 29 / 22               |

Both profiles lose about 10% of packets. Gilbert-Elliott's mean burst is 4.4 times Bernoulli's. This holds across all three seeds. The longest Gilbert-Elliott burst was 29 packets and the longest Bernoulli burst was 5.
Burst length matters so much in a control loop, even though both profiles have about the same loss percentage, because the network is down for longer periods of time.

![Burst length CCDF](figures/burst_ccdf.png)


## 2. Noise floor: the clean baseline

The clean run sent 10,000 packets and recorded 3 as lost. All 3 were replies that arrived after the 0.1 s timeout, for sequence numbers 4465, 4469, and 4546. The number of packets truly dropped was 0.
With nothing additionally injected, the program drops zero packets, so in the trial runs essentially every lost packet is one the injector dropped on purpose, and the instrument's own error is about 3 in 10,000.

## 3. The clean p99

The clean run's median round-trip time was 0.394 ms and its p99 was 7.366 ms, at 0.03% loss. The 0 ms latency-ladder run, which uses the same loopback path, had a p99 of 1.809 ms.
The 7.366 ms p99 does not come from the link, because loopback has no physical link. The most likely cause is the operating system briefly pausing the client and server processes. For about 10 seconds of the run 
(54 s to 64 s, sequence numbers 4243 to 4547), replies were repeatedly slow. All three timed-out packets from section 2 fall inside that window, and so do 14 of the 16 replies that took longer than 50 ms.


## 4. Injector validation

Gilbert-Elliott was configured for a mean burst of 5 packets. Measured end to end over the network, the three seeds gave 4.791, 4.966, and 4.916.
This shows the configuration for the Gilbert-Elliott pipeline accurately emulates our configured mean burst in the data.

## 5. Deadline_MS

The deadline of 50 ms in `analyze.py` is an arbitrary deadline amount.
This deadline is used by `analyze.py` to calculate `deadline_miss_pct` and `over_deadline`. A later deadline-sweep figure will use many different deadlines instead of just this one.

## 6. Replay check

In `verify_replay.py`, I used each run's seed to rebuild its channel and compared the channel's decisions, packet by packet, to the `lost` column in each run's CSV. Across all 6 runs (3 Bernoulli, 3 GE) and 60,000 packets sent, 59,999 matched. The one difference was a late packet (GE seed 2, seq 8409), not a drop caused by the injector. The channel delivered it, but the reply arrived after the 0.1 s timeout, so the client marked it as lost (`results/client.log` line 48445).

To reproduce: `python3 verify_replay.py`

## 7. Limitations

- The p99 only counts the round-trip time (RTT) of packets that were delivered. Lost packets have no RTT, so a run with many lost packets could still show a good p99. It is important to read this value alongside the loss %.
- The latency ladder and the jitter run each used only one seed, so there are no repeated trials for them.
- The client-server loop only has impairment on one leg rather than both. Impairment can only happen on the server side, after it receives the packet from the client and before it replies. This means the client-to-server leg is always clean. In real applications, packets can be lost in both directions, so the round-trip loss could be higher. 