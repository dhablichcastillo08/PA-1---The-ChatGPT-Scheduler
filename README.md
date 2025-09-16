# PA-1---The-ChatGPT-Scheduler

You are tasked with implementing three process scheduling algorithms: 
FIFO (First In, First Out), Pre-emptive SJF (Shortest Job First), 
and Round Robin in Python, but using ChatGPT.

ChatGPT's implementation should be able to simulate the scheduling 
of multiple processes under each algorithm and calculate their 
turnaround time, response time, and wait time.

The implementation should include:

1. A data structure to represent a process, including its 
   arrival time, execution time, and status.

2. A scheduler function for each algorithm that takes in 
   a list of processes and implements the chosen 
   scheduling algorithm.

3. A time slice parameter (Q-value) for Round Robin, 
   which determines how long each process should run 
   before being preempted.

4. A function to calculate the standard metrics: 
   turnaround time, waiting time, and response time 
   for each process.
