#!/bin/bash

# Script to create a new language directory for Nullianity translations
# Usage: ./new-language.sh <language_code>
# Example: ./new-language.sh es

if [ $# -eq 0 ]; then
    echo "Usage: $0 <language_code>"
    echo "Example: $0 es"
    echo ""
    echo "Common language codes:"
    echo "  es - Spanish"
    echo "  fr - French"
    echo "  de - German"
    echo "  pt - Portuguese"
    echo "  it - Italian"
    echo "  zh - Chinese"
    echo "  ja - Japanese"
    echo "  ko - Korean"
    echo "  ar - Arabic"
    echo "  hi - Hindi"
    exit 1
fi

LANG_CODE=$1
LANG_DIR="docs/$LANG_CODE"
TEMPLATE_DIR="docs/template"

# Check if language directory already exists
if [ -d "$LANG_DIR" ]; then
    echo "Error: Language directory '$LANG_DIR' already exists!"
    exit 1
fi

# Check if template directory exists
if [ ! -d "$TEMPLATE_DIR" ]; then
    echo "Error: Template directory '$TEMPLATE_DIR' not found!"
    exit 1
fi

# Create the new language directory
echo "Creating language directory: $LANG_DIR"
mkdir -p "$LANG_DIR"

# Copy template files
echo "Copying template files..."
cp "$TEMPLATE_DIR"/* "$LANG_DIR"/

echo ""
echo "✅ Successfully created language directory for '$LANG_CODE'"
echo ""
echo "Next steps:"
echo "1. Edit the files in $LANG_DIR/ and replace the placeholders with your translations"
echo "2. Use the original Russian files in docs/ru/ as reference for the content"
echo "3. Update the root README.md to include your language in the language list"
echo "4. Submit a Pull Request with your translation"
echo ""
echo "Files to translate:"
for file in "$LANG_DIR"/*; do
    echo "  - $(basename "$file")"
done 