#!/usr/bin/env bash
# Full pipeline: BLAST -> parse/filter/statistics (Python) -> plots (R)
# Usage: blast_pipeline.sh <query.fasta> <genome.fasta> <out_dir> <min_alignment_length> [min_pidentity] [max_evalue]
set -euo pipefail

if [ "$#" -lt 4 ]; then
	echo "Usage: $0 <query.fasta> <genome.fasta> <out_dir> <min_alignment_length> [min_pidentity=90] [max_evalue=0.01]" 1>&2
	exit 1
fi

in_gene="${1}"
in_genome="${2}"
out_dir="${3}"
min_len="${4}"
min_pident="${5:-90}"
max_evalue="${6:-0.01}"

BASEDIR="$(dirname "$(realpath "$0")")"

mkdir -p "${out_dir}/results/figures" "${out_dir}/logs"

# 1. BLAST
printf "[1/3] Running BLAST\n" 1>&2
"${BASEDIR}/blast_gene_to_genome.sh" "${in_gene}" "${in_genome}" \
	> "${out_dir}/results/blast_raw.tsv" \
	2> "${out_dir}/logs/blast.log"

# 2. Parse, filter and summarise the hits
printf "[2/3] Parsing BLAST results\n" 1>&2
python3 "${BASEDIR}/parsing_blast.py" \
	-i "${out_dir}/results/blast_raw.tsv" \
	-o "${out_dir}/results/blast_formatted.tsv" \
	-f "${out_dir}/results/blast_filtered.tsv" \
	-s "${out_dir}/results/blast_statistics.tsv" \
	-a "${min_len}" \
	-p "${min_pident}" \
	-e "${max_evalue}" \
	2> "${out_dir}/logs/parsing_blast.log"

# 3. Plots
printf "[3/3] Plotting\n" 1>&2
Rscript "${BASEDIR}/blast_visualizations.R" \
	-p "${out_dir}/results/blast_formatted.tsv" \
	-o "${out_dir}/results/figures/identity_histogram.png" \
	-s "${out_dir}/results/figures/identity_vs_length.png" \
	2> "${out_dir}/logs/blast_visualizations.log"

printf "Pipeline finished. Results in %s/results\n" "${out_dir}" 1>&2
