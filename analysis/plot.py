# ╔══════════════════════════════════════════════════════════════════════════════════════╗
# ║  ⠀⠀⠀⠀⣠⠶⡒⠒⢬⡲⣮⠂⣆⣀⠀⠀⠀⠀⠀⠀⢀⣤⣴⣦⣤⡀⠀⠀⠀⠀   MATEUS OLIVEIRA                        ║
# ║  ⠀⠀⠀⣀⣥⠠⣿⠆⠐⣻⣾⣿⣿⢷⡄⠀⠀⠀⠀⢠⡿⠋⠉⠉⠙⢿⡄⠀⠀⠀   m203656@dac.unicamp.edu.br             ║
# ║  ⠀⠀⢘⡵⢋⠄⡙⠒⣤⣄⣉⠙⣿⣗⠑⡄⠀⠀⠀⠘⡇⠀⠀⠀⠀⠈⡇⠀⠀⠀   UNICAMP - Universidade Estadual de     ║
# ║  ⠀⣴⢿⡜⢡⡞⢀⢼⣿⣿⣿⣿⣿⣿⠟⣂⠀⠀⢀⣀⠱⡀⠀⠀⠀⢰⠁⠀⠀⠀               Campinas                     ║
# ║  ⠰⢫⢟⡇⢸⡇⢸⢾⣿⣿⣿⣿⣿⣿⡷⠰⠀⢰⡏⠀⠀⢡⠀⠀⢠⠃⠀⠀⠀⠀   IC - Institute of Computing            ║
# ║  ⢰⠁⣿⢣⣿⠇⢀⣿⣿⡿⠿⠤⣭⣥⣶⡆⠀⠸⣷⣤⣠⡾⠀⢀⡇⠀⠀⠀⠀⠀   Computer Science Department              ║
# ║  ⡞⣰⣧⠟⡝⢸⢸⣿⣥⠖⣴⡆⣤⣬⠉⠀⠀⠀⠈⠉⠉⠀⠀⢸⣇⠀⠀⠀⠀⠀   github.com/oliveiraMats2              ║
# ║  ⠀⡿⡟⢸⡇⠸⡄⢹⣿⢸⣿⣇⡏⠟⣰⣄⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠁⠀⠀⠀   linkedin.com/in/mateus-eng            ║
# ║  ⠀⠇⣧⠘⡇⠦⣹⣸⣿⡇⡿⡿⣡⣼⣿⣿⣷⣦⣄⡀⠀⠀⣸⣿⣿⠄⠻⢷⣦⠀                                            ║
# ║  ⠀⢀⠘⣇⢹⡸⣿⣿⣿⢹⢃⣠⣿⣿⣿⣿⣿⣿⣿⣿⣆⠀⠑⠋⠉⠀⠀⠈⣿⣧   UNICAMP · IC · 2026                    ║
# ║  ⠀⢸⣿⡌⠘⢷⣿⣿⡏⢀⣾⣿⣿⣿⣿⣿⣿⢻⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⣿⡿                                            ║
# ║  ⠀⠈⣿⣿⣦⡌⢿⠏⣰⣿⣿⣿⣿⣿⣿⡿⡏⣼⣿⣿⣿⡇⣄⠀⠀⠀⢀⣼⣿⠇                                            ║
# ║  ⠀⠀⠹⣿⣿⢻⡀⣼⣿⣿⢻⣿⣿⣿⣿⡇⡇⢻⣿⣿⣿⡇⣿⣿⣶⣿⣿⠟⠁⠀                                            ║
# ║  ⠀⠀⠀⢻⣿⣦⡓⢿⣿⣿⡆⣿⣿⣿⣿⢃⣶⡸⣿⣿⣿⡇⠀⠉⠉⠁⠀⠀⠀⠀                                            ║
# ║  ⠀⠀⠀⠈⣿⣿⣿⡆⠀⠀⠀⣿⣿⣿⡟⣼⡿⠁⢹⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀                                            ║
# ╚══════════════════════════════════════════════════════════════════════════════════════╝

