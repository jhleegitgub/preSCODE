# Run SCODE and netctrl end-to-end: build inputs, infer GRN (A), and compute driver nodes. 

# Versions used in our run 
# - Python 3.10.12 
# - R 4.3.x (SCODE) 
# - ruby 3.2.x # - netctrl 0.2.0 / igraph 0.10.x 

# ---------- 1) Prepare SCODE inputs ---------- 
# Build TF intersection lists per Phase* folder 
python3 run_tf_intersection.py 
# Output per PhaseX_*: tf_list_<Suffix>.txt 

# Build SCODE training inputs (requires prep_scode_inputs_tf.py in the same folder) 
python3 run_prep_all.py 
# Outputs (per Phase folder): 
# exp_train.txt : matrix (G×C) after selecting TFs and transposing → genes×cells, tab-delimited, NO header 
# time_train.txt : two columns (cell_index, pseudotime) — pseudotime should be scaled to [0,1] 
# gene_order.txt : row (gene) order of exp_train to keep consistent mapping downstream 


# ---------- 2) Run SCODE ---------- 
Rscript SCODE.R <exp_train> <time_train> <out_dir> <G> <D> <C> <I> 
# Parameters: 
# G = number of TFs
# C = number of cells (count directly from exp_train file) 
# D = latent dimension (DEFAULT: 4 per SCODE paper; optionally verify via test RSS)
# I = iterations (start at 100; increase until test RSS no longer improves, then keep it

# SCODE outputs in <out_dir>: 
# A.txt (G×G) # B.txt (D×D) 
# W.txt (G×D) # RSS.txt (single number) 

# ---------- 2a) (Recommended) Multiple runs for stability ---------- 
# The authors recommend running SCODE multiple times and averaging A → meanA.txt 
ruby run_R.rb <Input1> <Input2> <OutDir> <G> <D> <C> <I> <R> 
# where R = number of repeats (e.g., 20–50).


# ---------- 3) Convert A.txt → edge list / .ncol ---------- 
# Batch-convert across all Phase* folders (requires convert_A_to_edgelist.py) 
python3 run_convert_all.py 
# Outputs per out_* folder: 
# A_edge_list.tsv : columns (source, target, weight), self-loops removed, weight sign preserved 
# input.ncol : "source target" pairs for netctrl (directed topology only) 

# Notes on thresholds: 
# --quantile q : |A| quantile cut (scale-invariant). Higher q → sparser graph. 
# --abs-threshold t : fixed absolute cut |A| ≥ t (scale-dependent). 

# ---------- 4) Run netctrl (driver nodes) ---------- 
# Run inside the SCODE result directory (e.g., out_d5_i500) 
# Liu mode uses only directed topology; weights/signs are not used in driver counts. 
netctrl -m liu -o liu.driver input.ncol 

# ==================== END ====================
