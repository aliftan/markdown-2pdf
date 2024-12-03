from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

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
        alignment=0
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
        leading=14,
        leftIndent=36,
        rightIndent=36,
        firstLineIndent=0,
        alignment=0,
        backColor=colors.Color(0.95, 0.95, 0.95),
        spaceShrinkage=0.05
    )
    
    code = ParagraphStyle(
        'CustomCode',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=9,
        spaceBefore=6,
        spaceAfter=6,
        leading=12,
        leftIndent=36,
        rightIndent=36,
        firstLineIndent=0,
        whitespace='pre-wrap',
        wordWrap='LTR',
        textColor=colors.black,
        backColor=colors.Color(0.95, 0.95, 0.95)  # Light gray background
    )

    return {
        'pageStyle': pageStyle,
        'h1': h1, 
        'h2': h2, 
        'h3': h3, 
        'normal': normal,
        'bullet': bullet,
        'blockquote': blockquote,
        'code': code
    }