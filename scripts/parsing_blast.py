#!/usr/bin/env python3
"""
Read, format, filter and summarise BLAST tabular output (-outfmt 6).

Outputs:
  - formatted table with column headers
  - filtered table (alignment length, percent identity and e-value thresholds)
  - per-query summary statistics (number of hits, subjects, min/max/mean of numeric fields)
  - optional human-readable text report (-t)
"""

import sys
import argparse

HEADERS = [
    "query_id", "subject_id", "pidentity", "alignment_length",
    "mismatches", "gap_opens", "q_start", "q_end",
    "s_start", "s_end", "e_value", "bitscore",
]
STR_FIELDS = {"query_id", "subject_id"}
FLOAT_FIELDS = {"pidentity", "e_value", "bitscore"}
SUMMARY_FIELDS = ["pidentity", "alignment_length", "e_value", "bitscore"]


def read_blast(filename):
    """Read a BLAST outfmt 6 file and return one dict per hit with typed values."""
    hits = []
    with open(filename) as f:
        for line_number, line in enumerate(f, start=1):
            fields = line.rstrip("\n").split("\t")
            if len(fields) != len(HEADERS):
                print(f"Skipping malformed line {line_number}: {line.strip()[:60]}", file=sys.stderr)
                continue
            hit = {}
            for key, value in zip(HEADERS, fields):
                if key in STR_FIELDS:
                    hit[key] = value
                elif key in FLOAT_FIELDS:
                    hit[key] = float(value)
                else:
                    hit[key] = int(value)
            hits.append(hit)
    if not hits:
        sys.exit(f"No valid BLAST hits found in {filename}")
    return hits


def write_table(hits, outfile):
    """Write hits as a tab-separated table with a header line."""
    with open(outfile, "w") as out:
        out.write("\t".join(HEADERS) + "\n")
        for hit in hits:
            row = []
            for key in HEADERS:
                value = hit[key]
                if key == "e_value":
                    row.append(f"{value:.2e}")
                elif key in FLOAT_FIELDS:
                    row.append(f"{value:.2f}")
                else:
                    row.append(str(value))
            out.write("\t".join(row) + "\n")


def compute_stats(hits, outfile, outtxt=None):
    """
    Compute, for each query: number of hits, number of distinct subjects and
    min/max/mean of percent identity, alignment length, e-value and bitscore.
    Writes a TSV table and, optionally, a readable text report. Returns the summary dict.
    """
    summary = {}
    for hit in hits:
        q = summary.setdefault(hit["query_id"], {
            "number_of_hits": 0,
            "subjects": {},
            "values": {field: [] for field in SUMMARY_FIELDS},
        })
        q["number_of_hits"] += 1
        q["subjects"][hit["subject_id"]] = q["subjects"].get(hit["subject_id"], 0) + 1
        for field in SUMMARY_FIELDS:
            q["values"][field].append(hit[field])

    for q in summary.values():
        q["stats"] = {
            field: {"min": min(v), "max": max(v), "mean": sum(v) / len(v)}
            for field, v in q["values"].items()
        }

    header = ["query_id", "num_hits", "num_subjects"]
    for field in SUMMARY_FIELDS:
        header += [f"{field}_min", f"{field}_max", f"{field}_mean"]

    with open(outfile, "w") as out:
        out.write("\t".join(header) + "\n")
        for query_id, q in summary.items():
            row = [query_id, str(q["number_of_hits"]), str(len(q["subjects"]))]
            for field in SUMMARY_FIELDS:
                fmt = "{:.2e}" if field == "e_value" else "{:.2f}"
                row += [fmt.format(q["stats"][field][s]) for s in ("min", "max", "mean")]
            out.write("\t".join(row) + "\n")

    if outtxt is not None:
        with open(outtxt, "w") as out:
            for query_id, q in summary.items():
                out.write(f"{query_id}:\n")
                out.write(f"\tnumber_of_hits: {q['number_of_hits']}\n")
                out.write("\tsubjects:\n")
                for subject, count in q["subjects"].items():
                    out.write(f"\t\t{subject}: {count}\n")
                out.write("\tnumeric_fields:\n")
                for field, stats in q["stats"].items():
                    fmt = "{:.2e}" if field == "e_value" else "{:.2f}"
                    out.write(f"\t\t{field}: " + ", ".join(f"{k}={fmt.format(v)}" for k, v in stats.items()) + "\n")
                out.write("\n")

    return summary


def filter_hits(hits, min_length, min_pident=90.0, max_evalue=0.01):
    """Keep hits with alignment_length >= min_length, pidentity > min_pident and e_value <= max_evalue."""
    return [
        hit for hit in hits
        if hit["alignment_length"] >= min_length
        and hit["pidentity"] > min_pident
        and hit["e_value"] <= max_evalue
    ]


def main():
    parser = argparse.ArgumentParser(
        description="Read, format, filter and compute statistics of a BLAST outfmt 6 file"
    )
    parser.add_argument("-i", "--input_file", required=True, help="BLAST outfmt 6 file")
    parser.add_argument("-o", "--output_file", required=True, help="formatted TSV with headers")
    parser.add_argument("-f", "--filtering_output", required=True, help="filtered hits TSV")
    parser.add_argument("-s", "--statistics_output", required=True, help="per-query statistics TSV")
    parser.add_argument("-a", "--alignment_length", required=True, type=int, help="minimum alignment length")
    parser.add_argument("-p", "--pidentity", default=90.0, type=float, help="minimum percent identity (default 90)")
    parser.add_argument("-e", "--e_value", default=0.01, type=float, help="maximum e-value (default 0.01)")
    parser.add_argument("-t", "--txt_output", default=None, help="optional readable text report")
    args = parser.parse_args()

    print("parsing_blast.py running", file=sys.stderr)
    hits = read_blast(args.input_file)
    write_table(hits, args.output_file)
    compute_stats(hits, args.statistics_output, args.txt_output)
    filtered = filter_hits(hits, args.alignment_length, args.pidentity, args.e_value)
    write_table(filtered, args.filtering_output)
    print(f"{len(hits)} hits read, {len(filtered)} kept after filtering", file=sys.stderr)


if __name__ == "__main__":
    main()
