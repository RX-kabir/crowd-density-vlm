import numpy as np, pandas as pd
from scipy import stats
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

D = "D:/Downloads"
N = pd.read_csv(f"{D}/gpt_experiment_A_zeroshot_densitydef_evaluated.csv")   # new prompt (definition)
O = pd.read_csv(f"{D}/gpt_experiment_A_zeroshot_evaluated.csv")              # old prompt (bare labels)

def hdr(s): print("\n" + "=" * 8, s)

def cm_(df):
    v = df.dropna(subset=["predicted_count"]); err = v.predicted_count - v.total_count; nz = v.total_count > 0
    return dict(n=len(v), MAE=err.abs().mean(), RMSE=np.sqrt((err ** 2).mean()), MAPE=(err[nz].abs() / v.total_count[nz]).mean() * 100,
                pearson=stats.pearsonr(v.total_count, v.predicted_count)[0], spearman=stats.spearmanr(v.total_count, v.predicted_count)[0])

def dm_(df):
    d = df.dropna(subset=["predicted_density"]); y, p = d.crowd_density.astype(int), d.predicted_density.astype(int)
    return dict(n=len(d), acc=accuracy_score(y, p), prec=precision_score(y, p, average="weighted", zero_division=0),
                rec=recall_score(y, p, average="weighted", zero_division=0), f1=f1_score(y, p, average="weighted", zero_division=0),
                recall_cls=recall_score(y, p, average=None, labels=[0, 1, 2], zero_division=0).round(4))

hdr("NEW"); print(cm_(N)); print(dm_(N))
hdr("OLD"); print(cm_(O)); print(dm_(O))

hdr("RELIABILITY")
print(N.status.value_counts().to_dict(), N.incomplete.notna().sum(), N.error.notna().sum(), N.predicted_count.notna().sum(), N.predicted_density.notna().sum(), "longest", N.raw_response.str.len().max())
print(N.raw_response.str.replace(r"\d+", "N", regex=True).value_counts().head(5).to_dict())

hdr("DENSITY")
d = N.dropna(subset=["predicted_density"]); cm = confusion_matrix(d.crowd_density.astype(int), d.predicted_density.astype(int), labels=[0, 1, 2]); print(cm)
print("pred share new", (d.predicted_density.value_counts(normalize=True).sort_index() * 100).round(1).to_dict(), "old", (O.predicted_density.value_counts(normalize=True).sort_index() * 100).round(1).to_dict(), "true", (d.crowd_density.value_counts(normalize=True).sort_index() * 100).round(1).to_dict())
k = int((d.crowd_density == d.predicted_density).sum()); print("k", k, "binom vs always-High:", stats.binomtest(k, len(d), 0.6644, alternative="greater").pvalue)
print("sparser", int((d.predicted_density < d.crowd_density).sum()), "denser", int((d.predicted_density > d.crowd_density).sum()))
cmo = confusion_matrix(O.crowd_density.astype(int), O.predicted_density.astype(int), labels=[0, 1, 2]); print("old cm\n", cmo)

hdr("PAIRED NEW vs OLD")
Ni = N.set_index("test_filename"); Oi = O.set_index("test_filename").reindex(Ni.index)
okN = Ni.predicted_density == Ni.crowd_density; okO = Oi.predicted_density == Ni.crowd_density
b = int((okN & ~okO).sum()); c = int((~okN & okO).sum()); print("wrong->right", b, "right->wrong", c, "mcnemar p", stats.binomtest(b, b + c, .5).pvalue, "changed", int((Ni.predicted_density != Oi.predicted_density).sum()))
# transitions of changed predictions
ch = Ni[Ni.predicted_density != Oi.predicted_density]
print(pd.crosstab(Oi.predicted_density[ch.index], ch.predicted_density).to_string())
for t_ in [0, 1, 2]:
    mk = Ni.crowd_density == t_
    print("true", t_, "flips wrong->right", int((okN & ~okO & mk).sum()), "right->wrong", int((~okN & okO & mk).sum()))
