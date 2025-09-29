from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from Edit import Edit
from FileBrowser import FileBrowser
from OutputWindow import OutputWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.tabWidget = None
        self.edit = None
        self.outputWindow = None
        
        self.__initMenuBar()
        self.__initUI()
        self.__initDocker()
        self.__initStatusBar()
        
    def __initMenuBar(self):
        fileMenu = self.menuBar().addMenu("File")
        
        newAction= QAction("New", self)
        fileMenu.addAction(newAction)
        
        openFileAction = QAction("Open", self)
        fileMenu.addAction(openFileAction)
        openFileAction.triggered.connect(self.__onOpenFile)
        
        openFolderAction = QAction("Open Folder", self)
        fileMenu.addAction(openFolderAction)
        openFolderAction.triggered.connect(self.__onOpenFolder)
        
        saveAction = QAction("Save", self)
        fileMenu.addAction(saveAction)
        
        exitAction = QAction("Exit", self)
        fileMenu.addAction(exitAction)
        
        editMenu = self.menuBar().addMenu("Edit")
        cutAction = QAction("Cut", self)
        editMenu.addAction(cutAction)
        
        editMenu.addAction(cutAction)
        copyAction = QAction("Copy", self)
        editMenu.addAction(copyAction)
        
        editMenu.addAction(copyAction)
        pasteAction = QAction("Paste", self)
        editMenu.addAction(pasteAction)
        
        helpMenu = self.menuBar().addMenu("Help")
        aboutAction = QAction("About", self)
        helpMenu.addAction(aboutAction)
        
    def __initUI(self):
        # 创建标签页控件
        self.tabWidget = QTabWidget()
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self.closeTab)
        
        # 设置为中心部件
        self.setCentralWidget(self.tabWidget)
        
        # 创建第一个默认编辑器标签页
        self.createTab("Untitled")
        
        self.setWindowTitle("@SYide")
        self.resize(1000, 750)
        
    def createTab(self, title, filePath=None):
        """
        创建一个新的标签页
        :param title: 标签标题
        :param filePath: 文件路径（可选）
        :return: 新创建的编辑器实例
        """
        editor = Edit()
        editor.breakpointToggled.connect(self.onBreakpointToggled)
        tabIndex = self.tabWidget.addTab(editor, title)
        self.tabWidget.setCurrentIndex(tabIndex)
        
        # 保存文件路径作为属性
        if filePath:
            editor.filePath = filePath
            
        return editor
        
    def closeTab(self, index):
        """
        关闭指定索引的标签页
        :param index: 标签页索引
        """
        # 不允许关闭最后一个标签页
        if self.tabWidget.count() <= 1:
            return
            
        self.tabWidget.removeTab(index)
        
    def getCurrentEditor(self):
        """
        获取当前活动的编辑器
        :return: 当前编辑器实例
        """
        return self.tabWidget.currentWidget()
        
    def onBreakpointToggled(self, line, added):
        """
        处理断点切换事件
        :param line: 行号
        :param added: True表示添加断点，False表示删除断点
        """
        current_editor = self.getCurrentEditor()
        file_name = "Untitled"
        if hasattr(current_editor, 'filePath'):
            file_name = current_editor.filePath
            
        if self.outputWindow:
            if added:
                self.outputWindow.appendInfo(f"Breakpoint added at line {line+1} in {file_name}")
            else:
                self.outputWindow.appendInfo(f"Breakpoint removed at line {line+1} in {file_name}")
        
    def openFileInTab(self, filePath):
        """
        在标签页中打开文件
        :param filePath: 文件路径
        """
        # 检查文件是否已经在打开的标签页中
        for i in range(self.tabWidget.count()):
            editor = self.tabWidget.widget(i)
            if hasattr(editor, 'filePath') and editor.filePath == filePath:
                # 文件已打开，直接切换到该标签页
                self.tabWidget.setCurrentIndex(i)
                return
                
        # 文件未打开，创建新标签页
        fileName = QFileInfo(filePath).fileName()
        editor = self.createTab(fileName, filePath)
        
        # 读取文件内容
        try:
            with open(filePath, "r", encoding="utf-8") as file:
                editor.setText(file.read())
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Cannot open file: {str(e)}")
            
        # 更新状态栏
        self.statusBar().showMessage(f"Opened {filePath}")
        
    def __initStatusBar(self):
        self.statusBar().showMessage("")
        
    def __initDocker(self):
        # 文件浏览器
        self.fileBrowser = FileBrowser()
        self.fileBrowser.openFile.connect(self.__onOpenFileDirect)
        self.fileBrowser.renameCompleted.connect(self.onRenameCompleted)
        self.fileBrowser.show()
        
        self.fileBrowserDock = QDockWidget("File Browser", self)
        self.fileBrowserDock.setWidget(self.fileBrowser)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.fileBrowserDock)
        
        # 输出窗口
        self.outputWindow = OutputWindow()
        self.addDockWidget(Qt.BottomDockWidgetArea, self.outputWindow)
        
        self.setCorner(Qt.BottomLeftCorner, Qt.LeftDockWidgetArea)
        self.setCorner(Qt.TopLeftCorner, Qt.LeftDockWidgetArea)
        self.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)
        self.setCorner(Qt.TopRightCorner, Qt.RightDockWidgetArea)
        
    def onRenameCompleted(self, message):
        """
        处理文件重命名完成事件
        :param message: 状态消息
        """
        self.statusBar().showMessage(message)
        # 同时在输出窗口中显示
        if self.outputWindow:
            self.outputWindow.appendText(message)
        
    def __onOpenFile(self):
        fileName = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt)")
        
        if fileName[0]:
            self.openFileInTab(fileName[0])
            # 在输出窗口中记录日志
            if self.outputWindow:
                self.outputWindow.appendText(f"Opened file: {fileName[0]}")
                
    def __onOpenFileDirect(self, path):
        self.openFileInTab(path)
        # 在输出窗口中记录日志
        if self.outputWindow:
            self.outputWindow.appendText(f"Opened file: {path}")
            
    def __onOpenFolder(self):
        folderName = QFileDialog.getExistingDirectory(self, "Open Folder", "")
        
        if folderName:
            self.fileBrowser.setRootPath(folderName)
            self.fileBrowser.loadRootDirectory()
            self.statusBar().showMessage("Opened " + folderName)
            # 在输出窗口中记录日志
            if self.outputWindow:
                self.outputWindow.appendText(f"Opened folder: {folderName}")