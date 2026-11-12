import numpy as np, pandas as pd
from scipy import stats
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

D = "D:/Downloads"; IN = "D:/CrowdDensityResearch/Phase5_Input"
NB = pd.read_csv(f"{D}/gpt_experiment_B_zeroshot_densitydef_evaluated.csv")   # new prompt, with YOLO
OB = pd.read_csv(f"{D}/gpt_experiment_B_zeroshot_evaluated.csv")              # old prompt, with YOLO
NA = pd.read_csv(f"{D}/gpt_experiment_A_zeroshot_densitydef_evaluated.csv")   # new prompt, no YOLO
OA = pd.read_csv(f"{D}/gpt_experiment_A_zeroshot_evaluated.csv")

def hdr(s): print("\n" + "=" * 8, s)
def cm_(df):
    v = df.dropna(subset=["predicted_count"]); err = v.predicted_count - v.total_count; nz = v.total_count > 0
    return dict(n=len(v), MAE=err.abs().mean(), RMSE=np.sqrt((err ** 2).mean()), MAPE=(err[nz].abs() / v.total_count[nz]).mean() * 100,
                pearson=stats.pearsonr(v.total_count, v.predicted_count)[0], spearman=stats.spearmanr(v.total_count, v.predicted_count)[0])
def dm_(df):
    d = df.dropna(subset=["predicted_density"]); y, p = d.crowd_density.astype(int), d.predicted_density.astype(int)
    return dict(acc=accuracy_score(y, p), prec=precision_score(y, p, average="weighted", zero_division=0), rec=recall_score(y, p, average="weighted", zero_division=0),
                f1=f1_score(y, p, average="weighted", zero_division=0), recall_cls=recall_score(y, p, average=None, labels=[0, 1, 2], zero_division=0).round(4))

hdr("NEW B"); print(cm_(NB)); print(dm_(NB))
hdr("OLD B"); print(cm_(OB)); print(dm_(OB))
hdr("NEW A"); print(cm_(NA)); print(dm_(NA))

hdr("YOLO baseline vs new B")
y = NB.yolo_predicted_count; t = NB.total_count; p = NB.predicted_count
ye = y - t; print("yolo MAE", ye.abs().mean(), np.sqrt((ye ** 2).mean()), (ye.abs()[t > 0] / t[t > 0]).mean() * 100)

hdr("RELIABILITY")
print(NB.status.value_counts().to_dict(), NB.incomplete.notna().sum(), NB.error.notna().sum(), "longest", NB.raw_response.str.len().max())
print(NB.raw_response.str.replace(r"\d+", "N", regex=True).value_counts().head(4).to_dict())

hdr("YOLO SOURCE new vs old")
def src(df, nm):
    p, y, t = df.predicted_count, df.yolo_predicted_count, df.total_count; ae = (p - t).abs(); echo = p == y
    r = (p / y.replace(0, np.nan)).dropna()
    print(nm, "exact", int(echo.sum()), round(echo.mean() * 100, 1), "MAE echo", round(ae[echo].mean(), 1), "within10 not exact", int((((p - y).abs() <= .1 * y.clip(lower=1)) & ~echo).sum()),
          ">=yolo", int((p >= y).sum()), round((p >= y).mean() * 100, 1), "median ratio", round(r.median(), 2), r.quantile(.25).round(2), r.quantile(.75).round(2),
          ">10% above", int((p > 1.1 * y).sum()), "<10% below", int((p < .9 * y).sum()))
    print("   echo by density", {k: round(echo[df.crowd_density == k].mean() * 100, 1) for k in [0, 1, 2]})
    m300 = y == 300
    print("   cap n", int(m300.sum()), "pred>300", round((p[m300] > 300).mean() * 100, 1), "echo300", round((p[m300] == 300).mean() * 100, 1), "MAE cap", round(ae[m300].mean(), 1), "non-cap", round(ae[~m300].mean(), 1), "cap share of abs err", round(ae[m300].sum() / ae.sum() * 100, 1))
    for nm2, mk in [("yolo>=75%", y >= .75 * t), ("yolo<25%", y < .25 * t)]:
        print("   ", nm2, int(mk.sum()), "echo", round(echo[mk].mean() * 100, 1), "MAE", round(ae[mk].mean(), 1))
    z0 = y == 0; print("   yolo zero", int(z0.sum()), "median pred", p[z0].median(), "max", p[z0].max(), "MAE", round(ae[z0].mean(), 1))
