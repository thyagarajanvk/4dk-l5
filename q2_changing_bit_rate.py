import csv
import subprocess
import re
import matplotlib.pyplot as plt

RUN = True  # set False to only plot

CSV_FILE = "q2_changing_bit_rate.csv"
XMT_TIME = 0.1

# ============================================================
# RUN MODE: Build + execute program for each N
# ============================================================
if RUN:
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["N", "RejectedRate", "TransmittedRate"])

        for N in range(3000, 30001, 1000):
            print(f"[RUN] Building + running with N={N}, PACKET_XMT_TIME={XMT_TIME}")

            # compile
            cmd = f"gcc -O2 -Wall -DPACKET_XMT_TIME={XMT_TIME} -DN={N} *.c -o run -lm"
            subprocess.run(cmd, shell=True, check=True)

            # run program
            result = subprocess.run("./run", shell=True, capture_output=True, text=True)
            txt = result.stdout

            # parse output
            rejected = float(re.search(r"Average Rejected bit count = ([0-9.]+)", txt).group(1))
            transmitted = float(re.search(r"Average Transmitted bit count = ([0-9.]+)", txt).group(1))

            # convert to rates
            writer.writerow([N, rejected / 100, transmitted / 100])


# ============================================================
# PLOT MODE: Load CSV + create plots
# ============================================================
Ns = []
rej_rates = []
tx_rates = []

with open(CSV_FILE) as f:
    r = csv.DictReader(f)
    for row in r:
        Ns.append(int(row["N"]))
        rej_rates.append(float(row["RejectedRate"]))
        tx_rates.append(float(row["TransmittedRate"]))

# -------- Rejected Plot --------
plt.figure(figsize=(10, 5))
plt.plot(Ns, rej_rates, marker="o")
plt.title(f"Rejected Bit Rate vs N (PACKET_XMT_TIME = {XMT_TIME})")
plt.xlabel("N")
plt.ylabel("Rejected Bit Rate (bps)")
plt.grid(True)
plt.savefig("q2_changing_bit_rate_rejected_bit_rate.png")

# -------- Transmitted Plot --------
plt.figure(figsize=(10, 5))
plt.plot(Ns, tx_rates, marker="o")
plt.title(f"Output Data Rate vs N (PACKET_XMT_TIME = {XMT_TIME})")
plt.xlabel("N")
plt.ylabel("Output Data Rate (bps)")
plt.grid(True)
plt.savefig("q2_changing_bit_rate_output_data_rate.png")
