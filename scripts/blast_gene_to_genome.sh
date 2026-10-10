#!/usr/bin/env bash
# Align a query sequence (FASTA) against a genome with blastn.
# Usage: blast_gene_to_genome.sh <query.fasta> <genome.fasta>
# Writes BLAST tabular output (-outfmt 6) to stdout and progress messages to stderr.

in_gene="${1}"
in_genome="${2}"

MAKEBLASTDB_EXT=".ndb"

# Build the BLAST database only if it does not exist yet
if [ -f "${in_genome}${MAKEBLASTDB_EXT}" ]; then
	printf "Skipping makeblastdb step.\n" 1>&2
else
	printf "Running makeblastdb...\n" 1>&2
	makeblastdb -dbtype nucl -in "${in_genome}" 1>&2
fi

printf "Running blast of %s against %s\n" "${in_gene}" "${in_genome}" 1>&2

if ! blastn -query "${in_gene}" -db "${in_genome}" -outfmt 6; then
	printf "Blast failed.\n" 1>&2
	exit 1
fi

printf "Blast gene to genome finished.\n" 1>&2
exit 0
