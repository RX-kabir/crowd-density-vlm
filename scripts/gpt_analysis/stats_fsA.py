import numpy as np, pandas as pd
from scipy import stats
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

P = "D:/CrowdDensityResearch/phase5"
e = pd.read_csv("D:/Downloads/gpt_experiment_A_evaluated.csv")
z = pd.read_csv("D:/Downloads/gpt_experiment_A_zeroshot_evaluated.csv")
sup = pd.read_csv(f"D:/CrowdDensityResearch/Phase5_Input/support_mapping.csv")
yolo = pd.read_csv(f"D:/CrowdDensityResearch/Phase5_Input/yolo_predictions.csv")
print("yolo cols", yolo.columns.tolist(), "sup cols", sup.columns.tolist()[:6])

def hdr(s): print("\n" + "=" * 8, s)

def count_metrics(df):
    v = df.dropna(subset=["predicted_count"])
    err = v.predicted_count - v.total_count
    nz = v.total_count > 0
    mape = (err[nz].abs() / v.total_count[nz]).mean() * 100
    return dict(n=len(v), MAE=err.abs().mean(), RMSE=np.sqrt((err ** 2).mean()), MAPE=mape,
                pearson=stats.pearsonr(v.total_count, v.predicted_count)[0], spearman=stats.spearmanr(v.total_count, v.predicted_count)[0])

def dens_metrics(df):
    d = df.dropna(subset=["predicted_density"])
    y, p = d.crowd_density.astype(int), d.predicted_density.astype(int)
    return dict(n=len(d), acc=accuracy_score(y, p), prec=precision_score(y, p, average="weighted", zero_division=0),
                rec=recall_score(y, p, average="weighted", zero_division=0), f1=f1_score(y, p, average="weighted", zero_division=0),
                recall_cls=recall_score(y, p, average=None, labels=[0, 1, 2], zero_division=0))

hdr("HEADLINE"); print(count_metrics(e)); print(dens_metrics(e))
hdr("ZERO-SHOT A (GPT)"); print(count_metrics(z)); print(dens_metrics(z))

hdr("RELIABILITY")
print(e.status.value_counts().to_dict(), e.incomplete.notna().sum(), e.error.notna().sum())
print("parsed", e.predicted_count.notna().sum(), e.predicted_density.notna().sum(), "longest", e.raw_response.str.len().max())
print("blank-line variant", e.raw_response.str.contains("\n\n").sum(), "single", (~e.raw_response.str.contains("\n\n")).sum())
print(e.raw_response.str.replace(r"\d+", "N", regex=True).value_counts().head(5))

hdr("SUPPORT ECHO")
m = e.merge(sup, left_on="test_filename", right_on="test_filename", how="left")
cnt_cols = [f"support{i}_count" for i in range(1, 6)]
print(cnt_cols, m[cnt_cols].isna().sum().sum())
echo = m.apply(lambda r: r.predicted_count in [r[c] for c in cnt_cols], axis=1)
print("matches any support count:", echo.sum(), echo.mean() * 100)
# chance rate: how often does the TRUE count equal a support count?
chance = m.apply(lambda r: r.total_count in [r[c] for c in cnt_cols], axis=1)
print("true count equals a support count:", chance.sum())
echo_non_small = m[(m.predicted_count > 20)].apply(lambda r: r.predicted_count in [r[c] for c in cnt_cols], axis=1)
print("echo among preds>20:", echo_non_small.sum(), len(echo_non_small))
print("echo rows sample:", m[echo][["test_filename", "predicted_count", "total_count"] + cnt_cols].head(8).to_string())
print("echo MAE", (m[echo].predicted_count - m[echo].total_count).abs().mean(), "non-echo", (m[~echo].predicted_count - m[~echo].total_count).abs().mean())
mean_sup = m[cnt_cols].mean(axis=1); print("corr pred vs mean support count", stats.spearmanr(m.predicted_count, mean_sup)[0], "true vs mean support", stats.spearmanr(m.total_count, mean_sup)[0])

hdr("DENSITY")
d = e.dropna(subset=["predicted_density"])
cm = confusion_matrix(d.crowd_density.astype(int), d.predicted_density.astype(int), labels=[0, 1, 2]); print(cm)
print("pred share", (d.predicted_density.value_counts(normalize=True).sort_index() * 100).round(1).to_dict(), "true share", (d.crowd_density.value_counts(normalize=True).sort_index() * 100).round(1).to_dict())
k = int((d.crowd_density == d.predicted_density).sum()); n = len(d)
print("binom vs 0.6644:", stats.binomtest(k, n, 0.6644, alternative="greater").pvalue, k, n)
# McNemar vs zero-shot A
zz = z.set_index("test_filename"); ee = e.set_index("test_filename")
ok5 = (ee.predicted_density == ee.crowd_density); ok0 = (zz.predicted_density.reindex(ee.index) == ee.crowd_density)
b = int((ok5 & ~ok0).sum()); c = int((~ok5 & ok0).sum()); print("McNemar 5shot-only-correct", b, "zeroshot-only-correct", c, "p", stats.binomtest(b, b + c, 0.5).pvalue)
print("directional: pred sparser than truth", int((d.predicted_density < d.crowd_density).sum()), "denser", int((d.predicted_density > d.crowd_density).sum()))

