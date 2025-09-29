from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class OutputWindow(QDockWidget):
    """
    输出窗口类，类似于VSCode中的输出窗口，用于显示日志和信息
    """
    
    def __init__(self, parent=None):
        super().__init__("Output", parent)
        self.__initUI()
        
    def __initUI(self):
        """
        初始化UI界面
        """
        # 创建文本编辑器用于显示输出
        self.outputText = QTextEdit()
        self.outputText.setReadOnly(True)
        self.outputText.setLineWrapMode(QTextEdit.NoWrap)
        
        # 设置字体
        font = QFont("Consolas", 10)
        self.outputText.setFont(font)
        
        # 设置为中央部件
        self.setWidget(self.outputText)
        
        # 设置可停靠区域
        self.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.RightDockWidgetArea)
        
    def appendText(self, text):
        """
        在输出窗口中追加文本
        :param text: 要追加的文本
        """
        self.outputText.append(text)
        # 滚动到底部以显示最新内容
        self.outputText.moveCursor(QTextCursor.End)
        
    def clearText(self):
        """
        清空输出窗口中的所有文本
        """
        self.outputText.clear()
        
    def setText(self, text):
        """
        设置输出窗口的文本内容
        :param text: 要设置的文本
        """
        self.outputText.setText(text)
        
    def getText(self):
        """
        获取输出窗口中的所有文本
        :return: 输出窗口中的文本内容
        """
        return self.outputText.toPlainText()
        
    def appendInfo(self, text):
        """
        追加信息级别的日志
        :param text: 日志文本
        """
        self.appendText(f"[INFO] {text}")
        
    def appendError(self, text):
        """
        追加错误级别的日志
        :param text: 错误文本
        """
        self.appendText(f"[ERROR] {text}")
        
    def appendDebug(self, text):
        """
        追加调试级别的日志
        :param text: 调试文本
        """
        self.appendText(f"[DEBUG] {text}")