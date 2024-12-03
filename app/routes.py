from flask import request, render_template, send_file, make_response
from app.utils import merge_pdfs
import os

def init_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/convert', methods=['POST'])
    def convert():
        if 'markdown_files' not in request.files:
            return 'No files uploaded', 400

        files = request.files.getlist('markdown_files')
        if not files or files[0].filename == '':
            return 'No files selected', 400

        # Validate markdown files
        for file in files:
            if not file.filename.endswith(('.md', '.txt')):
                return 'Only .md and .txt files are allowed', 400

        try:
            # Get the output PDF path
            output_path = merge_pdfs(files)

            # Send the file and ensure cleanup
            try:
                response = make_response(send_file(
                    output_path,
                    mimetype='application/pdf',
                    as_attachment=False  # This allows preview in browser
                ))
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = 'inline; filename=converted.pdf'
                return response
            finally:
                # Clean up the output file after sending
                try:
                    os.unlink(output_path)
                except:
                    pass

        except Exception as e:
            print(f"Conversion error: {str(e)}")  # Log the error
            return str(e), 500
