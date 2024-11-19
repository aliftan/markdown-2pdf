from flask import request, render_template
from app.utils import merge_pdfs

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
            if not file.filename.endswith('.md'):
                return 'Only .md files are allowed', 400

        return merge_pdfs(files)