from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Frame
from reportlab.platypus.doctemplate import PageTemplate
from reportlab.lib.units import inch
from .pdf_styles import create_styles

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
        self.canv.setFont('Times-Roman', 9)
        self.canv.drawRightString(
            self.width + self.leftMargin, 
            0.75*inch,
            str(self.canv.getPageNumber())
        )
        page_width = self.width + self.leftMargin
        self.canv.drawString(
            self.leftMargin,
            0.75*inch,
            '©ilmugunung.lab | Digital Asset Education - Building Financial Freedom'
        )
        self.canv.restoreState()