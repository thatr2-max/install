#!/bin/bash

# Script to add accessibility widget to all HTML pages

echo "Adding accessibility widget to all pages..."

# Update all HTML files in pages/ directory
for file in pages/*.html; do
  echo "Processing $file..."

  # Add accessibility widget CSS if not already present
  if ! grep -q "accessibility-widget.css" "$file"; then
    sed -i 's|<link rel="stylesheet" href="../assets/css/styles.css">|<link rel="stylesheet" href="../assets/css/styles.css">\n    <link rel="stylesheet" href="../assets/css/accessibility-widget.css">|' "$file"
    echo "  - Added CSS to $file"
  fi

  # Update title to include Springfield if it contains "City Government Portal"
  if grep -q "City Government Portal" "$file" && ! grep -q "Springfield City Government Portal" "$file"; then
    sed -i 's/City Government Portal/Springfield City Government Portal/g' "$file"
    echo "  - Updated title in $file"
  fi

  # Add accessibility widget script if not already present
  if ! grep -q "accessibility.js" "$file"; then
    # Find the line with </body> and add the script before it
    sed -i 's|</body>|    <!-- Accessibility Widget Script -->\n    <script src="../assets/js/accessibility.js"></script>\n</body>|' "$file"
    echo "  - Added JavaScript to $file"
  fi
done

echo "Done! All pages have been updated with the accessibility widget."
