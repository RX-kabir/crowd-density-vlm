import os, shutil
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix

SRC = "D:/Downloads"
OUT = "D:/CrowdDensityResearch/phase5/gpt/Five_Shot"
OUT2 = "D:/CrowdDensityResearch/phase5/Results/gpt/Five_Shot"
GPT_A, GPT_B = "#2E75B6", "#E67E22"
MODEL = "GPT-6.1 Terra"

A = pd.read_csv(f"{SRC}/gpt_experiment_A_evaluated.csv")
B = pd.read_csv(f"{SRC}/gpt_experiment_B_evaluated.csv")
lim = [0.5, 3e4]

def style(ax):
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)

def mae_by(df):
    return [(df[df.crowd_density == k].predicted_count - df[df.crowd_density == k].total_count).abs().mean() for k in [0, 1, 2]]

def cm_of(df):
    return confusion_matrix(df.crowd_density.astype(int), df.predicted_density.astype(int), labels=[0, 1, 2])

names = ["Low", "Medium", "High"]

# ================= B only =================
TB = f"{MODEL} — 5-Shot Experiment B"
fig, ax = plt.subplots(figsize=(8, 8))
ax.scatter(B.total_count.clip(lower=0.5), B.predicted_count.clip(lower=0.5), s=18, alpha=0.35, color=GPT_B, edgecolors="none")
ax.plot(lim, lim, "k--", lw=1.2, label="Perfect prediction")
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lim); ax.set_ylim(lim)
ax.set_xlabel("Ground-truth count (log scale)", fontsize=13); ax.set_ylabel("Predicted count (log scale)", fontsize=13)
ax.set_title(f"{TB}\nPredicted vs. Ground-Truth Crowd Count", fontsize=15); ax.legend(loc="upper left", frameon=False); style(ax)
fig.tight_layout(); fig.savefig(f"{OUT}/gptB_fig1_scatter.png", dpi=200); plt.close(fig)

mb = mae_by(B)
fig, ax = plt.subplots(figsize=(7, 5.4))
bars = ax.bar(["Low (0)", "Medium (1)", "High (2)"], mb, color=GPT_B, width=0.6)
for b, m in zip(bars, mb):
    ax.text(b.get_x() + b.get_width() / 2, m + max(mb) * 0.015, f"{m:.0f}", ha="center", fontsize=12)
ax.set_ylabel("Mean Absolute Error (MAE)", fontsize=13); ax.set_xlabel("Ground-truth crowd density class", fontsize=13)
ax.set_title(f"{TB}\nCounting MAE by Density Class", fontsize=14); ax.set_ylim(0, max(mb) * 1.1); style(ax)
fig.tight_layout(); fig.savefig(f"{OUT}/gptB_fig2_mae_by_density.png", dpi=200); plt.close(fig)

cm = cm_of(B)
fig, ax = plt.subplots(figsize=(6.2, 5.8))
ax.imshow(cm, cmap="Oranges", vmin=0, vmax=cm.max())
for i in range(3):
    for j in range(3):
        ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=14, color="white" if cm[i, j] > cm.max() * 0.55 else "black")
ax.set_xticks(range(3)); ax.set_xticklabels(names, fontsize=12); ax.set_yticks(range(3)); ax.set_yticklabels(names, fontsize=12)
ax.set_xlabel("Predicted density", fontsize=13); ax.set_ylabel("Ground-truth density", fontsize=13)
ax.set_title(f"{TB}\nDensity Confusion Matrix", fontsize=14)
for s in ["top", "right", "left", "bottom"]: ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/gptB_fig3_confusion.png", dpi=200); plt.close(fig)

y = B.yolo_predicted_count; p = B.predicted_count; echo = p == y
fig, ax = plt.subplots(figsize=(8, 8))
ax.scatter(y[~echo].clip(lower=0.5), p[~echo].clip(lower=0.5), s=16, alpha=0.3, color=GPT_A, edgecolors="none", label=f"Independent answer ({(~echo).sum()})")
ax.scatter(y[echo].clip(lower=0.5), p[echo].clip(lower=0.5), s=22, alpha=0.8, color=GPT_B, edgecolors="none", label=f"Exact echo of YOLO count ({echo.sum()}, {100 * echo.mean():.1f}%)")
ax.plot(lim, lim, "k--", lw=1.2, label="Prediction = YOLO count")
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lim); ax.set_ylim(lim)
ax.set_xlabel("YOLO count given in the prompt (log scale)", fontsize=13); ax.set_ylabel("GPT predicted count (log scale)", fontsize=13)
ax.set_title(f"{TB}\nPrediction vs. the YOLO Count in the Prompt\n(almost every answer is at or above the YOLO count)", fontsize=14)
ax.legend(loc="lower right", frameon=False); style(ax)
fig.tight_layout(); fig.savefig(f"{OUT}/gptB_fig4_yolo_vs_prediction.png", dpi=200); plt.close(fig)

# ================= A vs B =================
fig, axes = plt.subplots(1, 2, figsize=(14, 6.2), sharey=True)
for ax, df, col, ttl in [(axes[0], A, GPT_A, "Experiment A (5-shot, no YOLO)"), (axes[1], B, GPT_B, "Experiment B (5-shot, with YOLO)")]:
    ax.scatter(df.total_count.clip(lower=0.5), df.predicted_count.clip(lower=0.5), s=16, alpha=0.35, color=col, edgecolors="none")
    ax.plot(lim, lim, "k--", lw=1.2, label="Perfect prediction")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lim); ax.set_ylim(lim)
    ax.set_xlabel("Ground-truth count (log scale)", fontsize=13); ax.set_title(ttl, fontsize=13); ax.legend(loc="upper left", frameon=False); style(ax)
