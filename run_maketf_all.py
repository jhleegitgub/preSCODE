#!/usr/bin/env python3
# run_tf_intersection_all.py  (simple output)
import sys, subprocess
from pathlib import Path

TARGET_SCRIPT = "make_tf_intersection.py"   # 같은 폴더에 있어야 함
BASE_DIR = Path(".")
TF_FILE = "../data/tf_list/GO_symbol_zebrafish_regulation_of_transcription+sequence-specific_DNA_binding_list.txt"

EXP_PATTERN = "{dir}_exp_sampled.csv"
OUT_PATTERN = "tf_list_{suffix}.txt"

def count_lines(p: Path) -> int:
    try:
        with p.open("r", encoding="utf-8") as fh:
            return sum(1 for _ in fh if _.strip())
    except Exception:
        return -1

# --- checks ---
if not Path(TARGET_SCRIPT).is_file():
    print(f"❌ '{TARGET_SCRIPT}' not found."); sys.exit(1)
tf_path = Path(TF_FILE)
if not tf_path.exists():
    print(f"❌ TF file not found: {tf_path}"); sys.exit(1)

phase_dirs = sorted([p for p in BASE_DIR.glob("Phase*") if p.is_dir()])
if not phase_dirs:
    print("❌ No 'Phase*' folders found."); sys.exit(1)

print(f"Processing a total of {len(phase_dirs)} Phase folders...")

# --- main ---
ok = 0
for p_dir in phase_dirs:
    dir_name = p_dir.name
    print(f"\nProcessing: {dir_name}")

    try:
        suffix = dir_name.split("_", 1)[1]
    except IndexError:
        print(f"  ⚠️  Skip (cannot extract suffix from '{dir_name}')")
        continue

    exp_file = p_dir / EXP_PATTERN.format(dir=dir_name)
    out_file = p_dir / OUT_PATTERN.format(suffix=suffix)

    if not exp_file.exists():
        print(f"  ❌ Missing input: {exp_file} → skip")
        continue

    cmd = [
        "python3", TARGET_SCRIPT,
        "--exp-csv", str(exp_file),
        "--tf-list", str(tf_path),
        "--out-file", str(out_file),
    ]

    try:
        # 자식 출력 숨기기
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True)
        n = count_lines(out_file)
        if n >= 0:
            print(f"  ✅ Saved: {out_file} (intersection size: {n})")
        else:
            print(f"  ✅ Saved: {out_file}")
        ok += 1
    except subprocess.CalledProcessError:
        print("  ❌ Failed to create intersection list")

print(f"\n----------------------------------------------")
print(f"Done: {ok}/{len(phase_dirs)} folder(s) processed.")