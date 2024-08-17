from docx import Document
from docx2txt import process
import difflib

# Load the old and new documents
old_doc = process("doc-old.docx")
new_doc = process("doc-new.docx")

# Perform a line-by-line comparison
diff = difflib.unified_diff(old_doc.splitlines(), new_doc.splitlines(), lineterm='')
# Create a new Document to store the comparison
comparison_doc = Document()

# Add the differences to the new document
for line in diff:
    comparison_doc.add_paragraph(line)

# Save the comparison document with tracked changes enabled
comparison_doc.save("comparison-with-track-changes.docx")
