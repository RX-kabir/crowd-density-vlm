import os, shutil
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, recall_score

SRC = "D:/Downloads"
OUT = "D:/CrowdDensityResearch/phase5/gpt/Zero_Shot_Density"
OUT2 = "D:/CrowdDensityResearch/phase5/Results/gpt/Zero_Shot_Density"
GPT_B = "#E67E22"; GPT = "#2E75B6"; OLD = "#9AA5A6"
MODEL = "GPT-6.1 Terra"
TITLE = f"{MODEL} — Zero-Shot Experiment B, Density-Definition Prompt"

e = pd.read_csv(f"{SRC}/gpt_experiment_B_zeroshot_densitydef_evaluated.csv")
o = pd.read_csv(f"{SRC}/gpt_experiment_B_zeroshot_evaluated.csv")
lim = [0.5, 3e4]

def style(ax):
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)

# fig1: scatter
fig, ax = plt.subplots(figsize=(8, 8))
ax.scatter(e.total_count.clip(lower=0.5), e.predicted_count.clip(lower=0.5), s=18, alpha=0.35, color=GPT_B, edgecolors="none")
ax.plot(lim, lim, "k--", lw=1.2, label="Perfect prediction")
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lim); ax.set_ylim(lim)
ax.set_xlabel("Ground-truth count (log scale)", fontsize=13); ax.set_ylabel("Predicted count (log scale)", fontsize=13)
ax.set_title(f"{TITLE}\nPredicted vs. Ground-Truth Crowd Count", fontsize=14); ax.legend(loc="upper left", frameon=False); style(ax)
fig.tight_layout(); fig.savefig(f"{OUT}/gptDDB_fig1_scatter.png", dpi=200); plt.close(fig)

# fig2: confusion
cm = confusion_matrix(e.crowd_density.astype(int), e.predicted_density.astype(int), labels=[0, 1, 2])
fig, ax = plt.subplots(figsize=(6.2, 5.8))
ax.imshow(cm, cmap="Oranges", vmin=0, vmax=cm.max())
for i in range(3):
    for j in range(3):
        ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=14, color="white" if cm[i, j] > cm.max() * 0.55 else "black")
nm = ["Low", "Medium", "High"]
ax.set_xticks(range(3)); ax.set_xticklabels(nm, fontsize=12); ax.set_yticks(range(3)); ax.set_yticklabels(nm, fontsize=12)
ax.set_xlabel("Predicted density", fontsize=13); ax.set_ylabel("Ground-truth density", fontsize=13)
ax.set_title(f"{MODEL} — Zero-Shot B, Density-Definition Prompt\nDensity Confusion Matrix", fontsize=13)
for s in ["top", "right", "left", "bottom"]: ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/gptDDB_fig2_confusion.png", dpi=200); plt.close(fig)

# fig3: per-class recall, old vs new
def rec(df):
    return recall_score(df.crowd_density.astype(int), df.predicted_density.astype(int), average=None, labels=[0, 1, 2]) * 100
ro, rn = rec(o), rec(e)
x = np.arange(3); w = 0.36
fig, ax = plt.subplots(figsize=(8.4, 5.8))
b1 = ax.bar(x - w / 2, ro, w, color=OLD, label="Old prompt (bare labels)")
b2 = ax.bar(x + w / 2, rn, w, color=GPT_B, label="New prompt (with definitions)")
for bars in (b1, b2):
    for b in bars:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.2, f"{b.get_height():.1f}%", ha="center", fontsize=11)
ax.set_xticks(x); ax.set_xticklabels(nm, fontsize=12); ax.set_ylim(0, 112)
ax.set_ylabel("Recall (%)", fontsize=13); ax.set_xlabel("Ground-truth density class", fontsize=13)
ax.set_title(f"{MODEL} — Zero-Shot B: Per-Class Density Recall\nOld Prompt vs. Density-Definition Prompt", fontsize=14)
ax.legend(frameon=False, loc="upper left"); style(ax)
fig.tight_layout(); fig.savefig(f"{OUT}/gptDDB_fig3_recall_comparison.png", dpi=200); plt.close(fig)

# fig4: prediction vs the YOLO count (substitution)
y = e.yolo_predicted_count; p = e.predicted_count; echo = p == y
fig, ax = plt.subplots(figsize=(8, 8))
ax.scatter(y[~echo].clip(lower=0.5), p[~echo].clip(lower=0.5), s=16, alpha=0.3, color=GPT, edgecolors="none", label=f"Independent answer ({(~echo).sum()})")
ax.scatter(y[echo].clip(lower=0.5), p[echo].clip(lower=0.5), s=22, alpha=0.8, color=GPT_B, edgecolors="none", label=f"Exact echo of YOLO count ({echo.sum()}, {100 * echo.mean():.1f}%)")
ax.plot(lim, lim, "k--", lw=1.2, label="Prediction = YOLO count")
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lim); ax.set_ylim(lim)
ax.set_xlabel("YOLO count given in the prompt (log scale)", fontsize=13); ax.set_ylabel("GPT predicted count (log scale)", fontsize=13)
ax.set_title(f"{TITLE}\nPrediction vs. the YOLO Count in the Prompt\n(almost every answer is at or above the YOLO count)", fontsize=13)
ax.legend(loc="lower right", frameon=False); style(ax)
fig.tight_layout(); fig.savefig(f"{OUT}/gptDDB_fig4_substitution.png", dpi=200); plt.close(fig)

for f in ["gpt_experiment_B_zeroshot_densitydef.csv", "gpt_experiment_B_zeroshot_densitydef_evaluated.csv"]:
    shutil.copy2(f"{SRC}/{f}", f"{OUT}/{f}")
for f in os.listdir(OUT):
    if f.startswith(("gptDDB_fig", "gpt_experiment_B_zeroshot_densitydef")):
        shutil.copy2(f"{OUT}/{f}", f"{OUT2}/{f}")
print(sorted(os.listdir(OUT)))
