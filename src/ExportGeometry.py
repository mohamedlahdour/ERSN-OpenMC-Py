#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
import re
import string
from functools import partial
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from src.ExportMaterials import ExportMaterials
from src.PyEdit import TextEdit, NumberBar  
from src.syntax_py import Highlighter
from src.XMLHighlighter import XMLHighlighter

class ExportGeometry(QWidget):
    from .func import resize_ui, showDialog, Exit
    def __init__(self, v_1, regions, surf, surf_id, cell, cell_id, mat, mat_id, univ, univ_id, C_in_U, lat, lat_id, parent=None):
        super(ExportGeometry, self).__init__(parent)
        uic.loadUi("src/ui/ExportGeometry.ui", self)
        try:
            from openmc import __version__
            self.openmc_version = int(__version__.split('-')[0].replace('.', ''))
        except:
            self.showDialog('Warning', 'OpenMC not yet installed !')
            self.openmc_version = 0
 
        # add new editor
        self.plainTextEdit = TextEdit()
        self.plainTextEdit.setWordWrapMode(QTextOption.NoWrap)
        self.numbers = NumberBar(self.plainTextEdit)
        layoutH = QHBoxLayout()
        #layoutH.setSpacing(1.5)
        layoutH.addWidget(self.numbers)
        layoutH.addWidget(self.plainTextEdit)
        self.EditorLayout.addLayout(layoutH, 0, 0)
        # 
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        #sys.stderr = EmittingStream(textWritten=self.normalOutputWritten)
        self._initButtons() 
        self.v_1 = v_1        
        self.materials_name_list = mat
        self.materials_id_list = mat_id
        self.surface_name_list = surf
        self.surface_id_list = surf_id
        self.cell_name_list = cell
        self.cell_id_list = cell_id
        self.regions = regions
        self.cells_in_universes = C_in_U
        self.universe_name_list = univ
        self.universe_id_list = univ_id
        self.lattice_name_list = lat
        self.lattice_id_list = lat_id
        #
        self.Instanciate_Lists()
        self.Surfaces_List = ['openmc.Plane', 'openmc.XPlane', 'openmc.YPlane', 'openmc.ZPlane', 'openmc.Sphere', 'openmc.XCylinder', 
                                'openmc.YCylinder', 'openmc.ZCylinder', 'openmc.Cone', 'openmc.XCone', 'openmc.YCone', 'openmc.ZCone',
                                'openmc.Quadric', 'openmc.XTorus', 'openmc.YTorus', 'openmc.ZTorus', 'rectangular_prism', 'hexagonal_prism']
        if self.openmc_version >= 141:
            self.Surfaces_List[-2] = 'model.RectangularPrism'
            self.Surfaces_List[-1] = 'model.HexagonalPrism'

        self.comboBox.addItem('Select Surface Type')
        self.comboBox.addItems(self.Surfaces_List)
        self.comboBox.setItemData(17,"The rectangonal_prism(...) function has been replaced by the RectangularPrism(...) class "
                                             "in version 0.14.1 of OpenMC.", QtCore.Qt.ToolTipRole)
        self.comboBox.setItemData(18,"The hexagonal_prism(...) function has been replaced by the HexagonalPrism(...) class "
                                             "in version 0.14.1 of OpenMC.", QtCore.Qt.ToolTipRole)
        # to show window at the middle of the screen
        self.resize_ui()

    def Instanciate_Lists(self):
        self.lineEdit_18.setValidator(QIntValidator())
        self.validator = QDoubleValidator(self)

        for LE in [self.lineEdit_19, self.lineEdit_20, self.lineEdit_21, self.lineEdit_22, self.lineEdit_23, self.lineEdit_24]:
            LE.setValidator(self.validator)
        self.Liste = [self.lineEdit, self.lineEdit_2, self.lineEdit_3, self.lineEdit_4, self.lineEdit_5,
                      self.lineEdit_6, self.lineEdit_7, self.lineEdit_8, self.lineEdit_9, self.lineEdit_10]
        self.Liste1 = [self.label, self.label_2, self.label_3, self.label_4, self.label_5,
                       self.label_6, self.label_7, self.label_8, self.label_9, self.label_10]
        self.Liste1_LB = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K']
        for lbl in self.Liste1:
            lbl.setAlignment(QtCore.Qt.AlignCenter)
        for LE in self.Liste:
            LE.setValidator(self.validator)
        self.lineEdit_12.setValidator(QIntValidator())
        self.lineEdit_14.setValidator(QIntValidator())
        self.lineEdit_15.setValidator(QIntValidator())
        for item in [self.lineEdit_19, self.lineEdit_24, self.spinBox_3, self.label_21, self.label_26]:
            item.setEnabled(False)
        self.comboBox_6.show()
        self.Modify_TextEdit_PB.hide()        
        self.spinBox.setValue(1)
        self.spinBox_2.setValue(1)
        self.spinBox_3.setValue(1)
        self.text_inserted = False
        self.modify_universes = False

        self.surface_name_sub_list = []
        self.surface_id_sub_list = []
        self.cells = []
        self.universes = []
        self.cell_name_sub_list = []
        self.cell_id_sub_list = []
        self.universe_name_sub_list = []
        self.universe_id_sub_list = []

        self.surface_suffix = 'Surf'
        self.cell_suffix = 'Cell'
        self.universe_suffix = 'Univ'
        self.lattice_suffix = 'Lat'
        # Surface id
        if self.surface_id_list:
            n = self.surface_id_list[-1]
        else:
            n = 0
        self.surface_id = int(n) + 1  
        # Cell id      
        if self.cell_id_list:
            n = self.cell_id_list[-1]
        else:
            n = 0
        self.cell_id = int(n) + 1
        # Universe id
        if len(self.universe_id_list) > 0:
            n = int(self.universe_id_list[-1]) + 1
            while True:
                if str(n) not in self.universe_id_list and str(n) not in self.lattice_id_list :
                    self.universe_id = n
                    break
                else:
                    n += 1
        else:
            self.universe_id = 1
        # Lattice id
        if len(self.lattice_id_list) > 0:
            n = int(self.lattice_id_list[-1]) + 1
            while True:
                if str(n) not in self.lattice_id_list and str(n) not in self.universe_id_list:
                    self.lattice_id = n
                    break
                else:
                    n += 1
        else:
            if len(self.universe_id_list) > 0:
                n = int(self.universe_id_list[-1]) + 1
                while True:
                    if str(n) not in self.universe_id_list:
                        self.lattice_id = n
                        break
                    else:
                        n += 1
            else:
                self.lattice_id = 1
        self.Fill_ComboBox.addItems(["Select element", "None"])
        self.lineEdit_12.setText(str(self.surface_id))
        if self.comboBox_3.currentIndex() == 1:
            self.lineEdit_14.setText(str(self.cell_id))
        elif self.comboBox_3.currentIndex() == 2:
            self.lineEdit_15.setText(str(self.universe_id))
        self.lineEdit_18.setText(str(self.lattice_id))
        #self.lineEdit_17.setText(str(self.lattice_suffix))
        self.Fill_ComboBox.addItems(self.materials_name_list)
        self.Fill_ComboBox.addItems(self.universe_name_list)
        self.Fill_ComboBox.addItems(self.lattice_name_list)
        self.lineEdit_15.hide()
        self.XY_CB.hide()
        self.Orientation_CB.hide()
        self.comboBox_4.setCurrentIndex(0)

        if self.add_surf_id_CB.isChecked():
            self.lineEdit_11.setText(self.surface_suffix + str(self.lineEdit_12.text()))
        else:
            self.lineEdit_11.setText(self.surface_suffix)

        self.Univ_Lat_LE_Update()  

        for item in [self.Translation_CB, self.Rotation_CB, self.XX_LE, self.YY_LE, self.ZZ_LE, self.Theta_LE,
                     self.Phi_LE, self.Psi_LE]:
            item.setEnabled(False)
        for item in [self.lineEdit_19, self.lineEdit_24, self.spinBox_3, self.label_21, self.label_26]:
            item.setDisabled(True)

    def _initButtons(self):
        self.comboBox.currentIndexChanged.connect(self.Def_Surf)
        self.comboBox_3.currentIndexChanged.connect(self.Def_Cell_Univ)
        self.comboBox_3.currentIndexChanged.connect(self.activate_widgets)
        self.Fill_ComboBox.currentIndexChanged.connect(self.activate_widgets)
        self.comboBox_4.currentIndexChanged.connect(self.Def_Lattice)
        self.comboBox_5.currentIndexChanged.connect(self.Def_Region)
        self.pushButton_7.clicked.connect(self.Def_Matrix)
        self.comboBox_6.currentIndexChanged.connect(self.Pick_Universe)
        #self.comboBox_7.currentIndexChanged.connect(self.Pick_Universe)
        self.geomWidget.currentChanged.connect(self.Update_univ_CB_list)
        self.geomWidget.currentChanged.connect(self.Univ_Lat_LE_Update)
        self.Add_Surf_PB.clicked.connect(self.Add_Surface)
        self.Add_Cell_Univ_PB.clicked.connect(self.Add_Cell_Univ)
        self.Add_Lat_PB.clicked.connect(self.Add_Lattice)
        self.lineEdit_11.textChanged.connect(self.sync_surface_name1)
        self.lineEdit_12.textChanged.connect(self.sync_surface_id)
        self.add_surf_id_CB.stateChanged.connect(self.sync_surface_name)
        self.add_id_CB.stateChanged.connect(self.sync_name)
        self.add_id_lat_CB.stateChanged.connect(self.sync_name)        
        self.lineEdit_13.textChanged.connect(self.sync_name1)
        self.lineEdit_14.textChanged.connect(self.sync_id)
        self.lineEdit_15.textChanged.connect(self.sync_id)
        self.lineEdit_17.textChanged.connect(self.sync_name1)
        self.lineEdit_18.textChanged.connect(self.sync_id)
        self.Export_PB.clicked.connect(self.Export_to_Main_Window)
        self.Reset_Fields_PB.clicked.connect(self.Reset_Fields)
        self.pushButton_3.clicked.connect(self.Clear_Output)
        self.pushButton_4.clicked.connect(self.Exit)
        self.Reset_PB.clicked.connect(self.reset_text)
        self.RB_2D.toggled.connect(self.reset_widget)
        self.RB_3D.toggled.connect(lambda: self.spinBox_3.setValue(2))
        self.RB_2D.toggled.connect(lambda: self.spinBox_3.setValue(1))
        self.Modify_TextEdit_PB.clicked.connect(self.modify_textedit)
        self.XY_CB.currentIndexChanged.connect(self.Orientation_Lat)

    def Univ_Lat_LE_Update(self):
        if self.geomWidget.currentIndex() == 0:
            if self.comboBox_3.currentIndex() == 1:
                self.comboBox_5.addItems(sorted(self.regions))
                if self.add_id_CB.isChecked():
                    self.lineEdit_13.setText(self.cell_suffix + str(self.lineEdit_14.text()))
                else:
                    self.lineEdit_13.setText(self.cell_suffix)
            elif self.comboBox_3.currentIndex() == 2:
                if self.add_id_CB.isChecked():
                    self.lineEdit_13.setText(self.universe_suffix + str(self.lineEdit_15.text()))
                else:
                    self.lineEdit_13.setText(self.universe_suffix)
        elif self.geomWidget.currentIndex() == 1:
            if self.add_id_lat_CB.isChecked():
                self.lineEdit_17.setText(self.lattice_suffix + str(self.lineEdit_18.text()))
            else:
                self.lineEdit_17.setText(self.lattice_suffix)

    def RB_2D_Checked(self):
        if self.RB_2D.isChecked():
            nz = 1
        else:
            nz = self.spinBox_3.value()

    def modify_textedit(self):
        self.textEdit.setEnabled(True)
        self.modify_universes = True

    def reset_widget(self):
        for item in [self.lineEdit_19, self.lineEdit_24, self.spinBox_3, self.label_21, self.label_26]:
            if self.RB_2D.isChecked():
                item.setDisabled(True)
                self.RB_2D.toggled.connect(self.lineEdit_19.clear)
                self.RB_2D.toggled.connect(self.lineEdit_24.clear)
            else:
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
                #self.v_1.moveCursor(QTextCursor.End)
        self.Find_string(self.plainTextEdit, "geometry.xml")
        if self.Insert_Header:
            self.Find_string(self.v_1, "geometry.xml")
            if self.Insert_Header:
                self.v_1.insertPlainText('\n############################################################################### \n')
                self.v_1.insertPlainText('#                 Exporting to OpenMC geometry.xml file                        \n')
                self.v_1.insertPlainText('###############################################################################\n')
        self.Insert_Header = False

    def Export_to_Main_Window(self):
        cells = []
        string_to_find = "geometry.export_to_xml()"
        self.Find_string(self.v_1, string_to_find)
        cursor = self.v_1.textCursor()
        self.plainTextEdit.moveCursor(QTextCursor.End)
        cells = [item for item in self.cell_name_list if item not in self.cells_in_universes]
        if self.Insert_Header:
            print ('\ngeometry = openmc.Geometry(' + '[' + ', '.join(cells)+']' + ')')
            print (string_to_find, '\n')
            cursor.insertText(self.plainTextEdit.toPlainText())
        else:
            document = self.v_1.toPlainText()
            lines = document.split('\n')
            for line in lines:
                if ("openmc.Geometry" in line):
                    lines.remove(line)
                    document = self.v_1.toPlainText().replace(line,"")
            print ('\ngeometry = openmc.Geometry(' + '[' + ', '.join(cells)+']' + ')')
            print(string_to_find, '\n')
            document = document.replace(string_to_find,self.plainTextEdit.toPlainText())
            self.v_1.clear()
            #cursor = self.v_1.textCursor()
            cursor.insertText(document)
        self.text_inserted = True
        self.plainTextEdit.clear()

    def Find_string(self, text_window, string_to_find):
        self.current_line = ""
        self.line_number = 0
        self.Insert_Header = True
        document = text_window.toPlainText()
        for line in document.split('\n'):
            self.line_number += 1
            if string_to_find in line:
                self.current_line = line
                self.Insert_Header = False

    def sync_surface_name1(self):
        pos = self.lineEdit_11.cursorPosition()
        self.lineEdit_11.setCursorPosition(pos)
        self.surface_suffix = self.lineEdit_11.text().rstrip(string.digits)

    def sync_surface_name(self):
        self.surface_suffix = self.lineEdit_11.text().rstrip(string.digits)
        self.lineEdit_12.setText(str(self.surface_id))
        if self.add_surf_id_CB.isChecked():
            self.lineEdit_11.setText(self.surface_suffix + str(self.surface_id))
        else:
            self.surface_suffix = self.lineEdit_11.text().rstrip(string.digits)
            self.lineEdit_11.setText(self.surface_suffix)

    def sync_surface_id(self):
        if self.lineEdit_12.text():
            self.surface_id = int(self.lineEdit_12.text())
            if self.add_surf_id_CB.isChecked():
                self.lineEdit_11.setText(self.surface_suffix + str(self.surface_id))
            else:
                self.surface_suffix = self.lineEdit_11.text().rstrip(string.digits)
                self.lineEdit_11.setText(self.surface_suffix)

    def sync_name1(self):
        if self.geomWidget.currentIndex() == 0:
            if self.comboBox_3.currentIndex() == 1:
                pos = self.lineEdit_13.cursorPosition()
                self.lineEdit_13.setCursorPosition(pos)
                self.cell_suffix = self.lineEdit_13.text().rstrip(string.digits)  # 'Cell'
            if self.comboBox_3.currentIndex() == 2:
                pos = self.lineEdit_13.cursorPosition()
                self.lineEdit_13.setCursorPosition(pos)
                self.universe_suffix = self.lineEdit_13.text().rstrip(string.digits)
        elif self.geomWidget.currentIndex() == 1:
            pos = self.lineEdit_17.cursorPosition()
            self.lineEdit_17.setCursorPosition(pos)
            self.lattice_suffix = self.lineEdit_17.text().rstrip(string.digits)

    def sync_name(self):
        if self.geomWidget.currentIndex() == 0:
            if self.comboBox_3.currentIndex() == 1:
                self.lineEdit_14.setText(str(self.cell_id))
                if self.add_id_CB.isChecked():
                    self.lineEdit_13.setText(self.cell_suffix + str(self.cell_id))
                else:
                    if self.cell_suffix in self.lineEdit_13.text():
                        self.cell_suffix = self.lineEdit_13.text().rstrip(string.digits)  # 'Cell'
                    self.lineEdit_13.setText(self.cell_suffix)
            elif self.comboBox_3.currentIndex() == 2:
                self.lineEdit_14.setText(str(self.universe_id))
                if self.add_id_CB.isChecked():
                    self.lineEdit_13.setText(self.universe_suffix + str(self.universe_id))
                else:
                    if self.universe_suffix in self.lineEdit_13.text():
                        self.universe_suffix = self.lineEdit_13.text().rstrip(string.digits)
                    self.lineEdit_13.setText(self.universe_suffix)
        elif self.geomWidget.currentIndex() == 1:
            self.lineEdit_18.setText(str(self.lattice_id))
            if self.add_id_lat_CB.isChecked():
                self.lineEdit_17.setText(self.lattice_suffix + str(self.lattice_id))
            else:
                self.lattice_suffix = self.lineEdit_17.text().rstrip(string.digits)
                self.lineEdit_17.setText(self.lattice_suffix)

    def sync_id(self):
        if self.geomWidget.currentIndex() == 0:
            if self.comboBox_3.currentIndex() == 1:
                self.lineEdit_15.hide()
                self.lineEdit_14.show()
                if self.lineEdit_14.text():
                    self.cell_id = int(self.lineEdit_14.text())
                    if self.add_id_CB.isChecked():
                        self.lineEdit_13.setText(self.cell_suffix + str(self.cell_id))
                    else:
                        self.cell_suffix = self.lineEdit_13.text().rstrip(string.digits)  # 'Cell'
                        self.lineEdit_13.setText(self.cell_suffix)
            elif self.comboBox_3.currentIndex() == 2:
                self.lineEdit_14.hide()
                self.lineEdit_15.show()
                if self.lineEdit_15.text():
                    self.universe_id = int(self.lineEdit_15.text())
                    if self.add_id_CB.isChecked():
                        self.lineEdit_13.setText(self.universe_suffix + str(self.universe_id))
                    else:
                        self.universe_suffix = self.lineEdit_13.text().rstrip(string.digits)
                        self.lineEdit_13.setText(self.universe_suffix)

        elif self.geomWidget.currentIndex() == 1:
            if self.lineEdit_18.text():
                self.lattice_id = int(self.lineEdit_18.text())
                if self.add_id_lat_CB.isChecked():
                    self.lineEdit_17.setText(self.lattice_suffix + str(self.lattice_id))
                else:
                    self.lattice_suffix = self.lineEdit_17.text().rstrip(string.digits)
                    self.lineEdit_17.setText(self.lattice_suffix)

    def Reset_Fields(self):
        for item in [self.comboBox_3, self.Fill_ComboBox, self.comboBox_6, self.Operator_CB]:
            item.setCurrentIndex(0)
        self.plus_RB.setChecked(True)
        self.add_id_CB.setChecked(True)
        self.Translation_CB.setChecked(False)
        self.Rotation_CB.setChecked(False)
        self.Fill_ComboBox.setEnabled(True)
        for item in [self.lineEdit_14, self.lineEdit_15, self.lineEdit_13, self.lineEdit_14, self.lineEdit_15, self.Region_TextEdit]:
            item.clear()
        for item in[self.XX_LE, self.YY_LE, self.ZZ_LE, self.Theta_LE, self.Phi_LE, self.Psi_LE]:
            item.clear()
        for item in [self.Fill_ComboBox, self.label_15, self.label_27, self.Operator_CB, self.plus_RB, self.minus_RB]:
            item.show()

    def Def_Matrix(self):
        document = self.textEdit.toPlainText().split('\n')
        document = list(filter(str.strip, document))  # remove line if it contains only white spaces
        if document:
            qm = QMessageBox
            ret = qm.question(self, 'Warning', 'Text window is not empty. Do you want to clear data ?', qm.Yes | qm.No)
            if ret == qm.Yes:
                self.textEdit.clear()
            elif ret == qm.No:
                pass
        else:
            self.textEdit.clear()
        self.RB_2D_Checked()
        if self.comboBox_4.currentIndex() == 0:
            self.wind = LatticeRect(self.spinBox.value(), self.spinBox_2.value(), self.spinBox_3.value(),
                              self.universe_id_list, self.textEdit, self.lineEdit_17)
            self.wind.show()
            self.XY_CB.setEnabled(False)
        else:
            self.Orientation_Lat()
            #self.wind = LatticeHex(self.spinBox.value(), self.spinBox_3.value(), self.XY_CB.currentText(),
            self.wind = LatticeHex(self.spinBox.value(), self.spinBox_3.value(), self.orientation,
                              self.universe_id_list, self.universe_name_list, self.textEdit)
            self.wind.show()
            self.XY_CB.setEnabled(True)

    def Orientation_Lat(self):
        if self.XY_CB.currentText() == 'x':
            self.orientation = 'x'
        else:
            self.orientation = 'y'   

    def Def_Lattice(self):
        self.textEdit.clear()
        self.lineEdit_24.setEnabled(False)
        self.lineEdit_19.setEnabled(False)
        self.reset_widget()
        if self.comboBox_4.currentIndex() == 0:
            self.comboBox_6.show()
            self.Modify_TextEdit_PB.hide()
            self.lineEdit_20.setEnabled(True)
            self.lineEdit_20.clear()
            self.label_22.setText('Lower Left')
            self.label_23.setText('Dimensions')
            self.label_24.setText('nx')
            self.label_25.setText('ny')
            self.label_26.setText('nz')
            self.spinBox.setValue(1)
            self.spinBox_2.setValue(1)
            self.spinBox_3.setValue(1)
            self.XY_CB.hide()
            self.spinBox_2.show()
            self.Add_Lat_PB.setText("Add RectLattice >> ")
            self.textEdit.setEnabled(True)
        else:
            self.comboBox_6.hide()
            self.Modify_TextEdit_PB.show()
            self.lineEdit_20.setEnabled(False)
            self.label_22.setText('Center')
            self.label_24.setText('Rings')
            self.label_25.setText('Orientation')
            self.label_26.setText('Axial')
            self.spinBox.setValue(0)
            self.spinBox_3.setValue(1)
            self.XY_CB.show()
            self.spinBox_2.hide()
            self.Add_Lat_PB.setText("Add HexLattice >> ")

    def Pick_Universe(self):
        if self.comboBox_6.currentIndex() > 0:
            self.textEdit.insertPlainText(self.comboBox_6.currentText() + ' ')
        self.comboBox_6.setCurrentIndex(0)

    def Update_univ_CB_list(self):
        self.Region_TextEdit.clear()
        self.comboBox_6.clear()
        self.comboBox_6.addItem('Select Universes')
        self.comboBox_6.addItems(self.universe_name_list)
        self.comboBox_7.clear()
        self.comboBox_7.addItem('Select outer universe')
        self.comboBox_7.addItems(self.universe_name_list)

    def Def_Region(self):
        cursor = self.Region_TextEdit.textCursor()
        self.Region_TextEdit.ensureCursorVisible()
        text = self.Region_TextEdit.toPlainText()
        #text = ' '.join(text.split())
        if self.comboBox_3.currentIndex() == 0:
            self.label_14.setText('Id')
        elif self.comboBox_3.currentIndex() == 1:
            self.comboBox_5.setItemText(0, 'Select Region')

            if self.Operator_CB.currentIndex() == 0:
                if len(text) > 1:
                    op = ' & '
                else:
                    op = ''
            elif self.Operator_CB.currentIndex() == 1:
                if len(text) > 1:
                    op = ' | '
                else:
                    op = ''
            elif self.Operator_CB.currentIndex() == 2:
                if len(text) > 1:
                    op = ' & ~ '
                else:
                    op = ' ~ '
            elif self.Operator_CB.currentIndex() == 3:
                if len(text) > 1:
                    op = ' | ~ '
                else:
                    op = ' ~ '
            if self.comboBox_5.currentIndex() != 0:
                if self.minus_RB.isChecked():
                    sign = '-'
                elif self.plus_RB.isChecked():
                    sign = '+'
                if self.comboBox_5.currentText() in self.cell_name_list or 'openmc.model' in self.comboBox_5.currentText():
                    sign = ''
                if self.comboBox_5.currentText() in self.cell_name_list:
                    region = self.comboBox_5.currentText() + '.region'
                else:
                    region = self.comboBox_5.currentText()
                text = self.Region_TextEdit.toPlainText()
                if text and text != '(':
                    sign = op + sign
                if self.comboBox_5.currentText() in self.cell_name_list:
                    #if len(text) > 1:
                    sign = op

                text = self.Region_TextEdit.toPlainText()
                text = ' '.join(text.split())
                text_length = len(text)
                if self.comboBox_5.currentIndex() != 0:
                    current_pos = cursor.position()
                else:
                    current_pos = text_length
                #text = text + sign + region

                if current_pos < text_length:
                    cursor.setPosition(current_pos, QtGui.QTextCursor.KeepAnchor)
                    splitted_line = list(text)
                    if splitted_line[current_pos] in ['+', '-', '('] or splitted_line[current_pos + 1] in ['+', '-', '(']:
                        splitted_line.insert(current_pos, ' ' + sign + region + ' & ' )

                    elif splitted_line[current_pos] in ['&', ')', '|', '~'] or splitted_line[current_pos + 1] in ['&', ')', '|', '~']:
                        splitted_line.insert(current_pos, ' & ' + sign + region + ' ')
                    text = ''.join(splitted_line).replace('&  &', '&').replace('|  &', '|').replace('&  |', '|')
                else:
                    text = text + sign + region

            self.Region_TextEdit.clear()
            cursor.insertText(text.replace('( &', '(').replace('  ', ' '))
            self.plus_RB.setChecked(True)
            self.Operator_CB.setCurrentIndex(0)
            self.comboBox_5.setCurrentIndex(0)
        elif self.comboBox_3.currentIndex() == 2:
            self.label_14.setText('Univ Id')
            self.comboBox_5.setItemText(0, 'Select Cells')
            if self.comboBox_5.currentIndex() == 0:
                pass
            else:
                if self.Region_TextEdit.toPlainText():
                    text = self.Region_TextEdit.toPlainText()
                    self.Region_TextEdit.clear()
                    cursor.insertText(text + ', ' + self.comboBox_5.currentText())
                else:
                    '''text = self.Region_TextEdit.toPlainText()
                    self.Region_TextEdit.clear()'''
                    cursor.insertText(text + self.comboBox_5.currentText())
            self.comboBox_5.setCurrentIndex(0)

    def Add_Lattice(self):
        nx = self.spinBox.value()
        ny = self.spinBox_2.value()
        nz = self.spinBox_3.value()
        self.Insert_Header_Text()
        if not self.textEdit.toPlainText():
            self.showDialog('Warning', 'Lattice is empty !')
            return
        else:
            if self.lineEdit_17.text() == '':
                self.showDialog('Warning', 'Cannot create lattice, select name first.')
                return
            elif self.lineEdit_18.text() == '':
                self.showDialog('Warning', 'Cannot create lattice, select lattice id first.')
                return
            else:
                if self.lineEdit_17.text() in self.lattice_name_list:
                    self.showDialog('Warning', 'Lattice name already used, select new name !')
                    return
                elif int(self.lineEdit_18.text()) in self.lattice_id_list or int(self.lineEdit_18.text()) in self.universe_id_list:
                    self.showDialog('Warning', 'Lattice id already used, select new id !')
                    return
                else:
                    if self.lineEdit_21.text() == '' or self.lineEdit_22.text() == '' or self.lineEdit_23.text() == '':
                        self.showDialog('Warning', 'Required fields must be filled !')
                        return
                    if self.RB_2D.isChecked():
                        if self.comboBox_4.currentIndex() == 0:
                            if self.lineEdit_20.text() == '':
                                self.showDialog('Warning', 'Required fields must be filled !')
                                return
                    elif self.RB_3D.isChecked():
                        if self.lineEdit_19.text() == '' or self.lineEdit_24.text() == '':
                            self.showDialog('Warning', 'Required fields must be filled !')
                            return
                    ########################### RectLattice #######################
                    if self.comboBox_4.currentIndex() == 0:
                        document = self.textEdit.toPlainText()
                        document = document.split('\n')
                        #document = " ".join(str(document).split())
                        #document = document.split(',')
                        document = list(filter(str.strip, document))  # remove line if it contains only white spaces
                        document = list(filter(None, document))     # remove empty lines
                        if nz == 1:
                            if ny == 1:
                                document1 = ''
                            else:
                                document1 = ' ['
                        elif nz != 1:
                            document1 = '[['

                        j = 0
                        element_number = 0
                        lattice_size = nx * ny * nz
                        padding = ' ' * (len(self.lineEdit_17.text()) + 15)
                        pad = ' ' * (len(self.lineEdit_17.text()) + 14) + '['
                        for line in document:
                            liste = line.split()
                            liste = list(filter(lambda ele: ele != "['", liste))
                            liste = list(filter(lambda ele: "']" not in ele, liste))
                            liste = list(filter(lambda ele: ele != "'", liste))
                            liste = [int(str(ele).replace("'", "")) for ele in liste]
                            for i in liste:
                                if i not in self.universe_id_list:
                                    self.showDialog('Warning', "At least one universe id doesn't mutch available universe names !")
                                    return
                            #liste = [self.universe_name_list[int(i)-1] for i in liste]
                            liste = [self.universe_name_list[self.universe_id_list.index(int(id))] for id in liste]
                            j += 1
                            element_number += len(liste)
                            if j != 1:
                                if element_number == lattice_size:
                                    if ny == 1:
                                        document1 += pad + str(liste).replace("'", "") + ']]\n'
                                    else:
                                        if nz != 1:
                                            document1 += padding + str(liste).replace("'", "") + ']]'
                                        else:
                                            document1 += padding + str(liste).replace("'", "") + ']'    # $$$$$$$$$$$$$$
                                else:
                                    if (j - 1) % ny == 0 and nz != 1 and ny != 1:
                                        document1 += pad + str(liste).replace("'", "") + ',\n'
                                    elif j % ny == 0 and ny != 1:
                                        document1 += padding + str(liste).replace("'", "") + '],\n'
                                    elif ny == 1:
                                        document1 += pad + str(liste).replace("'", "") + '],\n'
                                    else:
                                        document1 += padding + str(liste).replace("'", "") + ',\n'
                            else:
                                if ny == 1:
                                    if nz != 1:
                                        document1 += str(liste).replace("'", "") + '],\n'
                                    else:
                                        document1 += str(liste).replace("'", "") + '\n'
                                else:
                                    document1 += str(liste).replace("'", "") + ',\n'
                        if element_number != lattice_size and self.textEdit.toPlainText() != '':
                            self.showDialog('Warning', 'Lattice elements number not equal to specified number !')
                            return
                        else:
                            print(self.lineEdit_17.text() + " = openmc.RectLattice(" + "lattice_id=" + self.lineEdit_18.text() + ")")
                            if self.RB_2D.isChecked():
                                print(self.lineEdit_17.text() + ".lower_left = [" + self.lineEdit_22.text() + ',' + self.lineEdit_23.text() + "]")
                                print(self.lineEdit_17.text() + ".pitch = [" + self.lineEdit_21.text() + ',' + self.lineEdit_20.text() + "]")
                            else:
                                print(self.lineEdit_17.text() + ".lower_left = [" + self.lineEdit_22.text() + ',' + self.lineEdit_23.text() + ',' + self.lineEdit_24.text() + "]")
                                print(self.lineEdit_17.text() + ".pitch = [" + self.lineEdit_21.text() + ',' + self.lineEdit_20.text() + ',' + self.lineEdit_19.text() + "]")
                            print(self.lineEdit_17.text() + ".universes = " + document1)
                            if self.comboBox_7.currentIndex() != 0:
                                print(self.lineEdit_17.text() + ".outer = " + self.comboBox_7.currentText())
                            self.lattice_name_list.append(self.lineEdit_17.text())
                            self.lattice_id_list.append(self.lineEdit_18.text())
                            if len(self.lattice_id_list) > 0:
                                idx = int(self.lattice_id_list[-1]) + 1
                                while True:
                                    if idx not in self.universe_id_list and idx not in self.universe_id_list:
                                        self.lattice_id = idx
                                        break
                                    else:
                                        idx += 1
                            else:
                                idx = int(self.lineEdit_18.text()) + 1
                                while True:
                                    if idx not in self.universe_id_list and idx not in self.lattice_id_list:
                                        self.lattice_id = idx
                                        break
                                    else:
                                        idx += 1

                            self.lineEdit_18.setText(str(self.lattice_id))
                            if self.add_id_CB.isChecked():
                                self.lineEdit_17.setText(self.lattice_suffix + str(self.lattice_id))
                            else:
                                self.lineEdit_17.setText(self.lattice_suffix)
                            self.lineEdit_15.setText(str(idx))
                            if self.add_id_CB.isChecked():
                                self.lineEdit_13.setText(self.universe_suffix + str(idx))
                            else:
                                self.lineEdit_17.setText(self.lattice_suffix)

                    ########################### HexLattice #######################
                    elif self.comboBox_4.currentIndex() == 1:
                        Axials = {}
                        Axials_rows = {}
                        self.Ring = {}
                        self.lattice = {}
                        self.altitude = []
                        self.elem_per_rings = []
                        self.values_to_remove = []
                        self.tot_element = 1
                        self.rings = self.spinBox.value()
                        self.axial = self.spinBox_3.value()
                        for k in range(self.axial + 1):   # last item not used
                            self.altitude.append("Axial%s" % (k + 1))
                        for name in self.altitude[:-1]:
                            self.lattice[name] = {}
                        if self.orientation == 'x':
                            rows = 2 * self.rings - 1
                            y = [j for j in range(-self.rings + 1, self.rings)]
                        elif self.orientation == 'y':
                            rows = 4 * self.rings - 3
                            y = [j for j in range(-self.rings * 2 + 2 , self.rings * 2 - 1)]
                        LatticeHex.xy_coordinates(self)
                        LatticeHex.ring_coordinates(self)
                        elements_per_tab = len(self.xx)
                        document = self.textEdit.toPlainText()
                        document = document.split('\n')
                        document = list(filter(None, document))     # remove empty lines
                        document = list(filter(str.strip, document))  # remove line if it contains only white spaces
                        tot_rows = len(document)
                        # sorting and ziping xy and indices from self.Ring
                        xy_coordinates = self.Ring['xy_coordinates']
                        indices = self.Ring['indices']
                        xy_ind = sorted(list(zip(xy_coordinates, indices)), key=lambda x: (x[0][1], x[0][0]))
                        # ///////////////////////////////// insert text /////////////////////////////////////////
                        #self.Find_string(self.plainTextEdit, "openmc.HexLattice")
                        #if self.Insert_Header:
                        print(self.lineEdit_17.text() + "= openmc.HexLattice(" + "lattice_id=" + self.lineEdit_18.text() + ")")
                        if self.RB_2D.isChecked():
                            print(self.lineEdit_17.text() + ".center = [" + self.lineEdit_22.text() + ',' + self.lineEdit_23.text() + "]")
                            print(self.lineEdit_17.text() + ".pitch = [" + self.lineEdit_21.text() + "]")
                        else:
                            print(
                                self.lineEdit_17.text() + ".center = [" + self.lineEdit_22.text() + ',' + self.lineEdit_23.text() + ',' + self.lineEdit_24.text() + "]")
                            print(
                                self.lineEdit_17.text() + ".pitch = [" + self.lineEdit_21.text() + ',' + self.lineEdit_19.text() + "]")
                        if self.comboBox_7.currentIndex() != 0:
                            print(self.lineEdit_17.text() + ".outer = " + self.comboBox_7.currentText())
                        # ///////////////////////////////////////////////////////////////////////////////////////
                        self.axials_lat_univ = []
                        if tot_rows == rows * self.axial:
                            for name in self.altitude[:-1]:
                                lattice_universes = []
                                Axials_rows[name] = []
                                Axials[name] = {}
                                Axials[name]['univ'] = []
                                tot_elements = 0
                                x = -self.rings + 1
                                for j in range(rows):
                                    index = j + rows * self.altitude.index(name)
                                    Axials[name]['univ'] += document[index].split()
                                    row_size = len(document[index].split())
                                    tot_elements += row_size
                                    if self.orientation == 'x':
                                        xy = [(x, y[j],)]
                                    else:
                                        xy = [(y[j], -x, )]
                                    xx = x
                                    for i in range(1, row_size):
                                        xx += 2
                                        if self.orientation == 'x':
                                            xy.append((xx, y[j],))
                                        else:
                                            xy = [(y[j], -xx,)]
                                    if j < int(rows * 0.5):
                                        x -= 1
                                    else:
                                        x += 1
                                    if 'xy' in Axials[name]:
                                        if not isinstance(Axials[name]['xy'], list):
                                            Axials[name]['xy'] = [Axials[name]['xy']]
                                        Axials[name]['xy'] += (xy)
                                    else:
                                        Axials[name]['xy'] = xy
                                if tot_elements == elements_per_tab:
                                    univ = Axials[name]['univ']
                                    xy_ind_univ = list(zip(xy_ind, univ))
                                    ind_univ_sorted_by_ring = sorted(zip([ x[1] for x in xy_ind], univ), key = lambda x: (x[0][0], x[0][1]))
                                    xy_ind_univ_sorted_by_ring = sorted(zip([ x[0] for x in xy_ind], [ x[1] for x in xy_ind], univ), key = lambda x: (x[1][0], x[1][1]))
                                    indices = 0
                                    start = 0
                                    for ir in range(self.rings):
                                        ring_universes = []
                                        if len(self.altitude) > 2:
                                            ring_name = name + 'ring' + str(ir)
                                        else:
                                            ring_name = 'ring' + str(ir)
                                        if ir == self.rings - 1:
                                            indices += 1
                                        else:
                                            indices += (self.rings - ir - 1) * 6
                                        stop = indices
                                        self.lattice[name][ir]['sorted_univ_id'] = [ u[2] for u in xy_ind_univ_sorted_by_ring[start:stop]]
                                        list1 = self.universe_name_list
                                        list2 = [ int(item) for item in self.lattice[name][ir]['sorted_univ_id']]
                                        list3 = self.universe_id_list
                                        start = stop
                                        if set(list2).issubset(list3):
                                            self.lattice[name][ir]['sorted_univ_name'] = [list1[list3.index(id)] for id in list2]
                                            ring_universes = self.lattice[name][ir]['sorted_univ_name']
                                        else:
                                            self.showDialog('Warning', "At least one universe id doesn't mutch available universe names !")
                                            return
                                        self.lattice[ring_name] = ring_universes
                                        lattice_universes.append(ring_name)
                                    self.axials_lat_univ.append(lattice_universes)
                                else:
                                    self.showDialog('Warning', "Total number of universes dosen't mutch the entered parameters !")
                                    return
                            for elem in self.axials_lat_univ:
                                for key in elem:
                                    univ = self.count_dups(self.lattice[key])[0]
                                    freq = self.count_dups(self.lattice[key])[1]
                                    liste = [(str([univ[i]]) + '*' + str(freq[i])) if freq[i] != 1 else str([univ[i]]) for i in range(len(univ)) ]
                                    liste = " + ".join(liste)
                                    print(key + ' = ' + str(liste).replace("'","").replace('"', ''))
                            liste = [str(item).replace("'", "") for item in self.axials_lat_univ]
                            padding = ',\n' + ' ' * (len(self.lineEdit_17.text()) + 14)
                            if len(liste) != 1:
                                print(self.lineEdit_17.text() + ".universes = [" + padding.join(liste) + ']')
                            else:
                                print(self.lineEdit_17.text() + ".universes = " + padding.join(liste))

                            print(self.lineEdit_17.text() + ".orientation = " + "'" + self.orientation + "'")
                            self.lattice_name_list.append(self.lineEdit_17.text())
                            self.lattice_id_list.append(self.lineEdit_18.text())
                            if len(self.lattice_id_list) > 0:
                                idx = int(self.lattice_id_list[-1]) + 1
                                while True:
                                    if idx not in self.universe_id_list:
                                        self.lattice_id = idx
                                        break
                                    else:
                                        idx += 1
                            else:
                                idx = int(self.lineEdit_18.text()) + 1
                                while True:
                                    if idx not in self.universe_id_list:
                                        self.lattice_id = idx
                                        break
                                    else:
                                        idx += 1
                            self.lineEdit_18.setText(str(self.lattice_id))
                            if self.add_id_CB.isChecked():
                                self.lineEdit_17.setText(self.lattice_suffix + str(self.lattice_id))
                            else:
                                self.lineEdit_17.setText(self.lattice_suffix)
                            self.lineEdit_15.setText(str(idx))
                            if self.add_id_CB.isChecked():
                                self.lineEdit_13.setText(self.universe_suffix + str(idx))
                            else:
                                self.lineEdit_13.setText(self.universe_suffix)
                        else:
                            self.showDialog('Warning', "Lattice size dosen't mutch the entered parameters !")
                            return
                self.comboBox_7.setCurrentIndex(0)

    def count_dups(self, nums):
        element = []
        freque = []
        if not nums:
            return element
        running_count = 1
        for i in range(len(nums) - 1):
            if nums[i] == nums[i + 1]:
                running_count += 1
            else:
                freque.append(running_count)
                element.append(nums[i])
                running_count = 1
        element.append(nums[len(nums) - 1])
        freque.append(running_count)
        return element, freque

    def Add_Cell_Univ(self):
        self.Insert_Header_Text()
        if self.comboBox_3.currentIndex() == 1:
            self.Translation_CB.setEnabled(True)
            self.Rotation_CB.setEnabled(True)
            self.cells.append(self.lineEdit_13.text())
            item = 'cell'
            if self.lineEdit_13.text() == '':
                self.showDialog('Warning', 'Cannot create ' + item + ', select name first!')
                return
            elif self.lineEdit_14.text() == '':
                self.showDialog('Warning', 'Cannot create  ' + item + ', select cell id first!')
                return
            else:
                if self.lineEdit_13.text() in self.cell_name_list:
                    self.showDialog('Warning', 'Cell name already used, select new name !')
                    return
                elif int(self.lineEdit_14.text()) in self.cell_id_list:
                    self.showDialog('Warning', 'Cell id already used, select new id !')
                    return
                else:
                    if self.lineEdit_13.text() not in self.regions:
                        self.regions.append(self.lineEdit_13.text())
                    print(self.lineEdit_13.text() + "= openmc.Cell(" + "cell_id=" + self.lineEdit_14.text() + ",", "name='" + self.lineEdit_13.text() + "')")
                    if self.Region_TextEdit.toPlainText():
                        if '|' in self.Region_TextEdit.toPlainText() or '~' in self.Region_TextEdit.toPlainText():
                            print(self.lineEdit_13.text() + ".region = " + self.Region_TextEdit.toPlainText())
                        else:
                            print(self.lineEdit_13.text() + ".region = " + self.Region_TextEdit.toPlainText().replace('(', '').replace(')', ''))
                    if self.Fill_ComboBox.currentIndex() != 0:
                        print(self.lineEdit_13.text() + ".fill = " + self.Fill_ComboBox.currentText())
                        self.Fill_ComboBox.setCurrentIndex(0)
                    if self.Translation_CB.isChecked():
                        if self.XX_LE.text() == '' or self.YY_LE.text() == '' or self.ZZ_LE.text() == '':
                            self.showDialog('Warning', 'The three coordinates must be given !')
                            return
                        else:
                            print(self.lineEdit_13.text() + ".translation = (" + self.XX_LE.text() + ', ' + self.YY_LE.text() + ', ' + self.ZZ_LE.text() +')')
                    if self.Rotation_CB.isChecked():
                        if self.Theta_LE.text() == '' or self.Phi_LE.text() == '' or self.Psi_LE.text() == '':
                            self.showDialog('Warning', 'The three coordinates must be given !')
                            return
                        else:
                            print(self.lineEdit_13.text() + ".rotation = (" + self.Theta_LE.text() + ', ' + self.Phi_LE.text() + ', ' + self.Psi_LE.text() +')')

                    self.cell = self.lineEdit_13.text()
                    self.cell_name_list.append(self.lineEdit_13.text())
                    self.cell_name_sub_list.append(self.lineEdit_13.text())
                    self.cell_id_list.append(self.lineEdit_14.text())
                    self.cell_id_sub_list.append(self.lineEdit_14.text())
                    self.comboBox_5.addItem(self.lineEdit_13.text())   # *******
                    self.cell_id = int(self.lineEdit_14.text()) + 1
                    self.lineEdit_14.setText(str(self.cell_id))
                    if self.add_id_CB.isChecked():
                        self.lineEdit_13.setText(self.cell_suffix + str(self.cell_id))
                    else:
                        self.lineEdit_13.setText(self.cell_suffix)
                        self.Region_TextEdit.clear()
                self.Translation_CB.setChecked(False)
                self.Rotation_CB.setChecked(False)
                self.XX_LE.setText('')
                self.YY_LE.setText('')
                self.ZZ_LE.setText('')
                self.Theta_LE.setText('')
                self.Phi_LE.setText('')
                self.Psi_LE.setText('')
        elif self.comboBox_3.currentIndex() == 2:
            '''self.Translation_CB.setEnabled(False)
            self.Rotation_CB.setEnabled(False)'''
            item = 'universe'
            if self.lineEdit_13.text() == '':
                self.showDialog('Warning', 'Cannot create ' + item + ', select name first!')
                return
            elif self.lineEdit_15.text() == '':
                self.showDialog('Warning', 'Cannot create  ' + item + ', select cell id first!')
                return
            else:
                if self.lineEdit_13.text() in self.universe_name_list or self.lineEdit_13.text() in self.lattice_name_list:
                    self.showDialog('Warning', 'Universe name already used, select new name !')
                    return
                elif int(self.lineEdit_15.text()) in self.universe_id_list or int(self.lineEdit_15.text()) in self.lattice_id_list:
                    self.showDialog('Warning', 'Universe id already used, select new id !')
                    return
                else:
                    print(self.lineEdit_13.text() + " = openmc.Universe(universe_id=" + self.lineEdit_15.text() + "," + " name='" + self.lineEdit_13.text() + "')")
                    if self.Region_TextEdit:
                        textList = self.Region_TextEdit.toPlainText().replace(' ','').split(",")
                        self.cells_in_universes += textList
                        print(self.lineEdit_13.text() + ".add_cells(" + str(textList).replace("'","") +")")
                    self.universe_name_list.append(self.lineEdit_13.text())
                    self.universe_id_list.append(self.lineEdit_15.text())
                    self.Fill_ComboBox.addItem(self.lineEdit_13.text())
                    self.universe_name_sub_list.append(self.lineEdit_13.text())
                    self.universe_id_sub_list.append(self.lineEdit_15.text())

                    if len(self.universe_id_list) > 0:
                        idx = int(self.universe_id_list[-1]) + 1
                        while True:
                            if idx not in self.universe_id_list and idx not in self.lattice_id_list:
                                self.universe_id = idx
                                break
                            else:
                                idx += 1
                    else:
                        idx = 1
                        while True:
                            if idx not in self.lattice_id_list:
                                self.universe_id = idx
                                break
                            else:
                                idx += 1
                    self.lineEdit_15.setText(str(self.universe_id))

                    if self.add_id_CB.isChecked():
                        self.lineEdit_13.setText(self.universe_suffix + str(self.universe_id))
                    else:
                        self.lineEdit_13.setText(self.universe_suffix)
                    
                    self.lineEdit_18.setText(str(idx + 1))
                    if self.add_id_lat_CB.isChecked():
                        self.lineEdit_17.setText(self.lattice_suffix + str(idx + 1))
                    else:
                        self.lineEdit_17.setText(self.lattice_suffix)

                self.Region_TextEdit.clear()
                self.comboBox_6.clear()
                self.comboBox_6.addItem('Select Universes')
                self.comboBox_6.addItems(self.universe_name_list)
                self.comboBox_7.clear()
                self.comboBox_7.addItem('Select outer universe')
                self.comboBox_7.addItems(self.universe_name_list)
                self.comboBox_5.setCurrentIndex(0)
        self.Reset_Fields()

    def activate_widgets(self):
        if self.comboBox_3.currentIndex() == 1:
            if self.Fill_ComboBox.currentText() in self.universe_name_list:
                for item in [self.Translation_CB, self.Rotation_CB, self.XX_LE, self.YY_LE, self.ZZ_LE, self.Theta_LE,
                         self.Phi_LE, self.Psi_LE]:
                    item.setEnabled(True)
            else:
                for item in [self.Translation_CB, self.Rotation_CB, self.XX_LE, self.YY_LE, self.ZZ_LE, self.Theta_LE,
                         self.Phi_LE, self.Psi_LE]:
                    item.setEnabled(False)
        if self.comboBox_3.currentIndex() == 2:
            for item in [self.Translation_CB, self.Rotation_CB, self.XX_LE, self.YY_LE, self.ZZ_LE, self.Theta_LE,
                     self.Phi_LE, self.Psi_LE]:
                item.setEnabled(False)

    def Def_Cell_Univ(self):
        self.comboBox_5.clear()
        for item in [self.Translation_CB, self.Rotation_CB, self.XX_LE, self.YY_LE, self.ZZ_LE, self.Theta_LE,
                     self.Phi_LE, self.Psi_LE]:
            item.setEnabled(False)

        if self.comboBox_3.currentIndex() == 1:
            self.plus_RB.show()
            self.minus_RB.show()
            self.label_15.show()
            self.label_27.show()
            self.Operator_CB.show()
            self.Fill_ComboBox.show()
            self.label_14.setText('Cell Id')
            self.comboBox_5.addItem('Select Region')
            self.comboBox_5.addItems(self.surface_name_list)
            self.comboBox_5.addItems(self.cell_name_list)
            self.sync_name()
            self.sync_id()
            if self.add_id_CB.isChecked():
                self.lineEdit_13.setText(self.cell_suffix + str(self.lineEdit_14.text()))
            else:
                self.lineEdit_13.setText(self.cell_suffix)
            self.lineEdit_14.clear()
            self.Region_TextEdit.clear()
            self.label_15.setText('Fill')
            self.Fill_ComboBox.setEnabled(True)
            self.Add_Cell_Univ_PB.setText("Add Cell >>")
            self.add_id_CB.setText('add id to cell name')
            self.lineEdit_14.setText(str(self.cell_id))
        elif self.comboBox_3.currentIndex() == 2:
            self.plus_RB.hide()
            self.minus_RB.hide()
            self.Operator_CB.hide()
            self.label_15.hide()
            self.label_27.hide()
            self.Fill_ComboBox.hide()
            self.comboBox_5.addItem('Select Cells')
            self.comboBox_5.addItems(self.cell_name_list)
            self.sync_name()
            self.sync_id()
            if self.add_id_CB.isChecked():
                self.lineEdit_13.setText(self.universe_suffix + str(self.lineEdit_15.text()))
            else:
                self.lineEdit_13.setText(self.universe_suffix)
            self.lineEdit_15.clear()
            self.Region_TextEdit.clear()
            self.label_14.setText('Universe id')
            self.add_id_CB.setText('add id to universe name')
            self.Fill_ComboBox.setEnabled(False)
            self.Add_Cell_Univ_PB.setText("Add Univ >>")
            self.lineEdit_15.setText(str(self.universe_id))
        else:
            self.lineEdit_13.clear()
            self.lineEdit_14.clear()
            self.lineEdit_15.clear()

    def Add_Surface(self):
        self.Insert_Header_Text()
        if self.lineEdit_11.text() == '':
            self.showDialog('Warning', 'Cannot create surface, select name first !')
            return
        elif self.lineEdit_12.text() == '':
            self.showDialog('Warning', 'Cannot create surface, select surface id first !')
            return
        else:
            if self.comboBox_2.currentIndex() in [0, 1]:
                Boundary_Def = ''
            else:
                Boundary_Def = ", boundary_type='" + self.comboBox_2.currentText() + "'"

            if self.lineEdit_11.text() in self.surface_name_list:
                self.showDialog('Warning', 'Surface name already used, select new name !')
                return
            elif int(self.lineEdit_12.text()) in self.surface_id_list:
                self.showDialog('Warning', 'Surface id already used, select new id !')
                return
            else:
                if self.lineEdit_11.text() not in self.regions:
                    self.regions.append(self.lineEdit_11.text())
                if self.comboBox.currentIndex() == 0:
                    return
                if self.comboBox.currentIndex() == 1:  # Plane
                    print(self.lineEdit_11.text() + "= openmc.Plane(" + "surface_id=" + self.lineEdit_12.text() + ",",
                                "a=" + self.lineEdit.text() + ",", "b=" + self.lineEdit_2.text() + ",",
                                "c=" + self.lineEdit_3.text() + ",",
                                "d=" + self.lineEdit_4.text() + ",", "name='" + self.lineEdit_11.text() +
                                "'" + Boundary_Def + ')')
                elif self.comboBox.currentIndex() in [2, 3, 4]:  # XPlane, YPlane, ZPlane
                    if self.comboBox.currentIndex() == 2:
                        d = 'x0='
                    if self.comboBox.currentIndex() == 3:
                        d = 'y0='
                    if self.comboBox.currentIndex() == 4:
                        d = 'z0='
                    list1 = ['= openmc.XPlane(', '= openmc.YPlane(', '= openmc.ZPlane(']
                    print(self.lineEdit_11.text() + list1[self.comboBox.currentIndex() - 2] +
                                "surface_id=" + self.lineEdit_12.text() + ",",
                                d + self.lineEdit.text() + ",", "name='" + self.lineEdit_11.text() +
                                "'" + Boundary_Def + ')')

                elif self.comboBox.currentIndex() == 5:    # Sphere
                    print(self.lineEdit_11.text() + "= openmc.Sphere(" + "surface_id=" + self.lineEdit_12.text() + ",",
                                "x0=" + self.lineEdit.text() + ",", "y0=" + self.lineEdit_2.text() + ",",
                                "z0=" + self.lineEdit_3.text() + ",",
                                "r=" + self.lineEdit_4.text() + ",", "name='" + self.lineEdit_11.text() +
                                "'" + Boundary_Def + ')')
                elif self.comboBox.currentIndex() == 6:   # XCylinder
                    print(self.lineEdit_11.text() + '= openmc.XCylinder(' +
                                "surface_id=" + self.lineEdit_12.text() + ",",
                                "y0=" + self.lineEdit_2.text() + ",", "z0=" + self.lineEdit_3.text() + ",",
                                "r=" + self.lineEdit_4.text() + ",", "name='" + self.lineEdit_11.text() +
                                "'" + Boundary_Def + ')')
                elif self.comboBox.currentIndex() == 7:  # YCylinder
                    print(self.lineEdit_11.text() + '= openmc.YCylinder(' +
                                "surface_id=" + self.lineEdit_12.text() + ",",
                                "x0=" + self.lineEdit.text() + ",", "z0=" + self.lineEdit_3.text() + ",",
                                "r=" + self.lineEdit_4.text() + ",", "name='" + self.lineEdit_11.text() +
                                "'" + Boundary_Def + ')')
                elif self.comboBox.currentIndex() == 8:   # ZCylinder
                    print(self.lineEdit_11.text() + '= openmc.ZCylinder(' +
                                "surface_id=" + self.lineEdit_12.text() + ",",
                                "x0=" + self.lineEdit.text() + ",", "y0=" + self.lineEdit_2.text() + ",",
                                "r=" + self.lineEdit_4.text() + ",", "name='" + self.lineEdit_11.text() +
                                "'" + Boundary_Def + ')')
                elif self.comboBox.currentIndex() == 9:    # Cone
                    print(self.lineEdit_11.text() + '= openmc.Cone(' + "surface_id=" + self.lineEdit_12.text() + ",",
                                "x0=" + self.lineEdit.text() + ",", "y0=" + self.lineEdit_2.text() + ",",
                                "z0=" + self.lineEdit_3.text() + ",", "r2=" + self.lineEdit_4.text() + ",",
                                "dx=" + self.lineEdit_5.text() + ",", "dy=" + self.lineEdit_6.text() + ",",
                                "dz=" + self.lineEdit_7.text() + ",", "name='" + self.lineEdit_11.text() +
                                "'" + Boundary_Def + ')')
                elif self.comboBox.currentIndex() in [10, 11, 12]:  # XCone, YCone, ZCone
                    print(self.lineEdit_11.text() + '= ' + self.comboBox.currentText() + '(' +
                                "surface_id=" + self.lineEdit_12.text() + ",",
                                "x0=" + self.lineEdit.text() + ",", "y0=" + self.lineEdit_2.text() + ",",
                                "z0=" + self.lineEdit_3.text() + ",",
                                "r2=" + self.lineEdit_4.text() + ",", "name='" + self.lineEdit_11.text() +
                                "'" + Boundary_Def + ')')
                elif self.comboBox.currentIndex() == 13:  # Quadratic
                    print(self.lineEdit_11.text() + '= openmc.Quadric(' + "surface_id=" + self.lineEdit_12.text() + ",",
                                "a=" + self.lineEdit.text() + ",", "b=" + self.lineEdit_2.text() + ",",
                                "c=" + self.lineEdit_3.text() + ",", "d=" + self.lineEdit_4.text() + ",",
                                "e=" + self.lineEdit_5.text() + ",", "f=" + self.lineEdit_6.text() + ",",
                                "g=" + self.lineEdit_7.text() + ",", "h=" + self.lineEdit_8.text() + ",",
                                "j=" + self.lineEdit_9.text() + ",", "k=" + self.lineEdit_10.text() + ",",
                                "name='" + self.lineEdit_11.text() +
                                "'" + Boundary_Def + ')')
                elif self.comboBox.currentIndex() in [14, 15, 16]:  # XTorus, YTorus, ZTorus
                    print(self.lineEdit_11.text() + '= ' + self.comboBox.currentText() + '(' + "surface_id=" + self.lineEdit_12.text() + ",",
                                "x0=" + self.lineEdit.text() + ",", "y0=" + self.lineEdit_2.text() + ",",
                                "z0=" + self.lineEdit_3.text() + ",", "a=" + self.lineEdit_7.text() + ",",
                                "b=" + self.lineEdit_8.text() + ",", "c=" + self.lineEdit_9.text() + ",",
                                "name='" + self.lineEdit_11.text() +
                                "'" + Boundary_Def + ')')
                elif self.comboBox.currentIndex() == 17:  # Rectangular prism
                    origin = (float(self.lineEdit.text()), float(self.lineEdit_2.text()),)
                    print(self.lineEdit_11.text() + '= openmc.model.' + self.comboBox.currentText() + '(',
                              self.lineEdit_7.text() + ",", self.lineEdit_8.text() + ",", "axis='" + self.Orientation_CB.currentText() + "',",
                              "origin=" + str(origin) + ",",
                              "corner_radius=" + self.lineEdit_4.text(), Boundary_Def + ')')
                elif self.comboBox.currentIndex() == 18:  # Hexagonal prism
                    origin = (float(self.lineEdit.text()), float(self.lineEdit_2.text()),)
                    print(self.lineEdit_11.text() + '= openmc.model.' + self.comboBox.currentText() + '(',
                              "edge_length=" + self.lineEdit_7.text() + ",", "orientation='" + self.Orientation_CB.currentText() + "',",
                              "origin=" + str(origin) + ",",
                              "corner_radius=" + self.lineEdit_4.text(), Boundary_Def + ')')

                self.surface_name_list.append(self.lineEdit_11.text())
                self.surface_name_sub_list.append(self.lineEdit_11.text())
                self.surface_id_list.append(self.lineEdit_12.text())
                self.surface_id_sub_list.append(self.lineEdit_12.text())
                self.comboBox_5.addItem(self.lineEdit_11.text())
                self.surface_id = int(self.lineEdit_12.text()) + 1
                self.lineEdit_12.setText(str(self.surface_id))
                if self.add_surf_id_CB.isChecked():
                    self.lineEdit_11.setText(self.surface_suffix + str(self.surface_id))
                else:
                    self.lineEdit_11.setText(self.surface_suffix)
        self.comboBox_2.setCurrentIndex(0)

    def Def_Surf(self):
        self.Orientation_CB.hide()
        self.lineEdit_3.show()
        self.label_2.show()
        for LE in self.Liste:
            LE.clear()
            LE.setEnabled(True)
        if self.comboBox.currentIndex() == 0:
            for LE in self.Liste:
                LE.clear()
                LE.setEnabled(True)
            for lbl in self.Liste1:
                lbl.setEnabled(True)
            for i in range(len(self.Liste1)):
                self.Liste1[i].setText(self.Liste1_LB[i])
        # Plane, XPlan, YPlane, ZPlane
        elif self.comboBox.currentIndex() in range(1, 5):
            self.label.setText('A');
            self.label_2.setText('B');
            self.label_3.setText('C');
            self.label_4.setText('D')
            for i in range(4, 10):
                self.Liste1[i].setEnabled(False)
                self.Liste[i].setEnabled(False)
            if self.comboBox.currentIndex() == 1:   # Plane
                for i in range(4):
                    self.Liste[i].setEnabled(True)
                    self.Liste1[i].setEnabled(True)
                for i in range(4):
                    self.Liste[i].setText('0.0')
            if self.comboBox.currentIndex() in [2, 3, 4]:  # XPlane, YPlane, ZPlane
                self.Liste[0].setText('0.0')
                self.Liste1[0].setEnabled(True)
                for i in [1, 2, 3]:
                    self.Liste[i].setEnabled(False)
                    self.Liste[i].clear()
                    self.Liste1[i].setEnabled(False)
                if self.comboBox.currentIndex() == 2:    # XPlane
                    self.Liste1[0].setText('x0')
                elif self.comboBox.currentIndex() == 3:  # YPlane
                    self.Liste1[0].setText('y0')
                elif self.comboBox.currentIndex() == 4:  # ZPlane
                    self.Liste1[0].setText('z0')
        # Sphere
        elif self.comboBox.currentIndex() == 5:
            self.label.setText('x0');
            self.label_2.setText('y0');
            self.label_3.setText('z0');
            self.label_4.setText('r')
            for i in range(4):
                self.Liste[i].setEnabled(True)
                self.Liste[i].setText('0.0')
                self.Liste1[i].setEnabled(True)
            for i in range(4, 10):
                self.Liste[i].setEnabled(False)
                self.Liste1[i].setEnabled(False)
            self.Liste[3].setText('1.0')
        # XCylinder, YCylinder, ZCylinder
        elif self.comboBox.currentIndex() in [6, 7, 8]:
            self.label.setText('x0');
            self.label_2.setText('y0');
            self.label_3.setText('z0');
            self.label_4.setText('r')
            for i in range(4):
                self.Liste[i].setEnabled(True)
                self.Liste1[i].setEnabled(True)
            for i in range(4, 10):
                self.Liste[i].setEnabled(False)
                self.Liste1[i].setEnabled(False)
            for i in range(3):
                self.Liste[i].setText('0.0')
            self.Liste[3].setText('1.0')
            if self.comboBox.currentIndex() == 6:     # XCylinder
                self.Liste[0].setEnabled(False)
                self.Liste1[0].setEnabled(False)
            elif self.comboBox.currentIndex() == 7:   # YCylinder
                self.Liste[1].setEnabled(False)
                self.Liste1[1].setEnabled(False)
            elif self.comboBox.currentIndex() == 8:
                self.Liste[2].setEnabled(False)
                self.Liste1[2].setEnabled(False)
        # Cone XCone , YCone and ZCone
        elif self.comboBox.currentIndex() in [9, 10, 11, 12]:
            for i in range(4):
                self.Liste[i].setEnabled(True)
                self.Liste1[i].setEnabled(True)
            for i in range(7, 10):
                self.Liste[i].setEnabled(False)
                self.Liste1[i].setEnabled(False)
                self.Liste[i].clear()
            self.Liste1[0].setText('x0')
            self.Liste1[1].setText('y0')
            self.Liste1[2].setText('z0')
            self.Liste1[3].setText('r2')
            self.Liste[3].setText('1.0')
            for i in range(3):
                self.Liste[i].setText('0.0')
            if self.comboBox.currentIndex() == 9:   # Cone
                for i in range(4, 7):
                    self.Liste[i].setEnabled(True)
                    self.Liste1[i].setEnabled(True)
                    self.Liste[i].setText('0.0')
                self.Liste[6].setText('1.0')
                self.Liste1[4].setText('dx')
                self.Liste1[5].setText('dy')
                self.Liste1[6].setText('dz')
            else:                                   # XCone , YCone and ZCone
                for i in range(4, 10):
                    self.Liste[i].setEnabled(False)
                    self.Liste[i].clear()
                    self.Liste1[i].setEnabled(False)
                for i in range(4, 8):
                    self.Liste1[i].setText(self.Liste1_LB[i])
        # Quadric
        elif self.comboBox.currentIndex() == 13:
            for i in range(10):
                self.Liste[i].setEnabled(True)
                self.Liste1[i].setEnabled(True)
                self.Liste1[i].setText(self.Liste1_LB[i])
                self.Liste[i].setText('0.0')
        # XTorus, YTorus, ZTorus
        elif self.comboBox.currentIndex() in [14, 15, 16]:
            for clr in self.Liste:
                clr.clear()
                clr.setEnabled(True)
            self.label_7.setEnabled(True)
            self.label_9.setEnabled(True)
            self.label.setText('x0');
            self.label_2.setText('y0');
            self.label_3.setText('z0');
            self.label_7.setText('A');
            self.label_8.setText('B');
            self.label_9.setText('C')
            self.label_4.setEnabled(False)
            self.label_8.setEnabled(True)
            for i in [0, 1, 2, 6, 7, 8]:
                self.Liste[i].setText('0.0')
            for i in [3, 4, 5, 9]:
                self.Liste[i].setEnabled(False)
            for i in [4, 5, 9]:
                self.Liste1[i].setEnabled(False)
            for i in [7, 8]:
                self.Liste[i].setEnabled(True)
        # Hexagonal and Rectangular prisms
        elif self.comboBox.currentIndex() in [17, 18]:
            self.lineEdit_3.hide()
            self.Orientation_CB.show()
            self.Orientation_CB.clear()
            self.label_9.setEnabled(False)
            self.lineEdit_9.setEnabled(False)
            self.label_4.setEnabled(True)
            self.label_7.setEnabled(True)
            for clr in self.Liste:
                clr.clear()
                clr.setEnabled(True)
            self.label.setAlignment(QtCore.Qt.AlignCenter)
            self.label.setText('Origin in the plane');
            self.label_2.hide()
            self.label_4.setText('Corner_radius')
            if self.comboBox.currentIndex() == 17:      # Hexagonal prism
                self.label_3.setText('Orientation')
                self.Orientation_CB.addItems(['x', 'y'])
                self.Orientation_CB.setCurrentIndex(0)
                self.label_7.setText('Edge_length')
                self.label_8.setEnabled(False)
                self.lineEdit_8.setEnabled(False)
            else:                                       # Rectangular prism
                self.label_3.setText('Axis')
                self.Orientation_CB.addItems(['x', 'y', 'z'])
                self.Orientation_CB.setCurrentIndex(2)
                self.label_7.setText('Width')
                self.label_8.setText('Height')
                self.label_8.setEnabled(True)
                self.lineEdit_8.setEnabled(True)
            self.Orientation_CB.show()
            self.lineEdit_3.hide()
            for i in range(4):
                self.Liste[i].setText('0.0')
            self.Liste[6].setText('1.0');
            self.Liste[7].setText('1.0');
            for i in [4, 5, 9]:
                self.Liste[i].setEnabled(False)
            self.label_5.setEnabled(False)
            self.label_6.setEnabled(False)
            self.label_10.setEnabled(False)

        elif self.comboBox.currentIndex() == 15:
            pass

    def Clear_Output(self):
        if self.text_inserted:
            self.plainTextEdit.clear()
        else:
            document = self.plainTextEdit.toPlainText().split('\n')
            document = list(filter(str.strip, document))  # remove line if it contains only white spaces
            if document:
                qm = QMessageBox
                ret = qm.question(self, 'Warning', 'Text window is not empty. Do you want to clear data ?',
                                  qm.Yes | qm.No)
                if ret == qm.Yes:
                    self.plainTextEdit.clear()
                elif ret == qm.No:
                    pass
            else:
                self.plainTextEdit.clear()

    def reset_text(self):
        qm = QMessageBox
        ret = qm.question(self, 'Warning', 'Do you really want to reset data ?', qm.Yes | qm.No)
        if ret == qm.Yes:
            self.textEdit.clear()
        elif ret == qm.No:
            pass
        self.textEdit.setEnabled(True)
        
    def Clear_Lists(self):
        if self.surface_name_sub_list:
            self.Remove_Selected(self.surface_name_sub_list, self.surface_name_list)
            self.Remove_Selected(self.surface_id_sub_list, self.surface_id_list)
            self.Remove_Selected(self.surface_name_sub_list, self.regions)
            if self.surface_id_list:
                self.lineEdit_12.setText(str(int(self.surface_id_list[-1]) + 1))
        if self.cell_name_sub_list:
            self.Remove_Selected(self.cell_name_sub_list, self.cell_name_list)
            self.Remove_Selected(self.cell_id_sub_list, self.cell_id_list)
            self.Remove_Selected(self.cell_name_sub_list, self.regions)
            if self.cell_id_list:
                self.lineEdit_14.setText(str(int(self.cell_id_list[-1]) + 1))
        if self.universe_name_sub_list:
            self.Remove_Selected(self.universe_name_sub_list, self.universe_name_list)
            self.Remove_Selected(self.universe_id_sub_list, self.universe_id_list)
            if self.universe_id_list:
                idx = int(self.universe_id_list[-1]) + 1
                while True:
                    if idx not in self.lattice_id_list:
                        self.lineEdit_15.setText(str(idx))
                        break
                    else:
                        idx += 1
            else:
                self.lineEdit_15.setText('1')
        self.comboBox_5.clear()
        self.comboBox_5.addItem('Select region')
        self.comboBox_5.addItems(self.regions)
        self.Region_TextEdit.clear()

    def Remove_Selected(self, Sub_List, List):
        List[:] = [item for item in List if item not in Sub_List]

    def normalOutputWritten(self, text):
        self.highlighter = Highlighter(self.plainTextEdit.document())
        cursor = self.plainTextEdit.textCursor()
        cursor.insertText(text)


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class LatticeRect(QWidget):
    from .func import resize_ui, showDialog, Exit
    def __init__(self, nx, ny, nz, univ_id, TexEdit, lineEdit_17, parent=None):
        super(LatticeRect, self).__init__(parent)
        self.setWindowTitle("Fill Lattice Input Parameters")
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint)
        self.universe_id_list = univ_id
        self.textEdit = TexEdit
        self.lineEdit_17 = lineEdit_17
        self.nx = nx
        self.ny = ny
        self.nz = nz
        self.lab6 = [0]*nx*ny*nz
        self.combobox = [0]*nx*ny*nz
        self.Matrix = [0]*nx*ny*nz
        self.layout = QVBoxLayout(self)
        self.typetab = QTabWidget(self)
        self.typetab.setFont(QtGui.QFont("Sanserif", 10))
        self.types = []
        self.tab1 = QWidget()
        typetablayout1 = QGridLayout(self.tab1)
        self.lab6[0] = QLabel("<font color=blue > Instantiate a Lattice </font>")
        typetablayout1.addWidget(self.lab6[0], 0, 0)
        self.lab7 = QLabel("<font color=blue > To fill the whole lattice </font>")
        typetablayout1.addWidget(self.lab7, 1, 0)
        self.universes_combobox = QComboBox()
        typetablayout1.addWidget(self.universes_combobox, 1, 1)
        self.universes_combobox.addItem('Select universe ID')
        self.universes_combobox.addItems([str(item) for item in self.universe_id_list])
        self.layout.addWidget(self.tab1)
        self._initButtons()
        for i in range(nz):
            self.types.append("Z %s" %(i+1))
        num = 0
        for name in self.types:
            self.tab = QWidget()
            self.typetab.addTab(self.tab, name[0:10])
            typetablayout = QGridLayout(self.tab)
            m = 0
            for j in range(ny):
                self.lab6[j] = QLabel("Y %s" %(j+1))
                self.lab6[j].setAlignment(Qt.AlignCenter)
                typetablayout.addWidget(self.lab6[j], j+7, 0)
                for i in range(nx):
                    self.lab6[i] = QLabel("X %s" %(i+1))
                    self.lab6[i].setAlignment(Qt.AlignCenter)
                    typetablayout.addWidget(self.lab6[i], 6, i+1)
                    self.combobox[nx*ny*num+m] = QComboBox()
                    typetablayout.addWidget(self.combobox[nx*ny*num+m], j+7, i+1)
                    self.combobox[nx * ny * num + m].addItem('0')
                    self.combobox[nx * ny * num + m].addItems([str(item) for item in self.universe_id_list])
                    m+=1

            self.layout.addWidget(self.typetab)
            self.setLayout(self.layout)
            if num == (len(self.types)-1):
                self.Save_Button = QPushButton(u"Save and Close")
                self.Save_Button.clicked.connect(partial(self.save, num))
                self.layout.addWidget(self.Save_Button)
            num += 1
        self.resize_ui()

    def _initButtons(self):
        self.universes_combobox.currentIndexChanged.connect(self.Fill_Matrix)

    def Fill_Matrix(self):
        k = self.typetab.currentIndex()
        if self.universes_combobox.currentIndex() != 0:
            m = 0
            for j in range(self.ny):
                for i in range(self.nx):
                    self.combobox[self.nx*self.ny*k+m].setCurrentIndex(self.universes_combobox.currentIndex())
                    m+=1
            self.universes_combobox.setCurrentIndex(0)

    def save(self, num):
        nx = self.nx
        ny = self.ny
        nz = self.nz
        del self.Matrix[:]
        for k in range(len(self.types)):
            m = 0
            self.Matrix.append([])
            for j in range(self.ny):
                self.Matrix[k].append([])

                for i in range(self.nx):
                    self.Matrix[k][j].append(eval(self.combobox[self.nx*self.ny*k+m].currentText()))
                    m += 1

        blanks = ' ' * (len(self.lineEdit_17.text()) + 15)
        Index = 0
        lattice = ''
        field_size = 5
        List = str(self.Matrix).replace(' ', '').split(']],')
        for Item in List:
            Index += 1
            if ']],' not in List:
                if Index < len(List) and self.nz > 1:
                    Item = Item + ']],'
            if self.nz == 1:
                Item = Item.replace('[[[', '[[').replace(']]]', ']]')

            index = 0
            list = Item.split('],')
            for item in list:
                if index == 0 and Index == 1:
                    space = ''
                else:
                    space = blanks
                index += 1
                if index < self.ny:
                    item = item + '],'
                if Index < self.nz and index == self.ny:
                    item = item + '],'
                text = item.replace('[', '').replace('],', '').replace(']', '').replace(' ', '')
                list_univ = text.split(',')
                matrix_row = ''
                for univ in list_univ:
                    univ = ' ' * (field_size - len(univ)) + univ + ' ' * (field_size - len(univ))
                    matrix_row += univ

                self.textEdit.insertPlainText(matrix_row + '\n')
                lattice += (space + item.replace(',', ', ') + '\n')

        if num == (len(self.types)-1):
            self.close()

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class LatticeHex(QWidget):
    from .func import resize_ui, showDialog
    def __init__(self, rings, axial, orientation, univ_id, univ, TexEdit, parent=None):
        super(QWidget, self).__init__(parent)
        self.setWindowTitle("Fill HexLattice Input Parameters")
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.universe_id_list = univ_id
        self.universe_name_list = univ
        self.textEdit = TexEdit
        self.rings = rings
        self.axial = axial
        self.orientation = orientation
        self.Ring = {}
        self.lattice = {}
        self.elem_per_rings = []
        self.values_to_remove = []
        self.tot_element = 1
        for n_rings in range(self.rings):
            self.tot_element += n_rings * 6

        self.cbstyle = [0] * 100
        self.lab = [0] * self.tot_element
        self.combobox = [0] * self.tot_element * (self.axial + 1)
        self.colors = ['darkred', 'red', 'darksalmon', 'orange', 'yellow', 'greenyellow', 'lightgreen', 'green',
                       'turquoise', 'lightblue', 'aquamarine', 'blue', 'cadetblue', 'lightsteelblue', 'midnightblue',
                       'blueviolet', 'mediumvioletred', 'violet', 'burlywood', 'silver', 'lightgray', 'lightslategray',
                       'mediumpurple', 'moccasin', 'papayawhip', 'rosybrown', 'saddlebrown', 'seashell', 'sienna', 'thistle']
        i = 0
        while i < self.rings:
            if i < len(self.colors):
                self.cbstyle[i] = "QComboBox { background: " + self.colors[i] + ";}"
            else:
                if abs(self.rings - i) < len(self.colors):
                    self.cbstyle[i] = "QComboBox { background: " + self.colors[abs(self.rings - i)] + ";}"
                elif abs(self.rings - 2 * i) < len(self.colors):
                    self.cbstyle[i] = "QComboBox { background: " + self.colors[abs(self.rings - 2 * i)] + ";}"
                else:
                    self.cbstyle[i] = ''
            i += 1
        groupBox1 = QGroupBox("Fill ring by ring")
        groupBox1.setStyleSheet('QGroupBox:title {color: blue;}')
        groupBox2 = QGroupBox("Show")
        groupBox2.setStyleSheet('QGroupBox:title {color: blue;}')
        typetablayout1 = QGridLayout(groupBox1)
        typetablayout3 = QGridLayout(groupBox2)
        self.RB1 = QRadioButton("(ring, index)")
        self.RB2 = QRadioButton("(x, y) index")

        typetablayout3.addWidget(self.RB1, 0, 0)
        typetablayout3.addItem(QSpacerItem(50, 10, QSizePolicy.Fixed), 0, 1)
        typetablayout3.addWidget(self.RB2, 0, 2)
        typetablayout3.addItem(QSpacerItem(150, 10, QSizePolicy.Expanding), 0, 3)
        self.RB1.setEnabled(False)
        self.RB2.setEnabled(False)
        self.RB1.setChecked(True)
        self.universes_combobox = [0] * self.rings
        for index in range(self.rings):
            self.universes_combobox[index] = QComboBox()
            typetablayout1.addWidget(self.universes_combobox[index], 0, index + 1)
            self.universes_combobox[index].addItem('Ring %s' % (index))
            self.universes_combobox[index].setStyleSheet(self.cbstyle[self.rings - index - 1])
            self.universes_combobox[index].addItems([str(item) for item in self.universe_id_list])
        scroll = QScrollArea()
        scroll.setWidget(groupBox1)
        scroll.setFixedHeight(80)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        self.layout.addWidget(scroll)
        self.layout.addWidget(groupBox2)

        self.altitude = []
        element_id = []
        for k in range(axial):
            self.altitude.append("Axial%s" % (k + 1))
        self.altitude.append("Indices")
        self.tabs = QTabWidget(self)
        for name in self.altitude[:-1]:
            #if name != self.altitude[-1]:
            self.lattice[name] = {}
        self.xy_coordinates()    # generates (x,y) coordinates: returns self.Ring[ir]['xy_indices'], self.xx, self.yy
        self.ring_coordinates()  # generates (ring, i) coordinates: returns self.Ring[n_rings]['ring_indices'], self.rings_index, self.rings_yy
        k_axial = 0
        elements_per_tab = len(self.xx)

        for name in self.altitude:
            row_col_list = []
            self.tab = QScrollArea()
            self.tabs.addTab(self.tab, name)
            self.content_widget2 = QWidget()
            self.tab.setWidget(self.content_widget2)
            typetablayout = QGridLayout(self.content_widget2)
            self.tab.setWidgetResizable(True)
            m = 0
            if self.orientation == 'x':
                if self.xx:
                    shift = abs(min(self.xx))
            elif self.orientation == 'y':
                if self.yy:
                    shift = abs(min(self.yy))
            while m <= len(self.xx) - 1:
                id = m + elements_per_tab * self.altitude.index(name)   # * k_axial
                element_id.append(id)
                self.combobox[id] = QComboBox()
                self.combobox[id].setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents) #setMinimumWidth(75)
                index = len(self.rings_index) - 1 - m
                iring = self.rings_index[index]
                self.combobox[id].setStyleSheet(self.cbstyle[self.rings - iring - 1])
                if id == 0:
                    row = shift
                    col = shift
                else:
                    row = self.yy[m] + shift
                    col = self.xx[m] + shift
                typetablayout.addWidget(self.combobox[id], row, col)
                row_col_list.append((col, row,))
                self.combobox[id].clear()
                if name != self.altitude[-1]:
                    self.combobox[id].addItem('Select')
                    self.combobox[id].addItems([str(item) for item in self.universe_id_list])
                else:
                    self.combobox[id].setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)  # setMinimumWidth(75)
                    self.combobox[id].addItem(str((iring, self.rings_yy[index],)))
                m += 1
            self.Ring['row_col'] = row_col_list
            self.Ring['elm_id'] = element_id

            k_axial += 1
        self.tabs.setCurrentIndex(0)
        self.tabs.currentChanged.connect(self.reset_index)
        for index in range(self.rings):
            self.universes_combobox[index].currentIndexChanged.connect(partial(self.AutoFillCombo, index, self.combobox, self.universes_combobox))
            self.universes_combobox[index].setCurrentIndex(0)
        self.layout.addWidget(self.tabs)
        self.butts = QWidget()
        buttslayout = QGridLayout(self.butts)
        self.Save_Button1 = QPushButton(u"Insert HexLattice")
        self.Save_Button1.clicked.connect(self.save)
        buttslayout.addWidget(self.Save_Button1, 0, 0)
        self.Exit_Button2 = QPushButton(u"Exit")
        self.Exit_Button2.clicked.connect(self.exit)
        buttslayout.addWidget(self.Exit_Button2, 0, 1)
        self.layout.addWidget(self.butts)

        self.resize_ui()

    def show_indices(self, combobox, xx, yy, rings_index, rings_yy):
        self.tabs.setCurrentIndex(self.axial)
        start = len(xx) * (self.axial)
        stop = len(xx) * (self.axial + 1)
        for m in range(start, stop):
            index = stop - 1 - m
            if self.RB1.isChecked():
                #self.spinBox_3.setValue(1)
                combobox[m].clear()
                combobox[m].addItem(str((rings_index[index], rings_yy[index],)))
            elif self.RB2.isChecked():
                #self.spinBox_3.setValue(2)
                combobox[m].clear()
                combobox[m].addItem(str((xx[m - start], yy[m - start],)))

    def xy_coordinates(self):
        # calculates (x, y) tuple of each element in the hexagonal lattice
        self.yy = []
        self.xx = []
        xy_list = []
        id = 0
        for n_rings in range(self.rings):
            ir = self.rings - n_rings - 1
            xy = []
            element_id = []
            self.elem_per_row = []
            x_matrix = []
            self.Ring[ir] = {}
            if n_rings == 0:
                row = [0]
                self.row_num = 1
                max_elem_per_row = 1
                self.elem_per_rings += [1]
            elif n_rings > 0:
                self.elem_per_rings += [n_rings * 6]  # 1  6  12  18 24 30 36   :  1  (i - 1)*6
                if self.orientation == 'x':
                    row = [i for i in range(-n_rings, n_rings + 1)]  # rows
                    max_elem_per_row = 2 * n_rings + 1
                elif self.orientation == 'y':
                    row = [i for i in range(-n_rings * 2, n_rings * 2 + 1)]
                    self.row_num = 4 * n_rings + 1

            for yy in row:
                if n_rings == 0:
                    self.elem_per_row += [1]
                else:
                    if self.orientation == 'x':
                        if yy <= 0:
                            self.elem_per_row += [max_elem_per_row + yy]
                        else:
                            self.elem_per_row += [max_elem_per_row - yy]
                    elif self.orientation == 'y':
                        if yy <= row[0] * 0.5:
                            self.elem_per_row += [n_rings * 2 + yy + 1]
                        elif yy > row[0] * 0.5 and yy < row[-1] * 0.5:
                            if (n_rings + abs(yy)) % 2 == 0:
                                self.elem_per_row += [n_rings + 1]
                            else:
                                self.elem_per_row += [n_rings]
                        elif yy >= row[-1] * 0.5:
                            self.elem_per_row += [n_rings * 2 - yy + 1]
            for i in range(len(row)):
                if self.elem_per_row[i] == 1:
                    x_matrix += [[0]]
                else:
                    start = -self.elem_per_row[i] + 1
                    stop = self.elem_per_row[i] + 1
                    x_matrix += [[j for j in range(start, stop, 2)]]
            for i in range(len(row)):
                for j in range(self.elem_per_row[i]):
                    xy_idx = (x_matrix[i][j], row[i],)
                    '''if self.orientation == 'y':
                        xy_idx = (x_matrix[i][j], row[i],)
                    elif self.orientation == 'x':
                        xy_idx = (x_matrix[i][j],row[i], )'''
                    if xy_idx not in self.values_to_remove:
                        id += 1
                        element_id.append(id)
                        xy.append(xy_idx)
                        self.xx.append(xy_idx[0])
                        self.yy.append(xy_idx[1])

            self.Ring[ir]['xy_indices'] = xy
            self.Ring[ir]['elem_per_row'] = self.elem_per_row
            xy_list += xy
            self.Ring['xy_coordinates'] = xy_list
            self.values_to_remove += xy
            self.Ring[ir]['element_id'] = element_id
            for name in self.altitude[:-1]:
                self.lattice[name][ir] = {}
                self.lattice[name][ir]['element_id'] = [id + self.tot_element * self.altitude.index(name) for id in element_id]

    def ring_coordinates(self):
        # calculates (ring, i) tuple of element in the hexagonal lattice
        self.rings_index = []
        self.rings_yy = []
        self.Ring['indices'] = []
        for iring in range(self.rings):
            ring_idx = []
            ir = self.rings - iring - 1
            if ir == 0:
                ring_idx.append((iring, 0,))
            else:
                if self.orientation == 'x':
                    for i in range(ir + 1):
                        idx = int(4 * ir + i)
                        ring_idx.append((iring, idx,))

                    left_idx = int(ring_idx[0][1] - 1)
                    right_idx = int(ring_idx[0][1] + ir + 1)
                    while len(ring_idx) <= self.elem_per_rings[ir] - 1:
                        if left_idx > self.elem_per_rings[ir] * 0.5 - ir:
                            if right_idx >= self.elem_per_rings[ir]:
                                right_idx = 0
                            ring_idx.append((iring, left_idx,))
                            ring_idx.append((iring, right_idx,))
                            left_idx -= 1
                            right_idx += 1
                        else:
                            for i in range(ir + 1):
                                idx = int(2 * ir - i)
                                ring_idx.append((iring, idx,))
                elif self.orientation == 'y':
                    i = 1
                    ring_idx.append((iring, 0,))
                    while len(ring_idx) <= self.elem_per_rings[ir] - 2:
                        left_idx = self.elem_per_rings[ir] - i
                        right_idx = self.elem_per_rings[ir] - left_idx
                        ring_idx.append((iring, left_idx,))
                        ring_idx.append((iring, right_idx,))
                        i += 1
                    ring_idx.append((iring, int(self.elem_per_rings[ir] * 0.5),))
            for ii in range(len(ring_idx)):
                jj = len(ring_idx) - ii - 1
                self.rings_index.append(ring_idx[jj][0])
                self.rings_yy.append(ring_idx[jj][1])
            self.Ring[iring]['ring_indices'] = ring_idx
        for ir in range(self.rings):
            self.Ring['indices'] += self.Ring[self.rings - ir - 1]['ring_indices']

    def AutoFillCombo(self, index, combobox, universes_combobox):
        uc_index = universes_combobox[index].currentIndex()
        tab_index = self.tabs.currentIndex()
        start = 1 + tab_index * self.tot_element
        stop = self.tot_element + tab_index * self.tot_element + 1
        if tab_index < self.axial and uc_index != 0:
            for id in range(start, stop):
                if (id - tab_index * self.tot_element) in self.Ring[index]['element_id']:
                    combobox[id - 1].setCurrentIndex(uc_index)

    def reset_index(self):
        for index in range(self.rings):
            self.universes_combobox[index].setCurrentIndex(0)
        if self.tabs.currentIndex() == self.axial:
            for index in range(self.rings):
                self.universes_combobox[index].setEnabled(False)
            self.RB1.setEnabled(True)
            self.RB2.setEnabled(True)
        else:
            for index in range(self.rings):
                self.universes_combobox[index].setEnabled(True)
            self.RB1.setEnabled(False)
            self.RB2.setEnabled(False)
        self.RB1.toggled.connect(partial(self.show_indices, self.combobox, self.xx, self.yy, self.rings_index, self.rings_yy))

    def exit(self):
        self.close()

    def save(self):
        self.axials_lat_univ = []
        field_size = 5
        if self.orientation == 'x':
            row_num = 2 * self.rings - 1
        elif self.orientation == 'y':
            row_num = 4 * self.rings - 3
        for name in self.altitude[:-1]:
            self.tabs.setCurrentIndex(self.altitude.index(name))
            lattice_universes = []
            universes = []
            #del self.Matrix[:]
            start = len(self.xx) * (self.tabs.currentIndex())
            stop = len(self.xx) * (self.tabs.currentIndex() + 1)
            for m in range(start, stop):
                index = stop - 1 - m
                iring = self.rings_index[index]
                universes.append(self.combobox[m].currentText())
                if m + 1 in self.lattice[name][iring]['element_id']:
                    u = self.combobox[m].currentText()
                if 'univ' in self.lattice[name][iring]:
                    if not isinstance(self.lattice[name][iring]['univ'], list):
                        self.lattice[name][iring]['univ'] = [self.lattice[name][iring]['univ']]
                    self.lattice[name][iring]['univ'].append(u)
                else:
                    self.lattice[name][iring]['univ'] = [u]
                for u in self.lattice[name][iring]['univ']:
                    if self.is_integer(u):   #   error
                        pass
                    else:
                        self.showDialog('Warnin', 'Universe id is not an integer !')
                        return
            self.Ring['universes'] = universes
            Ring_row_by_row = {}
            universes = {}
            m = start
            for x, y in self.Ring['xy_coordinates']:
                if y in Ring_row_by_row:
                    Ring_row_by_row[y].append((x, y))
                    universes[y].append(self.combobox[m].currentText())
                else:
                    Ring_row_by_row[y] = [(x, y)]
                    universes[y] = [self.combobox[m].currentText()]
                m += 1
            Ring_row_by_row = dict(sorted(Ring_row_by_row.items())) # sorted by key = row index
            universes = dict(sorted(universes.items()))  # sorted by key = row index
            self.textEdit.setFontPointSize(int(11))
            self.textEdit.setAlignment(Qt.AlignCenter)
            for y in Ring_row_by_row.keys():
                list1 = Ring_row_by_row[y]
                list2 = universes[y]
                lis1, lis2 = zip(*sorted(zip(list1, list2), key=lambda t: (t[0], t[1])))
                row = ''
                for univ in lis2:
                    univ = univ.replace("'", '')
                    univ = ' ' * (field_size - len(univ)) + univ + ' ' * (field_size - len(univ))
                    row += univ
                self.textEdit.insertPlainText("\n" + row + "\n")

        self.textEdit.setEnabled(False)

    def is_integer(self, n):
        try:
            float(n)
        except ValueError:
            return False
        else:
            return float(n).is_integer()


class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))
        pass

    def flush(self):
        pass