axes[0].set_ylabel("Predicted count (log scale)", fontsize=13)
fig.suptitle(f"{MODEL} — 5-Shot: Predicted vs. Ground-Truth Count, A vs. B", fontsize=15)
fig.tight_layout(rect=[0, 0, 1, 0.95]); fig.savefig(f"{OUT}/gptAB_fig1_scatter.png", dpi=200); plt.close(fig)

ma, mb = mae_by(A), mae_by(B)
x = np.arange(3); w = 0.36
fig, ax = plt.subplots(figsize=(9, 6))
b1 = ax.bar(x - w / 2, ma, w, color=GPT_A, label="Experiment A (5-shot)")
b2 = ax.bar(x + w / 2, mb, w, color=GPT_B, label="Experiment B (5-shot)")
for bars in (b1, b2):
    for b in bars:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + max(ma + mb) * 0.012, f"{b.get_height():.0f}", ha="center", fontsize=11)
ax.set_xticks(x); ax.set_xticklabels(["Low (0)", "Medium (1)", "High (2)"], fontsize=12)
ax.set_xlabel("Ground-truth crowd density class", fontsize=13); ax.set_ylabel("Mean Absolute Error (MAE)", fontsize=13)
ax.set_title(f"{MODEL} 5-Shot — Counting MAE by Density, A vs. B", fontsize=14); ax.legend(frameon=False, loc="upper left"); style(ax)
fig.tight_layout(); fig.savefig(f"{OUT}/gptAB_fig2_mae_by_density.png", dpi=200); plt.close(fig)

fig, axes = plt.subplots(1, 2, figsize=(13, 6))
for ax, df, cmap, ttl in [(axes[0], A, "Blues", "Experiment A (5-shot)"), (axes[1], B, "Oranges", "Experiment B (5-shot)")]:
    cm = cm_of(df); ax.imshow(cm, cmap=cmap, vmin=0, vmax=cm.max())
    for i in range(3):
        for j in range(3):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=14, color="white" if cm[i, j] > cm.max() * 0.55 else "black")
    ax.set_xticks(range(3)); ax.set_xticklabels(names, fontsize=12); ax.set_yticks(range(3)); ax.set_yticklabels(names, fontsize=12)
    ax.set_xlabel("Predicted density", fontsize=13); ax.set_ylabel("Ground-truth density", fontsize=13); ax.set_title(ttl, fontsize=12)
    for s in ["top", "right", "left", "bottom"]: ax.spines[s].set_visible(False)
fig.suptitle(f"{MODEL} — 5-Shot Density Confusion Matrices, A vs. B\n(the YOLO count does not change the density classification)", fontsize=14)
fig.tight_layout(rect=[0, 0, 1, 0.9]); fig.savefig(f"{OUT}/gptAB_fig3_confusion.png", dpi=200); plt.close(fig)

bins = [0, 10, 50, 100, 500, 1000, 10000]; labs = ["0-10", "11-50", "51-100", "101-500", "501-1k", "1k+"]
def bias_by(pred, truth):
    t = pd.DataFrame(dict(b=pd.cut(truth, bins, include_lowest=True, labels=labs), e=pred - truth))
    return np.array([t[t.b == l].e.mean() for l in labs])
ba, bb = bias_by(A.predicted_count, A.total_count), bias_by(B.predicted_count, B.total_count)
by = bias_by(B.yolo_predicted_count, B.total_count)
x = np.arange(len(labs)); w = 0.27
fig, ax = plt.subplots(figsize=(10.5, 6))
ax.bar(x - w, ba, w, color=GPT_A, label="Experiment A (no YOLO)")
ax.bar(x, bb, w, color=GPT_B, label="Experiment B (with YOLO)")
ax.bar(x + w, by, w, color="#7F8C8D", label="YOLO count itself")
ax.axhline(0, color="k", lw=0.8); ax.set_yscale("symlog", linthresh=100)
ax.set_xticks(x); ax.set_xticklabels(labs, fontsize=12)
ax.set_xlabel("Ground-truth count band", fontsize=13); ax.set_ylabel("Mean signed error (predicted - true), symlog scale", fontsize=12)
ax.set_title(f"{MODEL} 5-Shot — Counting Bias by Crowd Size\n(A over-counts dense scenes; B swings to under-counting; YOLO under-counts most)", fontsize=14)
ax.legend(frameon=False, loc="lower left"); style(ax)
fig.tight_layout(); fig.savefig(f"{OUT}/gptAB_fig4_bias_by_count.png", dpi=200); plt.close(fig)

for f in ["gpt_experiment_B.csv", "gpt_experiment_B_evaluated.csv"]:
    shutil.copy2(f"{SRC}/{f}", f"{OUT}/{f}")
for f in os.listdir(OUT):
    if f.startswith(("gptB_fig", "gptAB_fig", "gpt_experiment_B")):
        shutil.copy2(f"{OUT}/{f}", f"{OUT2}/{f}")
print(sorted(os.listdir(OUT)))
