import csv
import subprocess
import re
import matplotlib.pyplot as plt

RUN = True  # set False to only plot

CSV_FILE = "q2_changing_n_clkperiod.csv"

# ============================================================
# RUN MODE
# ============================================================
if RUN:
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["N", "XMTtime", "RejectedRate", "TransmittedRate"])

        for N in range(10000, 1000001, 20000):
            XMT_TIME = N / 1000000.0

            print(f"[RUN] N={N}  PACKET_XMT_TIME={XMT_TIME}")

            # compile
            cmd = (
                f"gcc -O2 -Wall -DPACKET_XMT_TIME={XMT_TIME} "
                f"-DN={N} *.c -o run -lm"
            )
            subprocess.run(cmd, shell=True, check=True)

            # run executable
            result = subprocess.run("./run", shell=True, capture_output=True, text=True)
            txt = result.stdout

            # extract values
            rejected = float(re.search(r"Average Rejected bit count = ([0-9.]+)", txt).group(1))
            transmitted = float(re.search(r"Average Transmitted bit count = ([0-9.]+)", txt).group(1))


            writer.writerow([N, XMT_TIME, rejected / 100, transmitted / 100])


# ============================================================
# PLOT MODE
# ============================================================
Ns = []
xmt_times = []
rej_rates = []
tx_rates = []

with open(CSV_FILE) as f:
    r = csv.DictReader(f)
    for row in r:
        Ns.append(int(row["N"]))
        xmt_times.append(float(row["XMTtime"]))
        rej_rates.append(float(row["RejectedRate"]))
        tx_rates.append(float(row["TransmittedRate"]))

# xticks show N and XMT_TIME:
xt_labels = [f"{Ns[i]}\n{round(xmt_times[i], 6)}" for i in range(len(Ns))]

# -------- Rejected Plot --------
plt.figure(figsize=(14, 6))
plt.plot(Ns, rej_rates, marker="o")
plt.title("Rejected Bit Rate vs N (PACKET_XMT_TIME = 1e6 / N)")
plt.xlabel("N  (with PACKET_XMT_TIME below)")
plt.ylabel("Rejected Bit Rate (bps)")
plt.xticks(Ns[::5], xt_labels[::5], rotation=45)
plt.grid(True)
plt.tight_layout()
plt.savefig("q2_changing_n_clkperiod_rejected_bit_rate.png")

# -------- Transmitted Plot --------
plt.figure(figsize=(14, 6))
plt.plot(Ns, tx_rates, marker="o")
plt.title("Output Data Rate vs N (PACKET_XMT_TIME = 1e6 / N)")
plt.xlabel("N  (with PACKET_XMT_TIME below)")
plt.ylabel("Output Data Rate (bps)")
plt.xticks(Ns[::5], xt_labels[::5], rotation=45)
plt.grid(True)
plt.tight_layout()
plt.savefig("q2_changing_n_clkperiod_output_data_rate.png")
