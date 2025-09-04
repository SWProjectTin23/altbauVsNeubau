#!/usr/bin/env bash
# filepath: /Users/tim/dhbw/04_Semester/altbauVsNeubau/gen_docs_md_pdf.sh
set -euo pipefail

DOCS_DIR="./docs"
README="./README.md"
OUT_MD="docs_full.md"
OUT_PDF="docs_full.pdf"
TMP_MD="__all_docs_tmp.md"

# YAML header
{
  echo "---"
  echo 'title: "Project Documentation"'
  echo 'author: "DHBW Heidenheim INF2023 Semester 4"'
  echo "date: \"$(date +%Y-%m-%d)\""
  echo "---"
  echo
} > "$TMP_MD"

# 1) Collect markdown files deterministically (no README)
mapfile -t MD_ARRAY < <(find "$DOCS_DIR" -type f -name "*.md" | sort)

# 2) TOC
{
  echo "# Documentation Table of Contents"
  echo
  echo "- **README.md**"
  for FILE in "${MD_ARRAY[@]}"; do
    REL_PATH="${FILE#$DOCS_DIR/}"
    DIR_PATH="$(dirname "$REL_PATH")"
    FILE_NAME="$(basename "$FILE")"
    echo "- **${DIR_PATH}/${FILE_NAME}**"
  done
  echo
} >> "$TMP_MD"

# 3) README
{
  echo -e "\n\n***\n\n## README.md\n"
  cat "$README"
  echo
} >> "$TMP_MD"

# 4) Append all docs
for FILE in "${MD_ARRAY[@]}"; do
  REL_PATH="${FILE#$DOCS_DIR/}"
  DIR_PATH="$(dirname "$REL_PATH")"
  FILE_NAME="$(basename "$FILE")"
  {
    echo -e "\n\n***\n\n## ${DIR_PATH}/${FILE_NAME}\n"
    cat "$FILE"
    echo
  } >> "$TMP_MD"
done

# 5) Write combined markdown
cp "$TMP_MD" "$OUT_MD"

# 6) Build PDF with XeLaTeX
RESOURCE_PATH="./:${DOCS_DIR}:${DOCS_DIR}/images:./images"

# Fonts: DejaVu Serif (Text), DejaVu Sans Mono (Code), Latin Modern Math (Mathe)
PANDOC_COMMON=(
  --from=gfm
  --toc --toc-depth=3
  --resource-path="$RESOURCE_PATH"
  --metadata title="Project Documentation"
  -V mainfont="DejaVu Serif"
  -V monofont="DejaVu Sans Mono"
  -V mathfont="Latin Modern Math"
  -V geometry:margin=2.5cm
)

echo "Using PDF engine: xelatex"
pandoc "$TMP_MD" -o "$OUT_PDF" "${PANDOC_COMMON[@]}" --pdf-engine=xelatex

# 7) Cleanup
rm "$TMP_MD"

echo "Markdown generated: $OUT_MD"
echo "PDF generated: $OUT_PDF"
