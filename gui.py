#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
from datetime import datetime

from PyQt5 import QtCore, QtWidgets, QtPrintSupport, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import QTextCursor, QIcon, QKeySequence, QColor, QTextCharFormat, QTextDocument, QTextFormat, \
    QFontDatabase
from PyQt5.QtWidgets import *
import time
import subprocess
from PyQt5 import uic                         # added
import glob
import os.path
from os import path
from PyQt5.QtGui import *
from src.InfoPythonScript import InfoPythonScript
from src.InfoXMLScripts import InfoXMLScripts
from src.ExportPlots import ExportPlots 
from src.ExportTallies import ExportTallies 
from src.ExportSettings import ExportSettings 
from src.ExportGeometry import ExportGeometry 
from src.ExportMaterials import ExportMaterials
from src.PyEdit import TextEdit, NumberBar, tab, lineHighlightColor
from src.install import InstallOpenMC
import src.source_rc
from src.syntax_py import Highlighter
from src.image_viewer import QImageViewer

lineBarColor = QColor("#d3d7cf")
lineHighlightColor = QColor("#fce94f")
tab = chr(9)
eof = "\n"
iconsize = QSize(24, 24)

# look if miniconda3 is installed
CONDA = subprocess.run(['which', 'conda'], stdout=subprocess.PIPE, text=True)
CONDA = CONDA.stdout.rstrip('\n')
if "miniconda3" in CONDA:
    try:
        from src.TallyDataProcessing import TallyDataProcessing
    except:
        pass

class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))
        pass

    def flush(self):
        pass

