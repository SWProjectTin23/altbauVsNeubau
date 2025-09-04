#!/bin/bash
# filepath: /Users/tim/dhbw/04_Semester/altbauVsNeubau/gen_docs_md_pdf.sh

DOCS_DIR="./docs"
README="./README.md"
OUT_MD="docs_full.md"
OUT_PDF="docs_full.pdf"
TMP_MD="__all_docs_tmp.md"

# YAML-Header für Pandoc
echo "---" > "$TMP_MD"
echo "title: \"Project Documentation\"" >> "$TMP_MD"
echo "author: \"DHBW Heidenheim INF2023 Semester 4\"" >> "$TMP_MD"
echo "date: \"$(date +%Y-%m-%d)\"" >> "$TMP_MD"
echo "---" >> "$TMP_MD"
echo "" >> "$TMP_MD"

# 1. Alle Markdown-Dateien finden und sortieren
MD_FILES=$(find "$DOCS_DIR" -type f -name "*.md" | sort)

# 2. Inhaltsverzeichnis generieren
echo "# Documentation Table of Contents" >> "$TMP_MD"
echo "" >> "$TMP_MD"
echo "- **README.md**" >> "$TMP_MD"
for FILE in $MD_FILES; do
  REL_PATH="${FILE#$DOCS_DIR/}"
  DIR_PATH=$(dirname "$REL_PATH")
  FILE_NAME=$(basename "$FILE")
  echo "- **${DIR_PATH}/${FILE_NAME}**" >> "$TMP_MD"
done
echo "" >> "$TMP_MD"

# 3. README.md einfügen
echo -e "\n\n***\n\n## README.md\n" >> "$TMP_MD"
cat "$README" >> "$TMP_MD"
echo "" >> "$TMP_MD"

# 4. Alle Markdown-Dateien zusammenfügen
for FILE in $MD_FILES; do
  REL_PATH="${FILE#$DOCS_DIR/}"
  DIR_PATH=$(dirname "$REL_PATH")
  FILE_NAME=$(basename "$FILE")
  echo -e "\n\n***\n\n## ${DIR_PATH}/${FILE_NAME}\n" >> "$TMP_MD"
  cat "$FILE" >> "$TMP_MD"
  echo "" >> "$TMP_MD"
done

# 5. Kopiere die Gesamtdokumentation als Markdown
cp "$TMP_MD" "$OUT_MD"

# 6. PDF mit Pandoc erzeugen
pandoc "$TMP_MD" -o "$OUT_PDF" --toc --toc-depth=3

# 7. Temporäre Datei löschen
rm "$TMP_MD"

echo "Markdown generated: $OUT_MD"
echo "PDF generated: $OUT_PDF"