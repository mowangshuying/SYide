from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import os

class TerminalWindow(QDockWidget):
    """
    终端窗口类，通过进程通信与真正的PowerShell交互
    """
    
    def __init__(self, parent=None):
        super().__init__("Terminal", parent)
        self.process = None
        self.command_history = []
        self.history_index = 0
        self.current_command_start = 0  # 记录当前命令在文本中的起始位置
        self.__initUI()
        self.__initProcess()
        
    def __initUI(self):
        """
        初始化UI界面
        """
        # 创建主部件和布局
        self.mainWidget = QWidget()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.mainWidget.setLayout(self.layout)
        
        # 创建文本显示区域
        self.terminalText = QTextEdit()
        self.terminalText.setFont(QFont("Consolas", 10))
        self.terminalText.installEventFilter(self)
        self.terminalText.setContextMenuPolicy(Qt.CustomContextMenu)
        self.terminalText.customContextMenuRequested.connect(self.showContextMenu)
        
        # 添加到布局
        self.layout.addWidget(self.terminalText)
        
        # 设置为中央部件
        self.setWidget(self.mainWidget)
        
        # 设置可停靠区域
        self.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.RightDockWidgetArea)
        
    def __initProcess(self):
        """
        初始化PowerShell进程
        """
        try:
            # 创建PowerShell进程
            self.process = QProcess(self)
            self.process.setProcessChannelMode(QProcess.MergedChannels)
            self.process.readyReadStandardOutput.connect(self.onReadyRead)
            self.process.started.connect(self.onProcessStarted)
            self.process.finished.connect(self.onProcessFinished)
            
            # 启动PowerShell
            if os.name == 'nt':  # Windows
                self.process.start('powershell.exe')
            else:  # Unix-like systems
                self.process.start('bash')
                
        except Exception as e:
            self.appendText(f"Error starting terminal process: {str(e)}")
            
    def onProcessStarted(self):
        """
        当进程启动时调用
        """
        self.appendText("Terminal connected. PowerShell is ready.\n")
        self.updatePrompt()
        
    def onProcessFinished(self):
        """
        当进程结束时调用
        """
        self.appendText("\nTerminal process finished.\n")
        
    def onReadyRead(self):
        """
        当进程有输出时调用
        """
        # 读取进程输出
        if self.process:
            output = self.process.readAllStandardOutput().data().decode('utf-8', errors='ignore')
            if output:
                # 在终端中显示输出
                self.appendText(output)
            
    def appendText(self, text):
        """
        在终端中追加文本
        """
        self.terminalText.insertPlainText(text)
        # 滚动到底部
        self.terminalText.moveCursor(QTextCursor.End)
        # 更新当前命令起始位置
        self.current_command_start = self.terminalText.textCursor().position()
        
    def updatePrompt(self):
        """
        更新命令行提示符
        """
        # 获取当前目录
        try:
            cwd = os.getcwd()
            prompt = f"PS {cwd}> "
            self.appendText(prompt)
            self.current_command_start = self.terminalText.textCursor().position()
        except:
            self.appendText("PS> ")
            self.current_command_start = self.terminalText.textCursor().position()
            
    def executeCommand(self, command):
        """
        执行命令
        """
        if not command:
            self.updatePrompt()
            return
            
        # 添加到历史记录
        self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        # 发送命令到PowerShell进程
        if self.process and self.process.state() == QProcess.Running:
            self.process.write(f"{command}\n".encode())
        else:
            self.appendText("Error: Terminal process is not running.\n")
            
    def eventFilter(self, obj, event):
        """
        事件过滤器，处理键盘事件
        """
        if obj == self.terminalText and event.type() == QEvent.KeyPress:
            cursor = self.terminalText.textCursor()
            
            # 只允许在最后一行编辑
            if cursor.position() < self.current_command_start:
                cursor.movePosition(QTextCursor.End)
                self.terminalText.setTextCursor(cursor)
                
            # 处理回车键
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                # 获取当前命令
                cursor.movePosition(QTextCursor.End)
                cursor.setPosition(self.current_command_start, QTextCursor.KeepAnchor)
                command = cursor.selectedText().strip()
                
                # 添加换行符
                self.appendText("\n")
                
                # 执行命令
                self.executeCommand(command)
                return True
                
            # 处理上下箭头键（历史命令）
            elif event.key() == Qt.Key_Up:
                if self.command_history and self.history_index > 0:
                    self.history_index -= 1
                    # 清除当前命令
                    cursor.movePosition(QTextCursor.End)
                    cursor.setPosition(self.current_command_start, QTextCursor.KeepAnchor)
                    cursor.removeSelectedText()
                    # 插入历史命令
                    cursor.insertText(self.command_history[self.history_index])
                return True
                
            elif event.key() == Qt.Key_Down:
                cursor.movePosition(QTextCursor.End)
                cursor.setPosition(self.current_command_start, QTextCursor.KeepAnchor)
                cursor.removeSelectedText()
                
                if self.command_history and self.history_index < len(self.command_history) - 1:
                    self.history_index += 1
                    cursor.insertText(self.command_history[self.history_index])
                elif self.history_index == len(self.command_history) - 1:
                    self.history_index += 1
                return True
                
            # 处理退格键，防止删除提示符
            elif event.key() == Qt.Key_Backspace:
                if cursor.position() <= self.current_command_start:
                    return True  # 阻止删除提示符
                    
            # 处理其他编辑键，防止移动到提示符前
            elif event.key() == Qt.Key_Left:
                if cursor.position() <= self.current_command_start:
                    return True
            elif event.key() == Qt.Key_Home:
                cursor.setPosition(self.current_command_start)
                self.terminalText.setTextCursor(cursor)
                return True
                
        return super().eventFilter(obj, event)
        
    def showContextMenu(self, position):
        """
        显示上下文菜单
        """
        menu = self.terminalText.createStandardContextMenu()
        
        menu.addSeparator()
        clearAction = QAction("Clear Terminal", self)
        clearAction.triggered.connect(self.clearTerminal)
        menu.addAction(clearAction)
        
        menu.exec_(self.terminalText.mapToGlobal(position))
        
    def clearTerminal(self):
        """
        清空终端内容
        """
        self.terminalText.clear()
        self.updatePrompt()
        
    def stopProcess(self):
        """
        停止终端进程
        """
        if self.process and self.process.state() == QProcess.Running:
            self.process.terminate()
            self.process.waitForFinished(3000)  # 等待3秒
            if self.process.state() == QProcess.Running:
                self.process.kill()