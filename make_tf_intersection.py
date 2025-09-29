#!/usr/bin/env python3
import pandas as pd, re, argparse
from pathlib import Path

def norm(x: str):
    x = x.strip()
    if not x:
        return None
    x = x.split()[0]                 # drop trailing tokens after whitespace
    x = re.sub(r"\.\d+$", "", x)     # remove version suffixes like ".1", ".2"
    return x

def main():
    p = argparse.ArgumentParser(
        description="Create a TF intersection list from an expression CSV and a TF list."
    )
    p.add_argument("--exp-csv", required=True,
                   help="cells×genes CSV (first column = cell ID). Only the header row is read.")
    p.add_argument("--tf-list", required=True,
                   help="TF list file (one symbol per line).")
    p.add_argument("--out-file", required=True,
                   help="Output path for the intersection TF list (one per line).")
    p.add_argument("--gene-col-start", type=int, default=1,
                   help="Index of the first gene column in the CSV header (default 1 = skip cell ID).")
    args = p.parse_args()

    exp_path = Path(args.exp_csv)
    tf_path  = Path(args.tf_list)
    out_path = Path(args.out_file)

    # Ensure output directory exists
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Read only the header to get the set of gene symbols
    df = pd.read_csv(exp_path, nrows=1)
    cols = list(df.columns)
    if args.gene_col_start >= len(cols):
        raise SystemExit(f"gene_col_start({args.gene_col_start}) >= #columns({len(cols)})")
    genes = set(cols[args.gene_col_start:])

    # Normalize TF symbols and build a set
    raw = tf_path.read_text().splitlines()
    tfs = {g for g in (norm(l) for l in raw) if g}

    # Intersection
    inter = sorted(genes & tfs)

    # Save
    out_path.write_text("\n".join(inter) + "\n", encoding="utf-8")
    print(f"[OK] saved: {out_path}  (intersection {len(inter)} genes)")
    print(f"[info] exp: {exp_path}  tf_list: {tf_path}")

if __name__ == "__main__":
    main()