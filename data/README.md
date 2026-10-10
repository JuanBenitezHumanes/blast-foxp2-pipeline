# Input data

The FASTA files are not included in the repository because of their size.
Place them in this folder before running the pipeline:

| File | Content |
|---|---|
| `human_foxp2.fasta` | Human *FOXP2* locus from two assemblies: GRCh38 chr7 (`NC_000007.14:114086327-114693765`) and T2T-CHM13v2.0 chr7 (`NC_060931.1:115401144-116008457`) |
| `mouse_genome.fasta` | Mouse reference genome (GRCm39, RefSeq chromosomes `NC_0000xx`) |

Example download with [NCBI EDirect](https://www.ncbi.nlm.nih.gov/books/NBK179288/) and [NCBI Datasets](https://www.ncbi.nlm.nih.gov/datasets/):

```bash
# Human FOXP2 locus (both assemblies)
efetch -db nuccore -id NC_000007.14 -seq_start 114086327 -seq_stop 114693765 -format fasta >  data/human_foxp2.fasta
efetch -db nuccore -id NC_060931.1  -seq_start 115401144 -seq_stop 116008457 -format fasta >> data/human_foxp2.fasta

# Mouse genome (GRCm39)
datasets download genome accession GCF_000001635.27 --include genome --filename mouse_genome.zip
unzip mouse_genome.zip && cat ncbi_dataset/data/GCF_000001635.27/*.fna > data/mouse_genome.fasta
```
