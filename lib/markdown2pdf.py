from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from .templates import BookTemplate
from .pdf_styles import create_styles

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

def process_blockquote(line, blockquote_content, in_blockquote=False):
    """Handle blockquote content and formatting"""
    if line.startswith('>'):
        in_blockquote = True
        text = line[1:].strip()
        
        # Handle bullet points in blockquote
        if text.startswith('-'):
            blockquote_content.append('• ' + text[1:].strip())
        else:
            blockquote_content.append(text)
            
        return True, blockquote_content
    
    if in_blockquote:
        # Handle continued blockquote content
        if not line.strip():
            blockquote_content.append('')
        elif line.startswith('-'):
            blockquote_content.append('• ' + line[1:].strip())
        else:
            blockquote_content.append(line.strip())
        return True, blockquote_content
        
    return False, blockquote_content

def process_code_block(line, code_content, in_code_block=False):
    """Handle code block content and formatting"""
    if line.startswith('```'):
        return not in_code_block, code_content
    
    if in_code_block:
        code_content.append(line)
        return True, code_content
        
    return False, code_content

def format_blockquote(blockquote_content):
    """Format the final blockquote content"""
    if not blockquote_content:
        return ''
    
    formatted_lines = []
    current_section = []
    
    for line in blockquote_content:
        if not line:  # Empty line
            if current_section:
                formatted_lines.extend(current_section)
                formatted_lines.append('')
                current_section = []
            continue
            
        # Handle bullet points
        if line.startswith('•'):
            current_section.append(line)
        else:
            # If we have a previous section, add it with spacing
            if current_section:
                formatted_lines.extend(current_section)
                formatted_lines.append('')
                current_section = []
            formatted_lines.append(line)
    
    # Add any remaining section
    if current_section:
        formatted_lines.extend(current_section)
    
    # Process text formatting (bold, italic)
    result = []
    for line in formatted_lines:
        if line:
            result.append(process_text(line))
        else:
            result.append('')
            
    return '\n'.join(result)

def format_code_block(code_content):
    if not code_content:
        return ''

    formatted_lines = []
    
    for line in code_content:
        # Skip if line is just code block markers
        if line.strip() == '```':
            continue
            
        # Split content by ' - ' delimiter and process
        if ' - ' in line:
            parts = line.split(' - ')
            header = parts[0].strip()
            items = parts[1:]
            
            # Add the header
            if header:
                if formatted_lines:  # Add spacing before new section
                    formatted_lines.append('')
                formatted_lines.append(header + ':')
            
            # Add items as bullet points
            for item in items:
                if item.strip():
                    formatted_lines.append(f'- {item.strip()}')
        else:
            # Regular line without delimiter
            formatted_lines.append(line.strip())

    # Clean up extra whitespace and join lines
    return '\n'.join(formatted_lines)


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
            if in_blockquote:
                elements.append(Paragraph(format_blockquote(blockquote_content), styles['blockquote']))
                blockquote_content = []
                in_blockquote = False
            elif in_code_block:
                code_content.append('')
            else:
                elements.append(Spacer(1, 12))
            continue

        # Handle code blocks
        is_code, code_content = process_code_block(line, code_content, in_code_block)
        if is_code != in_code_block:
            in_code_block = is_code
            if not in_code_block and code_content:  # End of code block
                elements.append(Paragraph(
                    f'<pre>{format_code_block(code_content)}</pre>', 
                    styles['code']
                ))
                code_content = []
            continue
        
        if in_code_block:
            continue

        # Handle blockquotes
        is_quote, blockquote_content = process_blockquote(line, blockquote_content, in_blockquote)
        if is_quote:
            in_blockquote = True
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
        elements.append(Paragraph(format_blockquote(blockquote_content), styles['blockquote']))
    elif code_content:
        elements.append(Paragraph(f'<pre>{format_code_block(code_content)}</pre>', styles['code']))
    
    doc.build(elements)