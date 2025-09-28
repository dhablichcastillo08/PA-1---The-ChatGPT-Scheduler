import sys

class FIFOProcess:
    def __init__(self, name, arrival, burst):
        self.name = name
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst

        self.start_time = None
        self.finish_time = None

    def __repr__(self):
        return f"{self.name}(arr={self.arrival}, burst={self.burst}, rem={self.remaining})"
    ''' def __repr__(self):
        return f"{self.name}(AT={self.arrival}, BT={self.burst})" '''

def parse_input():
    """
    Parses input of the format:
        processcount 3
        runfor 20
        use fifo
        process name A arrival 0 burst 5
        process name B arrival 1 burst 4
        process name C arrival 4 burst 2
        end
    """

    process_count = 0
    runfor = 0
    algorithm = ""
    processes = []

    for line in sys.stdin:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        parts = line.split()

        if parts[0] == "processcount":
            process_count = int(parts[1])

        elif parts[0] == "runfor":
            runfor = int(parts[1])

        elif parts[0] == "use":
            algorithm = parts[1].lower()

        elif parts[0] == "process":
            # process name A arrival 0 burst 5
            name = parts[2]
            arrival = int(parts[4])
            burst = int(parts[6])
            processes.append(FIFOProcess(name, arrival, burst))

        elif parts[0] == "end":
            break

    return process_count, runfor, algorithm, processes


'''def fifo_scheduler(processes, runfor):
    # Sort by arrival order (FIFO)
    processes.sort(key=lambda p: p.arrival)

    time = 0
    timeline = []

    for p in processes:
        # If CPU is idle before the process arrives, advance time
        if time < p.arrival:
            time = p.arrival

        p.start_time = time
        time += p.runtime
        p.finish_time = time

        timeline.append((p.name, p.start_time, p.finish_time))

    return timeline '''

def fifo_scheduler(processes, runfor):
    # Sort by arrival time
    processes.sort(key=lambda p: p.arrival)

    time = 0
    timeline = []
    unfinished = []

    for p in processes:
        # If CPU is idle before process arrives
        if time < p.arrival:
            time = p.arrival

        # Process starts now
        if p.start_time is None:
            p.start_time = time

        # If the whole burst fits before runfor
        if time + p.burst <= runfor:
            time += p.burst
            p.finish_time = time
            timeline.append((p.name, p.start_time, p.finish_time))
        else:
            # Process is cut off
            executed_time = runfor - time
            if executed_time > 0:
                # It partially runs before time runs out
                p.remaining = p.burst - executed_time
                timeline.append((p.name, p.start_time, runfor))
            else:
                # It never got to run
                p.remaining = p.burst
            unfinished.append(p.name)
            break  # We stop scheduling because runtime is over

    # If there are processes that arrive after runfor
    for p in processes:
        if p.finish_time is None and p.name not in unfinished:
            unfinished.append(p.name)

    return timeline, unfinished



def calculate_metrics(processes):
    results = {}
    for p in processes:
        if p.finish_time is None:
            # Process did not finish, metrics are undefined
            continue

        turnaround = p.finish_time - p.arrival
        waiting = turnaround - p.burst
        response = p.start_time - p.arrival

        results[p.name] = {
            "Turnaround": turnaround,
            "Waiting": waiting,
            "Response": response,
        }
    return results

''' def calculate_metrics(processes):
    results = {}
    for p in processes:
        turnaround = p.finish_time - p.arrival
        waiting = turnaround - p.runtime
        response = p.start_time - p.arrival

        results[p.name] = {
            "Turnaround": turnaround,
            "Waiting": waiting,
            "Response": response,
        }
    return results '''


def run_fifo_scheduler_from_file(input_file):
    if not input_file.endswith(".in"):
        print("Error: Input file must have .in extension")
        return

    output_file = os.path.splitext(input_file)[0] + ".out"

    process_count, runfor, algorithm, processes = parse_input_file(input_file)
    if processes is None:
        return

    if algorithm != "fifo":
        print(f"Currently only FIFO is implemented (input used {algorithm})")
        return

    timeline, unfinished = fifo_scheduler(processes, runfor)
    metrics = calculate_metrics(processes)

    # Write results to output file
    with open(output_file, "w") as f:
        f.write("=== Timeline ===\n")
        for entry in timeline:
            f.write(f"{entry[0]}: {entry[1]} → {entry[2]}\n")

        f.write("\n=== Metrics ===\n")
        for name, vals in metrics.items():
            f.write(f"{name}: TAT={vals['Turnaround']}, WT={vals['Waiting']}, RT={vals['Response']}\n")

        if unfinished:
            f.write("\n=== Unfinished Processes ===\n")
            for name in unfinished:
                f.write(f"{name} did not finish\n")

    print(f"FIFO scheduling results written to {output_file}")
