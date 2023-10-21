#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5 import Qt


# /////////////////////////////////////////////////////////////////////////////////////
# /////////////////////////////   P Y T H O N    S C R I P T     //////////////////////
# /////////////////////////////////////////////////////////////////////////////////////

class InfoPythonScript(QWidget):
    from .func import resize_ui
    def __init__(self,v_1,parent=None):
        super(InfoPythonScript, self).__init__(parent)
        uic.loadUi("src/ui/InfoPythonScript.ui", self)   
        self.v_1 = v_1
        self.directory = ''
        self._initButtons()  
        self.Header_text = '<!-- hi -->'
        self.dateTimeCreateNew.setDateTime(QDateTime.currentDateTime())
        self.dateTimeCreateNew.setDisplayFormat("dd/MM/yyyy hh:mm:ss")

        # to show window at the middle of the screen and resize it to the screen size
        self.resize_ui()
    
    def _createStatusBar(self):
        self.statusbar = self.statusBar()
        # Adding a temporary message
        self.statusbar.showMessage("Ready", 3000)

    def _initButtons(self):     
        self.pBCreateNew.clicked.connect(self.NewProject)   
        self.pushButton_2.clicked.connect(self.Exit)
        self.pushButton_3.clicked.connect(self.GetDir)

    def Exit(self):
        self.directory = ''
        self.close()   
    
    def GetDir(self):  
        self.directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.workspace.setText(self.directory)

    def showDialog(self, alert, msg):
        font = QFont('Arial', 12)
        msgBox = QMessageBox()
        msgBox.setFont(font)
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText(msg)
        msgBox.setWindowTitle(alert)
        msgBox.exec()
        
    def NewProject(self):
             
        ProjectFolder = self.workspace.text() + '/' + self.projectName.text() + self.projectCase.text()
        if QDir(ProjectFolder).exists() :
            self.showDialog('Warning', 'Cannot create project directory, already exists or requested data not provided ! Change Project name or case id.')
        else:
            QDir().mkdir(ProjectFolder)  
            self.Fill_Header(ProjectFolder)

        self.directory = ProjectFolder
        
    def Fill_Header(self, ProjectFolder): #
        self.filename = ProjectFolder + '/build_xml.py'
        self.file = open(self.filename,'w')
        Header_text0 = "#! /usr/bin/python3 \n#! -*- coding:utf-8 -*- \nimport openmc \n''' \n"
        self.Header_text = " =========================================================================="+\
                      '\n Description: '+ str( self.description.text()) + \
                      '\n Case: ' + str(self.projectCase.text()) + \
                      '\n Writen by: ' + str( self.writtenBy.text()) + \
                      '\n DateTime: ' + self.dateTimeCreateNew.text() + \
                      "\n =========================================================================="
        cursor = self.v_1.textCursor()
        cursor.insertText(Header_text0 + self.Header_text + "\n'''")

        self.file.write(Header_text0 + self.Header_text  + "\n'''")
        self.close()
