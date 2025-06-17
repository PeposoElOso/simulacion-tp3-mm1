import argparse
import random
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter


class MM1Simulator:
    def __init__(self, lam, mu, max_events, queue_limit=None):
        self.lam, self.mu = lam, mu
        self.max_events = max_events
        self.queue_limit = queue_limit

    def reset(self):
        self.time = self.area_q = self.area_system = 0.0
        self.last_event_time = 0.0
        self.server_busy = False
        self.queue = []
        self.total_delay = 0.0
        self.num_served = 0
        self.denials = 0
        self.events = 0
        self.next_arrival = random.expovariate(self.lam)
        self.next_departure = float("inf")
        self.sample_queue = []

    def step(self):
        t, event = (
            (self.next_arrival, "arrival")
            if self.next_arrival < self.next_departure
            else (self.next_departure, "departure")
        )
        dt = t - self.last_event_time
        self.area_q += len(self.queue) * dt
        self.area_system += (len(self.queue) + (1 if self.server_busy else 0)) * dt
        self.time, self.last_event_time = t, t
        system_size = len(self.queue) + (1 if self.server_busy else 0)
        self.sample_queue.append(system_size)
        if event == "arrival":
            self.next_arrival = self.time + random.expovariate(self.lam)
            if not self.server_busy:
                self.server_busy = True
                self.next_departure = self.time + random.expovariate(self.mu)
            elif self.queue_limit is not None and len(self.queue) >= self.queue_limit:
                self.denials += 1
            else:
                self.queue.append(self.time)
        else:
            if self.queue:
                arr = self.queue.pop(0)
                self.total_delay += self.time - arr
                self.num_served += 1
                self.next_departure = self.time + random.expovariate(self.mu)
            else:
                self.server_busy = False
                self.next_departure = float("inf")
        self.events += 1

    def run(self):
        self.reset()
        while self.events < self.max_events:
            self.step()

    def metrics(self):
        Lq = self.area_q / self.time
        L = self.area_system / self.time
        Wq = self.total_delay / self.num_served if self.num_served else float("nan")
        W = Wq + 1 / self.mu
        util = self.area_system / self.time - Lq
        denial_p = (
            self.denials / (self.denials + self.num_served)
            if self.queue_limit is not None
            else 0.0
        )
        counts = Counter(self.sample_queue)
        total = len(self.sample_queue)
        Pn = {n: counts[n] / total for n in sorted(counts)}
        return {
            "Lq": Lq,
            "L": L,
            "Wq": Wq,
            "W": W,
            "util": util,
            "denial_p": denial_p,
            "Pn": Pn,
        }


def main():
    parser = argparse.ArgumentParser(
        description="Simulación M/M/1: métricas y gráficos"
    )
    parser.add_argument("--service_rate", type=float, default=1.0, help="Tasa μ")
    parser.add_argument(
        "--max_events", type=int, default=100000, help="Eventos por corrida"
    )
    parser.add_argument(
        "--runs", type=int, default=10, help="Número de corridas por experimento"
    )
    args = parser.parse_args()

    arrival_ratios = [0.25, 0.5, 0.75, 1.0, 1.25]
    queue_limits = [0, 2, 5, 10, 50]
    results = []

    for rho in arrival_ratios: 
        lam = rho * args.service_rate
        print(f"\n=== ρ = {rho:.2f} (λ = {lam:.2f}) ===")
        for Q in queue_limits:
            agg = {k: [] for k in ["Lq", "L", "Wq", "W", "util", "denial_p"]}
            aggPn = Counter()
            for _ in range(args.runs):
                sim = MM1Simulator(
                    lam, args.service_rate, args.max_events, queue_limit=Q
                )
                sim.run()
                m = sim.metrics()
                for k in agg:
                    agg[k].append(m[k])
                aggPn.update(m["Pn"])
            avg = {k: np.mean(agg[k]) for k in agg}
            total = sum(aggPn.values())
            Pn_avg = {n: aggPn[n] / total for n in sorted(aggPn)}
            print(
                f"\nQ={Q}: L={avg['L']:.3f}, Lq={avg['Lq']:.3f}, W={avg['W']:.3f}, Wq={avg['Wq']:.3f}, util={avg['util']:.3f}, den_p={avg['denial_p']:.3f}"
            )
            print(
                " P(n) n=0..10:",
                ", ".join(f"{n}:{Pn_avg.get(n, 0):.3f}" for n in range(11)),
            )
            results.append({"rho": rho, "Q": Q, "avg": avg})

    # Gráficos
    import pandas as pd

    df = pd.DataFrame(results)
    metrics = ["L", "Lq", "W", "Wq", "util", "denial_p"]
    titles = [
        "Clientes en sistema",
        "Clientes en cola",
        "Tiempo sistema",
        "Tiempo cola",
        "Utilización",
        "Prob. denegación",
    ]
    fig, axes = plt.subplots(3, 2, figsize=(14, 12))

    for ax, metric, title in zip(axes.flatten(), metrics, titles):
        for Q in queue_limits:
            sub = df[df.Q == Q]
            ax.plot(
                sub.rho,
                [v["avg"][metric] for v in sub.to_dict("records")],
                label=f"Q={Q}",
            )
        ax.set_title(title)
        ax.set_xlabel("ρ")
        ax.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