src(NB, "NEW"); src(OB, "OLD")
oi = OB.set_index("test_filename"); ni = NB.set_index("test_filename")
print("new closer to yolo than old", ((ni.predicted_count - ni.yolo_predicted_count).abs() < (oi.predicted_count.reindex(ni.index) - ni.yolo_predicted_count).abs()).mean() * 100)
print("support echo n/a")

hdr("DENSITY NEW B")
d = NB; cm = confusion_matrix(d.crowd_density.astype(int), d.predicted_density.astype(int), labels=[0, 1, 2]); print(cm)
print("pred share new", (d.predicted_density.value_counts(normalize=True).sort_index() * 100).round(1).to_dict(), "old", (OB.predicted_density.value_counts(normalize=True).sort_index() * 100).round(1).to_dict())
k = int((d.crowd_density == d.predicted_density).sum()); print("k", k, "binom", stats.binomtest(k, len(d), .6644, alternative="greater").pvalue)
print("sparser", int((d.predicted_density < d.crowd_density).sum()), "denser", int((d.predicted_density > d.crowd_density).sum()))
print("old cm\n", confusion_matrix(OB.crowd_density.astype(int), OB.predicted_density.astype(int), labels=[0, 1, 2]))

hdr("PAIRED NEW vs OLD (B)")
okN = ni.predicted_density == ni.crowd_density; okO = oi.predicted_density.reindex(ni.index) == ni.crowd_density
b = int((okN & ~okO).sum()); c = int((~okN & okO).sum()); print("wrong->right", b, "right->wrong", c, "mcnemar", stats.binomtest(b, b + c, .5).pvalue, "changed", int((ni.predicted_density != oi.predicted_density.reindex(ni.index)).sum()))
ch = ni[ni.predicted_density != oi.predicted_density.reindex(ni.index)]; print(pd.crosstab(oi.predicted_density.reindex(ni.index)[ch.index], ch.predicted_density).to_string())
for t_ in [0, 1, 2]:
    mk = ni.crowd_density == t_; print("true", t_, "w->r", int((okN & ~okO & mk).sum()), "r->w", int((~okN & okO & mk).sum()))
aN = (ni.predicted_count - ni.total_count).abs(); aO = (oi.predicted_count.reindex(ni.index) - ni.total_count).abs()
print("MAE N/O", aN.mean(), aO.mean(), "wilcoxon", stats.wilcoxon(aN, aO).pvalue, "ttest", stats.ttest_rel(aN, aO).pvalue, "N better", int((aN < aO).sum()), "O better", int((aN > aO).sum()), "tie", int((aN == aO).sum()))
print("count differ", int((ni.predicted_count != oi.predicted_count.reindex(ni.index)).sum()), "spearman", stats.spearmanr(ni.predicted_count, oi.predicted_count.reindex(ni.index))[0])
eN = ni.predicted_count - ni.total_count; eO = oi.predicted_count.reindex(ni.index) - ni.total_count; print("bias N/O", eN.mean(), eO.mean())

