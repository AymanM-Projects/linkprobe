"""channel.py:
what happens to a packet?

    """
import random

def gilbert_params(loss_rate, mean_burst):
    """ gilbert_elliot uses p and r 
    p = probability of loss after delivered
    r = probability of delivered after loss
    Average length of no loss = 1/p  
    average lenght of loss = 1/r """
    bernoulli_burst = 1/(1-loss_rate) # the average burst length of Bernoulli is 1/(1-L) where L is the loss rate, example: if loss rate is 0.1, average burst length is 1/0.9 ≈ 1.111
    if mean_burst <= bernoulli_burst:
        raise ValueError(f"mean_burst must be greater than {bernoulli_burst:.4f} for a loss rate of {loss_rate:.4f}") # ensure the mean burst of GE is bigger than bernoulli burst length. if not, the GE model would mimic Bernoulli too closely and have no memory.
    r = 1/mean_burst # the probability of delivered after loss, for example if mean burst is 5, r = 0.2
    cycle = mean_burst/loss_rate # cycle one bad streak and one good streak, for example if mean burst is 5 and loss rate is 0.1, cycle is 50 (5 bad + 45 good)
    sunny = cycle - mean_burst # the average length of the good streak
    p = 1/sunny # the probability of loss after delivered, for example if sunny is 45, p = 0.0222
    return p, r

 # uses classes to represent different channels and their behavior

class Clean: # represents a clean channel with no packet loss
    def decide(self, packet):
        return True, 0.0
    # always delivers the packet with zero delay
    # class clean doesn't need a __init__ method because it has no parameters to store
class FixedDelay:
    """one rung of latency ladder run it once per delay step"""
    def __init__(self,delay_ms): # init saves delay settings after the object is made so object remembers the delay for future packets(this is done for each experimental trial)
        self.delay = delay_ms /1000 # convert delay from milliseconds to seconds this is necessary because time.sleep expects seconds
     # same delay for all PACKETS
    def decide(self, packet): # called for each packet by server
            return True, self.delay 
    

class Jitter:
    def __init__(self,mean_ms,sd_ms,rng):
        self.mean = mean_ms/1000 # convert mean delay from milliseconds to seconds 
        self.sd = sd_ms/1000 # convert standard deviation from milliseconds to seconds
        self.rng =rng # the random number generator for the random numbers
    def decide(self,packet):
        delay = self.rng.gauss(self.mean, self.sd)  # gauss(mean, standard deviation) chooses a random delay from a normal distribution or bell curve 
        return True, max(delay,0.0) # ensure the delay is non-negative 
    #randomized delay that follows a bell curve (normal distribution)

class Bernoulli:
    def __init__(self,loss_rate,rng): 
        self.loss_rate = loss_rate 
        self.rng = rng 
        # equal loss rate to all packets
    def decide(self,packet):
        dropped = self.rng.random() < self.loss_rate  # self.rng.random() generates a random number between 0 and 1, if it's less than the loss rate, the packet is dropped. For example if self.rng.random() generates a number such as 0.5 and lost rate is 0.1 then packet is not loss, but if it generates a number such as 0.05, the packet is lost.
        return (not dropped), 0.0 # instead of true, return whether the packet was not dropped based on last line. Also no injected delay. 


class GilbertElliott:
    def __init__(self, p, r, rng): # p and r come from the gilber_params method 
        self.p = p
        self.r = r
        self.rng = rng 
        self.bad = rng.random() < p / (p + r) # determines the initial state of the run(loss or no loss) and stores in boolean value
        # for example  if rng.random() generates a number less than p / (p + r), the initial state is bad (loss), otherwise it's good (no loss)
    def decide(self, packet): # this time the decide function has memory in self.bad, which tracks the current state of the run (loss or no loss)
        """ this leads 4 possibliies in teh decide function:
                1. bad -> bad (loss continues) - handle by first if block in decide function
                2. bad -> good (loss ends) - handle by first if block in decide function
                3. good -> good (no loss continues) - handle by second if block in decide function
                4. good -> bad (loss starts) - handle by second if block in decide function
                """
        if self.bad:
            if self.rng.random() < self.r:
                self.bad = False  
        # if we are currently in bad and the random number is less than r, we transition to good (no loss)
        else:
            if self.rng.random() < self.p:
                self.bad = True
        # if we currently are in good and the random number is less than p, we transition to bad (loss)
        return (not self.bad), 0.0
        # uses not self.bad to return True if the packet is not lost (good state) and False if it is lost (bad state)


def make_channel(profile, seed, **params): # factory function to create the appropriate channel based on the profile
    """ The pattern that make_channel follows is calling a classname() and inside is **params or rng
    after python sees class name, it makes an object with the specific class parameters provided 
    passes what ever inside the () to the init method of the class
    """
    rng = random.Random(seed) # creates one random number generator instance for the channel. started from the seed
    if profile == "clean": # create a clean channel with no loss or delay
        return Clean(**params) # uses **params to pass additional keyword arguments to the each profile in this method(based on which profile is called)
    if profile == "latency-ladder": # create a channel with fixed delay
        return FixedDelay(**params)
    if profile == "jitter": # create a channel with jittered delay
        return Jitter(rng=rng, **params)
    if profile == "bernoulli-loss": # create a channel with Bernoulli loss
        return Bernoulli(rng=rng, **params)
    if profile == "gilbert-elliott": # create a channel with Gilbert-Elliott loss model 
        p, r = gilbert_params(**params) # here the **params are the loss rate and mean burst and then converts that into p and r
        return GilbertElliott(p, r, rng)
    raise ValueError(f"unknown profile: {profile}") # if there is case error or spelling issue, raise an exception with the unknown profile name

if __name__ == "__main__": # this block only runs if the script is executed directly, not when imported as a module
    from collections import Counter # counts how many times an element appears in a list

    def measure(channel, n): # sends a fake packet n times through the channel and measures loss and burst statistics (without actual data transmission)
        lost = 0 # total packets loss
        current_run = 0 # length of the current burst of lost packets
        runs = [] # list of all burst lengths
        for _ in range(n): # loops through all packets 
            forward, _ = channel.decide(b"") # b"" represents an empty packet, forward is True if the packet is not lost, False if it is lost._ is delay
            if forward: # this if checks if the packet was successfully forwarded (not lost) and if it wasnt lost and there is a current burst of lost packets, it records the burst length and resets the current run
                if current_run > 0:
                    runs.append(current_run)
                    current_run = 0
            else:
                lost += 1
                current_run += 1
            # if it is lost then it increments the lost count and the current run of lost packets
        if current_run > 0: # if there is a current burst of lost packets at the end, record it
            runs.append(current_run)
        return lost / n, sum(runs) / len(runs), Counter(runs) # returns the loss rate, mean burst length, and a Counter object of burst lengths

    N = 1_000_000 # just 1000000 packets
    tests = [ # list of test cases, each with a name and a channel instance(parameters)
        ("bernoulli", make_channel("bernoulli-loss", seed=1, loss_rate=0.10)),
        ("gilbert", make_channel("gilbert-elliott", seed=1, loss_rate=0.10, mean_burst=5)),
    ]
    for name, channel in tests: # this runs the two test cases using measure anf then prints the results
        rate, mean_burst, counts = measure(channel, N)
        print(f"{name}: loss {rate:.4f}, mean burst {mean_burst:.3f}, bursts of length 1-5: {[counts[k] for k in range(1, 6)]}") # counts k shows the amount of burst k lenght from 1-5