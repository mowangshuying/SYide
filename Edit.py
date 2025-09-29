from PyQt5.Qsci import QsciScintilla
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class Edit(QsciScintilla):
    # 定义断点切换信号
    breakpointToggled = pyqtSignal(int, bool)  # 行号, 是否设置断点
    
    def __init__(self):
        super().__init__()
        
        # 存储断点的集合
        self.breakpoints = set()
        
        # 初始化编辑器
        self.__initEditor()
        
    def __initEditor(self):
        # 支持显示行号
        self.setMarginType(0, QsciScintilla.SC_MARGIN_NUMBER)
        self.setMarginLineNumbers(0, True)
        self.setMarginWidth(0, 40)
        
        # 添加断点边距（在行号右侧）
        self.setMarginType(1, QsciScintilla.SC_MARGIN_SYMBOL)
        self.setMarginWidth(1, 16)
        self.setMarginSensitivity(1, True)  # 确保边距可点击
        
        # 设置断点标记
        self.markerDefine(QsciScintilla.SC_MARK_CIRCLE, 1)
        self.setMarkerBackgroundColor(QColor(255, 0, 0, 100), 1)  # 半透明红色
        self.setMarkerForegroundColor(QColor(255, 0, 0), 1)
        
        # 连接信号
        self.marginClicked.connect(self.onMarginClicked)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onContextMenu)
        
    def onMarginClicked(self, margin, line, state):
        """
        处理边距点击事件
        :param margin: 边距索引
        :param line: 行号
        :param state: 状态
        """
        # 只处理断点边距（索引为1）
        if margin == 1:
            self.toggleBreakpoint(line)
            
    def onContextMenu(self, position):
        """
        处理上下文菜单事件
        :param position: 菜单位置
        """
        # 通过position坐标获取对应的行号
        line = self.lineAt(position)
        
        # 如果lineAt方法没有正确工作，使用当前光标位置的行号
        if line < 0:
            line = self.getCursorPosition()[0]  # 获取当前光标所在行号
        
        # 创建上下文菜单
        menu = self.createStandardContextMenu()
        
        # 添加断点操作菜单项
        # 即使line<0也显示断点菜单项，因为用户可能希望在当前行设置断点
        menu.addSeparator()
        
        # 确定使用哪一行设置断点（优先使用点击位置的行，否则使用光标位置的行）
        target_line = line if line >= 0 else self.getCursorPosition()[0]
        line_copy = target_line
        
        if target_line in self.breakpoints:
            removeBreakpointAction = QAction("Remove Breakpoint", self)
            removeBreakpointAction.triggered.connect(lambda checked, l=line_copy: self.removeBreakpoint(l))
            menu.addAction(removeBreakpointAction)
        else:
            addBreakpointAction = QAction("Add Breakpoint", self)
            addBreakpointAction.triggered.connect(lambda checked, l=line_copy: self.addBreakpoint(l))
            menu.addAction(addBreakpointAction)
            
        toggleBreakpointAction = QAction("Toggle Breakpoint", self)
        toggleBreakpointAction.triggered.connect(lambda checked, l=line_copy: self.toggleBreakpoint(l))
        menu.addAction(toggleBreakpointAction)
        
        # 显示菜单
        menu.exec_(self.mapToGlobal(position))
        
    def toggleBreakpoint(self, line):
        """
        切断点状态（添加或删除）
        :param line: 行号
        """
        if line in self.breakpoints:
            self.removeBreakpoint(line)
        else:
            self.addBreakpoint(line)
            
    def addBreakpoint(self, line):
        """
        添加断点
        :param line: 行号
        """
        if line not in self.breakpoints:
            self.breakpoints.add(line)
            self.markerAdd(line, 1)
            self.breakpointToggled.emit(line, True)
            
    def removeBreakpoint(self, line):
        """
        删除断点
        :param line: 行号
        """
        if line in self.breakpoints:
            self.breakpoints.remove(line)
            self.markerDelete(line, 1)
            self.breakpointToggled.emit(line, False)
            
    def clearBreakpoints(self):
        """
        清除所有断点
        """
        lines = list(self.breakpoints)  # 创建副本以避免在迭代时修改集合
        for line in lines:
            self.removeBreakpoint(line)
            
    def getBreakpoints(self):
        """
        获取所有断点
        :return: 断点行号列表
        """
        return sorted(list(self.breakpoints))