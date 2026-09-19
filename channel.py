"""channel.py:
what happens to a packet?

    """
import random

def gilbert_params(loss_rate, mean_burst):
    """ gilbert_elliot uses p and r 
    p = probaility of loss after delivered
    r = probaility of delivered after loss
    Average length of no loss = 1/p  
    average lenght of loss = 1/r """
    bernoulli_burst = 1/(1-loss_rate) # the average burst length is 1/(1-L) where L is the loss rate
    if mean_burst <= bernoulli_burst:
        raise ValueError(f"mean_burst must be greater than {bernoulli_burst:.4f} for a loss rate of {loss_rate:.4f}")
    r = 1/mean_burst # the probability of delivered after loss
    cycle = mean_burst/loss_rate 
    sunny = cycle - mean_burst
    p = 1/sunny 
    return p, r

class Clean:
    def decide(self, packet):
        return True, 0.0
         # no attempted packet loss
class FixedDelay:
    """one rung of latency ladder run it once per dealy step"""
    def __init__(self,delay_ms):
        self.delay = delay_ms /1000
    def decide(self, packet):
            return True, self.delay
    # we inflict a standard delay 

class Jitter:
    def __init__(self,mean_ms,sd_ms,rng):
        self.mean = mean_ms/1000
        self.sd = sd_ms/1000
        self.rng =rng

    def decide(self,packet):
        delay = self.rng.gauss(self.mean, self.sd)
        return True, max(delay,0.0)
    #randomized delay

class Bernoulli:
    def __init__(self,loss_rate,rng):
        self.loss_rate = loss_rate 
        self.rng = rng 
        # equal loss rate to all packets
    def decide(self,packet):
        dropped = self.rng.random() < self.loss_rate 
        return (not dropped), 0.0


class GilbertElliott:
    def __init__(self, p, r, rng):
        self.p = p
        self.r = r
        self.rng = rng
        self.bad = rng.random() < p / (p + r) # to see when pacekt loss burst starts and if a run starts with a lost packet

    def decide(self, packet):
        if self.bad: # decides for individual packets 
            if self.rng.random() < self.r:
                self.bad = False 
        else:
            if self.rng.random() < self.p:
                self.bad = True
        return (not self.bad), 0.0

def make_channel(profile, seed, **params):
    rng = random.Random(seed)
    if profile == "clean":
        return Clean(**params)
    if profile == "latency-ladder":
        return FixedDelay(**params)
    if profile == "jitter":
        return Jitter(rng=rng, **params)
    if profile == "bernoulli-loss":
        return Bernoulli(rng=rng, **params)
    if profile == "gilbert-elliott":
        p, r = gilbert_params(**params)
        return GilbertElliott(p, r, rng)
    raise ValueError(f"unknown profile: {profile}")

if __name__ == "__main__":
    from collections import Counter

    def measure(channel, n):
        lost = 0
        current_run = 0
        runs = []
        for _ in range(n):
            forward, _ = channel.decide(b"")
            if forward:
                if current_run > 0:
                    runs.append(current_run)
                    current_run = 0
            else:
                lost += 1
                current_run += 1
        if current_run > 0:
            runs.append(current_run)
        return lost / n, sum(runs) / len(runs), Counter(runs)

    N = 1_000_000
    tests = [
        ("bernoulli", make_channel("bernoulli-loss", seed=1, loss_rate=0.10)),
        ("gilbert", make_channel("gilbert-elliott", seed=1, loss_rate=0.10, mean_burst=5)),
    ]
    for name, channel in tests:
        rate, mean_burst, counts = measure(channel, N)
        print(f"{name}: loss {rate:.4f}, mean burst {mean_burst:.3f}, bursts of length 1-5: {[counts[k] for k in range(1, 6)]}")