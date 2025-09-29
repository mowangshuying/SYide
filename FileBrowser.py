from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os

class FileBrowser(QWidget):
    # 定义文件双击信号
    fileDoubleClicked = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initUI()
        
    def __initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建文件树
        self.fileTree = QTreeWidget()
        self.fileTree.setHeaderHidden(True)
        self.fileTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.fileTree.customContextMenuRequested.connect(self.showContextMenu)
        self.fileTree.itemExpanded.connect(self.loadDirectory)
        self.fileTree.itemDoubleClicked.connect(self.onItemDoubleClicked)
        
        # 添加到布局
        layout.addWidget(self.fileTree)
        
        # 设置初始目录为当前工作目录
        self.currentPath = QDir.currentPath()
        self.loadRootDirectory()
        
    def loadRootDirectory(self):
        """
        加载根目录
        """
        self.fileTree.clear()
        rootItem = QTreeWidgetItem(self.fileTree)
        rootItem.setText(0, QDir(self.currentPath).dirName() or self.currentPath)
        rootItem.setData(0, Qt.UserRole, self.currentPath)
        rootItem.setIcon(0, self.style().standardIcon(QStyle.SP_DirIcon))
        
        # 添加一个子项占位符，使项目可以展开
        placeholder = QTreeWidgetItem(rootItem)
        placeholder.setText(0, "Loading...")
        
    def loadDirectory(self, item):
        """
        加载指定目录的内容
        """
        # 如果不是目录，直接返回
        path = item.data(0, Qt.UserRole)
        if not os.path.isdir(path):
            return
            
        # 清除占位符
        item.takeChildren()
        
        try:
            # 获取目录内容
            entries = QDir(path).entryInfoList(
                QDir.AllEntries | QDir.NoDotAndDotDot | QDir.Hidden,
                QDir.DirsFirst | QDir.Name
            )
            
            for entry in entries:
                childItem = QTreeWidgetItem(item)
                childItem.setText(0, entry.fileName())
                childItem.setData(0, Qt.UserRole, entry.absoluteFilePath())
                
                # 设置图标
                if entry.isDir():
                    childItem.setIcon(0, self.style().standardIcon(QStyle.SP_DirIcon))
                    # 添加占位符子项
                    placeholder = QTreeWidgetItem(childItem)
                    placeholder.setText(0, "Loading...")
                else:
                    childItem.setIcon(0, self.style().standardIcon(QStyle.SP_FileIcon))
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法读取目录: {str(e)}")
            
    def onItemDoubleClicked(self, item, column):
        """
        处理项目双击事件
        """
        path = item.data(0, Qt.UserRole)
        if os.path.isfile(path):
            self.fileDoubleClicked.emit(path)
        elif os.path.isdir(path):
            self.fileTree.expandItem(item)
            
    def showContextMenu(self, position):
        """
        显示右键菜单
        """
        item = self.fileTree.itemAt(position)
        if not item:
            return
            
        path = item.data(0, Qt.UserRole)
        menu = QMenu()
        
        if os.path.isdir(path):
            openInTerminalAction = QAction("在终端中打开", self)
            openInTerminalAction.triggered.connect(lambda: self.openInTerminal(path))
            menu.addAction(openInTerminalAction)
            
            menu.addSeparator()
            
        copyPathAction = QAction("复制路径", self)
        copyPathAction.triggered.connect(lambda: self.copyPath(path))
        menu.addAction(copyPathAction)
        
        menu.exec_(self.fileTree.viewport().mapToGlobal(position))
        
    def copyPath(self, path):
        """
        复制路径到剪贴板
        """
        clipboard = QApplication.clipboard()
        clipboard.setText(path)
        
    def openInTerminal(self, path):
        """
        在终端中打开目录
        """
        try:
            if os.name == 'nt':  # Windows
                os.startfile(path)
            elif os.name == 'posix':  # Linux/Mac
                import subprocess
                subprocess.Popen(['gnome-terminal', '--working-directory', path])
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法在终端中打开: {str(e)}")
            
    def goBack(self):
        """
        返回上级目录
        """
        parentPath = QDir(self.currentPath).absolutePath()
        parentDir = QDir(parentPath).cdUp()
        if parentDir:
            self.currentPath = QDir(parentPath).absolutePath()
            self.pathEdit.setText(self.currentPath)
            self.loadRootDirectory()
            
    def refresh(self):
        """
        刷新当前目录
        """
        self.loadRootDirectory()
        
    def changePath(self):
        """
        更改当前路径
        """
        newPath = self.pathEdit.text()
        if os.path.exists(newPath):
            self.currentPath = newPath
            self.loadRootDirectory()
        else:
            QMessageBox.warning(self, "错误", "路径不存在")
            
    def setRootPath(self, path):
        """
        设置根路径
        """
        if os.path.exists(path):
            self.currentPath = path
            self.pathEdit.setText(path)
            self.loadRootDirectory()

# 使用示例
if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = QMainWindow()
    window.setWindowTitle("文件浏览器")
    window.resize(400, 600)
    
    # 创建文件浏览器
    fileBrowser = FileBrowser()
    
    # 连接文件双击信号
    def onFileDoubleClicked(filePath):
        print(f"打开文件: {filePath}")
        
    fileBrowser.fileDoubleClicked.connect(onFileDoubleClicked)
    
    window.setCentralWidget(fileBrowser)
    window.show()
    
    sys.exit(app.exec_())