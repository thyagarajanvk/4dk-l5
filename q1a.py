import subprocess
import csv
import re
import matplotlib.pyplot as plt
import os

# -----------------------------
# Configuration
# -----------------------------
RERUN = False           # True: sweep B, compile/run; False: just plot from CSV
B_values = range(1, 5) # Sweep B from 1 to 4 inclusive
CSV_FILE = "q1a.csv"
EXECUTABLE = "./run"
SOURCE_WILDCARD = "*.c"

# Regex patterns to parse output
REJECTED_PATTERN = re.compile(r"Rejected arrival count\s*=\s*([\d\.]+)")
TRANSMITTED_PATTERN = re.compile(r"Transmitted arrival count\s*=\s*([\d\.]+)")

# -----------------------------
# Function to compile with given B
# -----------------------------
def compile_program(B):
    cmd = f"gcc -O2 -Wall -DB={B} {SOURCE_WILDCARD} -o {EXECUTABLE} -lm"
    print(f"Compiling with B={B}...")
    subprocess.run(cmd, shell=True, check=True)

# -----------------------------
# Function to run executable and parse output
# -----------------------------
def run_and_parse():
    result = subprocess.run(EXECUTABLE, shell=True, capture_output=True, text=True)
    output = result.stdout

    rejected = None
    transmitted = None

    match = REJECTED_PATTERN.search(output)
    if match:
        rejected = float(match.group(1))

    match = TRANSMITTED_PATTERN.search(output)
    if match:
        transmitted = float(match.group(1))

    return rejected, transmitted

# -----------------------------
# Main logic
# -----------------------------
if RERUN:
    rejected_list = []
    transmitted_list = []

    for B in B_values:
        compile_program(B)
        rej, trans = run_and_parse()
        if rej is None or trans is None:
            print(f"Warning: failed to parse output for B={B}")
        rejected_list.append(rej)
        transmitted_list.append(trans)

    # Write CSV
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["B", "Rejected", "Transmitted"])
        for B, rej, trans in zip(B_values, rejected_list, transmitted_list):
            writer.writerow([B, rej, trans])

else:
    # just read csv
    B_values = []
    rejected_list = []
    transmitted_list = []

    if not os.path.exists(CSV_FILE):
        raise FileNotFoundError(f"{CSV_FILE} not found. Set RERUN=True first.")

    with open(CSV_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            B_values.append(int(row["B"]))
            rejected_list.append(float(row["Rejected"]))
            transmitted_list.append(float(row["Transmitted"]))

# -----------------------------
# Plotting
# -----------------------------
plt.figure(figsize=(10,5))

plt.subplot(1,2,1)
plt.plot(B_values, rejected_list, marker='o')
plt.title("Rejected arrivals vs B")
plt.xlabel("B")
plt.ylabel("Rejected arrivals")

plt.subplot(1,2,2)
plt.plot(B_values, transmitted_list, marker='o', color='green')
plt.title("Transmitted arrivals vs B")
plt.xlabel("B")
plt.ylabel("Transmitted arrivals")

plt.tight_layout()
plt.savefig("q1a.png") 
