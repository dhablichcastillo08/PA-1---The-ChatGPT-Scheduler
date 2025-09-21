# Made with ChatGPT. Link: https://chatgpt.com/share/68d0388a-b734-8008-963f-05ad45dbc656
# To run this code, call run_sjf_scheduler_from_file() with the filename as the argument

import sys
import os

class Process:
    def __init__(self, name, arrival, burst):
        self.name = name
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.start_time = None
        self.finish_time = None
        self.response_time = None

    def __repr__(self):
        return f"{self.name}(arrival={self.arrival}, burst={self.burst})"


def parse_input(input_lines):
    processes = []
    runfor = None
    algo = None
    processcount = None

    for line in input_lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        tokens = line.split()
        if tokens[0] == "processcount":
            if len(tokens) < 2:
                print("Error: Missing parameter processcount")
                sys.exit(1)
            processcount = int(tokens[1])

        elif tokens[0] == "runfor":
            if len(tokens) < 2:
                print("Error: Missing parameter runfor")
                sys.exit(1)
            runfor = int(tokens[1])

        elif tokens[0] == "use":
            if len(tokens) < 2:
                print("Error: Missing parameter use")
                sys.exit(1)
            algo = tokens[1].lower()
            if algo not in {"sjf"}:
                print(f"Error: Unsupported algorithm '{algo}'. Only 'sjf' is implemented.")
                sys.exit(1)

        elif tokens[0] == "process":
            if "name" not in tokens:
                print("Error: Missing parameter name")
                sys.exit(1)
            if "arrival" not in tokens:
                print("Error: Missing parameter arrival")
                sys.exit(1)
            if "burst" not in tokens:
                print("Error: Missing parameter burst")
                sys.exit(1)

            # name
            name_index = tokens.index("name") + 1
            if name_index >= len(tokens) or tokens[name_index] in {"arrival", "burst", "name"}:
                print("Error: Missing parameter name")
                sys.exit(1)
            name = tokens[name_index]

            # arrival
            arrival_index = tokens.index("arrival") + 1
            if arrival_index >= len(tokens) or tokens[arrival_index] in {"arrival", "burst", "name"}:
                print("Error: Missing parameter arrival")
                sys.exit(1)
            try:
                arrival = int(tokens[arrival_index])
            except ValueError:
                print("Error: Invalid arrival value")
                sys.exit(1)

            # burst
            burst_index = tokens.index("burst") + 1
            if burst_index >= len(tokens) or tokens[burst_index] in {"arrival", "burst", "name"}:
                print("Error: Missing parameter burst")
                sys.exit(1)
            try:
                burst = int(tokens[burst_index])
            except ValueError:
                print("Error: Invalid burst value")
                sys.exit(1)

            processes.append(Process(name, arrival, burst))

        elif tokens[0] == "end":
            break

    if processcount is None:
        print("Error: Missing parameter processcount")
        sys.exit(1)
    if runfor is None:
        print("Error: Missing parameter runfor")
        sys.exit(1)
    if algo is None:
        print("Error: Missing parameter use")
        sys.exit(1)

    if processcount != len(processes):
        print("Error: processcount does not match number of processes defined")
        sys.exit(1)

    return processes, runfor, algo


def sjf_preemptive_scheduler(processes, runtime, output_file):
    time = 0
    ready_queue = []
    current_process = None

    log = []
    finished = []

    while time < runtime:
        # (1) Arrivals
        for p in processes:
            if p.arrival == time:
                log.append(f"Time {time:3} : {p.name} arrived")
                ready_queue.append(p)

        # (2) Finishes
        finishes_this_tick = [p for p in processes if p.finish_time == time]
        for p in finishes_this_tick:
            log.append(f"Time {time:3} : {p.name} finished")
            if p in ready_queue:
                ready_queue.remove(p)
            if current_process == p:
                current_process = None
            if p not in finished:
                finished.append(p)

        # (3) Choose process
        if ready_queue:
            candidate = min(ready_queue, key=lambda x: (x.remaining, x.arrival))
            if candidate != current_process:
                current_process = candidate
                if current_process.start_time is None:
                    current_process.start_time = time
                    current_process.response_time = time - current_process.arrival
                log.append(f"Time {time:3} : {current_process.name} selected (burst {current_process.remaining:3})")
        else:
            if current_process is None:
                log.append(f"Time {time:3} : Idle")

        # (4) Run one tick
        if current_process:
            current_process.remaining -= 1
            if current_process.remaining == 0:
                current_process.finish_time = time + 1

        time += 1

    log.append(f"Finished at time {runtime:3}")
    log.append("")

    for p in processes:
        if p.finish_time is None:
            log.append(f"{p.name} did not finish")
        else:
            turnaround = p.finish_time - p.arrival
            waiting = turnaround - p.burst
            response = p.response_time if p.response_time is not None else 0
            log.append(f"{p.name} wait {waiting:3} turnaround {turnaround:3} response {response:3}")

    with open(output_file, "w") as f:
        f.write(f"{len(processes)} processes\n")
        f.write("Using preemptive Shortest Job First\n")
        for line in log:
            f.write(line + "\n")


def run_sjf_scheduler_from_file(input_file):
    if not input_file.endswith(".in"):
        print("Error: Input file must have .in extension")
        sys.exit(1)

    output_file = os.path.splitext(input_file)[0] + ".out"

    with open(input_file, "r") as f:
        input_data = f.readlines()

    processes, runfor, algo = parse_input(input_data)

    if algo == "sjf":
        sjf_preemptive_scheduler(processes, runfor, output_file)
