import os
import sys
import os.path
import PyQt5
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMessageBox
import datetime
import shutil
import subprocess
from pathlib import Path
from PyQt5.QtGui import QFont, QTextCharFormat, QBrush
from src.PyEdit import TextEdit, NumberBar, tab, lineHighlightColor
import numpy as np
from matplotlib import pyplot as plt, cm
from matplotlib import colors
import pandas as pd
import glob
import h5py
from PyQt5.QtWidgets import (QPlainTextEdit, QWidget, QVBoxLayout, QApplication, QFileDialog, QMessageBox, QLabel, QCompleter, 
                            QHBoxLayout, QTextEdit, QToolBar, QComboBox, QAction, QLineEdit, QDialog, QPushButton, QSizePolicy, 
                            QToolButton, QMenu, QMainWindow, QInputDialog, QColorDialog, QStatusBar, QSystemTrayIcon)
from PyQt5.QtGui import (QIcon, QPainter, QTextFormat, QColor, QTextCursor, QKeySequence, QClipboard, QTextDocument, 
                            QPixmap, QStandardItemModel, QStandardItem, QCursor, QFontDatabase)
from PyQt5.QtCore import (Qt, QVariant, QRect, QDir, QFile, QFileInfo, QTextStream, QSettings, QTranslator, QLocale, 
                            QProcess, QPoint, QSize, QCoreApplication, QStringListModel, QLibraryInfo)
from PyQt5 import QtPrintSupport
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtGui import QTextOption

iconsize = QSize(24, 24)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('max_colwidth', 30)
try:
    import openmc
except:
    pass

