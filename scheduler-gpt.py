"""
Group Members:
Luke Dederich
David Castillo
Ilarya Franco
Samantha Quan
"""

import sys
import os
from collections import deque

# Google Gemini used for creation. Link: https://g.co/gemini/share/b862a9784cd1

class RoundRobinProcess:
    """Represents a process with its attributes specific to Round Robin."""
    def __init__(self, name, arrival, burst):
        self.name = name
        self.arrival_time = arrival
        self.burst_time = burst
        self.remaining_time = burst
        self.start_time = -1
        self.finish_time = -1
        self.wait_time = 0
        self.turnaround_time = 0
        self.response_time = -1

class RoundRobinScheduler:
    """
    Manages the simulation of a process scheduling algorithm.
    It reads process data from a file, validates parameters,
    simulates the process execution, and generates a formatted output file.
    """
    def __init__(self, filename):
        self.filename = filename
        self.processes = []
        self.process_count = -1
        self.run_for = -1
        self.algorithm = None
        self.quantum = -1
        self.log = []
        
        # Parse the input file to populate scheduler attributes
        self._parse_file()
        
    def _parse_file(self):
        """
        Parses the input file to extract simulation parameters and process data.
        Performs basic checks for required parameters.
        """
        try:
            with open(self.filename, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: File not found at '{self.filename}'")
            sys.exit(1)

        for line in lines:
            parts = line.strip().split()
            if not parts:
                continue

            directive = parts[0]
            if directive == 'processcount':
                self.process_count = int(parts[1])
            elif directive == 'runfor':
                self.run_for = int(parts[1])
            elif directive == 'use':
                self.algorithm = parts[1]
            elif directive == 'quantum':
                self.quantum = int(parts[1])
            elif directive == 'process':
                name = parts[2]
                arrival = int(parts[4])
                burst = int(parts[6])
                self.processes.append(RoundRobinProcess(name, arrival, burst))
            elif directive == 'end':
                break

        self.processes.sort(key=lambda p: p.arrival_time)

    def _validate(self):
        """
        Validates the parsed parameters, including the specific check for
        'rr' algorithm requiring a quantum.
        """
        if self.process_count == -1:
            print("Error: Missing parameter processcount")
            sys.exit(1)
        if self.run_for == -1:
            print("Error: Missing parameter runfor")
            sys.exit(1)
        if self.algorithm is None:
            print("Error: Missing parameter use")
            sys.exit(1)
        if self.algorithm == 'rr' and self.quantum == -1:
            print("Error: Missing quantum parameter when use is 'rr'")
            sys.exit(1)
        if len(self.processes) != self.process_count:
            print("Error: Process count mismatch in file")
            sys.exit(1)
            
    def _run_round_robin(self):
        """
        Simulates the Round Robin (RR) scheduling algorithm.
        This method handles process arrivals, preemption, and execution.
        """
        ready_queue = deque()
        finished_processes = []
        current_process = None
        quantum_counter = 0
        
        process_idx = 0
        raw_logs = []
        
        for time in range(self.run_for):
            # Check for a process finishing at the beginning of this time tick
            if current_process and current_process.remaining_time == 0:
                current_process.finish_time = time
                current_process.turnaround_time = current_process.finish_time - current_process.arrival_time
                current_process.wait_time = current_process.turnaround_time - current_process.burst_time
                raw_logs.append((2, time, f"Time {time:3d} : {current_process.name} finished"))
                finished_processes.append(current_process)
                current_process = None
                quantum_counter = 0

            # Check for new arrivals at the current time tick
            while process_idx < len(self.processes) and self.processes[process_idx].arrival_time == time:
                p = self.processes[process_idx]
                raw_logs.append((1, time, f"Time {time:3d} : {p.name} arrived"))
                ready_queue.append(p)
                process_idx += 1
            
            # Preemption logic for the current process
            if current_process and quantum_counter == self.quantum:
                ready_queue.append(current_process)
                current_process = None
                quantum_counter = 0
            
            # Select a new process if the CPU is idle
            if current_process is None and ready_queue:
                current_process = ready_queue.popleft()
                if current_process.start_time == -1:
                    current_process.start_time = time
                    current_process.response_time = time - current_process.arrival_time
                raw_logs.append((3, time, f"Time {time:3d} : {current_process.name} selected (burst {current_process.remaining_time:3d})"))
            
            # Execute or log Idle
            if current_process:
                current_process.remaining_time -= 1
                quantum_counter += 1
            else:
                raw_logs.append((4, time, f"Time {time:3d} : Idle"))

        # Handle any remaining processes after the main simulation loop
        # This is for the case where a process finishes exactly at run_for.
        if current_process and current_process.remaining_time == 0:
            current_process.finish_time = self.run_for
            current_process.turnaround_time = current_process.finish_time - current_process.arrival_time
            current_process.wait_time = current_process.turnaround_time - current_process.burst_time
            raw_logs.append((2, self.run_for, f"Time {self.run_for:3d} : {current_process.name} finished"))
            finished_processes.append(current_process)
        
        # Unfinished processes: any process not in the finished list
        remaining_processes = [p for p in self.processes if p.remaining_time > 0]
        
        return finished_processes, remaining_processes, raw_logs

    def run(self):
        """
        Executes the entire simulation workflow.
        """
        self._validate()
        
        finished, remaining, raw_logs = [], [], []
        if self.algorithm == 'rr':
            finished, remaining, raw_logs = self._run_round_robin()
        else:
            # Placeholder for other algorithms.
            # You would add other methods like self._run_fcfs() here.
            print(f"Error: Algorithm '{self.algorithm}' not implemented.")
            sys.exit(1)

        # Sort logs by time, then by event priority (1=arrived, 2=finished, 3=selected, 4=idle)
        raw_logs.sort(key=lambda x: (x[1], x[0]))
        self.log = [message for _, _, message in raw_logs]
            
        self._generate_output(finished, remaining)

    def _generate_output(self, finished_processes, remaining_processes):
        """
        Generates and writes the final output to a file with the specified format.
        """
        output_filename = self.filename.split('.')[0] + ".out"
        with open(output_filename, 'w') as f:
            f.write(f"  {self.process_count} processes\n")
            
            if self.algorithm == 'rr':
                f.write("Using Round-Robin\n")
                f.write(f"Quantum   {self.quantum}\n\n")
            else:
                # Placeholder for other algorithms.
                f.write(f"Using {self.algorithm.upper()}\n")
            
            for entry in self.log:
                f.write(entry + "\n")
            
            f.write(f"Finished at time   {self.run_for}\n\n")

            # Final summary of process metrics, sorted by process name
            finished_processes.sort(key=lambda p: p.name)
            for p in finished_processes:
                f.write(f"{p.name} wait {p.wait_time:3d} turnaround {p.turnaround_time:3d} response {p.response_time:3d}\n")
            
            remaining_processes.sort(key=lambda p: p.name)
            for p in remaining_processes:
                f.write(f"{p.name} did not finish\n")

def simulate_round_robin_scheduler(filename):
    """
    Main function to run the scheduling simulation.
    This function will be used to test the scheduler.
    """
    scheduler = RoundRobinScheduler(filename)
    scheduler.run()

# Made with ChatGPT. Link: https://chatgpt.com/share/68d0388a-b734-8008-963f-05ad45dbc656

class SJFProcess:
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

            processes.append(SJFProcess(name, arrival, burst))

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

# ChatGPT used for implementation: https://chatgpt.com/share/68d8b0f2-e110-8000-b7dd-7b76757223c5

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
            f.write("Using First-Come First-Served\n")

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

# Made with ChatGPT. Link: https://chatgpt.com/share/68d96a4b-268c-8009-a596-e32ea23dbc36

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    # Check file extension
    if not input_file.endswith(".in"):
        print("Error: Input file must have a .in extension")
        sys.exit(1)

    try:
        with open(input_file, "r") as f:
            # Read first line: store second string as numProcesses
            first_line = f.readline().strip().split()
            numProcesses = int(first_line[1])

            # Read second line: store second string as timeUnits
            second_line = f.readline().strip().split()
            timeUnits = int(second_line[1])

            # Read third line: store second string as algo
            third_line = f.readline().strip().split()
            algo = third_line[1].lower()

            # Call the appropriate scheduling algorithm
            if algo == "fcfs":
                run_fifo_scheduler_from_file(input_file)
            elif algo == "sjf":
                run_sjf_scheduler_from_file(input_file)
            elif algo == "rr":
                simulate_round_robin_scheduler(input_file)
            else:
                sys.exit(1)

    except (IndexError, ValueError) as e:
        print(f"Error parsing input file: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"File not found: {input_file}")
        sys.exit(1)

if __name__ == "__main__":
    main()
