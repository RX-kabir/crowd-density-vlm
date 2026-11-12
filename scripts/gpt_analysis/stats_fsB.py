import numpy as np, pandas as pd
from scipy import stats
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

P = "D:/CrowdDensityResearch/phase5"
IN = "D:/CrowdDensityResearch/Phase5_Input"
A = pd.read_csv("D:/Downloads/gpt_experiment_A_evaluated.csv")
B = pd.read_csv("D:/Downloads/gpt_experiment_B_evaluated.csv")
ZB = pd.read_csv("D:/Downloads/gpt_experiment_B_zeroshot_evaluated.csv")
sup = pd.read_csv(f"{IN}/support_mapping.csv")
yolo = pd.read_csv(f"{IN}/yolo_predictions.csv").rename(columns={"image_id": "test_filename", "predicted_count": "yolo"})

def hdr(s): print("\n" + "=" * 8, s)

def count_metrics(df):
    v = df.dropna(subset=["predicted_count"]); err = v.predicted_count - v.total_count; nz = v.total_count > 0
    return dict(n=len(v), MAE=err.abs().mean(), RMSE=np.sqrt((err ** 2).mean()), MAPE=(err[nz].abs() / v.total_count[nz]).mean() * 100,
                pearson=stats.pearsonr(v.total_count, v.predicted_count)[0], spearman=stats.spearmanr(v.total_count, v.predicted_count)[0])

def dens_metrics(df):
    d = df.dropna(subset=["predicted_density"]); y, p = d.crowd_density.astype(int), d.predicted_density.astype(int)
    return dict(n=len(d), acc=accuracy_score(y, p), prec=precision_score(y, p, average="weighted", zero_division=0),
                rec=recall_score(y, p, average="weighted", zero_division=0), f1=f1_score(y, p, average="weighted", zero_division=0),
                recall_cls=recall_score(y, p, average=None, labels=[0, 1, 2], zero_division=0).round(3))

hdr("HEADLINE B"); print(count_metrics(B)); print(dens_metrics(B))
hdr("HEADLINE A"); print(count_metrics(A)); print(dens_metrics(A))
hdr("ZS B"); print(count_metrics(ZB)); print(dens_metrics(ZB))
yv = B.merge(yolo, on="test_filename"); assert (yv.yolo == yv.yolo_predicted_count).all()
ye = (yv.yolo - yv.total_count)
print("YOLO baseline MAE/RMSE", ye.abs().mean(), np.sqrt((ye ** 2).mean()), "MAPE", (ye.abs()[yv.total_count > 0] / yv.total_count[yv.total_count > 0]).mean() * 100)

hdr("RELIABILITY B")
print(B.status.value_counts().to_dict(), B.incomplete.notna().sum(), B.error.notna().sum(), "longest", B.raw_response.str.len().max())
print(B.raw_response.str.replace(r"\d+", "N", regex=True).value_counts().head(5).to_dict())

hdr("YOLO SOURCE B")
p, y, t = B.predicted_count, B.yolo_predicted_count, B.total_count
ae = (p - t).abs()
echo = p == y
near = ((p - y).abs() <= 0.1 * y.clip(lower=1)) & ~echo
above = (p > 1.1 * y) ; below = (p < 0.9 * y)
print("exact", echo.sum(), echo.mean() * 100, "MAE", ae[echo].mean(), "bias", (p - t)[echo].mean())
print("near(<=10%)", near.sum(), "MAE", ae[near].mean())
print(">10% above", (above & ~echo).sum(), "MAE", ae[above & ~echo].mean(), "bias", (p - t)[above & ~echo].mean())
print(">10% below", below.sum(), "MAE", ae[below].mean())
print("pred >= yolo", (p >= y).sum(), (p >= y).mean() * 100, "pred<yolo", (p < y).sum())
r = (p / y.replace(0, np.nan)).dropna(); print("ratio median/q", r.median(), r.quantile(.25), r.quantile(.75))
print("echo rate by density", {k: round(echo[B.crowd_density == k].mean() * 100, 1) for k in [0, 1, 2]})
print("B closer to yolo than A:", (( B.predicted_count - B.yolo_predicted_count).abs().values < (A.set_index('test_filename').predicted_count.reindex(B.test_filename).values - B.yolo_predicted_count.values).__abs__()).mean() * 100)
print("yolo max", y.max(), "yolo==300", (y == 300).sum(), "true>300 among them", (t[y == 300] > 300).mean() * 100, "median true", t[y == 300].median())
m300 = y == 300
print("pred>300 among cap", (p[m300] > 300).mean() * 100, "echo 300", (p[m300] == 300).mean() * 100)
Aidx = A.set_index("test_filename"); aA = (Aidx.predicted_count.reindex(B.test_filename).values - t.values); aA = np.abs(aA)
print("cap MAE B/A/YOLO", ae[m300].mean(), aA[m300.values].mean(), (y - t).abs()[m300].mean())
print("non-cap MAE B/A/YOLO", ae[~m300].mean(), aA[~m300.values].mean(), (y - t).abs()[~m300].mean(), "cap share of B abs err", ae[m300].sum() / ae.sum() * 100)
z0 = y == 0; print("yolo zero", z0.sum(), "median pred", p[z0].median(), "max", p[z0].max(), "MAE", ae[z0].mean())
good = y >= 0.75 * t; bad = y < 0.25 * t
for nm, mk in [("yolo>=75% true", good), ("yolo<25% true", bad)]:
    print(nm, mk.sum(), "echo", echo[mk].mean() * 100, "MAE B", ae[mk].mean(), "MAE A", aA[mk.values].mean(), "MAE YOLO", (y - t).abs()[mk].mean())
