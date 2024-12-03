from flask import send_file
import tempfile
import os
from PyPDF2 import PdfMerger
from lib.markdown2pdf import convert_markdown_to_pdf


def merge_pdfs(files):
    merger = PdfMerger()
    temp_files = []
    output = None

    try:
        # Convert each markdown file to PDF
        for file in files:
            markdown_content = file.read().decode('utf-8')
            temp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            temp_files.append(temp_pdf.name)
            convert_markdown_to_pdf(markdown_content, temp_pdf.name)
            merger.append(temp_pdf.name)

        # Create final merged PDF
        output = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        merger.write(output.name)
        merger.close()

        # Return the path instead of send_file
        return output.name

    finally:
        # Clean up temporary files except the output
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass
