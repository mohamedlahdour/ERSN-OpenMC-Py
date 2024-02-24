#!/usr/bin/python3
# -*- coding: utf-8 -*-
from ast import Pass
import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5 import QtCore, QtGui, QtWidgets
import src.materials
import src.Mixture_pnnl
from src.PyEdit import TextEdit, NumberBar  
from src.syntax_py import Highlighter

class ExportMaterials(QWidget):
    from .func import resize_ui, showDialog, Exit
    def __init__(self, v_1, available_xs, mat, mat_id, parent=None):
        super(ExportMaterials, self).__init__(parent)
        uic.loadUi("src/ui/ExportMaterials.ui", self)  
        try:
            from openmc import __version__
            self.openmc_version = int(__version__.split('-')[0].replace('.', ''))
        except:
            self.showDialog('Warning', 'OpenMC not yet installed !')
            self.openmc_version = 0
 
        #sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        #sys.stderr = EmittingStream(textWritten=self.normalOutputWritten)
        #self.Liste1 = [self.Nucl_Modif_RB, self.Nucl_Add_RB, self.Nuclide_CB, self.Percent_Nuclide_LE,
        self.Liste1 = [ self.Nuclide_CB, self.Percent_Nuclide_LE,
                                      self.Percent_Nuc_Type_CB, self.label_4, self.label_5, self.label_6]
        #self.Liste2 = [self.Elm_Modif_RB, self.Elm_Add_RB, self.Element_CB, self.Percent_Element_LE,
        self.Liste2 = [ self.Element_CB, self.Percent_Element_LE,
                                      self.Percent_Ele_Type_CB, self.Enricht_LE, self.Enrichment_Target_CB, self.Enrichment_Type_CB,
                       self.label_51, self.label_52, self.label_53, self.label_54, self.label_55, self.label_56]
        for item in self.Liste1:
            item.setEnabled(False)
        for item in self.Liste2:
            item.setEnabled(False)
        self.Materials_Construct.setCurrentIndex(0)
        self.lineEdit_2.setValidator(QIntValidator())
        self.Mat_ID_LE.setValidator(QIntValidator())
        self.validator = QDoubleValidator(self)
        for LE in [self.lineEdit_3, self.lineEdit_4, self.lineEdit_5, self.lineEdit_6, self.lineEdit_7,
                   self.Percent_Nuclide_LE, self.Temp_LE, self.Density_LE, self.Percent_Element_LE, self.Enricht_LE]:
            LE.setValidator(self.validator)
        self.v_1 = v_1
        self._initButtons()
        
        # add new editor
        self.plainTextEdit = TextEdit()
        self.plainTextEdit.setWordWrapMode(QTextOption.NoWrap)
        self.numbers = NumberBar(self.plainTextEdit)
        layoutH = QHBoxLayout()
        #layoutH.setSpacing(1.5)
        layoutH.addWidget(self.numbers)
        layoutH.addWidget(self.plainTextEdit)
        self.EditorLayout.addLayout(layoutH, 0, 0)
        #self.cursor = self.plainTextEdit.textCursor()

        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)

        self.Temperature = '293.6'
        self.lineEdit_3.setText(self.Temperature)
        self.lineEdit_7.setText(None)
        self.mat = None
        self.Mat_Name = None
        self.available_xs = available_xs
        self.Neutron_XS_List = self.available_xs[0]
        self.TSL_XS_List = self.available_xs[1]
        self.Photon_XS_List = self.available_xs[2]

        self.materials_name_list = mat
        self.materials_id_list = mat_id
        self.materials_name_sub_list = []
        self.materials_id_sub_list = []
        self.Mat_List_to_Modify = []
        self.Increment_Mat_Id()
        self.material_suffix = 'Mat'
        self.lineEdit_2.setText(str(self.material_id))
        self.text_inserted = False
        self.Enrichment = False
        self.nuclide_added = False
        self.element_added = False
        if self.add_id_CB.isChecked():
            self.lineEdit.setText(self.material_suffix + str(self.lineEdit_2.text()))
        else:
            self.lineEdit.setText(self.material_suffix)
        self.Nuclide_to_find_percent = None
        self.Percent_Nuc_Type = 'ao'
        self.Element_to_find_percent = None
        self.Percent_Elm_Type = 'ao'
        self.Element_Enrichment = ''
        self.Element_Enrichment_Target = None
        self.Element_Enrichment_Type = 'wo'
        self.Mat_Nuclide_List = {}
        self.Mat_Nuclide_Add_List = {}
        self.Mat_Nuclide_Percent_List = {}
        self.Mat_Nuclide_Percent_Type_List = {}
        self.Mat_Element_List = {}
        self.Mat_Element_Percent_List = {}
        self.Mat_Element_Percent_Type_List = {}
        self.Materials_In_Model = {}
        self.Elements_In_Material = {}
        self.Nuclides_In_Material = {}
        # self.Materials_In_Model[self.Mat_Name][self.Elements_In_Material]
        # self.Materials_In_Model[self.Mat_Name][self.Elements_In_Material][self.Element_Percent]
        # self.Materials_In_Model[self.Mat_Name][self.Elements_In_Material][self.Element_Percent_Type]
        # self.Materials_In_Model[self.Mat_Name][self.Elements_In_Material][self.Element_Enrichment]
        # self.Materials_In_Model[self.Mat_Name][self.Elements_In_Material][self.Element_Enrichment_Type]
        # self.Materials_In_Model[self.Mat_Name][self.Elements_In_Material][self.Element_Enrichment_Target]

        #self.Materials_In_Model = {'Mat1': {'id': 1, 'name': 'Mat1', 'density': 1.1, 'temperature': 300,
        #                                    'Elements': {'Elm1': {'symbol': 'He', 'fraction': 0.1, 'fraction_type': 'wo',
        #                                                          'enrichment': 30, 'enrichment_target': 'He4', 'enrichment_type': 'wo' },
        #                                                 'Elm2': {'symbol': 'C', 'fraction': 0.2, 'fraction_type': 'ao',
        #                                                          'enrichment': 40, 'enrichment_target': 'C14', 'enrichment_type': 'ao' } }   },
        #                           'Mat2': {'id': 2, 'name': 'Mat2', 'density': 1.2, 'temperature': 400,
        #                                    'Elements': {'Elm1': {'symbol': 'Be', 'fraction': 0.3, 'fraction_type': 'wo',
        #                                                          'enrichment': 30, 'enrichment_target': 'Be8', 'enrichment_type': 'wo' },
        #                                                 'Elm2': {'symbol': 'Co', 'fraction': 0.4, 'fraction_type': 'wo',
        #                                                          'enrichment': 50, 'enrichment_target': 'Co60', 'enrichment_type': 'wo' } } } }

        for i in range(len(src.materials.THERMAL_SCATTERING)):
            self.comboBox_2.addItem(src.materials.THERMAL_SCATTERING[i])
        for key in src.materials.NATURAL_ABUNDANCE.keys():
            self.comboBox_3.addItem(key)
        for value in src.materials.ELEMENT_SYMBOL.values():
            self.comboBox_5.addItem(value)
        for i in range(len(src.materials.THERMAL_SCATTERING)):
            self.SAB_CB.addItem(src.materials.THERMAL_SCATTERING[i])

        self.lines = self.v_1.toPlainText().split('\n')
        self.Mat_List_CB.clear()
        self.Mat_List_CB.addItem('Select Material')
        self.Mat_List_CB.addItems(sorted(self.materials_name_list))
        self.Mat_To_Suppress_List_CB.clear()
        self.Mat_To_Suppress_List_CB.addItem('Select Material')
        self.Mat_To_Suppress_List_CB.addItems(sorted(self.materials_name_list))
        self.Mat_List_CB.setCurrentIndex(0)
        self.Mat_ID_LE.setText('')
        self.Temp_LE.setText('')
        self.Nuclide_CB.clear()
        self.Nuclide_Supp_List_CB.clear()
        self.Element_Supp_List_CB.clear()
        self.Mixture_CB.hide()
        self.Fraction_Type_CB.hide()
        self.label_10.hide()
        self.Mixture_CB.addItem('Select Mixture')
        self.Extract_Isotopes_List()
        for value in src.Mixture_pnnl.Mixtures.values():
            self.Mixture_CB.addItem(value[0])
        self.Mixture_CB.setToolTip("Data are derived from Compendium of Material Composition Data for Radiation Transport Modeling, Revision 1, "
                                   "PNNL-15870 Rev. 1,  March 2001")
        self.Enrichment_Target_CB.setToolTip("There is a special procedure, in openMC version +0.14, for enrichment of U235 in U. To invoke it, "
                                             "the arguments 'enrichment_target'and 'enrichment_type' should be omitted. Provide a value only for 'enrichment' in weight percent.")
        self.Enrichment_Type_CB.setToolTip("There is a special procedure, in openMC version +0.14, for enrichment of U235 in U. To invoke it, "
                                             "the arguments 'enrichment_target'and 'enrichment_type' should be omitted. Provide a value only for 'enrichment' in weight percent.")
        self.comboBox_7.setToolTip("There is a special procedure, in openMC version +0.14, for enrichment of U235 in U. To invoke it, "
                                             "the arguments 'enrichment_target'and 'enrichment_type' should be omitted. Provide a value only for 'enrichment' in weight percent.")
        self.comboBox_8.setToolTip("There is a special procedure, in openMC version +0.14, for enrichment of U235 in U. To invoke it, "
                                             "the arguments 'enrichment_target'and 'enrichment_type' should be omitted. Provide a value only for 'enrichment' in weight percent.")

        # to show window at the middle of the screen and resize it to the screen size
        self.resize_ui()

    def _initButtons(self):
        self.pushButton.clicked.connect(self.Add_Material)
        self.pushButton_2.clicked.connect(self.Add_Nuclide)
        self.pushButton_3.clicked.connect(self.Add_Element)
        self.Check_Mixture_CB.stateChanged.connect(self.Fill_Mixture_List)
        self.Mixture_CB.currentIndexChanged.connect(self.Add_Mixture)
        self.Export_PB.clicked.connect(self.Export_to_Main_Window)
        self.pushButton_5.clicked.connect(self.Clear_Output)
        self.pushButton_6.clicked.connect(self.Exit)
        self.lineEdit.textChanged.connect(self.sync_name1)
        self.add_id_CB.stateChanged.connect(self.sync_name)
        self.lineEdit_2.textChanged.connect(self.sync_id)
        self.Materials_Construct.currentChanged.connect(self.reset_Modify_Data)
        self.Materials_Construct.currentChanged.connect(self.reset_Modify_Supp_Data)
        self.Materials_Construct.currentChanged.connect(self.Update_Mat_List)
        self.Mat_List_CB.currentIndexChanged.connect(self.Read_Mat_Data)
        self.Nucl_Modif_RB.toggled.connect(self.Update_Nuclides_CB)
        self.Nucl_Add_RB.toggled.connect(self.Update_Nuclides_CB)
        self.Nuclide_CB.currentIndexChanged.connect(self.Update_Nuclide_Data)
        self.Elm_Modif_RB.toggled.connect(self.Update_Elements_CB)
        self.Elm_Add_RB.toggled.connect(self.Update_Elements_CB)
        self.Element_CB.currentIndexChanged.connect(self.Update_Element_Data)
        self.Element_CB.currentIndexChanged.connect(self.Update_Enrich_Target_List)
        self.Enricht_LE.textChanged.connect(self.Update_Enrich_Target_CB)
        self.comboBox_5.currentIndexChanged.connect(self.Reset_Enrich_List)
        self.lineEdit_7.textChanged.connect(self.Update_Enrich_List)
        self.Mat_To_Suppress_List_CB.currentIndexChanged.connect(self.Read_Mat_Supp_Data)
        self.Modify_Mat_PB.clicked.connect(self.Modify_Material)
        self.Suppress_Component_PB.clicked.connect(self.Suppress_Component)

    def Increment_Mat_Id(self):
        if self.materials_id_list: #len(self.materials_id_list) > 0:
            n = int(self.materials_id_list[-1]) + 1
            while True:
                if n not in self.materials_id_list :
                    self.material_id = n
                    break
                else:
                    n += 1
        else:
            self.material_id = 1

    def Reset_Enrich_List(self):
        self.lineEdit_7.clear()
        self.comboBox_7.clear()
        self.comboBox_8.setCurrentIndex(0)

    def Update_Enrich_List(self):         # in add element to material
        self.comboBox_7.clear()
        if self.comboBox_5.currentIndex() == 0 or not self.lineEdit_7.text():
            self.comboBox_7.setCurrentIndex(0)
        else:
            self.comboBox_7.addItem('Select Isotope')
            for key in src.materials.NATURAL_ABUNDANCE.keys():
                element = ''.join(i for i in key if not i.isdigit())
                if self.comboBox_5.currentText() == element:
                    self.comboBox_7.addItem(key)

    def Extract_Isotopes_List(self):           # in modify material
        from collections import defaultdict
        self.Isotopes_In_Elements = defaultdict(list)
        for key in src.materials.NATURAL_ABUNDANCE.keys():
            if key != 'None':
                element = ''.join(i for i in key if not i.isdigit())
                self.Isotopes_In_Elements[element] += [key]

    def Update_Enrich_Target_CB(self):           # in modify material
        index = self.Enrichment_Target_CB.currentIndex()
        if self.Materials_Construct.currentIndex() == 1:
            if self.Enricht_LE.text() == '':
                self.Enrichment_Target_CB.clear()
            else:
                self.Enrichment_Target_CB.clear()
                element = self.Element_CB.currentText()
                self.Enrichment_Target_CB.addItems(self.Isotopes_In_Elements[element.replace("'", "")])
                self.Enrichment_Target_CB.setCurrentIndex(index)
        self.Enrichment_Target_CB.setCurrentIndex(0)

    def Update_Enrich_Target_List(self):           # in modify material
        if self.Materials_Construct.currentIndex() == 1:
            if self.Element_CB.currentIndex() == 0:
                self.Enrichment_Target_CB.clear()
                self.Enricht_LE.setText('')
            elif self.Element_CB.currentIndex() >= 1:
                self.Enrichment_Target_CB.clear()
                if self.Elm_Modif_RB.isChecked():
                    element = self.Element_CB.currentText()
                    enrichment = self.Elements_In_Material[element]['Enrichment']
                    if enrichment:
                        self.Enricht_LE.setText(enrichment)
                        self.Enrichment_Type_CB.setCurrentIndex(self.Enrichment_Type_CB.findText(self.Elements_In_Material[element]['Enrichment_type'].replace("'", ''), QtCore.Qt.MatchFixedString))
                        self.Enrichment_Target_CB.addItems(self.Isotopes_In_Elements[element.replace("'", "")])
                        target_item = self.Elements_In_Material[element]['Enrichment_target'].replace("'", "")
                        index = self.Enrichment_Target_CB.findText(target_item, QtCore.Qt.MatchFixedString)
                        self.Enrichment_Target_CB.setCurrentIndex(index)
                if self.Elm_Add_RB.isChecked():
                    if self.Enricht_LE.text():
                        pass

    def Update_Mat_List(self):
        self.Mat_List_CB.clear()
        self.Nuclide_CB.setCurrentIndex(0)
        self.Nuclide_Supp_List_CB.setCurrentIndex(0)
        self.Element_Supp_List_CB.setCurrentIndex(0)
        self.Mat_List_CB.addItem('Select Material')
        if self.Mat_List_CB.currentIndex() == 0:
            self.Mat_ID_LE.setText('')
            self.Nuclide_CB.clear()
            self.Nuclide_Supp_List_CB.clear()
            self.Element_Supp_List_CB.clear()
            self.Mat_To_Suppress_List_CB.clear()
            self.Mat_To_Suppress_List_CB.addItem('Select Material')
        if self.materials_name_list:
            self.Mat_List_CB.addItems(sorted(self.materials_name_list))
            self.Mat_To_Suppress_List_CB.addItems(sorted(self.materials_name_list))
        self.lines = self.v_1.toPlainText().split('\n')
        self.Increment_Mat_Id()
        self.lineEdit_2.setText(str(self.material_id))

    def Check_If_Material_Modified(self, Mat_Name):
        self.Material_Modified = False
        lines = self.plainTextEdit.toPlainText().split('\n')
        for line in lines:
            if str(Mat_Name) in line.replace(' ', '').split('=') and 'openmc.Materials' not in line:
                self.Material_Modified = True
                break
            else:
                self.Material_Modified = False
        if self.Material_Modified:
            self.lines = lines
        else:
            self.lines = self.v_1.toPlainText().split('\n')

    def Read_Mat_Data(self):
        if self.Materials_Construct.currentIndex() == 1 and self.Mat_List_CB.currentIndex() >= 1:
            self.lines = self.v_1.toPlainText().split('\n')
            self.Value_To_Find = None
            self.Nuclide_CB.clear()
            if self.materials_name_list:
                if self.Mat_List_CB.currentIndex() >= 1:
                    Mat_Name = self.Mat_List_CB.currentText()  
                    Mat_Id = self.materials_id_list[self.materials_name_list.index(Mat_Name)]   
                    self.Mat_Name = Mat_Name
                    self.Mat_Id = Mat_Id
                    self.Mat_ID_LE.setText(str(Mat_Id))
                    self.Check_If_Material_Modified(Mat_Name)
                    self.find_Temperature(self.lines, Mat_Name, 'temperature')
                    if self.Value_To_Find:
                        self.Temperature = self.Value_To_Find
                        self.Temp_LE.setText(self.Value_To_Find)
                    else:
                        self.Temp_LE.setText('')
                    self.Value_To_Find = None

                    self.find_Density(self.lines, Mat_Name, 'set_density')
                    if self.Value_To_Find:
                        self.Density_Unit_CB.setCurrentIndex(self.Density_Unit_CB.findText(self.Density_Unit.replace("'", ''), QtCore.Qt.MatchFixedString))
                        self.Density_LE.setText(self.Value_To_Find)
                        self.Mat_Density = self.Value_To_Find
                    else:
                        self.Density_Unit_CB.setCurrentIndex(0)
                        self.Density_LE.setText('')
                    self.Value_To_Find = None

                    self.find_SAB(self.lines, Mat_Name, 'add_s_alpha_beta')
                    if self.Value_To_Find:
                        self.SAB_CB.setCurrentIndex(self.SAB_CB.findText(self.Value_To_Find.replace("'", ''), QtCore.Qt.MatchFixedString))
                        self.SAB = self.Value_To_Find
                    else:
                        self.SAB_CB.setCurrentIndex(0)
                        self.SAB = ''
                    self.Value_To_Find = None
                    self.Store_Materials_Info(Mat_Name, Mat_Id)
                    self.find_Nuclides(self.lines, Mat_Name, 'add_nuclide')
                    self.find_Elements(self.lines, Mat_Name, 'add_element')
                    self.Update_Nuclides_CB()
                    self.Update_Elements_CB()
                    self.Update_Element_Data()
                    if self.Mat_Element_List[self.Mat_Name]:
                        if not self.Mat_Nuclide_List[self.Mat_Name]:
                            self.Elm_Modif_RB.setChecked(True)
                    elif self.Mat_Nuclide_List[self.Mat_Name]:
                        if not self.Mat_Element_List[self.Mat_Name]:
                            self.Nucl_Modif_RB.setChecked(True)
                else:
                    self.reset_Modify_Data()
        if self.Mat_List_CB.currentIndex() != 0:
            for item in self.Liste1:
                item.setEnabled(True)
            for item in self.Liste2:
                item.setEnabled(True)
        else:
            for item in self.Liste1:
                item.setEnabled(False)
            for item in self.Liste2:
                item.setEnabled(False)

    def Clear_plainTextEdit(self, Mat):
        document = self.plainTextEdit.toPlainText()
        self.plainTextEdit.clear()
        lines = document.split('\n')
        document = ''
        for line in lines:
            if Mat not in line and line != '':
                document += line + ('\n')
        self.plainTextEdit.clear()
        self.plainTextEdit.insertPlainText(document)

    def Modify_Material(self):
        #self.Mat_Nuclide_Add_List.setdefault(self.Mat_Name, [])
        self.Mat_Nuclide_Add_List[self.Mat_Name] = []
        self.Mat_List_to_Modify.append(self.Mat_Name)
        if self.Mat_List_CB.currentIndex() >= 1:
            if self.Nucl_Modif_RB.isChecked():    # modify existing nuclide
                self.Clear_plainTextEdit(self.Mat_Name)
                if self.Temp_LE.text():
                    print('\n' + self.Mat_Name, "= openmc.Material(material_id=" + str(self.Mat_ID_LE.text()) +
                        ", name='" + self.Mat_List_CB.currentText() + "',", "temperature=", str(self.Temp_LE.text()), ')')
                else:
                    print('\n' + self.Mat_Name, "= openmc.Material(material_id=" + str(self.Mat_ID_LE.text()) +
                        ", name='" + self.Mat_List_CB.currentText() + "'", ')')
                print(self.Mat_Name + '.set_density(' + "'" + self.Density_Unit_CB.currentText() + "',",
                      self.Density_LE.text() + ")")
                if self.Mat_Nuclide_List[self.Mat_Name]:
                    self.modify_nuclides()

            elif self.Elm_Modif_RB.isChecked():  # modify existing element
                self.Clear_plainTextEdit(self.Mat_Name)
                if self.Temp_LE.text():
                    print('\n' + self.Mat_Name, "= openmc.Material(material_id=" + str(self.Mat_ID_LE.text()) +
                        ", name='" + self.Mat_List_CB.currentText() + "',", "temperature=", str(self.Temp_LE.text()) + ')')
                else:
                    print('\n' + self.Mat_Name, "= openmc.Material(material_id=" + str(self.Mat_ID_LE.text()) +
                        ", name='" + self.Mat_List_CB.currentText() + "'" + ')')
                print(self.Mat_Name + '.set_density(' + "'" + self.Density_Unit_CB.currentText() + "',",
                      self.Density_LE.text() + ")")
                if self.Mat_Element_List[self.Mat_Name]:
                    self.modify_elements()

            elif self.Elm_Add_RB.isChecked():              # add new element to material
                if not self.element_added and not self.nuclide_added:
                    document = self.v_1.toPlainText()
                    lines = document.split('\n')
                    self.plainTextEdit.clear()
                    document = '\n'
                    self.density_card = ''
                    for line in lines:
                        if self.Mat_Name in line:
                            '''if 'set_density' in line:
                                self.density_card = line'''
                            if 'openmc.Materials' not in line and 'set_density' not in line and 'add_s_alpha_beta' not in line:
                                document += line + '\n'
                    self.plainTextEdit.insertPlainText(document)
                else:
                    document = self.plainTextEdit.toPlainText()
                    lines = document.split('\n')
                    self.plainTextEdit.clear()
                    document = '\n'
                    for line in lines:
                        if self.Mat_Name in line:
                            if 'set_density' not in line and 'add_s_alpha_beta' not in line:
                                document += line + '\n'
                    self.plainTextEdit.insertPlainText(document)
                self.density_card = self.Mat_Name + '.set_density(' + "'" + self.Density_Unit_CB.currentText() + "'," + self.Density_LE.text() + ")"
                element = "'" + self.Element_CB.currentText() + "'"
                if element in self.Mat_Element_List[self.Mat_Name]:
                    self.showDialog('Warning', 'Element ' + element + 'already in material! Choose another element or modify the existing one!')
                    return
                if self.Element_CB.currentIndex() != 0 and self.Percent_Element_LE.text() == "":
                    self.showDialog('Warning', 'No element fraction entered !')
                    return
                else:
                    fraction = self.Percent_Element_LE.text()
                fraction_type = self.Percent_Ele_Type_CB.currentText()
                if self.Enricht_LE.text():
                    enrichment = self.Enricht_LE.text()
                    #if self.Enrichment_Target_CB.currentIndex() >= 0:    # not necessary
                    if element == 'U' and self.openmc_version > 141:
                        enrichment_type = 'wo'
                        enrichment_target = 'U235'
                        #if self.Element_CB.currentIndex() != 0:
                        print(self.Mat_Name + ".add_element(" + element + ", " + fraction + ", percent_type=" + "'" + fraction_type +
                            "', enrichment=" + enrichment + "') ")
                    else: 
                        enrichment_target = self.Enrichment_Target_CB.currentText()
                        enrichment_type = self.Enrichment_Type_CB.currentText()
                        
                        #if self.Element_CB.currentIndex() != 0:
                        print(self.Mat_Name + ".add_element(" + element + ", " + fraction + ", percent_type=" + "'" + fraction_type +
                            "', enrichment=" + enrichment + ", enrichment_target='" + enrichment_target +
                            "', enrichment_type='" + enrichment_type + "') ")
                    enrichment_target_list = self.Isotopes_In_Elements[element.replace("'", "")]
                else:
                    enrichment = ''
                    enrichment_target = ''
                    enrichment_type = ''
                    enrichment_target_list = []
                    if self.Element_CB.currentIndex() != 0:
                        print(self.Mat_Name + ".add_element(" + element + ", " + fraction + ", percent_type=" + "'" + fraction_type + "')")
                self.element_added = True
                print(self.density_card )
                if self.Element_CB.currentIndex() != 0:
                    self.Mat_Element_List[self.Mat_Name].append(element)
                    self.Mat_Element_Percent_List[self.Mat_Name].append(fraction)
                    self.Mat_Element_Percent_Type_List[self.Mat_Name].append(fraction_type)
                    self.Store_Material_Elements_Info(element, fraction, fraction_type, enrichment, enrichment_target_list, enrichment_target, enrichment_type)
            elif self.Nucl_Add_RB.isChecked():              # add new nuclide to material
                if not self.nuclide_added and not self.element_added:
                    document = self.v_1.toPlainText()
                    lines = document.split('\n')
                    self.plainTextEdit.clear()
                    document = '\n'
                    self.density_card = ''
                    for line in lines:
                        if self.Mat_Name in line:
                            '''if 'set_density' in line:
                                self.density_card = line'''
                            if 'openmc.Materials' not in line and 'set_density' not in line and 'add_s_alpha_beta' not in line:
                                document += line + '\n'
                    self.plainTextEdit.insertPlainText(document)
                else:
                    document = self.plainTextEdit.toPlainText()
                    lines = document.split('\n')
                    self.plainTextEdit.clear()
                    document = '\n'
                    for line in lines:
                        if self.Mat_Name in line:
                            if 'set_density' not in line and 'add_s_alpha_beta' not in line:
                                document += line + '\n'
                    self.plainTextEdit.insertPlainText(document)
                self.density_card = self.Mat_Name + '.set_density(' + "'" + self.Density_Unit_CB.currentText() + "'," + self.Density_LE.text() + ")"
                nuclide = "'" + self.Nuclide_CB.currentText() + "'"
                if nuclide in self.Mat_Nuclide_List[self.Mat_Name]:
                    self.showDialog('Warning', 'Nuclide ' + nuclide + 'already in material! Choose another nuclide or modify the existing one!')
                    return
                if self.Nuclide_CB.currentIndex() != 0 and self.Percent_Nuclide_LE.text() == "":
                    self.showDialog('Warning', 'No nuclide fraction entered !')
                    return
                else:
                    fraction = self.Percent_Nuclide_LE.text()
                fraction_type = self.Percent_Nuc_Type_CB.currentText()
                if self.Nuclide_CB.currentIndex() != 0:
                    print(self.Mat_Name + ".add_nuclide(" + nuclide + ", " + fraction + ", percent_type=" + "'" + fraction_type + "')")
                self.nuclide_added = True
                print(self.density_card )
                if self.Nuclide_CB.currentIndex() != 0:
                    self.Mat_Nuclide_List[self.Mat_Name].append(nuclide)
                    self.Mat_Nuclide_Percent_List[self.Mat_Name].append(fraction)
                    self.Mat_Nuclide_Percent_Type_List[self.Mat_Name].append(fraction_type)
                    self.Store_Material_Nuclides_Info(nuclide, fraction, fraction_type)

            if self.SAB_CB.currentText() != 'None':
                print(self.Mat_Name + ".add_s_alpha_beta(" + "'" + self.SAB_CB.currentText() + "')")
        else:
            return

        idx = self.Mat_List_CB.currentIndex()
        if self.Elm_Add_RB.isChecked() or self.Nucl_Add_RB.isChecked():
            self.Mat_List_CB.setCurrentIndex(idx)
        else:
            self.Mat_List_CB.setCurrentIndex(0)
            self.Mat_ID_LE.clear()
            self.Density_LE.clear()
            self.Density_Unit_CB.setCurrentIndex(0)
            self.SAB_CB.setCurrentIndex(0)

        self.Percent_Element_LE.clear()
        self.Percent_Nuclide_LE.clear()
        self.Percent_Ele_Type_CB.setCurrentIndex(1)
        self.Percent_Nuc_Type_CB.setCurrentIndex(0)
        self.Enricht_LE.clear()
        self.Enrichment_Target_CB.clear()
        self.Enrichment_Type_CB.setCurrentIndex(1)
        self.Element_CB.setCurrentIndex(0)
        self.Nuclide_CB.setCurrentIndex(0)

    def modify_nuclides(self):
        for nuclide in self.Mat_Nuclide_List[self.Mat_Name]:
            if self.Nuclide_CB.currentText() == nuclide:
                if self.Percent_Nuclide_LE.text() == "":
                    self.showDialog('Warning', 'No nuclide fraction entered !')
                    return
                else:
                    fraction = self.Percent_Nuclide_LE.text()
                    fraction_type = self.Percent_Nuc_Type_CB.currentText()
            else:
                fraction = self.Nuclides_In_Material[nuclide]['Fraction']
                fraction_type = self.Nuclides_In_Material[nuclide]['Fraction_type']
            print(self.Mat_Name + ".add_nuclide(" + nuclide + ", " + fraction + ", percent_type=" + "'" + fraction_type + "')")
        if self.Mat_Element_List[self.Mat_Name]:
            for element in self.Mat_Element_List[self.Mat_Name]:
                self.paste_not_modified_elements(element)

        self.Store_Material_Nuclides_Info(nuclide, fraction, fraction_type)
        #self.modify_elements()

    def modify_elements(self):
        for element in self.Mat_Element_List[self.Mat_Name]:
            if self.Element_CB.currentText() == element:
                if self.Percent_Element_LE.text() == "":
                    self.showDialog('Warning', 'No element fraction entered !')
                    return
                else:
                    fraction = self.Percent_Element_LE.text()
                    fraction_type = self.Percent_Ele_Type_CB.currentText()
                    if self.Enricht_LE.text() != '':
                        enrichment = self.Enricht_LE.text()
                        if element == 'U' and self.openmc_version >= 141:
                            enrichment_target = 'U235'
                            enrichment_type = 'wo'
                            print(self.Mat_Name + ".add_element(" + element + ", " + fraction + ", percent_type=" + "'" + fraction_type +
                                "', enrichment=" + enrichment + "') ")
                        else:
                            enrichment_type = self.Enrichment_Type_CB.currentText()
                            enrichment_target = self.Enrichment_Target_CB.currentText()
                            print(self.Mat_Name + ".add_element(" + element + ", " + fraction + ", percent_type=" + "'" + fraction_type +
                                "', enrichment=" + enrichment + ", enrichment_target='" + enrichment_target +
                                "', enrichment_type='" + enrichment_type + "') ")
                        enrichment_target_list = self.Isotopes_In_Elements[element.replace("'", "")]
                    else:
                        enrichment = ''
                        enrichment_target = ''
                        enrichment_type = ''
                        enrichment_target_list = []
                        print(self.Mat_Name + ".add_element(" + element + ", " + fraction + ", percent_type=" + "'" + fraction_type + "')")
                    self.Elements_In_Material[element]['Fraction'] = fraction
                    self.Elements_In_Material[element]['Fraction_type'] = fraction_type
                    self.Elements_In_Material[element]['Enrichment'] = enrichment
                    self.Elements_In_Material[element]['Enrichment_target'] = enrichment_target
                    self.Elements_In_Material[element]['Enrichment_type'] = enrichment_type

                self.Enricht_LE.setText('')
                self.Store_Material_Elements_Info(element, fraction, fraction_type, enrichment, enrichment_target_list,
                                                  enrichment_target, enrichment_type)
            else:
                self.paste_not_modified_elements(element)
        if self.Mat_Nuclide_List[self.Mat_Name]:
            for nuclide in self.Mat_Nuclide_List[self.Mat_Name]:
                self.paste_not_modified_nuclides(nuclide)
        
    def paste_not_modified_elements(self, element):
        fraction = self.Elements_In_Material[element]['Fraction']
        fraction_type = self.Elements_In_Material[element]['Fraction_type']
        if self.Elements_In_Material[element]['Enrichment']:
            enrichment = self.Elements_In_Material[element]['Enrichment']
            enrichment_target_list = self.Isotopes_In_Elements[element.replace("'", "")]
            if element == 'U' and self.openmc_version >= 141:
                enrichment_target = 'U235'
                enrichment_type = 'wo'
                print(
                    self.Mat_Name + ".add_element(" + element + ", " + fraction + ", percent_type=" + "'" + fraction_type +
                    "', enrichment=" + enrichment + "') ")
            else:    
                enrichment_target = self.Elements_In_Material[element]['Enrichment_target'].replace("'", "")
                enrichment_type = self.Elements_In_Material[element]['Enrichment_type'].replace("'", "")
                print(
                    self.Mat_Name + ".add_element(" + element + ", " + fraction + ", percent_type=" + "'" + fraction_type +
                    "', enrichment=" + enrichment + ", enrichment_target='" + enrichment_target +
                    "', enrichment_type='" + enrichment_type + "') ")
        else:
            enrichment = ''
            enrichment_target = ''
            enrichment_type = ''
            enrichment_target_list = []
            print(self.Mat_Name + ".add_element(" + element + ", " + fraction + ", percent_type=" + "'" + fraction_type + "')")

        self.Store_Material_Elements_Info(element, fraction, fraction_type, enrichment, enrichment_target_list,
                                      enrichment_target, enrichment_type)

    def paste_not_modified_nuclides(self, nuclide):
        fraction = self.Nuclides_In_Material[nuclide]['Fraction']
        fraction_type = self.Nuclides_In_Material[nuclide]['Fraction_type']
        print(self.Mat_Name + ".add_nuclide(" + nuclide + ", " + fraction + ", percent_type=" + "'" + fraction_type + "')")
        self.Store_Material_Nuclides_Info(nuclide, fraction, fraction_type)

    def Suppress_Component(self):
        self.lines = self.v_1.toPlainText().split('\n')
        if self.Mat_To_Suppress_List_CB.currentIndex() == 0:
            pass
        else:
            if self.Nuclide_Supp_List_CB.currentIndex() == 0 and self.Element_Supp_List_CB.currentIndex() == 0:
                self.Remove_Material()
            elif self.Nuclide_Supp_List_CB.currentIndex() != 0 and self.Element_Supp_List_CB.currentIndex() != 0:
                self.Remove_Element()
                self.Remove_Nuclide()
            elif self.Nuclide_Supp_List_CB.currentIndex() != 0:
                self.Remove_Nuclide()
            elif self.Element_Supp_List_CB.currentIndex() != 0:
                self.Remove_Element()

    def Remove_Material(self):
        qm = QMessageBox
        ret = qm.question(self, 'Warning', 'Do you really want to suppress ' + self.Mat_Name + ' ?', qm.Yes | qm.No)
        if ret == qm.Yes:
            if self.plainTextEdit:
                lines = self.plainTextEdit.toPlainText().split('\n')
                lines[:] = [item for item in lines if self.Mat_Name not in item]
                self.plainTextEdit.clear()
                for line in lines:
                    if line:
                        self.plainTextEdit.insertPlainText(line + '\n')
            #self.materials_name_list[:] = [item for item in self.materials_name_list if item != self.Mat_Name]
            #self.materials_id_list[:] = [id for id in self.materials_id_list if id != self.Mat_Id]
            self.materials_name_list.remove(self.Mat_Name)
            self.materials_id_list.remove(self.Mat_Id)
            if self.Mat_Element_List[self.Mat_Name]:
                del self.Mat_Element_List[self.Mat_Name]
            if self.Mat_Nuclide_List[self.Mat_Name]:
                del self.Mat_Nuclide_List[self.Mat_Name]

            #del self.Materials_In_Model[self.Mat_Name]
            self.showDialog('Warning', self.Mat_Name + ' has been suppressed')
            self.Update_Mat_List()
            self.lines[:] = [item for item in self.lines if self.Mat_Name not in item]
            self.v_1.clear()
            for line in self.lines:
                if line:
                    if 'openmc.Material' in line:
                        self.v_1.insertPlainText('\n')
                    self.v_1.insertPlainText(line + '\n')
            self.v_1.insertPlainText('\nmaterials = openmc.Materials(' + '[' + ', '.join(self.materials_name_list) + ']' + ')')
            '''if self.plainTextEdit:
                self.Export_to_Main_Window()'''
        elif ret == qm.No:
            pass

    def Remove_Element(self):
        Index = self.Element_Supp_List_CB.currentIndex()
        Element_To_Suppress = self.Mat_Element_List[self.Mat_Name][Index - 1]
        qm = QMessageBox
        ret = qm.question(self, 'Warning', 'Do you really want to suppress ' + Element_To_Suppress + ' from ' + self.Mat_Name + ' ?', qm.Yes | qm.No)
        lines = self.v_1.toPlainText().split('\n')
        if ret == qm.Yes:
            #self.Mat_Element_List[self.Mat_Name][:] = [item for item in self.Mat_Element_List[self.Mat_Name] if item != Element_To_Suppress]
            self.Mat_Element_List[self.Mat_Name].remove(Element_To_Suppress)
            #self.Mat_Element_Percent_List[self.Mat_Name][:] = [item for item in self.Mat_Element_Percent_List[self.Mat_Name] if item != self.Mat_Element_Percent_List[self.Mat_Name][Index - 1]]
            self.Mat_Element_Percent_List[self.Mat_Name].remove(self.Mat_Element_Percent_List[self.Mat_Name][Index - 1])
            #self.Mat_Element_Percent_Type_List[self.Mat_Name].pop(Index - 1)
            self.Mat_Element_Percent_Type_List[self.Mat_Name].remove(self.Mat_Element_Percent_Type_List[self.Mat_Name][Index - 1])
            self.showDialog('Warning', Element_To_Suppress + ' has been suppressed')
            for line in lines:
                if self.Mat_Name in line and Element_To_Suppress in line:
                    lines.remove(line)
            self.v_1.clear()
            for line in lines:
                self.v_1.insertPlainText(line + '\n')
            #self.plainTextEdit.clear()
        elif ret == qm.No:
            pass
        self.Update_Elements_Supp_CB()

    def Remove_Nuclide(self):
        Index = self.Nuclide_Supp_List_CB.currentIndex()
        Nuclide_To_Suppress = self.Mat_Nuclide_List[self.Mat_Name][Index - 1]
        qm = QMessageBox
        ret = qm.question(self, 'Warning', 'Do you really want to suppress ' + Nuclide_To_Suppress + ' from ' + self.Mat_Name + ' ?', qm.Yes | qm.No)
        lines = self.v_1.toPlainText().split('\n')
        if ret == qm.Yes:
            self.Mat_Nuclide_List[self.Mat_Name][:] = [item for item in self.Mat_Nuclide_List[self.Mat_Name] if item != Nuclide_To_Suppress]
            self.Mat_Nuclide_Percent_List[self.Mat_Name].pop(Index - 1)
            self.Mat_Nuclide_Percent_Type_List[self.Mat_Name].pop(Index - 1)
            self.showDialog('Warning', Nuclide_To_Suppress + ' has been suppressed')
            for line in lines:
                if self.Mat_Name in line and Nuclide_To_Suppress in line:
                    lines.remove(line)
                    break
            self.v_1.clear()
            for line in lines:
                self.v_1.insertPlainText(line + '\n')
            #self.plainTextEdit.clear()
        elif ret == qm.No:
            pass
        self.Update_Nuclides_Supp_CB()

    def Read_Mat_Supp_Data(self):
        self.lines = self.v_1.toPlainText().split('\n')
        self.Value_To_Find = None
        self.Nuclide_Supp_List_CB.clear()
        self.Element_Supp_List_CB.clear()
        if self.Mat_To_Suppress_List_CB.currentIndex() >= 1:
            if self.materials_name_list:
                #Mat_Name = self.materials_name_list[self.Mat_To_Suppress_List_CB.currentIndex() -1]
                Mat_Name = self.Mat_To_Suppress_List_CB.currentText()
                #Mat_Id = self.materials_id_list[self.Mat_To_Suppress_List_CB.currentIndex() -1]
                Mat_Id = self.materials_id_list[self.materials_name_list.index(Mat_Name)]
                self.Mat_Name = Mat_Name
                self.Mat_Id = Mat_Id
                self.find_Nuclides(self.lines, Mat_Name, 'add_nuclide')
                self.find_Elements(self.lines, Mat_Name, 'add_element')
                self.Update_Nuclides_Supp_CB()
                self.Update_Elements_Supp_CB()
        else:
            self.reset_Modify_Supp_Data()

    def reset_Modify_Data(self):
        self.Mat_ID_LE.clear()
        self.Temp_LE.clear()
        self.Density_LE.clear()
        self.Density_Unit_CB.setCurrentIndex(0)
        self.SAB_CB.setCurrentIndex(0)
        self.Percent_Nuclide_LE.clear()
        self.Percent_Nuc_Type_CB.setCurrentIndex(0)
        self.Nuclide_CB.clear()
        self.Element_CB.clear()
        self.Percent_Element_LE.clear()
        self.Percent_Ele_Type_CB.setCurrentIndex(0)
        self.Enricht_LE.clear()
        self.Enrichment_Target_CB.clear()
        self.Enrichment_Type_CB.setCurrentIndex(1)
        for item in self.Liste1:
            item.setEnabled(False)
        for item in self.Liste2:
            item.setEnabled(False)

    def reset_Modify_Supp_Data(self):
        self.Mat_To_Suppress_List_CB.setCurrentIndex(0)
        self.Nuclide_Supp_List_CB.clear()
        self.Element_Supp_List_CB.clear()

    def Update_Nuclide_Data(self):
        if self.Materials_Construct.currentIndex() == 1:
            if len(self.materials_name_list) >= 1:
                if self.Mat_List_CB.currentIndex() >= 1:
                    if self.Nucl_Modif_RB.isChecked():
                        if self.Nuclide_CB.currentIndex() >= 1:
                            self.Percent_Nuclide_LE.setText(self.Nuclides_In_Material[self.Nuclide_CB.currentText()]['Fraction'])
                            fraction_type = self.Nuclides_In_Material[self.Nuclide_CB.currentText()]['Fraction_type']
                            self.Percent_Nuc_Type_CB.setCurrentIndex(self.Percent_Nuc_Type_CB.findText(fraction_type, QtCore.Qt.MatchFixedString))
                        else:
                            self.Percent_Nuclide_LE.setText('')
                    else:
                        pass
                else:
                    self.Nuclide_CB.clear()
                    self.Percent_Nuclide_LE.setText('')

    def Update_Element_Data(self):
        self.Enricht_LE.setText('')
        if self.Materials_Construct.currentIndex() == 1:
            if len(self.materials_name_list) >= 1:
                if self.Mat_List_CB.currentIndex() != 0:
                    if self.Elm_Modif_RB.isChecked():
                        if self.Element_CB.currentIndex() >=1:
                            element = self.Element_CB.currentText()
                            if self.Elements_In_Material[element]:
                                self.Percent_Element_LE.setText(self.Elements_In_Material[element]['Fraction'])
                                fraction_type = self.Elements_In_Material[element]['Fraction_type']
                                self.Percent_Ele_Type_CB.setCurrentIndex(self.Percent_Ele_Type_CB.findText(fraction_type, QtCore.Qt.MatchFixedString))
                                if self.Elements_In_Material[element]['Enrichment']:
                                    self.Enricht_LE.setText(self.Elements_In_Material[element]['Enrichment'])
                                    self.Update_Enrich_Target_List()
                                    target_item = self.Elements_In_Material[element]['Enrichment_target'].replace("'", "")
                                    index = self.Enrichment_Target_CB.findText(target_item, QtCore.Qt.MatchFixedString)
                                    self.Enrichment_Target_CB.setCurrentIndex(index)
                                    target_type = self.Elements_In_Material[element]['Enrichment_type'].replace("'", "")
                                    index = self.Enrichment_Type_CB.findText(target_type, QtCore.Qt.MatchFixedString)
                                    self.Enrichment_Type_CB.setCurrentIndex(index)

                            #self.showDialog('Warning', 'Element to modify not yet saved !')

                        else:
                            self.Percent_Element_LE.setText('')
                            self.Enricht_LE.setText('')
                    else:
                        pass
                else:
                    self.Element_CB.clear()
                    self.Percent_Element_LE.setText('')

    def Update_Mat_Supp_Data(self):
        if self.Materials_Construct.currentIndex() == 1:
            if len(self.materials_name_list) >= 1:
                if self.Mat_To_Suppress_List_CB.currentIndex() == 0:
                    self.Nuclide_Supp_List_CB.clear()
                    self.Element_Supp_List_CB.clear()

    def find_SAB(self, lines, Mat_Name, key):
        for line in lines:
            if Mat_Name in line:
                if key in line:
                    items = line[line.find("(") + 1: line.find(")")].replace(' ', '').split(',')
                    self.Value_To_Find = items[0]
                    break

    def find_Nuclides(self, lines, Mat_Name, key):
        self.Mat_Nuclide_List.setdefault(Mat_Name, [])
        self.Mat_Nuclide_Percent_List.setdefault(Mat_Name, [])
        self.Mat_Nuclide_Percent_Type_List.setdefault(Mat_Name, [])
        for line in lines:
            if Mat_Name in line:
                if key in line:
                    items = line[line.find("(") + 1: line.find(")")].replace(' ', '').split(',')
                    self.Nuclide_to_find = items[0]
                    self.Nuclide_to_find_percent = items[1]
                    if len(items) >= 3:
                        if '=' in items[2]:
                            self.Percent_Nuc_Type = items[2].split('=')[1]
                        else:
                            self.Percent_Nuc_Type = items[2]
                    else:
                        self.Percent_Nuc_Type = 'ao'
                    if self.Nuclide_to_find not in self.Mat_Nuclide_List[Mat_Name]:
                        self.Mat_Nuclide_List[Mat_Name].append(self.Nuclide_to_find)
                        self.Mat_Nuclide_Percent_List[Mat_Name].append(self.Nuclide_to_find_percent)
                        self.Mat_Nuclide_Percent_Type_List[Mat_Name].append(self.Percent_Nuc_Type)
                    self.Store_Material_Nuclides_Info(self.Nuclide_to_find, self.Nuclide_to_find_percent, self.Percent_Nuc_Type)

    def Update_Nuclides_CB(self):
        """for item in self.Liste1:
            item.setEnabled(True)"""
        '''for item in self.Liste2:
            item.setEnabled(False)'''
        self.Nuclide_CB.clear()
        if self.Nucl_Add_RB.isChecked():
            for cle in src.materials.NATURAL_ABUNDANCE.keys():
                self.Nuclide_CB.addItem(cle)
        elif self.Nucl_Modif_RB.isChecked():
            if len(self.Mat_Nuclide_List.setdefault(self.Mat_Name, [])):
                self.Nuclide_CB.addItem('Select nuclide')
                self.Nuclide_CB.addItems(self.Mat_Nuclide_List[self.Mat_Name])
            else:
                self.Nuclide_CB.addItem(None)

    def Update_Nuclides_Supp_CB(self):
        self.Nuclide_Supp_List_CB.clear()
        if len(self.Mat_Nuclide_List.setdefault(self.Mat_Name, [])):
            self.Nuclide_Supp_List_CB.addItem('Select nuclide')
            self.Nuclide_Supp_List_CB.addItems(self.Mat_Nuclide_List[self.Mat_Name])
        else:
            self.Nuclide_Supp_List_CB.addItem(None)

    def Update_Elements_Supp_CB(self):
        self.Element_Supp_List_CB.clear()
        if len(self.Mat_Element_List.setdefault(self.Mat_Name, [])):
            self.Element_Supp_List_CB.addItem('Select element')
            self.Element_Supp_List_CB.addItems(self.Mat_Element_List[self.Mat_Name])
        else:
            self.Element_Supp_List_CB.addItem(None)

    def find_Elements(self, lines, Mat_Name, key):
        self.Mat_Element_List.setdefault(Mat_Name, [])
        self.Mat_Element_Percent_List.setdefault(Mat_Name, [])
        self.Mat_Element_Percent_Type_List.setdefault(Mat_Name, [])
        self.Element_Enrichment = ''
        for line in lines:
            if Mat_Name in line:
                if key in line:
                    items = line[line.find("(") + 1: line.find(")")].replace(' ', '').split(',')
                    self.Element_to_find = items[0]
                    self.Element_to_find_percent = items[1]
                    if len(items) >= 3:
                        for w in items:
                            if 'percent_type' in w:
                                self.Percent_Elm_Type = w.split('=')[1].replace("'", "")
                                break
                            elif 'ao' in w or 'wo' in w:
                                self.Percent_Elm_Type = w
                                break
                        for w in items:
                            if 'enrichment' in w:
                                self.Enrichment = True
                                if self.Element_to_find == 'U' and self.openmc_version >= 141:
                                    self.Element_Enrichment_Target = 'U235'
                                    self.Element_Enrichment_Type = 'wo'
                                else:
                                    if 'enrichment_target' in w:
                                        self.Element_Enrichment_Target = w.split('=')[1]
                                    elif 'enrichment_type' in w:
                                        self.Element_Enrichment_Type = w.split('=')[1]
                                    else:
                                        self.Element_Enrichment = w.split('=')[1]
                            else:
                                self.Enrichment = False
                                self.Element_Enrichment = ''
                    else:
                        self.Percent_Elm_Type = 'ao'

                    if self.Element_to_find not in self.Mat_Element_List[Mat_Name]:
                        element = self.Element_to_find
                        fraction = self.Element_to_find_percent
                        fraction_type = self.Percent_Elm_Type
                        enrichment = ""
                        enrichment_target = ""
                        enrichment_type = ""
                        enrichment_target_list = []
                        self.Mat_Element_List[Mat_Name].append(element)
                        self.Mat_Element_Percent_List[Mat_Name].append(fraction)
                        self.Mat_Element_Percent_Type_List[Mat_Name].append(fraction_type)
                        if self.Enrichment:
                            enrichment = self.Element_Enrichment
                            enrichment_target = self.Element_Enrichment_Target
                            enrichment_type = self.Element_Enrichment_Type
                            enrichment_target_list = self.Isotopes_In_Elements[element.replace("'", "")]
                        self.Store_Material_Elements_Info(element, fraction, fraction_type, enrichment, enrichment_target_list, enrichment_target, enrichment_type)
                        
    def Store_Materials_Info(self, Mat_Name, Mat_Id):
        # new dictionary filling : parent
        self.Materials_In_Model[Mat_Name] = {}
        self.Materials_In_Model[Mat_Name]['id'] = Mat_Id
        self.Materials_In_Model[Mat_Name]['name'] = Mat_Name
        self.Materials_In_Model[Mat_Name]['temperature'] = self.Temperature
        self.Materials_In_Model[Mat_Name]['density'] = self.Mat_Density
        self.Materials_In_Model[Mat_Name]['density_unit'] = self.Density_Unit
        self.Materials_In_Model[Mat_Name]['SAB'] = self.SAB

    def Store_Material_Nuclides_Info(self, nuclide, fraction, fraction_type):
        # nested dictionaries : childs
        self.Nuclides_In_Material[nuclide] = {}
        self.Nuclides_In_Material[nuclide]['Symbol'] = nuclide.replace("'", "")
        self.Nuclides_In_Material[nuclide]['Fraction'] = fraction
        self.Nuclides_In_Material[nuclide]['Fraction_type'] = fraction_type.replace("'", '')
        if self.Nucl_Modif_RB.isChecked():
            if self.Nuclide_CB.currentIndex() >= 1:
                self.Mat_Nuclide_Percent_List[self.Mat_Name][self.Nuclide_CB.currentIndex() - 1] = fraction
                self.Mat_Nuclide_Percent_Type_List[self.Mat_Name][self.Nuclide_CB.currentIndex() - 1] = fraction_type

    def Store_Material_Elements_Info(self, element, fraction, fraction_type, enrichment, enrichment_target_list, enrichment_target, enrichment_type):
        # nested dictionaries : child
        self.Elements_In_Material[element] = {}
        self.Elements_In_Material[element]['Symbol'] = element
        self.Elements_In_Material[element]['Fraction'] = fraction
        self.Elements_In_Material[element]['Fraction_type'] = fraction_type.replace("'", "")
        self.Elements_In_Material[element]['Enrichment'] = enrichment
        self.Elements_In_Material[element]['Enrichment_target'] = enrichment_target
        self.Elements_In_Material[element]['Enrichment_type'] = enrichment_type
        if self.Element_CB.currentText() == element:
            index = self.Element_CB.currentIndex() - 1
            self.Mat_Element_Percent_List[self.Mat_Name][index] = fraction
            self.Mat_Element_Percent_Type_List[self.Mat_Name][index] = fraction_type

    def Update_Elements_CB(self):
        self.Element_CB.clear()
        self.Percent_Element_LE.clear()
        self.Enricht_LE.clear()
        self.Percent_Ele_Type_CB.setCurrentIndex(1)
        self.Enrichment_Type_CB.setCurrentIndex(1)
        if self.Elm_Add_RB.isChecked():
            for cle in src.materials.ELEMENT_SYMBOL.values():
                self.Element_CB.addItem(cle)
        elif self.Elm_Modif_RB.isChecked():
            if len(self.Mat_Element_List.setdefault(self.Mat_Name, [])):
                self.Element_CB.addItem('Select element')
                self.Element_CB.addItems(self.Mat_Element_List[self.Mat_Name])
            else:
                self.Element_CB.addItem(None)

    def find_Temperature(self, lines, Mat_Name, key):
        from string import ascii_letters
        for line in lines:
            if Mat_Name in line:
                if key in line:
                    items = line.replace(' ', '').split(',')
                    for w in items:
                        if key in w:
                            self.Value_To_Find = w.split('=')[1].rstrip(ascii_letters).strip(')')
                            break
                        else:
                            self.Value_To_Find = None
                    break

    def find_Density(self, lines, Mat_Name, key):
        for line in lines:
            if Mat_Name in line:
                if key in line:
                    items = line[line.find("(") + 1: line.find(")")].replace(' ', '').split(',')
                    self.Density_Unit = items[0]
                    self.Value_To_Find = items[1]
                    break

    def Detect_Data(self, line, key):
        items = line[line.find("(") + 1: line.find(")")].replace(' ', '').split(',')
        for w in items:
            if key in w:
                self.Value_To_Find = w.split('=')[1]
                break
            else:
                self.Value_To_Find = None

    def sync_name1(self):
        import string
        pos = self.lineEdit.cursorPosition()
        self.lineEdit.setCursorPosition(pos)
        self.material_suffix = self.lineEdit.text().rstrip(string.digits)

    def sync_name(self):
        import string
        self.material_suffix = self.lineEdit.text().rstrip(string.digits)
        self.lineEdit_2.setText(str(self.material_id))
        if self.add_id_CB.isChecked():
            self.lineEdit.setText(self.material_suffix + str(self.material_id))
        else:
            self.material_suffix = self.lineEdit.text().rstrip(string.digits)
            self.lineEdit.setText(self.material_suffix)

    def sync_id(self):
        import string
        if self.lineEdit_2.text():
            self.material_id = int(self.lineEdit_2.text())
            if self.add_id_CB.isChecked():
                self.lineEdit.setText(self.material_suffix + str(self.material_id))
            else:
                self.material_suffix = self.lineEdit.text().rstrip(string.digits)
                self.lineEdit.setText(self.material_suffix)

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

    def Add_Material(self):
        Mat_Exists = False
        self.Find_string(self.plainTextEdit, "import openmc")
        if self.Insert_Header:
            self.Find_string(self.v_1, "import openmc")
            if self.Insert_Header:
                print('import openmc')
        if self.lineEdit.text() == '':
            self.showDialog('Warning', 'Cannot create material, select name first !')
            return
        elif self.lineEdit_2.text() == '':
            self.showDialog('Warning', 'Cannot create material, select id first !')
            return
        if self.Check_Mixture_CB.isChecked():
            if self.Mixture_CB.currentIndex() == 0:
                self.showDialog('Warning', 'Select Mixture first !')
                return
            else:
                pass
        else:
            pass
        if self.lineEdit.text() in self.materials_name_list:
            self.showDialog('Warning', 'Material name already used, select new name !')
            Mat_Exists = True
            return
        else:
            Mat_Exists = False
        if int(self.lineEdit_2.text()) in self.materials_id_list:
            self.showDialog('Warning', 'Material id already used, select new id !')
            Mat_Exists = True
            return
        else:
            Mat_Exists = False
        if Mat_Exists:
            self.Update_Mat_List()
        else:
            if not self.Check_Mixture_CB.isChecked() and self.lineEdit_4.text() == '' and self.comboBox.currentText() not in ['sum', 'macro']:
                self.showDialog('Warning', 'Cannot create material, specify density first !')
                return
            self.Find_string(self.plainTextEdit, "materials.xml")
            if self.Insert_Header:
                self.Find_string(self.v_1, "materials.xml")
                if self.Insert_Header:
                    print('\n############################################################################### \n'
                   '#                 Exporting to OpenMC materials.xml file \n'
                   '###############################################################################')
                else:
                    self.Find_string(self.v_1, "openmc.Materials")
            if self.Check_Mixture_CB.isChecked():
                Density_Unit = "g/cc"
                Density = self.Mixture_Density
            else:
                Density_Unit = str(self.comboBox.currentText())
                Density = self.lineEdit_4.text()
            if self.Check_Mixture_CB.isChecked():
                self.Def_Mixture_Fraction()
                print('\n' + str(self.lineEdit.text()), "= openmc.Material(material_id=" + str(self.lineEdit_2.text()) +
                      ", name='" + self.Mixture_Name + "',", "temperature=" + str(self.lineEdit_3.text()) + ')')

                for element in self.Mixt_Element_List:
                    index = self.Mixt_Element_List.index(element)
                    fraction = self.Frac_List[index]
                    if True in [char.isdigit() for char in element]:
                        nuclide = element.replace("-", "")
                        print(str(self.lineEdit.text()) + ".add_nuclide('" + nuclide + "',", str(fraction) + ",", "'" + self.Fraction_Type + "'" + ")")
                    else:
                        print(str(self.lineEdit.text()) + ".add_element('" + element + "',", str(fraction) + ",", "'" + self.Fraction_Type + "'" + ")")
            else:
                print('\n' + str(self.lineEdit.text()), "= openmc.Material(material_id=" + str(self.lineEdit_2.text()) +
                      ", name='" + self.lineEdit.text() + "',", "temperature=" + str(self.lineEdit_3.text()) + ')')
            if self.comboBox.currentText() == 'sum':
                print(str(self.lineEdit.text()) + ".set_density('sum')")
            elif self.comboBox.currentText() == 'macro':
                print(str(self.lineEdit.text()) + ".set_density('macro')")
            else:
                print(str(self.lineEdit.text())+'.set_density(' + "'" + Density_Unit + "',", str(Density) + ")")
            if self.comboBox_2.currentText() != 'None':
                print(str(self.lineEdit.text() + ".add_s_alpha_beta(") + str("'"+self.comboBox_2.currentText() + "')"))

            self.mat = self.lineEdit.text()
            self.materials_name_list.append(self.lineEdit.text())
            self.materials_name_sub_list.append(self.lineEdit.text())
            self.materials_id_list.append(self.lineEdit_2.text())
            self.materials_id_sub_list.append(self.lineEdit_2.text())
            self.Mat_Density = Density
            self.Density_Unit = Density_Unit
            self.SAB = str("'"+self.comboBox_2.currentText()+"'")
            self.Store_Materials_Info(self.mat, self.lineEdit_2.text())
            self.Mat_Element_List[self.mat] = []
            self.Mat_Nuclide_List[self.mat] = []

        #self.material_id = int(self.materials_id_list[-1]) + 1
        self.Increment_Mat_Id()
        self.lineEdit_2.setText(str(self.material_id))
        self.lineEdit.setText(self.material_suffix + str(self.material_id))
        self.Check_Mixture_CB.setChecked(False)
        self.Mixture_CB.setCurrentIndex(0)
        self.lineEdit_4.setText('')

    def Add_Nuclide(self):
        if self.mat:
            if self.comboBox_3.currentText() != 'None':
                if self.comboBox_3.currentText() in self.Neutron_XS_List:
                    if self.comboBox_3.currentText() in self.Mat_Nuclide_List[self.mat]:
                        self.showDialog('Warning',
                                        'Nuclide ' + self.comboBox_3.currentText() + ' already in material! Choose another nuclide !')
                        self.comboBox_3.setCurrentIndex(0)
                        self.lineEdit_5.clear()
                        return
                    else:
                        if self.lineEdit_5.text() == '':
                            self.showDialog('Warning', 'Enter nuclide fraction first !')
                            return
                        else:
                            self.Mat_Nuclide_List[self.mat].append(self.comboBox_3.currentText())
                            print(self.mat + ".add_nuclide('"+ self.comboBox_3.currentText() + "', " +
                               self.lineEdit_5.text() + ", percent_type=" + "'" + self.comboBox_4.currentText() + "')")
                            self.nuclide_added = True
                else:
                    self.showDialog('Warning', 'Cross sections for Nuclide ' + self.comboBox_3.currentText() + ' are not available in installed data !')
                    return
            else:
                self.showDialog('Warning', 'Select nuclide first !')
                return
        else:
            self.showDialog('Warning', 'Add material first !')
            return
        self.comboBox_3.setCurrentIndex(0)
        self.comboBox_4.setCurrentIndex(0)
        self.lineEdit_5.clear()

    def Fill_Mixture_List(self):
        if self.Check_Mixture_CB.isChecked():
            self.Mixture_CB.show()
            self.Fraction_Type_CB.show()
            self.label_10.show()
            self.label_38.hide()
            self.label_42.hide()
            self.lineEdit_4.hide()
            self.comboBox.hide()
        else:
            self.Mixture_CB.hide()
            self.Fraction_Type_CB.hide()
            self.label_10.hide()
            self.label_38.show()
            self.label_42.show()
            self.lineEdit_4.show()
            self.comboBox.show()
            self.lineEdit_3.setText('293.6')
            self.Mixture_CB.setCurrentIndex(0)

    def Add_Mixture(self):
        self.Mixt_Element_List = []
        self.Mixt_Element_Atom_Frac_List = []
        self.Mixt_Element_Weight_Frac_List = []
        self.Mixt_Element_Atom_Density_List = []
        self.Mixture_Density = ''
        if '°' in self.Mixture_CB.currentText():
            self.Temperature = self.Mixture_CB.currentText().split('=')[1].split('°')[0]
        else:
            self.Temperature = '293.6'
        self.lineEdit_3.setText(self.Temperature)
        Mixtures = src.Mixture_pnnl.Mixtures
        ID = self.Mixture_CB.currentIndex()
        if ID >= 1:
            self.Mixture_Key = list(Mixtures.keys())[ID - 1]
            Components = Mixtures.get(self.Mixture_Key)
            self.Mixture_Name = Components[0]
            self.Mixture_Density = Components[1]
            self.Mixture_Components = Components[2]
            for index in range(int(len(self.Mixture_Components) / 4)):
                j = index + index * 3
                element = self.Mixture_Components[j]
                Weight_Fraction = self.Mixture_Components[j + 1]
                Atom_Fraction = self.Mixture_Components[j + 2]
                Atom_Density = self.Mixture_Components[j + 3]
                self.Mixt_Element_List.append(element)
                self.Mixt_Element_Atom_Frac_List.append(Atom_Fraction)
                self.Mixt_Element_Weight_Frac_List.append(Weight_Fraction)
                self.Mixt_Element_Atom_Density_List.append(Atom_Density)

    def Def_Mixture_Fraction(self):
        if self.Fraction_Type_CB.currentIndex() == 0:
            self.Fraction_Type = "wo"
            self.Frac_List = self.Mixt_Element_Weight_Frac_List
        else:
            self.Fraction_Type = "ao"
            self.Frac_List = self.Mixt_Element_Atom_Frac_List

    def Add_Element(self):
        if self.mat:
            if self.comboBox_5.currentText() != 'None':
                if self.comboBox_5.currentText() in self.Mat_Element_List[self.mat]:
                    self.showDialog('Warning',
                                    'Element ' + self.comboBox_5.currentText() + ' already in material! Choose another element !')
                    self.comboBox_5.setCurrentIndex(0)
                    self.lineEdit_6.clear()
                    return
                else:
                    if self.lineEdit_6.text() == '':
                        self.showDialog('Warning', 'Enter element fraction first !')
                        return
                    else:
                        if self.lineEdit_7.text():
                            if self.comboBox_5.currentText() == 'U' and self.openmc_version >= 141:
                                    print(self.mat + ".add_element( '" + self.comboBox_5.currentText() + "', " +
                                      self.lineEdit_6.text() + ", '" + self.comboBox_6.currentText() + "', enrichment=" +
                                      self.lineEdit_7.text() + "') ")
                            else:
                                if self.comboBox_7.currentIndex() >= 1:
                                    print(self.mat + ".add_element( '" + self.comboBox_5.currentText() + "', " +
                                        self.lineEdit_6.text() + ", '" + self.comboBox_6.currentText() + "', enrichment=" +
                                        self.lineEdit_7.text() + ", enrichment_target='" + self.comboBox_7.currentText() +
                                        "', enrichment_type='" + self.comboBox_8.currentText() + "') ")
                                else:
                                    if self.comboBox_5.currentText() != 'U' and self.openmc_version >= 141:
                                        self.showDialog('Warning', 'Select enrichment target first !')
                                        return
                        else:
                            print(self.mat + ".add_element( '" + self.comboBox_5.currentText() + "', " +
                                  self.lineEdit_6.text() + ", '" + self.comboBox_6.currentText() + "')")
                        self.Mat_Element_List[self.mat].append(self.comboBox_5.currentText())
                        self.element_added = True
            else:
                self.showDialog('Warning', 'Select element first !')
                return
        else:
            self.showDialog('Warning', 'Add material first !')
            return
        self.comboBox_5.setCurrentIndex(0)
        self.comboBox_6.setCurrentIndex(0)
        self.comboBox_8.setCurrentIndex(0)
        self.lineEdit_6.clear()
        self.lineEdit_7.clear()

    def update_materials_list(self, TextEdit):
        import re
        self.current_line = ""
        string_to_find = "openmc.Materials"
        self.Find_string(TextEdit, string_to_find)

        if not self.Insert_Header:
            st = self.current_line
            self.liste = re.findall('\[(.*?)\]', st)
        if self.lineEdit.text():
            self.liste.append(self.lineEdit.text())

    def Export_to_Main_Window(self):                          
        export_to_main_window = False
        self.v_1.moveCursor(QTextCursor.End)
        if self.plainTextEdit.toPlainText():
            lines = self.plainTextEdit.toPlainText().split('\n')
            for line in lines:
                if 'openmc.Material' in line:
                    export_to_main_window = True
        if export_to_main_window:
            string_to_find = "materials.export_to_xml()"
            self.lines = self.v_1.toPlainText().split('\n')
            self.Find_string(self.v_1, string_to_find)
            cursor = self.v_1.textCursor()
            self.Update_Mat_List()     #  to be verified
            if self.Insert_Header:
                self.plainTextEdit.moveCursor(QTextCursor.End) #######
                print('\nmaterials = openmc.Materials(','['+', '.join(self.materials_name_list)+']',')')
                cursor.insertText(self.plainTextEdit.toPlainText())
                cursor.insertText(string_to_find + '\n')
                #self.Insert_Header = True
            else:
                if self.Materials_Construct.currentIndex() == 1:
                    for mat in self.Mat_List_to_Modify:
                        self.lines[:] = [item for item in self.lines if mat not in item]
                    self.v_1.clear()
                    for line in self.lines:
                        if line:
                            if 'openmc.Material' in line:   # and 'openmc.Materials' not in line:
                                self.v_1.insertPlainText('\n')
                            self.v_1.insertPlainText(line + '\n')
                    for mat in self.Mat_List_to_Modify:
                        if mat not in self.materials_name_list:
                            self.materials_name_list.append(mat)
                    self.materials_name_list.sort()

                document = self.v_1.toPlainText()
                lines = document.split('\n')
                text = []
                for line in lines:
                    if "openmc.Materials" in line:
                        document = self.v_1.toPlainText().replace(line, "")
                self.plainTextEdit.moveCursor(QTextCursor.End)
                print('\nmaterials = openmc.Materials(' + '[' + ', '.join(self.materials_name_list) + ']' + ')')
                print(string_to_find)
                document = document.replace(string_to_find, self.plainTextEdit.toPlainText())
                self.v_1.clear()
                cursor.insertText(document)

            self.text_inserted = True
            self.plainTextEdit.clear()
            self.element_added = False
            self.nuclide_added = False
        else:
            pass
        self.mat = None

    def Clear_Output(self):
        self.plainTextEdit.clear()

    def Clear_Lists(self):
        self.Mat_To_Suppress_List_CB.setCurrentIndex(0)
        self.reset_Modify_Data()
        self.reset_Modify_Supp_Data()

        if self.materials_name_sub_list:
            self.Remove_Selected(self.materials_name_sub_list, self.materials_name_list)
            self.Remove_Selected(self.materials_id_sub_list, self.materials_id_list)

        self.Increment_Mat_Id()
        self.lineEdit_2.setText(str(self.material_id))
        if self.Mat_List_CB.currentIndex() >= 1:
            Mat_Name = self.Mat_List_CB.currentText()
            if self.Mat_Nuclide_Add_List[Mat_Name]:
                self.Remove_Selected(self.Mat_Nuclide_Add_List[Mat_Name], self.Mat_Nuclide_List[Mat_Name])
        self.Mat_List_CB.clear()
        self.Mat_List_CB.addItem('Select Material')
        self.Mat_List_CB.addItems(sorted(self.materials_name_list))
        self.Mat_To_Suppress_List_CB.clear()
        self.Mat_To_Suppress_List_CB.addItem('Select Material')
        self.Mat_To_Suppress_List_CB.addItems(sorted(self.materials_name_list))

    def Remove_Selected(self, Sub_List, List):
        List[:] = [item for item in List if item not in Sub_List]

    def normalOutputWritten(self, text):
        self.highlighter = Highlighter(self.plainTextEdit.document())
        cursor = self.plainTextEdit.textCursor()
        self.plainTextEdit.setTextCursor(cursor)
        cursor.insertText(text)
        self.plainTextEdit.moveCursor(cursor.End)

class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)
 
    def write(self, text):
        self.textWritten.emit(str(text))
        pass

    def flush(self):
        pass 
