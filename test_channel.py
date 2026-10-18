from channel import make_channel


def test_same_seed_same_drops():
    a = make_channel("gilbert-elliott", seed=7, loss_rate=0.1, mean_burst=5)
    b = make_channel("gilbert-elliott", seed=7, loss_rate=0.1, mean_burst=5)
    drops_a = []
    drops_b = []
    for _ in range(1000):
        forward_a, _ = a.decide(b"")
        forward_b, _ = b.decide(b"")
        drops_a.append(forward_a)
        drops_b.append(forward_b)
    assert drops_a == drops_b 


def test_bernoulli_loss_rate():
    ch = make_channel("bernoulli-loss", seed=1, loss_rate=0.1)
    n = 100_000
    lost = 0
    for _ in range(n):
        forward, _ = ch.decide(b"")
        if not forward:
            lost += 1
    rate = lost / n
    assert abs(rate - 0.1) < 0.005


def test_gilbert_mean_burst():
    ch = make_channel("gilbert-elliott", seed=1, loss_rate=0.1, mean_burst=5)
    bursts = []
    current = 0
    for _ in range(100_000):
        forward, _ = ch.decide(b"")
        if forward:
            if current > 0:
                bursts.append(current)
                current = 0
        else:
            current += 1
    if current > 0:
        bursts.append(current)
    mean_burst = sum(bursts) / len(bursts)
    assert abs(mean_burst - 5) < 0.5
