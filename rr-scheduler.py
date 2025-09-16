# The contents of this file will eventually be integrated into the main 'scheduler-gpt.py' file.
# Google Gemini used for creation. Link: https://g.co/gemini/share/b862a9784cd1
# To run this code, call simulate_round_robin_scheduler with the filename as an argument.

import sys
import re
from collections import deque

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