class TallyDataProcessing(QtWidgets.QMainWindow):
    from src.func import resize_ui, showDialog
    
    #def __init__(self, shellwin, parent=None):
    def __init__(self, parent=None):
        super(TallyDataProcessing, self).__init__(parent)
        uic.loadUi("src/ui/TallyDataProcessing.ui", self)
        try:
            from openmc import __version__
            self.openmc_version = int(__version__.split('-')[0].replace('.', ''))
        except:
            self.openmc_version = 0

        self.groupBox_15.hide()
        self.FILTER_TYPES = ['UniverseFilter', 'MaterialFilter', 'CellFilter', 'CellFromFilter', 'CellbornFilter',
                        'CellInstanceFilter', 'CollisionFilter', 'SurfaceFilter', 'MeshFilter', 'MeshSurfaceFilter',
                        'EnergyFilter', 'EnergyoutFilter', 'MuFilter', 'PolarFilter', 'AzimuthalFilter',
                        'DistribcellFilter', 'DelayedGroupFilter', 'EnergyFunctionFilter', 'LegendreFilter',
                        'SpatialLegendreFilter', 'SphericalHarmonicsFilter', 'ZernikeFilter', 'ZernikeRadialFilter',
                        'ParticleFilter', 'TimeFilter']
        self.sp_file = 'None'
        self.Display = False
        self.Tallies = {}
        self.Mesh_xy_RB.hide()
        self.Mesh_xz_RB.hide()
        self.Mesh_yz_RB.hide()
        self.spinBox.hide()
        self.spinBox_2.hide()
        self.buttons = [self.xLog_CB, self.yLog_CB, self.Add_error_bars_CB, self.xGrid_CB, self.yGrid_CB, self.MinorGrid_CB, self.label_2, self.label_3]
        self.buttons_Stack = [self.label_5, self.label_6, self.label_7, self.row_SB, self.col_SB]
        for elm in self.buttons: 
            elm.setEnabled(False)
        for elm in self.buttons_Stack: 
            elm.setEnabled(False)
        self.Graph_Layout_CB.setEnabled(False)
        self.Graph_type_CB.setEnabled(False)
        #self.set_Graph_stack()
        
        # add new editor for output window
        self.editor = TextEdit()
        self.editor.setWordWrapMode(QTextOption.NoWrap)
        self.numbers = NumberBar(self.editor)
        layoutH8 = QHBoxLayout()
        layoutH8.addWidget(self.numbers)
        layoutH8.addWidget(self.editor)    
        self.gridLayout_18.addLayout(layoutH8, 0, 0)
        # add editor to second tab 
        self.editor1 = TextEdit()
        self.editor1.setWordWrapMode(QTextOption.NoWrap)
        self.numbers1 = NumberBar(self.editor1)
        layoutH9 = QHBoxLayout()
        layoutH9.addWidget(self.numbers1)
        layoutH9.addWidget(self.editor1)    
        self.gridLayout_5.addLayout(layoutH9, 0, 0)

        self.grid = False
        self.which_axis = 'none'
        self.which_grid = 'both'
        self.resize_ui()

        self.Norm_Bins_comboBox = CheckableComboBox()
        self.Norm_Bins_comboBox.addItem('Check item')
        self.gridLayout_Norm.addWidget(self.Norm_Bins_comboBox)
        self.Norm_Bins_comboBox.model().item(0).setEnabled(False)

        # +++++++++++++++++++++++
        self.Tally_name_LE.setPlaceholderText("Name")
        self.root = QFileInfo.path(QFileInfo(QCoreApplication.arguments()[0]))
        self.openPath = ""
        self.dirpath = QDir.homePath() + "/Documents/tmp/"
        self.filename = ""
        #self.MaxRecentFiles = 15
        self.recentFileActs = []
        self.settings = QSettings("PyEdit", "PyEdit")
        #self.createActions()
        # +++++++++++++++++++++++
        if not self.score_plot_PB.isEnabled():
            self.score_plot_PB.setToolTip('If filter bins or selected nuclides or selected score change, press select button first')
        self.scores_display_PB.setToolTip('Press this button before ploting!')
        self._initButtons()
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        #sys.stderr = EmittingStream(textWritten=self.normalOutputWritten)
        
        # lines to be removed   
        #self.sp_file = str(Path.home()) + '/My_Projects/Project-ERSN-OpenMC/Gui_orig/examples/tallies/statepoint.310.h5'
        cwd = os.getcwd()
        self.sp_file = str(cwd) + '/examples/tallies/statepoint.310.h5'
        if not os.path.isfile(self.sp_file):
            self.sp_file = None
        else:
            self.lineEdit.setText(self.sp_file)
            self.Get_data_from_SP_file()
                  
    def _initButtons(self):
        self.browse_PB.clicked.connect(self.Get_SP_File)
        self.get_tally_info_PB.clicked.connect(self.Display_Tallies_Inf)
        self.Tally_id_comboBox.currentIndexChanged.connect(self.SelectTally)
        self.tally_display_PB.clicked.connect(self.Display_tally)
        self.Filters_comboBox.currentIndexChanged.connect(self.SelectFilter)
        self.filters_display_PB.clicked.connect(self.Display_filters)
        self.nuclides_display_PB.clicked.connect(self.Clear_nuclides)
        self.Nuclides_comboBox.currentIndexChanged.connect(self.SelectNuclides)
        self.Scores_comboBox.currentIndexChanged.connect(self.SelectScores)
        self.scores_display_PB.clicked.connect(self.Display_scores)
        self.Mesh_xy_RB.toggled.connect(self.Mesh_settings)
        self.Mesh_xz_RB.toggled.connect(self.Mesh_settings)
        self.Mesh_yz_RB.toggled.connect(self.Mesh_settings)
        self.Graph_type_CB.currentIndexChanged.connect(self.set_Scales)
        self.Plot_by_CB.currentIndexChanged.connect(self.set_Scales)
        self.xGrid_CB.stateChanged.connect(self.plot_grid_settings)
        self.yGrid_CB.stateChanged.connect(self.plot_grid_settings)
        self.MinorGrid_CB.stateChanged.connect(self.plot_grid_settings)
        self.Graph_Layout_CB.currentIndexChanged.connect(self.set_Graph_stack)
        self.Plot_by_CB.currentIndexChanged.connect(self.set_Graph_stack)
        self.score_plot_PB.clicked.connect(self.Plot)
        self.Close_Plots_PB.clicked.connect(lambda:plt.close('all'))
        self.ResetPlotSettings_PB.clicked.connect(self.Reset_Plot_Settings)
        self.Nuclides_List_LE.textChanged.connect(lambda:self.score_plot_PB.setEnabled(False))
        self.Scores_List_LE.textChanged.connect(lambda:self.score_plot_PB.setEnabled(False))
        self.lineEdit.textChanged.connect(self.Reset_Tally_CB)
        self.Define_Buttons()
        
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#++++++++++++++++++++++ CODE TO PROCESS SIMULATION SP FILE +++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def Get_SP_File(self):
        self.Tally_id_comboBox.clear()
        self.Tally_id_comboBox.addItem("Select the tally's ID")
        self.editor.clear()
        self.Plot_by_CB.clear()
        self.Filters_comboBox.clear()
        self.Nuclides_comboBox.clear()
        self.Scores_comboBox.clear()
        self.tabWidget_2.setCurrentIndex(0)
        self.sp_file = QtWidgets.QFileDialog.getOpenFileName(self,"Select The StatePoint File","~","statepoint*.h5")[0]
        self.lineEdit.setText(self.sp_file)
        self.Get_data_from_SP_file()
        self.lineLabel3.clear()

    def Get_data_from_SP_file(self):
        global sp
        self.Heating_LE.clear()
        self.Factor_LE.clear()
        try:
            for i in range(len(self.Bins_comboBox)):
                self.Bins_comboBox[i].hide()
        except:
            pass
        try:
            if os.path.isfile(self.sp_file):
                sp = openmc.StatePoint(self.sp_file)
                self.names = {}
                self.Nuclides = {}
                self.Scores = {}
                self.Estimator = {}                
                self.Tallies['tallies_ids'] = []
                self.Tallies['names'] = []
                self.meshes = {}
                _f = h5py.File(self.sp_file, 'r')
                self.tallies_group = _f['tallies']
                self.n_tallies = self.tallies_group.attrs['n_tallies']
                self.tally_ids = self.tallies_group.attrs['ids']
                self.filters_group = _f['tallies/filters']
                for tally_id in self.tally_ids:
                    tally = sp.get_tally(id=tally_id)  # Ok
                    name = tally.name
                    self.Tallies['tallies_ids'].append(tally_id)
                    self.Tallies['names'].append(name)
                    for score in tally.scores:
                        if score == 'heating':
                            heat = tally.mean.ravel()[0]
                            self.Heating_LE.setText(str(heat))
                # Read all meshes
                mesh_group = _f['tallies/meshes']
                # Iterate over all meshes
                for group in mesh_group.values():
                    mesh = openmc.MeshBase.from_hdf5(group)
                    self.meshes[mesh.id] = mesh
                self.Tally_id_comboBox.clear()
                self.Tally_id_comboBox.addItem("Select the tally's ID")

                self.Tallies_in_SP = list(sp.tallies.keys())
                if sp.run_mode == 'eigenvalue':
                    self.H = None
                    self.Tally_id_comboBox.addItem('Keff result')
                    self.batches = [i+1 for i in range(sp.n_batches)]
                    self.Keff_List = sp.k_generation.tolist()
                    self.keff = sp.keff.nominal_value
                    self.dkeff = sp.keff.std_dev
                    try:
                        self.H = sp.entropy.tolist()
                    except:
                        pass

                for key in self.Tallies_in_SP:
                    self.names[key] = []
                    self.Nuclides[key] = []
                    self.Scores[key] = []
                    self.Estimator[key] = []
                    text = str(sp.tallies[key]).split('\n')
                    for line in text:
                        if 'Name' in line:
                            name = line.split('=')[1].lstrip()
                            self.names[key].append(name)
                        if 'Nuclides' in line:
                            nuclide = line.split('=')[1].lstrip().split(' ')
                            self.Nuclides[key] = nuclide
                        if 'Scores' in line:
                            score1 = line.split('=')[1].lstrip().replace("'", "")
                            score = score1[score1.find('[') + 1: score1.find(']')].split(', ')
                            self.Scores[key] = [item for item in score]
                        if 'Estimator' in line:
                            estimator = line.split('=')[1].lstrip()
                            self.Estimator[key].append(estimator)
                    self.Tally_id_comboBox.addItem(str(key))
            else:
                pass
        except:
            pass

        self.lineLabel1.setText('Statepoint file : ' + self.sp_file)
        self.lineLabel2.setText('containing :  ' + str(self.n_tallies) + '  tallies')

    def Display_Tallies_Inf(self):
        self.Display = False
        self.Normalization = False
        print(self.tallies_group)
        if self.lineEdit.text():
            self.sp_file = self.lineEdit.text()
        if not os.path.isfile(self.sp_file):
            self.showDialog('Warning', 'Load valid sp file!')
            return
        self.editor1.clear()
        self.tabWidget_2.setCurrentIndex(1)
        if True:
            if os.path.isfile(self.sp_file):
                sp = openmc.StatePoint(self.sp_file)
                # print tallies summary
                self.editor1.insertPlainText('*'*57 + ' TALLIES SUMMARY ' + '*'*58 + '\n')
                for key in sp.tallies.keys():
                    self.editor1.insertPlainText(str(sp.tallies[key])+ '\n')
                self.editor1.insertPlainText('*'*134 + '\n')
                if sp.run_mode == 'eigenvalue':
                    # print Keff results
                    n = sp.n_batches
                    keff_glob = sp.global_tallies
                    INDEX = [str(idx,encoding='utf-8').ljust(25)  for idx in keff_glob['name']]
                    df = pd.DataFrame(keff_glob, index=INDEX, columns = ['name', 'mean', 'std_dev'])
                    for item in df['name']:
                        elem = str(item,encoding='utf-8').ljust(25)
                        df = df.replace({'name': item}, {'name': elem})
                    df.loc['Combined keff'] = ['Combined keff', self.keff, self.dkeff]
                    df.iloc[4], df.iloc[3] = df.iloc[3], df.iloc[4]
                    self.Print_Formated_df_Keff(df, self.editor1, '', 0)
                    # print Keff vs batches
                    self.batches = [i+1 for i in range(n)]
                    self.Keff_List = sp.k_generation.tolist()
                    df1 = pd.DataFrame({'batch': self.batches, 'Keff': self.Keff_List})
                    self.Print_Formated_df_Keff(df1, self.editor1, ' K EFFECTIVE VS BATCH ', 1)
                    try:    
                        self.H = sp.entropy.tolist()
                        df1 = pd.DataFrame({'batch': self.batches, 'Entropy': self.H}) 
                        self.Print_Formated_df_Keff(df1, self.editor1, '   SHANNON  ENTROPY   ', 1)
                    except:
                        pass
                # print tallies results
                _f = h5py.File(self.sp_file, 'r')
                self.tally_ids = self.tallies_group.attrs['ids']
                self.editor1.insertPlainText('*'*57 + ' TALLIES RESULTS ' + '*'*58 + '\n')
                for tally_id in self.tally_ids:
                    self.tally_id = tally_id
                    self.tally = sp.get_tally(id=tally_id)
                    df = self.tally.get_pandas_dataframe(float_format = '{:.2e}')  #'{:.6f}') 
                    self.Print_Formated_df(df.copy(), tally_id, self.editor1) 
            else:
                msg = 'Select your StatePoint file first !'
                self.showDialog('Warning', msg)
                return
        else:
            self.showDialog('Warning', 'Verify if OpenMC is installed !')
            return
        self.Tally_id_comboBox.setCurrentIndex(0)

    def Reset_Tally_CB(self):
        self.Tally_id_comboBox.setCurrentIndex(0)
        self.Tally_id_comboBox.clear()
        self.Tally_id_comboBox.addItem("Select the tally's ID")
        self.Plot_by_CB.clear()
        self.Filters_comboBox.clear()
        self.Nuclides_comboBox.clear()
        self.Scores_comboBox.clear()
        try:
            if os.path.isfile(self.lineEdit.text()):
                self.sp_file = self.lineEdit.text()
                sp = openmc.StatePoint(self.sp_file)
                if sp.run_mode == 'eigenvalue':
                    self.Tally_id_comboBox.addItem('Keff result')
                self.Tally_id_comboBox.addItems([str(tally) for tally in list(sp.tallies.keys())])
            else:
                pass
        except:
            return

    def Check_if_SP_file_exists(self):
        self.sp_file == self.lineEdit.text()
        if not os.path.isfile(self.sp_file):
            self.showDialog('Warning', 'Invalid path to stateppoint file!')
            self.Tally_id_comboBox.clear()
            self.Tally_id_comboBox.addItem("Select the tally's ID")
        else:
            pass

    def SelectTally(self):
        global power_items, Norm_Other
        tally_id = ''
        name = ''
        if self.lineEdit.text():
            self.sp_file = self.lineEdit.text()
        if not os.path.isfile(str(self.sp_file)):
            self.lineLabel1.setText("Current statepoint file : No valid statepoint file", 0)
            return
        self.score_plot_PB.setText('plot data')
        self.filters = []
        self.Bins = {}
        self.Tally_name_LE.clear()
        self.Curve_title.clear()
        self.Nuclides_List_LE.clear()
        self.Scores_List_LE.clear()
        self.Plot_by_CB.clear()
        self.Filters_comboBox.clear()
        self.Nuclides_comboBox.clear()
        self.Scores_comboBox.clear()
        self.Vol_List_LE.clear()
        for elm in self.buttons:
            elm.setEnabled(False)
        self.Graph_Layout_CB.setCurrentIndex(0)
        self.Graph_type_CB.setCurrentIndex(0)
        self.Graph_Layout_CB.setEnabled(False)
        self.score_plot_PB.setEnabled(False)
        self.xGrid_CB.setChecked(False)
        self.yGrid_CB.setChecked(False)
        self.MinorGrid_CB.setChecked(False)
        if self.Tally_id_comboBox.currentIndex() > 0 and 'Keff' not in self.Tally_id_comboBox.currentText():
            tally_id = int(self.Tally_id_comboBox.currentText())
            self.Filters_comboBox.clear()
            self.Scores_comboBox.clear()
            self.Nuclides_comboBox.clear()      
            idx = self.Tallies['tallies_ids'].index(tally_id)
            name = self.Tallies['names'][idx]
            self.Tally_name_LE.setText(name)
            self.Filters_comboBox.addItem('Select filter')
            self.Tallies[tally_id] = {}
            self.Tallies[tally_id]['id'] = [tally_id]
            self.Tallies[tally_id]['filter_ids'] = []
            self.Tallies[tally_id]['filter_types'] = []
            self.Tallies[tally_id]['filter_names'] = []
            self.tally = sp.get_tally(id=tally_id)
            group = self.tallies_group[f'tally {tally_id}']
            self.df = self.tally.get_pandas_dataframe()
            self.df_Keys = self.df.keys()[:-2].tolist()        
            self.n_filters = group['n_filters'][()]
            # hide comboBoxes in gridLayout_20
            for i in range(self.gridLayout_20.layout().count()):
                widget = self.gridLayout_20.layout().itemAt(i).widget()
                widget.hide()            
            # Read all filters
            if self.n_filters > 0:                  # filters are defined
                self.Bins_comboBox = [''] * self.n_filters
                for i in range(self.n_filters):
                    self.Bins_comboBox[i] = CheckableComboBox()
                    row = int(i / 3) + 1          
                    col = i + 4 - row * 3                
                    self.gridLayout_20.addWidget(self.Bins_comboBox[i], row , col)

                self.filter_ids = group['filters'][()].tolist()
                self.Tallies[tally_id]['filter_ids'] = self.filter_ids
                for filter_id in self.filter_ids:  
                    self.Tallies[tally_id][filter_id] = {}
                    self.Tallies[tally_id][filter_id]['Checked_bins_indices'] = []                  
                    self.Tallies[tally_id][filter_id]['Checked_bins'] = []                  
                    self.Tallies[tally_id][filter_id]['scores'] = []
                    filter_group = self.filters_group[f'filter {filter_id}']
                    new_filter = openmc.Filter.from_hdf5(filter_group, meshes=self.meshes)
                    filter_name = str(new_filter).split('\n')[0]
                    filter_type = filter_group['type'][()].decode()
                    self.Tallies[tally_id]['filter_types'] += [filter_type]
                    self.Tallies[tally_id]['filter_names'] += [filter_name]
                self.Filter_names = self.Tallies[tally_id]['filter_names']
                filters = [filter + ' , id= ' + str(id) for filter, id in zip(self.Tallies[tally_id]['filter_names'], self.filter_ids)]
                self.Filters_comboBox.addItems(filters)

                self.Filters_comboBox.setCurrentIndex(1)
                for i in range(len(self.Bins_comboBox)):
                    self.Bins_comboBox[i].currentIndexChanged.connect(self.SelectBins) 
                    self.Bins_comboBox[i].currentIndexChanged.connect(lambda:self.score_plot_PB.setEnabled(False)) 
                self.filters = self.Tallies[tally_id]['filter_types']
            else:                                    # no filter defined
                self.Tallies[tally_id]['scores'] = []
            # fill scores combobox
            self.scores = sorted(self.tally.scores)
            self.Tallies[tally_id]['scores'] = self.scores
            self.Scores_comboBox.clear()
            self.Scores_comboBox.addItem('Select score')
            if len(self.scores) > 1:
                self.Scores_comboBox.addItem('All scores')
            self.Scores_comboBox.addItems(self.scores)
            # fill nuclides combobox
            self.nuclides = self.tally.nuclides
            self.Tallies[tally_id]['nuclides'] = self.nuclides
            self.Nuclides_comboBox.clear()
            self.Nuclides_comboBox.addItem('Select nuclide')
            if len(self.nuclides) > 1:
                self.Nuclides_comboBox.addItems(['All nuclides'])
            self.Nuclides_comboBox.addItems(self.nuclides)
            self.Nuclides_comboBox.setCurrentIndex(1)
            if len(self.scores) == 1:
                self.Scores_List_LE.setText(self.scores[0]) 
            self.nuclides_display_PB.setEnabled(True)
            self.scores_display_PB.setEnabled(True)     
            self.label.setText('plot by')   
            self.Plot_by_CB.clear()
        elif self.Tally_id_comboBox.currentIndex() > 0 and 'Keff' in self.Tally_id_comboBox.currentText():
            self.Checked_batches = []
            self.Checked_batches_bins = []
            self.Tally_name_LE.setText('Keff vs batches')
            self.Filters_comboBox.clear()
            self.Filters_comboBox.addItem('Select filter')
            self.Filters_comboBox.addItem('Batches Filter')
            for i in reversed(range(self.gridLayout_20.count())): 
                self.gridLayout_20.itemAt(i).widget().setParent(None)   
            self.Bins_comboBox = ['']
            self.Bins_comboBox[0] = CheckableComboBox()
            self.gridLayout_20.addWidget(self.Bins_comboBox[0], 0, 0)
            self.Filters_comboBox.setCurrentIndex(1)
            self.SelectFilter()
            self.nuclides_display_PB.setEnabled(False)
            self.scores_display_PB.setEnabled(False)
            self.score_plot_PB.setEnabled(True)
            self.Graph_type_CB.setEnabled(True)
            self.Plot_by_CB.setEnabled(True)
            self.score_plot_PB.setText('plot Keff')
            for bt in self.buttons:
                bt.setEnabled(True)
            for i in [3, 4]:
                self.Graph_type_CB.model().item(i).setEnabled(True)
            for i in [1, 2, 5, 6]:
                self.Graph_type_CB.model().item(i).setEnabled(False)
            self.Bins_comboBox[0].currentIndexChanged.connect(self.SelectBins)
            self.Graph_type_CB.setCurrentIndex(3)
            self.Curve_title.setText(self.Tally_name_LE.text())
            self.Curve_xLabel.setText('batches')
            self.Curve_yLabel.setText('Keff')
            self.label.setText('plot') 
            self.Plot_by_CB.clear()
            self.Plot_by_CB.addItem('select item')
            if self.H:
                self.Plot_by_CB.addItems(['Keff', 'Keff & Shannon entropy', 'Shannon entropy'])
            else:
                self.Plot_by_CB.addItem('Keff')
            self.Plot_by_CB.setCurrentIndex(1)
        else:
            self.Tally_name_LE.clear()
            self.Curve_title.clear()
            self.Filters_comboBox.clear()
            try:
                for i in range(len(self.Bins_comboBox)):
                    self.Bins_comboBox[i].hide()
            except:
                pass            
            self.Plot_by_CB.setCurrentIndex(0)
            self.Graph_Layout_CB.setCurrentIndex(0)
            self.Graph_type_CB.setCurrentIndex(0)
            self.Graph_type_CB.setEnabled(False)

        power_items = [self.label_21, self.label_22, self.label_16, self.label_17, self.label_18, self.Nu_LE, 
                       self.Heating_LE, self.Keff_LE, self.Q_LE, self.Norm_to_Power_CB, self.Norm_to_Heating_CB, 
                       self.Power_LE, self.Factor_LE]
        Norm_Other = [self.label_37, self.label_19, self.label_23, self.Norm_to_BW_CB, self.Norm_to_Vol_CB, self.Norm_to_UnitLethargy_CB,
                      self.Norm_Bins_comboBox, self.Vol_List_LE]
        CBoxes = [self.Norm_to_BW_CB, self.Norm_to_Vol_CB, self.Norm_to_UnitLethargy_CB, self.Norm_to_Power_CB, self.Norm_to_Heating_CB]
        for item in power_items:
            item.setEnabled(False)
        for item in Norm_Other:
            item.setEnabled(False)
        for CB in CBoxes:
            CB.setChecked(False)
        self.Norm_Bins_comboBox.clear()
        
        if tally_id != '':
            self.lineLabel2.setText('Selected tally id : ' + str(tally_id))
            self.lineLabel3.setText('  Tally name : ' + name)
        #except:
        #pass

    def Display_tally(self):
        self.Display = False
        self.sp_file == self.lineEdit.text()
        self.Normalization = False
        self.tabWidget_2.setCurrentIndex(0)
        cursor = self.editor.textCursor()
        cursor.movePosition(cursor.End)
        if True:
            if os.path.isfile(self.sp_file):
                sp = openmc.StatePoint(self.sp_file)
                self.tabWidget_2.setCurrentIndex(0)
                if self.Tally_id_comboBox.currentIndex() > 0 and 'Keff' not in self.Tally_id_comboBox.currentText():
                    df = self.tally.get_pandas_dataframe(float_format = '{:.2e}')  #'{:.6f}')
                    tally_id = int(self.Tally_id_comboBox.currentText())
                    """cursor.insertText('*'*12*len(df.keys()) + ' TALLY SUMMARY ' + '*'*12*len(df.keys()) + '\n' +
                                        str(self.tally) + '\n\n' +
                                      '*'*12*len(df.keys()) + ' TALLY RESULTS ' + '*'*12*len(df.keys()) + '\n\n')
                    self.editor.setTextCursor(cursor)"""
                    self.Print_Formated_df(df.copy(), tally_id, self.editor)  
                elif self.Tally_id_comboBox.currentIndex() > 0 and 'Keff' in self.Tally_id_comboBox.currentText():
                    # print Keff results
                    n = sp.n_batches
                    keff_glob = sp.global_tallies
                    INDEX = [str(idx,encoding='utf-8').ljust(25)  for idx in keff_glob['name']]
                    df = pd.DataFrame(keff_glob, index=INDEX, columns = ['name', 'mean', 'std_dev'])
                    for item in df['name']:
                        elem = str(item,encoding='utf-8').ljust(25)
                        df = df.replace({'name': item}, {'name': elem})
                    df.loc['Combined keff'] = ['Combined keff', self.keff, self.dkeff]
                    df.iloc[4], df.iloc[3] = df.iloc[3], df.iloc[4]
                    self.Print_Formated_df_Keff(df, self.editor, '', 0)
                    # print Keff vs batches
                    df1 = pd.DataFrame({'batch': [i+1 for i in range(n)], 'Keff': sp.k_generation.tolist()})
                    self.Print_Formated_df_Keff(df1, self.editor, ' K EFFECTIVE VS BATCH ', 1)
                    try:
                        df1 = pd.DataFrame({'batch': [i+1 for i in range(n)], 'Entropy': sp.entropy.tolist()})
                        self.Print_Formated_df_Keff(df1, self.editor, '   SHANNON  ENTROPY   ', 1)
                    except:
                        pass
                else:
                    self.showDialog('Warning', 'Select Tally first!')
            else:
                self.showDialog('Warning', 'Select a valid StatePoint file first!')
                return
        else:
            return

    def Print_Formated_df(self, df, tally_id, editor):
        columns_header = []
        LTOT = 0
        for key in df.keys():
            if type(key) is tuple:  # and 'mesh' in key[0]:
                KEY = key[0]
                KEY1 = key[1]
            else:
                KEY = key
                KEY1 = ''
            if KEY1 in ['x', 'y', 'z']:   #'mesh' in key:
                pass
            if 'mesh' in KEY:
                FMT = '{:<20}'
            elif KEY in ['surface', 'cell', 'cellfrom', 'cellborn', 'universe', 'material', 'collision']:
                FMT = '{:<13d}'
            elif KEY in ['distribcell']:
                FMT = '{:<14d}'
            elif KEY in ['delayedgroup']:
                FMT = '{:<20d}'
            elif KEY in ['energy low [eV]', 'energy high [eV]', 'energyout low [eV]', 'energyout high [eV]', 
                       'polar low [rad]', 'polar high [rad]', 'azimuthal low [rad]',
                       'azimuthal high [rad]', 'time low [s]', 'time high [s]']:
                FMT = '{:<20.3e}'
            elif KEY in ['mu low', 'mu high', "mean", "std. dev."]:
                FMT = '{:<16.3e}'
            elif KEY in ['nuclide', 'particle', 'legendre', 'zernike']:
                FMT = '{:<14}'
            elif KEY in ['score', 'spatiallegendre', 'sphericalharmonics', 'zernikeradial']:
                FMT = '{:<20}'
            elif KEY in ['multiplier']:
                FMT = '{:<16.6e}'
            elif 'level' in KEY:
                FMT = '{:<10d}'
            df.loc[:, key] = df[key].map(FMT.format)
            if True:
                LJUST = int(FMT.split('<')[1].split('.')[0].replace('d', '').replace('}', ''))
            else:
                LJUST = 20
            LTOT += LJUST
            #for KEY in df.keys():    
            if type(KEY) is tuple:
                if 'mesh' in KEY[0]:
                    column_name = str(KEY[0] + ', ' + KEY[1]).ljust(LJUST)
                else:
                    column_name = KEY[0].ljust(LJUST)
            else:   
                column_name = KEY.ljust(LJUST)
            columns_header.append(column_name)

        LTOT += 30
        LTOT05 = int(LTOT / 1.5) 
        df.columns = columns_header             
        
        cursor = editor.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText('*'*LTOT + '\n')
        if self.Normalization:
            cursor.insertText('\n' + ' '*int(LTOT05 * 0.66) + 'Tally ' + str(tally_id) + ' results to be plotted after normalization\n' + '\n')
        else:
            if self.Display:
                cursor.insertText('\n' + ' '*int(LTOT05 * 0.7) + 'Tally ' + str(tally_id) + ' results to be plotted\n' + '\n')
            else:
                cursor.insertText('\n\n' + '*'*int(LTOT05 * 0.66) + ' TALLY SUMMARY ' + '*'*int(LTOT05 * 0.66) + '\n\n')
                cursor.insertText(str(self.tally) + '\n\n') 
                cursor.insertText('*'*int(LTOT05 * 0.66) + ' TALLY RESULTS ' + '*'*int(LTOT05 * 0.66) + '\n\n\n')
                cursor.insertText(' '*LTOT05 + 'Tally id : ' + str(tally_id) + '\n')
        
        cursor.insertText('*'*LTOT + '\n')
        cursor.insertText(df.to_csv(sep='\t', index=False)) 
        cursor.insertText('*'*LTOT + '\n\n')
        editor.setTextCursor(cursor)

    def Print_Formated_df_Keff(self, df, editor, TITLE, j):
        cursor = editor.textCursor()
        cursor.movePosition(cursor.End)

        if j == 0:
            cursor.insertText('*'*60 + ' K EFFECTIVE ' + '*'*60 + '\n')
            for key in df.keys():
                if key in ['mean', 'std_dev']:
                    df.loc[:, key] = df[key].map('{:<20.6f}'.format)
        elif j == 1:
            cursor.insertText('*'*55 + TITLE + '*'*55 + '\n')
            for key in df.keys():
                if 'batch' in key:
                    df.loc[:, key] = df[key].map('{:d}'.format)
                elif 'Keff' in key or 'Entropy' in key:
                    df.loc[:, key] = df[key].map('{:<20.6f}'.format)
        columns_header = [column_name for column_name in df.keys()]
        df.columns = columns_header  
                      
        cursor.insertText(df.to_csv(sep='\t', index=False)) 
        cursor.insertText('*'*134 + '\n')
        editor.setTextCursor(cursor)

    def SelectFilter(self):
        for elm in self.buttons:
            elm.setEnabled(False)
        self.Graph_Layout_CB.setEnabled(False)
        self.score_plot_PB.setEnabled(False)
        self.Mesh_xy_RB.hide()
        self.Mesh_xz_RB.hide()
        self.Mesh_yz_RB.hide()
        self.spinBox.hide()
        self.spinBox_2.hide()
        self.xlabel.setText('xlabel')
        self.ylabel.setText('ylabel')
        self.score_plot_PB.setText('plot data')
        self.Curve_xLabel.clear()
        self.Curve_yLabel.clear()
        self.Curve_title.clear()

        if self.Tally_id_comboBox.currentIndex() > 0 and 'Keff' not in self.Tally_id_comboBox.currentText():
            tally_id = int(self.Tally_id_comboBox.currentText())
            self.tally = sp.get_tally(id=tally_id)
            tally = self.tally 
            try:
                for idx in range(self.n_filters):
                    self.Bins_comboBox[idx].clear()
            except:
                pass

            if self.Filters_comboBox.currentIndex() > 0:
                for idx in range(self.n_filters):
                    filter_name = self.Tallies[tally_id]['filter_names'][idx]
                    self.label_4.setText('Select bins')
                    filter_id = self.filter_ids[idx]
                    self.Tallies[tally_id][filter_id]['bins'] = [item for item in tally.filters[idx].bins]
                    Bins = self.Tallies[tally_id][filter_id]['bins']
                    if 'MeshFilter' in self.Filters_comboBox.currentText():
                        self.Mesh_xy_RB.show()
                        self.Mesh_xz_RB.show()
                        self.Mesh_yz_RB.show()
                        self.spinBox.show()
                        self.spinBox_2.show()
                        self.Mesh_xy_RB.setChecked(True)
                        self.Curve_xLabel.setText('x/cm')
                        self.Curve_yLabel.setText('y/cm')
                        self.Curve_title.setText(self.Tally_name_LE.text())
                        self.mesh_id = tally.filters[0].mesh.id
                        self.mesh_type = str(tally.filters[0].mesh).split('\n')[0]
                        
                        self.mesh_name = tally.name
                        self.mesh_dimension = tally.filters[0].mesh.dimension
                        self.mesh_n_dim = tally.filters[0].mesh.n_dimension    

                        
                        print('Meshes : ', tally.filters[0].mesh)
                        print('*******************************************************************************************')
                        print('********************                           Mesh summary                             ******************')
                        print('*******************************************************************************************\n')
                        if self.mesh_type == 'RectilinearMesh':
                            self.mesh_LL = (tally.filters[0].mesh.x_grid[0], tally.filters[0].mesh.y_grid[0], tally.filters[0].mesh.z_grid[0],)
                            self.mesh_UR = (tally.filters[0].mesh.x_grid[-1], tally.filters[0].mesh.y_grid[-1], tally.filters[0].mesh.z_grid[-1],)                        
                            print('id               :  ', self.mesh_id)
                            print('name            :  ', self.mesh_name)
                            print('type            :  ', self.mesh_type)
                            print('dimension     :  ', self.mesh_n_dim)
                            print('voxels          :  ', self.mesh_dimension)
                            print('lower_left   :  ', self.mesh_LL)
                            print('upper_right  :  ', self.mesh_UR, '\n')
                            print('Tally filters : ', tally.filters, '\n')
                            print('*******************************************************************************************\n')
                            
                        else:                  #self.mesh_type == 'RegularMesh':
                            self.mesh_width = tally.filters[0].mesh.width
                            self.mesh_LL = tally.filters[0].mesh.lower_left
                            self.mesh_UR = tally.filters[0].mesh.upper_right

                            self.mesh_ids = tally.filters[0].bins
                            if len(tally.filters[0].mesh._grids) == 3:
                                self.x = tally.filters[0].mesh._grids[0][:-1] + tally.filters[0].mesh.width[0] * 0.5
                                self.y = tally.filters[0].mesh._grids[1][:-1] + tally.filters[0].mesh.width[1] * 0.5
                                self.z = tally.filters[0].mesh._grids[2][:-1] + tally.filters[0].mesh.width[2] * 0.5  
                                self.Mesh_xz_RB.setEnabled(True) 
                                self.Mesh_yz_RB.setEnabled(True) 
                            else:
                                self.x = tally.filters[0].mesh._grids[0][:-1] + tally.filters[0].mesh.width[0] * 0.5
                                self.y = tally.filters[0].mesh._grids[1][:-1] + tally.filters[0].mesh.width[1] * 0.5
                                self.z = ['z axis integrated']
                                self.mesh_dimension = np.append(self.mesh_dimension, 1)
                                self.Mesh_xz_RB.setEnabled(False) 
                                self.Mesh_yz_RB.setEnabled(False)   
                            # ******************************************************************************                     
                            print('id                :  ', self.mesh_id)
                            print('name          :  ', self.mesh_name)
                            print('type            :  ', self.mesh_type)
                            print('dimension   :  ', self.mesh_n_dim)
                            print('voxels         :  ', self.mesh_dimension)
                            print('width          :  ', self.mesh_width)
                            print('lower_left     :  ', self.mesh_LL)
                            print('upper_right  :  ', self.mesh_UR, '\n')
                            print('x grid      :  ', self.x)
                            print('y grid      :  ', self.y)
                            print('z grid      :  ', self.z, '\n')
                            print('Tally filters : ', tally.filters, '\n')
                            print('*******************************************************************************************\n')

                            self.Tallies[tally_id][filter_id]['slice_x'] = self.x
                            self.Tallies[tally_id][filter_id]['slice_y'] = self.y
                            self.Tallies[tally_id][filter_id]['slice_z'] = self.z
                            self.id_step = self.mesh_dimension[0] * self.mesh_dimension[1]
                            ij_indices = [(self.mesh_ids[i][0], self.mesh_ids[i][1],) for i in range(self.id_step)]
                            if len(tally.filters[0].mesh._grids) == 3:   
                                ik_indices = []
                                for k in range(self.mesh_dimension[2]):
                                    ik_indices += [(self.mesh_ids[i][0], self.mesh_ids[i][2],) for i in
                                                range(k * self.id_step, (k * self.id_step + self.mesh_dimension[0]))]
                                jk_indices = [(self.mesh_ids[i][1], self.mesh_ids[i][2],) for i in
                                            range(0, len(self.mesh_ids), self.mesh_dimension[0])]
                                self.Tallies[tally_id][filter_id]['ik_indices'] = ik_indices
                                self.Tallies[tally_id][filter_id]['jk_indices'] = jk_indices
                                
                            self.Tallies[tally_id][filter_id]['ij_indices'] = ij_indices
                            
                            if self.Mesh_xy_RB.isChecked():
                                if len(tally.filters[0].mesh._grids) == 3:
                                    self.z_id = [item[2] for item in [self.mesh_ids[i] for i in range(0, len(self.mesh_ids), self.id_step)]]
                                    self.list_axis = ['slice at z = ' + str("{:.1E}".format(z_)) for z_ in self.z]
                                else:
                                    self.z_id = [0]
                                    self.list_axis = ['z axis integrated']
                                #self.Tallies[tally_id][filter_id]['basis'] = [(x, y,) for y in self.y for x in self.y]
                                #self.Tallies[tally_id][filter_id]['basis_ids'] = [(i, j,) for i,j in zip(self.mesh_ids[0], self.mesh_ids[1])]
                            elif self.Mesh_xz_RB.isChecked():
                                self.id_step1 = self.mesh_dimension[0] * self.mesh_dimension[2]
                                self.y_id = [item[2] for item in [self.mesh_ids[i] for i in range(0, len(self.mesh_ids), self.id_step)]]
                                self.list_axis = ['slice at y = ' + str("{:.1E}".format(y_)) for y_ in self.y]
                                #self.Tallies[tally_id][filter_id]['basis'] = [(x, z,) for z in self.z for x in self.x]
                            elif self.Mesh_yz_RB.isChecked():
                                self.id_step2 = self.mesh_dimension[1] * self.mesh_dimension[2]
                                self.x_id = [item[2] for item in [self.mesh_ids[i] for i in range(0, len(self.mesh_ids), self.id_step)]]
                                self.list_axis = ['slice at x = ' + str("{:.1E}".format(x_)) for x_ in self.x]
                                #self.Tallies[tally_id][filter_id]['basis'] = [(y, z,) for z in self.z for y in self.y]
                            bins = self.list_axis  
                    else: 
                        self.Mesh_xy_RB.hide()
                        self.Mesh_xz_RB.hide()
                        self.Mesh_yz_RB.hide()
                        self.spinBox.hide()
                        self.spinBox_2.hide()
                        self.Curve_title.clear()                     
                        self.xlabel.setText('xlabel')
                        self.ylabel.setText('ylabel')
                        if 'energy low [eV]' in self.df_Keys and filter_name == 'EnergyFilter':
                            first = [item[0] for item in Bins]
                            last = [item[1] for item in Bins]
                            self.Checked_energies_Low = first
                            self.Checked_energies_High = last
                            bins = [str(("{:.3E}".format(x), "{:.3E}".format(y),)).replace("'", "") for x, y in
                                    zip(first, last)]
                        elif 'energyout low [eV]' in self.df_Keys and filter_name == 'EnergyoutFilter':                            
                            first = [item[0] for item in Bins]
                            last = [item[1] for item in Bins]
                            self.Checked_energiesout_Low = first
                            self.Checked_energiesout_High = last
                            bins = [str(("{:.3E}".format(x), "{:.3E}".format(y),)).replace("'", "") for x, y in
                                    zip(first, last)]
                        elif 'mu low' in self.df_Keys and filter_name == 'MuFilter':
                            first = [item[0] for item in Bins]
                            last = [item[1] for item in Bins]
                            self.Checked_mu_Low = first
                            self.Checked_mu_High = last
                            bins = [str(("{:.3f}".format(x), "{:.3f}".format(y),)).replace("'", "") for x, y in
                                    zip(first, last)]
                        elif 'polar low [rad]' in self.df_Keys and filter_name == 'PolarFilter':
                            first = [item[0] for item in Bins]
                            last = [item[1] for item in Bins]
                            self.Checked_polar_Low = first
                            self.Checked_polar_High = last
                            bins = [str(("{:.3f}".format(x), "{:.3f}".format(y),)).replace("'", "") for x, y in
                                    zip(first, last)]
                        elif 'azimuthal low [rad]' in self.df_Keys and filter_name == 'AzimuthalFilter':
                            first = [item[0] for item in Bins]
                            last = [item[1] for item in Bins]
                            self.Checked_azimuthal_Low = first
                            self.Checked_azimuthal_High = last
                            bins = [str(("{:.3f}".format(x), "{:.3f}".format(y),)).replace("'", "") for x, y in
                                    zip(first, last)]
                        elif 'time low [s]' in self.df_Keys and filter_name == 'TimeFilter':
                            first = [item[0] for item in Bins]
                            last = [item[1] for item in Bins]
                            self.Checked_time_Low = first
                            self.Checked_time_High = last
                            bins = [str(("{:.3f}".format(x), "{:.3f}".format(y),)).replace("'", "") for x, y in
                                    zip(first, last)]
                        else:
                            for KEY in self.df_Keys:
                                if 'distribcell' in KEY[0] and filter_name == 'DistribcellFilter':
                                    bins = [str(item) for item in range(len(self.tally.mean))]
                                if KEY in ['cell', 'cellfrom', 'cellborn', 'surface', 'universe', 'material', 
                                           'collision', 'particle', 'legendre', 'spatiallegendre', 
                                           'sphericalharmonics', 'delayedgroup', 'zernike', 'zernikeradial']:
                                    self.Curve_title.setText(self.Tally_name_LE.text())
                                    bins = sorted([str(item) for item in Bins])

                    self.Tallies[tally_id][filter_id]['bins'] = bins
                    self.Bins_comboBox[idx].addItem('Select ' + self.Tallies[tally_id]['filter_names'][idx] + ' bins')
                    self.Bins_comboBox[idx].addItem('All bins')
                    self.Bins_comboBox[idx].model().item(0).setEnabled(False)
                    #self.Bins_comboBox[idx].setItemChecked(0, False)
                    self.Bins_comboBox[idx].addItems(bins)
                    if 'MeshFilter' in self.Filters_comboBox.currentText() and len(tally.filters[0].mesh._grids) == 2:
                        self.Bins_comboBox[self.Filters_comboBox.currentIndex() - 1].setCurrentIndex(2)
                    try:
                        if self.Tallies[tally_id][filter_id]['Checked_bins_indices']:

                            for j in self.Tallies[tally_id][filter_id]['Checked_bins_indices']: 
                                self.Bins_comboBox[idx].setItemChecked(j, False)   # (j, True)
                        else:
                            for i in range(len(bins) + 1):
                                self.Bins_comboBox[idx].setItemChecked(i, False)
                    except:
                        self.showDialog('Warning', 'Filter bins not checked!')
            
        elif self.Tally_id_comboBox.currentIndex() > 0 and 'Keff' in self.Tally_id_comboBox.currentText():
            try:
                self.Bins_comboBox[0].clear()
            except:
                pass
            if self.Filters_comboBox.currentIndex() > 0:
                self.Bins_comboBox[0].addItem('Select batches')               
                self.Bins_comboBox[0].model().item(0).setEnabled(False)            
                self.Bins_comboBox[0].addItem('All bins')
                self.Bins_comboBox[0].addItems([str(i) for i in self.batches])

                for bt in self.buttons:
                    bt.setEnabled(True) 
                self.score_plot_PB.setEnabled(True)
                self.Curve_title.setText(self.Tally_name_LE.text())
                self.Curve_xLabel.setText('batches')
                self.Curve_yLabel.setText('Keff')
                self.Graph_type_CB.setEnabled(True)
                try:
                    if self.Checked_batches_bins:
                        for j in self.Checked_batches_bins: 
                            self.Bins_comboBox[0].setItemChecked(j, False)
                    else:
                        for i in range(len(self.batches) + 1):
                            self.Bins_comboBox[0].setItemChecked(i, False)
                except:
                    self.showDialog('Warning', '** Filter bins not checked!')
            else:
                self.Graph_type_CB.setEnabled(False)
                try:
                    self.Bins_comboBox[0].clear()
                except:
                    pass

    def Display_filters(self):
        self.tabWidget_2.setCurrentIndex(0)
        cursor = self.editor.textCursor()
        cursor.movePosition(cursor.End)
        
        if os.path.isfile(self.sp_file):
            if self.Tally_id_comboBox.currentIndex() > 0 and 'Keff' not in self.Tally_id_comboBox.currentText():
                tally_id = int(self.Tally_id_comboBox.currentText())
                if self.Filters_comboBox.currentIndex() > 0:
                    for id in self.filter_ids:
                        Filter_Type = self.Tallies[tally_id]['filter_types'][self.filter_ids.index(id)]
                        filter_id = id  
                        self.Filter_Bins_Select(tally_id, filter_id)
                        cursor.insertText('\n************************************************************' +
                            '\nTally Id            : ' + str(tally_id) +
                            '\nFilter Id           : ' + str(filter_id) +
                            '\nFilter type         : ' + Filter_Type +    
                            '\nChecked bins        : ' + str(self.Tallies[tally_id][filter_id]['Checked_bins']).replace("'", "") +
                            '\nChecked bins indices: ' + str(self.checked_bins_indices) +
                            '\n************************************************************')
            elif self.Tally_id_comboBox.currentIndex() > 0 and 'Keff' in self.Tally_id_comboBox.currentText():
                self.Filter_Bins_Select(0, 0)
                cursor.insertText('\n************************************************************' +
                    '\nKeff vs batches' +            
                    '\nChecked batches     : ' + str(self.Checked_batches) +
                    '\nChecked batches bins: ' + str(self.Checked_batches_bins) +
                    '\n************************************************************')
                self.Bins_comboBox[0].setCurrentIndex(0)  
            else:
                self.showDialog('Warning', 'Select Tally first!')
        else:
            self.showDialog('Warning', 'Select your StatePoint file first !')

        self.editor.setTextCursor(cursor)

    def SelectBins(self):
        if self.Tally_id_comboBox.currentIndex() > 0 and 'Keff' not in self.Tally_id_comboBox.currentText():
            tally_id = int(self.Tally_id_comboBox.currentText())
            self.tally = sp.get_tally(id=tally_id)
            _f = h5py.File(self.sp_file, 'r')
            tallies_group = _f['tallies']
            group = tallies_group[f'tally {tally_id}']
            self.n_filters = group['n_filters'][()]
            tally = self.tally
            for idx in range(self.n_filters):   
                if self.Filters_comboBox.currentIndex() > 0:
                    filter_id = self.filter_ids[idx]
                    if 'MeshFilter' in self.Filters_comboBox.currentText():
                        if self.Mesh_xy_RB.isChecked():
                            if len(tally.filters[0].mesh._grids) == 3:
                                z = self.z[self.Bins_comboBox[self.Filters_comboBox.currentIndex() - 1].currentIndex()-2]
                            else:
                                z = self.z[0]
                            self.xyz = [(x, y) + (z,) for y in self.y[:self.mesh_dimension[1]] for x in self.x[:self.mesh_dimension[0]]]
                        if self.Mesh_xz_RB.isChecked():
                            y = self.y[self.Bins_comboBox[self.Filters_comboBox.currentIndex() - 1].currentIndex()-2]
                            self.xyz = [(x,) + (y,) + (z,) for z in self.z[:self.mesh_dimension[1]] for x in self.x[:self.mesh_dimension[0]]]
                        if self.Mesh_yz_RB.isChecked():
                            x = self.x[self.Bins_comboBox[self.Filters_comboBox.currentIndex() - 1].currentIndex()-2]
                            self.xyz = [(x,) + (y, z) for z in self.z[:self.mesh_dimension[1]] for y in self.y[:self.mesh_dimension[0]]]
                    self.Filter_Bins_Select(tally_id, filter_id)
                    self.Bins_comboBox[idx].setCurrentIndex(0)
        elif self.Tally_id_comboBox.currentIndex() > 0 and 'Keff' in self.Tally_id_comboBox.currentText():
            self.Filter_Bins_Select(0, 0)
            self.Bins_comboBox[0].setCurrentIndex(0)
            
    def Filter_Bins_Select(self, tally_id, filter_id):
        try:
            if tally_id == 0 and filter_id == 0:
                if self.Bins_comboBox[0].currentIndex() == 1:
                    if self.Bins_comboBox[0].checkedItems():
                        self.Checked_batches_bins = self.Bins_comboBox[0].checkedItems()
                    else:
                        self.Checked_batches_bins = []
                    if self.Checked_batches_bins:
                        self.Checked_batches_bins.pop(0)
                elif self.Bins_comboBox[0].currentIndex() > 1:
                    self.Checked_batches_bins = self.Bins_comboBox[0].checkedItems()
                self.Checked_batches = [elm for elm in self.batches if self.batches.index(elm) + 2 in self.Checked_batches_bins]
            else:
                idx = self.filter_ids.index(filter_id)
                filter_name = self.Tallies[tally_id]['filter_names'][idx]
                if self.Bins_comboBox[idx].currentIndex() == 1:
                    if self.Bins_comboBox[idx].checkedItems():
                        self.Tallies[tally_id][filter_id]['Checked_bins_indices'] = self.Bins_comboBox[idx].checkedItems()
                    else:
                        self.Tallies[tally_id][filter_id]['Checked_bins_indices'] = []
                        self.Tallies[tally_id][filter_id]['bin'] = []
                    if self.Tallies[tally_id][filter_id]['Checked_bins_indices']:
                        self.Tallies[tally_id][filter_id]['Checked_bins_indices'].pop(0)
                elif self.Bins_comboBox[idx].currentIndex() > 1:
                    self.Tallies[tally_id][filter_id]['Checked_bins_indices'] = self.Bins_comboBox[idx].checkedItems()
                indices = self.Tallies[tally_id][filter_id]['Checked_bins_indices']
                lst = self.Tallies[tally_id][filter_id]['bins']
                self.Tallies[tally_id][filter_id]['Checked_bins'] = [elm for elm in lst if lst.index(elm) + 2 in indices]
                self.checked_bins_indices = self.Tallies[tally_id][filter_id]['Checked_bins_indices']

                if 'MeshFilter' in self.Filters_comboBox.currentText():
                    self.Tallies[tally_id][filter_id]['ijk_indices'] = {}
                    if self.Mesh_xy_RB.isChecked():
                        for bin_id in range(len(self.checked_bins_indices)):
                            self.Tallies[tally_id][filter_id]['ijk_indices'][self.checked_bins_indices[bin_id]] = []
                            k = self.checked_bins_indices[bin_id]
                            ijk_indices = [item + (k,) for item in self.Tallies[tally_id][filter_id]['ij_indices']]
                            self.Tallies[tally_id][filter_id]['ijk_indices'][self.checked_bins_indices[bin_id]] = ijk_indices
                    elif self.Mesh_xz_RB.isChecked():
                        for bin_id in range(len(self.checked_bins_indices)):
                            self.Tallies[tally_id][filter_id]['ijk_indices'][self.checked_bins_indices[bin_id]] = []
                            j = self.checked_bins_indices[bin_id]
                            ijk_indices = [item[:1] + (j,) + item[1:] for item in self.Tallies[tally_id][filter_id]['ij_indices']]
                            self.Tallies[tally_id][filter_id]['ijk_indices'][self.checked_bins_indices[bin_id]] = ijk_indices
                    elif self.Mesh_yz_RB.isChecked():
                        for bin_id in range(len(self.checked_bins_indices)):
                            self.Tallies[tally_id][filter_id]['ijk_indices'][self.checked_bins_indices[bin_id]] = []
                            i = self.checked_bins_indices[bin_id]
                            ijk_indices = [(i,) + item for item in self.Tallies[tally_id][filter_id]['ij_indices']]
                            self.Tallies[tally_id][filter_id]['ijk_indices'][self.checked_bins_indices[bin_id]] = ijk_indices
                else:
                    if 'cell' in self.df_Keys and filter_name == 'CellFilter':
                        self.Checked_cells = self.Tallies[tally_id][filter_id]['Checked_bins']
                    if 'cellfrom' in self.df_Keys and filter_name == 'CellFromFilter':
                        self.Checked_cellsfrom = self.Tallies[tally_id][filter_id]['Checked_bins']
                    if 'cellborn' in self.df_Keys and filter_name == 'CellBornFilter':
                        self.Checked_cellsborn = self.Tallies[tally_id][filter_id]['Checked_bins']
                    if 'distribcell' in self.df_Keys and filter_name == 'DistribcellFilter':
                        self.Checked_distribcell = self.Tallies[tally_id][filter_id]['Checked_bins'] 
                    if 'surface' in self.df_Keys and filter_name == 'SurfaceFilter':
                        self.Checked_surfaces = self.Tallies[tally_id][filter_id]['Checked_bins']
                    if 'energy low [eV]' in self.df_Keys and filter_name == 'EnergyFilter':
                        self.Checked_energies_Low = self.Tallies[tally_id][filter_id]['Checked_bins']
                    if 'energyout low [eV]' in self.df_Keys and filter_name == 'EnergyoutFilter':
                        self.Checked_energiesout_Low = self.Tallies[tally_id][filter_id]['Checked_bins']
                    if 'mu low' in self.df_Keys and filter_name == 'MuFilter':
                        self.Checked_mu_Low = self.Tallies[tally_id][filter_id]['Checked_bins']
                    if 'universe' in self.df_Keys and filter_name == 'UniverseFilter':
                        self.Checked_universes = self.Tallies[tally_id][filter_id]['Checked_bins']
                    if 'material' in self.df_Keys and filter_name == 'MaterialFilter':
                        self.Checked_materials = self.Tallies[tally_id][filter_id]['Checked_bins']
                    if 'collision' in self.df_Keys and filter_name == 'CollisionFilter':
                        self.Checked_collisions = self.Tallies[tally_id][filter_id]['Checked_bins']
                    if 'particle' in self.df_Keys and filter_name == 'ParticleFilter':
                        self.Checked_particles = self.Tallies[tally_id][filter_id]['Checked_bins']
                    if 'polar low [rad]' in self.df_Keys and filter_name == 'PolarFilter':
                        self.Checked_polar_Low = self.Tallies[tally_id][filter_id]['Checked_bins']
                    if 'azimuthal low [rad]' in self.df_Keys and filter_name == 'AzimuthalFilter':
                        self.Checked_azimuthal_Low = self.Tallies[tally_id][filter_id]['Checked_bins']
                    if 'legendre' in self.df_Keys and filter_name == 'LegendreFilter':
                        self.Checked_legendre = self.Tallies[tally_id][filter_id]['Checked_bins']
                    if 'spatiallegendre' in self.df_Keys and filter_name == 'SpatialLegendreFilter':
                        self.Checked_spatiallegendre = self.Tallies[tally_id][filter_id]['Checked_bins']
                    if 'sphericalharmonics' in self.df_Keys and filter_name == 'SphericalHarmonicsFilter':
                        self.Checked_sphericalharmonics = self.Tallies[tally_id][filter_id]['Checked_bins']
                    if 'time' in self.df_Keys and filter_name == 'TimeFilter':
                        self.Checked_times = self.Tallies[tally_id][filter_id]['Checked_bins']
                    if 'delayedgroup' in self.df_Keys and filter_name == 'DelayedGroupFilter':
                        self.Checked_delayed = self.Tallies[tally_id][filter_id]['Checked_bins']
                    if 'zernike' in self.df_Keys and filter_name == 'ZernikeFilter':
                        self.Checked_zernike = self.Tallies[tally_id][filter_id]['Checked_bins']
                    if 'zernikeradial' in self.df_Keys and filter_name == 'ZernikeRadialFilter':
                        self.Checked_zernikeradial = self.Tallies[tally_id][filter_id]['Checked_bins']
        except:
            return

    def SelectScores(self):        
        if self.Tally_id_comboBox.currentIndex() > 0 and 'Keff' not in self.Tally_id_comboBox.currentText():
            tally_id = int(self.Tally_id_comboBox.currentText())
            if self.Scores_comboBox.currentIndex() > 0:
                if self.Scores_comboBox.currentText() == 'All scores':
                    selected_score = self.scores
                else:
                    selected_score = list(filter(None, self.Scores_List_LE.text().split(' ')))
                    selected_score.append(str(self.Scores_comboBox.currentText()))
                selected_score = sorted(selected_score)
                self.selected_scores = list(dict.fromkeys(selected_score))
                text = ' '.join(self.selected_scores)
                self.Scores_List_LE.clear()
                self.Scores_List_LE.setText(text)

    def SelectNuclides(self):
        if self.Tally_id_comboBox.currentIndex() > 0 and 'Keff' not in self.Tally_id_comboBox.currentText():
            tally_id = int(self.Tally_id_comboBox.currentText())
            if self.Nuclides_comboBox.currentIndex() > 0:
                if self.Nuclides_comboBox.currentText() == 'All nuclides':
                    selected_nuclides = self.nuclides
                    self.Nuclides_List_LE.setText(str([nuclide for nuclide in selected_nuclides]))
                else:
                    selected_nuclides = list(filter(None, self.Nuclides_List_LE.text().split(' ')))
                    selected_nuclides.append(str(self.Nuclides_comboBox.currentText()))
                selected_nuclides = sorted(selected_nuclides)
                self.selected_nuclides = list(dict.fromkeys(selected_nuclides))
                text = ' '.join(selected_nuclides)
                self.Nuclides_List_LE.clear()
                self.Nuclides_List_LE.setText(text)
                self.Tallies[tally_id]['selected_nuclides'] = selected_nuclides

    def Clear_nuclides(self):
        self.Nuclides_List_LE.clear()
        self.Nuclides_comboBox.setCurrentIndex(0)

    def Display_scores(self):
        self.Display = True
        self.Normalization = False
        if not self.sp_file:
            self.showDialog('Warning', 'Select a valid StatePoint file first!')
            return
        if self.Tally_id_comboBox.currentIndex() == 0: 
            self.showDialog('Warning', "Select tally's id first !")
            return

        self.tally_id = int(self.Tally_id_comboBox.currentText())

        if self.n_filters == 0:                                   # scores are not filtered
            self.filter_ids = [0]
            self.filter_id = 0               
        else:                                 # scores are filtered 
            if self.Filters_comboBox.currentIndex() == 0: 
                self.showDialog('Warning', "Select filter's id first !")
                return            
            for id in self.filter_ids:
                self.filter_id = id
                if not self.Tallies[self.tally_id][self.filter_id]['Checked_bins_indices']:
                    self.showDialog('Warning', 'Check filter bins first !')
                    return
        
        if not self.Nuclides_List_LE.text().strip():
            self.showDialog('Warning', 'Select nuclides first!')
            return
        if not self.Scores_List_LE.text().strip():
            self.showDialog('Warning', 'Select score first!')
            return     

        self.tabWidget_2.setCurrentIndex(0)
        self.Graph_Layout_CB.setEnabled(True)
        self.Graph_Layout_CB.setCurrentIndex(0)
        self.Add_error_bars_CB.setChecked(False) 
               
        df = self.tally.get_pandas_dataframe(float_format = '{:.3e}')  #'{:.6f}')
        
        self.df = df.sort_values(by=df.keys().tolist()[:-2])  #[::-1])
        # list of selected nuclides
        self.selected_nuclides = list(filter(None, self.Nuclides_List_LE.text().split(' ')))
        self.selected_nuclides = sorted(self.selected_nuclides)
        self.selected_nuclides = list(dict.fromkeys(self.selected_nuclides))
        for elm in self.selected_nuclides:
            if elm not in self.nuclides:
                self.showDialog('Warning', 'nuclide : ' + str(elm) + ' not tallied for current tally!')
                return
        self.Tallies[self.tally_id]['selected_nuclides'] = self.selected_nuclides        
        # list of selected scores
        self.selected_scores = list(filter(None, self.Scores_List_LE.text().split(' ')))
        self.selected_scores = sorted(self.selected_scores)
        self.selected_scores = list(dict.fromkeys(self.selected_scores))
        for elm in self.selected_scores:
            if elm not in self.scores:
                self.showDialog('Warning', 'score : ' + str(elm) + ' not tallied for current tally!')
                return
        self.Tallies[self.tally_id]['selected_scores'] = self.selected_scores

        self.Plot_by_CB.clear()
        self.Plot_by_CB.addItem('select item')
        if self.n_filters == 0:                                   # scores are not filtered
            self.Unfiltered_Scores()
            self.Deactivate_Curve_Type()
            self.Curve_xLabel.setText('Nuclides')        
        elif self.n_filters >= 1:                                 # scores are filtered 
           self.Display_scores_2()
        
        # add keys to Plot_by_CB combobox
        if 'distribcell' in self.df.keys():    #  to be revised
            self.Plot_by_CB.addItem('distribcell')   
            self.Graph_type_CB.addItem('mesh graph')
            # to be modified if ploting works
            index = self.Graph_type_CB.findText('mesh graph')
            self.Graph_type_CB.model().item(index).setEnabled(False)
                
        index = self.Graph_type_CB.findText('mesh graph')
        self.Graph_type_CB.removeItem(index)
        for item in self.df_Keys:
            if 'surface' in self.df_Keys:
                if 'high' in item:
                    self.Plot_by_CB.addItem(item.split(' ')[0] + ' center of bin')
                else:
                    if item != 'nuclide': self.Plot_by_CB.addItem(str(item)) 
            else:  
                if 'high' in item:
                    self.Plot_by_CB.addItem(item.split(' ')[0] + ' center of bin')
                else:
                    self.Plot_by_CB.addItem(str(item))

        self.Curve_title.setText(self.Tally_name_LE.text())

        if 'MeshFilter' not in self.Filters_comboBox.currentText():
            if len(self.selected_scores) == 1: 
                if self.selected_scores[0] == 'flux':
                    self.Curve_yLabel.setText(self.selected_scores[0] + ' / cm ')
                else:
                    self.Curve_yLabel.setText(self.selected_scores[0])
            else:
                self.Curve_yLabel.setText('Tallies')
        
        cursor = self.editor.textCursor()
        cursor.movePosition(cursor.End)

        cursor.insertText('\n' + '*'*27*len(df.keys()) + '\n')
        cursor.insertText(' '*87 + ' tally id : ' + str(self.tally_id))
        cursor.insertText('\n' + '*'*27*len(df.keys()))
        for idx in range(self.n_filters):
            cursor.insertText('\nTally bins for filter id = ' + str(self.filter_ids[idx]) + ' : ' + str(self.Tallies[self.tally_id][self.filter_ids[idx]]['bins']).replace("'", ""))
            cursor.insertText('\nSelected bins for filter id = ' + str(self.filter_ids[idx]) + ' : ' + str(self.Tallies[self.tally_id][self.filter_ids[idx]]['Checked_bins']).replace("'", ""))
        cursor.insertText('\nTally nuclides : ' + str(self.tally.nuclides))
        cursor.insertText('\nSelected nuclides : ' + str(self.selected_nuclides))
        cursor.insertText('\nTally scores: ' + str(self.tally.scores))
        cursor.insertText('\nSelected scores : ' + str(self.selected_scores))  
        cursor.insertText('\n' + '*'*27*len(df.keys()) + '\n')
        
        self.editor.setTextCursor(cursor)

        if 'MeshFilter' not in self.Filters_comboBox.currentText():
            #if self.n_filters == 0:   
            self.df_filtered = self.df.loc[(self.df['nuclide'].isin(self.selected_nuclides)) & (self.df['score'].isin(self.selected_scores))]       
            if self.n_filters > 0:
                #self.df_filtered = self.df.loc[(self.df['nuclide'].isin(self.selected_nuclides)) & (self.df['score'].isin(self.selected_scores))]
                for idx in range(self.n_filters):
                    self.df_filtered = self.df_filtered.loc[self.df[self.Keys[idx]].isin(self.Key_Selected_Bins[idx])].copy()
            self.Print_Formated_df(self.df_filtered.copy(), self.tally_id, self.editor)
        self.Plot_by_CB.setCurrentIndex(1)
        self.Graph_Layout_CB.setCurrentIndex(1)
        self.Graph_type_CB.setCurrentIndex(1)
        if self.Graph_type_CB.currentText() in ['Bar', 'Stacked Bars', 'Stacked Area']:
            self.xLog_CB.setEnabled(False)
            if 'low' in self.Plot_By_Key or 'center' in self.Plot_By_Key: 
                if 'mu ' in self.Plot_By_Key:
                    self.Curve_xLabel.setText('$\mu$')
                else:
                    self.Curve_xLabel.setText(self.Plot_By_Key.replace('center', '').replace('low', '').replace('[', '/ ').replace(']', ''))
       
        self.Normalizing_Settings()
 
    def Display_scores_2(self):
        self.DATA = {}
        if 'MeshFilter' in self.Filters_comboBox.currentText(): # MeshFilter
            for elm in self.buttons:
                elm.setEnabled(False)
            self.Graph_Layout_CB.setCurrentIndex(0)             
            self.Graph_type_CB.setCurrentIndex(0)             
            self.Plot_by_CB.setCurrentIndex(0)             
            self.Graph_Layout_CB.setEnabled(False)
            self.Graph_type_CB.setEnabled(False)
            self.Plot_by_CB.setEnabled(False)
            self.score_plot_PB.setEnabled(True)
            self.label.setEnabled(False)
            self.xLog_CB.setEnabled(True)
            self.Curve_xLabel.setText('x/cm')
            self.Curve_yLabel.setText('y/cm')
            self.xLog_CB.setText('Interp')
            self.score_plot_PB.setText('plot mesh')
            self.Mesh_scores()
            return
        else:
            self.Plot_by_CB.setEnabled(True)

        self.Keys = [''] * len(self.filter_ids)
        self.Key_Selected_Bins = [''] * len(self.filter_ids)
        self.Key_Selected_Bins_High = [''] * len(self.filter_ids)
        self.Key_Selected_Bins_Center = [''] * len(self.filter_ids)
        self.Bins_For_Title = [''] * len(self.filter_ids)
        self.BIN = [''] * len(self.filter_ids)
        self.UNIT = [''] * len(self.filter_ids)
        for idx in range(self.n_filters):
            self.DATA[idx] = {}
            self.filter_id = self.filter_ids[idx] 
            self.filter_name = self.Tallies[self.tally_id]['filter_names'][idx]
            #self.Filter_Bins_Select(self.tally_id, self.filter_id)
            if 'cell' in self.df_Keys and self.filter_name == 'CellFilter':
                self.Keys[idx] = 'cell'
                self.Checked_cells = self.Select_Bins(idx)
                self.Key_Selected_Bins[idx] = self.Checked_cells
                self.BIN[idx] = ' in cell '
            elif 'cellfrom' in self.df_Keys and self.filter_name == 'CellFromFilter':
                self.Keys[idx] = 'cellfrom'
                self.Checked_cellsfrom = self.Select_Bins(idx)
                self.Key_Selected_Bins[idx] = self.Checked_cellsfrom
                self.BIN[idx] = ' from cell '
            elif 'cellborn' in self.df_Keys and self.filter_name == 'CellBornFilter':
                self.Keys[idx] = 'cellborn'
                self.Checked_cellsborn = self.Select_Bins(idx)
                self.Key_Selected_Bins[idx] = self.Checked_cellsborn
                self.BIN[idx] = ' born in cell '
            elif 'surface' in self.df_Keys and self.filter_name == 'SurfaceFilter':
                self.Keys[idx] = 'surface'
                self.Checked_surfaces = self.Select_Bins(idx)
                self.Key_Selected_Bins[idx] = self.Checked_surfaces
                self.BIN[idx] = ' at surface '
            elif 'universe' in self.df_Keys and self.filter_name == 'UniverseFilter':
                self.Keys[idx] = 'universe'
                self.Checked_universes = self.Select_Bins(idx)
                self.Key_Selected_Bins[idx] = self.Checked_universes
                self.BIN[idx] = ' in universe '
            elif 'material' in self.df_Keys and self.filter_name == 'MaterialFilter':
                self.Keys[idx] = 'material'
                self.Checked_materials = self.Select_Bins(idx)
                self.Key_Selected_Bins[idx] = self.Checked_materials
                self.BIN[idx] = ' for material '
            elif 'collision' in self.df_Keys and self.filter_name == 'CollisionFilter':
                self.Keys[idx] = 'collision'
                self.Checked_collisions = self.Select_Bins(idx)
                self.Key_Selected_Bins[idx] = self.Checked_collisions
                self.BIN[idx] = ' at collision '
            elif 'particle' in self.df_Keys and self.filter_name == 'ParticleFilter':
                self.Keys[idx] = 'particle'
                self.Checked_particles = self.Select_Bins(idx)
                self.Key_Selected_Bins[idx] = [item for item in self.Checked_particles]
                self.BIN[idx] = ' for '
            elif 'energy low [eV]' in self.df_Keys and self.filter_name == 'EnergyFilter':
                self.Keys[idx] = 'energy low [eV]'
                self.Checked_energies_Low, self.Checked_energies_High, self.Checked_energies_Center, self.Checked_Energy_Bins = self.Select_Bins_Energy_Angle_Time(idx)
                self.Key_Selected_Bins[idx] = self.Checked_energies_Low
                self.Key_Selected_Bins_High[idx] = self.Checked_energies_High
                self.Key_Selected_Bins_Center[idx] = self.Checked_energies_Center
                self.Checked_energies = self.Checked_energies_Low
                if any((ele < 0.01 or ele > 100) and ele != 0. for ele in self.Key_Selected_Bins[idx]):    
                    Format = "{:.1E}"
                else:
                    Format = "{:.2f}"
                Low = [xx for xx in self.Key_Selected_Bins[idx]]
                if any((ele < 0.01 or ele > 100) and ele != 0. for ele in self.Key_Selected_Bins_High[idx]):    
                    Format = "{:.1E}"
                else:
                    Format = "{:.2f}"
                High = [xx for xx in self.Key_Selected_Bins_High[idx]]
                self.Bins_For_Title[idx] = [str((Format.format(x), Format.format(y),)).replace("'", "") for x, y in
                                    zip(Low, High)]
                self.BIN[idx] = ' at energy '
                self.UNIT[idx] = ' eV '
            elif 'energyout low [eV]' in self.df_Keys and self.filter_name == 'EnergyoutFilter':
                self.Keys[idx] = 'energyout low [eV]'
                self.Checked_energiesout_Low, self.Checked_energiesout_High, self.Checked_energiesout_Center, self.Checked_Energyout_Bins = self.Select_Bins_Energy_Angle_Time(idx)
                self.Key_Selected_Bins[idx] = self.Checked_energiesout_Low
                self.Key_Selected_Bins_High[idx] = self.Checked_energiesout_High
                self.Key_Selected_Bins_Center[idx] = self.Checked_energiesout_Center
                self.Checked_energiesout = self.Checked_energiesout_Low
                if any((ele < 0.01 or ele > 100) and ele != 0. for ele in self.Key_Selected_Bins[idx]):    
                    Format = "{:.1E}"
                else:
                    Format = "{:.2f}"
                Low = [xx for xx in self.Key_Selected_Bins[idx]]
                if any((ele < 0.01 or ele > 100) and ele != 0. for ele in self.Key_Selected_Bins_High[idx]):    
                    Format = "{:.1E}"
                else:
                    Format = "{:.2f}"
                High = [xx for xx in self.Key_Selected_Bins_High[idx]]
                self.Bins_For_Title[idx] = [str((Format.format(x), Format.format(y),)).replace("'", "") for x, y in
                                    zip(Low, High)]                
                self.BIN[idx] = ' at energyout '
                self.UNIT[idx] = ' eV '
            elif 'mu low' in self.df_Keys and self.filter_name == 'MuFilter':
                self.Keys[idx] = 'mu low'
                self.Checked_mu_Low, self.Checked_mu_High, self.Checked_mu_Center, self.Checked_Mu_Bins = self.Select_Bins_Energy_Angle_Time(idx)
                self.Key_Selected_Bins[idx] = self.Checked_mu_Low
                self.Key_Selected_Bins_High[idx] = self.Checked_mu_High
                self.Key_Selected_Bins_Center[idx] = self.Checked_mu_Center
                self.Checked_mu = self.Checked_mu_Low
                if any(np.abs(ele) < 0.01 and ele != 0. for ele in self.Key_Selected_Bins[idx]):    
                    Format = "{:.1E}"
                else:
                    Format = "{:.2f}"
                Low = [xx for xx in self.Key_Selected_Bins[idx]]
                if any(np.abs(ele) < 0.01 and ele != 0. for ele in self.Key_Selected_Bins_High[idx]):    
                    Format = "{:.1E}"
                else:
                    Format = "{:.2f}"
                High = [xx for xx in self.Key_Selected_Bins_High[idx]]
                self.Bins_For_Title[idx] = [str((Format.format(x), Format.format(y),)).replace("'", "") for x, y in
                                    zip(Low, High)]
                self.BIN[idx] = " at $\mu$ "
            elif 'polar low [rad]' in self.df_Keys and self.filter_name == 'PolarFilter':
                self.Keys[idx] = 'polar low [rad]'
                self.Checked_polar_Low, self.Checked_polar_High, self.Checked_polar_Center, self.Checked_Polar_Bins = self.Select_Bins_Energy_Angle_Time(idx)
                self.Key_Selected_Bins[idx] = self.Checked_polar_Low
                self.Key_Selected_Bins_High[idx] = self.Checked_polar_High
                self.Key_Selected_Bins_Center[idx] = self.Checked_polar_Center
                self.Checked_polar = self.Checked_polar_Low
                if any(np.abs(ele) < 0.01 and ele != 0. for ele in self.Key_Selected_Bins[idx]):    
                    Format = "{:.1E}"
                else:
                    Format = "{:.2f}"
                Low = [xx for xx in self.Key_Selected_Bins[idx]]
                if any(np.abs(ele) < 0.01 and ele != 0. for ele in self.Key_Selected_Bins_High[idx]):    
                    Format = "{:.1E}"
                else:
                    Format = "{:.2f}"
                High = [xx for xx in self.Key_Selected_Bins_High[idx]]
                self.Bins_For_Title[idx] = [str((Format.format(x), Format.format(y),)).replace("'", "") for x, y in
                                    zip(Low, High)]
                self.BIN[idx] = " at polar "
                self.UNIT[idx] = ' rad '
            elif 'azimuthal low [rad]' in self.df_Keys and self.filter_name == 'AzimuthalFilter':
                self.Keys[idx] = 'azimuthal low [rad]'
                self.Checked_azimuthal_Low, self.Checked_azimuthal_High, self.Checked_azimuthal_Center, self.Checked_Azimuthal_Bins = self.Select_Bins_Energy_Angle_Time(idx)
                self.Key_Selected_Bins[idx] = self.Checked_azimuthal_Low
                self.Key_Selected_Bins_High[idx] = self.Checked_azimuthal_High
                self.Key_Selected_Bins_Center[idx] = self.Checked_azimuthal_Center
                self.Checked_azimuthal = self.Checked_azimuthal_Low
                if any(np.abs(ele) < 0.01 and ele != 0. for ele in self.Key_Selected_Bins[idx]):    
                    Format = "{:.1E}"
                else:
                    Format = "{:.2f}"
                Low = [xx for xx in self.Key_Selected_Bins[idx]]
                if any(np.abs(ele) < 0.01 and ele != 0. for ele in self.Key_Selected_Bins_High[idx]):    
                    Format = "{:.1E}"
                else:
                    Format = "{:.2f}"
                High = [xx for xx in self.Key_Selected_Bins_High[idx]]
                self.Bins_For_Title[idx] = [str((Format.format(x), Format.format(y),)).replace("'", "") for x, y in
                                    zip(Low, High)]
                self.BIN[idx] = " at azimuthal "
                self.UNIT[idx] = ' rad '
            elif 'time low [s]' in self.df_Keys and self.filter_name == 'TimeFilter':
                self.Keys[idx] = 'time low [s]'
                self.Checked_time_Low, self.Checked_time_High, self.Checked_time_Center, self.Checked_Time_Bins = self.Select_Bins_Energy_Angle_Time(idx)
                self.Key_Selected_Bins[idx] = self.Checked_time_Low
                self.Key_Selected_Bins_High[idx] = self.Checked_time_High
                self.Key_Selected_Bins_Center[idx] = self.Checked_time_Center
                self.Checked_time = self.Checked_time_Low
                if any(np.abs(ele) < 0.01 and ele != 0. for ele in self.Key_Selected_Bins[idx]):    
                    Format = "{:.1E}"
                else:
                    Format = "{:.2f}"
                Low = [xx for xx in self.Key_Selected_Bins[idx]]
                if any(np.abs(ele) < 0.01 and ele != 0. for ele in self.Key_Selected_Bins_High[idx]):    
                    Format = "{:.1E}"
                else:
                    Format = "{:.2f}"
                High = [xx for xx in self.Key_Selected_Bins_High[idx]]
                self.Bins_For_Title[idx] = [str((Format.format(x), Format.format(y),)).replace("'", "") for x, y in
                                    zip(Low, High)]
                self.BIN[idx] = " at time "
                self.UNIT[idx] = ' s '
            elif 'legendre' in self.df_Keys and self.filter_name == 'LegendreFilter':
                self.Keys[idx] = 'legendre'
                self.Checked_legendres = self.Select_Bins(idx)
                self.Key_Selected_Bins[idx] = self.Checked_legendres
                self.BIN[idx] = " Legendre "
            elif 'spatiallegendre' in self.df_Keys and self.filter_name == 'SpatialLegendreFilter':
                self.Keys[idx] = 'spatiallegendre'
                self.Checked_spatiallegendres = self.Select_Bins(idx)
                self.Key_Selected_Bins[idx] = self.Checked_spatiallegendres  
                self.BIN[idx] = " spatial Legendre "    
            elif 'sphericalharmonics' in self.df_Keys and self.filter_name == 'SphericalHarmonicsFilter':
                self.Keys[idx] = 'sphericalharmonics'
                self.Checked_sphericalharmonics = self.Select_Bins(idx)
                self.Key_Selected_Bins[idx] = self.Checked_sphericalharmonics  
                self.BIN[idx] = " spherical Harmonics "
            elif 'delayedgroup' in self.df_Keys and self.filter_name == 'DelayedGroupFilter':
                self.Keys[idx] = 'delayedgroup'
                self.Checked_times = self.Select_Bins(idx)
                self.Key_Selected_Bins[idx] = self.Checked_times  
                self.BIN[idx] = " delayedgroup "
            elif 'zernike' in self.df_Keys and self.filter_name == 'ZernikeFilter':
                self.Keys[idx] = 'zernike'
                self.Checked_times = self.Select_Bins(idx)
                self.Key_Selected_Bins[idx] = self.Checked_times  
                self.BIN[idx] = " zernike "
            elif 'zernikeradial' in self.df_Keys and self.filter_name == 'ZernikeRadialFilter':
                self.Keys[idx] = 'zernikeradial'
                self.Checked_times = self.Select_Bins(idx)
                self.Key_Selected_Bins[idx] = self.Checked_times  
                self.BIN[idx] = " zernikeradial "
            else:
                for KEY in self.df_Keys:
                    if 'distribcell' in KEY[0]:           
                        self.Keys[idx] = 'distribcell'
                        self.Checked_distribcells = self.Select_Bins(idx)
                        self.Key_Selected_Bins[idx] = self.Checked_distribcells
                        self.BIN[idx] = " Distrib cell "
            
            if not self.Bins_For_Title[idx]:
                self.Bins_For_Title[idx] = self.Key_Selected_Bins[idx]   
            
            # fill dic to plot data            
            self.DATA[idx]['Filter_name'] = self.filter_name
            self.DATA[idx]['KEY'] = self.Keys[idx]
            self.DATA[idx]['Checked_bins'] = self.Key_Selected_Bins[idx]
            self.DATA[idx]['Checked_bins_high'] = self.Key_Selected_Bins_High[idx]
            self.DATA[idx]['Checked_bins_center'] = self.Key_Selected_Bins_Center[idx]
            self.DATA[idx]['BIN'] = self.BIN[idx]
            self.DATA[idx]['BINforTitle'] = self.Bins_For_Title[idx]
            self.DATA[idx]['UNIT'] = self.UNIT[idx]       
            if self.filter_name == 'ParticleFilter':
                self.DATA[idx]['BINforTitle'] = [item + 's' for item in self.DATA[idx]['BINforTitle']]
  
    def Select_Bins(self, Filter_Index):
        Checked_elems = []
        filter_id = self.filter_ids[Filter_Index]
        indices = self.Tallies[self.tally_id][filter_id]['Checked_bins_indices']
        for index in indices:
            Checked_bin = self.Tallies[self.tally_id][filter_id]['bins'][index - 2]
            if Checked_bin.isdigit():   
                Checked_elems.append(eval(Checked_bin))
            else: 
                Checked_elems.append(Checked_bin)   
        return Checked_elems 
 
    def Select_Bins_Energy_Angle_Time(self, Filter_Index):
        filter_id = self.filter_ids[Filter_Index]
        Low = []
        High = []
        Center = []
        Bins = []
        indices = self.Tallies[self.tally_id][filter_id]['Checked_bins_indices']
        for index in indices:
            Low.append(self.tally.filters[Filter_Index].bins[:, 0][index - 2])
            High.append(self.tally.filters[Filter_Index].bins[:, 1][index - 2])
            Bins.append(self.tally.filters[Filter_Index].bins[:][index - 2])
        Center = (np.array(Low) + (np.array(High) - np.array(Low)) * np.array([0.5]*len(Low))).tolist()
        return Low, High, Center, Bins

    def Unfiltered_Scores(self):
        df = self.df
        self.mean = {}
        self.std = {}
        self.DATA = {}
        self.Checked_cells = ['root']
        self.mean['root'] = {}
        self.std['root'] = {}
        self.DATA['root'] = {}
        self.DATA['root']['Checked_bins'] = self.Checked_cells
        if len(self.selected_nuclides) == 0:
            self.showDialog('Warning', 'No nuclide selected !')
            return
        for nuclide in self.selected_nuclides:    # maybe unusfull
            if nuclide != '': 
                self.mean['root'][nuclide] = {}
                self.std['root'][nuclide] = {} 
                for score in self.selected_scores:
                    if score != '':
                        Score = df[df['nuclide'] == nuclide][df['score'] == score]
                        #Score1 = Score[Score['score'] == score]
                        index = self.selected_scores.index(score)
                        self.mean['root'][nuclide][index] = []
                        self.std['root'][nuclide][index] = []
                        print(df)
                        return
                        self.mean['root'][nuclide][index] += list(Score1['mean'])   
                        self.std['root'][nuclide][index] += list(Score1['std. dev.'])   

    def Plot(self):
        if 'MeshFilter' in self.Filters_comboBox.currentText():
            self.Plot_Mesh()
        elif 'DistribcellFilter' in self.Filters_comboBox.currentText() and self.Graph_type_CB.currentText() == 'mesh graph':
            self.Plot_Distribcell()
        elif 'Keff' in self.Tally_id_comboBox.currentText():
            self.Plot_Keff()
        else:
            if self.Plot_by_CB.currentIndex() == 0:
                self.showDialog('Warning', 'Nothing will be ploted. Select Plot_By option first!')
                return
            self.Plot_Score()

    def Plot_Keff(self):
        self.Plot_By_Key = self.Plot_by_CB.currentText()
        if not self.Checked_batches:
            self.showDialog('Warning', 'Check bathes to plot first!')
            return
        if self.Graph_type_CB.currentIndex() == 0:
            self.showDialog('Warning', 'Select graph type first!')
        else:
            from matplotlib.ticker import MaxNLocator
            Graph_type = self.Graph_type_CB.currentText()
            fig, ax = plt.subplots()
            x = self.Checked_batches
            if self.Plot_By_Key == 0:
                self.showDialog('Warning', 'Select data to plot!')
                plt.close()
                return
            elif self.Plot_By_Key == 'Keff':
                y = [self.Keff_List[i-1] for i in x]
                if Graph_type == 'Lin-Lin':
                    ax.plot(x, y, label='keff', color='b')
                elif Graph_type == 'Scatter':
                    ax.scatter(x, y, marker='^')
                ax.xaxis.set_major_locator(MaxNLocator(integer=True))
                plt.title(self.Curve_title.text())
                plt.xlabel(self.Curve_xLabel.text())
                plt.ylabel(self.Curve_yLabel.text(), color='b')
                try:
                    ax.errorbar(x, y, np.array(y_error), ecolor='black')
                except:
                    pass
            elif self.Plot_By_Key == 'Keff & Shannon entropy':
                y = [self.Keff_List[i-1] for i in x]
                if Graph_type == 'Lin-Lin':
                    ax.plot(x, y, label='keff', color='b')
                elif Graph_type == 'Scatter':
                    ax.scatter(x, y, marker='^')
                plt.title(self.Curve_title.text())
                plt.xlabel(self.Curve_xLabel.text())
                plt.ylabel(self.Curve_yLabel.text(), color='b') 
                
                try:
                    H = [self.H[i-1] for i in x]
                    ax2 = ax.twinx()
                    if Graph_type == 'Lin-Lin':
                        ax2.plot(x, H, label='entropy', color='g')
                    elif Graph_type == 'Scatter':
                        ax2.scatter(x, H, marker='^', color='g')
                    #plt.xlabel('Generation')
                    plt.ylabel('Shannon entropy', color='g', fontsize=int(self.yFont_CB.currentText()))
                    ax2.yaxis.set_tick_params(labelsize=int(self.yFont_CB.currentText())*0.75)
                except:
                    self.showDialog('Warning', 'Shannon entropy was not specified in simulation settings!')
                try:
                    ax.errorbar(x, y, np.array(y_error), ecolor='black')
                except:
                    pass
            elif self.Plot_By_Key == 'Shannon entropy':
                try:
                    H = [self.H[i-1] for i in x]
                    if Graph_type == 'Lin-Lin':
                        ax.plot(x, H, label='entropy', color='g')
                    elif Graph_type == 'Scatter':
                        ax.scatter(x, H, marker='^', color='g')
                    #plt.xlabel('Generation')
                    plt.ylabel('Shannon entropy', color='g')
                except:
                    self.showDialog('Warning', 'Shannon entropy was not specified in simulation settings!')
            if self.grid:
                ax.grid(visible=self.grid, which=self.which_grid, axis=self.which_axis)
            else:
                ax.grid(False)
            
            self.Change_Scales(ax, Graph_type)
            self.Labels_Font(ax, plt)            
            plt.subplots_adjust(left=0.18, right=0.98, top=0.92, bottom=0.12)
            plt.tight_layout()
            plt.show()
                   
    def Plot_Score(self):
        #Plot tallies
        self.Plot_By_Key = self.Plot_by_CB.currentText()
        self.Stack_Plot = False
        if self.Graph_Layout_CB.currentText() != 'BoxPlot' and self.Graph_type_CB.currentIndex() == 0:
            self.showDialog('Warning', 'Select graph type first!')
            return

        if self.Graph_Layout_CB.currentIndex() == 0:
            self.showDialog('Warning', 'Select graph layout first !')
            return
        
        """if self.row_SB.value()*self.col_SB.value() > 20 and self.Graph_Layout_CB.currentText() == 'Multiple curves':
                qm = QMessageBox
                ret = qm.question(self, 'Warning',' Warning : ' + str(self.N_Fig) + ' curves will be generated! \n continue ploting ?', qm.Yes | qm.No)
                if ret == qm.Yes:
                    pass 
                elif ret == qm.No:
                    self.WillPlot = False
                    return"""

        self.Normalization = False
        self.Normalizing() 

        if self.Normalization:
            df = self.df_filtered_normalized
        else:
            df = self.df_filtered

        if self.Graph_Layout_CB.currentText() == 'Multiple curves':        # Multiple curves
            self.Multiple_Curves(df)
            self.Stack_Plot = False
        elif self.Graph_Layout_CB.currentText() == 'Stacking subplots':    # Stacking subplots
            if self.filter_id == 0:
                self.Stack_Plot = False
                self.Multiple_Curves(df)                    
            else:
                self.Stack_Plot = True
                self.Stacking_plot_Curves(df)
        elif self.Graph_Layout_CB.currentText() == 'BoxPlot':               # Box Plots
            self.box_plot()
            self.Stack_Plot = False
   
    def set_Graph_stack(self):  
        if 'Keff' not in self.Tally_id_comboBox.currentText():
            if self.Graph_Layout_CB.currentIndex() in [0, 3]:
                for elm in self.buttons:
                    elm.setEnabled(False)
                for elm in self.buttons_Stack: 
                    elm.setEnabled(False)
                self.Graph_type_CB.setEnabled(False)
                self.Graph_type_CB.setCurrentIndex(0)
                if self.Graph_Layout_CB.currentIndex() == 0:
                    self.score_plot_PB.setText('plot score')
                    self.score_plot_PB.setEnabled(False)
                elif self.Graph_Layout_CB.currentIndex() == 3:
                    self.score_plot_PB.setText('plot Box Plot')
                    self.score_plot_PB.setEnabled(True)
                for CB in [self.xLog_CB, self.yLog_CB, self.Add_error_bars_CB, self.xGrid_CB, self.yGrid_CB, self.MinorGrid_CB]:
                    CB.setChecked(False)
            else:
                for elm in self.buttons:
                    elm.setEnabled(True)            
                self.score_plot_PB.setEnabled(True)
                self.score_plot_PB.setText('plot score')
                self.Graph_type_CB.setEnabled(True) 
                self.Graph_type_CB.setCurrentIndex(1)
                if self.Graph_Layout_CB.currentIndex() == 1:
                    for elm in self.buttons_Stack: 
                        elm.setEnabled(False)
                    self.row_SB.setEnabled(False)
                    self.col_SB.setEnabled(False)
                    self.label_5.setEnabled(False)
                    self.label_6.setEnabled(False)
                    self.label_7.setEnabled(False)
                elif self.Graph_Layout_CB.currentIndex() == 2:
                    for elm in self.buttons_Stack: 
                        elm.setEnabled(True)
                    self.row_SB.setValue(2)
                    self.col_SB.setValue(1)       
                self.set_Scales()

            self.Activate_Curve_Type()    
            self.Plot_By_Key = self.Plot_by_CB.currentText()
            if self.Plot_By_Key in ['nuclide', 'score', 'cell', 'cellfrom', 'cellborn', 'distribcell', 
                                    'surface', 'universe', 'material', 'particle', 'collision',
                                    'legendre', 'spatiallegendre', 'sphericalharmonics', 'zernike', 'zernikeradial']:
                self.Deactivate_Curve_Type()
                if self.Graph_type_CB.currentIndex() in [3, 5]:     #xxxxx
                    self.Graph_type_CB.setCurrentIndex(1)
            else:
                self.Activate_Curve_Type()
               
            try:     # try is needed because this will be executed before calculating self.Key
                # determine stack size
                self.N_Fig = 1
                if self.Plot_By_Key not in ['nuclide', 'score']:
                    self.N_Fig = len(self.selected_nuclides)
                if self.n_filters > 0:
                    for idx in range(len(self.filter_ids)):
                        self.N_Fig = self.N_Fig * len(self.Key_Selected_Bins[idx])
                    for idx in range(len(self.filter_ids)):
                        if self.Plot_By_Key == self.Keys[idx]:
                            self.N_Fig = int(self.N_Fig / len(self.Key_Selected_Bins[idx]))
                    if 'center' in self.Plot_By_Key:
                        index = self.Plot_by_CB.currentIndex() - 1
                        idx = self.Keys.index(self.Plot_by_CB.itemText(index))
                        self.N_Fig = int(self.N_Fig / len(self.Key_Selected_Bins[idx]))
                
                self.row_SB.setValue(int(np.sqrt(self.N_Fig) + 0.5))
                col = self.N_Fig / self.row_SB.value()
                if col.is_integer():
                    self.col_SB.setValue(int(col)) 
                else:      
                    self.col_SB.setValue(int(col + 1.))       
                if self.row_SB.value() == 1 and self.col_SB.value() > 3:
                    self.row_SB.setValue(int(self.col_SB.value() * 0.5 + 0.5) )
                    self.col_SB.setValue(int(self.col_SB.value() / self.row_SB.value() + 0.5))
                elif self.col_SB.value() == 1 and self.row_SB.value() > 3:
                    self.col_SB.setValue(int(self.row_SB.value() * 0.5 + 0.5))
                    self.row_SB.setValue(int(self.row_SB.value() / self.col_SB.value() + 0.5))
            except:
                pass

    def Multiple_Curves(self, df):
        if self.row_SB.value()*self.col_SB.value() > 20:
                qm = QMessageBox
                ret = qm.question(self, 'Warning',' Warning : ' + str(self.N_Fig) + ' curves will be generated! \n continue ploting ?', qm.Yes | qm.No)
                if ret == qm.Yes:
                    pass 
                elif ret == qm.No:
                    self.WillPlot = False
                    return

        self.WillPlot = True
        if self.n_filters == 0:
            ax = ['']    
        else:
            ax = [''] * self.N_Fig
  
        if self.Plot_By_Key in ['nuclide', 'score']:  
            self.Plot_By_Nuclide_Score(df, ax)
        else:
            self.Plot_By_Filter(df, ax)

        if not self.Stack_Plot:
            plt.tight_layout()
            if self.WillPlot:
                plt.show()
    
    def Stacking_plot_Curves(self, df):
        self.WillPlot = True
        self.Plot_By_Key = self.Plot_by_CB.currentText()
        Stack_Size = self.row_SB.value() * self.col_SB.value()
        if Stack_Size == 1:
            self.showDialog('Warning', 'Stacking plots need more rows and/or columns !')
            self.row_SB.setValue(2)
        if self.N_Fig == 1:
            self.Stack_Plot = False
            self.Multiple_Curves(df) 
            return        
        if Stack_Size < self.N_Fig:
            qm = QMessageBox
            ret = qm.question(self, 'Warning',' Stack size : ' + str(Stack_Size) + ' less than total available plots : ' + 
                                     str(self.N_Fig) + '\nLast plots will be removed! Continue ploting ?', qm.Yes | qm.No)
            if ret == qm.Yes:
                pass 
            elif ret == qm.No:
                self.WillPlot = False
                return
        
        fig, axs = plt.subplots(self.row_SB.value(), self.col_SB.value(), layout="constrained")   #, sharex=True)

        if self.N_Fig < Stack_Size:
            ax = [None] * Stack_Size
        else:    
            ax = [None] * self.N_Fig            
        
        for i, ax_ in enumerate(axs.flat):
            ax[i] = ax_

        if self.Plot_By_Key in ['nuclide', 'score']:  
            self.Plot_By_Nuclide_Score(df, ax)
        else:
            self.Plot_By_Filter(df, ax)

        if Stack_Size > self.N_Fig:
            for i in range(self.N_Fig, Stack_Size):
                ax[i].set_visible(False)        # to remove empty plots
        if self.WillPlot:
            plt.subplots_adjust(left=0.18, right=0.98, top=0.92, bottom=0.12)
            plt.tight_layout()
            plt.show()

    def Plot_By_Nuclide_Score(self, df, ax): 
        # up to 6 filters
        prop_cycle_color = ['#FB1304', '#008000', '#0751FC', '#C107FC', '#FBCE02',
                    '#00FFFF', '#F9F923', '#00FF00', '#800000', '#808000', 
                    '#FFFF00', '#000080', '#FF00FF', '#808080', '#000000', 
                    '#CD5C5C', '#BF5A31', '#31BFBD', '#FFA07A', '#70D38F',
                    '#AE31F0', '#F08080']
        Graph_type = self.Graph_type_CB.currentText()
        Width = 0.15    
        if self.Plot_By_Key == 'nuclide':
            KEY0 = 'nuclide'
            KEY01 = 'score'
            Checked_bins0 = self.selected_nuclides
            Checked_bins01 = self.selected_scores
        elif self.Plot_By_Key == 'score':
            KEY0 = 'score'
            KEY01 = 'nuclide'
            Checked_bins0 = self.selected_scores
            Checked_bins01 = self.selected_nuclides

        X_Shift = Width * 0.5 * (len(Checked_bins01) - 1)
        X_ = np.arange(len(Checked_bins0))
        Stack_Size = self.row_SB.value() * self.col_SB.value()
        Checked_bins = [''] * self.n_filters
        Bins_For_Title = [''] * self.n_filters
        BIN = [''] * self.n_filters
        UNIT = [''] * self.n_filters
        key = [''] * self.n_filters
        key1 = ['']; BIN1 = ['']; UNIT1 = ['']; Checked_bins1 = ['']; Bins_For_Title1 = ['']
        key2 = ['']; BIN2 = ['']; UNIT2 = ['']; Checked_bins2 = ['']; Bins_For_Title2 = ['']
        key3 = ['']; BIN3 = ['']; UNIT3 = ['']; Checked_bins3 = ['']; Bins_For_Title3 = ['']
        key4 = ['']; BIN4 = ['']; UNIT4 = ['']; Checked_bins4 = ['']; Bins_For_Title4 = ['']
        key5 = ['']; BIN5 = ['']; UNIT5 = ['']; Checked_bins5 = ['']; Bins_For_Title5 = ['']
        key6 = ['']; BIN6 = ['']; UNIT6 = ['']; Checked_bins6 = ['']; Bins_For_Title6 = ['']

        if self.n_filters >= 1:
            i = 0
            for filter in self.Filter_names:
                idx = self.Filter_names.index(filter)
                Checked_bins[i] = self.DATA[idx]['Checked_bins']
                key[i] = self.DATA[idx]['KEY']
                Bins_For_Title[i] = self.DATA[idx]['BINforTitle']
                BIN[i] = self.DATA[idx]['BIN']
                UNIT[i] = self.DATA[idx]['UNIT']
                i += 1

            key1 = key[0]; BIN1 = BIN[0]; UNIT1 = UNIT[0]; Checked_bins1 = Checked_bins[0]; Bins_For_Title1 = Bins_For_Title[0]
            if self.n_filters >= 2:    
                key2 = key[1]; BIN2 = BIN[1]; UNIT2 = UNIT[1]; Checked_bins2 = Checked_bins[1]; Bins_For_Title2 = Bins_For_Title[1]
                if self.n_filters >= 3:
                    key3 = key[2]; BIN3 = BIN[2]; UNIT3 = UNIT[2]; Checked_bins3 = Checked_bins[2]; Bins_For_Title3 = Bins_For_Title[2]
                    if self.n_filters >= 4:
                        key4 = key[3]; BIN4 = BIN[3]; UNIT4 = UNIT[3]; Checked_bins4 = Checked_bins[3]; Bins_For_Title4 = Bins_For_Title[3]
                        if self.n_filters >= 5:
                            key5 = key[4]; BIN5 = BIN[4]; UNIT5 = UNIT[4]; Checked_bins5 = Checked_bins[4]; Bins_For_Title5 = Bins_For_Title[4]
                            if self.n_filters >= 6:
                                key6 = key[5]; BIN6 = BIN[5]; UNIT6 = UNIT[5]; Checked_bins6 = Checked_bins[5]; Bins_For_Title6 = Bins_For_Title[5]

        i = 0
        for bin6 in Checked_bins6:
            j6 = Checked_bins6.index(bin6)
            for bin5 in Checked_bins5:
                j5 = Checked_bins5.index(bin5)
                for bin4 in Checked_bins4:                                  # loop on Filter4
                    j4 = Checked_bins4.index(bin4)    
                    for bin3 in Checked_bins3:                              # loop on Filter3
                        j3 = Checked_bins3.index(bin3)
                        for bin2 in Checked_bins2:                          # loop on Filter2
                            j2 = Checked_bins2.index(bin2)
                            for bin1 in Checked_bins1:                      # loop on Filter1
                                j1 = Checked_bins1.index(bin1)
                                
                                if not self.Stack_Plot:
                                    fig, ax[i] = plt.subplots()
                                else:
                                    if i + 1 > Stack_Size:
                                        break

                                xs_ = []; y_ = {}; y_err = {}  
                                for bin01 in Checked_bins01:
                                    y_[bin01] = []; y_err[bin01] = []
                                for bin0 in Checked_bins0: 
                                    bin0_idx = Checked_bins0.index(bin0)
                                    y_error = []; ys_ = []; ys_err = []
                                    X = bin0_idx   
                                    multiplier = 0
                                    xs_.append(X)                
                                    for bin01 in Checked_bins01:
                                        index = Checked_bins01.index(bin01)
                                        if Graph_type == 'Bar':
                                            offset = Width * multiplier
                                            X += offset
                                        x = X 
                                        multiplier = 1  
                                        
                                        y = self.df[self.df[KEY0] == bin0][self.df[KEY01] == bin01]['mean']
                                        y_error = self.df[self.df[KEY0] == bin0][self.df[KEY01] == bin01]['std. dev.']
                                        if self.n_filters >= 1: 
                                            y = y[self.df[key1] == bin1]
                                            y_error = y_error[self.df[key1] == bin1]
                                            if self.n_filters >= 2:
                                                y = y[self.df[key2] == bin2]
                                                y_error = y_error[self.df[key2] == bin2]
                                                if self.n_filters >= 3:
                                                    y = y[self.df[key3] == bin3]
                                                    y_error = y_error[self.df[key3] == bin3]
                                                    if self.n_filters >= 4:
                                                        y = y[self.df[key4] == bin4]
                                                        y_error = y_error[self.df[key4] == bin4]
                                                        if self.n_filters >= 5:
                                                            y = y[self.df[key5] == bin5]
                                                            y_error = y_error[self.df[key5] == bin5]
                                                            if self.n_filters >= 6:
                                                                y = y[self.df[key6] == bin6]
                                                                y_error = y_error[self.df[key6] == bin6]

                                        y = y.tolist()[0]   
                                        y_error = y_error.tolist()[0]    
                                        y_[bin01].append(y)             
                                        y_err[bin01].append(y_error)    
                                        ys_.append(y_[bin01])
                                        ys_err.append(y_err[bin01]) 
                                        Label = bin01 if bin0_idx == 0 else None
                                        if Graph_type in ['Bar', 'Scatter']:
                                            if Graph_type == 'Bar':
                                                pass
                                                ax[i].bar(x, y, width=Width, label=Label, color=prop_cycle_color[index])
                                            elif Graph_type == 'Scatter':
                                                ax[i].scatter(x, y, marker='^', label = Label, color=prop_cycle_color[index])
                                            if self.Add_error_bars_CB.isChecked():
                                                ax[i].errorbar(x, y, np.array(y_error), ecolor='black')
                                    ax[i].set_prop_cycle(None)

                                if Graph_type == 'Stacked Bars':
                                    Bottom = np.zeros(len(Checked_bins0))
                                    for bin01 in Checked_bins01:
                                        Label = bin01 if len(Checked_bins01) > 1 else None
                                        k = Checked_bins01.index(bin01)
                                        if self.Add_error_bars_CB.isChecked():
                                            ax[i].bar(np.array(xs_) + X_Shift, ys_[k], yerr = np.array(ys_err[k]), bottom = Bottom, label = Label, color=prop_cycle_color[k])
                                        else:
                                            ax[i].bar(np.array(xs_) + X_Shift, ys_[k], bottom = Bottom, label = Label, color=prop_cycle_color[k])
                                        Bottom += ys_[k]
                                elif Graph_type == 'Stacked Area':
                                    ax[i].stackplot(np.array(xs_) + X_Shift, ys_[:len(Checked_bins01)], labels = Checked_bins01, colors=prop_cycle_color)
                                    if self.Add_error_bars_CB.isChecked():
                                        Bottom = np.zeros(len(Checked_bins0))
                                        for k in range(len(Checked_bins01)):
                                            ax[i].errorbar(np.array(xs_) + X_Shift, ys_[k] + Bottom, np.array(ys_err[k]), fmt = '|', ecolor='black')
                                            Bottom += ys_[k]     
                                
                                if len(Checked_bins01) > 1: 
                                    ax[i].legend()

                                ax[i].set_xlabel(self.Curve_xLabel.text())
                                ax[i].set_ylabel(self.Curve_yLabel.text())    
                                Title = self.Curve_title.text()
                                if self.n_filters >= 1: 
                                    Title = Title + BIN1 + str(Bins_For_Title1[j1]).replace("'", "") + UNIT1
                                    if self.n_filters >= 2:
                                        Title = Title + ' - ' + BIN2 + str(Bins_For_Title2[j2]).replace("'","") + UNIT2
                                        if self.n_filters >= 3:
                                            Title = Title + '\n' + BIN3 + str(Bins_For_Title3[j3]).replace("'","") + UNIT3
                                            if self.n_filters >= 4:
                                                Title = Title + ' - ' + BIN4 + str(Bins_For_Title4[j4]).replace("'","") + UNIT4
                                                if self.n_filters >= 5:
                                                    Title = Title + ' - ' + BIN5 + str(Bins_For_Title5[j5]).replace("'","") + UNIT5
                                                    if self.n_filters >= 6:
                                                        Title = Title + ' - ' + BIN6 + str(Bins_For_Title6[j6]).replace("'","") + UNIT6
                                
                                ax[i].set_title(Title)

                                if Graph_type in ['Stacked Area', 'Stacked Bars', 'Bar']:  
                                    ax[i].set_xticks(X_ + X_Shift, Checked_bins0)  
                                else:
                                    ax[i].set_xticks(X_, Checked_bins0)   

                                self.Change_Scales(ax[i], Graph_type)
                                
                                if len(Checked_bins01) > 1: 
                                    ax[i].legend()

                                self.Labels_Font(ax[i], plt)
                                if self.grid:
                                    ax[i].grid(visible=self.grid, which=self.which_grid, axis=self.which_axis)
                                else:
                                    ax[i].grid(False)  
                                i += 1 

    def Plot_By_Filter(self, df, ax):
        Checked_bins = [''] * self.n_filters
        Bins_For_Title = [''] * self.n_filters
        Checked_bins_Low = ['']
        Checked_bins_High = ['']
        BIN = [''] * self.n_filters
        UNIT = [''] * self.n_filters
        key = [''] * self.n_filters
   
        if self.n_filters == 1:
            # filter1
            idx = 0
            if self.filter_name in self.ENERGY_ANGLE_FILTER:
                if 'low' in self.Plot_By_Key:
                    Checked_bins[0] = self.DATA[idx]['Checked_bins']
                elif 'center' in self.Plot_By_Key:
                    Checked_bins[0] = self.DATA[idx]['Checked_bins_center']
                Checked_bins_Low = self.DATA[idx]['Checked_bins']
                Checked_bins_High = self.DATA[idx]['Checked_bins_high']
            else:
                Checked_bins[0] = self.DATA[idx]['Checked_bins']
            key[0] = self.DATA[idx]['KEY']
            Bins_For_Title[0] = self.DATA[idx]['BINforTitle']
            BIN[0] = self.DATA[idx]['BIN']
            UNIT[0] = self.DATA[idx]['UNIT']
        
        elif self.n_filters >= 2:
            FILTERS = [filter for filter in self.Filter_names]            
            for filter in self.Filter_names:
                if 'low' in self.Plot_By_Key:
                    index = self.Plot_by_CB.currentIndex()
                    idx = self.Keys.index(self.Plot_by_CB.itemText(index))
                    Checked_bins[0] = self.DATA[idx]['Checked_bins']
                    Checked_bins_Low = self.DATA[idx]['Checked_bins']
                    Checked_bins_High = self.DATA[idx]['Checked_bins_high']
                elif 'center' in self.Plot_By_Key:
                    index = self.Plot_by_CB.currentIndex() - 1
                    idx = self.Keys.index(self.Plot_by_CB.itemText(index))
                    Checked_bins[0] = self.DATA[idx]['Checked_bins_center']
                    Checked_bins_Low = self.DATA[idx]['Checked_bins']
                    Checked_bins_High = self.DATA[idx]['Checked_bins_high']
                else:
                    index = self.Plot_by_CB.currentIndex()
                    idx = self.Keys.index(self.Plot_by_CB.itemText(index))
                    Checked_bins[0] = self.DATA[idx]['Checked_bins']

                key[0] = self.DATA[idx]['KEY']
                Bins_For_Title[0] = self.DATA[idx]['BINforTitle']
                BIN[0] = self.DATA[idx]['BIN']
                UNIT[0] = self.DATA[idx]['UNIT']
                idx_to_remove = idx
                break

            FILTERS.remove(self.Filter_names[idx_to_remove])
            i = 1
            for filter in FILTERS:
                idx = self.Filter_names.index(filter)
                Checked_bins[i] = self.DATA[idx]['Checked_bins']
                key[i] = self.DATA[idx]['KEY']
                Bins_For_Title[i] = self.DATA[idx]['BINforTitle']
                BIN[i] = self.DATA[idx]['BIN']
                UNIT[i] = self.DATA[idx]['UNIT']
                i += 1

        X_ = np.arange(len(Checked_bins))
        
        self.Plot_by_All_Filters(df, ax, Checked_bins, Checked_bins_Low, Checked_bins_High, key, Bins_For_Title, BIN, UNIT)

    def Plot_by_All_Filters(self, df, ax, Checked_bins, Checked_bins_Low, Checked_bins_High, key, Bins_For_Title, BIN, UNIT):
        # up to 6 filters
        Graph_type = self.Graph_type_CB.currentText()
        Width = 0.15 
        X_Shift = Width * 0.5 * (len(self.selected_scores) - 1)
        Stack_Size = self.row_SB.value()*self.col_SB.value()
        X_ = np.arange(len(Checked_bins[0]))
        x_Lin = Checked_bins[0]
        key2 = ['']; BIN2 = ['']; UNIT2 = ['']; Checked_bins2 = ['']; Bins_For_Title2 = ['']
        key3 = ['']; BIN3 = ['']; UNIT3 = ['']; Checked_bins3 = ['']; Bins_For_Title3 = ['']
        key4 = ['']; BIN4 = ['']; UNIT4 = ['']; Checked_bins4 = ['']; Bins_For_Title4 = ['']
        key5 = ['']; BIN5 = ['']; UNIT5 = ['']; Checked_bins5 = ['']; Bins_For_Title5 = ['']
        key6 = ['']; BIN6 = ['']; UNIT6 = ['']; Checked_bins6 = ['']; Bins_For_Title6 = ['']

        prop_cycle_color = ['#FB1304', '#008000', '#0751FC', '#C107FC', '#FBCE02',
                            '#00FFFF', '#F9F923', '#00FF00', '#800000', '#808000', 
                            '#FFFF00', '#000080', '#FF00FF', '#808080', '#000000', 
                            '#CD5C5C', '#BF5A31', '#31BFBD', '#FFA07A', '#70D38F',
                            '#AE31F0', '#F08080']  
        if Checked_bins_Low == ['']:
            Checked_bins_Low = Checked_bins[0]

        if self.n_filters >= 1:
            key1 = key[0]; BIN1 = BIN[0]; UNIT1 = UNIT[0]
            if self.n_filters >= 2:    
                key2 = key[1]; BIN2 = BIN[1]; UNIT2 = UNIT[1]; Checked_bins2 = Checked_bins[1]; Bins_For_Title2 = Bins_For_Title[1]
                if self.n_filters >= 3:
                    key3 = key[2]; BIN3 = BIN[2]; UNIT3 = UNIT[2]; Checked_bins3 = Checked_bins[2]; Bins_For_Title3 = Bins_For_Title[2]
                    if self.n_filters >= 4:
                        key4 = key[3]; BIN4 = BIN[3]; UNIT4 = UNIT[3]; Checked_bins4 = Checked_bins[3]; Bins_For_Title4 = Bins_For_Title[3]
                        if self.n_filters >= 5:
                            key5 = key[4]; BIN5 = BIN[4]; UNIT5 = UNIT[4]; Checked_bins5 = Checked_bins[4]; Bins_For_Title5 = Bins_For_Title[4]
                            if self.n_filters >= 6:
                                key6 = key[5]; BIN6 = BIN[5]; UNIT6 = UNIT[5]; Checked_bins6 = Checked_bins[5]; Bins_For_Title6 = Bins_For_Title[5]
        
        i = 0
        for bin6 in Checked_bins6:                        # loop on Filter6
            j6 = Checked_bins6.index(bin6)
            for bin5 in Checked_bins5:                        # loop on Filter5
                j5 = Checked_bins5.index(bin5)
                for bin4 in Checked_bins4:                           # loop on Filter4
                    j4 = Checked_bins4.index(bin4)
                    for bin3 in Checked_bins3:                           # loop on Filter3
                        j3 = Checked_bins3.index(bin3)
                        for bin2 in Checked_bins2:                          # loop on Filter2
                            j2 = Checked_bins2.index(bin2)
                            for nuclide in self.selected_nuclides:               # loop on nuclides                                
                                if not self.Stack_Plot:
                                    fig, ax[i] = plt.subplots()
                                else:
                                    if i + 1 > Stack_Size:
                                        break

                                xs_ = []; y_ = {}; y_err = {}  
                                for score in self.selected_scores:
                                    y_[score] = []; y_err[score] = []
                                for bin in Checked_bins_Low: 
                                    bin_idx = Checked_bins_Low.index(bin)
                                    y_error = []; ys_ = []; ys_err = []
                                    X = Checked_bins_Low.index(bin)    
                                    multiplier = 0
                                    xs_.append(X)
                                    for score in self.selected_scores:
                                        index = self.selected_scores.index(score)
                                        if Graph_type == 'Bar':
                                            offset = Width * multiplier 
                                            X += offset
                                        x = X 
                                        multiplier = 1   

                                        y = df[df[key1] == bin][df.nuclide == nuclide][df.score == score]['mean']  
                                        y_error = df[df[key1]  == bin][df.nuclide == nuclide][df.score == score]['std. dev.']  
                                        if self.n_filters >= 2:
                                            y = y[df[key2] == bin2]
                                            y_error = y_error[df[key2] == bin2]
                                            if self.n_filters >= 3:
                                                y = y[df[key3] == bin3]  
                                                y_error = y_error[df[key3] == bin3]   
                                                if self.n_filters >= 4:
                                                    y = y[df[key4] == bin4]  
                                                    y_error = y_error[df[key4] == bin4]   
                                                    if self.n_filters >= 5:
                                                        y = y[self.df[key5] == bin5]
                                                        y_error = y_error[self.df[key5] == bin5]
                                                        if self.n_filters >= 6:
                                                            y = y[self.df[key6] == bin6]
                                                            y_error = y_error[self.df[key6] == bin6]   

                                        y = y.tolist()[0]          
                                        y_error = y_error.tolist()[0]          
                                        y_[score].append(y)   
                                        y_err[score].append(y_error)   
                                        ys_.append(y_[score])
                                        ys_err.append(y_err[score])                    
        
                                        if Graph_type == 'Bar':
                                            Label = score if bin_idx == 0 else None
                                            ax[i].bar(x, y, width=Width, label=Label, color=prop_cycle_color[index])
                                            if self.Add_error_bars_CB.isChecked():
                                                ax[i].errorbar(x, y, y_error, fmt='|', ecolor='black')                            
                                    
                                    #ax[i].set_prop_cycle(None)

                                if Graph_type in ['Lin-Lin', 'Scatter', 'Stairs']:
                                    for score in self.selected_scores:
                                        if len(self.selected_scores) > 1:
                                            Label = score
                                        else:
                                            Label = None
                                        k = self.selected_scores.index(score)
                                        if Graph_type == 'Lin-Lin':
                                            if score == 'flux':    
                                                ax[i].plot(x_Lin, ys_[k], label = Label, drawstyle='steps-mid', color=prop_cycle_color[k])
                                            else:
                                                ax[i].plot(x_Lin, ys_[k], label = Label, color=prop_cycle_color[k])
                                        elif Graph_type == 'Scatter':
                                            if 'low' in self.Plot_By_Key or 'center' in self.Plot_By_Key:
                                                ax[i].scatter(x_Lin, ys_[k], marker='^', label = Label, color=prop_cycle_color[k])
                                            else:
                                                ax[i].scatter(X_, ys_[k], marker='^', label = Label, color=prop_cycle_color[k])
                                                ax[i].set_xticks(X_, Bins_For_Title[0])
                                        elif Graph_type == 'Stairs':
                                            edges = [Checked_bins_Low[0]]
                                            edges.extend(Checked_bins_High)
                                            ax[i].stairs(ys_[k], edges, label = Label, color=prop_cycle_color[k])
                                        if self.Add_error_bars_CB.isChecked():
                                            ax[i].errorbar(x_Lin, ys_[k], ys_err[k], fmt='|', ecolor='black')
                                elif Graph_type == 'Stacked Bars':
                                    Bottom = np.zeros(len(Checked_bins[0]))
                                    for score in self.selected_scores:
                                        Label = score if len(self.selected_scores) > 1 else None           
                                        k = self.selected_scores.index(score)
                                        if self.Add_error_bars_CB.isChecked():
                                            ax[i].bar(np.array(xs_) + X_Shift, ys_[k], yerr=np.array(ys_err[k]), bottom=Bottom, label=Label, color=prop_cycle_color[k])
                                        else:
                                            ax[i].bar(np.array(xs_) + X_Shift, ys_[k], bottom = Bottom, label = Label, color=prop_cycle_color[k])
                                        Bottom += ys_[k]            
                                elif Graph_type == 'Stacked Area':
                                    ax[i].stackplot(np.array(xs_) + X_Shift, ys_[:len(self.selected_scores)], labels = self.selected_scores, colors=prop_cycle_color)
                                    if self.Add_error_bars_CB.isChecked():
                                        Bottom = np.zeros(len(Checked_bins[0]))
                                        for k in range(len(self.selected_scores)):
                                            ax[i].errorbar(np.array(xs_) + X_Shift, ys_[k] + Bottom, np.array(ys_err[k]), fmt = '|', ecolor='black')
                                            Bottom += ys_[k]

                                ax[i].set_xlabel(self.Curve_xLabel.text())
                                ax[i].set_ylabel(self.Curve_yLabel.text())
                                if score in ['flux', 'current']:
                                    Subtitle = ''
                                else:
                                    if len(self.selected_nuclides) == 1 and nuclide == 'total':
                                        Subtitle = ''
                                    else:  
                                        Subtitle = '\nnuclide ' + str(nuclide)
        
                                Title = self.Curve_title.text()
                                if self.n_filters >= 2:
                                    Title = Title + ' - ' + BIN2 + str(Bins_For_Title2[j2]).replace("'","") + UNIT2
                                    if self.n_filters >= 3:
                                        Title = Title + BIN3 + str(Bins_For_Title3[j3]).replace("'","") + UNIT3
                                        if self.n_filters >= 4:
                                            Title = Title + '\n' + BIN4 + str(Bins_For_Title4[j4]).replace("'","") + UNIT4
                                            if self.n_filters >= 5:
                                                Title = Title + ' - ' + BIN5 + str(Bins_For_Title5[j5]).replace("'","") + UNIT5
                                                if self.n_filters >= 6:
                                                    Title = Title + ' - ' + BIN6 + str(Bins_For_Title6[j6]).replace("'","") + UNIT6
                        
                                ax[i].set_title(Title + Subtitle)

                                if Graph_type in ['Stacked Area', 'Stacked Bars', 'Bar']:  
                                    ax[i].set_xticks(X_ + X_Shift, Bins_For_Title[0])   # self.x)
                                    
                                self.Change_Scales(ax[i], Graph_type)
                                
                                if len(self.selected_scores) > 1: 
                                    ax[i].legend(self.selected_scores)

                                if self.grid:
                                    ax[i].grid(visible=self.grid, which=self.which_grid, axis=self.which_axis)
                                else:
                                    ax[i].grid(False)            
                                self.Labels_Font(ax[i], plt)
                                                    
                                i += 1

    def Normalizing_Settings(self):    # called by Display_scores
        # Set normalizing parameters 
        self.ENERGY_ANGLE_FILTER = ['EnergyFilter', 'EnergyoutFilter', 'MuFilter', 'PolarFilter', 'AzimuthalFilter', 'TimeFilter']
        self.Norm_Keys = ['energy', 'mu', 'polar', 'azimuthal', 'time']
        self.Norm_Available_Keys = [key.split()[0] for key in self.df_Keys if 'low' in key]
        Norm_CBox = [self.Norm_to_Power_CB, self.Norm_to_Heating_CB, self.Norm_to_UnitLethargy_CB, self.Norm_to_Vol_CB, self.Norm_to_BW_CB]
        Norm_LE = [self.Nu_LE, self.Heating_LE, self.Q_LE, self.Power_LE, self.Factor_LE, self.Keff_LE]
        validator_positif = QRegExpValidator(QRegExp("((\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)"))   
        for LE in Norm_LE:
            LE.setValidator(validator_positif)
        self.Norm_Bins_comboBox.clear()
        self.Norm_Bins_comboBox.addItem('Check item')        
        self.Norm_Bins_comboBox.addItems([key.split()[0] for key in self.df_Keys if 'low' in key])
        self.Norm_Bins_comboBox.model().item(0).setEnabled(False)
        if sp.run_mode == 'eigenvalue': 
            for item in power_items:
                item.setEnabled(True)
            self.Norm_to_Heating_CB.stateChanged.connect(self.onStateChange)
            self.Norm_to_Power_CB.stateChanged.connect(self.onStateChange)
            self.Norm_to_Heating_CB.toggled.connect(self.Normalize_to_Power)
            self.Norm_to_Power_CB.toggled.connect(self.Normalize_to_Power)
            self.Power_LE.textChanged.connect(self.Normalize_to_Power)
            self.Heating_LE.textChanged.connect(self.Normalize_to_Power)
        else:
            for item in power_items:
                item.setEnabled(False)
        for item in Norm_Other:
            item.setEnabled(True)
        for item in Norm_CBox:
            item.setChecked(False)
        if any(any(element2 in element1 for element2 in self.Norm_Keys) for element1 in self.df_Keys):
            self.Norm_to_BW_CB.setEnabled(True)
            self.label_37.setEnabled(True)
            self.Norm_Bins_comboBox.setEnabled(True)
        else:
            self.Norm_to_BW_CB.setEnabled(False)
            self.label_37.setEnabled(False)
            self.Norm_Bins_comboBox.setEnabled(False)
        if any('energy' in item for item in self.df_Keys):
            self.Norm_to_UnitLethargy_CB.setEnabled(True)
            self.label_23.setEnabled(True)
        else:
            self.Norm_to_UnitLethargy_CB.setEnabled(False)
            self.label_23.setEnabled(False)

        self.Norm_to_BW_CB.toggled.connect(self.Normalize_to_Bin_Width)
        self.Norm_to_UnitLethargy_CB.toggled.connect(self.Normalize_Flux_to_Unit_of_Lethargy)
        self.Norm_to_Vol_CB.toggled.connect(self.Normalize_to_Volume)
        self.Vol_List_LE.textChanged.connect(lambda:self.Norm_to_Vol_CB.setChecked(False))

    def Normalizing(self):             # called by Plot_Scores
        if self.Norm_to_BW_CB.isChecked() or self.Norm_to_UnitLethargy_CB.isChecked() or self.Norm_to_Vol_CB.isChecked() or self.Norm_to_Power_CB.isChecked():
            self.Normalization = True 
        else:
            self.Normalization = False
            return
        if self.Norm_to_BW_CB.isChecked() and self.Norm_to_UnitLethargy_CB.isChecked() and len(self.Checked_Keys_Norm) == 1:
            self.showDialog('Warning', "Couldn't combine both energy bin widh and unit of lethargy in normalizing data! " )
            return
        
        df = self.df_filtered.copy()
        count_row = df.shape[0]
        self.Normalizing_Factor = np.ones(count_row)
        Checked_bins = [''] * self.n_filters
        key = [''] * self.n_filters        
        for idx in range(self.n_filters):
            Checked_bins[idx] = self.DATA[idx]['Checked_bins']
            key[idx] = self.DATA[idx]['KEY']  

        # Normalize to cells volume
        if self.Norm_to_Power_CB.isChecked() or self.Norm_to_Heating_CB.isChecked():
            self.Normalizing_Factor *= np.array(self.Power_Factor)             
        if self.Norm_to_Vol_CB.isChecked():  # and 'cell' in self.df_Keys: 
            self.Normalizing_Factor *= self.Volume_Factor
        if self.Norm_to_BW_CB.isChecked():
            self.Normalizing_Factor *= self.Bin_Factor
        elif self.Norm_to_UnitLethargy_CB.isChecked():
            self.Normalizing_Factor *= self.Lethargy_Factor
    
        # multiply scores and std. dev. by Normalizing_Factor
        df.loc[:,['mean', 'std. dev.']] *= np.array(self.Normalizing_Factor[:, None])  # to be verified
        df['multiplier'] = self.Normalizing_Factor.tolist()

        self.df_filtered_normalized = df
        self.Print_Formated_df(self.df_filtered_normalized.copy(), self.tally_id, self.editor)

        self.showDialog('','')

    @pyqtSlot(int)
    def onStateChange(self, state):
        if state == Qt.Checked:
            if self.sender() == self.Norm_to_Power_CB:
                self.Norm_to_Heating_CB.setChecked(False)
            elif self.sender() == self.Norm_to_Heating_CB:
                self.Norm_to_Power_CB.setChecked(False)

    def Normalize_to_Bin_Width(self, checked):
        self.Checked_Keys_Norm = [self.Norm_Bins_comboBox.itemText(i) for i in self.Norm_Bins_comboBox.checkedItems()]
        if checked:
            self.Norm_to_UnitLethargy_CB.setEnabled(False)
            if len(self.Checked_Keys_Norm) == 0:
                self.showDialog('Warning', 'Check item first for bin width normalization!')
                self.Norm_to_BW_CB.setChecked(False)
                return
            else:
                df = self.df_filtered.copy()
                count_row = df.shape[0]                
                self.Bin_Factor = [''] * self.n_filters
                self.Bin_Factor = np.ones(count_row)
                HIGH_Keys = [key for key in self.df_Keys if 'high' in key]

                for i in  range(self.n_filters): 
                    if i < len(self.Checked_Keys_Norm):
                        elem = self.Checked_Keys_Norm[i]
                        print(i, elem)
                        for key in self.Keys:
                            print(i, elem, key)
                            if elem in key and 'low' in key:
                                idx = self.Keys.index(key)
                                Low = df[key].values[:]
                                High = df[HIGH_Keys[idx]].values[:]
                                self.Bin_Factor *= [1. / (y - x) for x,y in zip(Low, High)]
        else:
            self.Norm_to_UnitLethargy_CB.setEnabled(True)
        
        if checked:
            yText = self.Curve_yLabel.text()
            for elem in self.Checked_Keys_Norm:
                i = self.Checked_Keys_Norm.index(elem)
                if self.UNIT[i] == '':
                    unit = ''
                else:
                    unit = ' /' + self.UNIT[i]
                if unit not in yText:
                    self.Curve_yLabel.setText(yText + unit)
                else:
                    self.Curve_yLabel.setText(yText)
        else:
            for elem in self.Norm_Available_Keys:
                i = self.Norm_Available_Keys.index(elem)
                unit = ' /' + self.UNIT[i]
                yText = self.Curve_yLabel.text().replace(unit, '')
            self.Curve_yLabel.setText(yText)

    def Normalize_to_Power(self):
        self.Factor_LE.clear()
        if self.Power_LE.text():
            if list(self.Power_LE.text())[-1] not in ['E', 'e', '+', '-']:
                Power = float(self.Power_LE.text())                  # MW = J/s
            else:
                return
        else:
            self.showDialog('Warning', 'Enter reactor power first!')
            return
        if self.Norm_to_Power_CB.isChecked() or self.Norm_to_Heating_CB.isChecked():
            if self.Norm_to_Power_CB.isChecked():
                if self.Power_LE.text():
                    Nu = float(self.Nu_LE.text())
                    Q = float(self.Q_LE.text()) * 1.6022E-13       # MeV * J/eV = J
                    Keff = self.keff
                    Factor = Power * Nu / Q / Keff      # 1/s 
                else:
                    Factor = 1.
            elif self.Norm_to_Heating_CB.isChecked():
                if self.Heating_LE.text():
                    if list(self.Heating_LE.text())[-1] not in ['E', 'e', '+', '-']:
                        H = float(self.Heating_LE.text())                  # MW = J/s
                    else:
                        return
                    H = float(self.Heating_LE.text()) * 1.6022E-19   # eV * J/eV  = J
                    if H != 0:
                        Factor = Power / H                  # 1/s
                    else:
                        Factor = 1.
                else:
                    Factor = 1.

            self.Keff_LE.setText(str("{:.5f}".format(self.keff)))
            self.Power_Factor = Factor
        else:
            self.Power_Factor = 1.
        self.Factor_LE.setText(str(self.Power_Factor))

        if self.Norm_to_Power_CB.isChecked() or self.Norm_to_Heating_CB.isChecked():
            yText = self.Curve_yLabel.text()
            if ' / s ' not in yText:
                self.Curve_yLabel.setText(yText + ' / s ')
            else:
                self.Curve_yLabel.setText(yText)
        else:
            yText = self.Curve_yLabel.text()
            self.Curve_yLabel.setText(yText.replace(' / s ', ''))
    
    def Normalize_Flux_to_Unit_of_Lethargy(self, checked):
        import math
        df = self.df_filtered.copy()
        count_row = df.shape[0]
        # Obtain the width of Lethargy Energy
        self.Lethargy_Factor = np.ones(count_row)
        if checked: 
            key = 'energy low [eV]'   
            if key in self.df_Keys:    
                idx = self.df_Keys.index(key)
                Low = df[key].values[:]
                High = df[self.df_Keys[idx+1]].values[:]
            self.Lethargy_Factor *= [1. / math.log(y / x) for x,y in zip(Low, High)]
            print(idx, self.Lethargy_Factor)
            self.Norm_to_BW_CB.setEnabled(False)
        else:
            self.Norm_to_BW_CB.setEnabled(True)

        if checked:    
            yText = self.Curve_yLabel.text()
            if ' / unit lethargy ' not in yText:
                self.Curve_yLabel.setText(yText + ' / unit lethargy ')
            else:
                self.Curve_yLabel.setText(yText)
        else:
            yText = self.Curve_yLabel.text()
            self.Curve_yLabel.setText(yText.replace(' / unit lethargy ', ''))

    def Normalize_to_Volume(self, checked):
        # Obtain the width of Lethargy Energy
        if checked:            
                self.Volumes = self.LE_to_List(self.Vol_List_LE)
                n_bins = 0
                if self.n_filters > 0:
                    if 'cell' in self.df_Keys:
                        idx = self.Keys.index('cell')
                        Checked_Cells = self.DATA[idx]['Checked_bins']
                        n_bins = len(Checked_Cells)
                    else:
                        n_bins = 1
                    if len(self.Volumes) != n_bins:
                        self.showDialog('Warning', "Numbers of checked cells and entered volumes don't match!\n")
                        self.Norm_to_Vol_CB.setChecked(False)
                        return
                else:
                    n_bins = 1
                    if len(self.Volumes) > n_bins:
                        self.showDialog('Warning', 'Only first value of volumes list will be affected to root cell!')
                        self.Volumes = [self.Volumes[0]]
                        self.Vol_List_LE.setText(str(self.Volumes[0]))
                        Checked_Cells = self.DATA['root']['Checked_bins']
                    elif len(self.Volumes) == 0:
                        self.showDialog('Warning', 'Enter volume of the root cell!')
                        self.Norm_to_Vol_CB.setChecked(False)
                        return

                df = self.df_filtered.copy()
                count_row = df.shape[0]                
                self.All_Volumes = np.ones(count_row)

                if 'cell' in self.df_Keys:
                    for key in self.Keys:
                        if key == 'cell':
                            idx = self.Keys.index(key)
                            cells = df[key].values[:]
                            for i in range(count_row):
                                j = Checked_Cells.index(cells[i])
                                self.All_Volumes[i] = self.Volumes[j]
                else:
                    for i in range(count_row):
                        self.All_Volumes[i] = self.Volumes[0]

                self.Volume_Factor = np.reciprocal(self.All_Volumes).tolist()
                
        if checked: 
            yText = self.Curve_yLabel.text()   
            if 'flux' in yText:
                if ' / cm ' in yText:
                    self.Curve_yLabel.setText(yText.replace(' / cm ', ' / cm\u00b2 '))
                else:
                    self.Curve_yLabel.setText(yText + ' / cm\u00b2 ')
            else:
                if ' / cc ' not in yText:
                    self.Curve_yLabel.setText(yText + ' / cc ')
        else:
            yText = self.Curve_yLabel.text()
            if 'flux' in yText:
                yText = self.Curve_yLabel.text().replace(' / cm\u00b2 ', ' / cm ')
            else:
                yText = self.Curve_yLabel.text().replace(' / cc ', '')
            self.Curve_yLabel.setText(yText)

    def LE_to_List(self, LineEdit):
        text = LineEdit.text().replace('(', '').replace(')', '')
        if '*' in text: 
            text = text.replace('*', ' * ')
        for separator in [',', ';', ':', ' ']:
            if separator in text:
                text = str(' '.join(text.replace(separator, ' ').split()))
        List = text.split()
        while '*' in List:    
            index = List.index('*')
            n = int(List[index + 1]) - 1
            List.pop(index + 1)
            List.pop(index)
            insert_list = [List[index - 1] + ' '] * n
            List = self.insert_list_at_index(List, insert_list, index)
        Volumes = [float(item) for item in List]
        return Volumes

    def insert_list_at_index(self, main_list, insert_list, index):
        # Copy the main_list to avoid modifying it in given place
        result_list = main_list.copy()
        
        # Insert each element of insert_list into result_list at the specified index
        for element in insert_list:
            result_list.insert(index, element.strip())
            index += 1
        
        return result_list

    def Labels_Font(self, ax, PLT):
        titleFontSize = int(self.TitleFont_CB.currentText())
        xFontSize = int(self.xFont_CB.currentText())
        yFontSize = int(self.yFont_CB.currentText())
        xRotation = int(self.xLabelRot_CB.currentText())
        LegendeFontSize = int(self.Legende_CB.currentText())
        ax.title.set_size(titleFontSize)
        ax.xaxis.set_tick_params(labelsize=xFontSize*0.75, rotation=xRotation)
        ax.yaxis.set_tick_params(labelsize=yFontSize*0.75)
        ax.xaxis.label.set_size(xFontSize)
        ax.yaxis.label.set_size(yFontSize)
        if xRotation != 0:
            PLT.setp(ax.get_xticklabels(), ha="right", rotation_mode="anchor")
        PLT.rc('legend',fontsize=LegendeFontSize)
 
    def Change_Scales(self, PLT, Graph_type):
        if 'Keff' not in self.Tally_id_comboBox.currentText():
            if Graph_type in ['Lin-Lin','Scatter', 'Stairs']:  #'Stacked Area'
                if self.xLog_CB.isChecked():
                    if self.Plot_By_Key not in ['cell', 'surface', 'nuclide', 'score', 'material', 'universe']:
                        PLT.set_xscale('log')
        elif 'Keff' in self.Tally_id_comboBox.currentText():
            if self.xLog_CB.isChecked():
                PLT.set_xscale('log')
        if self.yLog_CB.isChecked():    
            PLT.set_yscale('log')

    def set_Scales(self): 
        if self.Graph_type_CB.currentIndex() == 0:
            for elm in self.buttons:
                elm.setEnabled(False)        
        else:
            if 'MeshFilter' in self.Filters_comboBox.currentText():
                self.Graph_type_CB.setCurrentIndex(0)
                self.Graph_type_CB.setEnabled(False)
                self.Plot_by_CB.clear()            
            else:
                if 'Batches' not in self.Filters_comboBox.currentText():
                    self.Plot_By_Key = self.Plot_by_CB.currentText()
                    if self.Plot_By_Key in ['mu low', 'mu center of bin']:
                        self.Curve_xLabel.setText('$\mu$')
                    elif 'energy' in self.Plot_By_Key:
                        self.Curve_xLabel.setText(self.Plot_By_Key.split(' ')[0] + ' / eV')
                    elif 'polar' in self.Plot_By_Key or 'azimuthal' in self.Plot_By_Key:
                        self.Curve_xLabel.setText(self.Plot_By_Key.split(' ')[0] + ' / rad')
                    elif 'cell' in self.Plot_By_Key and len(self.Plot_By_Key) > 4:
                        self.Curve_xLabel.setText(self.Plot_By_Key.replace('cell', 'cell '))
                    else:
                        self.Curve_xLabel.setText(self.Plot_By_Key)
                    for elm in self.buttons:
                        elm.setEnabled(True)
                    if self.Graph_type_CB.currentText() in ['Bar', 'Stacked Bars', 'Stacked Area']:
                        self.xLog_CB.setEnabled(False)
                    elif self.Graph_type_CB.currentText() == 'Scatter':
                        if self.Plot_By_Key in ['cell', 'cellfrom', 'cellborn', 'distribcell', 'material', 
                                                'universe', 'surface', 'particle' ,'collision', 'nuclide', 'score']:
                            self.xLog_CB.setEnabled(False)  
                        else:
                            self.xLog_CB.setEnabled(True)  
                    else:
                        pass           
  
    def plot_grid_settings(self):
        if self.MinorGrid_CB.isChecked():
            self.which_grid = 'both'
        else:
            self.which_grid = 'major'
        if self.xGrid_CB.isChecked() and self.yGrid_CB.isChecked():
            self.grid = True
            self.which_axis = 'both'
        elif self.xGrid_CB.isChecked() and not self.yGrid_CB.isChecked():
            self.grid = True
            self.which_axis = 'x'
        elif not self.xGrid_CB.isChecked() and self.yGrid_CB.isChecked() :
            self.grid = True
            self.which_axis = 'y'
        else:
            self.grid = False
            self.which_axis = ''

    def Activate_Curve_Type(self):
        for i in range(1,6):
            self.Graph_type_CB.model().item(i).setEnabled(True)

    def Deactivate_Curve_Type(self):
        for i in [3, 5]:
            self.Graph_type_CB.model().item(i).setEnabled(False)

    def Mesh_settings(self, enabled):
        self.score_plot_PB.setEnabled(False)
        self.Bins_comboBox[self.Filters_comboBox.currentIndex() - 1].clear()
        if os.path.isfile(self.sp_file):
            tally_id = int(self.Tally_id_comboBox.currentText())
            if self.Tally_id_comboBox.currentIndex() > 0 and 'Keff' not in self.Tally_id_comboBox.currentText():
                if self.Filters_comboBox.currentIndex() > 0:
                    filter_id = self.filter_ids[self.Filters_comboBox.currentIndex() - 1]
                    self.Bins_comboBox[self.Filters_comboBox.currentIndex() - 1].addItems(['Select bin', 'All bins'])
                    self.Bins_comboBox[self.Filters_comboBox.currentIndex() - 1].model().item(0).setEnabled(False)
                    if self.Mesh_xy_RB.isChecked():
                        self.list_axis = ['slice at z = ' + str("{:.1E}".format(z_)) for z_ in self.z]
                        self.xlabel.setText('xlabel')
                        self.ylabel.setText('ylabel')
                        self.Curve_xLabel.setText('x/cm')
                        self.Curve_yLabel.setText('y/cm')
                        self.spinBox.setValue(1)
                        self.spinBox_2.setValue(1)
                        self.spinBox.setMinimum(1)
                        self.spinBox.setMaximum(self.mesh_dimension[0])
                        self.spinBox_2.setMinimum(1)
                        self.spinBox_2.setMaximum(self.mesh_dimension[1])
                    elif self.Mesh_xz_RB.isChecked():
                        self.list_axis = ['slice at y = ' + str("{:.1E}".format(y_)) for y_ in self.y]
                        self.xlabel.setText('xlabel')
                        self.ylabel.setText('zlabel')
                        self.Curve_xLabel.setText('x/cm')
                        self.Curve_yLabel.setText('z/cm')
                        self.spinBox.setValue(1)
                        self.spinBox_2.setValue(1)
                        self.spinBox.setMinimum(1)
                        self.spinBox.setMaximum(self.mesh_dimension[0])
                        self.spinBox_2.setMaximum(self.mesh_dimension[2])
                    elif self.Mesh_yz_RB.isChecked():
                        self.list_axis = ['slice at x = ' + str("{:.1E}".format(x_)) for x_ in self.x]
                        self.xlabel.setText('ylabel')
                        self.ylabel.setText('zlabel')
                        self.Curve_xLabel.setText('y/cm')
                        self.Curve_yLabel.setText('z/cm')
                        self.spinBox.setValue(1)
                        self.spinBox_2.setValue(1)
                        self.spinBox_2.setMinimum(1)
                        self.spinBox.setMaximum(self.mesh_dimension[1])
                        self.spinBox_2.setMaximum(self.mesh_dimension[2])

                    bins = self.list_axis
                    self.Tallies[tally_id][filter_id]['bins'] = bins
                    self.Bins_comboBox[self.Filters_comboBox.currentIndex() - 1].addItems(bins)
                    for i in range(len(bins) + 1):
                        self.Bins_comboBox[self.Filters_comboBox.currentIndex() - 1].setItemChecked(i, False)
                    self.Tallies[tally_id][filter_id]['Checked_bins_indices'].clear()
    
    def Mesh_scores(self):
        df = self.df
        self.mean = {}

        if self.Mesh_xy_RB.isChecked():
            self.dim1 = self.mesh_dimension[0]
            self.dim2 = self.mesh_dimension[1]
            self.LL1 = self.mesh_LL[0]
            self.LL2 = self.mesh_LL[1]
            self.UR1 = self.mesh_UR[0]
            self.UR2 = self.mesh_UR[1]
        elif self.Mesh_xz_RB.isChecked():
            self.dim1 = self.mesh_dimension[0]
            self.dim2 = self.mesh_dimension[2]
            self.LL1 = self.mesh_LL[0]
            self.LL2 = self.mesh_LL[2]
            self.UR1 = self.mesh_UR[0]
            self.UR2 = self.mesh_UR[2]
        elif self.Mesh_yz_RB.isChecked():
            self.dim1 = self.mesh_dimension[1]
            self.dim2 = self.mesh_dimension[2]
            self.LL1 = self.mesh_LL[1]
            self.LL2 = self.mesh_LL[2]
            self.UR1 = self.mesh_UR[1]
            self.UR2 = self.mesh_UR[2]
        index = self.filter_ids.index(self.filter_id)
        key = self.Tallies[self.tally_id]['filter_types'][index] + ' ' + str(self.mesh_id)
        self.mean[key] = {}

        for bin in self.checked_bins_indices:
            self.mean[key][bin-1] = {}
            for score in self.selected_scores:
                if score != '':
                    self.mean[key][bin-1][score] = {}
                    Score = df[df['score'] == score]
                    for nuclide in self.selected_nuclides:
                        if nuclide != '':
                            self.mean[key][bin-1][score][nuclide] = []
                            Scoren = Score[Score['nuclide'] == nuclide]
                            if self.Mesh_xy_RB.isChecked():
                                Scoren = Scoren[Scoren[key]['z'] == bin-1]
                                for x in range(1,self.spinBox.value()+1):
                                    for y in range(1,self.spinBox_2.value()+1):
                                        Scorexy = Scoren[Scoren[key]['x'] == x]
                                        Scorexy = Scorexy[Scorexy[key]['y'] == y]
                            elif self.Mesh_xz_RB.isChecked():
                                Scoren = Scoren[Scoren[key]['y'] == bin-1]
                                for x in range(1,self.spinBox.value()+1):
                                    for z in range(1,self.spinBox_2.value()+1):
                                        Scorexz = Scoren[Scoren[key]['x'] == x]
                                        Scorexz = Scorexz[Scorexz[key]['z'] == z]
                            elif self.Mesh_yz_RB.isChecked():
                                Scoren = Scoren[Scoren[key]['x'] == bin-1]
                                for y in range(1,self.spinBox.value()+1):
                                    for z in range(1,self.spinBox_2.value()+1):
                                        Scoreyz = Scoren[Scoren[key]['y'] == y]
                                        Scoreyz = Scoreyz[Scoreyz[key]['z'] == z]
                            
                            self.mean[key][bin-1][score][nuclide] = Scoren['mean'].to_numpy()

    def Plot_Mesh(self):
        index = self.filter_ids.index(self.filter_id)
        key = self.Tallies[self.tally_id]['filter_types'][index] + ' ' + str(self.mesh_id)
        x = np.linspace(self.LL1, self.UR1, num=self.dim1 + 1)
        y = np.linspace(self.LL2, self.UR2, num=self.dim2 + 1)
        for bin in self.checked_bins_indices:
            for score in self.selected_scores:
                if score != '':
                    for nuclide in self.selected_nuclides:
                        if nuclide != '':
                            mean = self.mean[key][bin-1][score][nuclide].reshape((self.dim1, self.dim2))
                            plt.subplots()
                            if self.yLog_CB.isChecked() or self.xLog_CB.isChecked():
                                if self.yLog_CB.isChecked():
                                    im = plt.imshow(mean, cmap=cm.rainbow, norm=colors.LogNorm(), origin='lower', extent=[x.min(), x.max(), y.min(), y.max()])
                                    plt.show()
                                if self.xLog_CB.isChecked():
                                    im = plt.imshow(mean, cmap=cm.rainbow, interpolation='spline36', origin='lower', extent=[x.min(), x.max(), y.min(), y.max()])
                                    plt.show()
                            else:
                                plt.imshow(mean, interpolation='none', cmap='jet', origin='lower',
                                        extent=[x.min(), x.max(), y.min(), y.max()])
                            #plt.colorbar()
                            if score == 'flux':
                                Suptitle = score + ' / cm'
                            else:
                                Suptitle = score + ' rate '
                            if len(self.tally.filters[0].mesh._grids) == 3:
                                Suptitle = Suptitle + str(self.Tallies[self.tally_id][self.filter_id]['bins'][bin-2]).replace('slice', '') + (' cm')
                            else:
                                Suptitle = Suptitle + ' integrated on z axis'

                            plt.suptitle(Suptitle, fontsize=int(self.TitleFont_CB.currentText()), horizontalalignment='center')
                            if nuclide != 'total':
                                plt.title('Nuclide : ' + nuclide, fontsize=int(self.TitleFont_CB.currentText()))
                            plt.xlabel(self.Curve_xLabel.text(), fontsize=int(self.xFont_CB.currentText()))
                            plt.ylabel(self.Curve_yLabel.text(), fontsize=int(self.yFont_CB.currentText()))
                            plt.xticks(fontsize=int(self.xFont_CB.currentText())*0.75, rotation=int(self.xLabelRot_CB.currentText()))
                            plt.yticks(fontsize=int(self.yFont_CB.currentText())*0.75)
                            plt.colorbar().ax.tick_params(labelsize=int(self.xFont_CB.currentText())*0.75)
        plt.tight_layout()
        plt.show()

    def Plot_Distribcell(self):       # needs more developemnt
        # Distributed Cell Tally Visualization
        # This example demonstrates how a tally with a DistribcellFilter can be plotted using the openmc.lib module 
        # to determine geometry information. First, we'll begin by creating a simple model with a hexagonal lattice.
        # Jupiter example from https://nbviewer.org/gist/paulromano/f2fbf3d4731e324b6f5ab31ef3fcaa26
        #
        # ***********************************
        self.showDialog('Warning', 'Under development!')
        return
        # ***********************************
        import openmc.lib
        cwd = os.getcwd()
        resolution = (6000, 6000)
        img = np.full(resolution, np.nan)
        xmin, xmax = -30., 30.
        ymin, ymax = -30., 30.
        idx = self.filter_ids.index(self.filter_id)
        key = self.Tallies[self.tally_id]['filter_types'][idx]
        x = np.linspace(xmin, xmax, num=119)
        y = np.linspace(ymin, ymax, num=119)
        df = self.df.loc[(self.df['score'].isin(self.selected_scores)) & (self.df['nuclide'].isin(self.selected_nuclides))]
        df = df.loc[self.df[self.Keys[idx]].isin(self.Key_Selected_Bins[idx])].copy()
        '''for score in self.selected_scores:
            if score != '':
                for nuclide in self.selected_nuclides:
                    if nuclide != '':
                        mean = df[df.score == score][df.nuclide == nuclide]'''
        plt.subplots()
        mean = df
        #os.chdir(os.path.dirname(self.sp_file))
        if True: #with openmc.lib.run_in_memory():
            for row, y in enumerate(np.linspace(ymin, ymax, resolution[0])):
                for col, x in enumerate(np.linspace(xmin, xmax, resolution[1])):
                    try:
                        pass
                        # For each (x, y, z) point, determine the cell and distribcell index
                        cell, distribcell_index = openmc.lib.find_cell((x, y, 0.))
                    except openmc.exceptions.GeometryError:
                        # If a point appears outside the geometry, you'll get a GeometryError exception.
                        # These lines catch the exception and continue on
                        continue
                    print( self.tally.filters[idx].bins[0])
                    if cell.id == self.tally.filters[idx].bins[0]:  # fuel_cell.id:
                        # When the cell ID matches, we set the corresponding pixel in the image using the
                        # distribcell index. Note that we're taking advantage of the fact that the i-th element
                        # in the flux array corresponds to the i-th distribcell instance.
                        return
                        img[row, col] = mean[distribcell_index]
        options = {
                    'origin': 'lower',
                    'extent': (xmin, xmax, ymin, ymax),
                    'vmin': 0.03,
                    'vmax': 0.06,
                    'cmap': 'RdYlBu_r',
                }
        plt.imshow(img, **options)
        plt.xlabel('x [cm]')
        plt.ylabel('y [cm]')
        plt.colorbar()

        plt.xlabel(self.Curve_xLabel.text(), fontsize=int(self.xFont_CB.currentText()))
        plt.ylabel(self.Curve_yLabel.text(), fontsize=int(self.yFont_CB.currentText()))
        plt.xticks(fontsize=int(self.xFont_CB.currentText())*0.75, rotation=int(self.xLabelRot_CB.currentText()))
        plt.yticks(fontsize=int(self.yFont_CB.currentText())*0.75)
        plt.colorbar().ax.tick_params(labelsize=int(self.xFont_CB.currentText())*0.75)
        plt.tight_layout()
        plt.show()
        #os.chdir(cwd)

    def box_plot(self):
        print('Ploted Scores : \n', self.df.to_string())
        key = self.Plot_by_CB.currentText()
        print('selected key : ', key)
        if key != 'score':
            #if key == 'nuclide':
            for score in self.selected_scores:
                bp = self.df[self.df.score == score].boxplot(column='mean', by=key)
                plt.show()
                if score not in ['flux', 'current']:    
                    plt.title(score + ' RR')
                else:    
                    plt.title(score)
        else:
            if 'cell' in self.df.keys():
                bp = self.df.boxplot(column='mean', by=key)
                plt.show()
                for cell in self.Checked_cells:
                    bp = self.df[self.df.cell == cell].boxplot(column='mean', by=key)
                    plt.show()
                    plt.title('RR in cell ' + str(cell))
            else:
                bp = self.df.boxplot(column='mean', by=key)
                plt.show()
                plt.title('RR ')

    def Reset_Plot_Settings(self):
        self.xLabelRot_CB.setCurrentIndex(0)
        self.TitleFont_CB.setCurrentIndex(8)
        self.xFont_CB.setCurrentIndex(7)
        self.yFont_CB.setCurrentIndex(7)
        self.Legende_CB.setCurrentIndex(6)
        self.Graph_Layout_CB.setCurrentIndex(0)
        self.Graph_type_CB.setCurrentIndex(0)
        for CB in [self.xLog_CB, self.yLog_CB, self.Add_error_bars_CB, self.xGrid_CB, self.yGrid_CB, self.MinorGrid_CB]:
            CB.setChecked(False)

    def normalOutputWritten(self,text):
        self.cursor = self.editor.textCursor()
        self.cursor.insertText(text)
        self.editor.setTextCursor(self.cursor)

    def broadning_pulse_height(self):
        # ref. : https://github.com/openmc-dev/openmc-notebooks/blob/main/gamma-detector.ipynb
        try:
            sp = openmc.StatePoint(self.sp_file)
            tally = sp.get_tally(id=tally_id)
            pulse_height_values = tally.get_values(scores=['pulse-height']).flatten()
            # we want to display the pulse-height value in the center of the bin
            energy_bins = self.Checked_energies
            energy_bin_centers = energy_bins[1:] + 0.5 * (energy_bins[1] - energy_bins[0])
            plt.figure()
            plt.semilogy(energy_bin_centers, pulse_height_values)

            # plot the strongest sources as vertical lines
            plt.axvline(x=800_000, color="red", ls=":")     # source_1
            plt.axvline(x=661_700, color="red", ls=":")     # source_2

            plt.xlabel('Energy [eV]')
            plt.ylabel('Counts')
            plt.title('Pulse Height Values')
            plt.grid(True)
            plt.tight_layout()

            a, b, c = 1000, 4, 0.0002
            number_broadening_samples = 1e6
            samples = np.random.choice(energy_bin_centers[1:], size=int(number_broadening_samples), p=pulse_height_values[1:]/np.sum(pulse_height_values[1:]))
            broaded_pulse_height_values = gauss(samples)

            broaded_spectrum, _ = np.histogram(broaded_pulse_height_values, bins=energy_bins)
            renormalized_broaded_spectrum = broaded_spectrum / np.sum(broaded_spectrum) * np.sum(pulse_height_values[1:])

            plt.figure()

            plt.semilogy(energy_bin_centers[1:], pulse_height_values[1:], label="original simulation result")
            plt.semilogy(energy_bin_centers[1:], renormalized_broaded_spectrum[1:], label="broaded detector response")

            # plot the strongest sources as vertical lines
            plt.axvline(x=800_000, color="red", ls=":", label="gamma source")     # source_1
            plt.axvline(x=661_700, color="red", ls=":")                           # source_2

            plt.legend()
            plt.xlabel('Energy [eV]')
            plt.ylabel('Counts')
            plt.title('Pulse Height Values')
            plt.grid(True)
            plt.tight_layout()
        except:
            return

    def gauss(self, E, a, b, c):
        sigma = (a + b * (E + c * E**2)**0.5) / (2 * (2 * np.log(2))**0.5)
        return np.random.normal(loc=E, scale=sigma)

    #############################################################################
    #                        Editor methods and buttons
    #############################################################################

    def Define_Buttons(self):
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #++++++++++++++++++++++++++++++++++ D E F I N E B U T T O N S ++++++++++++++++++++++++++++++++++++++++
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        ### begin toolbar
        tb = self.addToolBar("File")
        tb.setContextMenuPolicy(Qt.PreventContextMenu)
        tb.setIconSize(QSize(QSize(24, 24)))
        tb.setMovable(False)
        tb.setAllowedAreas(Qt.AllToolBarAreas)
        tb.setFloatable(False)
        ### file buttons
        self.newAct = QAction(QIcon("src/icons/new24.png"), "&New", self, shortcut=QKeySequence.New,
                statusTip="new file", triggered=self.newFile)
        tb.addAction(self.newAct)

        self.openAct = QAction(QIcon("src/icons/open24.png"), "&Open", self, shortcut=QKeySequence.Open,
                statusTip="open file", triggered=self.openFile)
        tb.addAction(self.openAct)

        self.saveAct = QAction(QIcon("src/icons/document-save.png"), "&Save", self, shortcut=QKeySequence.Save,
                statusTip="save file", triggered=self.fileSave)
        tb.addAction(self.saveAct)

        self.saveAsAct = QAction(QIcon("src/icons/document-save-as.png"), "&Save as ...", self, shortcut=QKeySequence.SaveAs,
                statusTip="save file as ...", triggered=self.fileSaveAs)
        tb.addAction(self.saveAsAct)
        
        self.pdfAct = QAction(QIcon("src/icons/pdf.png"), "export PDF", self, shortcut="Ctrl+Shift+p",
                statusTip="save file as PDF", triggered=self.exportPDF)
        tb.addAction(self.pdfAct)
        self.Landscape_CB = QtWidgets.QCheckBox(self, text="Landscape", checkable=True)
        tb.addWidget(self.Landscape_CB)
        #tb.addAction(QAction("Landscape", self, checkable=True))

        ### color chooser
        tb.addSeparator()
        tb.addAction(QIcon('src/icons/color.png'), "change Color", self.changeColor)
        tb.addSeparator()
        tb.addAction(QIcon("src/icons/eraser.png"), "clear Output Label", self.clearLabel)
        tb.addSeparator()
        
        ### print preview
        self.printPreviewAct = QAction(QIcon("src/icons/document-print-preview.png"), "Print Preview", self, shortcut="Ctrl+Shift+P",
                statusTip="Preview Document", triggered=self.handlePrintPreview)
        tb.addAction(self.printPreviewAct)
        ### print
        self.printAct = QAction(QIcon("src/icons/document-print.png"), "Print", self, shortcut=QKeySequence.Print,
                statusTip="Print Document", triggered=self.handlePrint)
        tb.addAction(self.printAct) 

        tb.addSeparator()
        self.comboSize = QComboBox(tb)
        tb.addSeparator()
        self.comboSize.setObjectName("comboSize")
        tb.addWidget(self.comboSize)
        self.comboSize.setEditable(True)

        db = QFontDatabase()
        for size in db.standardSizes():
            self.comboSize.addItem("%s" % (size))
        self.comboSize.addItem("%s" % (90))
        self.comboSize.addItem("%s" % (100))
        self.comboSize.addItem("%s" % (160))
        self.comboSize.activated[str].connect(self.textSize)
        self.comboSize.setCurrentIndex(
                self.comboSize.findText(
                        "%s" % (QApplication.font().pointSize()))) 
        tb.addSeparator()
        self.bgAct = QAction(QIcon("src/icons/sbg_color.png"), "change Background Color",self, triggered=self.changeBGColor)
        self.bgAct.setStatusTip("change Background Color")
        tb.addSeparator()
        tb.addAction(self.bgAct)
        tb.addSeparator()

        # checkBox for highlighting
        self.checkbox = QCheckBox('Highlighting', self)
        tb.addWidget(self.checkbox)
        self.checkbox.stateChanged.connect(self.HLAct)

        ### find / replace toolbar
        #self.addToolBarBreak()
        tbf = self.addToolBar("Find")
        tbf.setContextMenuPolicy(Qt.PreventContextMenu)
        tbf.setMovable(False)
        tbf.setIconSize(QSize(iconsize))
        self.findfield = QLineEdit()
        self.findfield.addAction(QIcon("icons/edit-find.png"), QLineEdit.LeadingPosition)
        self.findfield.setClearButtonEnabled(True)
        self.findfield.setFixedWidth(150)
        self.findfield.setPlaceholderText("find")
        self.findfield.setToolTip("press RETURN to find")
        self.findfield.setText("")
        ft = self.findfield.text()
        self.findfield.returnPressed.connect(self.findText)
        tbf.addWidget(self.findfield)
        tbf.addSeparator()
        self.gotofield = QLineEdit()
        self.gotofield.addAction(QIcon("src/icons/go-next.png"), QLineEdit.LeadingPosition)
        self.gotofield.setClearButtonEnabled(True)
        self.gotofield.setFixedWidth(120)
        self.gotofield.setPlaceholderText("go to line")
        self.gotofield.setToolTip("press RETURN to go to line")
        self.gotofield.returnPressed.connect(self.gotoLine)
        tbf.addWidget(self.gotofield)
        tbf.addSeparator()
        tb.addWidget(tbf)
        ## addStretch
        empty = QWidget();
        empty.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Preferred);
        tb.addWidget(empty)
        self.exitAct = QAction(QIcon("src/icons/quit.png"), "exit", self, shortcut=QKeySequence.Quit,
                statusTip="Exit", triggered=self.Close)
        tb.addAction(self.exitAct)

        self.filemenu=self.menuFile 
        self.separatorAct = self.filemenu.addSeparator()
        self.filemenu.addAction(self.newAct)
        self.filemenu.addAction(self.openAct)
        self.filemenu.addAction(self.saveAct)
        self.filemenu.addAction(self.saveAsAct)
        self.filemenu.addSeparator()
        self.filemenu.addAction(self.pdfAct)
        self.filemenu.addSeparator()
        """for i in range(self.MaxRecentFiles):
            self.filemenu.addAction(self.recentFileActs[i])"""
        self.updateRecentFileActions()
        self.filemenu.addSeparator()

        self.clearRecentAct = QAction(QIcon("src/icons/close.png"), "clear Recent Files List", self, triggered=self.clearRecentFiles)
        self.filemenu.addAction(self.clearRecentAct)
        self.filemenu.addSeparator()

        editmenu = self.menuEdit
        editmenu.addAction(QAction(QIcon('src/icons/undo.png'), "Undo", self, triggered = self.editor.undo, shortcut = "Ctrl+u"))
        editmenu.addAction(QAction(QIcon('src/icons/redo.png'), "Redo", self, triggered = self.editor.redo, shortcut = "Shift+Ctrl+u"))
        editmenu.addSeparator()
        editmenu.addAction(QAction(QIcon('src/icons/copy.png'), "Copy", self, triggered = self.editor.copy, shortcut = "Ctrl+c"))
        editmenu.addAction(QAction(QIcon('src/icons/cut.png'), "Cut", self, triggered = self.editor.cut, shortcut = "Ctrl+x"))
        editmenu.addAction(QAction(QIcon('src/icons/paste.png'), "Paste", self, triggered = self.editor.paste, shortcut = "Ctrl+v"))
        editmenu.addAction(QAction(QIcon('src/icons/delete.png'), "Delete", self, triggered = self.editor.cut, shortcut = "Del"))
        editmenu.addSeparator()
        editmenu.addAction(QAction(QIcon('src/icons/select-all.png'), "Select All", self, triggered = self.editor.selectAll, shortcut = "Ctrl+a"))
        editmenu.addSeparator()

        for CB in [self.TitleFont_CB, self.xFont_CB, self.yFont_CB, self.Legende_CB]:
            CB.setEditable(True)
            db = QFontDatabase()
            for size in db.standardSizes():
                CB.addItem("%s" % (size))
            CB.addItem("%s" % (90))
            CB.addItem("%s" % (100))
            CB.addItem("%s" % (160))
        
        self.xLabelRot_CB.addItems(['0', '5', '15', '25', '30', '45', '60', '75', '90'])
        self.Reset_Plot_Settings()
        #self.readSettings()
        #self.lineLabel1.setText("self.root is: " + str(self.sp_file), 0)

        # Status bar
        self.lineLabel1 = QLabel()
        self.lineLabel2 = QLabel()
        self.lineLabel3 = QLabel()
        self.lineLabel2.setAlignment(QtCore.Qt.AlignCenter)
        self.lineLabel3.setAlignment(QtCore.Qt.AlignCenter)
        widget = QWidget(self)
        widget.setLayout(QHBoxLayout())
        widget.layout().addWidget(self.lineLabel1)
        widget.layout().addWidget(VLine())
        widget.layout().addWidget(self.lineLabel2)
        widget.layout().addWidget(VLine())
        widget.layout().addWidget(self.lineLabel3)
        self.statusBar.addWidget(widget, 1)

    def Close(self):
        import matplotlib.pyplot as plt

        box = QMessageBox()
        box.setIcon(QMessageBox.Question)
        box.setWindowTitle('Close gui!')
        box.setText("<h4><p>Many opened figures will be closed.</p>\n" \
                        "<p>Choose action</p></h4>")
        box.setStandardButtons(QMessageBox.Yes| QMessageBox.Discard | QMessageBox.No)
        #box.setStandardButtons(QMessageBox.Yes| QMessageBox.Discard | QMessageBox.No | QMessageBox.Cancel)
        buttonY = box.button(QMessageBox.Yes)
        buttonY.setText('keep all')
        buttonD = box.button(QMessageBox.Discard)
        buttonD.setText('close figures only')
        buttonN = box.button(QMessageBox.No)
        buttonN.setText('Close all')        
        
        box.exec_()

        if box.clickedButton() == buttonY:
            return 
        elif box.clickedButton() == buttonD:
            plt.close('all')
                    
        elif box.clickedButton() == buttonN:
            plt.close('all')
            self.close()

    def HLAct(self):
        if self.tabWidget_2.currentIndex() == 0:
            editor = self.editor
        elif self.tabWidget_2.currentIndex() == 1:
            editor = self.editor1
        if self.checkbox.isChecked():
            from src.syntax_py import Highlighter
            self.highlighter = Highlighter(editor.document())
        else:
            from src.syntax import Highlighter
            self.highlighter = Highlighter(editor.document())

    """def getLineNumber(self):
        if self.tabWidget_2.currentIndex() == 0:
            editor = self.editor
        elif self.tabWidget_2.currentIndex() == 1:
            editor = self.editor1
        editor.moveCursor(self.editor.cursor.StartOfLine)
        linenumber = self.editor.textCursor().blockNumber() + 1
        return linenumber"""

    def goToLine(self, ft):
        if self.tabWidget_2.currentIndex() == 0:
            editor = self.editor
        elif self.tabWidget_2.currentIndex() == 1:
            editor = self.editor1
        editor.moveCursor(int(self.gofield.currentText()),
                                QTextCursor.MoveAnchor) ### not working

    def findText(self):
        if self.tabWidget_2.currentIndex() == 0:
            editor = self.editor
        elif self.tabWidget_2.currentIndex() == 1:
            editor = self.editor1
        word = self.findfield.text()
        if editor.find(word):
            linenumber = editor.textCursor().blockNumber() + 1
            self.lineLabel1.setText("found <b>'" + self.findfield.text() + "'</b> at Line: " + str(linenumber))
            editor.centerCursor()
        else:
            self.lineLabel1.setText("<b>'" + self.findfield.text() + "'</b> not found")
            editor.moveCursor(QTextCursor.Start)
            if editor.find(word):
                linenumber = editor.textCursor().blockNumber() + 1
                self.lineLabel1.setText("found <b>'" + self.findfield.text() + "'</b> at Line: " + str(linenumber))
                editor.centerCursor()

    def gotoLine(self):
        if self.tabWidget_2.currentIndex() == 0:
            editor = self.editor
        elif self.tabWidget_2.currentIndex() == 1:
            editor = self.editor1
        ln = int(self.gotofield.text())
        linecursor = QTextCursor(editor.document().findBlockByLineNumber(ln-1))
        editor.moveCursor(QTextCursor.End)
        editor.setTextCursor(linecursor)

    def changeBGColor(self):
        if self.tabWidget_2.currentIndex() == 0:
            editor = self.editor
        elif self.tabWidget_2.currentIndex() == 1:
            editor = self.editor1
        all = editor.document().toHtml()
        bgcolor = all.partition("<body style=")[2].partition(">")[0].partition('bgcolor="')[2].partition('"')[0]
        if not bgcolor == "":
            col = QColorDialog.getColor(QColor(bgcolor), self)
            if not col.isValid():
                return
            else:
                colorname = col.name()
                new = all.replace("bgcolor=" + '"' + bgcolor + '"', "bgcolor=" + '"' + colorname + '"')
                editor.document().setHtml(new)
        else:
            col = QColorDialog.getColor(QColor("#FFFFFF"), self)
        if not col.isValid():
            return
        else:
            all = editor.document().toHtml()
            body = all.partition("<body style=")[2].partition(">")[0]
            newbody = body + "bgcolor=" + '"' + col.name() + '"'
            new = all.replace(body, newbody)
            editor.document().setHtml(new)
        bgcolor = "background-color: " + col.name()
        editor.setStyleSheet(bgcolor)

    def mergeFormatOnWordOrSelection(self, format):
        if self.tabWidget_2.currentIndex() == 0:
            editor = self.editor
        elif self.tabWidget_2.currentIndex() == 1:
            editor = self.editor1
        cursor = editor.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)

        cursor.mergeCharFormat(format)
        editor.mergeCurrentCharFormat(format)

    def textSize(self, pointSize):
        pointSize = float(self.comboSize.currentText())
        if pointSize > 0:
            fmt = QTextCharFormat()
            fmt.setFontPointSize(pointSize)
            self.mergeFormatOnWordOrSelection(fmt)

    def clearRecentFiles(self):
        self.settings.remove('recentFileList')
        self.recentFileActs = []
        self.settings.sync()

    def infobox(self,title, message):
        QMessageBox(QMessageBox.Information, title, message, QMessageBox.NoButton, self, Qt.Dialog|Qt.NoDropShadowWindowHint).show()

    def handlePrint(self):
        if self.tabWidget_2.currentIndex() == 0:
            editor = self.editor
        elif self.tabWidget_2.currentIndex() == 1:
            editor = self.editor1
        if editor.toPlainText() == "":
            self.lineLabel1.setText("no text")
        else:
            dialog = QtPrintSupport.QPrintDialog()
            if dialog.exec_() == QDialog.Accepted:
                self.handlePaintRequest(dialog.printer())
                self.lineLabel1.setText("Document printed")

    def handlePrintPreview(self):
        if self.tabWidget_2.currentIndex() == 0:
            editor = self.editor
        elif self.tabWidget_2.currentIndex() == 1:
            editor = self.editor1
        if editor.toPlainText() == "":
            self.lineLabel1.setText("no text")
        else:
            dialog = QtPrintSupport.QPrintPreviewDialog()
            dialog.setFixedSize(900,650)
            dialog.paintRequested.connect(self.handlePaintRequest)
            dialog.exec_()
            self.lineLabel1.setText("Print Preview closed")

    def handlePaintRequest(self, printer):
        if self.tabWidget_2.currentIndex() == 0:
            editor = self.editor
        elif self.tabWidget_2.currentIndex() == 1:
            editor = self.editor1
        printer.setDocName(self.filename)
        document = editor.document()
        document.print_(printer)

    def findNextWord(self):
        if self.tabWidget_2.currentIndex() == 0:
            editor = self.editor
        elif self.tabWidget_2.currentIndex() == 1:
            editor = self.editor1
        if editor.textCursor().selectedText() == "":
            tc = editor.textCursor()
            tc.select(QTextCursor.WordUnderCursor)
            rtext = tc.selectedText()
        else:
            rtext = editor.textCursor().selectedText()
        self.findfield.setText(rtext)
        self.findText()

    ### QPlainTextEdit contextMenu
    def contextMenuRequested(self, point):
        if self.tabWidget_2.currentIndex() == 0:
            editor = self.editor
        elif self.tabWidget_2.currentIndex() == 1:
            editor = self.editor1
        cmenu = QMenu()
        cmenu = editor.createStandardContextMenu()
        cmenu.addSeparator()
        cmenu.addAction(self.jumpToAct)
        cmenu.addSeparator()
        cmenu.addAction(QIcon.fromTheme("gtk-find-"),"find this (F10)", self.findNextWord)
        cmenu.addAction(self.texteditAction)
        cmenu.addSeparator()
        cmenu.addAction(QIcon('src/icons/color.png'), "change Color", self.changeColor)
        cmenu.exec_(editor.mapToGlobal(point))   

    def clearLabel(self):
        if self.tabWidget_2.currentIndex() == 0:
            self.editor.clear()
        elif self.tabWidget_2.currentIndex() == 1:
            self.editor1.clear()

    """def readSettings(self):
        if self.settings.value("pos") != "":
            pos = self.settings.value("pos", QPoint(200, 200))
            self.move(pos)
        if self.settings.value("size") != "":
            size = self.settings.value("size", QSize(400, 400))
            self.resize(size)"""

    def format(color, style=''):
        """Return a QTextCharFormat with the given attributes.
        """
        _color = QColor()
        _color.setNamedColor(color)

        _format = QTextCharFormat()
        _format.setForeground(_color)
        if 'bold' in style:
            _format.setFontWeight(QFont.Bold)
        if 'italic' in style:
            _format.setFontItalic(True)

        return _format

    def changeColor(self):
        if self.tabWidget_2.currentIndex() == 0:
            editor = self.editor
        elif self.tabWidget_2.currentIndex() == 1:
            editor = self.editor1
        fmt = QTextCharFormat()
        if not editor.textCursor().selectedText() == "":
            col = QColorDialog.getColor(QColor("#" + editor.textCursor().selectedText()), self)
            if not col.isValid():
                return
            else:
                colorname = col.name()
                _color = QColor()
                _color.setNamedColor(colorname)
                fmt.setForeground(_color)
                self.mergeFormatOnWordOrSelection(fmt)
        else:
            col = QColorDialog.getColor(QColor("black"), self)
            if not col.isValid():
                return
            else:
                colorname = col.name()
                _color = QColor()
                _color.setNamedColor(colorname)
                fmt.setForeground(_color)
                self.mergeFormatOnWordOrSelection(fmt)

    """def clearBookmarks(self):
        self.bookmarks.clear()"""

    def newFile(self):
        if self.tabWidget_2.currentIndex() == 0:
            editor = self.editor
        elif self.tabWidget_2.currentIndex() == 1:
            editor = self.editor1
        ### New File
        if self.maybeSave():
            editor.clear()
            #editor.setPlainText(self.mainText)
            self.filename = ""
            self.setModified(False)
            editor.moveCursor(editor.cursor.End)
            self.lineLabel1.setText("new File created.")
            editor.setFocus()
            #self.bookmarks.clear()
            self.setWindowTitle("new File[*]") 

    """def openFileOnStart(self, path=None):
        ### open File
        if path:
            self.openPath = QFileInfo(path).path() ### store path for next time
            inFile = QFile(path)
            if inFile.open(QFile.ReadWrite | QFile.Text):
                text = inFile.readAll()
                try:
                        # Python v3.
                    text = str(text, encoding = 'utf8')
                except TypeError:
                        # Python v2.
                    text = str(text)
                self.editor.setPlainText(text.replace(chr(9), "    "))
                self.setModified(False)
                self.setCurrentFile(path)
                self.editor.setFocus()
                ### save backup
                file = QFile(self.filename + "_backup")
                if not file.open( QFile.WriteOnly | QFile.Text):
                    QMessageBox.warning(self, "Error",
                        "Cannot write file %s:\n%s." % (self.filename, file.errorString()))
                    return
                outstr = QTextStream(file)
                QApplication.setOverrideCursor(Qt.WaitCursor)
                outstr << self.editor.toPlainText()
                QApplication.restoreOverrideCursor()
                self.lineLabel1.setText("File '" + path + "' loaded succesfully & bookmarks added & backup created ('" + self.filename + "_backup" + "')")"""

    def openFile(self, path=None):
        ### open File
        if self.openPath == "":
            self.openPath = self.dirpath
        if self.maybeSave():
            if not path:
                path, _ = QFileDialog.getOpenFileName(self, "Open File", self.openPath,
                    "Text Files (*.txt);; all Files (*)")

            '''if path:
                self.openFileOnStart(path)'''

    def fileSave(self):
        if self.tabWidget_2.currentIndex() == 0:
            editor = self.editor
        elif self.tabWidget_2.currentIndex() == 1:
            editor = self.editor1
        if (self.filename != ""):
            file = QFile(self.filename)
            if not file.open( QFile.WriteOnly | QFile.Text):
                QMessageBox.warning(self, "Error",
                        "Cannot write file %s:\n%s." % (self.filename, file.errorString()))
                return

            outstr = QTextStream(file)
            QApplication.setOverrideCursor(Qt.WaitCursor)
            outstr << editor.toPlainText()
            QApplication.restoreOverrideCursor()                
            self.setModified(False)
            self.fname = QFileInfo(self.filename).fileName() 
            self.setWindowTitle(self.fname + "[*]")
            self.lineLabel1.setText("File saved.")
            self.setCurrentFile(self.filename)
            editor.setFocus()

        else:
            self.fileSaveAs()

    def exportPDF(self):
        if self.tabWidget_2.currentIndex() == 0:
            editor = self.editor
        elif self.tabWidget_2.currentIndex() == 1:
            editor = self.editor1
        if editor.toPlainText() == "":
            self.lineLabel1.setText("no text")
        else:
            if (self.filename != ""):
                newname = self.strippedName(self.filename).replace(QFileInfo(self.filename).suffix(), "pdf")
            else:
                newname = 'tallies'
            #newname = editor.strippedName(self.filename).replace(QFileInfo(self.filename).suffix(), "pdf")
            fn, _ = QFileDialog.getSaveFileName(self,
                    "PDF files (*.pdf);;All Files (*)", (QDir.homePath() + "/PDF/" + newname))
            printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
            printer.setOutputFormat(QtPrintSupport.QPrinter.PdfFormat)
            printer.setPaperSize(QtPrintSupport.QPrinter.A4)
            printer.setPageSize(QtPrintSupport.QPrinter.A4)
            printer.setPageMargins(0, 10, 0, 10, QtPrintSupport.QPrinter.Millimeter)
            if self.Landscape_CB.isChecked():
                printer.setOrientation(QtPrintSupport.QPrinter.Landscape)
                textWidth = printer.pageRect().height()
            else:
                printer.setOrientation(QtPrintSupport.QPrinter.Portrait)
                textWidth = printer.pageRect().width()
            

            editor.document().setTextWidth(textWidth)
            
            # Adjust font size to fit within available width
            fontMetrics = editor.fontMetrics()
            text = editor.toPlainText()
            font = self.adjustFontSizeToFitWidth(editor, text, textWidth)
            editor.document().setDefaultFont(font)

            #printer.setFullPage(True)
            printer.setOutputFileName(fn)
            editor.document().print_(printer)
            # restore old font
            font.setPointSize(float(self.comboSize.currentText()))
            fontMetrics = editor.fontMetrics()
            editor.document().setDefaultFont(font)

    def adjustFontSizeToFitWidth(self, editor, text, width):
        # Start with a large font size
        font = editor.document().defaultFont()
        font.setPointSize(12)

        # Create a QFontMetrics object to measure text size
        fm = editor.fontMetrics()

        # Iterate until the text fits within the width
        while fm.width(text) > width and font.pointSize() > 4:
            font.setPointSize(font.pointSize() - 1)

        return font
    
    def fileSaveAs(self):
        ### save File
        fn, _ = QFileDialog.getSaveFileName(self, "Save as...", self.filename, "Text Files (*.txt);; all Files (*)")

        if not fn:
            print("Error saving")
            return False

        self.filename = fn
        self.fname = QFileInfo(QFile(fn).fileName())
        return self.fileSave()

    def maybeSave(self):
        ### ask to save
        if not self.isModified():
            return True

        if self.filename.startswith(':/'):
            return True

        ret = QMessageBox.question(self, "Message",
                "<h4><p>The document was modified.</p>\n" \
                "<p>Do you want to save changes?</p></h4>",
                QMessageBox.Yes | QMessageBox.Discard | QMessageBox.Cancel)

        if ret == QMessageBox.Yes:
            if self.filename == "":
                self.fileSaveAs()
                return False
            else:
                self.fileSave()
                return True

        if ret == QMessageBox.Cancel:
            return False

        return True   

    def isModified(self):
        if self.tabWidget_2.currentIndex() == 0:
            editor = self.editor
        elif self.tabWidget_2.currentIndex() == 1:
            editor = self.editor1
        return editor.document().isModified()

    def setModified(self, modified):
        if self.tabWidget_2.currentIndex() == 0:
            editor = self.editor
        elif self.tabWidget_2.currentIndex() == 1:
            editor = self.editor1
        editor.document().setModified(modified)

    """def createActions(self):
        for i in range(self.MaxRecentFiles):
            self.recentFileActs.append(QAction(self, visible=False, triggered=self.openRecentFile))"""

    """def openRecentFile(self):
        action = self.sender()
        if action:
            myfile = action.data()
            if (self.maybeSave()):
                if QFile.exists(myfile):
                    self.openFileOnStart(myfile)
                else:
                    self.msgbox("Info", "File does not exist!")"""

    def setCurrentFile(self, fileName):
        self.filename = fileName
        if self.filename:
            self.setWindowTitle(self.strippedName(self.filename) + "[*]")
        else:
            self.setWindowTitle("no File")      
        
        files = self.settings.value('recentFileList', [])

        try:
            files.remove(fileName)
        except ValueError:
            pass

        if not fileName == "/tmp/tmp.py":
            files.insert(0, fileName)
        #del files[self.MaxRecentFiles:]

        self.settings.setValue('recentFileList', files)

    def updateRecentFileActions(self):
        if self.settings.contains('recentFileList'):
            mytext = ""
            files = self.settings.value('recentFileList', [])

    def strippedName(self, fullFileName):
        return QFileInfo(fullFileName).fileName()

