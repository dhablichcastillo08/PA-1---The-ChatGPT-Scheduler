import sys
import os

def fcfs(input_file, output_file, numProcesses, timeUnits):
    # Placeholder for FCFS implementation
    output_file.write("fcfs() called\n")

def sjf(input_file, output_file, numProcesses, timeUnits):
    # Placeholder for SJF implementation
    output_file.write("sjf() called\n")

def rr(input_file, output_file, numProcesses, timeUnits):
    # Placeholder for RR implementation
    output_file.write("rr() called\n")

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    # Check file extension
    if not input_file.endswith(".in"):
        print("Error: Input file must have a .in extension")
        sys.exit(1)

    # Create output file with same base name
    base_name = os.path.splitext(input_file)[0]
    output_filename = base_name + ".out"

    try:
        with open(input_file, "r") as f, open(output_filename, "w") as out:
            # Read first line: store second string as numProcesses
            first_line = f.readline().strip().split()
            numProcesses = int(first_line[1])
            out.write(f"{numProcesses} processes\n")

            # Read second line: store second string as timeUnits
            second_line = f.readline().strip().split()
            timeUnits = int(second_line[1])

            # Read third line: store second string as algo
            third_line = f.readline().strip().split()
            algo = third_line[1].lower()

            # Call the appropriate scheduling algorithm
            if algo == "fcfs":
                out.write("Using fcfs\n")
                fcfs(input_file, out, numProcesses, timeUnits)
            elif algo == "sjf":
                out.write("Using sjf\n")
                sjf(input_file, out, numProcesses, timeUnits)
            elif algo == "rr":
                out.write("Using rr\n")
                rr(input_file, out, numProcesses, timeUnits)
            else:
                out.write(f"Unknown algorithm: {algo}\n")
                sys.exit(1)

    except (IndexError, ValueError) as e:
        print(f"Error parsing input file: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"File not found: {input_file}")
        sys.exit(1)

if __name__ == "__main__":
    main()
