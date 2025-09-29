from PyQt5.Qsci import QsciScintilla
from PyQt5.QtGui import *

class Edit(QsciScintilla):
    def __init__(self):
        super().__init__()
        
        
        
        # 支持显示行号
        self.setMarginType(0, QsciScintilla.SC_MARGIN_NUMBER)
        self.setMarginLineNumbers(0, True)
        self.setMarginWidth(0, 40)