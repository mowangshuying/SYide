from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from Edit import Edit
from FileBrowser import FileBrowser

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
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
        self.edit = Edit()
        self.setCentralWidget(self.edit)
        
        self.setWindowTitle("@SYide")
        self.resize(1000, 750)
        
    def __initStatusBar(self):
        self.statusBar().showMessage("")
        
    def __initDocker(self):
        self.fileBrowser = FileBrowser()
        self.fileBrowser.show()
        
        self.fileBrowserDock = QDockWidget("File Browser", self)
        self.fileBrowserDock.setWidget(self.fileBrowser)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.fileBrowserDock)
        
        self.setCorner(Qt.BottomLeftCorner, Qt.LeftDockWidgetArea)
        self.setCorner(Qt.TopLeftCorner, Qt.LeftDockWidgetArea)
        self.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)
        self.setCorner(Qt.TopRightCorner, Qt.RightDockWidgetArea)
        
    def __onOpenFile(self):
        fileName = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt)")
        
        # if fileName.count() != 1:
            # return
        
        if fileName[0]:
            with open(fileName[0], "r") as file:
                self.edit.setText(file.read())
                
            self.statusBar().showMessage("Opened " + fileName[0])
            
    def __onOpenFolder(self):
        folderName = QFileDialog.getExistingDirectory(self, "Open Folder", "")
        
        if folderName:
            self.fileBrowser.setRootPath(folderName)
            self.fileBrowser.loadRootDirectory()
            self.statusBar().showMessage("Opened " + folderName)
