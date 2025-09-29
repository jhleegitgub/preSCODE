import pandas as pd, numpy as np, argparse, sys, pathlib

p = argparse.ArgumentParser()
p.add_argument("--exp-csv", required=True, help="cells×genes CSV (first column = cell ID)")
p.add_argument("--pseudotime", required=True, help="single-column pseudotime file")
p.add_argument("--tf-list", required=True, help="intersection TF list (one per line)")
p.add_argument("--out-prefix", default="scode_TF", help="output prefix")
a = p.parse_args()

exp = pd.read_csv(a.exp_csv, index_col=0).apply(pd.to_numeric, errors="coerce")  # cells×genes

tfs = [x.strip() for x in open(a.tf_list) if x.strip()]
keep = [g for g in exp.columns if g in set(tfs)]
if not keep:
    sys.exit("No intersection between the TF list and expression columns.")
exp_T = exp[keep].T
exp_T.index.to_series().to_csv(f"{a.out_prefix}_gene_order.txt", index=False, header=False)
exp_T.to_csv(f"{a.out_prefix}_exp_train.txt", sep="\t", header=False, index=False)

t = pd.read_csv(a.pseudotime, header=None, sep=r"\s+", engine="python")[0].astype(float).to_numpy()
pd.DataFrame({"cell": np.arange(len(t)), "t": t}).to_csv(
    f"{a.out_prefix}_time_train.txt", sep="\t", header=False, index=False
)

print(f"[OK] genes={exp_T.shape[0]} cells={exp_T.shape[1]}")
print(f"[OK] -> {a.out_prefix}_exp_train.txt, {a.out_prefix}_time_train.txt, {a.out_prefix}_gene_order.txt")