class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))
        pass

    def flush(self):
        pass

class CheckableComboBox(QtWidgets.QComboBox):
    def __init__(self, parent = None):
        super(CheckableComboBox, self).__init__(parent)
        self._changed = False
        self.setView(QtWidgets.QListView(self))
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(PyQt5.QtGui.QStandardItemModel(self))

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
            self.undo_action(index.row())
        else:
            item.setCheckState(QtCore.Qt.Checked)
            self.do_action(index.row())
        self._changed = True

    def do_action(self, index):
        if self.model().item(index).text() == 'All bins' and self.model().item(1, 0).checkState() == QtCore.Qt.Checked:
            for i in range(2, self.count()):
                self.model().item(i, 0).setCheckState(QtCore.Qt.Checked)

    def undo_action(self, index):
        if self.model().item(index).text() == 'All bins' and self.model().item(1, 0).checkState() != QtCore.Qt.Checked:
            for i in range(1, self.count()):    #  2
                self.model().item(i, 0).setCheckState(QtCore.Qt.Unchecked)
        else:
            try:    
                self.model().item(1, 0).setCheckState(QtCore.Qt.Unchecked)
            except:
                pass

    def checkedItems(self):
        checkedItems = []
        for index in range(self.count()):
            item = self.model().item(index)
            if item.checkState() == QtCore.Qt.Checked:
                checkedItems.append(index)
        return checkedItems

    def hidePopup(self):
        if not self._changed:
            super().hidePopup()
        self._changed = False

    def itemChecked(self, index):
        item = self.model().item(index, self.modelColumn())
        return item.checkState() == Qt.Checked

    def setItemChecked(self, index, checked=False):
        item = self.model().item(index, self.modelColumn())  # QStandardItem object
        if checked:
            item.setCheckState(Qt.Checked)
        else:
            item.setCheckState(Qt.Unchecked)

    def setItemDisabled(self, index):
        item = self.model().item(index, self.modelColumn())  # QStandardItem object
        if item:
            item.setCheckState(Qt.Unchecked)
            item.setEnabled(False)

class VLine(QFrame):
    # a simple VLine, like the one you get from designer
    def __init__(self):
        super(VLine, self).__init__()
        self.setFrameShape(self.VLine | self.Sunken)

#  to be removed if called by gui.py
qapp = QApplication(sys.argv)
mainwindow = TallyDataProcessing()
mainwindow.show()
sys.exit(qapp.exec())






