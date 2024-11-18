from flask import Flask, request, send_file, render_template
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Frame
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus.doctemplate import PageTemplate
from PyPDF2 import PdfMerger
import tempfile
import os

app = Flask(__name__)

class BookTemplate(SimpleDocTemplate):
    def __init__(self, filename, **kw):
        styles = create_styles()
        pageStyle = styles['pageStyle']
        
        SimpleDocTemplate.__init__(
            self, 
            filename,
            pagesize=letter,
            leftMargin=pageStyle['leftMargin'],
            rightMargin=pageStyle['rightMargin'],
            topMargin=pageStyle['topMargin'],
            bottomMargin=pageStyle['bottomMargin']
        )
        
        self.pageTemplates = []
        template = PageTemplate(
            'normal',
            [Frame(
                self.leftMargin,
                self.bottomMargin,
                self.width,
                self.height,
                id='normal'
            )]
        )
        self.addPageTemplates(template)
        
    def beforePage(self):
        self.canv.saveState()
        # Page number
        self.canv.setFont('Times-Roman', 9)
        self.canv.drawRightString(
            self.width + self.leftMargin, 
            0.75*inch,
            str(self.canv.getPageNumber())
        )
        # Copyright footer with additional info
        page_width = self.width + self.leftMargin
        self.canv.drawString(
            self.leftMargin,
            0.75*inch,
            '©ilmugunung.lab | Digital Asset Education - ' + 
            'Building Financial Freedom - ' + 
            'Generation Wealthy'
        )
        self.canv.restoreState()

def escape_special_chars(text):
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#39;')
    return text

def create_styles():
    styles = getSampleStyleSheet()
    serif_font = 'Times-Roman'
    
    pageStyle = {
        'topMargin': 1*inch,
        'bottomMargin': 1*inch,
        'leftMargin': 1.25*inch,
        'rightMargin': 1.25*inch,
    }

    h1 = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontName=serif_font,
        fontSize=24,
        spaceAfter=12, 
        spaceBefore=24,
        leading=28,
        alignment=1
    )
    
    h2 = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontName=serif_font,
        fontSize=18,
        spaceAfter=6,  
        spaceBefore=12,
        leading=20,
        alignment=1
    )
    
    h3 = ParagraphStyle(
        'CustomH3',
        parent=styles['Heading3'],
        fontName=serif_font,
        fontSize=14,
        spaceAfter=4,  
        spaceBefore=4, 
        leading=16     
    )
    
    normal = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=serif_font,
        fontSize=11,
        spaceBefore=3, 
        spaceAfter=3,  
        leading=14,    
        alignment=4
    )
    
    bullet = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontName=serif_font,
        fontSize=11,
        spaceBefore=2, 
        spaceAfter=2,  
        leading=14,    
        leftIndent=24,
        firstLineIndent=0
    )
    
    blockquote = ParagraphStyle(
        'CustomBlockquote',
        parent=styles['Normal'],
        fontName=serif_font,
        fontSize=10,
        spaceBefore=8, 
        spaceAfter=8,  
        leading=12,    
        leftIndent=36,
        rightIndent=36,
        firstLineIndent=0,
        backColor=colors.Color(0.95, 0.95, 0.95)
    )
    
    code = ParagraphStyle(
        'CustomCode',
        parent=styles['Code'],
        fontSize=9,
        fontName='Courier',
        spaceBefore=6, 
        spaceAfter=6,  
        leading=12,
        leftIndent=36,
        rightIndent=36
    )

    indented = ParagraphStyle(
        'CustomIndented',
        parent=styles['Normal'],
        fontName=serif_font,
        fontSize=11,
        spaceBefore=6,
        spaceAfter=6,
        leading=16,
        leftIndent=24,
        alignment=0
    )

    return {
        'pageStyle': pageStyle,
        'h1': h1, 
        'h2': h2, 
        'h3': h3, 
        'normal': normal,
        'bullet': bullet,
        'blockquote': blockquote,
        'code': code,
        'indented': indented
    }

def process_text(text):
    # First escape special characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#39;')
    
    # Handle italic text (single asterisks)
    parts = text.split('*')
    for i in range(1, len(parts), 2):
        if i < len(parts):
            parts[i] = f'<i>{parts[i]}</i>'
    text = ''.join(parts)
    
    # Handle bold text (double asterisks)
    parts = text.split('**')
    for i in range(1, len(parts), 2):
        if i < len(parts):
            parts[i] = f'<b>{parts[i]}</b>'
    text = ''.join(parts)
    
    return text

def convert_markdown_to_pdf(markdown_content, output_path):
    doc = BookTemplate(output_path)
    styles = create_styles()
    elements = []
    
    lines = markdown_content.split('\n')
    in_code_block = False
    in_blockquote = False
    code_content = []
    blockquote_content = []
    
    for line in lines:
        # Handle empty lines
        if not line.strip():
            if in_blockquote and blockquote_content:
                elements.append(Paragraph('\n'.join(blockquote_content), styles['blockquote']))
                blockquote_content = []
                in_blockquote = False
            elif in_code_block:
                continue  # Preserve empty lines in code blocks
            elements.append(Spacer(1, 12))
            continue

        # Handle code blocks        
        if line.startswith('```'):
            if in_code_block:  # End of code block
                elements.append(Paragraph('<pre>{}</pre>'.format('\n'.join(code_content)), styles['code']))
                code_content = []
            in_code_block = not in_code_block
            continue
        
        if in_code_block:
            code_content.append(line)
            continue

        # Handle blockquotes
        if line.startswith('>'):
            in_blockquote = True
            text = line[1:].strip()
            blockquote_content.append(text)
            continue
            
        # Handle continued blockquote content
        if in_blockquote:
            if line.startswith('-'):
                text = '• ' + line[1:].strip()
            else:
                text = line.strip()
            blockquote_content.append(text)
            continue

        # Regular content
        text = process_text(line.strip())
        
        if line.startswith('# '):
            text = text[2:]
            elements.append(Paragraph(text, styles['h1']))
        elif line.startswith('## '):
            text = text[3:]
            elements.append(Paragraph(text, styles['h2']))
        elif line.startswith('### '):
            text = text[4:]
            elements.append(Paragraph(text, styles['h3']))
        elif line.startswith('#### '):
            text = text[5:]
            elements.append(Paragraph(text, styles['h3']))
        elif line.startswith('- '):
            text = '• ' + text[2:]
            elements.append(Paragraph(text, styles['bullet']))
        else:
            elements.append(Paragraph(text, styles['normal']))
    
    # Handle any remaining content
    if blockquote_content:
        elements.append(Paragraph('\n'.join(blockquote_content), styles['blockquote']))
    elif code_content:
        elements.append(Paragraph('<pre>{}</pre>'.format('\n'.join(code_content)), styles['code']))
    
    doc.build(elements)

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

    merger = PdfMerger()
    temp_files = []

    try:
        for file in files:
            markdown_content = file.read().decode('utf-8')
            temp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            temp_files.append(temp_pdf.name)
            convert_markdown_to_pdf(markdown_content, temp_pdf.name)
            merger.append(temp_pdf.name)

        output = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        merger.write(output.name)
        merger.close()

        return send_file(
            output.name,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='merged.pdf'
        )

    finally:
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass
        try:
            os.unlink(output.name)
        except:
            pass

if __name__ == '__main__':
    app.run(debug=True)