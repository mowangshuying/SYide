from PyQt5.QtWidgets import *
import sys

from MainWindow import *

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    app.exec_()
