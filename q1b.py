import subprocess
import csv
import re
import matplotlib.pyplot as plt
import os

# -----------------------------
# Configuration
# -----------------------------
RERUN = True                       # True: sweep rates, compile/run; False: just plot from CSV
ARRIVAL_RATES = range(10, 201, 10)  # From 10 to 200 inclusive
CSV_FILE = "q1b.csv"
EXECUTABLE = "./run"
SOURCE_WILDCARD = "*.c"
RUN_LENGTH = 100000

# Regex patterns to parse output
REJECTED_PATTERN = re.compile(r"Rejected arrival count\s*=\s*([\d\.]+)")
TRANSMITTED_PATTERN = re.compile(r"Transmitted arrival count\s*=\s*([\d\.]+)")

# -----------------------------
# Function to compile program with PACKET_ARRIVAL_RATE
# -----------------------------
def compile_program(arrival_rate):
    cmd = f"gcc -O2 -Wall -DPACKET_ARRIVAL_RATE={arrival_rate} {SOURCE_WILDCARD} -o {EXECUTABLE} -lm"
    print(f"Compiling with PACKET_ARRIVAL_RATE={arrival_rate}...")
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

    for rate in ARRIVAL_RATES:
        compile_program(rate)
        rej, trans = run_and_parse()
        if rej is None or trans is None:
            print(f"Warning: failed to parse output for rate={rate}")
        rejected_list.append(rej / RUN_LENGTH)       # convert to rate
        transmitted_list.append(trans / RUN_LENGTH) # convert to rate

    # Write CSV
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ArrivalRate", "RejectedRate", "TransmittedRate"])
        for rate, rej, trans in zip(ARRIVAL_RATES, rejected_list, transmitted_list):
            writer.writerow([rate, rej, trans])

else:
    # just read csv
    ARRIVAL_RATES = []
    rejected_list = []
    transmitted_list = []

    if not os.path.exists(CSV_FILE):
        raise FileNotFoundError(f"{CSV_FILE} not found. Set RERUN=True first.")

    with open(CSV_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ARRIVAL_RATES.append(int(row["ArrivalRate"]))
            rejected_list.append(float(row["RejectedRate"]))
            transmitted_list.append(float(row["TransmittedRate"]))

# -----------------------------
# Plotting
# -----------------------------
plt.figure(figsize=(10,5))

plt.subplot(1,2,1)
plt.plot(ARRIVAL_RATES, rejected_list, marker='o')
plt.title("Rejected arrival rate vs Packet Arrival Rate")
plt.xlabel("Packet Arrival Rate")
plt.ylabel("Rejected rate")

plt.subplot(1,2,2)
plt.plot(ARRIVAL_RATES, transmitted_list, marker='o', color='green')
plt.title("Transmitted arrival rate vs Packet Arrival Rate")
plt.xlabel("Packet Arrival Rate")
plt.ylabel("Transmitted rate")

plt.tight_layout()
plt.savefig("q1b.png")  # save figure instead of showing
