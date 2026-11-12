import os, shutil
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix

SRC = "D:/Downloads"
OUT = "D:/CrowdDensityResearch/phase5/gpt/Five_Shot"
OUT2 = "D:/CrowdDensityResearch/phase5/Results/gpt/Five_Shot"
os.makedirs(OUT, exist_ok=True); os.makedirs(OUT2, exist_ok=True)

GPT = "#2E75B6"
MODEL = "GPT-6.1 Terra"
TITLE = f"{MODEL} — 5-Shot Experiment A"

e = pd.read_csv(f"{SRC}/gpt_experiment_A_evaluated.csv")
v = e.dropna(subset=["predicted_count"]).copy()
d = e.dropna(subset=["predicted_density"]).copy()

def style(ax):
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)

# fig1: predicted vs ground truth (log-log)
fig, ax = plt.subplots(figsize=(8, 8))
ax.scatter(v.total_count.clip(lower=0.5), v.predicted_count.clip(lower=0.5), s=18, alpha=0.35, color=GPT, edgecolors="none")
lim = [0.5, 3e4]
ax.plot(lim, lim, "k--", lw=1.2, label="Perfect prediction")
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lim); ax.set_ylim(lim)
ax.set_xlabel("Ground-truth count (log scale)", fontsize=13); ax.set_ylabel("Predicted count (log scale)", fontsize=13)
ax.set_title(f"{TITLE}\nPredicted vs. Ground-Truth Crowd Count", fontsize=15)
ax.legend(loc="upper left", frameon=False); style(ax)
fig.tight_layout(); fig.savefig(f"{OUT}/gptA_fig1_scatter.png", dpi=200); plt.close(fig)

# fig2: MAE by density class
mae = [(v[v.crowd_density == k].predicted_count - v[v.crowd_density == k].total_count).abs().mean() for k in [0, 1, 2]]
fig, ax = plt.subplots(figsize=(7, 5.4))
bars = ax.bar(["Low (0)", "Medium (1)", "High (2)"], mae, color=GPT, width=0.6)
for b, m in zip(bars, mae):
    ax.text(b.get_x() + b.get_width() / 2, m + max(mae) * 0.015, f"{m:.0f}", ha="center", va="bottom", fontsize=12)
ax.set_ylabel("Mean Absolute Error (MAE)", fontsize=13); ax.set_xlabel("Ground-truth crowd density class", fontsize=13)
ax.set_title(f"{TITLE}\nCounting MAE by Density Class", fontsize=14); ax.set_ylim(0, max(mae) * 1.1); style(ax)
fig.tight_layout(); fig.savefig(f"{OUT}/gptA_fig2_mae_by_density.png", dpi=200); plt.close(fig)

# fig3: density confusion matrix
cm = confusion_matrix(d.crowd_density.astype(int), d.predicted_density.astype(int), labels=[0, 1, 2])
fig, ax = plt.subplots(figsize=(6.2, 5.8))
ax.imshow(cm, cmap="Blues", vmin=0, vmax=cm.max())
for i in range(3):
    for j in range(3):
        ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=14, color="white" if cm[i, j] > cm.max() * 0.55 else "black")
nm = ["Low", "Medium", "High"]
ax.set_xticks(range(3)); ax.set_xticklabels(nm, fontsize=12); ax.set_yticks(range(3)); ax.set_yticklabels(nm, fontsize=12)
ax.set_xlabel("Predicted density", fontsize=13); ax.set_ylabel("Ground-truth density", fontsize=13)
ax.set_title(f"{TITLE}\nDensity Confusion Matrix", fontsize=14)
for s in ["top", "right", "left", "bottom"]: ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/gptA_fig3_confusion.png", dpi=200); plt.close(fig)

for f in ["gpt_experiment_A.csv", "gpt_experiment_A_evaluated.csv"]:
    shutil.copy2(f"{SRC}/{f}", f"{OUT}/{f}")
for f in os.listdir(OUT):
    if f.startswith("gptA_fig") or f.startswith("gpt_experiment_A"):
        shutil.copy2(f"{OUT}/{f}", f"{OUT2}/{f}")
print(sorted(os.listdir(OUT)))
