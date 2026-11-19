#!/usr/bin/env bash
# Split the full compiled paper into a main PDF (main text, statements, references)
# and an appendix PDF (Appendix A onward). Page numbers and all cross-reference
# numbers stay exactly as in the full PDF.
# Usage: bash split_main_appendix.sh full.pdf [out_prefix]
# Needs pdftotext (poppler-utils) and qpdf.
set -euo pipefail
full="$1"
prefix="${2:-${full%.pdf}}"
pages=$(pdfinfo "$full" | awk '/^Pages:/ {print $2}')
start=""
for ((p = 1; p <= pages; p++)); do
  # Appendix A opens with this sentence (sections/training_algorithm_en.tex).
  if pdftotext -f "$p" -l "$p" "$full" - | tr -s ' \n' ' ' | grep -q "Algorithm 1 summarizes the co-evolution loop"; then
    start=$p
    break
  fi
done
if [[ -z "$start" ]]; then
  echo "Could not find the start of Appendix A in $full" >&2
  exit 1
fi
qpdf --empty --pages "$full" "1-$((start - 1))" -- "${prefix}_main.pdf"
qpdf --empty --pages "$full" "$start-z" -- "${prefix}_appendix.pdf"
echo "Appendix A starts on page $start of $pages."
echo "Main:     ${prefix}_main.pdf (pages 1-$((start - 1)))"
echo "Appendix: ${prefix}_appendix.pdf (pages $start-$pages)"
