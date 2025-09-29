from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from Edit import Edit

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.edit = Edit()
        self.setCentralWidget(self.edit)
        
        self.setWindowTitle("@SYide")
        self.resize(1000, 750)