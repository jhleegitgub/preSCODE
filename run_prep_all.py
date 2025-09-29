import sys
import subprocess
from pathlib import Path

# --- Settings ---

# 1. Name of the target script to run
TARGET_SCRIPT = 'prep_scode_inputs_tf.py'

# 2. Base directory to work in (current location)
BASE_DIR = Path('.')

# --- Main Logic ---

# Check that the target script exists in the current folder
if not Path(TARGET_SCRIPT).is_file():
    print(f"❌ Error: Could not find script '{TARGET_SCRIPT}' in the current folder.")
    sys.exit()

# Find all folders starting with 'Phase'
phase_dirs = sorted([p for p in BASE_DIR.glob('Phase*') if p.is_dir()])

if not phase_dirs:
    print("❌ Could not find any folders starting with 'Phase*'.")
    sys.exit()

print(f"Running '{TARGET_SCRIPT}' for a total of {len(phase_dirs)} Phase folders...")
print("-" * 50)

# Iterate through each folder and perform the task
for p_dir in phase_dirs:
    dir_name = p_dir.name  # e.g., "Phase2_Ectoderm"
    print(f"▶️  Processing: {dir_name}")

    # Extract suffix from the folder name (e.g., "Ectoderm")
    try:
        suffix = dir_name.split('_', 1)[1]
    except IndexError:
        print(f"  ⚠️  Skipping: filename pattern not found in '{dir_name}'.")
        continue

    # --- Dynamically construct file paths for each script argument ---
    exp_csv_file = p_dir / f"{dir_name}_exp_sampled.csv"
    pseudotime_file = p_dir / f"{dir_name}_pse_sampled.txt"
    tf_list_file = p_dir / f"tf_list_{suffix}.txt"
    
    # Ensure output files are saved inside each Phase folder
    out_prefix = p_dir / f"{suffix}_TF"

    # Verify that all required input files exist
    if not all([f.exists() for f in [exp_csv_file, pseudotime_file, tf_list_file]]):
        print(f"  ❌ Skipping: one or more input files are missing.")
        # Optionally show which files are missing
        if not exp_csv_file.exists(): print(f"     - Missing: {exp_csv_file}")
        if not pseudotime_file.exists(): print(f"     - Missing: {pseudotime_file}")
        if not tf_list_file.exists(): print(f"     - Missing: {tf_list_file}")
        continue
        
    # --- Build and run the terminal command ---
    command = [
        "python3",
        TARGET_SCRIPT,
        "--exp-csv", str(exp_csv_file),
        "--pseudotime", str(pseudotime_file),
        "--tf-list", str(tf_list_file),
        "--out-prefix", str(out_prefix),
    ]

    try:
        # Execute the terminal command with subprocess.run
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True  # Raise an exception on non-zero return code
        )
        # On success, print the success messages from prep_scode_inputs_tf.py
        for line in result.stdout.strip().split('\n'):
            print(f"  {line}")

    except subprocess.CalledProcessError as e:
        # Error occurred while running TARGET_SCRIPT
        print(f"  ❌ Error while running '{TARGET_SCRIPT}':")
        print(e.stderr)  # Print the script's error message

print("-" * 50)
print("✅ All tasks completed.")