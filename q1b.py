import subprocess
import csv
import re
import matplotlib.pyplot as plt
import os

# -----------------------------
# Configuration
# -----------------------------
RERUN = False                       # True: sweep rates, compile/run; False: just plot from CSV
LINK_BIT_RATES = range(20, 401, 20)  # From 100 to 2000 inclusive
CSV_FILE = "q1b.csv"
EXECUTABLE = "./run"
SOURCE_WILDCARD = "*.c"
RUN_LENGTH = 100

# Regex patterns to parse output
REJECTED_PATTERN = re.compile(r"Rejected arrival count\s*=\s*([\d\.]+)")
TRANSMITTED_PATTERN = re.compile(r"Transmitted arrival count\s*=\s*([\d\.]+)")

# -----------------------------
# Function to compile program with LINK_BIT_RATE
# -----------------------------
def compile_program(link_bit_rate):
    cmd = f"gcc -O2 -Wall -DLINK_BIT_RATE={link_bit_rate} {SOURCE_WILDCARD} -o {EXECUTABLE} -lm"
    print(f"Compiling with LINK_BIT_RATE={link_bit_rate}...")
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

    for rate in LINK_BIT_RATES:
        compile_program(rate)
        rej, trans = run_and_parse()
        if rej is None or trans is None:
            print(f"Warning: failed to parse output for rate={rate}")
        rejected_list.append(rej / RUN_LENGTH)       # convert to rate
        transmitted_list.append(trans / RUN_LENGTH) # convert to rate

    # Write CSV
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["LinkBitRate", "RejectedRate", "TransmittedRate"])
        for rate, rej, trans in zip(LINK_BIT_RATES, rejected_list, transmitted_list):
            writer.writerow([rate, rej, trans])

else:
    # just read csv
    LINK_BIT_RATES = []
    rejected_list = []
    transmitted_list = []

    if not os.path.exists(CSV_FILE):
        raise FileNotFoundError(f"{CSV_FILE} not found. Set RERUN=True first.")

    with open(CSV_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            LINK_BIT_RATES.append(int(row["LinkBitRate"]))
            rejected_list.append(float(row["RejectedRate"]))
            transmitted_list.append(float(row["TransmittedRate"]))

# -----------------------------
# Plotting
# -----------------------------
plt.figure(figsize=(10,5))

plt.subplot(1,2,1)
plt.plot(LINK_BIT_RATES, rejected_list, marker='o')
plt.title("Rejected packet rate vs R")
plt.xlabel("R (packets/sec)")
plt.ylabel("Rejected packet rate (packets/sec)")

plt.subplot(1,2,2)
plt.plot(LINK_BIT_RATES, transmitted_list, marker='o', color='green')
plt.title("Output/Processed Packet rate vs R")
plt.xlabel("R (packets/sec)")
plt.ylabel("Output/Processed Packet rate (packets/sec)")

plt.tight_layout()
plt.savefig("q1b.png")  # save figure instead of showing
