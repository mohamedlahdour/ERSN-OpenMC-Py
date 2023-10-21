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
# /////////////////////////////   X M L    S C R I P T     ////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////////

class InfoXMLScripts(QWidget):
    from .func import resize_ui
    def __init__(self,v_1,v_2,v_3,v_4,v_5,v_6,v_7,parent=None):
        super(InfoXMLScripts, self).__init__(parent)
        uic.loadUi("src/ui/InfoXMLScripts.ui", self)   
        self.v_1 = v_1
        self.v_2 = v_2
        self.v_3 = v_3
        self.v_4 = v_4
        self.v_5 = v_5
        self.v_6 = v_6
        self.v_7 = v_7
        self.directory = None
        self._initButtons()   
        self.dateTimeCreateNew.setDateTime(QDateTime.currentDateTime())
        self.dateTimeCreateNew.setDisplayFormat("dd/MM/yyyy hh:mm:ss")
        self.pushButton_2.setCheckable(True)

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
        self.directory = None
        self.newFile = False
        self.close()

    def GetDir(self):  
        self.directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.workspace.setText(self.directory)
        #open('script.dir', "w" ).write(str(self.directory))

    def showDialog(self, alert, msg):
        font = QFont('Arial', 12)
        msgBox = QMessageBox()
        msgBox.setFont(font)
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText(msg)
        msgBox.setWindowTitle(alert)
        msgBox.exec()
        
    def NewProject(self):
        self.v_4.clear()
        self.v_5.clear()
        self.v_6.clear()
        
        ProjectFolder = self.workspace.text() + '/' + self.projectName.text() + self.projectCase.text()
        if QDir(ProjectFolder).exists() :
            self.showDialog('Warning', 'Cannot create project directory, already exists or requested data not provided ! Change Project name or case id.')
        else:
            QDir().mkdir(ProjectFolder)  
            self.Fill_Header(ProjectFolder)
            

        self.directory = ProjectFolder           #############""

        self.v_7.showMessage("Project path: " + ProjectFolder)  
        self.v_7.setStyleSheet("QStatusBar{padding-left:8px;color:black;font-weight:bold;}")
        
    def Fill_Header(self, ProjectFolder): 
        filename = open(ProjectFolder + '/geometry.xml','w')
        Header_text = "<?xml version='1.0' encoding='utf-8'?>" + \
                      '\n <!-- \n ==========================================================================' +\
                      '\n Description: '+ str( self.description.text()) +\
                      '\n Case: '+ str( self.projectCase.text()) +\
                      '\n Writen by: '+ str( self.writtenBy.text()) +\
                      '\n DateTime: '+  self.dateTimeCreateNew.text()  +\
                      '\n ========================================================================== \n -->'
        filename.write(Header_text)
        filename.write('\n <geometry>')
        filename.write('      <!-- insert your code bellow this line --> \n')
        filename.write('\n </geometry>')
        filename = open(ProjectFolder + '/geometry.xml','r') 
        self.v_1.show() 
        self.v_1.setPlainText(filename.read())
        
        filename = open(ProjectFolder + '/materials.xml','w')
        filename.write(Header_text)
        filename.write('\n <materials>')
        filename.write('     <!-- insert your code bellow this line --> \n')
        filename.write('\n </materials>')
        filename = open(ProjectFolder + '/materials.xml','r')
        self.v_2.show()
        self.v_2.setPlainText(filename.read())
        
        filename = open(ProjectFolder + '/settings.xml','w')
        filename.write(Header_text)
        filename.write('\n <settings>')
        filename.write('      <!-- insert your code bellow this line --> \n')
        filename.write('\n </settings>')
        filename = open(ProjectFolder + '/settings.xml','r')
        self.v_3.show()
        self.v_3.setPlainText(filename.read())
        
        if self.checkBox_4.isChecked() == True:
            filename = open(ProjectFolder + '/tallies.xml','w')
            filename.write(Header_text)
            filename.write('\n <tallies>')
            filename.write('        <!-- insert your code bellow this line --> \n')
            filename.write('\n </tallies>')
            filename = open(ProjectFolder + '/tallies.xml','r')
            self.v_4.show()
            self.v_4.setPlainText(filename.read())
        if self.checkBox_5.isChecked() == True:
            filename = open(ProjectFolder + '/plots.xml','w')
            filename.write(Header_text)
            filename.write('\n <plots>')
            filename.write('       <!-- insert your code bellow this line --> \n')
            filename.write('\n </plots>')
            filename = open(ProjectFolder + '/plots.xml','r')
            self.v_5.show()
            self.v_5.setPlainText(filename.read())
        if self.checkBox_6.isChecked() == True:
            filename = open(ProjectFolder + '/cmfd.xml','w')
            filename.write(Header_text)
            filename.write('\n <cmfd>')
            filename.write('       <!-- insert your code bellow this line --> \n')
            filename.write('\n </cmfd>')
            filename = open(ProjectFolder + '/cmfd.xml','r')
            self.v_6.show()
            self.v_6.setPlainText(filename.read())           
        self.close()
