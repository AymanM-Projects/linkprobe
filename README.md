# linkprobe
 A codebase that will measure what a network does to messages between two machines: round-trip time, packet loss, and how long losses run in a row. Then degrades the link on purpose through five named profiles, one command each. Built for latency-sensitive robotics work, used as part of experimental methodology layer in robotics research . 


## Why

Often when networks transfer packets from machines, they lose packets and extra run time and add delay, or drop them in unnecessary bursts. Most current work assumes losses are independent. Through linkprobe, observations of what happens during packet loss and creating a formula to identify and combat that is the main goal. 

## What it measures

    - Round trip time per message(seconds of how long packets take from one machine to another)
    - packet sequence gaps(packet loss)
    - Run length(how many packets were lost back to back)

## The profiles
    table: profile | what it does|
    clean	no impairment — your baseline
    latency-ladder	fixed delay, stepped 0 → 250 ms in 50 ms increments
    jitter	delay that varies around a mean, e.g. 100 ms ± 30 ms
    bernoulli-loss	each packet independently dropped with probability p — the standard assumption
    gilbert-elliott	two-state model, good and bad; losses cluster into bursts — what real networks do


## Install

<!-- fill in once there's something to install -->

## Status

<!-- what works today, what's next. Update this as you go. -->

## Results
<!-- what i actually delivered-->

---
Built during the NASA x Hack Club Stardance Challenge, 2026.