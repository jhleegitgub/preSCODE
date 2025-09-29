import sys, subprocess
from pathlib import Path

TARGET_SCRIPT = "convert_A_to_edgelist.py"
BASE_DIR = Path(".")

if not Path(TARGET_SCRIPT).is_file():
    print(f"❌ '{TARGET_SCRIPT}' is not in the current folder."); sys.exit(1)

phase_dirs = sorted([p for p in BASE_DIR.glob("Phase*") if p.is_dir()])
if not phase_dirs:
    print("❌ No 'Phase*' folders found."); sys.exit(1)

print(f"Scanning a total of {len(phase_dirs)} Phase folders...\n" + "-"*50)

for p_dir in phase_dirs:
    print(f"▶️  Phase: {p_dir.name}")
    try:
        suffix = p_dir.name.split("_", 1)[1]
    except IndexError:
        print(f"  ⚠️  Failed to extract suffix from '{p_dir.name}' → skipping"); continue

    tf_list_file = p_dir / f"{suffix}_TF_gene_order.txt"
    out_dirs = sorted([d for d in p_dir.glob("out_*") if d.is_dir()])
    if not out_dirs:
        print(f"  - No out_* folders inside '{p_dir.name}'."); continue

    for out_dir in out_dirs:
        print(f"  ▶️  {out_dir.relative_to(p_dir)}")
        matrix_file = out_dir / "A.txt"                  # averageA is not used
        output_file = out_dir / "A_edge_list.tsv"
        ncol_file   = out_dir / "input.ncol"             # for NETCONTROL

        if not tf_list_file.exists() or not matrix_file.exists():
            print("    ❌ Missing input files:")
            if not tf_list_file.exists(): print(f"       - {tf_list_file}")
            if not matrix_file.exists():  print(f"       - {matrix_file}")
            continue

        cmd = [
            "python3", TARGET_SCRIPT,
            str(tf_list_file), str(matrix_file), str(output_file),
            "--quantile", "0.99",  #"--abs-threshold", "0.1",
            "--decimals", "6",
            "--ncol-file", str(ncol_file),
            "--ncol-unique",
        ]

        try:
            res = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"    ✅ Created: {output_file}, {ncol_file}")
        except subprocess.CalledProcessError as e:
            print("    ❌ Conversion failed:"); print(e.stderr)

print("-"*50); print("✅ All tasks completed.")