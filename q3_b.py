import subprocess
import matplotlib.pyplot as plt
import sys
import os

c_source = "q3_b.c"
simlib_source = "simlib.c"
executable = "q3_b_sim"
seeds = [333333, 4444444, 5555555, 400383048]

def compile_code():
    print("compiling q3 part b...")
    cmd = ["gcc", c_source, simlib_source, "-o", executable, "-lm"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("compilation failed")
        print(result.stderr)
        sys.exit(1)

def run_simulation(bt, bd, rate, seed):
    if os.name == 'nt': 
        cmd = [f"{executable}.exe", str(bt), str(bd), str(rate), str(seed)]
    else: 
        cmd = [f"./{executable}", str(bt), str(bd), str(rate), str(seed)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        line = result.stdout.strip()
        parts = line.split(',')
        return float(parts[0]), float(parts[1])
    except:
        return 0.0, 0.0

def get_averaged_point(bt, bd, rate):
    total_loss = 0
    total_out = 0
    for s in seeds:
        l, o = run_simulation(bt, bd, rate, s)
        total_loss += l
        total_out += o
    return total_loss / len(seeds), total_out / len(seeds)

def apply_style(ax, title, xlabel, xdata, loss_data, out_data):
    color_loss = '#1f77b4' 
    color_out = 'green'     

    ax.plot(xdata, loss_data, marker='o', color=color_loss, label='loss rate', markersize=5)
    ax.set_xlabel(xlabel, color='black')
    ax.set_ylabel('loss rate', color='black')
    ax.tick_params(axis='y', labelcolor='black', colors='black')
    ax.tick_params(axis='x', labelcolor='black', colors='black')
    
    ax2 = ax.twinx()
    ax2.plot(xdata, out_data, marker='o', color=color_out, label='throughput', markersize=5)
    ax2.set_ylabel('output rate (bps)', color='black')
    ax2.tick_params(axis='y', labelcolor='black', colors='black')

    ax.grid(False)
    ax2.grid(False)
    for spine in ax.spines.values(): spine.set_edgecolor('black')
    for spine in ax2.spines.values(): spine.set_edgecolor('black')
    ax.set_title(title, color='black')

def main():
    compile_code()
    
    exp_x, exp_loss, exp_out = [], [], []

    print("running bit-based experiments")
    
    # sweep token rate from 50k to 250k bps
    # average packet size is 1500 bits
    # average arrival rate is 100 pkt/sec
    # average load = 150,000 bps
    
    for rate in range(50000, 260000, 10000):
        # bt = 10,000 bits (approx 6-7 average packets)
        # bd = 50 packets
        loss, out = get_averaged_point(10000, 50, float(rate))
        exp_x.append(rate)
        exp_loss.append(loss)
        exp_out.append(out)

    print("generating plot")
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    apply_style(ax, 'q3 part b: bit-based performance', 'token rate (bps)', exp_x, exp_loss, exp_out)
    
    plt.tight_layout()
    plt.savefig('lab5_q3_b.png')
    print("saved lab5_q3_b.png")

if __name__ == "__main__":
    main()