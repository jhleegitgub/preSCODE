#!/usr/bin/env python3
"""Convert SCODE output matrix A.txt into an edge list and optional .ncol file."""

from __future__ import annotations
import argparse
from pathlib import Path
from typing import List, Sequence, Tuple

def read_genes(tf_file: Path) -> List[str]:
    genes = []
    for line in tf_file.read_text().splitlines():
        g = line.strip()
        if g:
            genes.append(g)
    if not genes:
        raise ValueError(f"No genes found in {tf_file}")
    return genes

def read_matrix(matrix_file: Path) -> List[List[float]]:
    rows = []
    for line in matrix_file.read_text().splitlines():
        s = line.strip()
        if s:
            rows.append([float(x) for x in s.split()])
    if not rows:
        raise ValueError(f"No numeric rows found in {matrix_file}")
    return rows

def validate_matrix(matrix: Sequence[Sequence[float]], expected_size: int) -> None:
    if len(matrix) != expected_size:
        raise ValueError(
            f"Gene count ({expected_size}) does not match matrix row count ({len(matrix)})"
        )
    for i, row in enumerate(matrix):
        if len(row) != expected_size:
            raise ValueError(
                f"Row {i} in matrix has length {len(row)} but expected {expected_size}"
            )

def compute_quantile(values: Sequence[float], q: float) -> float:
    if not 0.0 <= q <= 1.0:
        raise ValueError("Quantile must be between 0 and 1")
    vals = sorted(values)
    if not vals:
        raise ValueError("Cannot compute quantile of empty sequence")
    if len(vals) == 1:
        return vals[0]
    pos = q * (len(vals) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(vals) - 1)
    frac = pos - lo
    return vals[lo] + (vals[hi] - vals[lo]) * frac

def determine_threshold(
    matrix: Sequence[Sequence[float]],
    absolute_threshold: float,
    quantile: float | None,
    exclude_diagonal: bool = True,
) -> float:
    if quantile is None:
        return max(absolute_threshold, 0.0)
    abs_vals = []
    for i, row in enumerate(matrix):
        for j, w in enumerate(row):
            if exclude_diagonal and i == j:
                continue
            abs_vals.append(abs(w))
    return max(compute_quantile(abs_vals, quantile), 0.0)

def collect_edges(
    genes: List[str],
    matrix: Sequence[Sequence[float]],
    threshold: float,
) -> List[Tuple[str, str, float]]:
    edges = []
    for tgt_i, tgt in enumerate(genes):
        weights = matrix[tgt_i]
        for src_i, src in enumerate(genes):
            if src_i == tgt_i:
                continue
            w = weights[src_i]
            if abs(w) < threshold:
                continue
            edges.append((src, tgt, w))  # directed src -> tgt
    return edges

def write_tsv(edges: List[Tuple[str, str, float]], output_file: Path, decimals: int) -> None:
    fmt = f"{{:.{decimals}f}}"
    with output_file.open("w", encoding="utf-8") as fh:
        fh.write("source\ttarget\tweight\n")
        for s, t, w in edges:
            fh.write(f"{s}\t{t}\t{fmt.format(w)}\n")

def write_ncol(edges: List[Tuple[str, str, float]], ncol_file: Path, unique: bool) -> None:
    if unique:
        seen = set()
        lines = []
        for s, t, _ in edges:
            key = (s, t)
            if key not in seen:
                seen.add(key)
                lines.append(f"{s} {t}\n")
    else:
        lines = [f"{s} {t}\n" for s, t, _ in edges]
    ncol_file.write_text("".join(lines), encoding="utf-8")

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Convert SCODE's A.txt to edge list / .ncol")
    p.add_argument("tf_file", type=Path, help="TF list in EXACT same order as A.txt")
    p.add_argument("matrix_file", type=Path, help="A.txt (GxG)")
    p.add_argument("output_file", type=Path, help="Edge list TSV path")
    p.add_argument("--abs-threshold", type=float, default=0.0,
                   help="Absolute |weight| threshold (default 0.0)")
    p.add_argument("--quantile", type=float,
                   help="Quantile (0–1) of |weight| as threshold (overrides abs)")
    p.add_argument("--decimals", type=int, default=10,
                   help="Decimal places for weights (default 10)")
    p.add_argument("--ncol-file", type=Path,
                   help="Also write NETCONTROL-compatible .ncol (source target)")
    p.add_argument("--ncol-unique", action="store_true",
                   help="Deduplicate identical directed edges in .ncol")
    return p

def main() -> None:
    args = build_parser().parse_args()
    genes = read_genes(args.tf_file)
    matrix = read_matrix(args.matrix_file)
    validate_matrix(matrix, len(genes))

    thr = determine_threshold(matrix, args.abs_threshold, args.quantile, exclude_diagonal=True)
    edges = collect_edges(genes, matrix, thr)

    write_tsv(edges, args.output_file, args.decimals)
    if args.ncol_file:
        write_ncol(edges, args.ncol_file, args.ncol_unique)

    print(f"[OK] genes={len(genes)}  edges_kept={len(edges)}  threshold={thr:.6g}")
    if args.ncol_file:
        print(f"[OK] wrote: {args.ncol_file}")

if __name__ == "__main__":
    main()