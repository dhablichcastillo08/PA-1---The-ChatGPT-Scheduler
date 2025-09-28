#ChatGPT used for implementation: https://chatgpt.com/share/68d8b0f2-e110-8000-b7dd-7b76757223c5
#To run this code, call run_fifo_scheduler_from_file with the filename as the argument

import sys
import os


class FIFOProcess:
    def __init__(self, name, arrival, burst):
        self.name = name
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.start_time = None
        self.finish_time = None


def parse_file(filename):
    # --- Error checking ---
    if not os.path.exists(filename):
        print(f"Error: file '{filename}' not found.", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(filename):
        print(f"Error: '{filename}' is not a valid file.", file=sys.stderr)
        sys.exit(1)

    process_count = 0
    runfor = 0
    algorithm = ""
    processes = []

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
                # Example: process name A arrival 0 burst 5
                name = parts[2]
                arrival = int(parts[4])
                burst = int(parts[6])
                processes.append(FIFOProcess(name, arrival, burst))
            elif parts[0] == "end":
                break

    return process_count, runfor, algorithm, processes


def fifo_scheduler(processes, runfor):
    processes.sort(key=lambda p: p.arrival)

    time = 0
    log_lines = []
    finished_processes = set()
    ready_queue = []

    while time < runfor:
        # Check for arrivals
        for p in processes:
            if p.arrival == time:
                log_lines.append(f"time {time} : {p.name} arrived")
                ready_queue.append(p)

        if ready_queue:
            current = ready_queue[0]
            if current.start_time is None:
                current.start_time = time
                log_lines.append(f"time {time} : {current.name} selected (burst {current.remaining})")

            current.remaining -= 1

            if current.remaining == 0:
                current.finish_time = time + 1
                log_lines.append(f"time {time+1} : {current.name} finished")
                finished_processes.add(current.name)
                ready_queue.pop(0)
        else:
            log_lines.append(f"time {time} : Idle")

        time += 1

    log_lines.append(f"time {runfor} : Simulator ended")

    unfinished = [p.name for p in processes if p.name not in finished_processes]
    return log_lines, processes, unfinished


def calculate_metrics(processes):
    metrics = {}
    for p in processes:
        if p.finish_time is None:
            continue
        turnaround = p.finish_time - p.arrival
        waiting = turnaround - p.burst
        response = p.start_time - p.arrival
        metrics[p.name] = {
            "Turnaround": turnaround,
            "Waiting": waiting,
            "Response": response,
        }
    return metrics


def run_fifo_scheduler_from_file(input_filename):
    # --- Parse input file ---
    process_count, runfor, algorithm, processes = parse_file(input_filename)

    if algorithm != "fcfs":
        print(f"Warning: input requested '{algorithm}', running FIFO instead.", file=sys.stderr)

    log_lines, processes, unfinished = fifo_scheduler(processes, runfor)
    metrics = calculate_metrics(processes)

    # --- Write output file ---
    output_filename = os.path.splitext(input_filename)[0] + ".out"
    try:
        with open(output_filename, "w") as f:
            f.write(f"{process_count} processes\n")
            f.write("Using First-Come First-Served\n\n")

            for line in log_lines:
                f.write(line + "\n")

            f.write("\n")
            for p in processes:
                if p.finish_time is not None:
                    f.write(
                        f"{p.name} wait {metrics[p.name]['Waiting']} "
                        f"turnaround {metrics[p.name]['Turnaround']} "
                        f"response {metrics[p.name]['Response']}\n"
                    )

            for name in unfinished:
                f.write(f"{name} did not finish\n")

    except Exception as e:
        print(f"Error: could not write to output file '{output_filename}': {e}", file=sys.stderr)
        sys.exit(1)
