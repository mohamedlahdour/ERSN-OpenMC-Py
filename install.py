import os
import sys
import datetime
import shutil
import subprocess
from pathlib import Path
from PyQt5 import QtCore, QtWidgets
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QFont, QTextOption
from src.PyEdit import TextEdit, NumberBar  

# The new Stream Object which replaces the default stream associated with sys.stdout
# This object just puts data in a queue!

class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)
    def write(self, text):
        self.textWritten.emit(str(text))
        pass

    def flush(self):
        pass

class InstallOpenMC(QtWidgets.QMainWindow):
    from src.func import resize_ui
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("src/ui/GUI_Install.ui", self)

        # add new editor
        self.receiveArea = TextEdit()
        self.receiveArea.setWordWrapMode(QTextOption.NoWrap)
        self.numbers = NumberBar(self.receiveArea)
        layoutH = QHBoxLayout()
        #layoutH.setSpacing(1.5)
        layoutH.addWidget(self.numbers)
        layoutH.addWidget(self.receiveArea)
        self.EditorLayout.addLayout(layoutH, 0, 0)

        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        #sys.stderr = EmittingStream(textWritten=self.normalOutputWritten)
        self.initUI()
        self.resize_ui()

    def initUI(self):
        # QProcess object for external app
        self.process = QtCore.QProcess(self)
        self.process.setProcessChannelMode(1)                 # Unification des 2 sorties (normale + erreur) du QProcess
        self.process.readyRead.connect(self.dataReady)        # QProcess emits `readyRead` when there is data to be read
        # =====================================================
        #                Initialization
        # =====================================================
        self.menu_bar()
        self.define_pB()
        self.tab_install.currentChanged.connect(self.set_Options_to_default)
        self.tab_install.setCurrentIndex(0)
        self.set_Options_to_default()
        self.set_prerequis_Options_to_default()

    def dataReady(self):
        cursor = self.receiveArea.textCursor()
        cursor.movePosition(cursor.End)
        # Here we have to decode the QByteArray
        cursor.insertText(str(self.process.readAll().data().decode()))
        self.receiveArea.ensureCursorVisible()

    def normalOutputWritten(self, text):
        cursor = self.receiveArea.textCursor()
        cursor.insertText(text)

    def script_exec(self, cmd):
        global rc
        print(cmd)
        rc = 1
        if CANCEL_PROCESS is False:
            # run the process
            # `start` takes the exec and a list of arguments
            self.process.start(cmd, QtCore.QIODevice.ReadWrite)
            self.dataReady()

    def disable_enable_pB(self):
        # Just to prevent accidentally running multiple times
        # Disable the button when process starts, and enable it when it finishes
        tab_index = self.tab_install.currentIndex()
        if tab_index == 0:
            self.process.started.connect(lambda: self.pB_Start_conda.setEnabled(False))
            self.process.started.connect(lambda: self.pB_Refresh_conda.setEnabled(False))
            self.process.finished.connect(lambda: self.pB_Start_conda.setEnabled(True))
            self.process.finished.connect(lambda: self.pB_Refresh_conda.setEnabled(True))
        elif tab_index == 1:
            # Just to prevent accidentally running multiple times
            # Disable the button when process starts, and enable it when it finishes
            self.process.started.connect(lambda: self.pB_Start_prerequis.setEnabled(False))
            self.process.started.connect(lambda: self.pB_Refresh_prerequis.setEnabled(False))
            self.process.started.connect(lambda: self.tools_conda_lE.setEnabled(False))
            self.process.finished.connect(lambda: self.pB_Start_prerequis.setEnabled(True))
            self.process.finished.connect(lambda: self.pB_Refresh_prerequis.setEnabled(True))
            self.process.finished.connect(lambda: self.tools_conda_lE.setEnabled(True))
            self.process.finished.connect(lambda: self.tools_conda_lE.setText(''))
        elif tab_index == 2:
            self.process.started.connect(lambda: self.pB_Start.setEnabled(False))
            self.process.started.connect(lambda: self.pB_Refresh.setEnabled(False))
            self.process.finished.connect(lambda: self.pB_Start.setEnabled(True))
            self.process.finished.connect(lambda: self.pB_Refresh.setEnabled(True))
            self.process.started.connect(lambda: self.WORK_DIR.setEnabled(False))
            self.process.started.connect(lambda: self.pB_Browse.setEnabled(False))
            self.process.finished.connect(lambda: self.WORK_DIR.setEnabled(True))
            self.process.finished.connect(lambda: self.pB_Browse.setEnabled(True))
        elif tab_index == 3:
            self.process.started.connect(lambda: self.pB_Refresh_XS.setEnabled(False))
            self.process.started.connect(lambda: self.pB_Browse_XS.setEnabled(False))
            self.process.finished.connect(lambda: self.pB_Refresh_XS.setEnabled(True))
            self.process.finished.connect(lambda: self.pB_Browse_XS.setEnabled(True))
            self.process.started.connect(lambda: self.pB_get_XS_H5.setEnabled(False))
            self.process.started.connect(lambda: self.pB_get_XS_ACE.setEnabled(False))
            self.process.finished.connect(lambda: self.pB_get_XS_H5.setEnabled(True))
            self.process.finished.connect(lambda: self.pB_get_XS_ACE.setEnabled(True))
            self.process.started.connect(lambda: self.pB_get_depl_chain.setEnabled(False))
            self.process.finished.connect(lambda: self.pB_get_depl_chain.setEnabled(True))
            self.process.started.connect(lambda: self.pB_get_build_NJOY.setEnabled(False))
            self.process.finished.connect(lambda: self.pB_get_build_NJOY.setEnabled(True))
            self.process.started.connect(lambda: self.pB_get_endf_file.setEnabled(False))
            self.process.finished.connect(lambda: self.pB_get_endf_file.setEnabled(True))
        # pB common to tabs
        self.process.started.connect(lambda: self.pB_Clear_Text.setEnabled(False))
        self.process.finished.connect(lambda: self.pB_Clear_Text.setEnabled(True))

    def uncheck_rB(self):
        self.buttonGroup.setExclusive(False)
        self.rB_py37.setChecked(False)
        self.rB_py39.setChecked(False)
        self.rB_py311.setChecked(False)
        self.buttonGroup.setExclusive(True)

    def define_pB(self):
        # Define pressButtons of Install Miniconda tab
        self.pB_Start_conda.clicked.connect(self.install_miniconda)
        self.pB_Refresh_conda.clicked.connect(self.set_Options_to_default)
        self.pB_Cancel_conda.clicked.connect(self.kill_process)
        self.pB_Start_conda.setStatusTip("Will install miniconda3")
        self.pB_Refresh_conda.setStatusTip("Will set options to default")
        self.pB_Cancel_conda.setStatusTip("Will kill process !")
        # Define pressButtons of Install OpenMC tab
        self.pB_Start.clicked.connect(self.Proc_Start)
        self.pB_Browse.clicked.connect(lambda: self.get_working_directory(self.WORK_DIR))
        self.pB_Refresh.clicked.connect(self.set_Options_to_default)
        self.pB_Cancel.clicked.connect(self.kill_process)
        self.pB_Start.setStatusTip("Will clone OpenMC and build binaries")
        self.pB_Refresh.setStatusTip("Will set options to default")
        self.pB_Cancel.setStatusTip("Will kill process !")
        # Define pressButtons of Install prerequisites tab
        self.pB_Start_prerequis.clicked.connect(self.Proc_Start)
        self.pB_Cancel_prerequis.clicked.connect(self.kill_process)
        self.pB_extra_tools.clicked.connect(self.install_extra_tools)
        self.pB_Refresh_prerequis.clicked.connect(self.set_prerequis_Options_to_default)
        self.pB_Start_prerequis.setStatusTip("Will download and install prerequisites")
        self.pB_Refresh_prerequis.setStatusTip("Will set options to default")
        self.pB_extra_tools.setStatusTip("Will download and install additional tools")
        self.pB_Cancel_prerequis.setStatusTip("Will kill process !")
        # Define pressButtons of XS download
        self.pB_Browse_XS.clicked.connect(lambda: self.get_working_directory(self.WORKDIR_XS))
        self.pB_get_XS_H5.clicked.connect(lambda: self.get_XS_data('H5_Lib'))
        self.pB_get_XS_ACE.clicked.connect(lambda: self.get_XS_data('ACE_Lib'))
        self.pB_get_depl_chain.clicked.connect(lambda: self.get_XS_data('Depletion_Chain'))
        self.pB_get_endf_file.clicked.connect(lambda: self.get_XS_data('ENDF_FILE'))
        self.pB_get_build_NJOY.clicked.connect(self.get_NJOY_build)
        self.pB_Cancel_XS.clicked.connect(self.kill_process)
        self.pB_Refresh_XS.clicked.connect(self.set_Options_to_default)
        # common button
        self.pB_Clear_Text.clicked.connect(self.clear_text)
        self.pB_exit.clicked.connect(self.ExitInstall)
        self.pB_Clear_Text.setStatusTip("Will clear the text area !")
        self.pB_exit.setStatusTip("Will close the GUI !")

    def menu_bar(self):
        # define menu bar actions
        # File menu
        self.actionOpen.triggered.connect(self.OpenFiles)
        self.actionOpen.setShortcut("Ctrl+O")
        self.actionSave_as.triggered.connect(self.SaveAsFiles)
        self.actionSave.triggered.connect(self.SaveFiles)
        self.actionSave.setShortcut("Ctrl+S")
        self.actionClose.triggered.connect(self.CloseFile)
        self.actionExit.triggered.connect(self.ExitInstall)
        self.actionExit.setShortcut("Ctrl+X")
        # Edit menu
        self.actionUndo.triggered.connect(self.receiveArea.undo)
        self.actionRedo.triggered.connect(self.receiveArea.redo)
        self.actionCut.triggered.connect(self.receiveArea.cut)
        self.actionCopy.triggered.connect(self.receiveArea.copy)
        self.actionPaste.triggered.connect(self.receiveArea.paste)
        self.actionSelect_All.triggered.connect(self.receiveArea.selectAll)
        # get cursor position
        self.receiveArea.cursorPositionChanged.connect(self.CursorPosition)

    def get_XS_data(self, library):
        global WORK_DIR_XS, XS_H5_Library, XS_ACE_Library, DEPLETION_CHAIN_DATA, XS_ENDF_FILE
        # this must be done *after* re-setting the view
        self.disable_enable_pB()
        WORK_DIR_XS = self.WORKDIR_XS.text()        # Workdir where data will be put
        ENVNAME = self.Env_Name_XS.text()            # get environment name
        # get data available for the simulation and depletion calculation
        # library = 'H5_Lib'
        # =============================   H5   FILES   ==========================
        if library == 'H5_Lib':                     # download XS in h5 format
            XS_H5_Lib = self.XS_Eval_H5_cB.currentText()
            # Official data of OpenMC
            if 'NNDC official' in XS_H5_Lib:
                XS_H5_Library = 'NNDC'
            elif 'ENDF-B/VIII.0 official' in XS_H5_Lib:
                XS_H5_Library = 'ENDF-B/VIII.0'
            elif 'ENDF-B/VII.1 official' in XS_H5_Lib:
                XS_H5_Library = 'ENDF-B/VII.1'
            elif 'JEFF-3.3 official' in XS_H5_Lib:
                XS_H5_Library = 'JEFF-3.3'
            # MCNP ACE data converted to h5 files
            elif 'MCNP_ENDF-B/VIII.0' in XS_H5_Lib:
                XS_H5_Library = 'MCNP_ENDF-B/VIII.0'
            elif 'MCNP_ENDF-B/VII.1' in XS_H5_Lib:
                XS_H5_Library = 'MCNP_ENDF-B/VII.1'
            elif 'MCNP_ENDF-B/VII.0' in XS_H5_Lib:
                XS_H5_Library = 'MCNP_ENDF-B/VII.0'
            elif 'ACE2H5_JEFF-3.3' in XS_H5_Lib:
                XS_H5_Library = 'ACE2H5_JEFF-3.3'
            elif 'ACE2H5_JEFF-3.2' in XS_H5_Lib:
                XS_H5_Library = 'ACE2H5_JEFF-3.2'
            XS_ACE_Library = 'none'
            DEPLETION_CHAIN_DATA = 'none'
            XS_ENDF_FILE = 'none'
        # =============================   ACE  FILES   ==========================
        elif library == 'ACE_Lib':                  # download XS in ACE format
            XS_ACE_Library = self.XS_eval_ACE_cB.currentText()
            if 'ENDF-B/VII.1 T=293.6K' in XS_ACE_Library:
                XS_ACE_Library = 'ACE-ENDF-B/VII.1_293K'
            if 'ENDF-B/VII.1 T=300K' in XS_ACE_Library:
                XS_ACE_Library = 'ACE-ENDF-B/VII.1_300K'
            elif 'ENDF-B/VIII.0' in XS_ACE_Library:
                XS_ACE_Library = 'ACE-ENDF-B/VIII.0'
            elif 'JEFF-3.3 T=293K' in XS_ACE_Library:
                XS_ACE_Library = 'ACE-JEFF-3.3_293K'
            elif 'JEFF-3.3 T=600K' in XS_ACE_Library:
                XS_ACE_Library = 'ACE-JEFF-3.3_600K'
            elif 'JEFF-3.3 T=900K' in XS_ACE_Library:
                XS_ACE_Library = 'ACE-JEFF-3.3_900K'
            elif 'JEFF-3.3 T=1200K' in XS_ACE_Library:
                XS_ACE_Library = 'ACE-JEFF-3.3_1200K'
            elif 'JEFF-3.3 T=1500K' in XS_ACE_Library:
                XS_ACE_Library = 'ACE-JEFF-3.3_1500K'
            elif 'JEFF-3.3 T=1800K' in XS_ACE_Library:
                XS_ACE_Library = 'ACE-JEFF-3.3_1800K'
            elif 'JEFF-3.3 TSL' in XS_ACE_Library:
                XS_ACE_Library = 'ACE-JEFF-3.3_TSL'

            XS_H5_Library = 'none'
            XS_ENDF_FILE = 'none'
            DEPLETION_CHAIN_DATA = 'none'
        # ==========================   DEPLETION  FILES   =======================
        elif library == 'Depletion_Chain':
            DEPLETION_CHAIN_DATA = self.depletion_chain_cB.currentText()
            if DEPLETION_CHAIN_DATA == 'ENDF-B/VII.1 PWR spectrum v0.11':
                DEPLETION_CHAIN_DATA = 'ENDF-BVII.1_PWR_spectrum_v0.11'
            elif DEPLETION_CHAIN_DATA == 'ENDF-B/VII.1 PWR spectrum v0.12':
                DEPLETION_CHAIN_DATA = 'ENDF-BVII.1_PWR_spectrum_v0.12'
            elif DEPLETION_CHAIN_DATA == 'ENDF-B/VII.1 fast spectrum v0.11':
                DEPLETION_CHAIN_DATA = 'ENDF-BVII.1_fast_spectrum_v0.11'
            elif DEPLETION_CHAIN_DATA == 'ENDF-B/VII.1 fast spectrum v0.12':
                DEPLETION_CHAIN_DATA = 'ENDF-BVII.1_fast_spectrum_v0.12'
            elif DEPLETION_CHAIN_DATA == 'Simplified chain PWR spectrum v0.11':
                DEPLETION_CHAIN_DATA = 'Simplified_chain_PWR_spectrum_v0.11'
            elif DEPLETION_CHAIN_DATA == 'Simplified chain PWR spectrum v0.12':
                DEPLETION_CHAIN_DATA = 'Simplified_chain_PWR_spectrum_v0.12'
            elif DEPLETION_CHAIN_DATA == 'Simplified chain fast spectrum v0.11':
                DEPLETION_CHAIN_DATA = 'Simplified_chain_fast_spectrum_v0.11'
            elif DEPLETION_CHAIN_DATA == 'Simplified chain fast spectrum v0.12':
                DEPLETION_CHAIN_DATA = 'Simplified_chain_fast_spectrum_v0.12'
            XS_H5_Library = 'none'
            XS_ACE_Library = 'none'
            XS_ENDF_FILE = 'none'
        # =============================   ENDF FILES   ==========================
        elif library == 'ENDF_FILE':
            XS_ENDF_FILE = self.get_ENDF_FILE_cB.currentText()
            XS_H5_Library = 'none'
            XS_ACE_Library = 'none'
            DEPLETION_CHAIN_DATA = 'none'

        # restore text editor default options
        self.receiveArea.setStyleSheet("")

        # Options of installation
        OPTIONS_LIST = [WORK_DIR_XS, XS_H5_Library, XS_ACE_Library, DEPLETION_CHAIN_DATA, XS_ENDF_FILE, ENVNAME]
        OPTIONS = ' '
        OPTIONS = OPTIONS.join(OPTIONS_LIST)
        self.print_lines("will download cross sections or depletion chain data !")
        self.script_exec('bash bash_scripts/get_cross_sections.sh ' + OPTIONS)

    def get_NJOY_build(self):
        # restore text editor default options
        self.receiveArea.setStyleSheet("")
        # download and build NJOY2016 or NJOY21
        WORK_DIR_XS = self.WORKDIR_XS.text()        # Workdir wher data will be put
        NJOY_RELEASE = self.get_NJOY_cB.currentText()
        self.script_exec('bash bash_scripts/get_njoy21.sh ' + WORK_DIR_XS + ' ' + NJOY_RELEASE)

    def install_extra_tools(self):
        # restore text editor default options
        self.receiveArea.setStyleSheet("")
        CONDA = subprocess.run(['which', 'conda'], stdout=subprocess.PIPE, text=True)
        CONDA = CONDA.stdout.rstrip('\n')
        # CONDA = script_exec('which conda')
        cmd = self.tools_conda_lE.text().replace('Installing ','')
        if "miniconda3" in CONDA:
            self.showDialog('conda info', '         miniconda3 found       ')
            if cmd == '':
                self.print_lines('Nothing done !')
            else:
                self.print_lines('installing  ' + cmd + '   under Miniconda')
                self.script_exec(CONDA + ' install -y ' + cmd)
        else:
            self.print_lines("can't continue without miniconda3 installed !")
            self.showDialog('conda warning', '   miniconda3 not found, Install miniconda3 first !  ')
            self.print_lines('miniconda3 not found, Install miniconda3 first !')
            self.tools_conda_lE.setText('Installing ' + cmd)

    def set_prerequis_Options_to_default(self):
        # set radioButtons to default
        self.rB_yes_all_prerequis.setChecked(True)
        self.rB_no_MPI_prerequis.setChecked(True)
        self.rB_no_compiler.setChecked(True)
        self.rB_no_cmake.setChecked(True)
        self.tools_conda_lE.setText(None)
        self.pB_extra_tools.setDisabled(True)
        self.Paraview_cB.setChecked(False)
        self.Mayavi_cB.setChecked(False)
        # The toggled() signal of both the buttons is connected to update_compiler() function.
        # Use of lambda allows the source of signal to be passed to the function as an argument.
        #self.rB_yes_compiler.toggled.connect(self.pB_Start_prerequis.setDisabled)
        #self.rB_yes_cmake.toggled.connect(self.pB_Start_prerequis.setDisabled)
        #self.rB_yes_compiler.toggled.connect(lambda: self.update_compiler(self.rB_yes_compiler, gcc))
        #self.rB_yes_cmake.toggled.connect(lambda: self.update_compiler(self.rB_yes_cmake, cmake))

        self.tools_conda_lE.textChanged[str].connect(lambda: self.pB_extra_tools.setDisabled(self.tools_conda_lE.text() == ""))

    def set_Options_to_default(self):
        global CONDA_MD5_IN
        tab_index = self.tab_install.currentIndex()
        if tab_index == 0:                     # miniconda tab
            # set radioButtons to default
            self.rB_no_conda.setChecked(True)
            self.rB_yes_update_conda.setChecked(True)
            self.rB_no_checksum.setChecked(True)
            self.rB_CONDA_URL.setChecked(True)
            # set MD5 to its default value
            self.lineEdit_SHA256.setText(CONDA_MD5_IN)
        elif tab_index == 1:               # prerequisites tab
            # set radioButtons to default
            self.rB_yes_update_env_prerequis.setChecked(True)
            ENV_NAME_PREFIX = 'openmc-py'
            self.lineEdit_Env_Name_prerequis.setText(ENV_NAME_PREFIX)
            self.rB_py37_prerequis.toggled.connect(lambda: self.PyVer_btnstate(self.rB_py37_prerequis, ENV_NAME_PREFIX, self.lineEdit_Env_Name_prerequis))
            self.rB_py39_prerequis.toggled.connect(lambda: self.PyVer_btnstate(self.rB_py39_prerequis, ENV_NAME_PREFIX, self.lineEdit_Env_Name_prerequis))
            self.rB_py311_prerequis.toggled.connect(lambda: self.PyVer_btnstate(self.rB_py311_prerequis, ENV_NAME_PREFIX, self.lineEdit_Env_Name_prerequis))
            self.rB_yes_all_prerequis.setChecked(True)
            self.rB_py37_prerequis.setChecked(True)
            self.rB_no_MPI_prerequis.setChecked(True)
            self.rB_no_compiler.setChecked(True)
            self.rB_no_cmake.setChecked(True)
            self.tools_conda_lE.setText(None)
            self.pB_extra_tools.setDisabled(True)
            self.Paraview_cB.setChecked(False)
            self.Mayavi_cB.setChecked(False)
            self.Paraview_cB.toggled.connect(self.Visualisation_Tools)
            self.Mayavi_cB.toggled.connect(self.Visualisation_Tools)

            # The toggled() signal of both the buttons is connected to update_compiler() function.
            # Use of lambda allows the source of signal to be passed to the function as an argument.
            self.rB_yes_compiler.toggled.connect(self.pB_Start_prerequis.setDisabled)
            self.rB_yes_cmake.toggled.connect(self.pB_Start_prerequis.setDisabled)
            self.rB_yes_compiler.toggled.connect(lambda: self.update_compiler(self.rB_yes_compiler, gcc))
            self.rB_yes_cmake.toggled.connect(lambda: self.update_compiler(self.rB_yes_cmake, cmake))
            # will activate run button if text changed
            self.tools_conda_lE.textChanged[str].connect(lambda: self.pB_extra_tools.setDisabled(self.tools_conda_lE.text() == ""))
        elif tab_index == 2:               # openmc tab
            # set radioButtons to default
            self.rB_yes_in_conda.setChecked(True)
            self.rB_no_update_env.setChecked(True)
            self.rB_no_prerequis.setChecked(True)
            self.rB_no_Editable.setChecked(True)
            self.rB_no_MPI.setChecked(True)
            self.rB_no_del_src.setChecked(True)
            self.uncheck_rB()
            # Env. Name
            ENV_NAME_PREFIX = 'openmc-py'
            self.rB_py37.setChecked(True)
            self.lineEdit_Env_Name.setText(ENV_NAME_PREFIX + PYTHON_VERSION)
            self.rB_py37.toggled.connect(lambda: self.PyVer_btnstate(self.rB_py37, ENV_NAME_PREFIX, self.lineEdit_Env_Name))
            self.rB_py39.toggled.connect(lambda: self.PyVer_btnstate(self.rB_py39, ENV_NAME_PREFIX, self.lineEdit_Env_Name))
            self.rB_py311.toggled.connect(lambda: self.PyVer_btnstate(self.rB_py311, ENV_NAME_PREFIX, self.lineEdit_Env_Name))
            # Working Directory and Install Prefix
            self.WORK_DIR.setText(QDir.homePath() + "/Py-OpenMC-" + str(datetime.date.today().year))
            self.INSTALL_PREFIX_QLnE.setText(self.WORK_DIR.text() + "/opt/openmc/"+datetime.date.today().strftime("%m-%Y"))  # Where to install (if INSTALL_IN_CONDA and INSTALL_EDITABLE are disabled)
            self.INSTALL_PREFIX_QLnE.setDisabled(True)
            self.rB_yes_in_conda.toggled.connect(self.INSTALL_PREFIX_QLnE.setDisabled)
        elif tab_index == 3:
            self.WORKDIR_XS.setText(QDir.homePath() + "/Py-OpenMC-" + str(datetime.date.today().year))
            self.Env_Name_XS.setText("openmc-py3.7")

    def enable_pB(self):
        self.pB_Refresh.setEnabled(True)
        self.pB_Start.setEnabled(True)
        self.pB_Clear_Text.setEnabled(True)
        self.pB_Clear_Text.setEnabled(True)

    def update_compiler(self, rB, app):
        # this function checks state of radio button emitting toggled() signal.
        if rB.isChecked():
            app = self.tools_conda_lE.text() + ' ' + app
            self.tools_conda_lE.setText(app)
        else:
            # self.tools_conda_lE.setText('')
            s = self.tools_conda_lE.text()
            your_list = s.split()
            i = 0
            if 'compiler' in rB.objectName() :
                pat = 'g'
            elif 'cmake' in rB.objectName():
                pat = 'cmak'
            while i < len(your_list):
                if your_list[i].startswith(pat):
                    del your_list[i]
                else:
                    i += 1
            app = ' '.join(your_list)
            self.tools_conda_lE.setText(app)

    def Visualisation_Tools(self):
        cmd = ''
        if self.Paraview_cB.isChecked():
            cmd = ' -c conda-forge paraview '
            self.Mayavi_cB.setChecked(False)
        elif self.Mayavi_cB.isChecked():
            cmd = ' -c conda-forge mayavi '
            self.Paraview_cB.setChecked(False)
        self.tools_conda_lE.setText(cmd)

    def Proc_Start(self):
        global INSTALL_MINICONDA, UPDATE_CONDA, INSTALL_PYQT, INSTALL_PREREQUISITES, DOWNLOAD_OPENMC, OPENMC_DIR #, WITH_MPI, INSTALL_OPENMC    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        tab_index = self.tab_install.currentIndex()
        # restore text editor default options
        self.receiveArea.setStyleSheet("")
        self.disable_enable_pB()
        INSTALL_MINICONDA = "no"
        UPDATE_CONDA = "no"
        INSTALL_PYQT = "no"
        DOWNLOAD_MINICONDA = "no"
        if tab_index == 2:      # if tab2 is selected switch to openmc installation
            INSTALL_PREREQUISITES = 'no'
            INSTALL_OPENMC = 'yes'
            self.update_openmc_options()    # update of OpenMC installation options
            if rc != 0:
                self.print_lines("can't continue without checking python version !")
                self.enable_pB()
                return
        elif tab_index == 1:    # if tab1 is selected switch to prerequisites installation
            INSTALL_OPENMC = 'no'
            INSTALL_PREREQUISITES = 'yes'
            self.update_prerequis_options()    # update of prerequisites installation options
            if rc != 0:
                self.print_lines("can't continue without checking python version !")
                self.enable_pB()
                return

        # look if miniconda3 is installed
        CONDA = subprocess.run(['which', 'conda'], stdout=subprocess.PIPE, text=True)
        CONDA = CONDA.stdout.rstrip('\n')
        if "miniconda3" in CONDA:
            self.showDialog('conda info', '         miniconda3 found       ')
            self.print_lines('miniconda3 found ')
            CONDA_DIR = str(CONDA.replace('/bin/conda', ''))
        else:                 # suggest to install miniconda
            self.showDialog('conda warning', 'miniconda3 not found, Install miniconda3 first ! \nIf it has been just installed you need to close shell and open it !')
            self.print_lines('miniconda3 not found, Install miniconda3 first !')
            self.print_lines(' IMPORTANTE: For changes to take effect, close and re-open your current shell and the GUI ! ')
            return

        if "miniconda3" in CONDA:
            if tab_index == 2:
                self.make_dir(WORK_DIR)                          # create WORK_DIR if doesn't exist
                if OPENMC_RELEASE == 'latest':
                    subdir = '/openmc'
                else:
                    subdir = OPENMC_RELEASE.replace('v', '/openmc-')
                OPENMC_DIR = WORK_DIR + subdir
                self.look_if_dir_exists(OPENMC_DIR)    # look if WORK_DIR/openmc exists
                self.enable_pB()
                if DOWNLOAD_OPENMC == 'yes':
                    self.print_lines('will download fresh ' + OPENMC_RELEASE + ' release of openmc ! ')
                elif DOWNLOAD_OPENMC == 'no':
                    self.print_lines('will use the existing openmc directory on your computer at your own risk ! ')
                else:
                    self.print_lines('OpenMC installation is canceled ! ')
                    return
            # Options of installation
            OPTIONS_LIST = [INSTALL_MINICONDA, DOWNLOAD_MINICONDA, "none", "none", "none", UPDATE_CONDA,
                            "none", INSTALL_PREREQUISITES, WITH_MPI, INSTALL_IN_CONDA, INSTALL_EDITABLE,
                            DELETE_SOURCES, UPDATE_ENV, PYTHON_VERSION, ENV_NAME, WORK_DIR,
                            INSTALL_PREFIX, CONDA, CONDA_DIR, INSTALL_OPENMC, OPENMC_RELEASE, DOWNLOAD_OPENMC,
                            OPENMC_DIR, INSTALL_PYQT]
            OPTIONS = ' '
            OPTIONS = OPTIONS.join(OPTIONS_LIST)
            self.print_lines("will install openmc and/or the preriquisites")
            self.script_exec('bash bash_scripts/openmc-conda-install.sh ' + OPTIONS)
        else:
            self.print_lines("can't continue without miniconda3 installed !")
            return

    def update_prerequis_options(self):
        global INSTALL_MINICONDA, UPDATE_CONDA, ENV_NAME, UPDATE_ENV, INSTALL_PREREQUISITES, WITH_MPI, INSTALL_OPENMC, rc
        INSTALL_MINICONDA = 'no'
        UPDATE_CONDA = 'no'
        INSTALL_OPENMC = 'no'
        self.Test_If_rB_Checked(self.Python_Version_gB_prerequis, self.rB_py37_prerequis, self.rB_py39_prerequis, self.rB_py311_prerequis)
        ENV_NAME = self.lineEdit_Env_Name_prerequis.text()
        if self.rB_yes_update_env_prerequis.isChecked():
            UPDATE_ENV = 'yes'
        else:
            UPDATE_ENV = 'no'
        if self.rB_yes_all_prerequis.isChecked():
            INSTALL_PREREQUISITES = 'yes'
        else:
            INSTALL_PREREQUISITES = 'no'
        if self.rB_yes_MPI_prerequis.isChecked():
            WITH_MPI = 'yes'
        else:
            WITH_MPI = 'no'

    def del_scripts(self, file_name):
        import glob
        file_list = glob.glob(file_name)
        files = ' '
        files = files.join(file_list)
        self.question1('Verify', 'Really delete ' + file_name + '?', 'rm -f' + files)

    def look_for_script(self, script_str):
        import glob
        global rc, SH_SCRIPT, DOWNLOAD_MINICONDA
        self.del_logfiles()
        CONDA_MD5 = self.lineEdit_SHA256.text()
        i_str_chk = 0
        rc = 1
        script_list = glob.glob(script_str + "*")
        if len(script_list) != 0:
            self.print_lines(str(len(script_list)) + "     install file(s) found")
            for SH_SCRIPT in script_list:
                if self.rB_yes_checksum.isChecked():
                    i_str_chk += 1
                    check_sum = subprocess.Popen(['sha256sum', SH_SCRIPT], stdout=subprocess.PIPE)
                    str_chk = str(check_sum.stdout.read())
                    if CONDA_MD5 in str_chk:
                        self.print_lines(SH_SCRIPT + ' checksum succes; \n it will be installed')
                        DOWNLOAD_MINICONDA = 'no'
                        return SH_SCRIPT, DOWNLOAD_MINICONDA
                        #break
                    elif i_str_chk >= len(script_list):
                        self.print_lines(SH_SCRIPT + ' checksum fails; it will be downloaded and installed')
                        DOWNLOAD_MINICONDA = 'yes'
                        return DOWNLOAD_MINICONDA
                        #break
                else:
                    script_list = glob.glob(script_str + "*")
                    self.print_lines(str(len(script_list)) + " install file(s) found and the more recent will be installed !")
                    DOWNLOAD_MINICONDA = 'no'
                    if len(script_list) != 0:
                        SH_SCRIPT = max(script_list, key=os.path.getsize)
                        return SH_SCRIPT, DOWNLOAD_MINICONDA
        else:
            self.print_lines('Miniconda script will be downloaded !')
            DOWNLOAD_MINICONDA = 'yes'
            return DOWNLOAD_MINICONDA

    def del_logfiles(self):
        import glob
        log_list = glob.glob('wget-log*')
        if len(log_list) != 0:
            self.del_scripts("wget-log*")

    def install_miniconda(self):
        global SH_SCRIPT, CONDA_URL, INSTALL_MINICONDA, INSTALL_PYQT, CONDA_DIR
        # restore text editor default options
        self.receiveArea.setStyleSheet("")
        self.update_conda_options()
        self.disable_enable_pB()
        CONDA = subprocess.run(['which', 'conda'], stdout=subprocess.PIPE, text=True)
        CONDA = CONDA.stdout.rstrip('\n')
        # if self.rB_yes_conda.isChecked():
        if INSTALL_MINICONDA == 'yes':
            if "miniconda3" in CONDA:                             # look if miniconda3 is installed
                self.showDialog('conda info', '         miniconda3 found       ')
                self.print_lines("miniconda3 already installed")
                INSTALL_MINICONDA = 'no'
                if UPDATE_CONDA == 'yes':
                    self.print_lines("miniconda will be updated !")
                else:
                    self.print_lines("miniconda needs to be updated !")
            else:
                # check if $HOME/miniconda3 directory exists
                conda_path = str(Path.home()) + "/miniconda3"
                if os.path.isdir(conda_path):
                    if os.path.isfile(CONDA_DIR + '/condabin/conda'):
                        self.showDialog('conda warning', conda_path + 'It seems like if miniconda3 is already installed; check if it can be activated!')
                        return
                    else:
                        self.showDialog('conda warning', conda_path + '  directory already exists; delete or rename it before retrying!')
                        return
                else:
                    script_str = 'Miniconda3-latest'
                    self.print_lines("Checking if " + script_str + " script exists")
                    self.look_for_script(script_str)
                CONDA = CONDA_DIR + "/condabin/conda"
        else:
            if UPDATE_CONDA == 'yes':
                if "miniconda3" in CONDA:                             # look if miniconda3 is installed
                    self.print_lines("miniconda will be updated !")
                else:
                    self.print_lines("miniconda not installed and cannot be updated !")
                    return
            else:
                self.print_lines("Nothing will be done !")
                return

        if "miniconda3" in CONDA:
            # CONDA_DIR = str(CONDA.replace('/conda', ''))
            if os.path.isfile(CONDA_DIR + '/bin/qmake'):
                INSTALL_PYQT = 'no'
            else:
                INSTALL_PYQT = 'yes'

        if CANCEL_PROCESS is not True:
            # Options of installation
            NONE = 'no'
            OPTIONS_LIST = [INSTALL_MINICONDA, DOWNLOAD_MINICONDA, CHECKSUM, SH_SCRIPT, CONDA_MD5, UPDATE_CONDA,
                            CONDA_URL, NONE, WITH_MPI, NONE, NONE, NONE, NONE, NONE, NONE, NONE,
                            NONE, CONDA, CONDA_DIR, NONE, NONE, NONE, NONE, INSTALL_PYQT]
            OPTIONS = ' '
            OPTIONS = OPTIONS.join(OPTIONS_LIST)
            self.script_exec('bash bash_scripts/openmc-conda-install.sh ' + OPTIONS)

    def update_conda_options(self):
        global INSTALL_MINICONDA, UPDATE_CONDA, CHECKSUM, CONDA_MD5, CONDA_URL, SH_SCRIPT
        if self.rB_yes_conda.isChecked():
            INSTALL_MINICONDA = 'yes'
        else:
            INSTALL_MINICONDA = 'no'
        if self.rB_yes_update_conda.isChecked():
            UPDATE_CONDA = 'yes'
        else:
            UPDATE_CONDA = 'no'
        if self.rB_yes_checksum.isChecked():
            CHECKSUM = 'yes'
        else:
            CHECKSUM = 'no'
        CONDA_MD5 = self.lineEdit_SHA256.text()
        if self.rB_CONDA_URL.isChecked():
            CONDA_URL = url1
            SH_SCRIPT = 'Miniconda3-latest-Linux-x86_64.sh'
        elif self.rB_MIRROR_URL.isChecked():
            CONDA_URL = url2
            SH_SCRIPT = 'Miniconda3-py311_23.10.0-1-Linux-x86_64.sh'

    def update_openmc_options(self):
        # update of OpenMC installation options
        global ENV_NAME, UPDATE_ENV, INSTALL_IN_CONDA, INSTALL_PREREQUISITES, INSTALL_OPENMC,\
               INSTALL_EDITABLE, WITH_MPI, DELETE_SOURCES, WORK_DIR, INSTALL_PREFIX, OPENMC_RELEASE
        INSTALL_OPENMC = 'yes'
        self.Test_If_rB_Checked(self.Python_Version_gB, self.rB_py37, self.rB_py39, self.rB_py311)
        ENV_NAME = self.lineEdit_Env_Name.text()
        if self.rB_yes_update_env.isChecked():
            UPDATE_ENV = 'yes'
        else:
            UPDATE_ENV = 'no'
        if self.rB_yes_in_conda.isChecked():
            INSTALL_IN_CONDA = 'yes'
        else:
            INSTALL_IN_CONDA = 'no'
        if self.rB_yes_prerequis.isChecked():
            INSTALL_PREREQUISITES = 'yes'
        else:
            INSTALL_PREREQUISITES = 'no'
        if self.rB_yes_Editable.isChecked():
            INSTALL_EDITABLE = 'yes'
        else:
            INSTALL_EDITABLE = 'no'
        if self.rB_yes_MPI.isChecked():
            WITH_MPI = 'yes'
        else:
            WITH_MPI = 'no'
        if self.rB_yes_del_src.isChecked():
            DELETE_SOURCES = 'yes'
        else:
            DELETE_SOURCES = 'no'
        WORK_DIR = self.WORK_DIR.text()
        self.INSTALL_PREFIX_QLnE.setText(WORK_DIR + "/opt/openmc/"+datetime.date.today().strftime("%m-%Y"))
        INSTALL_PREFIX = self.INSTALL_PREFIX_QLnE.text()
        OPENMC_RELEASE = self.OpenMC_Release_cB.currentText()

    def print_lines(self, text):
        import textwrap
        rA_width = int(self.receiveArea.width() / 4)   # 5 could be changed
        print('#' * int(rA_width / 2.09))              # 2.04 to convert pixels to character
        lines = textwrap.wrap(text, fix_sentence_endings = True)
        print("\n".join(line.ljust(rA_width) for line in lines))
        print('#' * int(rA_width / 2.09))

    def Test_If_rB_Checked(self, gB, rB1, rB2, rB3):
        global rc
        if not rB1.isChecked() and not rB2.isChecked() and not rB3.isChecked():
            msg = 'Choose   ' + str(gB.title()) + '  !'
            self.showDialog('Warning', msg)
            rc = 1
        else:
            rc = 0

    def showDialog(self, alert, msg):
        font = QFont('Arial', 12)
        msgBox = QMessageBox()
        msgBox.setFont(font)
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText(msg)
        msgBox.setWindowTitle(alert)
        msgBox.exec()

    def PyVer_btnstate(self, rB, ENV_NAME_PREFIX, line_Edit):
        global ENV_NAME, PYTHON_VERSION
        if rB.isChecked() is True:
            PYTHON_VERSION = rB.text()
        ENV_NAME = ENV_NAME_PREFIX + PYTHON_VERSION
        line_Edit.setText(ENV_NAME)

    def get_working_directory(self, dir):
        directory = QFileDialog.getExistingDirectory(None, "Choose Directory", QDir.homePath(),
                                                     QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        dir.setText(directory)
        self.INSTALL_PREFIX_QLnE.setText(directory + "/opt/openmc/" + datetime.date.today().strftime("%m-%Y"))
        #return directory

    def get_INSTALL_PREFIX(self):                  # get text if modified
        self.dir.setText(self.QDir.homePath() + "/Py-OpenMC-" + str(datetime.date.today().year))

    def make_dir(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
        else:
            self.print_lines(directory + ' already exists and will be used !')

    def clear_text(self, text):
        if text != "\n":
            self.receiveArea.clear()
            self.setStatusTip("")
        # restore text editor default options
        self.receiveArea.setStyleSheet("")

    def look_if_dir_exists(self, dir1):
        global rc
        if os.path.exists(dir1):
            dir2 = dir1 + '/build'
            self.print_lines('Could not create ' + dir1 + ' !' + ' Delete it or change working directory !')
            self.question2('Warning', dir1 + ' already exists, delete it ?', lambda : shutil.rmtree(dir1), lambda : shutil.rmtree(dir2), dir1, dir2)

    def question1(self, alert, msg, cmd):
        global rc
        qm = QMessageBox
        ret = qm.question(self, alert, msg, qm.Yes | qm.No)
        if ret == qm.Yes:
            cmd()
            rc = 0

    def question2(self, alert, msg, cmd1, cmd2, dir1, dir2):
        global DOWNLOAD_OPENMC
        qm = QMessageBox
        ret = qm.question(self, alert, msg, qm.Yes | qm.No | qm.Cancel)
        if ret == qm.Yes:
            cmd1()
            DOWNLOAD_OPENMC = 'yes'
        elif ret == qm.No:
            if os.path.exists(dir2):
                cmd2()
            DOWNLOAD_OPENMC = 'no'
        else:
            DOWNLOAD_OPENMC = 'cancel'

    def kill_process(self):
        global CANCEL_PROCESS
        pid = self.process.pid()
        self.process.close()
        self.process.kill()
        CANCEL_PROCESS = False
        self.print_lines('process  '+ str(pid) + '   has been killed !')
        self.print_lines('Exit code :  '+ str(self.process.exitCode()))

    def ExitInstall(self):
        """Generate 'question' dialog on clicking 'X' button in title bar.
        Reimplement the closeEvent() event handler to include a 'Question'
        dialog with options on how to proceed - Save, Close, Cancel buttons
        """
        reply = QMessageBox.question(self, "Message",
                "Are you sure you want to quit ?", QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()
        else:
            pass

    # action called by file open action

    def OpenFiles(self):
        self.receiveArea.setStyleSheet("""QPlainTextEdit{
                                           font-family:'Consolas';
                                           color: #ccc;
                                           background-color: #2b2b2b;}""")
        # getting path and bool value
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "",
                  "All Files (*);;Python Files (*.py);;XML Files (*.xml);;Bash Scripts (*.sh);;Text Files (*.txt)")

        # if path is true
        if path:
            # try opening path
            try:
                with open(path, 'rU') as f:
                    # read the file
                    text = f.read()
            # if some error occured
            except Exception as e:
                # show error using critical method
                self.dialog_critical(str(e))
            # else
            else:
                # update path value
                self.path = path
                '''
                if self.path.split(".")[-1] == "py":
                    self.highlight = syntax.PythonHighlighter(self.receiveArea.document())
                elif self.path.split(".")[-1] == "xml":
                    self.receiveArea.setStyleSheet("")
                    self.highlight = syntax.XMLHighlighter(self.receiveArea.document())
                '''
                # update the text
                self.receiveArea.setPlainText(text)
                # update the title
                self.update_title()

    # action called by file save action
    def SaveFiles(self, text):
        # if there is no save path
        if self.path is None:
            # call save as method
            return self.SaveAsFiles()
        # else call save to path method
        if text == "\n":
            messageBox = QMessageBox()
            title = "File content deleted "
            message = "The content of this file has been deleted ! Save file ?"
            reply = messageBox.question(self, title, message, messageBox.Yes | messageBox.No)
            if reply == messageBox.Yes:
                self._save_to_path(self.path)
            else:
                pass
        else:
            self._save_to_path(self.path)

    # action called by save as action
    def SaveAsFiles(self):
        # opening path
        path, _ = QFileDialog.getSaveFileName(self, "Save file", "",
                             "All Files (*);;Python Files (*.py);;XML Files (*.xml);;Bash Scripts (*.sh);;Text Files (*.txt)")
        # if dialog is cancelled i.e no path is selected
        if not path:
            # return this method
            # i.e no action performed
            return
        # else call save to path method
        self._save_to_path(path)

    # save to path method
    def _save_to_path(self, path):
        # get the text
        text = self.receiveArea.toPlainText()
        # try catch block
        try:
            # opening file to write
            with open(path, 'w') as f:
                # write text in the file
                f.write(text)
        # if error occurs
        except Exception as e:
            # show error using critical
            self.dialog_critical(str(e))
        # else do this
        else:
            # change path
            self.path = path
            # update the title
            # self.update_title()

    def CloseFile(self, text):
        self.clear_text(text)
        self.path = ""
        self.receiveArea.setStyleSheet("")

    def update_title(self):
        # setting status bar message
        self.setStatusTip("%s - Editing" %(os.path.abspath(self.path) if self.path else "Untitled"))

    def CursorPosition(self):
        line = self.receiveArea.textCursor().blockNumber() + 1
        col = self.receiveArea.textCursor().columnNumber() + 1
        linecol = ("Line: "+str(line)+" | "+"Column: "+str(col))
        self.statusbar.showMessage(linecol)

    # creating dialog critical method to show errors
    def dialog_critical(self, s):
        # creating a QMessageBox object
        dlg = QMessageBox(self)
        # setting text to the dlg
        dlg.setText(s)
        # setting icon to it
        dlg.setIcon(QMessageBox.Critical)
        # showing it
        dlg.show()

# //////////////////////////////////////////////////////////////////////////////////////////////////////////
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# initialize openmc installation options
global INSTALL_PREREQUISITES, WITH_MPI, INSTALL_OPENMC, INSTALL_MINICONDA, DOWNLOAD_MINICONDA, UPDATE_CONDA,\
       CHECKSUM, CONDA_MD5_IN, SH_SCRIPT, CONDA_URL, CONDA_DIR
# tab_index = 0
# Miniconda3 MD5 and download url
INSTALL_MINICONDA = 'no'
DOWNLOAD_MINICONDA = 'no'
UPDATE_CONDA = 'no'
CHECKSUM = 'no'
INSTALL_PYQT = 'no'
SH_SCRIPT = 'Miniconda3-latest-Linux-x86_64.sh'
CONDA_MD5 = "c9ae82568e9665b1105117b4b1e499607d2a920f0aea6f94410e417a0eff1b9c"
CONDA_MD5_IN = CONDA_MD5
url1 = 'https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh'
url2 = 'https://repo.anaconda.com/miniconda/Miniconda3-py39_23.10.0-1-Linux-x86_64.sh'
CONDA_URL = url1
miniconda = QDir.homePath() + '/miniconda3/bin/conda'

cmd = ''
gcc = 'gcc_linux-64 gxx_linux-64'
cmake = 'cmake'

INSTALL_PREREQUISITES = 'no'
WITH_MPI = 'no'
INSTALL_IN_CONDA = 'yes'
INSTALL_EDITABLE = 'no'
DELETE_SOURCES = 'no'
UPDATE_ENV = 'no'
WORK_DIR = QDir.homePath()
WORK_DIR_XS = QDir.homePath()
PYTHON_VERSION = '3.7'
ENV_NAME = 'openmc-py'
INSTALL_PREFIX = QDir.homePath() + '/Py-OpenMC'
CONDA = 'conda'
CONDA_DIR = QDir.homePath() + '/miniconda3'
DOWNLOAD_OPENMC = 'yes'
INSTALL_OPENMC = 'no'
OPENMC_RELEASE = 'latest'
OPENMC_DIR = ''
CANCEL_PROCESS = False
line = '~' * 70


#  to be removed if called by gui.py
qapp = QApplication(sys.argv)
mainwindow = InstallOpenMC()
mainwindow.show()
sys.exit(qapp.exec_())