hdr("COUNT STRATA")
v = e.dropna(subset=["predicted_count"]).copy(); v["err"] = v.predicted_count - v.total_count
for k_ in [0, 1, 2]:
    g = v[v.crowd_density == k_]; print(k_, len(g), round(g.err.abs().mean(), 1), round(np.sqrt((g.err ** 2).mean()), 1), round(g.err.mean(), 1))
bins = [0, 10, 50, 100, 500, 1000, 1e9]; labs = ["0-10", "11-50", "51-100", "101-500", "501-1000", "1001+"]
v["band"] = pd.cut(v.total_count, bins, include_lowest=True, labels=labs)
print(v.groupby("band", observed=True).apply(lambda g: pd.Series(dict(n=len(g), mae=g.err.abs().mean(), bias=g.err.mean()))).round(1))
print("over", int((v.err > 0).sum()), "under", int((v.err < 0).sum()), "exact", int((v.err == 0).sum()), "median AE", v.err.abs().median(),
      "within10%", ((v.err.abs() / v.total_count.clip(lower=1)) <= 0.10).mean() * 100)
worst = v.reindex(v.err.abs().sort_values(ascending=False).index)
print("MAE w/o 5 worst", worst.iloc[5:].err.abs().mean())
print(worst[["test_filename", "total_count", "predicted_count", "err"]].head(8).to_string())
print("max pred", v.predicted_count.max(), ">10000:", int((v.predicted_count > 10000).sum()), "multiples of 1000 (>=1000):", int(((v.predicted_count >= 1000) & (v.predicted_count % 1000 == 0)).sum()))
print("round (mult of 10) share:", (v.predicted_count % 10 == 0).mean() * 100, "truth:", (v.total_count % 10 == 0).mean() * 100)

hdr("IMAGE 3411 and earlier-extreme images")
for f in [3411, 4056, 2542, 3334, 212, 2592, 4159, 2203, 2070, 814, 3178, 1510, 2354, 2580]:
    r = e[e.test_filename == f].iloc[0]; zr = z[z.test_filename == f].iloc[0]
    print(f, "true", r.total_count, "5shot", r.predicted_count, "0shot", zr.predicted_count)

hdr("VS ZERO-SHOT A (paired)")
a5 = (ee.predicted_count - ee.total_count).abs(); a0 = (zz.predicted_count.reindex(ee.index) - ee.total_count).abs()
print("MAE 5shot", a5.mean(), "0shot", a0.mean(), "wilcoxon", stats.wilcoxon(a5, a0).pvalue, "ttest", stats.ttest_rel(a5, a0).pvalue, "5shot better in", int((a5 < a0).sum()), "worse", int((a5 > a0).sum()))
e5 = ee.predicted_count - ee.total_count; e0 = zz.predicted_count.reindex(ee.index) - ee.total_count
print("bias 5shot", e5.mean(), "0shot", e0.mean())
for k_ in [0, 1, 2]:
    mk = ee.crowd_density == k_; print(k_, "mae 5/0", round(a5[mk].mean(), 1), round(a0[mk].mean(), 1), "bias", round(e5[mk].mean(), 1), round(e0[mk].mean(), 1))
v["band"] = pd.cut(v.total_count, bins, include_lowest=True, labels=labs)
tmp = pd.DataFrame(dict(b=pd.cut(ee.total_count, bins, include_lowest=True, labels=labs), e5=e5, e0=e0)); print(tmp.groupby("b", observed=True).mean().round(1))
print("recall 0shot", dens_metrics(z)["recall_cls"])

hdr("TOKENS / COST")
print("in mean", e.in_tok.mean(), "out", e.out_tok.mean(), "reason mean", e.reason_tok.mean(), "median", e.reason_tok.median(), "max out", e.out_tok.max())
print("totals", e.in_tok.sum(), e.out_tok.sum(), "cost", (e.in_tok.sum() * 1 + e.out_tok.sum() * 5) / 1e6 * 0.5)
print("reason vs true", stats.spearmanr(e.reason_tok, e.total_count)[0], "vs abs err", stats.spearmanr(e.reason_tok, e.err.abs() if "err" in e else v.err.abs())[0] if False else stats.spearmanr(v.reason_tok, v.err.abs())[0])
print("reason by density", e.groupby("crowd_density").reason_tok.mean().round(0).to_dict())
print("zero-shot A in_tok", z.in_tok.mean(), "reason", z.reason_tok.mean())

hdr("YOLO baseline")
y = yolo.rename(columns={"image_id": "test_filename"}) if "image_id" in yolo else yolo
print(y.columns.tolist())

hdr("OPEN-SOURCE 5-SHOT A")
for name, path in [("Qwen", f"{P}/qwen/Five_Shot/qwen_experiment_A_evaluated.csv"), ("LLaVA", f"{P}/llava/Five_Shot/llava_experiment_A_evaluated.csv"), ("Gemma", f"{P}/gemma/Five_Shot/gemma_experiment_A_evaluated.csv")]:
    o = pd.read_csv(path)
    pc = [c for c in o.columns if "pred" in c and "count" in c][0]; pdn = [c for c in o.columns if "pred" in c and "dens" in c][0]
    o2 = o.rename(columns={pc: "predicted_count", pdn: "predicted_density"})
    if "total_count" not in o2: print(name, o2.columns.tolist()); continue
    cmx = count_metrics(o2); dm = dens_metrics(o2)
    print(name, {k_: (round(v_, 3) if not isinstance(v_, np.ndarray) else v_.round(3)) for k_, v_ in {**cmx, **dm}.items()})
