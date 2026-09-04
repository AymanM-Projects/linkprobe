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
#Day 1:
    created readme, github, hackatime, and stardance account. Did beginning research and understanding concepts of packet loss in networks.

## Results
<!-- what i actually delivered-->

---
Built during the NASA x Hack Club Stardance Challenge, 2026.