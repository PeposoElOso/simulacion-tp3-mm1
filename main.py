import math, random
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter


class MM1Simulator:
    def __init__(self, arrival_rate, service_rate, max_events, queue_limit=None):
        self.lam = arrival_rate
        self.mu = service_rate
        self.Q = queue_limit  # None = cola infinita
        self.reset()

    def reset(self):
        self.time = 0.0
        self.server_busy = False
        self.queue = []
        self.total_delay = 0.0
        self.num_served = 0
        self.area_q = 0.0
        self.area_system = 0.0
        self.last_event_time = 0.0
        self.next_arrival = self.time + random.expovariate(self.lam)
        self.next_departure = float("inf")
        self.events_processed = 0

    def step(self):
        # avance al siguiente evento
        if self.next_arrival < self.next_departure:
            t_next = self.next_arrival
            event = "arrival"
        else:
            t_next = self.next_departure
            event = "departure"
        # actualizar estadísticas de área
        dt = t_next - self.last_event_time
        self.area_q += len(self.queue) * dt
        self.area_system += (len(self.queue) + (1 if self.server_busy else 0)) * dt
        self.last_event_time = t_next
        self.time = t_next

        # ejecutar evento
        if event == "arrival":
            # programar próxima llegada
            self.next_arrival = self.time + random.expovariate(self.lam)
            # si servidor libre, atiende
            if not self.server_busy:
                self.server_busy = True
                self.next_departure = self.time + random.expovariate(self.mu)
            else:
                if self.Q is not None and len(self.queue) >= self.Q:
                    # denegación
                    self.denials += 1
                else:
                    self.queue.append(self.time)
        else:
            # salida
            if self.queue:
                arrival_time = self.queue.pop(0)
                delay = self.time - arrival_time
                self.total_delay += delay
                self.num_served += 1
                self.next_departure = self.time + random.expovariate(self.mu)
            else:
                self.server_busy = False
                self.next_departure = float("inf")
        self.events_processed += 1

    def run(self, max_events):
        self.reset()
        self.denials = 0
        while self.events_processed < max_events:
            self.step()

    def metrics(self):
        Lq = self.area_q / self.time
        L = self.area_system / self.time
        Wq = self.total_delay / self.num_served if self.num_served else float("nan")
        W = Wq + 1 / self.mu
        p0 = max(0.0, 1 - (self.lam / self.mu))
        # distribución empírica del nº en cola
        # no trackeamos en cada instante, pero se podría muestrear
        return {
            "Lq": Lq,
            "L": L,
            "Wq": Wq,
            "W": W,
            "util": self.area_system / self.time - Lq,  # (tiempo-servicio)/tiempo total
            "den_prob": self.denials / (self.denials + self.num_served)
            if self.Q is not None
            else 0.0,
        }


# Parámetros del experimento
service_rate = 1.0  # μ = 1 servicio/unidad tiempo
arrival_ratios = [0.25, 0.5, 0.75, 1.0, 1.25]
queue_limits = [None, 0, 2, 5, 10, 50]  # None=infinita

results = []
for rho in arrival_ratios:
    lam = rho * service_rate
    for Q in queue_limits:
        vals = {"Lq": [], "L": [], "Wq": [], "W": [], "util": [], "den_prob": []}
        for run in range(10):
            sim = MM1Simulator(lam, service_rate, max_events=100000, queue_limit=Q)
            sim.run(max_events=100000)
            m = sim.metrics()
            for k in vals:
                vals[k].append(m[k])
        results.append({"rho": rho, "Q": Q, "avg": {k: np.mean(vals[k]) for k in vals}})

# 🎨 Visualización
import pandas as pd

df = pd.DataFrame(results)

fig, axes = plt.subplots(3, 2, figsize=(14, 12))
metrics = ["L", "Lq", "W", "Wq", "util", "den_prob"]
titles = [
    "Prom. clientes en sistema",
    "Prom. en cola",
    "Tiempo en sistema",
    "Tiempo en cola",
    "Utilización",
    "Prob. denegación",
]

for ax, metric, title in zip(axes.flatten(), metrics, titles):
    for Q in queue_limits:
        sub = df[df.Q == Q]
        ratios = sub.rho
        ax.plot(
            ratios, [v["avg"][metric] for v in sub.to_dict("records")], label=f"Q={Q}"
        )
    ax.set_title(title)
    ax.set_xlabel("ρ = λ/μ")
    ax.legend()
plt.tight_layout()
plt.show()
