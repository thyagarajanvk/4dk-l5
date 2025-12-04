import subprocess
import matplotlib.pyplot as plt
import sys
import os

c_source = "q3.c"
simlib_source = "simlib.c"
executable = "token_sim"
seeds = [333333, 4444444, 5555555, 400383048]

def compile_code():
    print("compiling code...")
    cmd = ["gcc", c_source, simlib_source, "-o", executable, "-lm"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("compilation failed")
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
    # style inspired by picture 2: no grid, black spines, specific colors
    color_loss = '#1f77b4'  # standard blue
    color_out = 'green'     # standard green

    # plot loss rate (blue) on left axis
    ax.plot(xdata, loss_data, marker='o', color=color_loss, label='loss rate', markersize=5)
    ax.set_xlabel(xlabel, color='black')
    ax.set_ylabel('loss rate', color='black')
    ax.tick_params(axis='y', labelcolor='black', colors='black')
    ax.tick_params(axis='x', labelcolor='black', colors='black')
    
    # plot throughput (green) on right axis
    ax2 = ax.twinx()
    ax2.plot(xdata, out_data, marker='o', color=color_out, label='output rate', markersize=5)
    ax2.set_ylabel('output rate (pps)', color='black')
    ax2.tick_params(axis='y', labelcolor='black', colors='black')

    # axis colors and grid
    ax.grid(False)
    ax2.grid(False)
    
    for spine in ax.spines.values():
        spine.set_edgecolor('black')
    for spine in ax2.spines.values():
        spine.set_edgecolor('black')

    ax.set_title(title, color='black')

def main():
    compile_code()
    
    exp1_x, exp1_loss, exp1_out = [], [], []
    exp2_x, exp2_loss, exp2_out = [], [], []
    exp3_x, exp3_loss, exp3_out = [], [], []

    print("running exp 1 varying bt")
    for bt in range(1, 51, 1):
        loss, out = get_averaged_point(bt, 10, 90.0)
        exp1_x.append(bt)
        exp1_loss.append(loss)
        exp1_out.append(out)

    print("running exp 2 varying bd")
    for bd in range(1, 51, 1):
        loss, out = get_averaged_point(10, bd, 90.0)
        exp2_x.append(bd)
        exp2_loss.append(loss)
        exp2_out.append(out)

    print("running exp 3 varying rate")
    for rate in range(50, 155, 5):
        loss, out = get_averaged_point(10, 10, float(rate))
        exp3_x.append(rate)
        exp3_loss.append(loss)
        exp3_out.append(out)

    print("generating plots")

    # image 1: buckets (bt and bd)
    fig1, axes1 = plt.subplots(1, 2, figsize=(12, 5))
    apply_style(axes1[0], 'exp 1: varying token bucket (bt)', 'token bucket size', exp1_x, exp1_loss, exp1_out)
    apply_style(axes1[1], 'exp 2: varying data bucket (bd)', 'data bucket size', exp2_x, exp2_loss, exp2_out)
    plt.tight_layout()
    plt.savefig('lab5_buckets.png')
    print("saved lab5_buckets.png")

    # image 2: rate
    fig2, ax2 = plt.subplots(1, 1, figsize=(6, 5))
    apply_style(ax2, 'exp 3: varying token rate', 'token rate (pps)', exp3_x, exp3_loss, exp3_out)
    plt.tight_layout()
    plt.savefig('lab5_rate.png')
    print("saved lab5_rate.png")

if __name__ == "__main__":
    main()