hdr("DD A vs DD B (new prompt)")
nai = NA.set_index("test_filename").reindex(ni.index); aA = (nai.predicted_count - ni.total_count).abs()
print("MAE A/B", aA.mean(), aN.mean(), "change %", (aN.mean() / aA.mean() - 1) * 100, "RMSE change %", (np.sqrt(((ni.predicted_count - ni.total_count) ** 2).mean()) / np.sqrt(((nai.predicted_count - ni.total_count) ** 2).mean()) - 1) * 100)
W = stats.wilcoxon(aN, aA); print("wilcoxon", W.statistic, W.pvalue, "ttest", stats.ttest_rel(aN, aA), "B better", int((aN < aA).sum()), "A better", int((aN > aA).sum()), "tie", int((aN == aA).sum()))
okA = nai.predicted_density == ni.crowd_density; bb = int((okN & ~okA).sum()); cc = int((~okN & okA).sum()); print("density A->B w->r", bb, "r->w", cc, "p", stats.binomtest(bb, bb + cc, .5).pvalue, "changed", int((ni.predicted_density != nai.predicted_density).sum()))
print("old A vs old B MAE / wilcoxon", (OA.set_index("test_filename").reindex(ni.index).predicted_count - ni.total_count).abs().mean())

hdr("STRATA")
v = NB.copy(); v["err"] = v.predicted_count - v.total_count
for k_ in [0, 1, 2]:
    g = v[v.crowd_density == k_]; print(k_, len(g), round(g.err.abs().mean(), 1), round(np.sqrt((g.err ** 2).mean()), 1), round(g.err.mean(), 1))
for k_ in [0, 1, 2]:
    g = OB[OB.crowd_density == k_]; print("old", k_, round((g.predicted_count - g.total_count).abs().mean(), 1), round((g.predicted_count - g.total_count).mean(), 1))
bins = [0, 10, 50, 100, 500, 1000, 1e9]; labs = ["0-10", "11-50", "51-100", "101-500", "501-1000", "1001+"]
v["band"] = pd.cut(v.total_count, bins, include_lowest=True, labels=labs)
print(v.groupby("band", observed=True).apply(lambda g: pd.Series(dict(n=len(g), mae=g.err.abs().mean(), bias=g.err.mean()))).round(1))
print("over", int((v.err > 0).sum()), "under", int((v.err < 0).sum()), "exact", int((v.err == 0).sum()), "medAE", v.err.abs().median(), "within10", ((v.err.abs() / v.total_count.clip(lower=1)) <= .1).mean() * 100)
worst = v.reindex(v.err.abs().sort_values(ascending=False).index); print("MAE w/o 5 worst", worst.iloc[5:].err.abs().mean())
print(worst[["test_filename", "total_count", "predicted_count", "yolo_predicted_count", "err"]].head(8).to_string())
print("max pred", v.predicted_count.max(), ">10000", int((v.predicted_count > 10000).sum()))
for f in [3411, 3178, 4159, 814, 2203, 3539]:
    r = NB[NB.test_filename == f].iloc[0]; o = OB[OB.test_filename == f].iloc[0]; print(f, "true", r.total_count, "yolo", r.yolo_predicted_count, "new", r.predicted_count, "old", o.predicted_count)
print("pearson/spearman", cm_(NB)["pearson"], cm_(NB)["spearman"])

hdr("TOKENS")
print("in", NB.in_tok.mean(), "out", NB.out_tok.mean(), "reason", NB.reason_tok.mean(), NB.reason_tok.median(), "max out", NB.out_tok.max(), "totals", NB.in_tok.sum(), NB.out_tok.sum(), "cost", (NB.in_tok.sum() + 5 * NB.out_tok.sum()) / 1e6 * .5)
print("old in", OB.in_tok.mean(), "reason", OB.reason_tok.mean(), "wilcoxon", stats.wilcoxon(ni.reason_tok, oi.reason_tok.reindex(ni.index)).pvalue, "vs A new reason", NA.reason_tok.mean())
print("reason vs true", stats.spearmanr(NB.reason_tok, NB.total_count)[0], "vs abs err", stats.spearmanr(v.reason_tok, v.err.abs())[0], "by density", NB.groupby("crowd_density").reason_tok.mean().round(0).to_dict())
