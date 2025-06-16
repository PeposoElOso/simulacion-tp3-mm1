import math
import random
import sys

# Constantes
Q_LIMIT = 100
BUSY = 1
IDLE = 0

# Variables globales
next_event_type = 0
num_custs_delayed = 0
num_delays_required = 0
num_events = 2
num_in_q = 0
server_status = IDLE
area_num_in_q = 0.0
area_server_status = 0.0
mean_interarrival = 0.0
mean_service = 0.0
sim_time = 0.0
time_arrival = [0.0] * (Q_LIMIT + 1)
time_last_event = 0.0
time_next_event = [0.0, 0.0, 0.0]
total_of_delays = 0.0


def expon(mean):
    """Genera una variable exponencial con media 'mean'."""
    u = random.random()
    return -mean * math.log(u)


def initialize():
    global sim_time, server_status, num_in_q, time_last_event
    global num_custs_delayed, total_of_delays, area_num_in_q, area_server_status
    global time_next_event

    sim_time = 0.0
    server_status = IDLE
    num_in_q = 0
    time_last_event = 0.0
    num_custs_delayed = 0
    total_of_delays = 0.0
    area_num_in_q = 0.0
    area_server_status = 0.0

    time_next_event[1] = sim_time + expon(mean_interarrival)
    time_next_event[2] = float("inf")


def timing(outfile):
    global next_event_type, sim_time
    min_time = float("inf")
    next_event = 0

    for i in range(1, num_events + 1):
        if time_next_event[i] < min_time:
            min_time = time_next_event[i]
            next_event = i

    if next_event == 0:
        print(f"\nEvent list empty at time {sim_time}", file=outfile)
        sys.exit(1)

    sim_time = min_time
    next_event_type = next_event


def arrive(outfile):
    global server_status, num_in_q
    global time_next_event, sim_time, total_of_delays, num_custs_delayed

    time_next_event[1] = sim_time + expon(mean_interarrival)

    if server_status == BUSY:
        num_in_q += 1
        if num_in_q > Q_LIMIT:
            print(f"\nOverflow of time_arrival at time {sim_time}", file=outfile)
            sys.exit(2)
        time_arrival[num_in_q] = sim_time
    else:
        delay = 0.0
        total_of_delays += delay
        num_custs_delayed += 1
        server_status = BUSY
        time_next_event[2] = sim_time + expon(mean_service)


def depart():
    global server_status, num_in_q, time_next_event
    global sim_time, total_of_delays, num_custs_delayed

    if num_in_q == 0:
        server_status = IDLE
        time_next_event[2] = float("inf")
    else:
        num_in_q -= 1
        delay = sim_time - time_arrival[1]
        total_of_delays += delay
        num_custs_delayed += 1
        time_next_event[2] = sim_time + expon(mean_service)
        for i in range(1, num_in_q + 1):
            time_arrival[i] = time_arrival[i + 1]


def update_time_avg_stats():
    global area_num_in_q, area_server_status, time_last_event
    global sim_time, num_in_q, server_status

    time_since = sim_time - time_last_event
    time_last_event = sim_time

    area_num_in_q += num_in_q * time_since
    area_server_status += server_status * time_since


def report(outfile):
    avg_delay = total_of_delays / num_custs_delayed
    avg_num_in_q = area_num_in_q / sim_time
    server_util = area_server_status / sim_time

    print("Single-server queuing system\n", file=outfile)
    print(f"Mean interarrival time: {mean_interarrival:.3f} minutes", file=outfile)
    print(f"Mean service time: {mean_service:.3f} minutes", file=outfile)
    print(f"Number of customers: {num_delays_required}", file=outfile)
    print(f"\nAverage delay in queue: {avg_delay:.3f} minutes", file=outfile)
    print(f"Average number in queue: {avg_num_in_q:.3f}", file=outfile)
    print(f"Server utilization: {server_util:.3f}", file=outfile)
    print(f"Time simulation ended: {sim_time:.3f} minutes", file=outfile)


def main():
    global mean_interarrival, mean_service, num_delays_required

    mean_interarrival = float(input("Media inter-arrival (minutos): "))
    mean_service = float(input("Media service (minutos): "))
    num_delays_required = int(input("Cantidad de clientes a simular: "))

    # Solo archivo de salida
    with open("mm1.out", "w") as outfile:
        initialize()
        while num_custs_delayed < num_delays_required:
            timing(outfile)
            update_time_avg_stats()
            if next_event_type == 1:
                arrive(outfile)
            elif next_event_type == 2:
                depart()
        report(outfile)


if __name__ == "__main__":
    main()
