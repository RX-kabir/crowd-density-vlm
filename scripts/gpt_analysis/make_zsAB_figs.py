import os, shutil
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix

SRC = "D:/Downloads"
OUT = "D:/CrowdDensityResearch/phase5/gpt/Zero_Shot"
GPT_A, GPT_B = "#2E75B6", "#E67E22"       # A = GPT blue, B = orange (same convention as the other models' A-vs-B figures)
MODEL = "GPT-6.1 Terra"

A = pd.read_csv(f"{SRC}/gpt_experiment_A_zeroshot_evaluated.csv")
B = pd.read_csv(f"{SRC}/gpt_experiment_B_zeroshot_evaluated.csv")

def style(ax):
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)

# ---- fig1: predicted vs ground truth, A vs B side by side ----
fig, axes = plt.subplots(1, 2, figsize=(14, 6.2), sharey=True)
lim = [0.5, 3e4]
for ax, df, col, ttl in [(axes[0], A, GPT_A, "Experiment A (zero-shot, no YOLO)"), (axes[1], B, GPT_B, "Experiment B (zero-shot, with YOLO)")]:
    ax.scatter(df.total_count.clip(lower=0.5), df.predicted_count.clip(lower=0.5), s=16, alpha=0.35, color=col, edgecolors="none")
    ax.plot(lim, lim, "k--", lw=1.2, label="Perfect prediction")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lim); ax.set_ylim(lim)
    ax.set_xlabel("Ground-truth count (log scale)", fontsize=13); ax.set_title(ttl, fontsize=13)
    ax.legend(loc="upper left", frameon=False); style(ax)
axes[0].set_ylabel("Predicted count (log scale)", fontsize=13)
fig.suptitle(f"{MODEL} — Zero-Shot: Predicted vs. Ground-Truth Count, A vs. B", fontsize=15)
fig.tight_layout(rect=[0, 0, 1, 0.95]); fig.savefig(f"{OUT}/gptZS_AB_fig1_scatter.png", dpi=200); plt.close(fig)

# ---- fig2: density confusion matrices, A vs B ----
def cm_of(df):
    d = df.dropna(subset=["predicted_density"])
    return confusion_matrix(d.crowd_density.astype(int), d.predicted_density.astype(int), labels=[0, 1, 2])
names = ["Low", "Medium", "High"]
fig, axes = plt.subplots(1, 2, figsize=(13, 6))
for ax, df, cmap, ttl in [(axes[0], A, "Blues", "Experiment A (zero-shot)"), (axes[1], B, "Oranges", "Experiment B (zero-shot)")]:
    cm = cm_of(df)
    ax.imshow(cm, cmap=cmap, vmin=0, vmax=cm.max())
    for i in range(3):
        for j in range(3):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=14, color="white" if cm[i, j] > cm.max() * 0.55 else "black")
    ax.set_xticks(range(3)); ax.set_xticklabels(names, fontsize=12); ax.set_yticks(range(3)); ax.set_yticklabels(names, fontsize=12)
    ax.set_xlabel("Predicted density", fontsize=13); ax.set_ylabel("Ground-truth density", fontsize=13); ax.set_title(ttl, fontsize=12)
    for s in ["top", "right", "left", "bottom"]: ax.spines[s].set_visible(False)
fig.suptitle(f"{MODEL} — Zero-Shot Density Confusion Matrices, A vs. B\n(small change — the YOLO count does not fix the Medium → High confusion)", fontsize=14)
fig.tight_layout(rect=[0, 0, 1, 0.9]); fig.savefig(f"{OUT}/gptZS_AB_fig2_confusion.png", dpi=200); plt.close(fig)

# ---- fig3: MAE by density, A vs B ----
def mae_by(df):
    v = df.dropna(subset=["predicted_count"])
    return [(v[v.crowd_density == k].predicted_count - v[v.crowd_density == k].total_count).abs().mean() for k in [0, 1, 2]]
ma, mb = mae_by(A), mae_by(B)
x = np.arange(3); w = 0.36
fig, ax = plt.subplots(figsize=(9, 6))
b1 = ax.bar(x - w / 2, ma, w, color=GPT_A, label="Experiment A (zero-shot)")
b2 = ax.bar(x + w / 2, mb, w, color=GPT_B, label="Experiment B (zero-shot)")
for bars in (b1, b2):
    for b in bars:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + max(ma + mb) * 0.012, f"{b.get_height():.0f}", ha="center", fontsize=11)
ax.set_xticks(x); ax.set_xticklabels(["Low (0)", "Medium (1)", "High (2)"], fontsize=12)
ax.set_xlabel("Ground-truth crowd density class", fontsize=13); ax.set_ylabel("Mean Absolute Error (MAE)", fontsize=13)
ax.set_title(f"{MODEL} Zero-Shot — Counting MAE by Density, A vs. B", fontsize=14); ax.legend(frameon=False, loc="upper left"); style(ax)
fig.tight_layout(); fig.savefig(f"{OUT}/gptZS_AB_fig3_mae_by_density.png", dpi=200); plt.close(fig)

# ---- fig4: signed bias by ground-truth count band (the overcount that YOLO removes) ----
bins = [0, 10, 50, 100, 500, 1000, 10000]
labs = ["0-10", "11-50", "51-100", "101-500", "501-1k", "1k+"]
def bias_by(df):
    v = df.dropna(subset=["predicted_count"]).copy(); v["b"] = pd.cut(v.total_count, bins, include_lowest=True, labels=labs)
    return v.groupby("b", observed=True).apply(lambda g: (g.predicted_count - g.total_count).mean()).values
ba, bb = bias_by(A), bias_by(B)
yb = B.copy(); yb["b"] = pd.cut(yb.total_count, bins, include_lowest=True, labels=labs)
by = yb.groupby("b", observed=True).apply(lambda g: (g.yolo_predicted_count - g.total_count).mean()).values
x = np.arange(len(labs)); w = 0.27
fig, ax = plt.subplots(figsize=(10.5, 6))
ax.bar(x - w, ba, w, color=GPT_A, label="Experiment A (no YOLO)")
ax.bar(x, bb, w, color=GPT_B, label="Experiment B (with YOLO)")
ax.bar(x + w, by, w, color="#7F8C8D", label="YOLO count itself")
ax.axhline(0, color="k", lw=0.8)
ax.set_yscale("symlog", linthresh=100)
ax.set_xticks(x); ax.set_xticklabels(labs, fontsize=12)
ax.set_xlabel("Ground-truth count band", fontsize=13); ax.set_ylabel("Mean signed error (predicted - true), symlog scale", fontsize=12)
ax.set_title(f"{MODEL} Zero-Shot — Counting Bias by Crowd Size\n(A over-counts increasingly; YOLO under-counts; B lands near zero)", fontsize=14)
ax.legend(frameon=False, loc="lower left"); style(ax)
fig.tight_layout(); fig.savefig(f"{OUT}/gptZS_AB_fig4_bias_by_count.png", dpi=200); plt.close(fig)

for f in ["gpt_experiment_B_zeroshot.csv", "gpt_experiment_B_zeroshot_evaluated.csv"]:
    shutil.copy2(f"{SRC}/{f}", f"{OUT}/{f}")
print("done")
