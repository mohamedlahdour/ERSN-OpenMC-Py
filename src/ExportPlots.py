#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from src.syntax_py import Highlighter
from src.PyEdit import TextEdit, NumberBar  

class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))
        pass

    def flush(self):
        pass

class ExportPlots(QWidget):
    from .func import resize_ui, showDialog, Exit, Find_string
    def __init__(self, v_1, Plot, Plot_ID, file_name, parent=None):
        super(ExportPlots, self).__init__(parent)
        #sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        #sys.stderr = EmittingStream(textWritten=self.normalOutputWritten)
        uic.loadUi("src/ui/ExportPlots.ui", self)
        self.v_1 = v_1 
        self.text_inserted = False
        self.Insert_Header = True
        self._initButtons()
        if file_name == '':
            self.plots_file_name = 'plots'
        else:
            self.plots_file_name = file_name
        self.X_LE.setText("0")
        self.Y_LE.setText("0")
        self.Z_LE.setText("0")
        self.plot_suffix = '_plot'
        self.int_validator = QRegExpValidator(QRegExp(r'[0-9]+'))
        self.PlotId_LE.setValidator(self.int_validator)
        self.validator = QDoubleValidator(self)
        for LineEd in [self.X_LE, self.Y_LE, self.Z_LE, self.X_Width_LE, self.Y_Width_LE, self.Z_Width_LE]:
            LineEd.setValidator(self.validator)
        self.plot_name_list = Plot
        self.plot_id_list = Plot_ID
        n = len(Plot)
        self.Plot_ID = int(n) + 1
        self.PlotId_LE.setText(str(self.Plot_ID))
        if self.AddPlotId_CB.isChecked():
            self.PlotName_LE.setText(self.plot_suffix + str(self.PlotId_LE.text()))
        else:
            self.PlotName_LE.setText(self.plot_suffix)
        self.Z_Width_LE.setEnabled(False)
        self.Z_Pixels_LE.setEnabled(False)
        self.text_inserted = False
        self.liste = []
        for item in [self.Basis_CB, self.label_1, self.Z_Width_LE, self.Z_Pixels_LE]:
            item.setEnabled(True)
        for item in [self.Z_Width_LE, self.Z_Pixels_LE]:
            item.setEnabled(False)

        # add new editor
        self.plainTextEdit = TextEdit()
        self.plainTextEdit.setWordWrapMode(QTextOption.NoWrap)
        self.numbers = NumberBar(self.plainTextEdit)
        layoutH = QHBoxLayout()
        #layoutH.setSpacing(1.5)
        layoutH.addWidget(self.numbers)
        layoutH.addWidget(self.plainTextEdit)
        self.EditorLayout.addLayout(layoutH, 0, 0)
        
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        #sys.stderr = EmittingStream(textWritten=self.normalOutputWritten)
        # to show window at the middle of the screen and resize it to the screen size
        self.resize_ui()
         
    def _initButtons(self):
        self.plot2D_RB.toggled.connect(self.activate_widgets)
        self.Basis_CB.currentIndexChanged.connect(self.activate_widgets)
        self.PlotId_LE.textChanged.connect(self.sync_plot_id)
        self.AddPlotId_CB.stateChanged.connect(self.sync_plot_id)
        self.PlotName_LE.textChanged.connect(self.sync_plot_name1)
        #self.PlotName_LE.textChanged.connect(self.sync_plot_name)

        self.CreatePlot_PB.clicked.connect(self.Add_Plot)
        self.ExportData_PB.clicked.connect(self.Export_to_Main_Window)
        self.ClearData_PB.clicked.connect(self.Clear_Output)
        self.Exit_PB.clicked.connect(self.Exit)


    def sync_plot_name1(self):
        import string
        pos = self.PlotName_LE.cursorPosition()
        self.PlotName_LE.setCursorPosition(pos)
        self.plot_suffix = self.PlotName_LE.text().rstrip(string.digits)

    def sync_plot_name(self):
        import string
        self.plot_suffix = self.PlotName_LE.text().rstrip(string.digits)
        if self.AddPlotId_CB.isChecked():
            self.PlotName_LE.setText(self.plot_suffix + str(self.Plot_ID))
        else:
            self.plot_suffix = self.PlotName_LE.text().rstrip(string.digits)
            self.PlotName_LE.setText(self.plot_suffix)

    def sync_plot_id(self):
        import string
        if self.PlotId_LE.text():
            self.Plot_ID = int(self.PlotId_LE.text())
            if self.AddPlotId_CB.isChecked():
                self.PlotName_LE.setText(self.plot_suffix + str(self.Plot_ID))
            else:
                self.plot_suffix = self.PlotName_LE.text().rstrip(string.digits)
                self.PlotName_LE.setText(self.plot_suffix)

    def activate_widgets(self):
        for item in [self.X_Width_LE, self.X_Pixels_LE, self.Y_Width_LE, self.Y_Pixels_LE, self.Z_Width_LE,
                     self.Z_Pixels_LE]:
            item.clear()
        if self.plot2D_RB.isChecked():
            for item in [self.Basis_CB, self.label_1]:
                item.setEnabled(True)
            if self.Basis_CB.currentText() == 'xy':
                for item in [self.X_Width_LE, self.X_Pixels_LE, self.Y_Width_LE, self.Y_Pixels_LE]:
                    item.setEnabled(True)
                for item in [self.Z_Width_LE, self.Z_Pixels_LE]:
                    item.setEnabled(False)
            elif self.Basis_CB.currentText() == 'xz':
                for item in [self.X_Width_LE, self.X_Pixels_LE, self.Z_Width_LE, self.Z_Pixels_LE]:
                    item.setEnabled(True)
                for item in [self.Y_Width_LE, self.Y_Pixels_LE]:
                    item.setEnabled(False)
            elif self.Basis_CB.currentText() == 'yz':
                for item in [self.Y_Width_LE, self.Y_Pixels_LE, self.Z_Width_LE, self.Z_Pixels_LE]:
                    item.setEnabled(True)
                for item in [self.X_Width_LE, self.X_Pixels_LE]:
                    item.setEnabled(False)
        else:
            for item in [self.Basis_CB, self.label_1]:
                item.setEnabled(False)
            for item in [self.X_Width_LE, self.X_Pixels_LE, self.Y_Width_LE, self.Y_Pixels_LE, self.Z_Width_LE, self.Z_Pixels_LE]:
                item.setEnabled(True)

    def Insert_Header_Text(self):
        self.Find_string(self.plainTextEdit, "import openmc")
        self.v_1.moveCursor(QTextCursor.End)
        if self.Insert_Header:
            self.Find_string(self.v_1, "import openmc")
            if self.Insert_Header:
                cursor = self.v_1.textCursor()
                cursor.setPosition(0)
                self.v_1.setTextCursor(cursor)
                self.v_1.insertPlainText('import openmc\n')
        self.Find_string(self.plainTextEdit, "plots.xml")
        if self.Insert_Header:
            self.Find_string(self.v_1, "plots.xml")
            if self.Insert_Header:
                self.v_1.insertPlainText('\n############################################################################### \n')
                self.v_1.insertPlainText('#                 Exporting to OpenMC plots.xml file                        \n')
                self.v_1.insertPlainText('###############################################################################\n')
        self.Insert_Header = False

    def Add_Plot(self):
        self.Insert_Header_Text()
        if self.PlotName_LE.text() == '':
            self.showDialog('Warning', 'Cannot create plot, enter name first !')
            return
        elif self.PlotId_LE.text() == '':
            self.showDialog('Warning', 'Cannot create plot, enter plot id first !')
            return
        if self.PlotName_LE.text() in self.plot_name_list:
            self.showDialog('Warning', 'Plot name already used, select new name !')
            return
        if self.PlotId_LE.text() in self.plot_id_list:
            self.showDialog('Warning', 'Plot id already used, select new id !')
            return
        print ('\n'+str(self.PlotName_LE.text()),"= openmc.Plot(plot_id=",str(self.PlotId_LE.text()),")")
        print (str(self.PlotName_LE.text())+'.filename =',"'"+str(self.PlotName_LE.text())+"'")
        print (str(self.PlotName_LE.text())+'.origin =',"("+str(self.X_LE.text())+","+
               str(self.Y_LE.text())+","+str(self.Z_LE.text())+")")
        if self.plot2D_RB.isChecked():
            if self.Basis_CB.currentText() == 'xy':
                print (str(self.PlotName_LE.text())+'.width =',"("+str(self.X_Width_LE.text())+","+
                       str(self.Y_Width_LE.text())+")")
                print (str(self.PlotName_LE.text())+'.pixels =',"("+str(self.X_Pixels_LE.text())+","+
                       str(self.Y_Pixels_LE.text())+")")
            elif self.Basis_CB.currentText() == 'xz':
                print (str(self.PlotName_LE.text())+'.width =',"("+str(self.X_Width_LE.text())+","+
                       str(self.Z_Width_LE.text())+")")
                print (str(self.PlotName_LE.text())+'.pixels =',"("+str(self.X_Pixels_LE.text())+","+
                       str(self.Z_Pixels_LE.text())+")")
            elif self.Basis_CB.currentText() == 'yz':
                print (str(self.PlotName_LE.text())+'.width =',"("+str(self.Y_Width_LE.text())+","+
                       str(self.Z_Width_LE.text())+")")
                print (str(self.PlotName_LE.text())+'.pixels =',"("+str(self.Y_Pixels_LE.text())+","+
                       str(self.Z_Pixels_LE.text())+")")
        else:
            print(str(self.PlotName_LE.text()) + '.width =', "(" + str(self.X_Width_LE.text()) + "," +
                  str(self.Y_Width_LE.text()) + "," + self.Z_Width_LE.text() + ")")
            print(str(self.PlotName_LE.text()) + '.pixels =', "(" + str(self.X_Pixels_LE.text()) + "," +
                  str(self.Y_Pixels_LE.text()) + "," + self.Z_Pixels_LE.text() + ")")
            print(str(self.PlotName_LE.text())+'.type ="voxel"')
        print (str(self.PlotName_LE.text())+'.color_by =',"'"+self.ColorBy_CB.currentText()+"'")
        if self.plot2D_RB.isChecked():
            print (str(self.PlotName_LE.text())+'.basis =',"'"+self.Basis_CB.currentText()+"'")

        self.plot_name_list.append(self.PlotName_LE.text())
        self.plot_id_list.append(self.PlotId_LE.text())
        self.Plot_ID = int(self.plot_id_list[-1]) + 1
        self.PlotId_LE.setText(str(self.Plot_ID))
        self.PlotName_LE.setText('_plot')
        self.sync_plot_id()

    def Export_to_Main_Window(self):
        string_to_find = self.plots_file_name + '.export_to_xml()'
        self.Find_string(self.v_1, string_to_find)
        cursor = self.v_1.textCursor()
        self.plainTextEdit.moveCursor(QTextCursor.End)
        if self.Insert_Header:
            print('\n' + self.plots_file_name + ' = openmc.Plots(','['+', '.join(self.plot_name_list)+']',')')
            print (string_to_find)
            cursor.insertText(self.plainTextEdit.toPlainText())
        else:
            document = self.v_1.toPlainText()
            lines = document.split('\n')
            for line in lines:
                if ("openmc.Plots" in line):
                    lines.remove(line)
                    document = self.v_1.toPlainText().replace(line,"")
            print('\n' + self.plots_file_name + ' = openmc.Plots(','['+', '.join(self.plot_name_list)+']',')')
            print(string_to_find)
            document = document.replace(string_to_find,self.plainTextEdit.toPlainText())
            self.v_1.clear()
            cursor = self.v_1.textCursor()
            cursor.insertText(document)
        self.text_inserted = True
        self.plainTextEdit.clear()

    def Clear_Output(self):
        if self.text_inserted:
            self.plainTextEdit.clear()
        else:
            if self.plainTextEdit:
                qm = QMessageBox
                ret = qm.question(self, 'Warning', 'Do you really want to clear data ?', qm.Yes | qm.No)
                if ret == qm.Yes:
                    self.plainTextEdit.clear()
                elif ret == qm.No:
                    pass
            else:
                self.plainTextEdit.clear()

    def normalOutputWritten(self, text):
        self.highlighter = Highlighter(self.plainTextEdit.document())
        cursor = self.plainTextEdit.textCursor()
        cursor.insertText(text)