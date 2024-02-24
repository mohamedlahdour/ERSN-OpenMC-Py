#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5 import QtCore, QtGui, QtWidgets
from src.syntax_py import Highlighter
from src.PyEdit import TextEdit, NumberBar  

class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)
 
    def write(self,text):
        self.textWritten.emit(str(text))
        pass

    def flush(self):
        pass 

class ExportSettings(QWidget):
    from .func import resize_ui, showDialog, Def_Source_ToolTips, Exit

    def __init__(self, v_1, Directory, Surf_list, Surf_Id_list, Cells_list, Mat_list, Vol_Calcs_list, Source_list, Source_Id, Strength_list, parent=None):
        super(ExportSettings, self).__init__(parent)
        #sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        #sys.stderr = EmittingStream(textWritten=self.normalOutputWritten)
        uic.loadUi("src/ui/ExportSettings.ui", self)
        self.v_1 = v_1
        self.text_inserted = False
        self._initButtons()
        self.Insert_Header = True
        self.Imported_X_Y_List = False
        self.directory = Directory
        self.surface_name_list = Surf_list
        self.surface_id_list = Surf_Id_list
        self.Source_Surfaces_CB.addItems(self.surface_name_list)
        self.cell_name_list = Cells_list
        self.materials_name_list = Mat_list
        self.vol_calcs = Vol_Calcs_list
        self.list_of_cells = []
        self.list_of_surfaces = []
        self.list_of_surfaces_ids = []
        self.list_of_materials = self.materials_name_list
        self.Source_name_list = Source_list
        self.Source_id_list = Source_Id
        self.Source_strength_list = Strength_list
        self.vol_calcs = []
        self.Strength_LE.setText('1.')
        self.src_filename = ''
        self.Entropy_LE_List = [self.X_dim, self.Y_dim, self.Z_dim, 
                                self.X_LL_Entropy, self.Y_LL_Entropy, self.Z_LL_Entropy,
                                self.X_UR_Entropy, self.Y_UR_Entropy, self.Z_UR_Entropy]
        # validators
        Dblevalidator = QDoubleValidator(self)
        dim_validator = QRegExpValidator(QRegExp(r'[0-9 ,;:]+'))
        int_validator = QRegExpValidator(QRegExp(r'[0-9]+'))

        for item in [self.LineEdit_1, self.LineEdit_2, self.LineEdit_5, self.Particles_Number]:
            item.setValidator(int_validator)
        for item in [self.Photon_Cut, self.Strength_LE, self.X_LL, self.Y_LL, self.Z_LL, self.X_UR, self.Y_UR, self.Z_UR,
                     self.Energy_LE, self.Proba_LE, self.Mu_Min_LE, self.Phi_Min_LE, self.Mu_Max_LE, self.Phi_Max_LE]:
            item.setValidator(Dblevalidator)
        for item in self.Entropy_LE_List[3:9]:
            item.setValidator(Dblevalidator)
        for item in self.Entropy_LE_List[0:2]:
            item.setValidator(dim_validator)
            item.clear()
            item.setEnabled(False)
        for Label in [self.label_X_R, self.label_Y_Theta, self.label_Z_phi]:
            Label.setAlignment(Qt.AlignCenter)
        self.Import_Lists_PB.hide()
        self.Widget_Status()
        import re
        for s in self.Source_name_list:
            id = re.sub('.*?([0-9]*)$', r'\1', s)
            self.Source_id_list.append(id)
        if self.Source_id_list:
            self.Source_id = int(self.Source_id_list[-1]) + 1
        else:
            self.Source_id = 1
        self.Name_LE.setText(''.join([i for i in self.Name_LE.text() if not i.isdigit()]) + str(self.Source_id))

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
        # to show window at the middle of the screen and resize it to the screen size
        self.resize_ui()

    def _initButtons(self):
        self.Run_Mode_CB.currentIndexChanged.connect(self.Widget_Status)
        self.Photon_CB.stateChanged.connect(self.Widget_Status_1)
        self.Create_Surface_SRC_CB.stateChanged.connect(self.Widget_Status_2)
        self.Volume_Calc_CB.currentIndexChanged.connect(self.Widget_Status_3)
        self.Direction_Dist_CB.currentIndexChanged.connect(self.Widget_Status_4)
        self.Entropy_type_CB.currentIndexChanged.connect(self.Entropy_Widgets_Status)
        self.One_Source_RB.toggled.connect(self.Def_Source_Settings)
        self.Source_Geom_CB.currentIndexChanged.connect(self.Def_Source_Settings)
        self.Source_Geom_CB.currentIndexChanged.connect(self.Def_Source_Spatial)
        self.Source_Geom_CB.currentIndexChanged.connect(self.Def_Source_ToolTips)
        self.X_Dist_CB.currentIndexChanged.connect(self.Def_Source_ToolTips)
        self.Y_Dist_CB.currentIndexChanged.connect(self.Def_Source_ToolTips)
        self.Z_Dist_CB.currentIndexChanged.connect(self.Def_Source_ToolTips)
        self.Energy_Dist_CB.currentIndexChanged.connect(self.Def_Source_ToolTips)
        self.X_Dist_CB.currentIndexChanged.connect(self.Def_Source_Spatial_Dist_X)
        self.Y_Dist_CB.currentIndexChanged.connect(self.Def_Source_Spatial_Dist_Y)
        self.Z_Dist_CB.currentIndexChanged.connect(self.Def_Source_Spatial_Dist_Z)
        self.Energy_Dist_CB.currentIndexChanged.connect(self.Def_Source_Energy)
        self.Particle_CB.currentIndexChanged.connect(self.Def_Energy_Dist)
        self.Particle_CB.currentIndexChanged.connect(self.Choose_Only_Fissionable)
        self.Only_Fissionable_CB.stateChanged.connect(self.Choose_Only_Fissionable)
        self.Source_Geom_CB.currentIndexChanged.connect(self.Choose_Only_Fissionable)
        self.Create_Separate_SRC_CB.stateChanged.connect(self.Create_Separate_Source)
        self.Create_Surface_SRC_CB.stateChanged.connect(self.Create_Surface_Source)
        self.Source_Surfaces_CB.currentIndexChanged.connect(self.Add_Surface_Source)
        self.Import_Lists_PB.clicked.connect(lambda: self.Import_x_y_Lists(self.Energy_LE, self.Proba_LE))
        self.Add_Run_Mode_PB.clicked.connect(self.Run_Mode)
        self.Add_Vol_Calc_PB.clicked.connect(self.Volume_Calculation)
        self.Add_Entropy_PB.clicked.connect(self.Entropy_Settings)
        self.Add_Source_PB.clicked.connect(self.Add_Sources)
        self.Cells_CB.currentIndexChanged.connect(self.Add_Cells)
        self.Mat_CB.currentIndexChanged.connect(self.Add_Materials)
        self.Export_Settings_PB.clicked.connect(self.Export_to_Main_Window)
        self.Clear_PB.clicked.connect(self.clear_text)
        self.Exit_PB.clicked.connect(self.Exit)
        self.Def_Source_ToolTips()
        self.Photon_Cut.setDisabled(True)
        self.ttb_RB.setDisabled(True)
        self.led_RB.setDisabled(True)
        self.ttb_RB.setChecked(True)
        self.led_RB.setChecked(False)
        self.Create_Separate_SRC_CB.hide()
        self.Create_Surface_SRC_CB.hide()
        self.Source_Surfaces_CB.hide()
        self.Cells_CB.hide()
        self.Mat_CB.hide()
        self.LineEdit_3.hide()
        self.LineEdit_4.hide()
        self.LineEdit_6.hide()
        self.Particles_Max_LE.hide()
        self.Volume_Calc_CB.hide()
        self.Add_Vol_Calc_PB.hide()
        self.label_11.hide()
        self.Add_Run_Mode_PB.setEnabled(False)
        self.Add_Vol_Calc_PB.setEnabled(False)
        self.Add_Entropy_PB.setEnabled(False)
        self.Add_Source_PB.setEnabled(False)
        self.Num_of_Srcs_Label.setEnabled(False)
        self.Number_of_Sources.setEnabled(False)
        self.Only_Fissionable_CB.setEnabled(False)
        self.Only_Fissionable_CB.setChecked(False)
        self.Only_Fissionable = False
        self.Create_Separate_SRC = False
        self.Create_Surface_SRC = False
        self.Name_LE.setText('source')
        self.Origin_LE.hide()
        self.Origin_Label.hide()
        self.Disable_SRC_Widgets()

    def Find_string(self, text_window, string_to_find):
        self.list_of_items = []
        self.current_line = ''
        self.line_number = 0
        self.Insert_Header = True
        document = text_window.toPlainText()
        for line in document.split('\n'):
            self.line_number += 1
            if string_to_find in line:
                self.current_line = line
                self.list_of_items.append(line[0:len(line) -1])
                self.Insert_Header = False

    def Add_Cells(self):
        if self.Run_Mode_CB.currentIndex() == 3:
            if self.Cells_CB.currentIndex() != 0:
                self.list_of_cells.append(self.cell_name_list[self.Cells_CB.currentIndex() - 1])
                self.LineEdit_3.setText(str(self.list_of_cells).replace("'", ""))
            self.Cells_CB.setCurrentIndex(0)

    def Add_Materials(self):
        self.list_of_materials = self.materials_name_list
        if self.Mat_CB.currentIndex() != 0:
            self.LineEdit_6.setText(str(self.list_of_materials).replace("'", ""))
        self.Mat_CB.setCurrentIndex(0)

    def Widget_Status(self):                            # If Run Mode changed
        self.LineEdit_4.setText('')
        self.list_of_surfaces_ids.clear()
        if self.Run_Mode_CB.currentIndex() in [0, 1, 2]:
            for item in [self.Volume_Calc_CB, self.Source_Surfaces_CB, self.Cells_CB, self.Mat_CB, self.label_11,
                            self.LineEdit_4, self.LineEdit_3, self.LineEdit_6, self.Particles_Max_LE]:
                item.hide()
            for item in [self.Label_1, self.Label_2, self.Label_5, self.Label_37, self.LineEdit_1, self.LineEdit_2,
                        self.LineEdit_5, self.Particles_Number, self.Create_Separate_SRC_CB, self.Create_Surface_SRC_CB]:
                item.show()
                if self.Run_Mode_CB.currentIndex() == 0:
                    item.setEnabled(False)
                elif self.Run_Mode_CB.currentIndex() in [1, 2]:
                    item.setEnabled(True)
            if self.Run_Mode_CB.currentIndex() == 1:
                self.Label_1.setText('Batches')
                self.Label_2.setText('Inactive Batches')
                self.Label_5.setText('Generations')
                self.Label_37.setText('Particles')
                self.LineEdit_1.setText('110')
                self.LineEdit_2.setText('10')
                self.LineEdit_5.setText('10')
                self.Photon_Cut.setText('1000.0')
                self.Particles_Number.setText('10000')
        if self.Run_Mode_CB.currentIndex() in [1, 2]:
            self.Add_Run_Mode_PB.setEnabled(True)
            self.Volume_Calc_CB.hide()
            self.Cells_CB.hide()
            self.LineEdit_3.hide()
            self.LineEdit_6.hide()
            self.Mat_CB.hide()
            self.Create_Separate_SRC_CB.show()
            self.Create_Surface_SRC_CB.show()
            self.label_16.setEnabled(True)
            self.Photon_CB.setEnabled(True)
            '''self.Photon_Cut.setEnabled(False)'''
            self.ttb_RB.setChecked(True)
            self.led_RB.setChecked(False)
        else:
            '''self.Create_Separate_SRC_CB.hide()
            self.Create_Surface_SRC_CB.hide()'''
            self.Add_Run_Mode_PB.setEnabled(False)
            self.label_16.setEnabled(False)
            self.Label_17.setEnabled(False)
            self.Label_18.setEnabled(False)
            self.Photon_CB.setEnabled(False)
            '''self.Photon_Cut.setDisabled(False)'''
            self.ttb_RB.setEnabled(False)
            self.led_RB.setEnabled(False)
            self.Photon_Cut.setEnabled(False)
            self.Photon_CB.setChecked(False)
            self.Create_Separate_SRC_CB.setChecked(False)
            self.Create_Surface_SRC_CB.setChecked(False)
        if self.Run_Mode_CB.currentIndex() == 2:
            self.LineEdit_5.show()
            self.Label_5.show()
            self.Volume_Calc_CB.hide()
            self.Label_1.setText('Batches')
            self.LineEdit_1.setText('110')
            self.LineEdit_2.hide()
            self.Label_2.hide()
        if self.Run_Mode_CB.currentIndex() == 3:
            if self.Volume_Calc_CB.currentIndex() == 0:
                self.Add_Vol_Calc_PB.setEnabled(False)
            else:
                self.Add_Vol_Calc_PB.setEnabled(True)
            self.Volume_Calc_CB.setCurrentIndex(0)
            self.Add_Vol_Calc_PB.show()
            self.Add_Run_Mode_PB.hide()
            self.Volume_Calc_CB.show()
            self.LineEdit_1.hide()
            self.Label_1.hide()
            self.LineEdit_2.show()
            self.Label_2.show()
            self.Label_5.show()
            self.Label_5.setText('Lower Left (x, y, z)')
            self.Label_2.setText('Upper Right (x, y, z)')
            self.Geometry_Key(self.v_1)
            self.LineEdit_5.setText('(-1, -1, -1)')
            self.LineEdit_2.setText('(1, 1, 1)')
            self.Create_Separate_SRC_CB.setEnabled(False)
            self.Create_Surface_SRC_CB.setEnabled(False)
        else:
            self.Add_Vol_Calc_PB.hide()
            self.Add_Run_Mode_PB.show()
        self.Create_Separate_SRC_CB.setChecked(False)
        self.Create_Surface_SRC_CB.setChecked(False)

    def Widget_Status_1(self):                              # if photon mode changed
        if self.Photon_CB.isChecked():
            self.ttb_RB.setEnabled(True)
            self.led_RB.setEnabled(True)
            self.Photon_Cut.setEnabled(True)
            self.Label_17.setEnabled(True)
            self.Label_18.setEnabled(True)
        else:
            self.ttb_RB.setEnabled(False)
            self.led_RB.setEnabled(False)
            self.Photon_Cut.setEnabled(False)
            self.Label_17.setEnabled(False)
            self.Label_18.setEnabled(False)

    def Widget_Status_2(self):                              # if creating source mode changed
            if self.Create_Surface_SRC:
                self.Particles_Max_LE.show()
                self.LineEdit_4.show()
                self.Source_Surfaces_CB.show()
                self.Source_Surfaces_CB.setCurrentIndex(0)
            else:
                pass

    def Widget_Status_3(self):                              # if volume calculation option changed
        items = [self.Label_5, self.LineEdit_5, self.Label_37, self.Particles_Number, self.Label_2, self.LineEdit_2]
        if self.Volume_Calc_CB.currentIndex() == 0:
            self.Add_Vol_Calc_PB.setEnabled(False)
            for item in items:
                item.setEnabled(False)
        else:
            self.Add_Vol_Calc_PB.setEnabled(True)
            for item in items:
                item.setEnabled(True)
        if self.Volume_Calc_CB.currentIndex() == 1:
            for item in items:
                item.setEnabled(True)
        elif self.Volume_Calc_CB.currentIndex() == 2:
            self.LineEdit_5.setDisabled(True)
            self.LineEdit_2.setDisabled(True)
            self.Cells_CB.show()
            self.LineEdit_3.show()
            if self.cell_name_list:
                self.Cells_CB.addItems(self.cell_name_list)
            else:
                pass
        if self.Volume_Calc_CB.currentIndex() == 3:
            self.LineEdit_5.setDisabled(True)
            self.LineEdit_2.setDisabled(True)
            self.Cells_CB.hide()
            self.LineEdit_3.hide()
            self.LineEdit_5.setText('(-1, -1, -1)')
            self.LineEdit_2.setText('(1, 1, 1)')
        if self.Volume_Calc_CB.currentIndex() not in [2, 3, 6]:
            self.LineEdit_5.setEnabled(True)
            self.LineEdit_2.setEnabled(True)
        if self.Volume_Calc_CB.currentIndex() == 6:
            self.Mat_CB.show()
            self.LineEdit_6.show()
            self.Cells_CB.hide()
            self.LineEdit_3.hide()
            if self.materials_name_list:
                self.Mat_CB.addItem('Select material')
                self.Mat_CB.addItems(self.materials_name_list)
        else:
            self.Mat_CB.hide()
            self.LineEdit_6.hide()

    def Widget_Status_4(self):
        if self.Direction_Dist_CB.currentIndex() in [0, 1]:
            for item in [self.Mu_Min_LE, self.Mu_Max_LE, self.Phi_Min_LE, self.Phi_Max_LE,
                        self.label_10, self.Ref_UVW_CB,
                        self.Mu_Dist_CB, self.Phi_Dist_CB, self.label_20, self.label_21]:
                item.setEnabled(False)
        elif self.Direction_Dist_CB.currentIndex() in [2, 3]:
            for item in [self.label_10, self.Ref_UVW_CB]:
                item.setEnabled(True)
        elif self.Direction_Dist_CB.currentIndex() == 4:
            for item in [self.Mu_Min_LE, self.Mu_Max_LE, self.Phi_Min_LE, self.Phi_Max_LE,
                        self.label_10, self.Ref_UVW_CB,
                        self.Mu_Dist_CB, self.Phi_Dist_CB, self.label_20, self.label_21]:
                item.setEnabled(True)

    def Def_Settings(self, comboBox_Index, msg ):
        if comboBox_Index == 0:
            self.showDialog('Warning', msg)
            return
        else:
            self.Find_string(self.v_1, "openmc.Settings")
            if self.Insert_Header:
                self.Find_string(self.plainTextEdit, "openmc.Settings")
                if self.Insert_Header:
                    print('\n############################################################################### \n'
                             '#                 Exporting to OpenMC settings.xml file \n'
                             '###############################################################################')
                    print("settings = openmc.Settings()\n")
                else:
                    pass

    def Import_OpenMC(self):
        self.Find_string(self.plainTextEdit, "import openmc")
        if self.Insert_Header:
            self.Find_string(self.v_1, "import openmc")
            if self.Insert_Header:
                print('import openmc')

    def Run_Mode(self):
        self.Import_OpenMC()
        # /////////////////////////////   Run Mode   /////////////////////////////
        msg = 'Select Run Mode first ! '
        self.Def_Settings(self.Run_Mode_CB.currentIndex(), msg)
        string_to_find = "settings.run_mode"
        self.Find_string(self.v_1, string_to_find)
        if not self.Insert_Header:
            msg = 'Run Mode already specified in the project !'
            self.showDialog('Warning', msg)
            self.Run_Mode_Extra(self.v_1)
        else:
            self.Find_string(self.plainTextEdit, string_to_find)
            if not self.Insert_Header:
                msg = 'Only one run mode is allowed in the project !'
                self.showDialog('Warning', msg)
                self.Run_Mode_Extra(self.plainTextEdit)
            else:
                # Eigenvalue problem
                if self.Run_Mode_CB.currentIndex() == 1:
                    print("settings.run_mode = 'eigenvalue'")
                    print("settings.particles = " + str(self.Particles_Number.text()))
                    print("settings.batches = " + str(self.LineEdit_1.text()))
                    print("settings.inactive = " + self.LineEdit_2.text())
                    print("settings.generations = " + str(self.LineEdit_5.text()) + "\n")
                # Fixed source problem
                elif self.Run_Mode_CB.currentIndex() == 2:
                    print("settings.run_mode = 'fixed source'")
                    print("settings.particles = " + str(self.Particles_Number.text()))
                    print("settings.batches = " + str(self.LineEdit_1.text()))
                    print("settings.generations = " + str(self.LineEdit_5.text()) + "\n")
                if self.Run_Mode_CB.currentIndex() in [1, 2]:
                    if self.Photon_CB.isChecked():
                        print("settings.photon_transport = True")
                        print("settings.cutoff = {'energy_photon' : " + self.Photon_Cut.text() + " }")
                        if self.ttb_RB.isChecked():
                            print("settings.electron_treatment = 'ttb'")
                        elif self.led_RB.isChecked():
                            print("settings.electron_treatment = 'led'")
                    if self.Create_Separate_SRC_CB.isChecked():
                        print("settings.sourcepoint = {‘separate’: True}")
                    if self.Create_Surface_SRC_CB.isChecked():
                        self.LE_to_List1(self.LineEdit_4)
                        Surfaces_List = str(self.List)
                        print("settings.surf_source_write = { 'surfaces_ids': " + Surfaces_List + ", 'max_particles': " + str(self.Particles_Max_LE.text()) +" }")
        self.Run_Mode_CB.setCurrentIndex(0)
        self.Photon_CB.setChecked(False)
        self.Create_Separate_SRC_CB.setChecked(False)
        self.Create_Surface_SRC_CB.setChecked(False)

    def LE_to_List(self, LineEdit1, LineEdit2):
        text1 = LineEdit1.text()
        text2 = LineEdit2.text()
        self.Error = 0
        for separator in [',', ';', ':', ' ']:
            if separator in text1:
                text1 = str(' '.join(text1.replace(separator, ' ').split()))
        for separator in [',', ';', ':', ' ']:
            if separator in text2:
                text2 = str(' '.join(text2.replace(separator, ' ').split()))
        List1 = text1.split()    #(separator)
        List2 = text2.split()
        X_Length = len(List1)
        P_Length = len(List2)
        if X_Length == P_Length:
            pass
        else:
            self.showDialog('Warning', 'Lists must be the same length. Check the entered data !')
            return
            self.Error = 1
        LineEdit1.setText(str(List1).replace("'", ''))
        LineEdit2.setText(str(List2).replace("'", ''))

    def LE_to_List1(self, LineEdit):
        text = LineEdit.text()
        for separator in [',', ';', ':', ' ']:
            if separator in text:
                text = str(' '.join(text.replace(separator, ' ').split()))
        self.List = text.split() #str(text.split(separator)).replace("'", '')
        return self.List

    def Run_Mode_Extra(self, Document):
        if self.Create_Separate_SRC:
            self.Find_string(Document, "settings.sourcepoint")
            if self.Insert_Header:
                print("settings.sourcepoint = {‘separate’: True}")
        if self.Create_Surface_SRC:
            self.Find_string(Document, "settings.surf_source_write")
            if self.Insert_Header:
                print("settings.surf_source_write = { 'surfaces_ids': " + str(
                    self.LineEdit_4.text()) + ", 'max_particles': " + str(self.Particles_Max_LE.text()) + " }")
        if self.Photon_CB.isChecked():
            self.Find_string(Document, "settings.photon_transport")
            if self.Insert_Header:
                print("settings.photon_transport = True")
                print("settings.cutoff = {'energy_photon' : " + self.Photon_Cut.text() + " }")
                if self.ttb_RB.isChecked():
                    print("settings.electron_treatment = 'ttb'")
                elif self.led_RB.isChecked():
                    print("settings.electron_treatment = 'led'")
            else:
                self.Find_string(Document, "settings.electron_treatment")
                if self.Insert_Header:
                    if self.ttb_RB.isChecked():
                        print("settings.electron_treatment = 'ttb'")
                    elif self.led_RB.isChecked():
                        print("settings.electron_treatment = 'led'")

    def Volume_Calculation(self):
        self.Import_OpenMC()
        # Volume calculation
        self.Insert_Header = True
        msg = ' Select Volume Calculation option first !'
        self.Def_Settings(self.Volume_Calc_CB.currentIndex(), msg)
        if self.Volume_Calc_CB.currentIndex() != 0:
            self.Find_string(self.v_1, 'eigenvalue')
            if not self.Insert_Header:
                self.showDialog('Warning', 'Could not be added, Eigenvalue Mode already specified in the project !')
                return
            else:
                self.Find_string(self.v_1, 'fixed source')
                if not self.Insert_Header:
                    self.showDialog('Warning', 'Could not be added, Fixed-source Mode already specified in the project !')
                    return
                else:
                    self.Find_string(self.plainTextEdit, 'eigenvalue')
                    if not self.Insert_Header:
                        self.showDialog('Warning', 'Only one run mode is allowed in the project !')
                        return
                    else:
                        self.Find_string(self.plainTextEdit, 'fixed source')
                        if not self.Insert_Header:
                            self.showDialog('Warning', 'Only one run mode is allowed in the project !')
                            return
                        else:
                            string_to_find = "settings.run_mode = 'Volume'"
                            self.Find_string(self.plainTextEdit, string_to_find)
                            if self.Insert_Header:
                                self.Find_string(self.v_1, string_to_find)
                                if self.Insert_Header:
                                    print('# Volume calculation mode')
                                    print("settings.run_mode = 'Volume'")
                                    self.Insert_Header = False
                                else:
                                    string_to_find = 'openmc.VolumeCalculation'
                                    self.Find_string(self.v_1, string_to_find)
                                    self.Delete_lines(self.v_1, string_to_find, False)
                                    self.Delete_lines(self.v_1, 'settings.volume_calculations', True)
                                    for item in self.list_of_items:
                                        self.vol_calcs.append(item)
                            samples = str(self.Particles_Number.text())
                            if self.Volume_Calc_CB.currentIndex() == 1:     # Vol_Calc: General
                                Lower_Left = str(self.LineEdit_5.text())
                                Upper_Right = str(self.LineEdit_2.text())
                                self.vol_calcs.append('openmc.VolumeCalculation([domain1, domain2, ...], ' + samples +
                                                             ", lower_left = " + Lower_Left + ", upper_right = " + Upper_Right + ')')
                            if self.Volume_Calc_CB.currentIndex() == 2:     # Vol_Calc: Specific cells
                                self.vol_calcs.append('openmc.VolumeCalculation(' + self.LineEdit_3.text() + ", " + samples + ")")
                            if self.Volume_Calc_CB.currentIndex() == 3:     # Vol_Calc: Root cells
                                self.Geometry_Key(self.v_1)
                                self.vol_calcs.append('openmc.VolumeCalculation(list(' + self.Geo + ".cells.values()), " + samples + ")")
                            if self.Volume_Calc_CB.currentIndex() == 4:     # Vol_Calc: Cells in box
                                self.Geometry_Key(self.v_1)
                                self.vol_calcs.append('openmc.VolumeCalculation(list(' + self.Geo + ".cells.values()), " + samples + ', ' + self.Geo + '.bounding_box[0], ' + self.Geo + '.bounding_box[1])')
                            if self.Volume_Calc_CB.currentIndex() == 5:     # Vol_Calcs: Root
                                self.vol_calcs.append('openmc.VolumeCalculation([root], ' + samples + ', ' + self.Geo + '.bounding_box[0], ' + self.Geo + '.bounding_box[1])')
                            if self.Volume_Calc_CB.currentIndex() == 6:     # Vol_Calc: Materials
                                self.Geometry_Key(self.v_1)
                                self.vol_calcs.append('openmc.VolumeCalculation(' + self.LineEdit_6.text() + ", " + samples + ', ' + self.Geo + '.bounding_box[0], ' + self.Geo + '.bounding_box[1])' )
                            self.Find_string(self.plainTextEdit, 'openmc.VolumeCalculation')
                            if not self.Insert_Header:
                                self.Delete_lines(self.plainTextEdit, 'openmc.VolumeCalculation', False)
                                self.plainTextEdit.moveCursor(QtGui.QTextCursor.Start)
                                cursor = QtGui.QTextCursor(self.plainTextEdit.document().findBlockByLineNumber(self.pos))
                                self.plainTextEdit.setTextCursor(cursor)
                                for i, item in enumerate(self.vol_calcs):
                                    if i:
                                        print(',')
                                    print(item, end='')
                                print(" ]")
                            else:
                                print('vol_calcs = [')
                                for i, item in enumerate(self.vol_calcs):
                                    if i:
                                        print(',')
                                    print(item, end='')
                                print(" ]")
                                print("settings.volume_calculations = vol_calcs")
        self.Volume_Calc_CB.setCurrentIndex(0)
        self.Cells_CB.hide()
        self.LineEdit_3.hide()

    def Delete_lines(self, text_window, key, clear_flag):
        lines = text_window.toPlainText().split('\n')
        self.pos = 0
        key0 = key
        for i, w in reversed(list(enumerate(lines))):
            #print(i, w)
            if key in w:
                if clear_flag:
                    key = lines[i].split('=')[1].replace(' ', '')
                    key.strip()
                    clear_flag = False
                self.pos = i
                del lines[i]

        text_window.clear()
        cursor = text_window.textCursor()
        text_window.setTextCursor(cursor)
        for i, line in enumerate(lines):
            text_window.insertPlainText(line + '\n')

    def question(self, alert, msg) :
        qm = QMessageBox
        ret = qm.question(self, alert, msg, qm.Yes | qm.No)
        if ret == qm.Yes:
            self.Close_Project()
            self.NewFiles()
        elif ret == qm.No:
            pass

    def Entropy_Settings(self):
        # /////////////////////////   Entropy Setting   /////////////////////////
        if self.Entropy_type_CB.currentIndex() == 1:
            if self.X_LL_Entropy.text() and self.Y_LL_Entropy.text() and self.Y_LL_Entropy.text()\
                    and self.X_UR_Entropy.text() and self.Y_UR_Entropy.text() and self.Y_UR_Entropy.text()\
                    and self.Z_UR_Entropy.text() and self.X_dim.text() and self.Y_dim.text() and self.Z_dim.text():
                LL = str((self.X_LL_Entropy.text(), self.Y_LL_Entropy.text(), self.Z_LL_Entropy.text())).replace("'", "")
                UR = str((self.X_UR_Entropy.text(), self.Y_UR_Entropy.text(), self.Z_UR_Entropy.text())).replace("'","")
                dim = str((self.X_dim.text(), self.Y_dim.text(), self.Z_dim.text())).replace("'","")
                for item in self.Entropy_LE_List:
                    item.clear()
            else:
                ret = QMessageBox.question(self, 'Warning', 'All the fields must be filled or default data will be used.\nThe default data may be incompatible with the model geometry!\nUse the default data ?')
                if ret == QMessageBox.Yes:
                    LL = "(-50, -50, -25))"
                    UR = "(50, 50, 25)"
                    dim = "(8, 8, 8)"
                elif ret == QMessageBox.No:
                    return

            print("\nentropy_mesh = openmc.RegularMesh()")
            print("entropy_mesh.lower_left = " + LL)
            print("entropy_mesh.upper_right = " + UR)
            print("entropy_mesh.dimension = " + dim)
            print("settings.entropy_mesh = entropy_mesh\n")
        elif self.Entropy_type_CB.currentIndex() == 2:
            self.Geometry_Key(self.v_1)
            print("\nentropy_mesh = openmc.RegularMesh()")
            print("entropy_mesh.lower_left, entropy_mesh.upper_right = " + self.Geo + ".bounding_box")
            print("entropy_mesh.dimension = (8, 8, 8)")
            print("settings.entropy_mesh = entropy_mesh\n")

        self.Entropy_type_CB.setCurrentIndex(0)

    def Entropy_Widgets_Status(self):
        if self.Entropy_type_CB.currentIndex() == 1:
            for item in self.Entropy_LE_List:
                item.setEnabled(True)
        else:
            for item in self.Entropy_LE_List:
                item.clear()
                item.setEnabled(False)
        if self.Entropy_type_CB.currentIndex() == 0:
            self.Add_Entropy_PB.setEnabled(False)
        else:
            self.Add_Entropy_PB.setEnabled(True)

    def Def_Source_Settings(self):
        # /////////////////////////   Source Settings   /////////////////////////
        if self.One_Source_RB.isChecked():
            self.Num_of_Srcs_Label.setEnabled(False)
            self.Number_of_Sources.setEnabled(False)
        else:
            self.Num_of_Srcs_Label.setEnabled(True)
            self.Number_of_Sources.setEnabled(True)

        self.Name_LE.setText(''.join([i for i in self.Name_LE.text() if not i.isdigit()]) + str(self.Source_id))
        self.spatial = 'spatial' + str(self.Source_id)
        self.angle = 'angle' + str(self.Source_id)
        self.energy = 'energy' + str(self.Source_id)
        if self.Source_Geom_CB.currentIndex() == 0:
            self.Particle_CB.setCurrentIndex(0)
            self.Add_Source_PB.setEnabled(False)
        else:
            self.Add_Source_PB.setEnabled(True)

    def Def_Energy_Dist(self):
        self.Energy_Dist_CB.clear()
        self.Energy_Dist_CB.addItem('Energy distribution')
        if self.Particle_CB.currentIndex() == 0:
            self.Energy_Dist_CB.addItems(['Discrete', 'Maxwell', 'Watt', 'Tabular'])
        else:
            self.Energy_Dist_CB.addItems(['Discrete', 'Tabular'])

    def Choose_Only_Fissionable(self):
        if self.Source_Geom_CB.currentIndex() == 2:
            if self.Particle_CB.currentIndex() == 0:
                self.Only_Fissionable_CB.setEnabled(True)
            else:
                self.Only_Fissionable_CB.setEnabled(False)
            if self.Only_Fissionable_CB.isChecked():
                self.Only_Fissionable = True
            else:
                self.Only_Fissionable = False
        else:
            self.Only_Fissionable_CB.setEnabled(False)
            self.Only_Fissionable_CB.setChecked(False)
            self.Only_Fissionable = False

    def Create_Separate_Source(self):
        if self.Create_Separate_SRC_CB.isChecked():
            self.Create_Separate_SRC = True
        else:
            self.Create_Separate_SRC = False

    def Add_Surface_Source(self):
        if self.Create_Surface_SRC:
            self.list_of_surfaces.append(self.surface_name_list[self.Source_Surfaces_CB.currentIndex() - 1])
            self.list_of_surfaces_ids.append(self.surface_id_list[self.Source_Surfaces_CB.currentIndex()])
            self.LineEdit_4.setText(str(self.list_of_surfaces_ids).replace("'", ""))

    def Create_Surface_Source(self):
        if self.Create_Surface_SRC_CB.isChecked():
            self.Create_Surface_SRC = True
            self.Source_Surfaces_CB.show()
            self.LineEdit_4.show()
            self.label_11.show()
            self.Particles_Max_LE.show()
        else:
            self.Create_Surface_SRC = False
            self.Source_Surfaces_CB.hide()
            self.LineEdit_4.hide()
            self.label_11.hide()
            self.Particles_Max_LE.hide()

    def Def_Source_Spatial(self):
        if self.Source_Geom_CB.currentIndex() in [0, 1, 2]:
            self.label_12.setEnabled(False)
            for LineEdit in [self.X_LL, self.Y_LL, self.Z_LL]:
                LineEdit.clear()
            for LineEdit in [self.X_UR, self.Y_UR, self.Z_UR]:
                LineEdit.clear()
            for combobox in [self.X_Dist_CB, self.Y_Dist_CB, self.Z_Dist_CB]:
                combobox.setCurrentIndex(0)
        if self.Source_Geom_CB.currentIndex() in [0, 6, 7]:
            self.Disable_SRC_Widgets()
        else:
            self.Enable_SRC_ED_Widgets()
        if self.Source_Geom_CB.currentIndex() == 1:                  #  Point Source
            self.label_X_R.setEnabled(True)
            self.label_Y_Theta.setEnabled(True)
            self.label_Z_phi.setEnabled(True)
            self.LL_label.setEnabled(True)
            self.UR_label.setEnabled(False)
            self.X_LL.setEnabled(True)
            self.Y_LL.setEnabled(True)
            self.Z_LL.setEnabled(True)
            for combobox in [self.X_Dist_CB, self.Y_Dist_CB, self.Z_Dist_CB]:
                    combobox.setEnabled(False)
            self.X_UR.setEnabled(False)
            self.Y_UR.setEnabled(False)
            self.Z_UR.setEnabled(False)
            self.LL_label.setText('Coordinates')
        elif self.Source_Geom_CB.currentIndex() in [2, 3, 4, 5]:
            if self.Source_Geom_CB.currentIndex() == 2:
                self.LL_label.setText('Lower left')
                self.UR_label.setText('Upper right')
                for combobox in [self.X_Dist_CB, self.Y_Dist_CB, self.Z_Dist_CB]:
                    combobox.setEnabled(False)
            if self.Source_Geom_CB.currentIndex() in [3, 4, 5]:
                self.label_12.setEnabled(True)
                self.LL_label.setText('min/values')
                self.UR_label.setText('max/proba')
                for combobox in [self.X_Dist_CB, self.Y_Dist_CB, self.Z_Dist_CB]:
                    combobox.setEnabled(True)
                if self.Source_Geom_CB.currentIndex() in [4, 5]:
                    self.Origin_Label.show()
                    self.Origin_Label.setText('origin')
                    self.Origin_LE.show()
                    self.Origin_LE.setText('(0. ,0., 0.)')
                    self.label_X_R.setText('R')
                    self.label_Y_Theta.setText('Theta')
                    if self.Source_Geom_CB.currentIndex() == 4:
                        self.label_Z_phi.setText('Phi')
                    if self.Source_Geom_CB.currentIndex() == 5:
                        self.label_Z_phi.setText('Z')
                    for combobox in [self.X_Dist_CB, self.Y_Dist_CB, self.Z_Dist_CB]:
                        combobox.view().setRowHidden(2, True)

            self.label_X_R.setEnabled(True)
            self.label_Y_Theta.setEnabled(True)
            self.label_Z_phi.setEnabled(True)
            self.LL_label.setEnabled(True)
            self.X_LL.setEnabled(True)
            self.Y_LL.setEnabled(True)
            self.Z_LL.setEnabled(True)
            self.UR_label.setEnabled(True)
            self.X_UR.setEnabled(True)
            self.Y_UR.setEnabled(True)
            self.Z_UR.setEnabled(True)
        if self.Source_Geom_CB.currentIndex() not in [4, 5]:
            self.label_X_R.setText('X')
            self.label_Y_Theta.setText('Y')
            self.label_Z_phi.setText('Z')
            self.Origin_Label.hide()
            self.Origin_LE.hide()
            for combobox in [self.X_Dist_CB, self.Y_Dist_CB, self.Z_Dist_CB]:
                combobox.view().setRowHidden(2, False)
        for combobox in [self.X_Dist_CB, self.Y_Dist_CB, self.Z_Dist_CB]:
            combobox.setCurrentIndex(0)
        if self.Source_Geom_CB.currentIndex() in [6, 7]:
            self.src_filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', "~", "source*.h5;; surface*.h5;; *.h5")[0]
            if self.src_filename:
                self.Origin_Label.show()
                self.Origin_Label.setText('File name')
                self.Origin_LE.show()
                if self.directory and self.directory in self.src_filename:
                    self.src_filename = self.src_filename.split('/')[-1]
                self.Origin_LE.setText(self.src_filename)
            else:
                self.Source_Geom_CB.setCurrentIndex(0)

    def Def_Source_Energy(self):
        if self.Energy_Dist_CB.currentIndex() == 1:  # Discrete
            self.Proba_LE.show()
            self.label_14.show()
            self.label_13.setText('Energy in eV')
            self.label_14.setText('Probability')
            self.Energy_LE.setEnabled(True)
            self.Proba_LE.setEnabled(True)
            self.label_13.setEnabled(True)
            self.label_14.setEnabled(True)
            self.Interpolate_CB.setEnabled(False)
            self.Import_Lists_PB.show()
        elif self.Energy_Dist_CB.currentIndex() == 2:  # Maxwell
            self.Energy_LE.setEnabled(True)
            self.Proba_LE.hide()
            self.label_14.hide()
            self.Energy_LE.setEnabled(True)
            self.label_13.setEnabled(True)
            self.Interpolate_CB.setEnabled(False)
            self.label_13.setText('TM in eV')
            self.Import_Lists_PB.hide()
        elif self.Energy_Dist_CB.currentIndex() == 3:  # Watt
            self.Proba_LE.show()
            self.label_14.show()
            self.Energy_LE.setEnabled(True)
            self.Proba_LE.setEnabled(True)
            self.label_13.setEnabled(True)
            self.label_14.setEnabled(True)
            self.label_13.setText('Param. a in eV')
            self.label_14.setText('Param. b in 1/eV')
            self.Interpolate_CB.setEnabled(False)
            self.Import_Lists_PB.hide()
        elif self.Energy_Dist_CB.currentIndex() == 4:  # Tabular
            self.Proba_LE.show()
            self.label_14.show()
            self.Energy_LE.setEnabled(True)
            self.Proba_LE.setEnabled(True)
            self.label_13.setEnabled(True)
            self.label_14.setEnabled(True)
            self.label_13.setText('Energy in eV')
            self.label_14.setText('Probability')
            self.Interpolate_CB.setEnabled(True)
            self.Import_Lists_PB.show()
        else:
            self.Proba_LE.show()
            self.label_14.show()
            self.label_13.setEnabled(False)
            self.Energy_LE.setEnabled(False)
            self.Proba_LE.setEnabled(False)
            self.label_14.setEnabled(False)
            self.label_13.setText('Energy in eV')
            self.label_14.setText('Probability')
            self.Interpolate_CB.setEnabled(False)
            self.Import_Lists_PB.hide()

    def Import_x_y_Lists(self, line1, line2):
        self.Imported_X_Y_List = True
        if self.Energy_Dist_CB.currentIndex() in [1, 4]:
            file = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', "~", "*;; *.inp;; *.dat;; *.txt")[0]
        if file:
            f = open(file, "r")
            lines = f.readlines()
            x = []; y = []
            for line in lines:
                x.append(line.split()[0])
                y.append(line.split()[1])
            f.close()
            line1.setText(str(x).replace("'", ""))
            line2.setText(str(y).replace("'", ""))

    def Disable_SRC_Widgets(self):
        for label in [self.label_X_R, self.label_Y_Theta, self.label_Z_phi, self.label_12, self.LL_label, self.UR_label,
                      self.label_10, self.label_13, self.label_14, self.label_20, self.label_21]:
            label.setEnabled(False)
        for lineedit in [self.X_LL, self.Y_LL, self.Z_LL, self.X_UR, self.Y_UR, self.Z_UR, self.Energy_LE,
                         self.Proba_LE, self.Mu_Min_LE, self.Phi_Min_LE, self.Mu_Max_LE, self.Phi_Max_LE]:
            lineedit.setEnabled(False)
        for combobox in [self.X_Dist_CB, self.Y_Dist_CB, self.Z_Dist_CB, self.Energy_Dist_CB, self.Interpolate_CB,
                         self.Direction_Dist_CB, self.Ref_UVW_CB, self.Mu_Dist_CB, self.Phi_Dist_CB]:
            combobox.setEnabled(False)

    def Enable_SRC_ED_Widgets1(self):
        for label in [self.label_10, self.label_13, self.label_14, self.label_20, self.label_21]:
            label.setEnabled(True)
        for lineedit in [self.Energy_LE, self.Proba_LE, self.Mu_Min_LE, self.Phi_Min_LE, self.Mu_Max_LE, self.Phi_Max_LE]:
            lineedit.setEnabled(True)
        for combobox in [self.Energy_Dist_CB, self.Interpolate_CB, self.Direction_Dist_CB, self.Ref_UVW_CB, self.Mu_Dist_CB, self.Phi_Dist_CB]:
            combobox.setEnabled(True)

    def Enable_SRC_ED_Widgets(self):
        for combobox in [self.Energy_Dist_CB, self.Direction_Dist_CB]:
            combobox.setEnabled(True)

    def Def_Source_Spatial_Dist_X(self):
        if self.X_Dist_CB.currentIndex() in [1, 2]:
            if self.Source_Geom_CB.currentIndex() == 3:
                self.X_LL.setText('')
                self.X_UR.setText('')
            elif self.Source_Geom_CB.currentIndex() in [4, 5]:
                self.X_LL.setText('')
                self.X_UR.setText('')
            self.X_LL.setStyleSheet("QLineEdit{color:black}")
            self.X_UR.setStyleSheet("QLineEdit{color:black}")
        else:
            self.X_LL.clear()
            self.X_UR.clear()

    def Def_Source_Spatial_Dist_Y(self):
        if self.Y_Dist_CB.currentIndex() in [1, 2]:
            if self.Source_Geom_CB.currentIndex() == 3:
                self.Y_LL.setText('')
                self.Y_UR.setText('')
            elif self.Source_Geom_CB.currentIndex() == 4:
                self.Y_LL.setText('')
                self.Y_UR.setText('')
            elif self.Source_Geom_CB.currentIndex() == 5:
                self.Y_LL.setText('')
                self.Y_UR.setText('')
            self.Y_LL.setStyleSheet("QLineEdit{color:black}")
            self.Y_UR.setStyleSheet("QLineEdit{color:black}")
        else:
            self.Y_LL.clear()
            self.Y_UR.clear()

    def Def_Source_Spatial_Dist_Z(self):
        if self.Z_Dist_CB.currentIndex() in [1, 2]:
            if self.Source_Geom_CB.currentIndex() in [3, 5]:
                self.Z_LL.setText('')
                self.Z_UR.setText('')
            elif self.Source_Geom_CB.currentIndex() == 4:
                self.Z_LL.setText('')
                self.Z_UR.setText('')
            self.Z_LL.setStyleSheet("QLineEdit{color:black}")
            self.Z_UR.setStyleSheet("QLineEdit{color:black}")
        else:
            self.Z_LL.clear()
            self.Z_UR.clear()

    def Change_Text_Color(self):
        for LineEdit in [self.X_LL, self.X_UR, self.Y_LL, self.Y_UR, self.Z_LL, self.Z_UR, self.Energy_LE, self.Proba_LE,
                         self.Mu_Min_LE, self.Mu_Max_LE, self.Phi_Min_LE, self.Phi_Min_LE]:
            LineEdit.setStyleSheet("QLineEdit{color:black}")

    def Source_Spatial_Distribution(self):
        Error = 0
        self.Error = 0
        self.ErrorSP = 0
        #  //////////////////////////////// Spatial distribution ////////////////////////////////
        if self.Source_Geom_CB.currentIndex() == 0:
            self.showDialog('Warning', 'Choose option first !')
            return
        if self.Source_Geom_CB.currentIndex() in [1, 2, 3, 4, 5]:
            if self.X_LL.text() == '' or self.Y_LL.text() == '' or self.Z_LL.text() == '':
                self.showDialog('Warning', 'Fill the given fields first !')
                self.ErrorSP = 1
                return
        if self.Source_Geom_CB.currentIndex() in [2, 3, 4, 5]:
            if self.X_UR.text() == '' or self.Y_UR.text() == '' or self.Z_UR.text() == '':
                self.showDialog('Warning', 'Fill the given fields first !')
                self.ErrorSP = 1
                return
        if self.Source_Geom_CB.currentIndex() == 1:
            ###################################  Point Source ###################################
            print(self.spatial + '= openmc.stats.Point([ ' + str(self.X_LL.text()) + ', ' + str(self.Y_LL.text()) + ', ' + str(self.Z_LL.text()) + '])')
        elif self.Source_Geom_CB.currentIndex() == 2:
            ####################################  Box Source ####################################
            print(self.spatial + ' = openmc.stats.Box([ ' + str(self.X_LL.text()) + ', ' + str(self.Y_LL.text()) + ', ' + str(self.Z_LL.text()) + '], [ '
                  + str(self.X_UR.text()) + ', ' + str(self.Y_UR.text()) + ', ' + str(self.Z_UR.text()) + ']' + self.Only_Fissionable_String +')')
        elif self.Source_Geom_CB.currentIndex() == 3:
            ############################### Cartesian Independent ###############################
            if self.X_Dist_CB.currentIndex() == 0:                      # Uniform
                x_min = str(self.X_LL.text())
                x_max = str(self.X_UR.text())
                print('x_dist = openmc.stats.Uniform(' + x_min +', ' + x_max + ')')
            elif self.X_Dist_CB.currentIndex() == 1:                    # X Discrete
                # validator
                self.LE_to_List(self.X_LL, self.X_UR)
                print('x_dist = openmc.stats.Discrete(' + self.X_LL.text() + ', ' + self.X_UR.text() + ')')
                if self.Error == 1:
                    Error += self.Error
                    self.X_LL.setStyleSheet("QLineEdit{color:red}")
                    self.X_UR.setStyleSheet("QLineEdit{color:red}")
                    self.plainTextEdit.setStyleSheet("QTextEdit{color:red}")
                    print('# Error: The lists in the line above must be the same length !')
            elif self.X_Dist_CB.currentIndex() == 2:                    # X Tabular
                self.LE_to_List(self.X_LL, self.X_UR)
                print('x_dist = openmc.stats.Tabular(' + str(self.X_LL.text()) + ', ' + str(self.X_UR.text()) + ')')
                if self.Error == 1:
                    Error += self.Error
                    self.X_LL.setStyleSheet("QLineEdit{color:red}")
                    self.X_UR.setStyleSheet("QLineEdit{color:red}")
                    self.plainTextEdit.setStyleSheet("QTextEdit{color:red}")
                    print('# Error: The lists in the line above must be the same length !')
            if self.Y_Dist_CB.currentIndex() == 0:                      # X Uniform
                y_min = str(self.Y_LL.text())
                y_max = str(self.Y_UR.text())
                print('y_dist = openmc.stats.Uniform(' + y_min + ', ' + y_max + ')')
            elif self.Y_Dist_CB.currentIndex() == 1:                    # Y Discrete
                self.LE_to_List(self.Y_LL, self.Y_UR)
                print('y_dist = openmc.stats.Discrete(' + str(self.Y_LL.text()) + ', ' + str(self.Y_UR.text()) + ')')
                if self.Error == 1:
                    Error += self.Error
                    self.Y_LL.setStyleSheet("QLineEdit{color:red}")
                    self.Y_UR.setStyleSheet("QLineEdit{color:red}")
                    self.plainTextEdit.setStyleSheet("QTextEdit{color:red}")
                    print('# Error: The lists in the line above must be the same length !')
            elif self.Y_Dist_CB.currentIndex() == 2:                    # Y Tabular
                self.LE_to_List(self.Y_LL, self.Y_UR)
                print('y_dist = openmc.stats.Tabular(' + str(self.Y_LL.text()) + ', ' + str(self.Y_UR.text()) + ')')
                if self.Error == 1:
                    Error += self.Error
                    self.Y_LL.setStyleSheet("QLineEdit{color:red}")
                    self.Y_UR.setStyleSheet("QLineEdit{color:red}")
                    self.plainTextEdit.setStyleSheet("QTextEdit{color:red}")
                    print('# Error: The lists in the line above must be the same length !')
            if self.Z_Dist_CB.currentIndex() == 0:                      # Z Uniform
                z_min = str(self.Z_LL.text())
                z_max = str(self.Z_UR.text())
                print('z_dist = openmc.stats.Uniform(' + z_min + ', ' + z_max + ')')
            elif self.Z_Dist_CB.currentIndex() == 1:                    # Discrete
                self.LE_to_List(self.Z_LL, self.Z_UR)
                print('z_dist = openmc.stats.Discrete(' + str(self.Z_LL.text()) + ', ' + str(self.Z_UR.text()) + ')')
                if self.Error == 1:
                    Error += self.Error
                    self.Z_LL.setStyleSheet("QLineEdit{color:red}")
                    self.Z_UR.setStyleSheet("QLineEdit{color:red}")
                    self.plainTextEdit.setStyleSheet("QTextEdit{color:red}")
                    print('# Error: The lists in the line above must be the same length !')
            elif self.Z_Dist_CB.currentIndex() == 2:                    # Tabular
                self.LE_to_List(self.Z_LL, self.Z_UR)
                print('z_dist = openmc.stats.Tabular(' + str(self.Z_LL.text()) + ', ' + str(self.Z_UR.text()) + ')')
                if self.Error == 1:
                    Error += self.Error
                    self.Z_LL.setStyleSheet("QLineEdit{color:red}")
                    self.Z_UR.setStyleSheet("QLineEdit{color:red}")
                    self.plainTextEdit.setStyleSheet("QTextEdit{color:red}")
                    print('# Error: The lists in the line above must be the same length !')
            print(self.spatial + ' = openmc.stats.CartesianIndependent(x_dist, y_dist, z_dist)')
        elif self.Source_Geom_CB.currentIndex() == 4:
            ################################## Spherical Independent ################################
            if self.X_Dist_CB.currentIndex() == 0:                      # R Uniform
                R_min = str(self.X_LL.text())
                R_max = str(self.X_UR.text())
                print('r_dist = openmc.stats.Uniform(' + R_min +', ' + R_max + ')')
            elif self.X_Dist_CB.currentIndex() == 1:                    # R Discrete
                self.LE_to_List(self.X_LL, self.X_UR)
                print('r_dist = openmc.stats.Discrete(' + str(self.X_LL.text()) + ', ' + str(self.X_UR.text()) + ')')
                if self.Error == 1:
                    Error += self.Error
                    self.X_LL.setStyleSheet("QLineEdit{color:red}")
                    self.X_UR.setStyleSheet("QLineEdit{color:red}")
                    self.plainTextEdit.setStyleSheet("QTextEdit{color:red}")
                    print('# Error: The lists in the line above must be the same length !')
            if self.Y_Dist_CB.currentIndex() == 0:                      # Theta Uniform
                theta_min = str(self.Y_LL.text())
                theta_max = str(self.Y_UR.text())
                print('theta_dist = openmc.stats.Uniform(' + theta_min + ', ' + theta_max + ')')
            elif self.Y_Dist_CB.currentIndex() == 1:                    # Theta Discrete
                self.LE_to_List(self.Y_LL, self.Y_UR)
                print('theta_dist = openmc.stats.Discrete(' + str(self.Y_LL.text()) + ', ' + str(self.Y_UR.text()) + ')')
                if self.Error == 1:
                    Error += self.Error
                    self.Y_LL.setStyleSheet("QLineEdit{color:red}")
                    self.Y_UR.setStyleSheet("QLineEdit{color:red}")
                    self.plainTextEdit.setStyleSheet("QTextEdit{color:red}")
                    print('# Error: The lists in the line above must be the same length !')
            if self.Z_Dist_CB.currentIndex() == 0:                      # Phi Uniform
                phi_min = str(self.Z_LL.text())
                phi_max = str(self.Z_UR.text())
                print('phi_dist = openmc.stats.Uniform(' + phi_min + ', ' + phi_max + ')')
            elif self.Z_Dist_CB.currentIndex() == 1:                    # Phi Discrete
                self.LE_to_List(self.Z_LL, self.Z_UR)
                print('phi_dist = openmc.stats.Discrete(' + str(self.Z_LL.text()) + ', ' + str(self.Z_UR.text()) + ')')
                if self.Error == 1:
                    Error += self.Error
                    self.Z_LL.setStyleSheet("QLineEdit{color:red}")
                    self.Z_UR.setStyleSheet("QLineEdit{color:red}")
                    self.plainTextEdit.setStyleSheet("QTextEdit{color:red}")
                    print('# Error: The lists in the line above must be the same length !')
            print(self.spatial + ' = openmc.stats.SphericalIndependent(r_dist, theta_dist, phi_dist, origin=' + str(self.Origin_LE.text()) + ')')
        elif self.Source_Geom_CB.currentIndex() == 5:
            ############################### Cylindrical Independent ###############################
            if self.X_Dist_CB.currentIndex() == 0:                          # R Uniform
                R_min = str(self.X_LL.text())
                R_max = str(self.X_UR.text())
                print('r_dist = openmc.stats.Uniform(' + R_min + ', ' + R_max + ')')
            elif self.X_Dist_CB.currentIndex() == 1:                        # R Discrete
                self.LE_to_List(self.X_LL, self.X_UR)
                print('r_dist = openmc.stats.Discrete(' + str(self.X_LL.text()) + ', ' + str(self.X_UR.text()) + ')')
                if self.Error == 1:
                    Error += self.Error
                    self.X_LL.setStyleSheet("QLineEdit{color:red}")
                    self.X_UR.setStyleSheet("QLineEdit{color:red}")
                    self.plainTextEdit.setStyleSheet("QTextEdit{color:red}")
                    print('# Error: The lists in the line above must be the same length !')
            if self.Y_Dist_CB.currentIndex() == 0:                          # Phi Uniform
                phi_min = str(self.Y_LL.text())
                phi_max = str(self.Y_UR.text())
                print('phi_dist = openmc.stats.Uniform(' + phi_min + ', ' + phi_max + ')')
            elif self.Y_Dist_CB.currentIndex() == 1:                        # Phi Discrete
                self.LE_to_List(self.Y_LL, self.Y_UR)
                print('phi_dist = openmc.stats.Discrete(' + str(self.Y_LL.text()) + ', ' + str(self.Y_UR.text()) + ')')
                if self.Error == 1:
                    Error += self.Error
                    self.Y_LL.setStyleSheet("QLineEdit{color:red}")
                    self.Y_UR.setStyleSheet("QLineEdit{color:red}")
                    self.plainTextEdit.setStyleSheet("QTextEdit{color:red}")
                    print('# Error: The lists in the line above must be the same length !')
            if self.Z_Dist_CB.currentIndex() == 0:                          # Z Uniform
                z_min = str(self.Z_LL.text())
                z_max = str(self.Z_UR.text())
                print('z_dist = openmc.stats.Uniform(' + z_min + ', ' + z_max + ')')
            elif self.Z_Dist_CB.currentIndex() == 1:                        # Z Discrete
                self.LE_to_List(self.Z_LL, self.Z_UR)
                print('z_dist = openmc.stats.Discrete(' + str(self.Z_LL.text()) + ', ' + str(self.Z_UR.text()) + ')')
                if self.Error == 1:
                    Error += self.Error
                    self.Z_LL.setStyleSheet("QLineEdit{color:red}")
                    self.Z_UR.setStyleSheet("QLineEdit{color:red}")
                    self.plainTextEdit.setStyleSheet("QTextEdit{color:red}")
                    print('# Error: The lists in the line above must be the same length !')
            print(self.spatial + ' = openmc.stats.CylindricalIndependent(r_dist, phi_dist, z_dist, origin=' + str(self.Origin_LE.text()) + ')')
        if Error != 0:
            self.showDialog('Warning', 'Some lists in spatial distribution must be the same length !')

    def Source_Energy_Distribution(self):
        # ////////////////////////////////   Energy distribution   ////////////////////////////////
        self.Error = 0
        self.ErrorEn = 0
        if self.Source_Geom_CB.currentIndex() not in [6, 7]:
            if self.Energy_LE == '' or self.Proba_LE == '':
                self.showDialog('Warning', 'Fill the given fields first !')
                self.ErrorEn = 1
                return
            if self.Energy_Dist_CB.currentIndex() == 1:      # Discrete
                self.Proba_LE.setEnabled(True)
                self.label_14.setEnabled(True)
                self.Interpolate_CB.setEnabled(False)
                if not self.Imported_X_Y_List:
                    self.LE_to_List(self.Energy_LE, self.Proba_LE)
                print(self.energy + ' = openmc.stats.Discrete(' + self.Energy_LE.text() + ', ' + self.Proba_LE.text() + ')')
                if self.Error == 1:
                    self.Energy_LE.setStyleSheet("QLineEdit{color:red}")
                    self.Proba_LE.setStyleSheet("QLineEdit{color:red}")
                    self.plainTextEdit.setStyleSheet("QTextEdit{color:red}")
                    print('# Error: The lists in the line above must be the same length !')
            elif self.Energy_Dist_CB.currentIndex() == 2:      # Maxwell
                self.Proba_LE.setEnabled(False)
                self.label_14.setEnabled(False)
                self.Interpolate_CB.setEnabled(False)
                print(self.energy + ' = openmc.stats.Maxwell(' + self.Energy_LE.text() + ')')
            elif self.Energy_Dist_CB.currentIndex() == 3:      # Watt
                self.Proba_LE.setEnabled(True)
                self.label_14.setEnabled(True)
                self.Interpolate_CB.setEnabled(False)
                print(self.energy + ' = openmc.stats.Watt(' + self.Energy_LE.text() + ', ' + self.Proba_LE.text() + ')')
            elif self.Energy_Dist_CB.currentIndex() == 4:      # Tabular
                self.Proba_LE.setEnabled(True)
                self.label_14.setEnabled(True)
                self.Interpolate_CB.setEnabled(True)
                if self.Energy_LE == '' or self.Proba_LE == '':
                    self.showDialog('Warning', 'Energy and Proba lists must be provided !')
                    return
                else:
                    if not self.Imported_X_Y_List:
                        self.LE_to_List(self.Energy_LE, self.Proba_LE)
                    if self.Interpolate_CB.currentIndex() == 0:
                        self.showDialog('Warning', 'Select Interpolation type first !')
                        return
                    else:
                        print(self.energy + ' = openmc.stats.Tabular(' + self.Energy_LE.text() + ', ' + self.Proba_LE.text() +  ',' + ' interpolation=' + "'" + self.Interpolate_CB.currentText() + "' )")
                if self.Error == 1:
                    self.Energy_LE.setStyleSheet("QLineEdit{color:red}")
                    self.Proba_LE.setStyleSheet("QLineEdit{color:red}")
                    self.plainTextEdit.setStyleSheet("QTextEdit{color:red}")
                    print('# Error: The lists in the line above must be the same length !')
            else:
                '''self.Energy_LE.setEnabled(False)
                self.Proba_LE.setEnabled(False)
                self.label_14.setEnabled(False)
                self.Interpolate_CB.setEnabled(False)'''
                #self.showDialog('Warning', 'Select energy distribution !')
                return
            if self.Error == 1:
                self.showDialog('Warning', 'The lists in the energy distribution must be the same length !')
                return

    def Source_Angle_Distribution(self):
        #   ////////////////////////////////   Angle distribution   /////////////////////////////////
        Error = 0
        self.Error = 0
        if self.Direction_Dist_CB.currentIndex() in [0, 1, 2, 3]:
            for item in [self.Mu_Min_LE, self.Mu_Max_LE, self.Phi_Min_LE, self.Phi_Min_LE,
                        self.label_10, self.Ref_UVW_CB]:
                item.setEnabled(False)
            for item in [self.Mu_Min_LE, self.Mu_Max_LE, self.Phi_Min_LE, self.Phi_Min_LE]:
                item.setText('')
        # //////////////////////////////////// Isotropic /////////////////////////////////////////
        if self.Direction_Dist_CB.currentIndex() == 1:
            print(self.angle + ' = openmc.stats.Isotropic()')
        # ///////////////////////////////// Monodirectional //////////////////////////////////////
        elif self.Direction_Dist_CB.currentIndex() == 2:
            self.Ref_UVW_CB.setEnabled(True)
            print(self.angle + ' = openmc.stats.Monodirectional(reference_uvw=' + self.Ref_UVW_CB.currentText() + ')')
        # //////////////////////////////////// UnitSphere ////////////////////////////////////////
        elif self.Direction_Dist_CB.currentIndex() == 3:
            self.Ref_UVW_CB.setEnabled(True)
            print(self.angle + ' = openmc.stats.UnitSphere(reference_uvw=' + self.Ref_UVW_CB.currentText() + ')')
        # //////////////////////////////////// PolarAzimuthal ////////////////////////////////////////
        if self.Direction_Dist_CB.currentIndex() == 4:
            if self.Mu_Dist_CB.currentIndex() == 0:                       # Mu Uniform
                print('mu_dist = openmc.stats.Uniform(' + self.Mu_Min_LE.text() + ',' + self.Mu_Max_LE.text() + ' )')
            elif self.Mu_Dist_CB.currentIndex() == 1:                     # Mu Discrete
                self.LE_to_List(self.Mu_Min_LE, self.Mu_Max_LE)
                print('mu_dist = openmc.stats.Discrete(' + self.Mu_Min_LE.text(), self.Mu_Max_LE.text() + ' )')
                if self.Error == 1:
                    Error += self.Error
                    self.Mu_Min_LE.setStyleSheet("QLineEdit{color:red}")
                    self.Mu_Max_LE.setStyleSheet("QLineEdit{color:red}")
                    self.plainTextEdit.setStyleSheet("QTextEdit{color:red}")
                    print('# Error: The lists in the line above must be the same length !')
            if self.Phi_Dist_CB.currentIndex() == 0:                      # Phi Uniform
                print('phi_dist = openmc.stats.Uniform(' + self.Phi_Min_LE.text() + ',' + self.Phi_Max_LE.text() + ' )')
            elif self.Phi_Dist_CB.currentIndex() == 1:                    # Phi Discrete
                self.LE_to_List(self.Phi_Min_LE, self.Phi_Max_LE)
                print('phi_dist = openmc.stats.Discrete(' + self.Phi_Min_LE.text(), self.Phi_Max_LE.text() +' )')
                if self.Error == 1:
                    Error += self.Error
                    self.Phi_Min_LE.setStyleSheet("QLineEdit{color:red}")
                    self.Phi_Max_LE.setStyleSheet("QLineEdit{color:red}")
                    self.plainTextEdit.setStyleSheet("QTextEdit{color:red}")
                    print('# Error: The lists in the line above must be the same length !')
            print(self.angle + ' = openmc.stats.PolarAzimuthal(mu_dist, phi_dist, reference_uvw=' + self.Ref_UVW_CB.currentText() + ')')
        if Error != 0:
            self.showDialog('Warning', 'The lists in the angle distribution must be the same length !')
            return

    def Add_Sources(self):
        self.Import_OpenMC()
        self.Find_string(self.v_1, "openmc.Settings")
        if self.Insert_Header:
            self.Find_string(self.plainTextEdit, "openmc.Settings")
            if self.Insert_Header:
                print('\n############################################################################### \n'
                      '#                 Exporting to OpenMC settings.xml file \n'
                      '###############################################################################')
                print("settings = openmc.Settings()\n")
            else:
                pass
        if self.Source_Geom_CB.currentIndex() in [1, 2, 3, 4, 5]:
            if self.Particle_CB.currentIndex() == 0:
                self.Particle = "'neutron'"
            elif self.Particle_CB.currentIndex() == 1:
                self.Particle = "'photon'"
            elif self.Particle_CB.currentIndex() == 2:
                self.Particle = "'electron'"
            else:
                self.Particle = "'positron'"
            if self.Only_Fissionable:
                self.Only_Fissionable_String = ', only_fissionable=True'
            else:
                self.Only_Fissionable_String = ''
            if self.Array_Sources_RB.isChecked():
                self.Num_of_Srcs_Label.show()
                self.Number_of_Sources.show()
                if float(self.Strength_LE.text()) >= 1.:
                    self.showDialog('Warning', 'Strength must be smaller than 1. !.')
            if self.Name_LE.text() not in self.Source_name_list:
                self.Source_Spatial_Distribution()
                if self.ErrorSP != 0:
                    return
                self.Source_Energy_Distribution()
                if self.ErrorEn != 0:
                    return
                self.Source_Angle_Distribution()
                if self.Energy_Dist_CB.currentIndex() == 0:
                    energy_str = ''
                else:
                    energy_str = self.energy + ', '
                if self.Direction_Dist_CB.currentIndex() == 0:
                    angle_str = ''
                else:
                    angle_str = self.angle + ', '
                print(str(self.Name_LE.text()) + ' = openmc.Source(' + self.spatial + ', ' + angle_str + energy_str + 'strength=' + str(
                        self.Strength_LE.text()) + ', particle=' + self.Particle + ')\n')
                self.Source_name_list.append(self.Name_LE.text())
                self.Source_id_list.append(self.Source_id)
            else:
                self.showDialog('Warning', 'Source name must not be repeated!')
                return
            document = self.v_1.toPlainText()
            lines = document.split('\n')
            strg = 'settings.source = ' + str(self.Source_name_list).replace("'", "")
            print(strg)
            '''for line in lines:
                if "settings.export_to_xml" in line: # or line == '':
                    lines.remove(line)
                    document = self.v_1.toPlainText().replace(line, '')'''
            self.v_1.clear()
            cursor = self.v_1.textCursor()
            cursor.insertText(document)
            #print ('settings.source = ' + str(self.Source_name_list).replace("'", ""))
        elif self.Source_Geom_CB.currentIndex() == 6:
            ############################### File based source (.h5) #################################
            print(str(self.Name_LE.text()) + " = openmc.Source(filename= '" + self.src_filename +"')")
        elif self.Source_Geom_CB.currentIndex() == 7:
            ############################### Read Surface source (.h5) #################################
            print(str(self.Name_LE.text()) + " = openmc.surf_source_read(filename= '" + self.src_filename + "')")
        else:
            pass
        self.Source_id += 1
        self.Energy_LE.clear()
        self.Proba_LE.clear()
        self.Mu_Min_LE.clear()
        self.Mu_Max_LE.clear()
        self.Phi_Min_LE.clear()
        self.Phi_Max_LE.clear()
        self.Change_Text_Color()
        self.Particle_CB.setCurrentIndex(0)
        self.Source_Geom_CB.setCurrentIndex(0)
        self.Energy_Dist_CB.setCurrentIndex(0)
        self.Direction_Dist_CB.setCurrentIndex(0)
        self.Mu_Dist_CB.setCurrentIndex(0)
        self.Phi_Dist_CB.setCurrentIndex(0)
        self.Insert_Header = False

    def Geometry_Key(self, text_window):
        self.Find_string(text_window, "openmc.Geometry")
        if self.current_line != "":
            Geo = self.current_line.split("=")[0]
            self.Geo = Geo.strip()
        else:
            self.showDialog('Warning', 'Geometry not yet created !.')
            self.Geo = "geometry"
        self.Cells_CB.setCurrentIndex(0)

    def Export_to_Main_Window(self):
        self.Find_string(self.v_1, "openmc.Settings")
        self.v_1.moveCursor(QTextCursor.End)
        if self.Insert_Header:
            self.Find_string(self.plainTextEdit, "openmc.Settings")
            if self.Insert_Header:
                print('\n############################################################################### \n'
                      '#                 Exporting to OpenMC settings.xml file \n'
                      '###############################################################################')
                print("settings = openmc.Settings()\n")
            else:
                pass
        self.Insert_Header = False
        string_to_find = "settings.export_to_xml()"
        self.Find_string(self.v_1, string_to_find)
        cursor = self.v_1.textCursor()
        self.plainTextEdit.moveCursor(QTextCursor.End)
        if self.Insert_Header:
            cursor.insertText(self.plainTextEdit.toPlainText())
            cursor.insertText('\n' + string_to_find + '\n')
        else:
            document = self.v_1.toPlainText()
            if self.tabWidget.currentIndex() == 0:
                print ('\n' + string_to_find)
                document = document.replace(string_to_find, self.plainTextEdit.toPlainText())
            else:
                lines = document.split('\n')
                for line in lines:
                    if "settings.source" in line: # or line == '':
                        lines.remove(line)
                        document = document.replace(line, self.plainTextEdit.toPlainText())

            self.v_1.clear()
            cursor = self.v_1.textCursor()
            cursor.insertText(document)
        self.text_inserted = True
        self.plainTextEdit.clear()

    def clear_text(self):
        self.plainTextEdit.clear()

    def normalOutputWritten(self,text):
        self.highlighter = Highlighter(self.plainTextEdit.document())
        cursor = self.plainTextEdit.textCursor()
        cursor.insertText(text)
