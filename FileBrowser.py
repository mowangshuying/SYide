from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os

class FileBrowser(QWidget):
    # 定义文件双击信号
    # fileDoubleClicked = pyqtSignal(str)
    
    openFile = pyqtSignal(str)
    renameCompleted = pyqtSignal(str)  # 添加重命名完成信号
    
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
        # self.fileTree.itemDoubleClicked.connect(self.onItemDoubleClicked)
        self.fileTree.itemClicked.connect(self.onItemClicked)
        
        # 添加键盘事件处理
        self.fileTree.keyPressEvent = self.treeKeyPressEvent
        
        # 添加到布局
        layout.addWidget(self.fileTree)
        
        # 设置初始目录为当前工作目录
        self.currentPath = QDir.currentPath()
        self.loadRootDirectory()
        
    def treeKeyPressEvent(self, event):
        """处理文件树的键盘按键事件"""
        if event.key() == Qt.Key_F2:
            self.renameSelectedItem()
        elif event.key() == Qt.Key_Delete:
            self.deleteSelectedItem()
        else:
            # 调用原始的keyPressEvent处理其他按键
            QTreeWidget.keyPressEvent(self.fileTree, event)
            
    def deleteSelectedItem(self):
        """删除选中的项目"""
        currentItem = self.fileTree.currentItem()
        if not currentItem:
            return
            
        path = currentItem.data(0, Qt.UserRole)
        if not os.path.exists(path):
            return
            
        # 获取项目名称
        name = currentItem.text(0)
        
        # 确认删除
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            f"确定要删除 '{name}' 吗？\n此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 执行删除
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    # 递归删除目录
                    self.removeDirectory(path)
                    
                # 从树中移除项目
                parent = currentItem.parent()
                if parent:
                    parent.removeChild(currentItem)
                else:
                    index = self.fileTree.indexOfTopLevelItem(currentItem)
                    if index >= 0:
                        self.fileTree.takeTopLevelItem(index)
                        
                self.renameCompleted.emit(f"已删除: {name}")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"删除失败: {str(e)}")
                
    def removeDirectory(self, path):
        """
        递归删除目录
        :param path: 目录路径
        """
        try:
            # 使用shutil.rmtree更安全地删除目录
            import shutil
            shutil.rmtree(path)
        except Exception as e:
            raise Exception(f"无法删除目录 {path}: {str(e)}")
            
    def renameSelectedItem(self):
        """重命名选中的项目"""
        currentItem = self.fileTree.currentItem()
        if not currentItem:
            return
            
        path = currentItem.data(0, Qt.UserRole)
        if not os.path.exists(path):
            return
            
        # 使用QInputDialog来获取新名称
        oldName = currentItem.text(0)
        newName, ok = QInputDialog.getText(self, "重命名", "新名称:", QLineEdit.Normal, oldName)
        
        if not ok or not newName:
            return  # 用户取消或输入空名称
            
        # 检查名称是否与原名称相同
        if newName == oldName:
            return
            
        # 检查名称是否合法
        if "/" in newName or "\\" in newName or ":" in newName or "*" in newName or "?" in newName or "\"" in newName or "<" in newName or ">" in newName or "|" in newName:
            QMessageBox.warning(self, "错误", "文件名不能包含以下字符: / \\ : * ? \" < > |")
            return
            
        # 构造新路径
        dirPath = os.path.dirname(path)
        newPath = os.path.join(dirPath, newName)
        
        # 检查同名文件/文件夹是否已存在
        if os.path.exists(newPath):
            QMessageBox.warning(self, "错误", f"文件或文件夹 '{newName}' 已存在")
            return
            
        # 执行重命名
        try:
            os.rename(path, newPath)
            # 更新项目文本和数据
            currentItem.setText(0, newName)
            currentItem.setData(0, Qt.UserRole, newPath)
            self.renameCompleted.emit(f"已重命名: {oldName} -> {newName}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"重命名失败: {str(e)}")
            
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
            
    def onItemClicked(self, item, column):
        """
        处理项目点击事件
        """
        # 获取到文件路径
        path = item.data(0, Qt.UserRole)
        if os.path.isfile(path):
            self.openFile.emit(path)
        # elif os.path.isdir(path):
            # self.fileTree.expandItem(item)
        
    # def onItemDoubleClicked(self, item, column):
    #     """
    #     处理项目双击事件
    #     """
    #     path = item.data(0, Qt.UserRole)
    #     if os.path.isfile(path):
    #         self.fileDoubleClicked.emit(path)
    #     elif os.path.isdir(path):
    #         self.fileTree.expandItem(item)
            
    def showContextMenu(self, position):
        """
        显示右键菜单
        """
        item = self.fileTree.itemAt(position)
        if not item:
            return
            
        path = item.data(0, Qt.UserRole)
        menu = QMenu()
        
        # 添加重命名选项到上下文菜单
        renameAction = QAction("重命名", self)
        renameAction.triggered.connect(self.renameSelectedItem)
        menu.addAction(renameAction)
        
        # 添加删除选项到上下文菜单
        deleteAction = QAction("删除", self)
        deleteAction.triggered.connect(self.deleteSelectedItem)
        menu.addAction(deleteAction)
        
        menu.addSeparator()
        
        if os.path.isdir(path):
            openInTerminalAction = QAction("在终端中打开", self)
            openInTerminalAction.triggered.connect(lambda: self.openInTerminal(path))
            menu.addAction(openInTerminalAction)
            
            menu.addSeparator()
            
        # 打开文件所在目录，UI显示
        showInExplorerAction = QAction("在资源管理器中打开", self)
        showInExplorerAction.triggered.connect(lambda: os.startfile(os.path.dirname(path)))
        menu.addAction(showInExplorerAction)

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
            self.loadRootDirectory()

