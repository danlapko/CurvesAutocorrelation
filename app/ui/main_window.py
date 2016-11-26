""" This module serves for displaying main window using QT library"""
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gazprom.ui'
#
# Created: Tue Mar 29 19:36:34 2016
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox

from app.domain import main_context
from app.ui import tree_widget
from app.ui.tab_2d_map import Tab2DMap
from app.ui.tab_sections import Sections
from app.util.config import Config


class MainWindow(QMainWindow):
    """ Main window frame """
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def setupUi(self, MainWindow):
        """ sets static settings and parameters of MainWindow"""
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1080, 670)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.treeWidget = tree_widget.TreeWidget(self.centralwidget)


        self.horizontalLayout.addWidget(self.treeWidget)
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_2d_map = Tab2DMap()
        self.tab_2d_map.setObjectName("tab_2d_map")
        self.tabWidget.addTab(self.tab_2d_map, "")

        self.tab_sections = Sections()
        self.tab_sections.setObjectName('tab_sections')
        self.tabWidget.addTab(self.tab_sections, "")

        self.horizontalLayout.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 640, 27))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.actionImport = QtWidgets.QAction(MainWindow)
        self.actionImport.setObjectName("actionImport")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen_project = QtWidgets.QAction(MainWindow)
        self.actionOpen_project.setObjectName("actionOpen_project")
        self.actionSave_project = QtWidgets.QAction(MainWindow)
        self.actionSave_project.setObjectName("actionSave_project")
        self.actionSave_project_as = QtWidgets.QAction(MainWindow)
        self.actionSave_project_as.setShortcut("")
        self.actionSave_project_as.setObjectName("actionSave_project_as")
        self.actionExport = QtWidgets.QAction(MainWindow)
        self.actionExport.setObjectName("actionExport")
        self.actionClose = QtWidgets.QAction(MainWindow)
        self.actionClose.setObjectName("actionClose")
        self.actionNew_project = QtWidgets.QAction(MainWindow)
        self.actionNew_project.setObjectName("actionNew_project")

        self.menuFile.addAction(self.actionNew_project)
        self.menuFile.addAction(self.actionOpen_project)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave_project)
        self.menuFile.addAction(self.actionSave_project_as)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionImport)
        self.menuFile.addAction(self.actionExport)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionClose)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)

        # ----------- My zone ------------

        self.actionImport.triggered.connect(lambda: self.treeWidget.on_actionImport_triggered(self.menuFile))
        self.actionClose.triggered.connect(lambda: self.close())
        self.actionNew_project.triggered.connect(self.on_actionNewProject_triggered)
        self.actionSave_project_as.triggered.connect(self.on_actionSave_project_as_triggered)
        self.actionSave_project.triggered.connect(self.on_actionSave_project_triggered)
        self.actionOpen_project.triggered.connect(self.on_actionOpen_project_triggered)

        # QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        """ accessory method for setupUI() """
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Gazprom"))

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2d_map), _translate("MainWindow", "2d map"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_sections), _translate("MainWindow", "Sections"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionImport.setText(_translate("MainWindow", "Import"))
        self.actionImport.setShortcut(_translate("MainWindow", "Ctrl+I"))
        self.actionOpen_project.setText(_translate("MainWindow", "Open project"))
        self.actionOpen_project.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionSave_project.setText(_translate("MainWindow", "Save project"))
        self.actionSave_project.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionSave_project_as.setText(_translate("MainWindow", "Save project as"))
        self.actionExport.setText(_translate("MainWindow", "Export"))
        self.actionExport.setShortcut(_translate("MainWindow", "Ctrl+E"))
        self.actionClose.setText(_translate("MainWindow", "Close"))
        self.actionNew_project.setText(_translate("MainWindow", "New project"))
        self.actionNew_project.setShortcut(_translate("MainWindow", "Ctrl+N"))

        # ----------- My zone -----------
        self.treeWidget.reset_content()

    def on_actionOpen_project_triggered(self):
        """ executes on menu 'open project' item triggered """
        file_name, file_type = QFileDialog.getOpenFileName(
            self,
            "Select project to open",
            "/home/danila/PycharmProjects/gazprom/gazprom_new/data",
            "project file *.gpprj(*.gpprj)")
        if file_name:
            main_context.deserialize(file_name)
        self.treeWidget.reset_content()

    def on_actionNewProject_triggered(self):
        """ executes on menu 'new project' item triggered """
        main_context.reset_context()
        self.treeWidget.reset_content()

    def on_actionSave_project_as_triggered(self):
        """ executes on menu 'save project as' item triggered """
        dialog = QFileDialog
        file_name, file_type = dialog.getSaveFileName(self, 'Save project as',
                                                      Config.default_dir_path + "untitled.gpprj",
                                                      "*.gpprj(*.gpprj)")
        if file_name:
            if (file_name[-6:] != '.gpprj') or (len(file_name) - len(Config.default_dir_path) < 7):
                QMessageBox(QMessageBox.Information, 'Rejected', "         Project haven't been stored!\n"
                                                                 '  The extends of the file should be "*.gpprj"\n'
                                                                 ' and file name should has at least one letter.',
                            QMessageBox.Ok, self).show()
                return
            main_context.serialize(file_name)

    def on_actionSave_project_triggered(self):
        """ executes on menu 'save project' item triggered """
        if main_context.project_file is not None:
            main_context.serialize(main_context.project_file)
        else:
            self.on_actionSave_project_as_triggered()