class VLine(QFrame):
    # a simple VLine, like the one you get from designer
    def __init__(self):
        super(VLine, self).__init__()
        self.setFrameShape(self.VLine | self.Sunken)

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class Application(QtWidgets.QMainWindow):
    from src.func import Surf,Cell,Hex_Lat,Rec_Lat,Comment,Mat,Settings,Tally
    from src.func import Filter,Mesh,Ass_Sep,CMDF,Plot_S,Plot_V
    from src.func import showDialog, CursorPosition

    def __init__(self, title= "Py_ERSN_OpenMC", parent=None):
        super(Application, self).__init__(parent)
        from subprocess import Popen, PIPE
        #sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        #sys.stderr = EmittingStream(textWritten=self.normalOutputWritten)
        #self.settings = QSettings("PyEdit", "Py_ERSN_OpenMC")
        try:
            from openmc import __version__
            self.openmc_version = int(__version__.split('-')[0].replace('.', ''))
        except:
            self.showDialog('Warning', 'OpenMC not yet installed !')
            self.openmc_version = 0
        self.title = title
        self.ui = uic.loadUi("src/ui/Interface.ui", self)
        self.new_File = False
        self.openedFiles = False
        self.ploting = False
        #self.initUI()
        self.radioButton.setChecked(True)
        self.directory = ''
        self.filename = ''
        self.app_dir = os.getcwd()
        self.Surfaces_key_list = ['Plane', 'XPlane', 'YPlane', 'ZPlane', 'Sphere', 'XCylinder', 'YCylinder', 'ZCylinder',
                              'Cone', 'XCone', 'YCone', 'Zcone', 'Quadric', 'XTorus', 'YTorus', 'ZTorus', 'model.hexagonal_prism', 'model.rectangular_prism']
        self.Filters_key_list = ['UniverseFilter', 'MaterialFilter', 'CellFilter', 'CellFromFilter', 'CellbornFilter',
                                 'CellInstanceFilter', 'SurfaceFilter', 'MeshFilter', 'MeshSurfaceFilter',
                                 'DistribcellFilter', 'CollisionFilter', 'EnergyFilter', 'EnergyoutFilter',
                                 'MuFilter', 'PolarFilter', 'AzimuthalFilter', 'DelayedGroupFilter', 'EnergyFunctionFilter',
                                 'LegendreFilter', 'SpatialLegendreFilter', 'SphericalHarmonicsFilter', 'ZernikeFilter',
                                 'ZernikeRadialFilter', 'ParticleFilter', 'TimeFilter']
        self.Filters_key_sub_list = ['CellFilter', 'CellFromFilter', 'CellbornFilter', 'CellInstanceFilter']

        self.clear_Lists()
        self.Enrichment = False
        self.plots_file_name = ''
        # detects available nuclides in cross_section.xml
        self.Neutron_XS_List = []
        self.TSL_XS_List = []
        self.Photon_XS_List = []
        process = Popen(["echo $OPENMC_CROSS_SECTIONS"], stdout=PIPE, shell=True)
        f = process.communicate()[0].decode('ascii').rstrip('\n')
        if not os.path.isfile(f):
            f = './bash_scripts/cross_sections.xml'
        lines = open(f, 'r').read().split('\n')
        for line in lines:
            if 'neutron' in line:
                item = line.split()
                """if 'materials' in item and '=' in item:
                    nuclide = item.strip('materials').strip('=').strip().replace('"','')
                elif 'materials' in item and '=' not in item:
                    nuclide = items[items.index(item) + 1].strip().replace('"','')"""
                nuclide = line[line.find('materials') + 1: line.find('path')].split('=')[1].rstrip().replace('"', '')
                self.Neutron_XS_List.append(nuclide)
            elif 'thermal' in line:
                tsl = line[line.find('materials') + 1: line.find('path')].split('=')[1].rstrip().replace('"', '')
                self.TSL_XS_List.append(tsl)
            elif 'photon' in line or 'wmp' in line:
                element = line[line.find('materials') + 1: line.find('path')].split('=')[1].rstrip().replace('"', '')
                self.Photon_XS_List.append(element)
            self.available_xs = [self.Neutron_XS_List, self.TSL_XS_List, self.Photon_XS_List]
        self.xml_file_names_list = ['geometry.xml', 'materials.xml', 'settings.xml', 'tallies.xml', 'plots.xml', 'cmfd.xml']

        #self.statusBar().addPermanentWidget(VLine())
        self.statusBar().setStyleSheet("color : blue")

        # this part is added to allow myEditor to work
        # Brackets ExtraSelection ...
        self.left_selected_bracket = QTextEdit.ExtraSelection()
        self.right_selected_bracket = QTextEdit.ExtraSelection()
        self.fname = ""
        self.words = []
        self.root = QDir.currentPath()
        self.wordList = []
        self.appfolder = self.root
        self.openPath = ""

        self.MaxRecentFiles = 15
        self.windowList = []
        self.recentFileActs = []
        self.settings = QSettings("PyEdit", "PyEdit")
        self.dirpath = QDir.homePath() + "$HOME/Documents/python_files/"
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowIcon(QIcon("src/icons/python3.png"))
        self.createActions()
        self.line = 0
        self.pos = 0
        #myEditor()
        self.editor_tool_bar()
        self.editor_menu()
        self.editor_core()

        self.initUI()

        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        #sys.stderr = EmittingStream(textWritten=self.normalOutputWritten)
        self._initButtons()

        if self.tabWidget.currentWidget().objectName() == 'tab_python':              # python script window
            #self.toolBar_1.setEnabled(True)
            self.toolBar_2.setEnabled(True)
            self.toolBar_4.setEnabled(True)
            self.editor = self.plainTextEdit_7
        else:
            #self.toolBar_1.setEnabled(False)
            self.toolBar_2.setEnabled(False)
            self.toolBar_4.setEnabled(False)

        self.checkbox.setChecked(True)
        # addapt GUI size to screen dimensions
        self.resize_ui()

    def _initButtons(self):
        self.pushButton_20.clicked.connect(self.Surf)
        self.pushButton_21.clicked.connect(self.Cell)
        self.pushButton_22.clicked.connect(self.Comment)
        self.pushButton_23.clicked.connect(self.Hex_Lat)
        self.pushButton_24.clicked.connect(self.Rec_Lat)
        self.pushButton_29.clicked.connect(self.Filter)
        self.pushButton_25.clicked.connect(self.Mat)
        self.pushButton_27.clicked.connect(self.Tally)
        self.pushButton_26.clicked.connect(self.Comment)
        self.pushButton_15.clicked.connect(self.createGeom)
        self.pushButton_28.clicked.connect(self.Comment)
        self.pushButton_30.clicked.connect(self.Mesh)
        self.pushButton_31.clicked.connect(self.Ass_Sep)
        self.pushButton_33.clicked.connect(self.Plot_S)
        self.pushButton_32.clicked.connect(self.Comment)
        self.pushButton_34.clicked.connect(self.Plot_V)
        self.pushButton_19.clicked.connect(self.Run_OpenMC)
        self.comboBox_3.currentIndexChanged.connect(self.Settings)
        self.comboBox_4.currentIndexChanged.connect(self.CMDF)
        self.actionExit.triggered.connect(self.Exit)
        self.actionHelp.triggered.connect(self.Help)
        self.actionAbout.triggered.connect(self.About)
        self.actionClose_Project.triggered.connect(self.Close_Project)
        self.pB_Clear_OW_2.clicked.connect(self.clear_text)
        self.actionGet_OpenMC.triggered.connect(self.Get_OpenMC)
        self.pushButton.clicked.connect(self.Python_Materials)
        self.pushButton_2.clicked.connect(self.Python_Geometry)
        self.pushButton_3.clicked.connect(self.Python_Settings)
        self.pushButton_4.clicked.connect(self.Python_Tallies)
        self.pushButton_5.clicked.connect(self.Python_Plots)
        self.actionAlign_Left.triggered.connect(self.Align_Left)
        self.actionAlign_Right.triggered.connect(self.Align_Right)
        self.actionAlign_Center.triggered.connect(self.Align_Center)
        self.actionAlign_Justify.triggered.connect(self.Align_Justify)
        self.actionXML_Validation.triggered.connect(self.XML_Validation)
        self.action2D_Slice.triggered.connect(self.View_2D)
        self.actionDump_sammay_h5.triggered.connect(self.Dump_H5)
        self.actionEdit_Tallies_out.triggered.connect(self.Tallies_View)
        self.actionVoxels_to_VTI.triggered.connect(self.Voxels_to_VTI)
        self.actionTracks_to_VTI.triggered.connect(self.Tracks_to_VTI)
        self.actionTally_Data_Processing.triggered.connect(self.Python_TallyDataProcessing)
        self.action3D_Voxels_3.triggered.connect(self.View_3D)
        self.actionView_Track.triggered.connect(self.View_Track)
        self.tabWidget.currentChanged.connect(self.editor_id)
        self.tabWidget_3.currentChanged.connect(self.editor_id)
        self.RunMode_CB.currentIndexChanged.connect(self.SetRunMode)
        self.radioButton.toggled.connect(self.RunPB_State)
        self.tabWidget.currentChanged.connect(self.Update_StatusBar)
        # self.plainTextEdit_7.blockCountChanged.connect(self.detect_components)
        self.plainTextEdit_7.textChanged.connect(self.detect_components)

    def initUI(self):
        # defining widgets in statusBar
        # self.statusBar().showMessage(self.appfolder)
        self.lineLabel1 = QLabel("Project")
        self.lineLabel2 = QLabel()
        self.lineLabel3 = QLabel("Cursor position")
        self.lineLabel2.setAlignment(QtCore.Qt.AlignCenter)
        self.lineLabel3.setAlignment(QtCore.Qt.AlignCenter)
        widget = QWidget(self)
        widget.setLayout(QHBoxLayout())
        widget.layout().addWidget(self.lineLabel1)
        widget.layout().addWidget(VLine())
        widget.layout().addWidget(self.lineLabel2)
        widget.layout().addWidget(VLine())
        widget.layout().addWidget(self.lineLabel3)
        self.statusBar().addWidget(widget, 1)
        self.editor_id()
        self.CursorPositionChanged()
        # The program below adds tooltip messages to the buttons.
        self.pushButton_20.setToolTip(
       'Each <surface> element can have the following attributes or sub-elements: \n'
       'id: A unique integer that can be used to identify the surface. Default: None\n' 
       'type: The type of the surfaces. This can be “x-plane”, “y-plane”, “z-plane”, “plane”, “x-cylinder”, “y-cylinder”, “z-cylinder”, “sphere”,“x-cone”,\n'
       '“y-cone”, “z-cone”, or “quadric”. Default: None\n'
       'coeffs: The corresponding coefficients for the given type of surface. See below for a list a what coefficients to specify for a given surface. \n'
       'Default: None\n\n'
       'boundary: The boundary condition for the surface. This can be “periodic”, “vacuum”, “reflective” or “white”. Default: “transmissive” \n\n'
       'More information can be found in : https://openmc.readthedocs.io/en/stable/usersguide/index.html')
        self.pushButton_21.setToolTip(
        'Each <cell> element can have the following attributes or sub-elements:\n'
        '- id: A unique integer that can be used to identify the surface. Default: None\n'
        '- universe: The id of the universe that this cell is contained in. Default: 0\n'
        '- fill: The id of the universe that fills this cell.\n'
        '- material: The id of the material that this cell contains. If the cell should contain no material, this can also be set to “void”. Default: None\n'
        '- region: A list of the ids for surfaces that bound this cell, e.g. if the cell is on the negative side of surface 3 and the positive side of \n'
        'surface 5, the bounding surfaces would be given as “-3 5”. \n'
        'Note: space means intersection operator, | means union operator and Gui_orig.\n'
        'and the Complement of an existing openmc.Region can be created by using the ~ operator\n'
        '- rotation: If the cell is filled with a universe, this element specifies the angles in degrees about the x, y, and z axes that the filled universe\n'
        'should be rotated. Should be given as three real numbers. Rotation can be omitted if no rotation is applyed. Default: None\n'
        '- translation: If the cell is filled with a universe, this element specifies a vector that is used to translate (shift) the universe. Should be given\n'
        'as three real numbers. Translation can be omitted if no translation is applyed. Default: None\n\n'
        'More information can be found in : https://openmc.readthedocs.io/en/stable/usersguide/index.html')
        self.pushButton_23.setToolTip("<b>HTML</b> <i>can</i> be shown too..")

    def editor_tool_bar(self):
        self.actionNew = QAction(QIcon("src/icons/new_project.png"), "&New Project", self, shortcut=QKeySequence.New,
                              statusTip="new project", triggered=self.NewFiles)
        self.toolBar.addAction(self.actionNew)

        self.newAct = QAction(QIcon("src/icons/new24.png"), "&New File", self, shortcut=QKeySequence.New,
                              statusTip="new file", triggered=self.newFile)
        self.toolBar.addAction(self.newAct)

        self.actionOpen = QAction(QIcon("src/icons/open24.png"), "&Open Project", self, shortcut=QKeySequence.Open,
                              statusTip="open project", triggered=self.OpenFiles)
        self.toolBar.addAction(self.actionOpen)

        self.actionSave = QAction(QIcon("src/icons/document-save.png"), "&Save Project", self, shortcut=QKeySequence.Save,
                              statusTip="save files", triggered=self.SaveFiles)
        self.toolBar.addAction(self.actionSave)

        self.actionSave_as = QAction(QIcon("src/icons/document-save-as.png"), "Sa&ve Project as", self, shortcut=QKeySequence.SaveAs,
                              statusTip="save file as", triggered=self.SaveAsFiles)
        self.toolBar.addAction(self.actionSave_as)

        ####################################################################################################
        self.toolBar.addSeparator()

        self.actionCut = QAction(QIcon("src/icons/cut_text.png"), "&Cut", self, shortcut=QKeySequence.Cut,
                              statusTip="cut", triggered=self.Cut)
        self.toolBar.addAction(self.actionCut)

        self.actionCopy = QAction(QIcon("src/icons/copy_text.png"), "&Copy", self, shortcut=QKeySequence.Copy,
                              statusTip="copy", triggered=self.Copy)
        self.toolBar.addAction(self.actionCopy)

        self.actionPaste = QAction(QIcon("src/icons/paste_text.png"), "&Paste", self, shortcut=QKeySequence.Paste,
                              statusTip="paste", triggered=self.Paste)
        self.toolBar.addAction(self.actionPaste)

        self.actionUndo = QAction(QIcon("src/icons/undo_text.png"), "&Undo", self, shortcut=QKeySequence.Undo,
                              statusTip="undo", triggered=self.Undo)
        self.toolBar.addAction(self.actionUndo)

        self.actionRedo = QAction(QIcon("src/icons/redo_text.png"), "&Redo", self, shortcut=QKeySequence.Redo,
                              statusTip="redo", triggered=self.Redo)
        self.toolBar.addAction(self.actionRedo)

        self.toolBar.addSeparator()
        ####################################################################################################

        self.toolBar_2 = QToolBar()
        self.toolBar.addWidget(self.toolBar_2)

        ### comment buttons
        self.commentAct = QAction(QIcon("src/icons/comment.png"), "#comment Line", self, shortcut="F2",
                                  statusTip="comment Line (F2)", triggered=self.commentLine)
        self.toolBar_2.addAction(self.commentAct)

        self.uncommentAct = QAction(QIcon("src/icons/uncomment.png"), "uncomment Line", self, shortcut="F3",
                                    statusTip="uncomment Line (F3)", triggered=self.uncommentLine)
        self.toolBar_2.addAction(self.uncommentAct)

        self.commentBlockAct = QAction(QIcon("src/icons/commentBlock.png"), "comment Block", self, shortcut="F6",
                                       statusTip="comment selected block (F6)", triggered=self.commentBlock)
        self.toolBar_2.addAction(self.commentBlockAct)

        self.uncommentBlockAct = QAction(QIcon("src/icons/uncommentBlock.png"), "uncomment Block (F7)", self,
                                         shortcut="F7",
                                         statusTip="uncomment selected block (F7)", triggered=self.uncommentBlock)
        self.toolBar_2.addAction(self.uncommentBlockAct)

        self.toolBar_2.addSeparator()

        ### color chooser
        self.toolBar_2.addAction(QIcon('src/icons/color1.png'), "insert QColor", self.insertColor)
        self.toolBar_2.addAction(QIcon('src/icons/color.png'),  "change Color", self.changeColor)

        ####################################################################################################
        self.toolBar.addSeparator()

        self.toolBar_3 = QToolBar()
        self.toolBar.addWidget(self.toolBar_3)

        self.indentAct = QAction(QIcon("src/icons/format-indent-more.png"), "indent more, select text to indent", self,
                                 triggered=self.indentLine,
                                 shortcut="F8")
        self.indentLessAct = QAction(QIcon("src/icons/format-indent-less.png"), "indent less, select text to indent", self,
                                     triggered=self.indentLessLine, shortcut="F9")

        self.toolBar_3.addAction(self.indentAct)
        self.toolBar_3.addAction(self.indentLessAct)
        self.toolBar_3.addSeparator()

        ### save as pdf
        self.pdfAct = QAction(QIcon("src/icons/pdf.png"), "export PDF", self, shortcut="Ctrl+Shift+p",
                              statusTip="save file as PDF", triggered=self.exportPDF)
        self.toolBar_3.addAction(self.pdfAct)

        ### print preview
        self.printPreviewAct = QAction(QIcon("src/icons/document-print-preview.png"), "Print Preview", self,
                                       shortcut="Ctrl+Shift+P",
                                       statusTip="Preview Document", triggered=self.handlePrintPreview)
        self.toolBar_3.addAction(self.printPreviewAct)

        ### print
        self.printAct = QAction(QIcon("src/icons/document-print.png"), "Print", self, shortcut=QKeySequence.Print,
                                statusTip="Print Document", triggered=self.handlePrint)
        self.toolBar_3.addAction(self.printAct)

        self.comboSize = QComboBox(self.toolBar_3)
        self.toolBar_3.addSeparator()
        self.comboSize.setObjectName("comboSize")
        self.toolBar_3.addWidget(self.comboSize)
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
        self.bgAct = QAction(QIcon("src/icons/sbg_color.png"), "change Background Color", self,
                             triggered=self.changeBGColor)
        self.bgAct.setStatusTip("change Background Color")
        self.toolBar_3.addAction(self.bgAct)
        self.toolBar.addSeparator()

        # checkBox for highlighting
        self.checkbox = QCheckBox('Highlighting', self)
        self.toolBar.addWidget(self.checkbox)
        self.checkbox.stateChanged.connect(self.HLAct)

        ### show / hide shellWin
        self.toolBar.addSeparator()
        self.shToggleAction = QAction(QIcon("src/icons/close-terminal.png"), "show/ hide shell window", self,
                                      statusTip="show/ hide shell window", triggered=self.handleShellWinToggle)
        self.shToggleAction.setCheckable(True)
        self.toolBar.addAction(self.shToggleAction)

        self.toolBar_4 = QToolBar()
        self.toolBar.addWidget(self.toolBar_4)

        ### path python buttons
        self.py3Act = QAction(QIcon('src/icons/run.png'), "run in Python 3 (F5)", self, shortcut="F5",
                              statusTip="run in Python 3 (F5)", triggered=self.runPy3)
        self.toolBar_4.addAction(self.py3Act)


        self.toolBar_4.addAction(QIcon("src/icons/eraser.png"), "Clear output", self.clearLabel)

        self.toolBar_3 = QToolBar()
        self.toolBar.addWidget(self.toolBar_3)

        self.killPyAct = QAction(QIcon('src/icons/close.png'), "kill process (F12)", self, shortcut="F12",
                              statusTip="kill process (F12)", triggered=self.killPython)
        self.toolBar_3.addAction(self.killPyAct)

        self.toolBar.addSeparator()
        ####################################################################################################

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
        self.replacefield = QLineEdit()
        self.replacefield.addAction(QIcon("src/icons/edit-find-replace.png"), QLineEdit.LeadingPosition)
        self.replacefield.setClearButtonEnabled(True)
        self.replacefield.setFixedWidth(150)
        self.replacefield.setPlaceholderText("replace with")
        self.replacefield.setToolTip("press RETURN to replace the first")
        self.replacefield.returnPressed.connect(self.replaceOne)
        tbf.addSeparator()
        tbf.addWidget(self.replacefield)
        tbf.addSeparator()

        self.repAllAct = QPushButton("replace all")
        self.repAllAct.setFixedWidth(100)
        self.repAllAct.setIcon(QIcon("src/icons/edit-find-replace.png"))
        self.repAllAct.setStatusTip("replace all")
        self.repAllAct.clicked.connect(self.replaceAll)
        tbf.addWidget(self.repAllAct)
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

        # add ComboBox for rescaling factor
        ComboBox_label = QLabel('Rescale Factor', self)
        self.comboBox = QComboBox()
        self.comboBox.addItems(['1', '0.9', '0.8', '0.7', '0.6', '0.5'])
        tbf.addWidget(ComboBox_label)
        tbf.addWidget(self.comboBox)
        self.comboBox.currentIndexChanged.connect(self.resize_ui)

        ## addStretch
        empty = QWidget();
        empty.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred);
        tbf.addWidget(empty)

        tbf.addSeparator()

        self.exitAct = QAction(QIcon("src/icons/quit.png"), "exit", self, shortcut=QKeySequence.Quit,
                               statusTip="Exit", triggered=self.Exit)
        tbf.addAction(self.exitAct)
        ##############################################################################################""""""

    def editor_menu(self):
        # project menu
        self.projectmenu = self.menubar.addMenu("Project")
        self.separatorAct = self.projectmenu.addSeparator()
        self.projectmenu.addAction(self.actionNew)
        self.projectmenu.addAction(self.actionOpen)
        self.projectmenu.addAction(self.actionSave)
        self.projectmenu.addAction(self.actionSave_as)
        self.projectmenu.addSeparator()
        self.projectmenu.addAction(self.actionClose_Project)
        self.projectmenu.addSeparator()
        self.projectmenu.addAction(self.actionExit)
        self.projectmenu.addSeparator()

        ### file buttons
        self.filemenu = self.menubar.addMenu("File")
        self.filemenu.addSeparator()
        self.filemenu.addSeparator()
        '''self.newAct = QAction(QIcon("src/icons/new24.png"), "&New", self, shortcut=QKeySequence.New,
                              statusTip="new file", triggered=self.newFile)'''
        self.filemenu.addAction(self.newAct)
        self.filemenu.addAction(self.actionOpen)
        self.filemenu.addAction(self.actionSave)
        self.filemenu.addAction(self.actionSave_as)
        self.filemenu.addSeparator()
        self.filemenu.addAction(self.pdfAct)
        self.filemenu.addSeparator()
        for i in range(self.MaxRecentFiles):
            self.filemenu.addAction(self.recentFileActs[i])
        try:
            self.updateRecentFileActions()
        except:
            pass
        self.filemenu.addSeparator()

        self.clearRecentAct = QAction(QIcon("src/icons/close.png"), "clear Recent Files List", self,
                                      triggered=self.clearRecentFiles)
        self.filemenu.addAction(self.clearRecentAct)
        self.filemenu.addSeparator()
        self.filemenu.addAction(self.exitAct)

        # tools menu
        self.toolsmenu = self.menubar.addMenu("Tools")
        self.separatorAct = self.toolsmenu.addSeparator()
        self.toolsmenu.addAction(self.actionXML_Validation)
        self.separatorAct = self.toolsmenu.addSeparator()
        self.submenu1 = self.toolsmenu.addMenu("View output")
        self.separatorAct = self.toolsmenu.addSeparator()
        self.submenu1.addAction(self.actionEdit_Tallies_out)
        self.separatorAct = self.submenu1.addSeparator()
        self.submenu1.addAction(self.actionDump_sammay_h5)
        self.separatorAct = self.toolsmenu.addSeparator()
        self.submenu2 = self.toolsmenu.addMenu("View geometry")
        self.separatorAct = self.toolsmenu.addSeparator()
        self.submenu2.addAction(self.action2D_Slice)
        self.separatorAct = self.submenu2.addSeparator()
        self.submenu2.addAction(self.action3D_Voxels_3)
        self.separatorAct = self.toolsmenu.addSeparator()
        self.submenu3 = self.toolsmenu.addMenu("Convert H to VTI file")
        self.separatorAct = self.toolsmenu.addSeparator()
        self.submenu3.addAction(self.actionVoxels_to_VTI)
        self.separatorAct = self.submenu3.addSeparator()
        self.submenu3.addAction(self.actionTracks_to_VTI)
        self.separatorAct = self.toolsmenu.addSeparator()
        self.toolsmenu.addAction(self.actionView_Track)
        self.separatorAct = self.toolsmenu.addSeparator()
        self.toolsmenu.addAction(self.actionTally_Data_Processing)
        self.separatorAct = self.toolsmenu.addSeparator()

        # get openmc menu
        self.getOpenMCmenu = self.menubar.addMenu("Get OpenMC")
        self.separatorAct = self.getOpenMCmenu.addSeparator()
        self.getOpenMCmenu.addAction(self.actionGet_OpenMC)
        self.separatorAct = self.getOpenMCmenu.addSeparator()

        # about menu
        self.toolsmenu = self.menubar.addMenu("About")
        self.separatorAct = self.toolsmenu.addSeparator()
        self.toolsmenu.addAction(self.actionAbout)

        # help menu
        self.toolsmenu = self.menubar.addMenu("Help")
        self.separatorAct = self.toolsmenu.addSeparator()
        self.toolsmenu.addAction(self.actionHelp)

    def editor_core(self):
        from PyQt5.QtGui import QTextOption
        # add new editor for python window
        U_layout = QGridLayout()
        U_widgets = QWidget()
        D_layout = QGridLayout()
        self.D_widgets = QWidget()
        U_widgets.setLayout(U_layout)
        self.D_widgets.setLayout(D_layout)

        self.plainTextEdit_7 = TextEdit()
        self.numbers = NumberBar(self.plainTextEdit_7)
        self.shellWin = TextEdit()        # QTextEdit()
        self.shellWin.setContextMenuPolicy(Qt.CustomContextMenu)

        layoutH7 = QHBoxLayout()
        layoutH7.addWidget(self.numbers)
        layoutH7.addWidget(self.plainTextEdit_7)
        layoutH7_ = QVBoxLayout()
        layoutH7_.addWidget(self.shellWin)
        U_layout.addLayout(layoutH7, 0, 0)
        D_layout.addLayout(layoutH7_, 0, 0)

        splitter1 = QSplitter(Qt.Vertical, frameShape=QFrame.NoFrame, frameShadow=QFrame.Plain, lineWidth=0)
        splitter1.addWidget(U_widgets)
        splitter1.addWidget(self.D_widgets)
        splitter1.setSizes([450, 100])

        self.EditorLayout.addWidget(splitter1)

        # add new editor for output window
        self.plainTextEdit_8 = TextEdit()
        self.numbers = NumberBar(self.plainTextEdit_8)
        layoutH8 = QHBoxLayout()
        #layoutH8.setSpacing(1.5)
        layoutH8.addWidget(self.numbers)
        layoutH8.addWidget(self.plainTextEdit_8)
        self.OutputEditor.addLayout(layoutH8, 0, 0)

        # add new editor for xml windows
        self.plainTextEdit_1 = TextEdit()
        if self.tabWidget.currentWidget().objectName() == 'tab_python':  # python script window
            self.editor = self.plainTextEdit_7
        elif self.tabWidget.currentWidget().objectName() == 'tab_xml':  # xml script window
            self.editor = self.plainTextEdit_1
        elif self.tabWidget.currentWidget().objectName() == 'tab_run':  # output window
            self.editor = self.plainTextEdit_8

        self.editor.setWordWrapMode(QTextOption.NoWrap)
        self.highlighter = Highlighter(self.editor.document())

        self.editor.setContextMenuPolicy(Qt.CustomContextMenu)
        self.editor.customContextMenuRequested.connect(self.contextMenuRequested)

        self.readSettings()

        self.numbers = NumberBar(self.plainTextEdit_1)
        layoutH = QHBoxLayout()
        #layoutH.setSpacing(1.5)
        layoutH.addWidget(self.numbers)
        layoutH.addWidget(self.plainTextEdit_1)
        self.GeomEditor.addLayout(layoutH, 0, 0)
        #
        self.plainTextEdit_2 = TextEdit()
        self.numbers = NumberBar(self.plainTextEdit_2)
        layoutH2 = QHBoxLayout()
        #layoutH2.setSpacing(1.5)
        layoutH2.addWidget(self.numbers)
        layoutH2.addWidget(self.plainTextEdit_2)
        self.MatEditor.addLayout(layoutH2, 0, 0)
        #
        self.plainTextEdit_3 = TextEdit()
        self.numbers = NumberBar(self.plainTextEdit_3)
        layoutH3 = QHBoxLayout()
        #layoutH3.setSpacing(1.5)
        layoutH3.addWidget(self.numbers)
        layoutH3.addWidget(self.plainTextEdit_3)
        self.SetEditor.addLayout(layoutH3, 0, 0)
        #
        self.plainTextEdit_4 = TextEdit()
        self.numbers = NumberBar(self.plainTextEdit_4)
        layoutH4 = QHBoxLayout()
        #layoutH4.setSpacing(1.5)
        layoutH4.addWidget(self.numbers)
        layoutH4.addWidget(self.plainTextEdit_4)
        self.TallyEditor.addLayout(layoutH4, 0, 0)
        #
        self.plainTextEdit_5 = TextEdit()
        self.numbers = NumberBar(self.plainTextEdit_5)
        layoutH5 = QHBoxLayout()
        #layoutH5.setSpacing(1.5)
        layoutH5.addWidget(self.numbers)
        layoutH5.addWidget(self.plainTextEdit_5)
        self.PlotEditor.addLayout(layoutH5, 0, 0)
        #
        self.plainTextEdit_6 = TextEdit()
        self.numbers = NumberBar(self.plainTextEdit_6)
        layoutH6 = QHBoxLayout()
        #layoutH6.setSpacing(1.5)
        layoutH6.addWidget(self.numbers)
        layoutH6.addWidget(self.plainTextEdit_6)
        self.CMFDEditor.addLayout(layoutH6, 0, 0)

    def HLAct(self):
        if self.checkbox.isChecked():
            from src.syntax_py import Highlighter
            self.highlighter = Highlighter(self.editor.document())
        else:
            from src.syntax import Highlighter
            self.highlighter = Highlighter(self.editor.document())

    def editor_id(self):
        if self.tabWidget.currentWidget().objectName() == 'tab_python':              # python script window
            self.editor = self.plainTextEdit_7
            self.cursor = self.editor.textCursor()
            self.cursor = self.editor.textCursor()
            self.editor.setTextCursor(self.cursor)
            self.editor.moveCursor(self.cursor.End)
            self.filemenu.setEnabled(True)
            #self.toolBar_1.setEnabled(True)
            self.toolBar_2.setEnabled(True)
            self.toolBar_4.setEnabled(True)
        elif self.tabWidget.currentWidget().objectName() == 'tab_xml':             # xml script windows
            self.filemenu.setEnabled(False)
            #self.toolBar_1.setEnabled(False)
            self.toolBar_2.setEnabled(False)
            self.toolBar_4.setEnabled(False)
            if self.tabWidget_3.currentWidget().objectName() == 'tab_11':
                self.editor = self.plainTextEdit_1
                self.cursor = self.editor.textCursor()
                self.editor.setTextCursor(self.cursor)
                self.editor.moveCursor(self.cursor.End)
            elif self.tabWidget_3.currentWidget().objectName() == 'tab_12':
                self.editor = self.plainTextEdit_2
                self.cursor = self.editor.textCursor()
                self.editor.setTextCursor(self.cursor)
                self.editor.moveCursor(self.cursor.End)
            elif self.tabWidget_3.currentWidget().objectName() == 'tab_13':
                self.editor = self.plainTextEdit_3
                self.cursor = self.editor.textCursor()
                self.editor.setTextCursor(self.cursor)
                self.editor.moveCursor(self.cursor.End)
            elif self.tabWidget_3.currentWidget().objectName() == 'tab_14':
                self.editor = self.plainTextEdit_4
                self.cursor = self.editor.textCursor()
                self.editor.setTextCursor(self.cursor)
                self.editor.moveCursor(self.cursor.End)
            elif self.tabWidget_3.currentWidget().objectName() == 'tab_15':
                self.editor = self.plainTextEdit_5
                self.cursor = self.editor.textCursor()
                self.editor.setTextCursor(self.cursor)
                self.editor.moveCursor(self.cursor.End)
            elif self.tabWidget_3.currentWidget().objectName() == 'tab_16':
                self.editor = self.plainTextEdit_6
                self.cursor = self.editor.textCursor()
                self.editor.setTextCursor(self.cursor)
                self.editor.moveCursor(self.cursor.End)
        elif self.tabWidget.currentWidget().objectName() == 'tab_run':              # output window
            self.editor = self.plainTextEdit_8
            self.cursor = self.editor.textCursor()
            self.editor.setTextCursor(self.cursor)
            self.editor.moveCursor(self.cursor.End)
            self.filemenu.setEnabled(True)
            self.toolBar_2.setEnabled(False)
            self.toolBar_4.setEnabled(False)
        self.Update_StatusBar()

        self.highlighter = Highlighter(self.editor.document())
        self.editor.cursorPositionChanged.connect(self.CursorPositionChanged)

    def Update_StatusBar(self):
        if self.tabWidget.currentWidget().objectName() == 'tab_python':              # python script window
            if self.filename and os.path.getsize(self.filename) != 0:
                msg = 'Project python file : ' + self.filename + '      size :' + str(os.path.getsize(self.filename)) + ' KB'
            else:
                msg = 'Python file : '
            msg1 = self.editor.blockCount()
        elif self.tabWidget.currentWidget().objectName() == 'tab_xml':              # xml script window
            if self.directory:
                filename = self.directory + '/' + self.xml_file_names_list[self.tabWidget_3.currentIndex()]
                if os.path.exists(filename):
                    if os.path.getsize(filename) != 0 and self.editor.toPlainText() != '':
                        msg = 'Project xml file : ' + filename + '           size :' + str(os.path.getsize(filename)) + ' B'
                    else:
                        msg = 'xml file : ' + self.xml_file_names_list[self.tabWidget_3.currentIndex()]
                else:
                    msg = 'xml file : ' + self.xml_file_names_list[self.tabWidget_3.currentIndex()]
            else:
                msg = 'xml file : ' + self.xml_file_names_list[self.tabWidget_3.currentIndex()]
            msg1 = self.editor.blockCount()
        else:
            msg = 'Window output'
            msg1 = ""
        self.lineLabel1.setText(msg)
        self.lineLabel2.setText('  Blocks number : ' + str(msg1))
        self.lineLabel3.setText("Cursor position:    line " + str(self.line) + " | column " + str(self.pos))

    def clear_Lists(self):
        self.surface_id_list = ['0']
        self.surface_name_list = []
        self.regions = []
        self.cell_name_list = []
        self.Vol_Calcs_list = []
        self.cell_id_list = ['0']
        self.materials_name_list = []
        self.materials_id_list = []
        self.lattice_id_list = []
        self.lattice_name_list = []
        self.universe_id_list = []
        self.universe_name_list = []
        self.Source_name_list = []
        self.Source_id_list = []
        self.Source_strength_list = []
        self.tally_name_list = []
        self.tally_id_list = []
        self.filter_name_list = []
        self.filter_id_list = ['0']
        self.plot_name_list = []
        self.plot_id_list = ['0']
        self.score_name_list = []
        self.score_id_list = ['0']
        self.mesh_name_list = []
        self.mesh_id_list = []
        self.Model_Nuclides_List = []
        self.Model_Elements_List = []
        self.filters = {}
        self.Bins = {}

    def Python_TallyDataProcessing(self):
        #self.inst = TallyDataProcessing(self.shellWin)
        self.interface = TallyDataProcessing()
        self.interface.show()
        List_name = [self.surface_name_list, self.cell_name_list, self.materials_name_list, self.lattice_name_list,
                        self.universe_name_list, self.tally_name_list, self.mesh_name_list, self.filter_name_list]

        List_id = [self.surface_id_list, self.cell_id_list, self.materials_id_list, self.lattice_id_list,
                        self.universe_id_list, self.tally_id_list, self.mesh_id_list, self.filter_id_list]

    def file_name(self):
        if self.tabWidget.currentIndex() == 0:
            if self.directory:
                self.filename = self.directory + '/' + self.xml_file_names_list[self.tabWidget_3.currentIndex()]
            else:
                self.filename = ''

    def Get_OpenMC(self):
        self.inst = InstallOpenMC()
        self.inst.show()

    def Tracks_to_VTI(self):
        self.tabWidget.setCurrentIndex(2)
        self.plainTextEdit_8.clear()
        if self.directory:
            os.chdir(self.directory)
        h5_file = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', "~", "track*.h5")[0]
        self.directory = os.path.dirname(h5_file)
        self.lineLabel1.setText("File path: " + h5_file)
        self.lineLabel2.setText('  Blocks number : ' + str(self.editor.blockCount()))
        self.lineLabel3.setText("Cursor position:    line " + str(self.line) + " | column " + str(self.pos))
        if h5_file != "":
            file = open(h5_file, "r")
            cmd = 'openmc-track-to-vtk ' + h5_file
            self.process.start(cmd, QtCore.QIODevice.ReadWrite)
        os.chdir(self.app_dir)

    def Voxels_to_VTI(self):
        self.tabWidget.setCurrentIndex(2)
        self.plainTextEdit_8.clear()
        if self.directory:
            os.chdir(self.directory)
        h5_file = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', "~", "*.h5")[0]
        self.directory = os.path.dirname(h5_file)
        self.lineLabel1.setText("File path: " + h5_file)
        self.lineLabel2.setText('  Blocks number : ' + str(self.editor.blockCount()))
        self.lineLabel3.setText("Cursor position:    line " + str(self.line) + " | column " + str(self.pos))
        if h5_file != "":
            file = open(h5_file, "r")
            cmd = 'openmc-voxel-to-vtk ' + h5_file
            self.process.start(cmd, QtCore.QIODevice.ReadWrite)
        os.chdir(self.app_dir)

    def Dump_H5(self):
        self.tabWidget.setCurrentIndex(2)
        self.plainTextEdit_8.clear()
        if self.directory:
            os.chdir(self.directory)
        h5_file = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', "~", "*.h5")[0]
        self.directory = os.path.dirname(h5_file)
        self.lineLabel1.setText("File path: " + h5_file)
        self.lineLabel2.setText('  Blocks number : ' + str(self.editor.blockCount()))
        self.lineLabel3.setText("Cursor position:    line " + str(self.line) + " | column " + str(self.pos))
        if h5_file != "":
            file = open(h5_file, "r")
            cmd = 'h5dump ' + h5_file
            self.plainTextEdit_8.insertPlainText(os.popen(cmd).read())
        os.chdir(self.app_dir)

    def Tallies_View(self):
        self.tabWidget.setCurrentIndex(2)
        self.plainTextEdit_8.clear()
        if self.directory:
            os.chdir(self.directory)
        tallies_out = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', "~", "*.out")[0]
        self.directory = os.path.dirname(tallies_out)
        self.lineLabel1.setText("File path: " + tallies_out)
        self.lineLabel2.setText('  Blocks number : ' + str(self.editor.blockCount()))
        self.lineLabel3.setText("Cursor position:    line " + str(self.line) + " | column " + str(self.pos))
        if tallies_out != "":
            file = open(tallies_out, "r")
            self.plainTextEdit_8.setPlainText(file.read())
        os.chdir(self.app_dir)

    def XML_Validation1(self):
        # openmc-validate-xml -i test/ -r ~/miniconda3/envs/openmc-py3.7/share/openmc/relaxng/
        self.tabWidget.setCurrentIndex(2)
        self.plainTextEdit_8.clear()
        env: str = os.environ['CONDA_DEFAULT_ENV']
        cmd = 'which openmc'
        openmc_path: str = subprocess.getoutput(cmd)
        validate_script = openmc_path.replace('bin/openmc', 'bin/openmc-validate-xml')
        relaxng_dir = openmc_path.replace('bin/openmc', 'share/openmc/relaxng')
        cmd = validate_script + ' -i ' + str(self.directory) + ' -r ' + relaxng_dir
        if self.plainTextEdit_1.toPlainText():
            stream = os.popen(cmd)
            document = stream.read()
            self.highlighter = Highlighter(self.plainTextEdit_8.document())
            self.plainTextEdit_8.clear()
            self.plainTextEdit_8.insertPlainText(document)
        else:
            msg = 'Project is empty or no active project !'
            self.showDialog('Warning', msg)

    def XML_Validation(self):
        # openmc-validate-xml -i test/ -r ~/miniconda3/envs/openmc-py3.7/share/openmc/relaxng/
        from src.syntax_validate import Highlighter
        os.chdir(self.app_dir)
        self.checkbox.setChecked(False)
        self.tabWidget.setCurrentIndex(2)
        self.plainTextEdit_8.clear()
        self.highlighter = Highlighter(self.plainTextEdit_8.document())
        self.Process()
        validate_script = './validate_xml/openmc-validate-xml'
        relaxng_dir = './validate_xml/relaxng'
        cmd = validate_script + ' -i ' + str(self.directory) + ' -r ' + relaxng_dir
        if self.plainTextEdit_1.toPlainText():
            self.process.start(cmd)
        else:
            msg = 'Project is empty or no active project !'
            self.showDialog('Warning', msg)

    def ViewXML(self, Editor):
        Header_text_lines = []
        self.xml_files_list = []
        if self.filename:
            if self.new_File:
                Header_text = self.wind8.Header_text
            elif self.openedFiles:
                lines = self.plainTextEdit_7.toPlainText().split('\n')
                matchers = ['Description', 'Case', 'Writen by', 'DateTime']
                Header_text_lines = [line for line in lines if any(xs in line for xs in matchers)]
                if any('Description' in item for item in Header_text_lines):
                    pass
                else:
                    Header_text_lines.insert(0, ' Description: ')
                if any('Case' in item for item in Header_text_lines):
                    pass
                else:
                    Header_text_lines.insert(1, ' Case: ')
                if any('Writen by' in item for item in Header_text_lines):
                    pass
                else:
                    Header_text_lines.insert(2, ' Writen by: ' + os.getlogin())
                if any('DateTime' in item for item in Header_text_lines):
                    pass
                else:
                    Header_text_lines.insert(3, ' DateTime: ' + str(datetime.now()))
                Header_text = '='*75 + '\n' + '\n'.join(Header_text_lines) + '\n' + '='*75
            self.directory = os.path.dirname(self.filename)
            os.chdir(self.directory)

            for TE in [self.plainTextEdit_1, self.plainTextEdit_2, self.plainTextEdit_3, self.plainTextEdit_4,
                       self.plainTextEdit_5, self.plainTextEdit_6]:
                TE.clear()
            if path.exists(self.directory + '/geometry.xml') == True:
                self.xml_files_list.append('geometry.xml')
                files = self.directory + '/geometry.xml'
                file = open(files,"r")
                text = file.read().split('\n')
                text.insert(1, ' <!-- ')
                text.insert(2, Header_text)
                text.insert(3, ' -->')
                self.plainTextEdit_1.setPlainText('\n'.join(text))
                self.plainTextEdit_1.show()
            if path.exists(self.directory + '/materials.xml') == True:
                self.xml_files_list.append('materials.xml')
                files = self.directory + '/materials.xml'
                file = open(files,"r")
                text = file.read().split('\n')
                text.insert(1, ' <!-- ')
                text.insert(2, Header_text)
                text.insert(3, ' -->')
                self.plainTextEdit_2.setPlainText('\n'.join(text))
                self.plainTextEdit_2.show()
            if path.exists(self.directory + '/settings.xml') == True:
                self.xml_files_list.append('settings.xml')
                files = self.directory + '/settings.xml'
                file = open(files,"r")
                text = file.read().split('\n')
                text.insert(1, ' <!-- ')
                text.insert(2, Header_text)
                text.insert(3, ' -->')
                self.plainTextEdit_3.setPlainText('\n'.join(text))
                self.plainTextEdit_3.show()
            if path.exists(self.directory + '/tallies.xml') == True:
                self.xml_files_list.append('tallies.xml')
                files = self.directory+'/tallies.xml'
                file = open(files,"r")
                text = file.read().split('\n')
                text.insert(1, ' <!-- ')
                text.insert(2, Header_text)
                text.insert(3, ' -->')
                self.plainTextEdit_4.setPlainText('\n'.join(text))
                self.plainTextEdit_4.show()
            if path.exists(self.directory + '/cmfd.xml') == True:
                self.xml_files_list.append('cmfd.xml')
                files = self.directory+'/cmfd.xml'
                file = open(files,"r")
                text = file.read().split('\n')
                text.insert(1, ' <!-- ')
                text.insert(2, Header_text)
                text.insert(3, ' -->')
                self.plainTextEdit_6.setPlainText('\n'.join(text))
                self.plainTextEdit_6.show()
            if path.exists(self.directory + '/plots.xml') == True:
                self.xml_files_list.append('plots.xml')
                files = self.directory+'/plots.xml'
                file = open(files,"r")
                text = file.read().split('\n')
                text.insert(1, ' <!-- ')
                text.insert(2, Header_text)
                text.insert(3, ' -->')
                self.plainTextEdit_5.setPlainText('\n'.join(text))
                self.plainTextEdit_5.show()
            if self.xml_files_list:
                Editor.insertPlainText("\nfiles " + str(self.xml_files_list) + " have been created\n\n")

        else:
            msg = 'Select or save project first !'
            self.showDialog('Warning', msg)

    def detect_component_id(self, line, key, ID):
        import re
        item_id = line[line.find("(") + 1: line.find(")")].replace(' ', '').split(',')
        for w in item_id:
            if key in w and '=' in w:
                try:
                    self.id = int(w.split('=')[1])
                except:
                    self.showDialog('Warning', 'Element id must be integer')
                    return
                break
            elif key in w and '=' not in w:
                try:
                    self.id = int(re.search(r"(\d+)$", w).group())
                except:
                    self.showDialog('Warning', 'Element id must be integer')
                    return
                break    
            elif key not in w and '=' not in w and w.isdigit():
                try:
                    self.id = int(w)
                except:
                    self.showDialog('Warning', 'Element id must be integer')
                    return
                break
            else:
                self.id = ID
                break

    def detect_components(self):
        import re
        if not self.plainTextEdit_7.toPlainText().strip():
            return
        Lists = [self.Model_Elements_List, self.Model_Nuclides_List, self.materials_name_list,
                self.surface_name_list, self.cell_name_list, self.universe_name_list,
                self.lattice_name_list, self.Source_name_list, self.Source_id_list,
                self.tally_name_list, self.filter_name_list, self.mesh_name_list,
                self.plot_name_list, self.plot_id_list]
        for item in Lists:
            item.clear()
        self.materials_id_list = []
        self.cell_id_list = []
        self.surface_id_list = []
        self.universe_id_list = []
        self.cells_in_universes = []
        self.lattice_id_list = []
        self.mesh_id_list = []
        self.filter_id_list = []
        self.tally_id_list = []
        self.plot_id_list = []
        tally_filters_lines = []
        tally_elements_lines = []
        tally_nuclides_lines = []
        filter_bins_lines = []
        filters_list = []
        bins_list = []
        Elements_In_Material = []
        lines = self.plainTextEdit_7.toPlainText().split('\n')
        for line in lines:
            if 'openmc.Material' in line and 'openmc.Materials' not in line and 'Filter' not in line:
                item = line.split('=')[0].replace(' ', '')
                if item not in self.filter_name_list:
                    self.materials_name_list.append(item)
                    ID = len(self.materials_name_list)
                    self.detect_component_id(line, 'material_id', ID)
                    self.materials_id_list.append(self.id)
            elif 'openmc.Cell' in line and 'Filter' not in line:
                item = line.split('=')[0].replace(' ', '')
                if item not in self.filter_name_list:
                    self.cell_name_list.append(item)
                    ID = len(self.cell_name_list)
                    self.detect_component_id(line, 'cell_id', ID)
                    self.cell_id_list.append(self.id)
            elif 'openmc.Universe' in line and 'Filter' not in line:
                item = line.split('=')[0].replace(' ', '')
                if item not in self.filter_name_list:
                    self.universe_name_list.append(item)
                    ID = len(self.universe_name_list)
                    self.detect_component_id(line, 'universe_id', ID)
                    self.universe_id_list.append(self.id)
                    #self.lattice_id_list.append(self.id)
            elif '.add_cells' in line:
                item = list(line.replace(' ', '').split('[')[1].split(']')[0].split(","))
                self.cells_in_universes += item
            elif 'openmc.RectLattice' in line :
                item = line.split('=')[0].replace(' ', '')
                self.lattice_name_list.append(item)
                ID = len(self.lattice_name_list)
                self.detect_component_id(line, 'lattice_id', ID)
                self.lattice_id_list.append(self.id)
            elif 'openmc.HexLattice' in line:
                item = line.split('=')[0].replace(' ', '')
                self.lattice_name_list.append(item)
                ID = len(self.lattice_name_list)
                self.detect_component_id(line, 'lattice_id', ID)
                self.lattice_id_list.append(self.id)            
            elif 'openmc.Source' in line:
                item = line.split('=')[0].replace(' ', '')
                self.Source_name_list.append(item)
            elif 'openmc.RectilinearMesh' in line:
                item = line.split('=')[0].replace(' ', '')
                self.mesh_name_list.append(item)
                ID = len(self.mesh_name_list)
                self.detect_component_id(line, 'mesh_id', ID)
                self.mesh_id_list.append(self.id)
            elif 'openmc.RegularMesh' in line:
                item = line.split('=')[0].replace(' ', '')
                self.mesh_name_list.append(item)
                ID = len(self.mesh_name_list)
                self.detect_component_id(line, 'mesh_id', ID)
                self.mesh_id_list.append(self.id)
            elif 'openmc.Plot' in line and 'openmc.Plots' not in line:
                item = line.split('=')[0].replace(' ', '')
                self.plot_name_list.append(item)
                ID = len(self.plot_name_list)
                self.detect_component_id(line, 'plot_id', ID)
                self.plot_id_list.append(self.id)
            elif 'openmc.Plots' in line:
                item = line.split('=')[0].replace(' ', '')
                self.plots_file_name = item
            elif 'openmc.Tally' in line:
                item = line.split('=')[0].replace(' ', '')
                self.tally_name_list.append(item)
                ID = len(self.tally_name_list)
                self.detect_component_id(line, 'tally_id', ID)
                self.tally_id_list.append(self.id)
                self.filters[self.id] = []
            elif '.filters' in line:
                tally_filters_lines.append(line)
            elif 'openmc.' in line and 'Filter' in line:
                filter_bins_lines.append(line)
                for key in self.Filters_key_list:
                        key = 'openmc.' + key  
                        if key in line:
                            item = line.split('=')[0].replace(' ', '')
                            self.filter_name_list.append(item)
                            ID = len(self.filter_name_list)
                            self.detect_component_id(line, 'filter_id', ID)
                            self.filter_id_list.append(self.id)
                            break
            elif 'add_element' in line or 'add_nuclide' in line:
                tally_elements_lines.append(line)
            else:
                for key in self.Surfaces_key_list:
                    key = 'openmc.' + key
                    if key in line:
                        item = line.split('=')[0].replace(' ', '')
                        self.surface_name_list.append(item)
                        ID = len(self.surface_name_list)
                        self.detect_component_id(line, 'surface_id', ID)
                        self.surface_id_list.append(self.id)
                        break
                
        # Fil filters dictionary for each tally id
        for line in tally_filters_lines:
            tally = line.split('.')[0]
            if '=' in line:
                text = line.split('=')[1]
                filters_list = text[text.find('[') + 1: text.find(']')].replace(' ', '').split(',')
            elif 'append' in line:
                text = line.split('append')[1]
                filters_list = text[text.find('(') + 1: text.find(')')].replace(' ', '').split(',')
            try:
                id = self.tally_id_list[self.tally_name_list.index(tally)] # + 1]
            except:
                return
            self.filters[id] += filters_list
        # fill bins dictionary for each filter
        for line in filter_bins_lines:
            text = line.replace(' ', '').split('=')
            Filter_txt = text[0]
            text1 = text[1]
            if '[' in text1:
                bins_list = text1[text1.find('[') + 1: text1.find(']')].replace(' ', '').split(',')
            else:
                bins_list = text1[text1.find('(') + 1: text1.find(',')].replace(' ', '').split(',')
            id = self.filter_id_list[self.filter_name_list.index(Filter_txt)] # + 1]
            self.Bins[id] = bins_list
        # fill list of nuclides and elements in the model
        for line in tally_elements_lines:
            if 'add_nuclide' in line:
                line = line[line.find("(") + 1: line.find(")")]
                line =[item.rstrip().lstrip() for item in list(filter(None, line.replace("'","").replace('"','').split(',')))]
                try:
                    for item in line:
                        if item.isalnum() and 'wo' not in item and 'ao' not in item : Nuclide_In_Material = item   
                    if Nuclide_In_Material not in self.Model_Nuclides_List:
                        self.Model_Nuclides_List.append(Nuclide_In_Material)
                except:
                    pass
            elif 'add_element' in line:
                line = line[line.find("(") + 1: line.find(")")]
                line = ''.join([i for i in line.replace('.', '').replace("'", "").replace('"','') if not i.isdigit()]).replace(' ', '')
                line = list(filter(None, line.split(',')))
                Elements_In_Material += [item for item in line if 'ao' not in item and 'wo' not in item and 'enrichment' not in item]
                for elem in Elements_In_Material:   
                    if elem not in self.Model_Elements_List:
                        self.Model_Elements_List.append(elem) 
                
        if self.Model_Elements_List:
            self.Nuclides_In_Element(self.Model_Elements_List)   
        
        self.Model_Nuclides_List = sorted(self.Model_Nuclides_List)

    def Nuclides_In_Element(self, Elements_list):
        import string
        for cle in src.materials.NATURAL_ABUNDANCE.keys():
            if cle in self.Neutron_XS_List and cle.rstrip(string.digits) in Elements_list and cle not in self.Model_Nuclides_List:
                    self.Model_Nuclides_List.append(cle)

    def Python_Materials(self):
        """
        function for exporting to material.xml file
        """    
        v_1 = self.plainTextEdit_7
        #self.detect_components()
        if self.available_xs:
            self.wind3 = ExportMaterials(v_1, self.available_xs, self.materials_name_list, self.materials_id_list)
            self.wind3.show()
        else:
            self.showDialog('Warning', 'Cross secions files not defined !')
        self.SaveFiles()

    def Python_Geometry(self): 
        """
        function for exporting to geometry.xml file
        """
        v_1 = self.plainTextEdit_7
        #self.detect_components()
        mat = self.materials_name_list
        mat_id = self.materials_id_list
        regions = self.regions
        surf = self.surface_name_list
        surf_id = self.surface_id_list
        cell = self.cell_name_list
        cell_id = self.cell_id_list
        univ = self.universe_name_list
        univ_id = self.universe_id_list
        lat = self.lattice_name_list
        lat_id = self.lattice_id_list
        C_in_U = self.cells_in_universes
        self.wind4 = ExportGeometry(v_1, regions, surf, surf_id, cell, cell_id, mat, mat_id, univ, univ_id, C_in_U, lat, lat_id)
        self.wind4.show()
        self.SaveFiles()

    def Python_Settings(self): 
        """
        function for exporting to settings.xml file
        """     
        v_1 = self.plainTextEdit_7
        #self.detect_components()
        self.wind5 = ExportSettings(v_1, self.directory, self.surface_name_list, self.surface_id_list, self.cell_name_list,
                                    self.materials_name_list, self.Vol_Calcs_list, self.Source_name_list,
                                    self.Source_id_list, self.Source_strength_list)
        self.wind5.show()

        self.SaveFiles()

    def Python_Tallies(self): 
        """
        function for exporting to tallies.xml file
        """     
        v_1 = self.plainTextEdit_7
        #self.detect_components()
        if self.available_xs:
            self.wind6 = ExportTallies(v_1, self.available_xs, self.tally_name_list, self.tally_id_list,
                                       self.filter_name_list, self.filter_id_list,
                                       self.score_name_list, self.score_id_list, self.surface_name_list,
                                       self.surface_id_list,
                                       self.cell_name_list, self.cell_id_list, self.universe_name_list,
                                       self.materials_name_list,
                                       self.Model_Elements_List, self.Model_Nuclides_List, self.mesh_name_list,
                                       self.mesh_id_list)
        else:
            self.showDialog('Warning', 'Cross secions files not defined !')

        self.wind6.show()
        self.SaveFiles()

    def Python_Plots(self): 
        """
        function for exporting to plots.xml file
        """     
        v_1 = self.plainTextEdit_7
        #self.detect_components()
        self.wind7 = ExportPlots(v_1, self.plot_name_list, self.plot_id_list, self.plots_file_name)
        self.wind7.show()
        self.SaveFiles()

    def SetRunMode(self):
        cursor = self.plainTextEdit_7.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText('\n')
        if self.RunMode_CB.currentIndex() == 0:
            pass
        elif self.RunMode_CB.currentIndex() == 1:
            cursor.insertText('openmc.run()\n')
        elif self.RunMode_CB.currentIndex() == 2:
            cursor.insertText('openmc.calculate_volumes()\n')
        elif self.RunMode_CB.currentIndex() == 3:
            cursor.insertText('openmc.plot_geometry()\n')
        elif self.RunMode_CB.currentIndex() == 4:
            cursor.insertText('openmc.plot_inline()\n')
        elif self.RunMode_CB.currentIndex() == 5:
            cursor.insertText('openmc.search_for_keff()\n')
        self.RunMode_CB.setCurrentIndex(0)

    def clear_text(self, text):
        if text != "\n":
            self.plainTextEdit_8.clear()
            self.lineLabel1.setText("Ready")

    def RunPB_State(self):
        if self.radioButton.isChecked():   #   xml scripts
            self.pushButton_15.setEnabled(True)
        else:
            self.pushButton_15.setEnabled(False)

    def View_2D(self):                                  # modified to handle many plots
        #self.tabWidget.setCurrentIndex(2)
        if self.directory:
            os.chdir(self.directory)            
            if glob.glob('*.png'):
                image_list = glob.glob('*.png')
            elif glob.glob('*.ppm'):
                image_list = glob.glob('*.ppm')
            elif glob.glob('*.jpg'):
                image_list = glob.glob('*.jpg')
            elif glob.glob('*.jpeg'):
                image_list = glob.glob('*.jpeg')
            elif glob.glob('*.bmp'):
                image_list = glob.glob('*.bmp')
            elif glob.glob('*.gif'):
                image_list = glob.glob('*.gif')
            else:
                self.showDialog('Warning', 'No images found !')
                return
            if image_list:
                image_number = len(image_list)
                self.ImView = [""] * image_number
                '''if self.which('eog'):
                    for i in range(image_number):
                        os.popen('eog ' + image_list[i])        # this could replace the above
                else:'''
                for i in range(image_number):
                    self.ImView[i] = QImageViewer(image_list[i]) 
                    self.ImView[i].show()            
            else:
                self.showDialog('Warning', 'No images found !')
        else:
            self.showDialog('Warning', 'No project has been loaded !')

        os.chdir(self.app_dir)

    def which(self, pgm):
        path = os.getenv('PATH')
        for p in path.split(os.path.pathsep):
            p = os.path.join(p, pgm)
            if os.path.exists(p) and os.access(p, os.X_OK):
                return p

    def View_3D(self):                                  # modified to handle many plots
        self.tabWidget.setCurrentIndex(2)
        self.plainTextEdit_8.clear()
        if self.directory:
            os.chdir(self.directory)
        vti_file = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', "~", "*.vti")[0]
        if vti_file:
            file = open(vti_file, "r")
            cmd = 'paraview ' + vti_file
            self.process.start(cmd, QtCore.QIODevice.ReadWrite)
        os.chdir(self.app_dir)

    def View_Track(self):
        self.tabWidget.setCurrentIndex(2)
        self.plainTextEdit_8.clear()
        if self.directory:
            os.chdir(self.directory)
        vti_file = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', "~", "track*.vtp")[0]
        if vti_file:
            file = open(vti_file, "r")
            cmd = 'paraview ' + vti_file
            self.process.start(cmd, QtCore.QIODevice.ReadWrite)
        os.chdir(self.app_dir)

    def Process(self):
        # QProcess object for output window
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)  # added Unification des 2 sorties (normale + erreur) du QProcess
        # QProcess emits `readyRead` when there is data to be read
        self.process.readyRead.connect(self.dataReady)
        #self.process.started.connect(lambda: self.plainTextEdit_8.insertPlainText("starting process\n"))
        #self.process.finished.connect(lambda: self.plainTextEdit_8.insertPlainText("process ended\n\n"))
        self.process.stateChanged.connect(self.handle_state)

    def Run_OpenMC(self):
        self.checkbox.setChecked(True)
        run_openmc = False
        plot_openmc = False
        self.Process()
        os.environ["PATH"] += os.pathsep + os.pathsep.join([self.app_dir])
        if self.radioButton.isChecked():     #   xml scripts
            if self.directory:
                self.lineLabel1.setText("Running Project :" + self.directory)
                os.chdir(self.directory)
                self.process.start('openmc ', QtCore.QIODevice.ReadWrite)  # modified
                os.chdir(self.app_dir)
            else:
                msg = 'Select your project directory first !!!!'
                self.showDialog('Warning', msg)
        else:                                   #   python script
            if not self.plainTextEdit_7.toPlainText().strip():
                self.lineLabel1.setText("no Code to run!")
                return
            else:
                if self.filename:
                    for line in self.plainTextEdit_7.toPlainText().split():
                        if self.openmc_version >= 141:
                            if 'rectangular_prism' in line:
                                self.showDialog('Warning', 'rectangular_prism must be replaced by RectangularPrism!')
                                return
                            if 'hexagonal_prism' in line:
                                self.showDialog('Warning', 'hexagonal_prism must be replaced by HexagonalPrism!')
                                return
                        if 'openmc.run()' in line and '#openmc.run()' not in line.strip():
                            run_openmc = True
                        if 'openmc.plot_geometry()' in line and '#openmc.plot_geometry()' not in line.strip():
                            plot_openmc = True
                    cmd = 'python3'
                    self.readData(cmd, self.process)
                    os.chdir(self.app_dir)
                    if 'export_to_xml()' in self.plainTextEdit_7.toPlainText():
                        self.ViewXML(self.plainTextEdit_8)
                        if not run_openmc and not plot_openmc:
                            self.showDialog('Warning', 'No simulation neither plot will be processed.\n Only xml files will be created !')
                else:
                    msg = 'Select your project python script or save it first !'
                    self.showDialog('Warning', msg)

    def runPy3(self):
        self.checkbox.setChecked(True)
        run_openmc = False
        plot_openmc = False
        for line in self.plainTextEdit_7.toPlainText().split():
            if self.openmc_version >= 141:
                if 'rectangular_prism' in line:
                    self.showDialog('Warning', 'rectangular_prism must be replaced by RectangularPrism!')
                    return
                if 'hexagonal_prism' in line:
                    self.showDialog('Warning', 'hexagonal_prism must be replaced by HexagonalPrism!')
                    return        
        # Qprocess for shell_editor process
        #self.Process()
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyRead.connect(self.shell_dataReady)
        self.process.started.connect(lambda: self.shellWin.insertPlainText("starting process\n"))
        self.process.finished.connect(lambda: self.shellWin.insertPlainText("process ended\n"))

        if not self.plainTextEdit_7.toPlainText().strip():
            self.lineLabel1.setText("no Code to run!")
            return
        else:
            if self.filename:
                self.fileSave()
                cmd = 'python3'
                self.readData(cmd, self.process)
                time.sleep(1)
                if 'export_to_xml()' in self.plainTextEdit_7.toPlainText():
                    self.ViewXML(self.shellWin)
                    if 'openmc.run()' in self.plainTextEdit_7.toPlainText() and '#openmc.run()' not in self.plainTextEdit_7.toPlainText().strip():
                        run_openmc = True
                    if 'openmc.plot_geometry()' in self.plainTextEdit_7.toPlainText() and '#openmc.plot_geometry()' not in self.plainTextEdit_7.toPlainText().strip():
                        plot_openmc = True
                    if not run_openmc and not plot_openmc:
                        self.showDialog('Warning',
                                        'No simulation neither plot will be processed.\n Only xml files will be created !')
            else:
                self.filename = "/tmp/tmp.py"
                self.fileSave()
                self.runPy3() 
        os.chdir(self.app_dir)
        
    def createGeom(self):  # modified to handle many plots
        self.checkbox.setChecked(True)
        os.environ["PATH"] += os.pathsep + os.pathsep.join([self.app_dir])
        self.ploting = True
        self.Process()
        if self.radioButton.isChecked():  # xml scripts
            if self.directory:
                os.chdir(self.directory)
                cmd = 'openmc -p'
                self.process.start(cmd, QtCore.QIODevice.ReadWrite)
                self.lineLabel1.setText(" Creating plots of Project : " + self.directory)
            else:
                msg = 'Select your project directory or save your project first !'
                self.showDialog('Warning', msg)

    def killPython(self):
        try:
            if self.process:
                self.process.kill()
        except:
            self.showDialog('Warning', 'No process is running!')

    def handle_state(self, state):
        states = {
            QProcess.NotRunning: 'Not running',
            QProcess.Starting: 'Starting',
            QProcess.Running: 'Running',
        }
        state_name = states[state]
        self.lineLabel2.setText(f"Process state: {state_name}")
        if state_name == 'Not running':
            if self.radioButton.isChecked():
                self.pushButton_15.setEnabled(True)
            else:
                self.ViewXML(self.plainTextEdit_8)
            self.pushButton_19.setEnabled(True)
            self.plainTextEdit_8.moveCursor(QTextCursor.End)
            if self.ploting:
                self.plainTextEdit_8.insertPlainText('\n  Plots processing terminated\n')
                self.ploting = False
            else:
                self.plainTextEdit_8.insertPlainText('\n  Processing terminated\n')
        else:
            self.pushButton_15.setEnabled(False)
            self.pushButton_19.setEnabled(False)

    def readData(self, cmd, Process):
        if self.filename:
            dname = QFileInfo(self.filename).filePath().replace(QFileInfo(self.filename).fileName(), "")
        try:
            if dname:
                os.chdir(dname)
                if cmd == 'python3':
                    Process.start(cmd, ['-u', dname + self.strippedName(self.filename)])
                elif cmd == 'openmc':
                    Process.start(cmd)
        except:
            self.showDialog('Warning', 'No project is loaded !')
            return

        os.chdir(self.appfolder)

    def dataReady(self):
        cursor = self.plainTextEdit_8.textCursor()
        self.plainTextEdit_8.setReadOnly(True)
        cursor.movePosition(cursor.End)
        # Here we have to decode the QByteArray
        cursor.insertText(str(self.process.readAll().data().decode()))
        self.plainTextEdit_8.ensureCursorVisible()
        self.plainTextEdit_7.ensureCursorVisible()

    def shell_dataReady(self):
        cursor = self.shellWin.textCursor()
        self.shellWin.setReadOnly(True)
        cursor.movePosition(cursor.End)
        # Here we have to decode the QByteArray
        cursor.insertText(str(self.process.readAll().data().decode()))
        self.shellWin.ensureCursorVisible()
        self.plainTextEdit_7.ensureCursorVisible()

    def normalOutputWritten(self, text):
        if self.tabWidget.currentWidget().objectName() == 'tab_xml':
            if self.tabWidget_3.currentWidget().objectName() == 'tab_11':
                self.cursor = self.plainTextEdit_1.textCursor()
                self.plainTextEdit_1.setTextCursor(self.cursor)
                self.cursor.insertText(text)
                self.plainTextEdit_1.moveCursor(self.cursor.End)
            elif self.tabWidget_3.currentWidget().objectName() == 'tab_12':
                cursor = self.plainTextEdit_2.textCursor()
                cursor.insertText(text)
            elif self.tabWidget_3.currentWidget().objectName() == 'tab_13':
                cursor = self.plainTextEdit_3.textCursor()
                cursor.insertText(text)
            elif self.tabWidget_3.currentWidget().objectName() == 'tab_14':
                cursor = self.plainTextEdit_4.textCursor()
                cursor.insertText(text)
            elif self.tabWidget_3.currentWidget().objectName() == 'tab_15':
                cursor = self.plainTextEdit_5.textCursor()
                cursor.insertText(text)
            elif self.tabWidget_3.currentWidget().objectName() == 'tab_16':
                cursor = self.plainTextEdit_6.textCursor()
                cursor.insertText(text)
        elif self.tabWidget.currentWidget().objectName() == 'tab_python':
            cursor = self.plainTextEdit_7.textCursor()
            cursor.insertText(text)
        elif self.tabWidget.currentWidget().objectName() == 'tab_run':
            cursor = self.plainTextEdit_8.textCursor()
            cursor.insertText(text)

    def Exit(self):
        reply = QMessageBox.question(self, "Message",
            "Are you sure you want to quit ?", QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.Close_Project()
            qapp.quit()
        else:
            pass 
            
    def OpenFiles(self):
        #self.comboSize.setCurrentIndex(4)
        if self.tabWidget.currentWidget().objectName() == 'tab_run':
            msg = 'Select xml or python project tab first !'
            self.showDialog('Warning', msg)
            return

        self.shellWin.clear()
        self.folder = self.directory   # added
        if self.directory: # and self.plainTextEdit_1.toPlainText():
            qm = QMessageBox
            ret = qm.question(self, 'Warning',' Current project is not empty, close it ?', qm.Yes | qm.No)
            if ret == qm.Yes:
                self.Close_Project() 
            elif ret == qm.No:
                return

        if self.tabWidget.currentWidget().objectName() == 'tab_python':   # python script
            self.filename = QtWidgets.QFileDialog.getOpenFileName(self,'Open File', "~", "*.py")[0]
            self.directory = os.path.dirname(self.filename)
            self.openedFiles = True
            if self.filename:
                self.lineLabel1.setText("File path: " + self.filename)
                self.lineLabel2.setText('  Blocks number : ' + str(self.editor.blockCount()))
                self.lineLabel3.setText("Cursor position:    line " + str(self.line) + " | column " + str(self.pos))
            if self.filename != "":
                file = open(self.filename,"r")
                self.plainTextEdit_7.setPlainText(file.read())
                self.plainTextEdit_7.show()
                self.detect_components()
                self.regions = self.cell_name_list + self.surface_name_list

        elif self.tabWidget.currentWidget().objectName() == 'tab_xml':   # xml scripts
            self.directory = QFileDialog.getExistingDirectory()
            if self.directory:
                pass
            else :
                self.directory = self.folder
            if self.directory:
                self.lineLabel1.setText("Project path: " + self.directory)
                self.lineLabel2.setText('  Blocks number : ' + str(self.editor.blockCount()))
                self.lineLabel3.setText("Cursor position:    line " + str(self.line) + " | column " + str(self.pos))
                self.plainTextEdit_4.clear()
                self.plainTextEdit_5.clear()
                self.plainTextEdit_6.clear() 
                if path.exists(self.directory + '/geometry.xml') == True:
                    filename = self.directory+'/geometry.xml'
                    file = open(filename,"r")
                    self.plainTextEdit_1.setPlainText(file.read())
                    self.plainTextEdit_1.show()
                if path.exists(self.directory + '/materials.xml') ==True:
                    filename = self.directory+'/materials.xml'
                    file = open(filename,"r")
                    self.plainTextEdit_2.setPlainText(file.read())
                    self.plainTextEdit_2.show()
                if path.exists(self.directory + '/settings.xml') ==True:
                    filename = self.directory+'/settings.xml'
                    file = open(filename,"r")
                    self.plainTextEdit_3.setPlainText(file.read())
                    self.plainTextEdit_3.show()
                if path.exists(self.directory + '/tallies.xml') ==True:
                    filename = self.directory+'/tallies.xml'
                    file = open(filename,"r")
                    self.plainTextEdit_4.setPlainText(file.read())
                    self.plainTextEdit_4.show()
                if path.exists(self.directory + '/cmfd.xml') ==True:
                    filename = self.directory+'/cmfd.xml'
                    file = open(filename,"r")
                    self.plainTextEdit_6.setPlainText(file.read())
                    self.plainTextEdit_6.show()
                if path.exists(self.directory + '/plots.xml') ==True:
                    filename = self.directory+'/plots.xml'
                    file = open(filename,"r")
                    self.plainTextEdit_5.setPlainText(file.read())
                    self.plainTextEdit_5.show()
                else:
                    pass
                self.tabWidget_3.setCurrentIndex(0)
        self.Update_StatusBar()
        self.textSize(float(self.comboSize.currentText()))

    def NewFiles(self):
        #self.comboSize.setCurrentIndex(4)
        self.shellWin.clear()
        if self.tabWidget.currentWidget().objectName() == 'tab_python':
            try:
                if self.directory:
                    qm = QMessageBox
                    ret = qm.question(self, 'Warning', ' Current project is not empty, close it ?', qm.Yes | qm.No)
                    if ret == qm.Yes:
                        self.Close_Project()
                    elif ret == qm.No:
                        return  
                if self.plainTextEdit_7.toPlainText().strip():
                    qm = QMessageBox
                    ret = qm.question(self, 'Warning', 'Python script window is not empty! It will be cleared!')
                    if ret == qm.Yes:
                        self.plainTextEdit_7.clear()
                    elif ret == qm.No:
                        return
                elif self.plainTextEdit_1.toPlainText():
                    qm = QMessageBox
                    ret = qm.question(self, 'Warning', 'XML script window is not empty! It will be cleared!')
                    if ret == qm.Yes:
                        self.plainTextEdit_1.clear()
                    elif ret == qm.No:
                        return
            except:
                pass

            self.Close_Project()
            v_1 = self.plainTextEdit_7
            self.wind8 = InfoPythonScript(v_1)
            self.wind8.show()
            self.openedFiles = False
            self.new_File = True
            self.clear_Lists()
        elif self.tabWidget.currentWidget().objectName() == 'tab_xml':
            if self.directory:
                qm = QMessageBox
                ret = qm.question(self, 'Warning', ' Current project is not empty, close it ?', qm.Yes | qm.No)
                if ret == qm.Yes:
                    self.Close_Project()
                elif ret == qm.No:
                    return
            elif self.plainTextEdit_7.toPlainText().strip():
                qm = QMessageBox
                ret = qm.question(self, 'Warning', 'Python script window is not empty! It will be cleared!')
                if ret == qm.Yes:
                    self.plainTextEdit_7.clear()
                elif ret == qm.No:
                    return
            elif self.plainTextEdit_1.toPlainText():
                qm = QMessageBox
                ret = qm.question(self, 'Warning', 'XML script window is not empty! It will be cleared!')
                if ret == qm.Yes:
                    self.Close_Project()
                elif ret == qm.No:
                    return
            v_1 = self.plainTextEdit_1
            v_2 = self.plainTextEdit_2
            v_3 = self.plainTextEdit_3
            v_4 = self.plainTextEdit_4
            v_5 = self.plainTextEdit_5
            v_6 = self.plainTextEdit_6
            v_7 = self.statusbar
            if self.directory and self.plainTextEdit_1.toPlainText():
                pass
            else:
                self.wind = InfoXMLScripts(v_1,v_2,v_3,v_4,v_5,v_6,v_7)
                self.wind.show()
                self.openedFiles = False
                self.new_File = True
        else:
            msg = 'Select xml or python project to create first !'
            self.showDialog('Warning', msg)
        self.textSize(float(self.comboSize.currentText()))

    def SaveFiles(self):
        #self.comboSize.setCurrentIndex(4)
        if self.tabWidget.currentWidget().objectName() == 'tab_xml':
            if self.new_File:
                self.directory = self.wind.directory
            else:
                pass
            if self.directory:
                if path.exists(self.directory + '/geometry.xml') == True:
                    files = self.directory + '/geometry.xml'
                    file = open(files, "w")
                    file.write(self.plainTextEdit_1.toPlainText())
                    file.close()
                if path.exists(self.directory + '/materials.xml') == True:
                    files = self.directory + '/materials.xml'
                    file = open(files, "w")
                    file.write(self.plainTextEdit_2.toPlainText())
                    file.close()
                if path.exists(self.directory + '/settings.xml') == True:
                    files = self.directory + '/settings.xml'
                    file = open(files, "w")
                    file.write(self.plainTextEdit_3.toPlainText())
                    file.close()
                if path.exists(self.directory + '/tallies.xml') == True:
                    files = self.directory + '/tallies.xml'
                    file = open(files, "w")
                    file.write(self.plainTextEdit_4.toPlainText())
                    file.close()
                if path.exists(self.directory + '/cmfd.xml') == True:
                    files = self.directory + '/cmfd.xml'
                    file = open(files, "w")
                    file.write(self.plainTextEdit_6.toPlainText())
                    file.close()
                if path.exists(self.directory + '/plots.xml') == True:
                    files = self.directory + '/plots.xml'
                    file = open(files, "w")
                    file.write(self.plainTextEdit_5.toPlainText())
                    file.close()
                else:
                    pass
            else:
                self.showDialog('Warning', 'No directory has been selected !')
                return

        elif self.tabWidget.currentWidget().objectName() == 'tab_python':
            lines = self.plainTextEdit_7.toPlainText().split('\n')
            self.cursor = self.plainTextEdit_7.textCursor()
            self.plainTextEdit_7.clear()
            text = [x for x in lines if x.strip()]   # reduces spaces to ''
            self.cursor.insertText(str('\n'.join(text)))
            if self.new_File:
                self.directory = self.wind8.directory
            else:
                pass
            if self.plainTextEdit_7.toPlainText():
                if self.directory:
                    if not self.filename:
                        self.filename = self.directory + '/build_xml.py'
                if self.filename:
                    file = open(self.filename,"w")
                    file.write(self.plainTextEdit_7.toPlainText())
                    file.close()
                else:
                    pass

        elif self.tabWidget.currentWidget().objectName() == 'tab_run':
                self.SaveAsFiles()
        self.textSize(float(self.comboSize.currentText()))

    def SaveAsFiles(self):
        #self.comboSize.setCurrentIndex(4)
        if self.tabWidget.currentWidget().objectName() == 'tab_python':
            self.filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save as File', "Python Files (*.py);;All Files (*)")[0]
            if self.filename:
                file = open(self.filename, "w")
                file.write(self.plainTextEdit_7.toPlainText())
                file.close()
            else:
                pass
        elif self.tabWidget.currentWidget().objectName() == 'tab_xml':
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            self.filename, _ = QFileDialog.getSaveFileName(self, "Save XML Files", "",
                                                           "XML Files (*.xml);;All Files (*)", options=options)
            if self.filename != "":
                file = open(self.filename, "w")
                if 'geometry.xml' in self.filename:
                    file.write(self.plainTextEdit_1.toPlainText())
                    file.close()
                elif 'materials.xml' in self.filename:
                    file.write(self.plainTextEdit_2.toPlainText())
                    file.close()
                elif 'settings.xml' in self.filename:
                    file.write(self.plainTextEdit_3.toPlainText())
                    file.close()
                elif 'tallies.xml' in self.filename:
                    file.write(self.plainTextEdit_4.toPlainText())
                    file.close()
                elif 'cmfd.xml' in self.filename:
                    file.write(self.plainTextEdit_6.toPlainText())
                    file.close()
                elif 'plots.xml' in self.filename:
                    file.write(self.plainTextEdit_5.toPlainText())
                    file.close()
        elif self.tabWidget.currentWidget().objectName() == 'tab_run':
            if self.plainTextEdit_8.toPlainText():
                self.filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save as File', "*.log")[0]
                if not self.filename:  # Cancel
                    pass
                else:
                    if "*" in self.filename:
                        msg = 'Choose file name first !'
                        self.wind4.showDialog(self, 'Warning', msg)
                        self.filename = ''
                    else:
                        file = open(self.filename, "w")
                        file.write(self.plainTextEdit_8.toPlainText())
                        file.close()
            else:
                pass
        else:
            pass
        self.textSize(float(self.comboSize.currentText()))

    def fileSave(self):
        ### save File
        #self.comboSize.setCurrentIndex(4)
        if self.tabWidget.currentWidget().objectName() != 'tab_xml':
            if (self.filename != ""):
                file = QFile(self.filename)
                if not file.open(QFile.WriteOnly | QFile.Text):
                    QMessageBox.warning(self, "Error",
                                        "Cannot write file %s:\n%s." % (self.filename, file.errorString()))
                    return
                outstr = QTextStream(file)
                QApplication.setOverrideCursor(Qt.WaitCursor)
                outstr << self.editor.toPlainText()
                QApplication.restoreOverrideCursor()
                self.setModified(False)
                self.fname = QFileInfo(self.filename).fileName()
                self.setWindowTitle(self.fname + "[*]")
                #self.lineLabel2.setText("File saved.")
                self.setCurrentFile(self.filename)
                self.editor.setFocus()
            else:
                self.fileSaveAs()
            self.textSize(float(self.comboSize.currentText()))
        else:
            self.textSize(float(self.comboSize.currentText()))
            return

    def fileSaveAs(self):
        #self.comboSize.setCurrentIndex(4)
        if self.tabWidget.currentWidget().objectName() != 'tab_xml':
            fn, _ = QFileDialog.getSaveFileName(self, "Save as...", self.filename,
                                                "Python files (*.py)")
            if not fn:
                self.shellWin.setPlainText("Saving canceled")
                return False

            lfn = fn.lower()
            if not lfn.endswith('.py'):
                fn += '.py'
            self.filename = fn
            self.fname = QFileInfo(QFile(fn).fileName())
            return self.fileSave()
        else:
            return
        self.textSize(float(self.comboSize.currentText()))

    def Close_Project(self):
        if self.tabWidget.currentWidget().objectName() == 'tab_python':   #   python script
            self.filename = ''
            if self.directory:
                self.directory = ''
            if self.new_File :
                self.wind8.filename = ''
        elif self.tabWidget.currentWidget().objectName() == 'tab_xml':  # xml scripts
            if self.filename:
                self.filename = ''
            self.directory = ''
        else:
            self.filename = ''
            self.directory = ''

        self.lineLabel1.setText("Ready")
        self.plainTextEdit_1.clear()
        self.plainTextEdit_2.clear()
        self.plainTextEdit_3.clear()
        self.plainTextEdit_4.clear()
        self.plainTextEdit_5.clear()
        self.plainTextEdit_6.clear()
        self.plainTextEdit_7.clear()
        self.plainTextEdit_8.clear()
        self.comboSize.setCurrentIndex(4)

    def question(self, alert, msg) : 
        qm = QMessageBox
        ret = qm.question(self, alert, msg, qm.Yes | qm.No)
        if ret == qm.Yes:
            self.Close_Project() 
            self.NewFiles()
        elif ret == qm.No:
            pass

    def parseFileName(self):
        filename = self.filename.split("/")
        self.fname = filename[-1]
        return self.fname  
                
    def About(self):
        title = "about ERSN-OpenMC-Py"
        message = """
                    <span style='color: #3465a4; font-size: 20pt;font-weight: bold;'>
                    ERSN-OpenMC-Py v 1.2 </strong></span></p><h3>

                    <span style='color: #000000; font-size: 14pt;'>
                    created by 
                    <a title='M. Lahdour & T. El Bardouni' href='https://github.com/mohamedlahdour' target='_blank'>M. Lahdour & T. El Bardouni </a> <br><br>
                    from University Abdelmalek Essaadi, 
                    Radiations and Nuclear Systems Laboratory ERSN, Tetouan, Morocco </strong></span></p><h3>

                    ©2024 M. Lahdour & T. El Bardouni </strong></span></p>
                        """
        QMessageBox(QMessageBox.Information, title, message, QMessageBox.NoButton, self,
                    Qt.Dialog | Qt.NoDropShadowWindowHint).show()
        
    def Help(self):
        title = "How to use ERSN-OpenMC-Py"
        message = """
                            <span style='color: #000000; font-size: 12pt;'>
                            contact us     
                            <a title='M. Lahdour' href='mailto:mlahdour@uae.ac.ma' target='_blank'>M. Lahdour  </a> 
                            or 
                            <a title='T. El Bardouni' href='mailto:telbardouni@uae.ac.ma' target='_blank'>T. El Bardouni </a> <br><br>
                            <span style='color: #000000; font-size: 10pt;'>
                            University Abdelmalek Essaadi, 
                            Radiations and Nuclear Systems Laboratory ERSN, Tetouan, Morocco</strong></span></p><h2>
                            <a title:'Github repository' href='https://github.com/mohamedlahdour/ERSN-OpenMC-Py' target='_blank'>Github repository</a> <br><br> 
                            <a title:'Readme' href='https://github.com/mohamedlahdour/ERSN-OpenMC-Py/blob/master/readme.txt' target='_blank'>Readme</a> <br><br> 

                            ©2024 M. Lahdour & T. El Bardouni </strong></span></p>
                                """
        QMessageBox(QMessageBox.Information, title, message, QMessageBox.NoButton, self,
                    Qt.Dialog | Qt.NoDropShadowWindowHint).show()

    def Undo(self):
        self.editor.undo()

    def Redo(self):
        self.editor.redo()

    def Copy(self):
        self.editor.copy()

    def Cut(self):
        self.editor.cut()

    def Paste(self):
        self.editor.paste()

    def Align_Left(self):
        self.plainTextEdit_7.setAlignment(QtCore.Qt.AlignLeft)

    def Align_Right(self):
        self.plainTextEdit_7.setAlignment(QtCore.Qt.AlignRight) 

    def Align_Center(self):
        self.plainTextEdit_7.setAlignment(QtCore.Qt.AlignCenter)

    def Align_Justify(self):
        self.plainTextEdit_7.setAlignment(QtCore.Qt.AlignJustify)

    ###############################################################################
    ###############################################################################
    ##########   myEditor python functions for editor from PyEdit.py  #############
    ###############################################################################
    ###############################################################################

    def textSize(self, pointSize):
        pointSize = float(self.comboSize.currentText())
        if pointSize > 0:
            fmt = QTextCharFormat()
            fmt.setFontPointSize(pointSize)
            self.mergeFormatOnWordOrSelection(fmt)

    def mergeFormatOnWordOrSelection(self, format):
        cursor = self.editor.textCursor()
        if not cursor.hasSelection():
            #cursor.select(QTextCursor.WordUnderCursor)
            cursor.select(QTextCursor.Document)

        cursor.mergeCharFormat(format)
        self.editor.mergeCurrentCharFormat(format)

    def changeBGColor(self):
        all = self.editor.document().toHtml()
        bgcolor = all.partition("<body style=")[2].partition(">")[0].partition('bgcolor="')[2].partition('"')[0]
        if not bgcolor == "":
            col = QColorDialog.getColor(QColor(bgcolor), self)
            if not col.isValid():
                return
            else:
                colorname = col.name()
                new = all.replace("bgcolor=" + '"' + bgcolor + '"', "bgcolor=" + '"' + colorname + '"')
                self.editor.document().setHtml(new)
        else:
            col = QColorDialog.getColor(QColor("#FFFFFF"), self)
        if not col.isValid():
            return
        else:
            all = self.editor.document().toHtml()
            body = all.partition("<body style=")[2].partition(">")[0]
            newbody = body + "bgcolor=" + '"' + col.name() + '"'
            new = all.replace(body, newbody)
            self.editor.document().setHtml(new)
        bgcolor = "background-color: " + col.name()
        self.editor.setStyleSheet(bgcolor)

    def handleShellWinToggle(self):
        if self.shellWin.isVisible():
            self.shellWin.setVisible(False)
            self.D_widgets.hide()
        else:
            self.shellWin.setVisible(True)
            self.D_widgets.show()

    def keyPressEvent(self, event):
        if self.editor.hasFocus():
            if event.key() == Qt.Key_F10:
                self.findNextWord()

    def CursorPositionChanged(self):
        self.line = self.editor.textCursor().blockNumber() + 1
        self.pos = self.editor.textCursor().positionInBlock()
        self.lineLabel3.setText("line " + str(self.line) + " | position " + str(self.pos))

    def Test(self):
        self.editor.selectAll()

    def reindentText(self):
        if self.editor.toPlainText() == "":  # or self.editor.toPlainText() == self.mainText:
            self.lineLabel1.setText("no code to reindent")
        else:
            self.editor.selectAll()
            tab = "\t"
            oldtext = self.editor.textCursor().selectedText()
            newtext = oldtext.replace(tab, "    ")
            self.editor.textCursor().insertText(newtext)
            self.lineLabel1.setText("code reindented")

    def insertColor(self):
        col = QColorDialog.getColor(QColor("#000000"), self)
        if not col.isValid():
            return
        else:
            colorname = 'QColor("' + col.name() + '")'
            self.editor.textCursor().insertText(colorname)

    def changeColor(self):
        fmt = QTextCharFormat()
        if not self.editor.textCursor().selectedText() == "":
            col = QColorDialog.getColor(QColor("#" + self.editor.textCursor().selectedText()), self)
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

    ### QPlainTextEdit contextMenu
    def contextMenuRequested(self, point):
        cmenu = QMenu()
        cmenu = self.editor.createStandardContextMenu()
        cmenu.addSeparator()
        if not self.editor.textCursor().selectedText() == "":
            cmenu.addAction(QIcon("src/icons/edit-find-replace.png"), "replace all occurrences with", self.replaceThis)
            cmenu.addSeparator()
        cmenu.addAction(QIcon.fromTheme("firefox"), "find with 'google'", self.findWithFirefox)
        cmenu.addAction(QIcon("src/icons/edit-find.png"), "find this (F10)", self.findNextWord)
        #cmenu.addAction(self.texteditAction)
        cmenu.addSeparator()
        cmenu.addAction(self.py3Act)
        cmenu.addSeparator()
        cmenu.addAction(self.commentAct)
        cmenu.addAction(self.uncommentAct)
        cmenu.addSeparator()
        if not self.editor.textCursor().selectedText() == "":
            cmenu.addAction(self.commentBlockAct)
            cmenu.addAction(self.uncommentBlockAct)
            cmenu.addSeparator()
            cmenu.addAction(self.indentAct)
            cmenu.addAction(self.indentLessAct)
        cmenu.addSeparator()
        cmenu.addAction(QIcon('src/icons/color1.png'), "insert QColor", self.insertColor)

        cmenu.addSeparator()
        cmenu.addAction(QIcon('src/icons/color.png'), "change Color", self.changeColor)
        cmenu.exec_(self.editor.mapToGlobal(point))

        ### shellWin contextMenu

    def shellWincontextMenuRequested(self, point):
        shellWinMenu = QMenu()
        shellWinMenu = self.shellWin.createStandardContextMenu()
        #        shellWinMenu.addAction(QAction(QIcon.fromTheme('edit-copy'), "Copy", self, triggered = self.shellWin.copy, shortcut = "Ctrl+c"))
        shellWinMenu.addSeparator()
        shellWinMenu.addAction(QIcon.fromTheme("firefox"), "find with 'google'", self.findWithFirefox_shell)
        if "/" in self.shellWin.textCursor().selectedText():
            shellWinMenu.addAction(self.fmanAction)
        shellWinMenu.exec_(self.shellWin.mapToGlobal(point))

    def replaceThis(self):
        rtext = self.editor.textCursor().selectedText()
        text = QInputDialog.getText(self, "replace with", "replace '" + rtext + "' with:", QLineEdit.Normal, "")
        oldtext = self.editor.document().toPlainText()
        if not (text[0] == ""):
            newtext = oldtext.replace(rtext, text[0])
            self.editor.setPlainText(newtext)
            self.setModified(True)

    def findWithFirefox(self):
        if self.editor.textCursor().selectedText() == "":
            tc = self.editor.textCursor()
            tc.select(QTextCursor.WordUnderCursor)
            rtext = tc.selectedText()
        else:
            rtext = "python%20" + self.editor.textCursor().selectedText().replace(" ", "%20")
        url = "https://www.google.com/search?q=" + rtext
        QProcess.startDetached("firefox " + url)

    def findWithFirefox_shell(self):
        if not self.shellWin.textCursor().selectedText() == "":
            rtext = "python%20" + self.shellWin.textCursor().selectedText().replace(" ", "%20")
            url = "https://www.google.com/search?q=" + rtext.replace(" ", "%20")
            QProcess.startDetached("firefox " + url)

    def findNextWord(self):
        if self.editor.textCursor().selectedText() == "":
            tc = self.editor.textCursor()
            tc.select(QTextCursor.WordUnderCursor)
            rtext = tc.selectedText()
        else:
            rtext = self.editor.textCursor().selectedText()
        self.findfield.setText(rtext)
        self.findText()

    def indentLine(self):
        if not self.editor.textCursor().selectedText() == "":
            newline = u"\u2029"
            ot = self.editor.textCursor().selectedText()
            theList = ot.splitlines()
            newlist = ["    " + suit for suit in theList]
            newtext = newline.join(newlist)
            self.editor.textCursor().insertText(newtext)
            self.setModified(True)
            self.editor.find(newtext)
            self.lineLabel1.setText("more indented")

    def indentLessLine(self):
        if not self.editor.textCursor().selectedText() == "":
            newline = u"\u2029"
            ot = self.editor.textCursor().selectedText()
            theList = ot.splitlines()
            newlist = [suit.replace("    ", "", 1) for suit in theList]
            newtext = newline.join(newlist)
            self.editor.textCursor().insertText(newtext)
            self.setModified(True)
            self.editor.find(newtext)
            self.lineLabel1.setText("less indented")

    def createActions(self):
        for i in range(self.MaxRecentFiles):
            self.recentFileActs.append(
                QAction(self, visible=False,
                        triggered=self.openRecentFile))

    def getLineNumber(self):
        self.editor.moveCursor(self.cursor.StartOfLine)
        linenumber = self.editor.textCursor().blockNumber() + 1
        return linenumber

    def gotoLine(self):
        ln = int(self.gotofield.text())
        linecursor = QTextCursor(self.editor.document().findBlockByLineNumber(ln - 1))
        self.editor.moveCursor(QTextCursor.End)
        self.editor.setTextCursor(linecursor)

    def gotoErrorLine(self, ln):
        if ln.isalnum:
            t = int(ln)
            if t != 0:
                linecursor = QTextCursor(self.editor.document().findBlockByLineNumber(t - 1))
                self.editor.moveCursor(QTextCursor.End)
                self.editor.setTextCursor(linecursor)
                self.editor.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            else:
                return

    def clearLabel(self):
        self.shellWin.clear()

    def openRecentFile(self):
        #self.comboSize.setCurrentIndex(4)
        action = self.sender()
        if action:
            myfile = action.data()
            if (self.maybeSave()):
                if QFile.exists(myfile):
                    self.openFileOnStart(myfile)
                else:
                    self.msgbox("Info", "File does not exist!")

    ### New File
    def newFile(self):
        self.shellWin.clear()
        #self.comboSize.setCurrentIndex(4)
        if self.tabWidget.currentWidget().objectName() != 'tab_xml':
            self.openedFiles = True
            if self.maybeSave():
                self.editor.clear()
                # self.editor.setPlainText(self.mainText)
                self.filename = ""
                self.setModified(False)
                self.editor.moveCursor(QTextCursor.End)
                self.lineLabel1.setText("new File created.")
                self.editor.setFocus()
                self.setWindowTitle("new File[*]")
        else:
            return
        self.textSize(float(self.comboSize.currentText()))

    ### open File
    def openFileOnStart(self, path=None):
        #self.comboSize.setCurrentIndex(4)
        self.shellWin.clear()
        if self.tabWidget.currentWidget().objectName() != 'tab_xml':
            if path:
                self.openPath = QFileInfo(path).path()  ### store path for next time
                inFile = QFile(path)
                if inFile.open(QFile.ReadWrite | QFile.Text):
                    text = inFile.readAll()
                    try:
                        # Python v3.
                        text = str(text, encoding='utf8')
                    except TypeError:
                        # Python v2.
                        text = str(text)
                    self.editor.setPlainText(text.replace(tab, "    "))
                    self.setModified(False)
                    self.setCurrentFile(path)
                    self.editor.setFocus()
                    ### save backup
                    file = QFile(self.filename + "_backup")
                    if not file.open(QFile.WriteOnly | QFile.Text):
                        QMessageBox.warning(self, "Error",
                                            "Cannot write file %s:\n%s." % (self.filename, file.errorString()))
                        return
                    outstr = QTextStream(file)
                    QApplication.setOverrideCursor(Qt.WaitCursor)
                    outstr << self.editor.toPlainText()
                    QApplication.restoreOverrideCursor()
        else:
            return
        self.textSize(float(self.comboSize.currentText()))

    ### open File
    def openFile(self, path=None):
        self.shellWin.clear()
        if self.tabWidget.currentWidget().objectName() != 'tab_xml':
            if self.openPath == "":
                self.openPath = self.dirpath
            if self.maybeSave():
                if not path:
                    path, _ = QFileDialog.getOpenFileName(self, "Open File", self.openPath,
                                                          "Python Files (*.py);; all Files (*)")
                if path:
                    self.openFileOnStart(path)
            self.openedFiles = True
        else:
            return
        self.textSize(float(self.comboSize.currentText()))

    def exportPDF(self):
        if self.editor.toPlainText() == "":
            self.lineLabel1.setText("no text to save")
        else:
            newname = self.strippedName(self.filename).replace(QFileInfo(self.filename).suffix(), "pdf")
            fn, _ = QFileDialog.getSaveFileName(self,
                                                "PDF files (*.pdf);;All Files (*)",
                                                (QDir.homePath() + "/PDF/" + newname))
            printer = QtPrintSupport.QPrinter()  #QtPrintSupport.QPrinter.HighResolution)
            printer.setOutputFormat(QtPrintSupport.QPrinter.PdfFormat)
            printer.setOutputFileName(fn)
            self.editor.document().print_(printer)

    def maybeSave(self):
        if self.plainTextEdit_7.toPlainText() not in ["", " "]:
            self.tabWidget.setCurrentIndex(1)

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

    def about(self):
        title = "about ERSN-OpenMC-Py"
        message = """
                    <span style='color: #3465a4; font-size: 20pt;font-weight: bold;'>
                    ERSN-OpenMC-Py v 1.0 </strong></span></p><h3>

                    <span style='color: #000000; font-size: 14pt;'>
                    created by 
                    <a title='M. Lahdour & T. El Bardouni' href='https://github.com/tarekbardouni' target='_blank'>M. Lahdour & T. El Bardouni </a> <br><br>
                    from University Abdelmalek Essaadi, 
                    Radiations and Nuclear Systems Laboratory ERSN, Tetouan, Morocco </strong></span></p><h3>

                    <span style='color: #000000; font-size: 10pt;'>
                    PyEdit Original Python Editor created by 
                    <a title='Axel Schneider' href='http://goodoldsongs.jimdo.com' target='_blank'>Axel Schneider</a> <br><br> </span></p><h3>
                    <span style='color: #3465a4; font-size: 9pt;'>
                    ©2024 M. Lahdour & T. El Bardouni </strong></span></p>
                        """
        self.infobox(title, message)

    def commentBlock(self):
        self.editor.copy()
        clipboard = QApplication.clipboard();
        originalText = clipboard.text()
        mt1 = tab + tab + "'''" + "\n"
        mt2 = "\n" + tab + tab + "'''"
        mt = mt1 + originalText + mt2
        clipboard.setText(mt)
        self.editor.paste()

    def uncommentBlock(self):
        self.editor.copy()
        clipboard = QApplication.clipboard();
        originalText = clipboard.text()
        mt1 = tab + tab + "'''" + "\n"
        mt2 = "\n" + tab + tab + "'''"
        clipboard.setText(originalText.replace(mt1, "").replace(mt2, ""))
        self.editor.paste()

        self.lineLabel1.setText("added block comment")

    def commentLine(self):
        newline = u"\u2029"
        comment = "#"
        List = []
        ot = self.editor.textCursor().selectedText()
        if not self.editor.textCursor().selectedText() == "":
            ### multiple lines selected
            theList = ot.splitlines()
            linecount = ot.count(newline)
            for i in range(linecount + 1):
                List.insert(i, comment + theList[i])
            self.editor.textCursor().insertText(newline.join(list))
            self.setModified(True)
            self.lineLabel1.setText("added comment")
        else:
            ### one line selected
            self.editor.moveCursor(QTextCursor.StartOfLine)
            self.editor.textCursor().insertText("#")

    def uncommentLine(self):
        comment = "#"
        newline = u"\u2029"
        List = []
        ot = self.editor.textCursor().selectedText()
        if not self.editor.textCursor().selectedText() == "":
            ### multiple lines selected
            theList = ot.splitlines()
            linecount = ot.count(newline)
            for i in range(linecount + 1):
                List.insert(i, (theList[i]).replace(comment, "", 1))
            self.editor.textCursor().insertText(newline.join(list))
            self.setModified(True)
            self.lineLabel1.setText("comment removed")
        else:
            ### one line selected
            self.editor.moveCursor(QTextCursor.StartOfLine)
            self.editor.moveCursor(QTextCursor.Right, QTextCursor.KeepAnchor)
            if self.editor.textCursor().selectedText() == comment:
                self.editor.textCursor().deleteChar()
                self.editor.moveCursor(QTextCursor.StartOfLine)
            else:
                self.editor.moveCursor(QTextCursor.StartOfLine)

    def goToLine(self, ft):
        self.editor.moveCursor(int(self.gofield.currentText()),
                               QTextCursor.MoveAnchor)  ### not working

    def findText(self):
        word = self.findfield.text()
        if self.editor.find(word):
            linenumber = self.editor.textCursor().blockNumber() + 1
            self.lineLabel1.setText("found <b>'" + self.findfield.text() + "'</b> at Line: " + str(linenumber))
            self.editor.centerCursor()
        else:
            self.lineLabel1.setText("<b>'" + self.findfield.text() + "'</b> not found")
            self.editor.moveCursor(QTextCursor.Start)
            if self.editor.find(word):
                linenumber = self.editor.textCursor().blockNumber() + 1
                self.lineLabel1.setText("found <b>'" + self.findfield.text() + "'</b> at Line: " + str(linenumber))
                self.editor.centerCursor()

    def match_left(self, block, character, start, found):
        map = {'{': '}', '(': ')', '[': ']'}

        while block.isValid():
            data = block.userData()
            if data is not None:
                braces = data.braces
                N = len(braces)

                for k in range(start, N):
                    if braces[k].character == character:
                        found += 1

                    if braces[k].character == map[character]:
                        if not found:
                            return braces[k].position + block.position()
                        else:
                            found -= 1

                block = block.next()
                start = 0

    def match_right(self, block, character, start, found):
        map = {'}': '{', ')': '(', ']': '['}

        while block.isValid():
            data = block.userData()

            if data is not None:
                braces = data.braces

                if start is None:
                    start = len(braces)
                for k in range(start - 1, -1, -1):
                    if braces[k].character == character:
                        found += 1
                    if braces[k].character == map[character]:
                        if found == 0:
                            return braces[k].position + block.position()
                        else:
                            found -= 1
            block = block.previous()
            start = None

        cursor = self.editor.textCursor()
        block = cursor.block()
        data = block.userData()
        previous, next = None, None

        if data is not None:
            position = cursor.position()
            block_position = cursor.block().position()
            braces = data.braces
            N = len(braces)

            for k in range(0, N):
                if braces[k].position == position - block_position or braces[
                    k].position == position - block_position - 1:
                    previous = braces[k].position + block_position
                    if braces[k].character in ['{', '(', '[']:
                        next = self.match_left(block,
                                               braces[k].character,
                                               k + 1, 0)
                    elif braces[k].character in ['}', ')', ']']:
                        next = self.match_right(block,
                                                braces[k].character,
                                                k, 0)
                    if next is None:
                        next = -1

        if next is not None and next > 0:
            if next == 0 and next >= 0:
                format = QTextCharFormat()

            cursor.setPosition(previous)
            cursor.movePosition(QTextCursor.NextCharacter,
                                QTextCursor.KeepAnchor)

            format.setBackground(QColor('white'))
            self.left_selected_bracket.format = format
            self.left_selected_bracket.cursor = cursor

            cursor.setPosition(next)
            cursor.movePosition(QTextCursor.NextCharacter,
                                QTextCursor.KeepAnchor)

            format.setBackground(QColor('white'))
            self.right_selected_bracket.format = format
            self.right_selected_bracket.cursor = cursor

    def paintEvent(self, event):
        highlighted_line = QTextEdit.ExtraSelection()
        highlighted_line.format.setBackground(lineHighlightColor)
        highlighted_line.format.setProperty(QTextFormat
                                            .FullWidthSelection,
                                            QVariant(True))
        highlighted_line.cursor = self.editor.textCursor()
        highlighted_line.cursor.clearSelection()
        self.editor.setExtraSelections([highlighted_line,
                                        self.left_selected_bracket,
                                        self.right_selected_bracket])

    def document(self):
        return self.editor.document

    def isModified(self):
        return self.editor.document().isModified()

    def setModified(self, modified):
        self.editor.document().setModified(modified)

    def setLineWrapMode(self, mode):
        self.editor.setLineWrapMode(mode)

    def clear(self):
        self.editor.clear()

    def setPlainText(self, *args, **kwargs):
        self.editor.setPlainText(*args, **kwargs)

    def setDocumentTitle(self, *args, **kwargs):
        self.editor.setDocumentTitle(*args, **kwargs)

    def set_number_bar_visible(self, value):
        self.numbers.setVisible(value)

    def replaceAll(self):
        if not self.editor.document().toPlainText() == "":
            if not self.findfield.text() == "":
                self.lineLabel1.setText("replacing all")
                oldtext = self.editor.document().toPlainText()
                newtext = oldtext.replace(self.findfield.text(), self.replacefield.text())
                self.editor.setPlainText(newtext)
                self.setModified(True)
            else:
                self.lineLabel1.setText("nothing to replace")
        else:
            self.lineLabel1.setText("no text")

    def replaceOne(self):
        if not self.editor.document().toPlainText() == "":
            if not self.findfield.text() == "":
                self.lineLabel1.setText("replacing all")
                oldtext = self.editor.document().toPlainText()
                newtext = oldtext.replace(self.findfield.text(), self.replacefield.text(), 1)
                self.editor.setPlainText(newtext)
                self.setModified(True)
            else:
                self.lineLabel1.setText("nothing to replace")
        else:
            self.lineLabel1.setText("no text")

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
        del files[self.MaxRecentFiles:]

        self.settings.setValue('recentFileList', files)

        '''for widget in QApplication.topLevelWidgets():
            if isinstance(widget, myEditor):
                widget.updateRecentFileActions()'''

    def updateRecentFileActions(self):
        if self.settings.contains('recentFileList'):
            mytext = ""
            files = self.settings.value('recentFileList', [])
            try:
                if not len(files) == 0:
                    numRecentFiles = len(files)

                    for i in range(numRecentFiles):
                        text = "&%d %s" % (i + 1, self.strippedName(files[i]))
                        self.recentFileActs[i].setText(text)
                        self.recentFileActs[i].setData(files[i])
                        self.recentFileActs[i].setVisible(True)
                        self.recentFileActs[i].setIcon(QIcon('icons/file.png'))

                    for j in range(numRecentFiles, self.MaxRecentFiles):
                        self.recentFileActs[j].setVisible(False)

                    self.separatorAct.setVisible((numRecentFiles > 0))
                else:
                    for i in range(len(self.recentFileActs)):
                        self.recentFileActs[i].remove()
            except:
                pass

    def strippedName(self, fullFileName):
        return QFileInfo(fullFileName).fileName()

    def clearRecentFiles(self):
        self.settings.remove('recentFileList')
        self.recentFileActs = []
        self.settings.sync()
        '''for widget in QApplication.topLevelWidgets():
            if isinstance(widget, myEditor):
                widget.updateRecentFileActions()'''
        try:
            self.updateRecentFileActions()
        except:
            pass

    def readSettings(self):
        if self.settings.value("pos") != "":
            pos = self.settings.value("pos", QPoint(200, 200))
            self.move(pos)
        if self.settings.value("size") != "":
            size = self.settings.value("size", QSize(400, 400))
            self.resize(size)

    def writeSettings(self):
        self.settings.setValue("pos", self.pos())
        self.settings.setValue("size", self.size())

    def msgbox(self, title, message):
        QMessageBox.warning(self, title, message)

    def infobox(self, title, message):
        QMessageBox(QMessageBox.Information, title, message, QMessageBox.NoButton, self,
                    Qt.Dialog | Qt.NoDropShadowWindowHint).show()

    def handlePrint(self):
        if self.editor.toPlainText() == "":
            self.lineLabel1.setText("no text")
        else:
            dialog = QtPrintSupport.QPrintDialog()
            if dialog.exec_() == QDialog.Accepted:
                self.handlePaintRequest(dialog.printer())
                self.lineLabel1.setText("Document printed")

    def handlePrintPreview(self):
        if self.editor.toPlainText() == "":
            self.lineLabel1.setText("no text")
        else:
            dialog = QtPrintSupport.QPrintPreviewDialog()
            dialog.setFixedSize(900, 650)
            dialog.paintRequested.connect(self.handlePaintRequest)
            dialog.exec_()
            self.lineLabel1.setText("Print Preview closed")

    def handlePaintRequest(self, printer):
        printer.setDocName(self.filename)
        document = self.editor.document()
        document.print_(printer)

    def modelFromFile(self, fileName):
        f = QFile(fileName)
        if not f.open(QFile.ReadOnly):
            return QStringListModel(self.completer)

        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

        #        self.words = self.words ###[]
        while not f.atEnd():
            line = f.readLine().trimmed()
            if line.length() != 0:
                try:
                    line = str(line, encoding='ascii')
                except TypeError:
                    line = str(line)

                self.words.append(line)
        QApplication.restoreOverrideCursor()
        return QStringListModel(self.words, self.completer)

    def resize_ui(self):
        # to show window at the middle of the screen and resize it to the screen size
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        ratio = float(self.comboBox.currentText())
        width = int(QDesktopWidget().availableGeometry().width() * ratio)
        height = int(QDesktopWidget().availableGeometry().height() * ratio)
        self.setMaximumWidth(width)
        self.setMaximumHeight(height)
    #######################################################################################
    #######################################################################################
    #######################################################################################
    #######################################################################################

version = '1.2'
qapp = QApplication(sys.argv)  
app  = Application(u'ERSN-OpenMC-Py')
qapp.setStyleSheet("QPushButton { background-color: palegoldenrod; border-width: 2px; border-color: darkkhaki}"
                   #"QPushButton { border-style: solid; border-radius: 5; padding: 3px; min-width: 9ex; min-height: 2.5ex;}"
                   "QLabel, QAbstractButton { font: bold; font-size: 11px }"
                   "QStatusBar QLabel { font: normal }"
                   "QStatusBar::item { border-width: 1; border-color: darkkhaki; border-style: solid; border-radius: 2;}"
                   "QComboBox, QLineEdit, QSpinBox, QTextEdit, QListView { background-color: cornsilk; selection - color: #0a214c}"
                   "QComboBox, QLineEdit, QSpinBox, QTextEdit, QListView { selection-background-color:  #C19A6B;}"
                   "QLineEdit, QFrame { border-width: 1px; border-style: solid; border-color: darkkhaki; border-radius: 5px}"
                   "QLabel { border: none; padding: 0; background: none; }"
                   "QPlainTextEdit {font-family: Monospace; font-size: 13px; background:  #E2E2E2; color:  #202020; border: 1px solid #1EAE3D;}")
app.setWindowTitle('ERSN-OpenMC-Py version ' + version)
app.show()
qapp.exec_()