print("yolo within 10% of truth?", ((y - t).abs() <= .1 * t.clip(lower=1)).sum())

hdr("SUPPORT ECHO B")
m = B.merge(sup, on="test_filename"); cc = [f"support{i}_count" for i in range(1, 6)]
se = m.apply(lambda r: r.predicted_count in [r[c] for c in cc], axis=1)
print("matches support count", se.sum(), se.mean() * 100, "excluding yolo echoes", (se & (m.predicted_count != m.yolo_predicted_count)).sum())

hdr("DENSITY B")
d = B.dropna(subset=["predicted_density"]); cm = confusion_matrix(d.crowd_density.astype(int), d.predicted_density.astype(int), labels=[0, 1, 2]); print(cm)
print("pred share", (d.predicted_density.value_counts(normalize=True).sort_index() * 100).round(1).to_dict())
k = int((d.crowd_density == d.predicted_density).sum()); print("binom", stats.binomtest(k, len(d), 0.6644, alternative="greater").pvalue)
print("sparser", int((d.predicted_density < d.crowd_density).sum()), "denser", int((d.predicted_density > d.crowd_density).sum()))

hdr("STRATA B")
v = B.copy(); v["err"] = v.predicted_count - v.total_count
for k_ in [0, 1, 2]:
    g = v[v.crowd_density == k_]; print(k_, len(g), round(g.err.abs().mean(), 1), round(np.sqrt((g.err ** 2).mean()), 1), round(g.err.mean(), 1))
bins = [0, 10, 50, 100, 500, 1000, 1e9]; labs = ["0-10", "11-50", "51-100", "101-500", "501-1000", "1001+"]
v["band"] = pd.cut(v.total_count, bins, include_lowest=True, labels=labs)
print(v.groupby("band", observed=True).apply(lambda g: pd.Series(dict(n=len(g), mae=g.err.abs().mean(), bias=g.err.mean()))).round(1))
print("over", int((v.err > 0).sum()), "under", int((v.err < 0).sum()), "exact", int((v.err == 0).sum()), "medAE", v.err.abs().median(), "within10", ((v.err.abs() / v.total_count.clip(lower=1)) <= .1).mean() * 100)
worst = v.reindex(v.err.abs().sort_values(ascending=False).index)
print("MAE w/o 5 worst", worst.iloc[5:].err.abs().mean())
print(worst[["test_filename", "total_count", "predicted_count", "yolo_predicted_count", "err"]].head(8).to_string())
print("max pred", v.predicted_count.max(), ">10000", int((v.predicted_count > 10000).sum()), "mult 1000", int(((v.predicted_count >= 1000) & (v.predicted_count % 1000 == 0)).sum()))
for f in [3411, 3178, 4159, 814, 2203, 1343, 3015, 2580, 3697]:
    r_ = B[B.test_filename == f].iloc[0]; a_ = A[A.test_filename == f].iloc[0]
    print(f, "true", r_.total_count, "yolo", r_.yolo_predicted_count, "B", r_.predicted_count, "A", a_.predicted_count)

hdr("A vs B PAIRED")
Bi = B.set_index("test_filename"); Ai = A.set_index("test_filename").reindex(Bi.index)
aB = (Bi.predicted_count - Bi.total_count).abs(); aAx = (Ai.predicted_count - Bi.total_count).abs()
print("MAE A/B", aAx.mean(), aB.mean(), "change %", (aB.mean() / aAx.mean() - 1) * 100, "RMSE change", )
eB = Bi.predicted_count - Bi.total_count; eA = Ai.predicted_count - Bi.total_count
print("RMSE A/B", np.sqrt((eA ** 2).mean()), np.sqrt((eB ** 2).mean()), "RMSE change %", (np.sqrt((eB ** 2).mean()) / np.sqrt((eA ** 2).mean()) - 1) * 100)
W = stats.wilcoxon(aB, aAx); print("wilcoxon", W.statistic, W.pvalue, "ttest", stats.ttest_rel(aB, aAx))
print("B better", int((aB < aAx).sum()), "A better", int((aB > aAx).sum()), "tie", int((aB == aAx).sum()))
print("bias A/B", eA.mean(), eB.mean())
for k_ in [0, 1, 2]:
    mk = Bi.crowd_density == k_; print(k_, "MAE A/B", round(aAx[mk].mean(), 1), round(aB[mk].mean(), 1), "RMSE A/B", round(np.sqrt((eA[mk] ** 2).mean()), 1), round(np.sqrt((eB[mk] ** 2).mean()), 1), "bias A/B", round(eA[mk].mean(), 1), round(eB[mk].mean(), 1))
