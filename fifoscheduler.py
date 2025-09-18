class Process:
    def __init__(self, name, arrival, runtime):
        self.name = name
        self.arrival = arrival
        self.runtime = runtime
        self.remaining = runtime

        self.start_time = None
        self.finish_time = None

    def __repr__(self):
        return f"{self.name}(arr={self.arrival}, burst={self.burst}, rem={self.remaining})"


''' def schedulerFIFO(processes, runfor):
    # Sort by arrival order
    ready = sorted(processes, key=lambda x: x.arrival)

    time = 0
    ready = []

    queue = []
    current = None

    while time < runfor:
        # Check arrivals
        for p in ready:
            if p.arrival == time:
                log.append(f"Time {time} : {p.name} arrived")
                queue.append(p)

        # If no process running, pick the next in queue
        if current is None and queue:
            current = queue.pop(0)
            if current.start_time is None:
                current.start_time = time
            log.append(f"Time {time} : {current.name} selected (burst {current.remaining})")

        # Run current process if available
        if current:
            current.remaining -= 1
            if current.remaining == 0:
                current.finish_time = time + 1
                log.append(f"Time {time+1} : {current.name} finished")
                current = None
        else:
            log.append(f"Time {time} : Idle")

        time += 1

    log.append(f"Finished at time {runfor}")
    return log '''

def fifo_scheduler(processes, runfor):
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

    return timeline


''' def calculate_metrics(processes):
    results = []
    for p in processes:
        if p.finish_time is None:
            results.append(f"{p.name} did not finish")
            continue
        turnaround = p.finish_time - p.arrival
        wait = turnaround - p.runtime
        response = (p.start_time - p.arrival) if p.start_time is not None else 0
        results.append(f"{p.name} wait {wait} turnaround {turnaround} response {response}")
    return results '''

def calculate_metrics(processes):
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
    return results


processes = [
    Process("A", 0, 5),
    Process("B", 2, 3),
    Process("C", 2, 8),
]

runfor = 20

# Run FIFO scheduler
timeline = fifo_scheduler(processes, runfor)
print("Timeline:", timeline)

# Metrics
metrics = calculate_metrics(processes)
for name, vals in metrics.items():
    print(f"{name}: {vals}")