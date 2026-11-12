import os, shutil
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix

SRC = "D:/Downloads"
OUT = "D:/CrowdDensityResearch/phase5/gpt/Zero_Shot"
OUT2 = "D:/CrowdDensityResearch/phase5/Results/gpt/Zero_Shot"
os.makedirs(OUT, exist_ok=True); os.makedirs(OUT2, exist_ok=True)

GPT = "#2E75B6"          # GPT colour (Qwen red, LLaVA green, Gemma purple, YOLO grey are taken)
MODEL = "GPT-6.1 Terra"
TITLE = f"{MODEL} — Zero-Shot Experiment A"

e = pd.read_csv(f"{SRC}/gpt_experiment_A_zeroshot_evaluated.csv")
v = e.dropna(subset=["predicted_count"]).copy()
d = e.dropna(subset=["predicted_density"]).copy()

def style(ax):
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)

# ---- fig1: predicted vs ground-truth (log-log) ----
fig, ax = plt.subplots(figsize=(8, 8))
x = v.total_count.clip(lower=0.5); y = v.predicted_count.clip(lower=0.5)
ax.scatter(x, y, s=18, alpha=0.35, color=GPT, edgecolors="none")
lim = [0.5, 3e4]
ax.plot(lim, lim, "k--", lw=1.2, label="Perfect prediction")
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lim); ax.set_ylim(lim)
ax.set_xlabel("Ground-truth count (log scale)", fontsize=13); ax.set_ylabel("Predicted count (log scale)", fontsize=13)
ax.set_title(f"{TITLE}\nPredicted vs. Ground-Truth Crowd Count", fontsize=15)
ax.legend(loc="upper left", frameon=False); style(ax)
fig.tight_layout(); fig.savefig(f"{OUT}/gptZS_fig1_scatter.png", dpi=200); plt.close(fig)

# ---- fig2: MAE by density class ----
labels = ["Low (0)", "Medium (1)", "High (2)"]
mae = [(v[v.crowd_density == k].predicted_count - v[v.crowd_density == k].total_count).abs().mean() for k in [0, 1, 2]]
fig, ax = plt.subplots(figsize=(7, 5.4))
bars = ax.bar(labels, mae, color=GPT, width=0.6)
for b, m in zip(bars, mae):
    ax.text(b.get_x() + b.get_width() / 2, m + max(mae) * 0.015, f"{m:.0f}", ha="center", va="bottom", fontsize=12)
ax.set_ylabel("Mean Absolute Error (MAE)", fontsize=13); ax.set_xlabel("Ground-truth crowd density class", fontsize=13)
ax.set_title(f"{TITLE}\nCounting MAE by Density Class", fontsize=14); ax.set_ylim(0, max(mae) * 1.1); style(ax)
fig.tight_layout(); fig.savefig(f"{OUT}/gptZS_fig2_mae_by_density.png", dpi=200); plt.close(fig)

# ---- fig3: density confusion matrix ----
cm = confusion_matrix(d.crowd_density.astype(int), d.predicted_density.astype(int), labels=[0, 1, 2])
fig, ax = plt.subplots(figsize=(6.2, 5.8))
im = ax.imshow(cm, cmap="Blues", vmin=0, vmax=cm.max())
for i in range(3):
    for j in range(3):
        ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=14,
                color="white" if cm[i, j] > cm.max() * 0.55 else "black")
names = ["Low", "Medium", "High"]
ax.set_xticks(range(3)); ax.set_xticklabels(names, fontsize=12); ax.set_yticks(range(3)); ax.set_yticklabels(names, fontsize=12)
ax.set_xlabel("Predicted density", fontsize=13); ax.set_ylabel("Ground-truth density", fontsize=13)
ax.set_title(f"{TITLE}\nDensity Confusion Matrix", fontsize=14)
for s in ["top", "right", "left", "bottom"]: ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/gptZS_fig3_confusion.png", dpi=200); plt.close(fig)

# ---- fig4: class distribution, truth vs predicted (cf. Qwen's class-collapse figure) ----
true_share = d.crowd_density.value_counts(normalize=True).sort_index() * 100
pred_share = d.predicted_density.value_counts(normalize=True).sort_index() * 100
xx = np.arange(3); w = 0.38
fig, ax = plt.subplots(figsize=(7.4, 5.4))
b1 = ax.bar(xx - w / 2, true_share.values, w, color="#9AA5A6", label="Ground truth")
b2 = ax.bar(xx + w / 2, pred_share.values, w, color=GPT, label=f"{MODEL} prediction")
for bars in (b1, b2):
    for b in bars:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1, f"{b.get_height():.1f}%", ha="center", fontsize=11)
ax.set_xticks(xx); ax.set_xticklabels(labels, fontsize=12)
ax.set_ylabel("Share of the 1600 test images (%)", fontsize=13); ax.set_ylim(0, 100)
ax.set_title(f"{TITLE}\nDensity Class Distribution: Truth vs. Prediction", fontsize=14)
ax.legend(frameon=False); style(ax)
fig.tight_layout(); fig.savefig(f"{OUT}/gptZS_fig4_class_distribution.png", dpi=200); plt.close(fig)

# ---- copy the two CSVs next to the figures (same naming as the other models) ----
for f in ["gpt_experiment_A_zeroshot.csv", "gpt_experiment_A_zeroshot_evaluated.csv"]:
    shutil.copy2(f"{SRC}/{f}", f"{OUT}/{f}")
print("done:", sorted(os.listdir(OUT)))