tmp = pd.DataFrame(dict(b=pd.cut(Bi.total_count, bins, include_lowest=True, labels=labs), a=eA, bb=eB, y=Bi.yolo_predicted_count - Bi.total_count)); print(tmp.groupby("b", observed=True).mean().round(1))
print("over/under/exact A", int((eA > 0).sum()), int((eA < 0).sum()), int((eA == 0).sum()), "medAE A", aAx.median(), "within10 A", ((aAx / Bi.total_count.clip(lower=1)) <= .1).mean() * 100)
okB = Bi.predicted_density == Bi.crowd_density; okA = Ai.predicted_density == Bi.crowd_density
bb_ = int((okB & ~okA).sum()); cc_ = int((~okB & okA).sum()); print("density changed", int((Bi.predicted_density != Ai.predicted_density).sum()), "wrong->right", bb_, "right->wrong", cc_, "mcnemar", stats.binomtest(bb_, bb_ + cc_, .5).pvalue)
print("count preds differing", int((Bi.predicted_count != Ai.predicted_count).sum()))
print("recall A/B", dens_metrics(A)["recall_cls"], dens_metrics(B)["recall_cls"])
print("pred share A", (A.predicted_density.value_counts(normalize=True).sort_index() * 100).round(1).to_dict())
print("Medium->High A/B", int(((Ai.crowd_density == 1) & (Ai.predicted_density == 2)).sum()), int(((Bi.crowd_density == 1) & (Bi.predicted_density == 2)).sum()), "Low->Medium", int(((Ai.crowd_density == 0) & (Ai.predicted_density == 1)).sum()), int(((Bi.crowd_density == 0) & (Bi.predicted_density == 1)).sum()))
yy = (Bi.yolo_predicted_count - Bi.total_count).abs()
print("B vs YOLO closer", int((aB < yy).sum()), "YOLO closer", int((aB > yy).sum()), "tie", int((aB == yy).sum()), "wilcoxon", stats.wilcoxon(aB, yy).pvalue)
print("A vs YOLO closer", int((aAx < yy).sum()), int((aAx > yy).sum()))
print("B closer to yolo than A", (( (Bi.predicted_count - Bi.yolo_predicted_count).abs()) < ((Ai.predicted_count - Bi.yolo_predicted_count).abs())).mean() * 100)

hdr("TOKENS")
print("B in", B.in_tok.mean(), "out", B.out_tok.mean(), "reason", B.reason_tok.mean(), B.reason_tok.median(), "max out", B.out_tok.max(), "totals", B.in_tok.sum(), B.out_tok.sum(), "cost", (B.in_tok.sum() + 5 * B.out_tok.sum()) / 1e6 * .5)
print("A reason", A.reason_tok.mean(), "in", A.in_tok.mean(), "wilcoxon reason", stats.wilcoxon(B.set_index('test_filename').reason_tok, A.set_index('test_filename').reason_tok.reindex(Bi.index)).pvalue)
print("reason vs true", stats.spearmanr(B.reason_tok, B.total_count)[0], "vs abs err", stats.spearmanr(B.reason_tok, ae)[0], "by density", B.groupby("crowd_density").reason_tok.mean().round(0).to_dict())

hdr("VS ZERO-SHOT B and OPEN-SOURCE 5-SHOT B")
print("ZS B", count_metrics(ZB)["MAE"], dens_metrics(ZB)["acc"])
for name, path in [("Qwen", f"{P}/qwen/Five_Shot/qwen_experiment_B_evaluated.csv"), ("LLaVA", f"{P}/llava/Five_Shot/llava_experiment_B_evaluated.csv"), ("Gemma", f"{P}/gemma/Five_Shot/gemma_experiment_B_evaluated.csv")]:
    o = pd.read_csv(path)
    pc = [c for c in o.columns if "pred" in c and "count" in c and "yolo" not in c][0]; pdn = [c for c in o.columns if "pred" in c and "dens" in c][0]
    yc = [c for c in o.columns if "yolo" in c]
    o2 = o.rename(columns={pc: "predicted_count", pdn: "predicted_density"})
    cmx = count_metrics(o2); dm = dens_metrics(o2)
    ex = (o2.predicted_count == o2[yc[0]]).mean() * 100 if yc else None
    print(name, yc, {k_: (round(float(v_), 3) if not isinstance(v_, np.ndarray) else v_.tolist()) for k_, v_ in {**cmx, **dm}.items()}, "yolo echo %", ex)
