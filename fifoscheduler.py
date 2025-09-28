#ChatGPT used for implementation: https://chatgpt.com/share/68d8b0f2-e110-8000-b7dd-7b76757223c5
#To run this code, call run_fifo_scheduler_from_file with the filename as the argument

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

    def __repr__(self):
        return f"{self.name}(AT={self.arrival}, BT={self.burst})"


def parse_file(filename):
    """
    Parses input from a file in the format:
        processcount 3
        runfor 20
        use fifo
        process name A arrival 0 burst 5
        ...
        end
    """

    # --- Basic file checks ---
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(filename):
        print(f"Error: '{filename}' is not a file.", file=sys.stderr)
        sys.exit(1)

    process_count = 0
    runfor = 0
    algorithm = ""
    processes = []

    try:
        with open(filename, "r") as f:
            for line in f:
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
                    if len(parts) != 7:
                        print(f"Error: Invalid process line -> '{line}'", file=sys.stderr)
                        sys.exit(1)

                    name = parts[2]
                    arrival = int(parts[4])
                    burst = int(parts[6])
                    processes.append(Process(name, arrival, burst))

                elif parts[0] == "end":
                    break
    except Exception as e:
        print(f"Error while reading file '{filename}': {e}", file=sys.stderr)
        sys.exit(1)

    if process_count != len(processes):
        print(
            f"Warning: Declared processcount={process_count}, but parsed {len(processes)} processes.",
            file=sys.stderr,
        )

    return process_count, runfor, algorithm, processes


def fifo_scheduler(processes, runfor):
    processes.sort(key=lambda p: p.arrival)
    time = 0
    timeline = []
    unfinished = []

    for p in processes:
        if time < p.arrival:
            time = p.arrival

        if p.start_time is None:
            p.start_time = time

        if time + p.burst <= runfor:
            time += p.burst
            p.finish_time = time
            timeline.append((p.name, p.start_time, p.finish_time))
        else:
            executed_time = runfor - time
            if executed_time > 0:
                p.remaining = p.burst - executed_time
                timeline.append((p.name, p.start_time, runfor))
            else:
                p.remaining = p.burst
            unfinished.append(p.name)
            break

    for p in processes:
        if p.finish_time is None and p.name not in unfinished:
            unfinished.append(p.name)

    return timeline, unfinished


def calculate_metrics(processes):
    results = {}
    for p in processes:
        if p.finish_time is None:
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


def run_fifo_scheduler_from_file(filename):
    
    process_count, runfor, algorithm, processes = parse_file(filename)

    if algorithm != "fifo":
        print(f"Warning: Input requested '{algorithm}', running FIFO only.", file=sys.stderr)

    timeline, unfinished = fifo_scheduler(processes, runfor)
    metrics = calculate_metrics(processes)

    return timeline, metrics, unfinished
