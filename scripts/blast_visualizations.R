#!/usr/bin/env Rscript
# Plot BLAST hit statistics: percent identity histogram and identity vs alignment length.
# Usage:
#   Rscript blast_visualizations.R -p blast_formatted.tsv -o identity_histogram.png -s identity_vs_length.png

suppressPackageStartupMessages({
  library(ggplot2)
  library(optparse)
})

arguments <- list(
  make_option(c("-p", "--parsed"), type = "character",
              help = "path to the formatted BLAST table (TSV with headers)"),
  make_option(c("-o", "--histogram"), type = "character", default = "identity_histogram.png",
              help = "output path for the histogram [default %default]"),
  make_option(c("-s", "--scatter"), type = "character", default = "identity_vs_length.png",
              help = "output path for the scatter plot [default %default]")
)

opt <- parse_args(OptionParser(option_list = arguments))
if (is.null(opt$parsed)) stop("Missing required argument -p/--parsed")

df <- read.delim(opt$parsed, header = TRUE, sep = "\t")

h <- ggplot(df, aes(x = pidentity)) +
  geom_histogram(binwidth = 2, fill = "steelblue", colour = "black") +
  facet_wrap(~ query_id) +
  labs(title = "Distribution of percent identity of BLAST hits",
       x = "Percent identity (%)", y = "Number of hits") +
  theme_bw()

sp <- ggplot(df, aes(x = pidentity, y = alignment_length)) +
  geom_point(size = 2, shape = 21, colour = "black", fill = "firebrick", alpha = 0.6) +
  facet_wrap(~ query_id) +
  labs(title = "Percent identity vs alignment length",
       x = "Percent identity (%)", y = "Alignment length (bp)") +
  theme_bw()

ggsave(opt$histogram, h, width = 9, height = 4.5, dpi = 150)
ggsave(opt$scatter, sp, width = 9, height = 4.5, dpi = 150)