aN = (Ni.predicted_count - Ni.total_count).abs(); aO = (Oi.predicted_count - Ni.total_count).abs()
print("MAE N/O", aN.mean(), aO.mean(), "wilcoxon", stats.wilcoxon(aN, aO).pvalue, "ttest", stats.ttest_rel(aN, aO).pvalue, "N better", int((aN < aO).sum()), "O better", int((aN > aO).sum()), "tie", int((aN == aO).sum()))
print("count preds differing", int((Ni.predicted_count != Oi.predicted_count).sum()), "corr of new/old preds spearman", stats.spearmanr(Ni.predicted_count, Oi.predicted_count)[0])
eN = Ni.predicted_count - Ni.total_count; eO = Oi.predicted_count - Ni.total_count; print("bias N/O", eN.mean(), eO.mean())

hdr("COUNT STRATA")
v = N.copy(); v["err"] = v.predicted_count - v.total_count
for k_ in [0, 1, 2]:
    g = v[v.crowd_density == k_]; print(k_, len(g), round(g.err.abs().mean(), 1), round(np.sqrt((g.err ** 2).mean()), 1), round(g.err.mean(), 1))
bins = [0, 10, 50, 100, 500, 1000, 1e9]; labs = ["0-10", "11-50", "51-100", "101-500", "501-1000", "1001+"]
v["band"] = pd.cut(v.total_count, bins, include_lowest=True, labels=labs)
print(v.groupby("band", observed=True).apply(lambda g: pd.Series(dict(n=len(g), mae=g.err.abs().mean(), bias=g.err.mean()))).round(1))
print("over", int((v.err > 0).sum()), "under", int((v.err < 0).sum()), "exact", int((v.err == 0).sum()), "medAE", v.err.abs().median(), "within10", ((v.err.abs() / v.total_count.clip(lower=1)) <= .1).mean() * 100)
worst = v.reindex(v.err.abs().sort_values(ascending=False).index); print("MAE w/o 5 worst", worst.iloc[5:].err.abs().mean())
print(worst[["test_filename", "total_count", "predicted_count", "err"]].head(8).to_string())
print("max pred", v.predicted_count.max(), ">10000", int((v.predicted_count > 10000).sum()))
for f in [3411, 4159, 814, 2203, 4056, 2542, 3334, 212]:
    r = N[N.test_filename == f].iloc[0]; o = O[O.test_filename == f].iloc[0]; print(f, "true", r.total_count, "new", r.predicted_count, "old", o.predicted_count)
bo = pd.DataFrame(dict(b=pd.cut(Ni.total_count, bins, include_lowest=True, labels=labs), n=eN, o=eO)); print(bo.groupby("b", observed=True).mean().round(1))
for k_ in [0, 1, 2]:
    mk = Ni.crowd_density == k_; print(k_, "MAE new/old", round(aN[mk].mean(), 1), round(aO[mk].mean(), 1))

hdr("TOKENS")
print("in", N.in_tok.mean(), "out", N.out_tok.mean(), "reason", N.reason_tok.mean(), N.reason_tok.median(), "max out", N.out_tok.max(), "totals", N.in_tok.sum(), N.out_tok.sum(), "cost", (N.in_tok.sum() + 5 * N.out_tok.sum()) / 1e6 * .5)
print("old in", O.in_tok.mean(), "reason", O.reason_tok.mean(), "wilcoxon reason", stats.wilcoxon(Ni.reason_tok, Oi.reason_tok).pvalue)
print("reason vs true", stats.spearmanr(N.reason_tok, N.total_count)[0], "vs abs err", stats.spearmanr(v.reason_tok, v.err.abs())[0], "by density", N.groupby("crowd_density").reason_tok.mean().round(0).to_dict(), "by predicted", N.groupby("predicted_density").reason_tok.mean().round(0).to_dict())