"""Parse OSU osu_bw / osu_latency logs (native vs Apptainer), save .npy arrays,
plot bandwidth.png and latency.png, and write results/summary.txt.

Run from anywhere: python analysis/plot.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parent.parent
LOGS, RES, FIG = REPO / "logs", REPO / "results", REPO / "figures"
SCENARIOS, BENCHES = ("native", "container"), ("osu_bw", "osu_latency")
COLORS = {"native": "#2ca02c", "container": "#d62728"}
LINK_MBS = 12500.0  # HDR100: 100 Gb/s = 12500 MB/s (OSU MB = 1e6 bytes)


def parse(path):
    """Return {size: value} from the two first numeric columns of every data row."""
    rows = {}
    # ponytail: drop the last line when it has no trailing newline (truncated log)
    for line in path.read_text(errors="ignore").split("\n")[:-1]:
        parts = line.split()
        if len(parts) < 2 or line.lstrip().startswith("#"):
            continue
        try:
            size, val = float(parts[0]), float(parts[1])
        except ValueError:
            continue
        if size.is_integer() and np.isfinite(val):
            rows[int(size)] = val
    return rows


def load(scen, bench):
    """Return (sizes (M,), values (R, M)) aligned on sizes present in every run, or None."""
    runs = [r for r in (parse(p) for p in sorted((LOGS / scen).glob(f"{bench}_run*.log"))) if r]
    if not runs:
        return None
    sizes = np.array(sorted(set.intersection(*(set(r) for r in runs))))
    return sizes, np.array([[r[s] for s in sizes] for r in runs])


def plot(bench, data, ylabel, fname, logy):
    # large fonts: the report shows both figures side by side at half page width
    plt.rcParams.update({"axes.labelsize": 17, "xtick.labelsize": 16, "ytick.labelsize": 16, "legend.fontsize": 13})
    fig, ax = plt.subplots(figsize=(8, 5))
    for scen, (sizes, v) in data.items():
        m = sizes > 0  # 0 B cannot sit on a log axis
        ax.plot(sizes[m], v.mean(0)[m], "o-", ms=3, color=COLORS[scen], label=f"{scen} (mean, {len(v)} runs)")
        ax.fill_between(sizes[m], v.min(0)[m], v.max(0)[m], color=COLORS[scen], alpha=0.25, label=f"{scen} (min to max)")
    if bench == "osu_bw":
        ax.axhline(LINK_MBS, ls="--", color="gray", label="HDR100 theoretical (100 Gb/s)")
        ax.secondary_yaxis("right", functions=(lambda x: x * 8 / 1000, lambda x: x * 1000 / 8)).set_ylabel("Bandwidth (Gb/s)")
    if logy:
        ax.set_yscale("log")
    ax.set_xscale("log", base=2)
    ax.margins(x=0)  # x axis starts at the first size and ends at the last
    ax.set_xlabel("Message size (bytes)")
    ax.set_ylabel(ylabel)
    ax.set_title(f"{bench}: native vs Apptainer", fontsize=17)
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG / fname, dpi=150)
    plt.close(fig)


def cv_max(v):
    """Max over sizes of the run-to-run coefficient of variation (sample std / mean), in %."""
    return float(np.max(v.std(0, ddof=1) / v.mean(0)) * 100) if len(v) > 1 else float("nan")


def main():
    RES.mkdir(exist_ok=True)
    FIG.mkdir(exist_ok=True)
    data = {b: {} for b in BENCHES}
    for s in SCENARIOS:
        for b in BENCHES:
            d = load(s, b)
            if d is not None:
                data[b][s] = d
                np.save(RES / f"{s}_{b}_sizes.npy", d[0])
                np.save(RES / f"{s}_{b}.npy", d[1])
    if data["osu_bw"]:
        plot("osu_bw", data["osu_bw"], "Bandwidth (MB/s, 1 MB = 1e6 B)", "bandwidth.png", logy=False)
    if data["osu_latency"]:
        plot("osu_latency", data["osu_latency"], "Latency (us)", "latency.png", logy=True)

    out = []
    for s in SCENARIOS:
        out.append(f"[{s}]")
        for b in BENCHES:
            if s in data[b]:
                sizes, v = data[b][s]
                out.append(f"  {b}: {len(v)} runs, {len(sizes)} sizes, max CV over sizes = {cv_max(v):.2f} %")
            else:
                out.append(f"  {b}: no logs")
        if s in data["osu_bw"]:
            sizes, v = data["osu_bw"][s]
            mean = v.mean(0)
            peak = mean.max()
            stable = sizes[np.argmax(mean >= 0.95 * peak)]
            out.append(f"  peak mean bandwidth = {peak:.1f} MB/s = {peak * 8 / 1000:.2f} Gb/s = {peak / LINK_MBS * 100:.1f} % of 100 Gb/s")
            out.append(f"  bandwidth reaches >= 95 % of peak from {stable} B")
        if s in data["osu_latency"]:
            sizes, v = data["osu_latency"][s]
            out.append(f"  smallest-message mean latency = {v.mean(0)[0]:.3f} us at {sizes[0]} B")
    out.append("[container vs native, (container - native) / native]")
    for b, pick, what in (("osu_bw", -1, "bandwidth at largest"), ("osu_latency", 0, "latency at smallest")):
        if len(data[b]) == 2:
            (sn, vn), (sc, vc) = data[b]["native"], data[b]["container"]
            common = np.intersect1d(sn, sc)
            size = common[pick]
            n, c = vn.mean(0)[sn == size][0], vc.mean(0)[sc == size][0]
            out.append(f"  {what} common size ({size} B): {n:.3f} vs {c:.3f} -> {(c - n) / n * 100:+.2f} %")
        else:
            out.append(f"  {b}: needs both scenarios")
    text = "\n".join(out) + "\n"
    print(text, end="")
    (RES / "summary.txt").write_text(text)


if __name__ == "__main__":
    main()
