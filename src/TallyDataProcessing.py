import os
import sys
import os.path
import PyQt5
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDir, Qt
from PyQt5.QtWidgets import QMessageBox
import datetime
import shutil
import subprocess
from pathlib import Path
from PyQt5.QtGui import QFont, QTextCharFormat, QBrush
#from src.PyEdit import myEditor
from src.PyEdit import TextEdit, NumberBar, tab, lineHighlightColor

import numpy as np
import openmc
import matplotlib.pyplot as plt
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

iconsize = QSize(24, 24)
pd.set_option('display.max_rows', None)


class TallyDataProcessing(QtWidgets.QMainWindow):
    from src.func import resize_ui, showDialog
    #def __init__(self, shellwin, parent=None):
    def __init__(self, parent=None):
        super(TallyDataProcessing, self).__init__(parent)
        uic.loadUi("src/ui/TallyDataProcessing.ui", self)
        #self._initButtons()
        #self.shellwin = shellwin
        self.sp_file = None
        self.Tallies = {}
        self.Bins_tuple = []
        self.Mesh_xy_RB.hide()
        self.Mesh_xz_RB.hide()
        self.Mesh_yz_RB.hide()
        self.spinBox.hide()
        self.spinBox_2.hide()
        self.buttons = [self.xLog_CB, self.yLog_CB, self.label_6, self.label_7, self.Graph_type_CB, self.row_SB, self.col_SB, self.Add_error_bars_CB, self.xGrid_CB, self.yGrid_CB, self.MinorGrid_CB]
        for elm in self.buttons: 
            elm.setEnabled(False)
        self.Graph_Layout_CB.setEnabled(False)
        self.set_Graph_stack()
        
        # add new editor for output window
        self.editor = TextEdit()
        self.numbers = NumberBar(self.editor)
        layoutH8 = QHBoxLayout()
        layoutH8.addWidget(self.numbers)
        layoutH8.addWidget(self.editor)
        self.gridLayout_18.addLayout(layoutH8, 0, 0)
        #self.highlighter = Highlighter(self.editor.document())

        self.grid = False
        self.which_axis = 'none'
        self.which_grid = 'both'
        self.resize_ui()

        # +++++++++++++++++++++++
        self.Tally_name_LE.setPlaceholderText("Name")
        self.root = QFileInfo.path(QFileInfo(QCoreApplication.arguments()[0]))
        self.openPath = ""
        self.dirpath = QDir.homePath() + "/Documents/python_files/"
        self.filename = ""
        self.MaxRecentFiles = 15
        self.recentFileActs = []
        self.settings = QSettings("PyEdit", "PyEdit")
        self.createActions()
        # +++++++++++++++++++++++

        # four lines to be removed
        self.sp_file = str(Path.home()) + '/My_Projects/Project-ERSN-OpenMC/Gui_orig/prof/statepoint.10.h5'
        if not os.path.isfile(self.sp_file):
            #self.Get_SP_File()
            self.sp_file = None
        self.lineEdit.setText(self.sp_file)
        self.Get_data_from_SP_file()

        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        #sys.stderr = EmittingStream(textWritten=self.normalOutputWritten)

        self._initButtons()

    def _initButtons(self):
        self.browse_PB.clicked.connect(self.Get_SP_File)
        self.get_tally_info_PB.clicked.connect(self.Get_Tally_Inf)
        self.tally_display_PB.clicked.connect(self.Display_tally)
        self.filters_display_PB.clicked.connect(self.Display_filters)
        self.nuclides_display_PB.clicked.connect(self.Clear_nuclides)
        self.Tally_id_comboBox.currentIndexChanged.connect(self.SelectTally)
        self.Filters_comboBox.currentIndexChanged.connect(self.SelectFilter)
        self.Nuclides_comboBox.currentIndexChanged.connect(self.SelectNuclides)
        self.Scores_comboBox.currentIndexChanged.connect(self.SelectScores)
        self.scores_display_PB.clicked.connect(self.Display_scores)
        self.Mesh_xy_RB.toggled.connect(self.Mesh_settings)
        self.Mesh_xz_RB.toggled.connect(self.Mesh_settings)
        self.Mesh_yz_RB.toggled.connect(self.Mesh_settings)
        self.Graph_Layout_CB.currentIndexChanged.connect(self.set_Graph_stack)
        self.Graph_type_CB.currentIndexChanged.connect(self.set_Scales)
        self.xGrid_CB.stateChanged.connect(self.plot_grid_settings)
        self.yGrid_CB.stateChanged.connect(self.plot_grid_settings)
        self.MinorGrid_CB.stateChanged.connect(self.plot_grid_settings)
        self.Plot_by_CB.currentIndexChanged.connect(self.Plot_By)
        self.score_plot_PB.clicked.connect(self.Plot)
        #self.TightPlots_PB.clicked.connect(lambda:plt.tight_layout())
        self.Close_Plots_PB.clicked.connect(lambda:plt.close('all'))
        self.ResetPlotSettings_PB.clicked.connect(self.Reset_Plot_Settings)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
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
        for i in range(self.MaxRecentFiles):
            self.filemenu.addAction(self.recentFileActs[i])
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
        self.readSettings()
        self.statusBar().showMessage("self.root is: " + self.root, 0)

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
        #buttonC = box.button(QMessageBox.Cancel)
        #buttonC.setText('close gui only')        
        
        box.exec_()
        if box.clickedButton() == buttonY:
            return 
        elif box.clickedButton() == buttonD:
            plt.close('all')
                    
        elif box.clickedButton() == buttonN:
            plt.close('all')
            self.close()
        """elif box.clickedButton() == buttonN:
            self.close()"""

    def HLAct(self):
        if self.checkbox.isChecked():
            from src.syntax_py import Highlighter
            self.highlighter = Highlighter(self.editor.document())
        else:
            from src.syntax import Highlighter
            self.highlighter = Highlighter(self.editor.document())

    def getLineNumber(self):
        self.editor.moveCursor(self.editor.cursor.StartOfLine)
        linenumber = self.editor.textCursor().blockNumber() + 1
        return linenumber

    def replaceAll(self):
        if not self.editor.document().toPlainText() == "":
            if not self.findfield.text() == "":
                self.statusBar().showMessage("replacing all")
                oldtext = self.editor.document().toPlainText()
                newtext = oldtext.replace(self.findfield.text(), self.replacefield.text())
                self.editor.setPlainText(newtext)
                self.setModified(True)
            else:
                self.statusBar().showMessage("nothing to replace")
        else:
                self.statusBar().showMessage("no text")

    def goToLine(self, ft):
        self.editor.moveCursor(int(self.gofield.currentText()),
                                QTextCursor.MoveAnchor) ### not working

    def replaceOne(self):
        if not self.editor.document().toPlainText() == "":
            if not self.findfield.text() == "":
                self.statusBar().showMessage("replacing all")
                oldtext = self.editor.document().toPlainText()
                newtext = oldtext.replace(self.findfield.text(), self.replacefield.text(), 1)
                self.editor.setPlainText(newtext)
                self.setModified(True)
            else:
                self.statusBar().showMessage("nothing to replace")
        else:
                self.statusBar().showMessage("no text")

    def findText(self):
        word = self.findfield.text()
        if self.editor.find(word):
            linenumber = self.editor.textCursor().blockNumber() + 1
            self.statusBar().showMessage("found <b>'" + self.findfield.text() + "'</b> at Line: " + str(linenumber))
            self.editor.centerCursor()
        else:
            self.statusBar().showMessage("<b>'" + self.findfield.text() + "'</b> not found")
            self.editor.moveCursor(QTextCursor.Start)
            if self.editor.find(word):
                linenumber = self.editor.textCursor().blockNumber() + 1
                self.statusBar().showMessage("found <b>'" + self.findfield.text() + "'</b> at Line: " + str(linenumber))
                self.editor.centerCursor()

    def gotoLine(self):
        ln = int(self.gotofield.text())
        linecursor = QTextCursor(self.editor.document().findBlockByLineNumber(ln-1))
        self.editor.moveCursor(QTextCursor.End)
        self.editor.setTextCursor(linecursor)

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

    def mergeFormatOnWordOrSelection(self, format):
        cursor = self.editor.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)

        cursor.mergeCharFormat(format)
        self.editor.mergeCurrentCharFormat(format)

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
        '''for widget in QApplication.topLevelWidgets():
            if isinstance(widget, myEditor):
                widget.updateRecentFileActions()
        self.updateRecentFileActions()'''

    def infobox(self,title, message):
        QMessageBox(QMessageBox.Information, title, message, QMessageBox.NoButton, self, Qt.Dialog|Qt.NoDropShadowWindowHint).show()

    def handlePrint(self):
        if self.editor.toPlainText() == "":
            self.statusBar().showMessage("no text")
        else:
            dialog = QtPrintSupport.QPrintDialog()
            if dialog.exec_() == QDialog.Accepted:
                self.handlePaintRequest(dialog.printer())
                self.statusBar().showMessage("Document printed")

    def handlePrintPreview(self):
        if self.editor.toPlainText() == "":
            self.statusBar().showMessage("no text")
        else:
            dialog = QtPrintSupport.QPrintPreviewDialog()
            dialog.setFixedSize(900,650)
            dialog.paintRequested.connect(self.handlePaintRequest)
            dialog.exec_()
            self.statusBar().showMessage("Print Preview closed")

    def handlePaintRequest(self, printer):
        printer.setDocName(self.filename)
        document = self.editor.document()
        document.print_(printer)

    def findNextWord(self):
        if self.editor.textCursor().selectedText() == "":
            tc = self.editor.textCursor()
            tc.select(QTextCursor.WordUnderCursor)
            rtext = tc.selectedText()
        else:
            rtext = self.editor.textCursor().selectedText()
        self.findfield.setText(rtext)
        self.findText()

    ### QPlainTextEdit contextMenu
    def contextMenuRequested(self, point):
        cmenu = QMenu()
        cmenu = self.editor.createStandardContextMenu()
        cmenu.addSeparator()
        cmenu.addAction(self.jumpToAct)
        cmenu.addSeparator()
        if not self.editor.textCursor().selectedText() == "":
            cmenu.addAction(QIcon.fromTheme("gtk-find-and-replace"),"replace all occurrences with", self.replaceThis)
            cmenu.addSeparator()
        cmenu.addAction(QIcon.fromTheme("gtk-find-"),"find this (F10)", self.findNextWord)
        cmenu.addAction(self.texteditAction)
        cmenu.addSeparator()
        cmenu.addAction(QIcon('src/icons/color.png'), "change Color", self.changeColor)
        cmenu.exec_(self.editor.mapToGlobal(point))   

    def clearLabel(self):
        self.editor.clear()

    def readSettings(self):
        if self.settings.value("pos") != "":
            pos = self.settings.value("pos", QPoint(200, 200))
            self.move(pos)
        if self.settings.value("size") != "":
            size = self.settings.value("size", QSize(400, 400))
            self.resize(size)

    def mergeFormatOnWordOrSelection(self, format):
        cursor = self.editor.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)

        cursor.mergeCharFormat(format)
        self.editor.mergeCurrentCharFormat(format)

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

    def clearBookmarks(self):
        self.bookmarks.clear()

        ### New File
    def newFile(self):
        if self.maybeSave():
            self.editor.clear()
            #self.editor.setPlainText(self.mainText)
            self.filename = ""
            self.setModified(False)
            self.editor.moveCursor(self.editor.cursor.End)
            self.statusBar().showMessage("new File created.")
            self.editor.setFocus()
            self.bookmarks.clear()
            self.setWindowTitle("new File[*]") 

       ### open File
    def openFileOnStart(self, path=None):
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
                self.statusBar().showMessage("File '" + path + "' loaded succesfully & bookmarks added & backup created ('" + self.filename + "_backup" + "')")

        ### open File
    def openFile(self, path=None):
        if self.openPath == "":
            self.openPath = self.dirpath
        if self.maybeSave():
            if not path:
                path, _ = QFileDialog.getOpenFileName(self, "Open File", self.openPath,
                    "Text Files (*.txt);; all Files (*)")

            '''if path:
                self.openFileOnStart(path)'''

    def fileSave(self):
        if (self.filename != ""):
            file = QFile(self.filename)
            if not file.open( QFile.WriteOnly | QFile.Text):
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
            self.statusBar().showMessage("File saved.")
            self.setCurrentFile(self.filename)
            self.editor.setFocus()

        else:
            self.fileSaveAs()

    def exportPDF(self):
        if self.editor.toPlainText() == "":
            self.statusBar().showMessage("no text")
        else:
            newname = self.editor.strippedName(self.filename).replace(QFileInfo(self.filename).suffix(), "pdf")
            fn, _ = QFileDialog.getSaveFileName(self,
                    "PDF files (*.pdf);;All Files (*)", (QDir.homePath() + "/PDF/" + newname))
            printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
            printer.setOutputFormat(QtPrintSupport.QPrinter.PdfFormat)
            printer.setOutputFileName(fn)
            self.editor.document().print_(printer)
            
            ### save File
    def fileSaveAs(self):
        fn, _ = QFileDialog.getSaveFileName(self, "Save as...", self.filename, "Text Files (*.txt);; all Files (*)")

        if not fn:
            print("Error saving")
            return False

        """lfn = fn.lower()
        if not lfn.endswith('.py'):
            fn += '.py'   """

        self.filename = fn
        self.fname = QFileInfo(QFile(fn).fileName())
        return self.fileSave()

        ### ask to save
    def maybeSave(self):
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
        return self.editor.document().isModified()

    def setModified(self, modified):
        self.editor.document().setModified(modified)

    def createActions(self):
        for i in range(self.MaxRecentFiles):
            self.recentFileActs.append(QAction(self, visible=False, triggered=self.openRecentFile))

    def openRecentFile(self):
        action = self.sender()
        if action:
            myfile = action.data()
            if (self.maybeSave()):
                if QFile.exists(myfile):
                    self.openFileOnStart(myfile)
                else:
                    self.msgbox("Info", "File does not exist!")

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

    def updateRecentFileActions(self):
        if self.settings.contains('recentFileList'):
            mytext = ""
            files = self.settings.value('recentFileList', [])

    def strippedName(self, fullFileName):
        return QFileInfo(fullFileName).fileName()

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#++++++++++++++++++++++ CODE TO PROCESS SIMULATION SP FILE +++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def Get_SP_File(self):
        self.Tally_id_comboBox.clear()
        self.Tally_id_comboBox.addItem("Select the tally's ID")
        self.editor.clear()
        self.tabWidget_2.setCurrentIndex(0)
        self.sp_file = QtWidgets.QFileDialog.getOpenFileName(self,"Select The StatePoint File","~","statepoint*.h5")[0]
        self.lineEdit.setText(self.sp_file)
        self.Get_data_from_SP_file()

    def Get_data_from_SP_file(self):
        global sp
        if self.sp_file:
            try:
                sp = openmc.StatePoint(self.sp_file)
                #self.tally = sp.get_tally()
                self.names = {}
                self.Nuclides = {}
                self.Scores = {}
                self.Estimator = {}
                self.keys = list(sp.tallies.keys())
                for key in self.keys:
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
                    #self.combo3.addItems(Scores[key])
                    self.Tally_id_comboBox.addItem(str(key))
            except:
                #self.shellwin.setPlainText("Something went wrong when reading the statepoint file !")
                self.showDialog("Error", "Something went wrong when reading the statepoint file.\n Choose an other file !")
                self.lineEdit.clear()
                return

    def SelectTally(self):
        self.score_plot_PB.setText('plot data')
        self.filters = []
        self.Bins = {}
        self.meshes = {}
        self.Tallies['tallies_ids'] = []
        self.Tallies['names'] = []
        self.Tally_name_LE.clear()
        self.Curve_title.clear()
        self.Nuclides_List_LE.clear()
        self.Scores_List_LE.clear()
        for elm in self.buttons:
            elm.setEnabled(False)
        self.Graph_Layout_CB.setCurrentIndex(0)
        self.Graph_type_CB.setCurrentIndex(0)
        self.Graph_Layout_CB.setEnabled(False)
        self.score_plot_PB.setEnabled(False)
        self.xGrid_CB.setChecked(False)
        self.yGrid_CB.setChecked(False)
        self.MinorGrid_CB.setChecked(False)
        if self.Tally_id_comboBox.currentIndex() >= 1:
            _f = h5py.File(self.sp_file, 'r')
            tallies_group = _f['tallies']
            n_tallies = tallies_group.attrs['n_tallies']
            tally_ids = tallies_group.attrs['ids']
            for tally_id in tally_ids:
                tally = sp.get_tally(id=tally_id)  # Ok
                name = tally.name
                self.Tallies['tallies_ids'].append(tally_id)
                self.Tallies['names'].append(name)
            # Read all meshes
            mesh_group = _f['tallies/meshes']
            
            # Iterate over all meshes
            for group in mesh_group.values():
                mesh = openmc.MeshBase.from_hdf5(group)
                self.meshes[mesh.id] = mesh
        if self.Tally_id_comboBox.currentIndex() >= 1:
            tally_id = int(self.Tally_id_comboBox.currentText())
            self.Filters_comboBox.clear()
            self.Scores_comboBox.clear()
            self.Filters_comboBox.clear()
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
            group = tallies_group[f'tally {tally_id}']
            # hide comboBoxes in gridLayout_20
            for i in range(self.gridLayout_20.layout().count()):
                widget = self.gridLayout_20.layout().itemAt(i).widget()
                widget.hide()            
            
            # Read all filters
            self.n_filters = group['n_filters'][()]
            if self.n_filters > 0:                  # filters are defined
                self.Bins_comboBox = [''] * self.n_filters

                for i in range(self.n_filters):
                    self.Bins_comboBox[i] = CheckableComboBox()
                    self.gridLayout_20.addWidget(self.Bins_comboBox[i],1 ,i + 1)
                    #self.Bins_comboBox[i].currentIndexChanged.connect(self.SelectBins)

                self.filter_ids = group['filters'][()].tolist()
                self.Tallies[tally_id]['filter_ids'] = self.filter_ids
                filters_group = _f['tallies/filters']
                
                for filter_id in self.filter_ids:  
                    self.Tallies[tally_id][filter_id] = {}
                    self.Tallies[tally_id][filter_id]['Checked_bins'] = []                  
                    self.Tallies[tally_id][filter_id]['Checked_bins_text'] = []                  
                    self.Tallies[tally_id][filter_id]['scores'] = []
                    filter_group = filters_group[f'filter {filter_id}']
                    new_filter = openmc.Filter.from_hdf5(filter_group, meshes=self.meshes)
                    filter_name = str(type(new_filter)).split('.filter.')[1].rstrip("'>")
                    filter_type = filter_group['type'][()].decode()
                    self.Tallies[tally_id]['filter_types'] += [filter_type]
                    self.Tallies[tally_id]['filter_names'] += [filter_name]
                filters = [filter + ' , id= ' + str(id) for filter, id in zip(self.Tallies[tally_id]['filter_names'], self.filter_ids)]
                self.Filters_comboBox.addItems(filters)

                # fill scores combobox
                self.scores = sorted(self.tally.scores)
                self.Tallies[tally_id][filter_id]['scores'] = self.scores
                self.Scores_comboBox.clear()
                self.Scores_comboBox.addItem('Select score')
                if len(self.scores) > 1:
                    self.Scores_comboBox.addItem('All scores')
                self.Scores_comboBox.addItems(self.scores)
            else:                               # no filter defined
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
                #self.Nuclides_comboBox.addItems(['total','All nuclides'])
                self.Nuclides_comboBox.addItems(['All nuclides'])
            self.Nuclides_comboBox.addItems(self.nuclides)
            self.Nuclides_comboBox.setCurrentIndex(1)
            #self.Nuclides_List_LE.setText(self.Nuclides_comboBox.currentText())
            if len(self.scores) == 1:
                self.Scores_List_LE.setText(self.scores[0]) 
            if self.n_filters == 1:
                self.Filters_comboBox.setCurrentIndex(1) 
                      
        else:
            self.Tally_name_LE.clear()
            self.Curve_title.clear()
            self.Filters_comboBox.clear()


    def SelectScores(self):        
        if self.Tally_id_comboBox.currentIndex() >= 1:
            tally_id = int(self.Tally_id_comboBox.currentText())
            if self.Scores_comboBox.currentIndex() > 0:
                if self.Scores_comboBox.currentText() == 'All scores':
                    selected_score = self.scores
                else:
                    selected_score = list(filter(None, self.Scores_List_LE.text().split(' ')))
                    selected_score.append(str(self.Scores_comboBox.currentText()))
                selected_score = sorted(selected_score)
                self.selected_score = list(dict.fromkeys(selected_score))
                text = ' '.join(self.selected_score)
                self.Scores_List_LE.clear()
                self.Scores_List_LE.setText(text)

    def SelectNuclides(self):
        if self.Tally_id_comboBox.currentIndex() >= 1:
            tally_id = int(self.Tally_id_comboBox.currentText())
            if self.Nuclides_comboBox.currentIndex() > 0:
                if self.Nuclides_comboBox.currentText() == 'All nuclides':
                    selected_nuclides = self.nuclides
                    self.Nuclides_List_LE.setText(str([nuclide for nuclide in selected_nuclides]))
                else:
                    selected_nuclides = list(filter(None, self.Nuclides_List_LE.text().split(' ')))
                    selected_nuclides.append(str(self.Nuclides_comboBox.currentText()))
                selected_nuclides = sorted(selected_nuclides)
                selected_nuclides = list(dict.fromkeys(selected_nuclides))
                text = ' '.join(selected_nuclides)
                self.Nuclides_List_LE.clear()
                self.Nuclides_List_LE.setText(text)
                self.Tallies[tally_id]['selected_nuclides'] = selected_nuclides

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
        if self.Tally_id_comboBox.currentIndex() > 0:
            tally_id = int(self.Tally_id_comboBox.currentText())
            self.tally = sp.get_tally(id=tally_id)
            tally = self.tally 
            try:
                self.Bins_comboBox[self.Filters_comboBox.currentIndex() - 1].clear()
            except:
                pass

            if self.Filters_comboBox.currentIndex() > 0:
                self.label_4.setText('Select bins')
                #filter_id = self.Tallies[tally_id]['filter_ids'][self.Filters_comboBox.currentIndex() - 1]
                filter_id = self.filter_ids[self.Filters_comboBox.currentIndex() - 1]
                self.Tallies[tally_id][filter_id]['bins'] = []
                #self.Tallies[tally_id][filter_id]['scores'] = []
                self.Tallies[tally_id][filter_id]['bins'] = tally.filters[self.Filters_comboBox.currentIndex() - 1].bins
                Bins = self.Tallies[tally_id][filter_id]['bins']
                '''self.Bins_comboBox[self.Filters_comboBox.currentIndex() - 1].addItems(['Select bin', 'All bins'])
                self.Bins_comboBox[self.Filters_comboBox.currentIndex() - 1].setItemChecked(0, False)'''
                
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
                    
                    #self.mesh_name = tally.filters[0].mesh.name
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
                        '''bins = [str(item) for item in tally.filters[self.Filters_comboBox.currentIndex() - 1].bins]     #????
                        return'''
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

                    '''    
                        if self.Mesh_xy_RB.isChecked():
                            self.z_id = [item[2] for item in
                                        [self.mesh_ids[i] for i in range(0, len(self.mesh_ids), self.id_step)]]
                            self.list_axis = ['slice at z = ' + str("{:.1E}".format(z_)) for z_ in self.z]
                        if self.Mesh_xy_RB.isChecked():
                            self.spinBox.setMinimum(1)
                            self.spinBox.setMaximum(self.mesh_dimension[0])
                            self.spinBox_2.setMinimum(1)
                            self.spinBox_2.setMaximum(self.mesh_dimension[1])
                    bins = [str(item) for item in tally.filters[self.Filters_comboBox.currentIndex() - 1].bins]     #????
                    #return'''
                elif 'EnergyFilter' in self.Filters_comboBox.currentText():
                    self.xlabel.setText('xlabel')
                    self.ylabel.setText('ylabel')
                    first = [item[0] for item in Bins]
                    last = [item[1] for item in Bins]
                    self.Checked_energies_Low = first
                    self.Checked_energies_High = last
                    bins = [str(("{:.3E}".format(x), "{:.3E}".format(y),)).replace("'", "") for x, y in
                            zip(first, last)]
                    self.Bins_tuple = tuple(Bins[0])                
                else:
                    self.Mesh_xy_RB.hide()
                    self.Mesh_xz_RB.hide()
                    self.Mesh_yz_RB.hide()
                    self.spinBox.hide()
                    self.spinBox_2.hide()
                    self.Curve_title.clear()
                    self.Curve_title.setText(self.Tally_name_LE.text())
                    self.xlabel.setText('xlabel')
                    self.ylabel.setText('ylabel')
                    self.Curve_xLabel.clear()
                    self.Curve_yLabel.clear()
                    bins =sorted([str(item) for item in Bins])

                self.Tallies[tally_id][filter_id]['bins'] = bins
                self.Bins_comboBox[self.Filters_comboBox.currentIndex() - 1].clear()
                self.Bins_comboBox[self.Filters_comboBox.currentIndex() - 1].addItems(['Select bin', 'All bins'])
                self.Bins_comboBox[self.Filters_comboBox.currentIndex() - 1].setItemChecked(0, False)
                self.Bins_comboBox[self.Filters_comboBox.currentIndex() - 1].addItems(bins)
                if 'MeshFilter' in self.Filters_comboBox.currentText() and len(tally.filters[0].mesh._grids) == 2:
                    self.Bins_comboBox[self.Filters_comboBox.currentIndex() - 1].setCurrentIndex(2)
                try:
                    if self.Tallies[tally_id][filter_id]['Checked_bins']:
                        for j in self.Tallies[tally_id][filter_id]['Checked_bins']: 
                            bin = self.Tallies[tally_id][filter_id]['bins'][j-2]
                            self.Bins_comboBox[self.Filters_comboBox.currentIndex() - 1].setItemChecked(j, True)
                    else:
                        for i in range(len(bins) + 1):
                            self.Bins_comboBox[self.Filters_comboBox.currentIndex() - 1].setItemChecked(i, False)
                except:
                    self.showDialog('Warning', ' Filter bins not set!')
            else:
                try:
                    for i in range(len(self.Bins_comboBox)):
                        self.Bins_comboBox[i].clear()
                except:
                    pass
        else:
            pass
            
        try:
            for i in range(len(self.Bins_comboBox)):
                self.Bins_comboBox[i].currentIndexChanged.connect(self.SelectBins)
        except:
            pass

    def Display_filters(self):
        self.tabWidget_2.setCurrentIndex(0)
        if self.sp_file:
            if self.Tally_id_comboBox.currentIndex() > 0:
                tally_id = int(self.Tally_id_comboBox.currentText())
                if self.Filters_comboBox.currentIndex() > 0:
                    #filter_id = self.Tallies[tally_id]['filter_ids'][self.Filters_comboBox.currentIndex() - 1]
                    filter_id = self.filter_ids[self.Filters_comboBox.currentIndex() - 1]
                    self.Filter_Bins_Select(tally_id, filter_id)
                    print('\n************************************************************',
                          '\nTally Id            : ', tally_id, 
                          '\nFilter Id           : ', filter_id,
                          '\nFilter type         : ', self.Filters_comboBox.currentText().split(',')[0],
                          '\nChecked bins        : ', self.Tallies[tally_id][filter_id]['Checked_bins_text'],
                          '\nChecked bins indices: ', self.checked_bins,
                          '\n************************************************************')
        else:
            self.showDialog('Warning', 'Select your StatePoint file first !')

    def SelectBins(self):
        if self.Tally_id_comboBox.currentIndex() > 0:
            tally_id = int(self.Tally_id_comboBox.currentText())
            self.tally = sp.get_tally(id=tally_id)
            tally = self.tally
            if self.Filters_comboBox.currentIndex() > 0:
                #filter_id = self.Tallies[tally_id]['filter_ids'][self.Filters_comboBox.currentIndex() - 1]
                filter_id = self.filter_ids[self.Filters_comboBox.currentIndex() - 1]
                self.Bins_comboBox[self.Filters_comboBox.currentIndex() - 1].setItemDisabled(0)
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
                self.Bins_comboBox[self.Filters_comboBox.currentIndex() - 1].setCurrentIndex(0)

    def Filter_Bins_Select(self, tally_id, filter_id):
        if self.Bins_comboBox[self.Filters_comboBox.currentIndex() - 1].currentIndex() == 1:
            if self.Bins_comboBox[self.Filters_comboBox.currentIndex() - 1].checkedItems():
                self.Tallies[tally_id][filter_id]['Checked_bins'] = self.Bins_comboBox[self.Filters_comboBox.currentIndex() - 1].checkedItems()
            else:
                self.Tallies[tally_id][filter_id]['Checked_bins'] = []
            if self.Tallies[tally_id][filter_id]['Checked_bins']:
                self.Tallies[tally_id][filter_id]['Checked_bins'].pop(0)
            
        elif self.Bins_comboBox[self.Filters_comboBox.currentIndex() - 1].currentIndex() > 1:
            self.Tallies[tally_id][filter_id]['Checked_bins'] = self.Bins_comboBox[self.Filters_comboBox.currentIndex() - 1].checkedItems()
        indices = self.Tallies[tally_id][filter_id]['Checked_bins']
        lst = self.Tallies[tally_id][filter_id]['bins']
        self.Tallies[tally_id][filter_id]['Checked_bins_text'] = [elm for elm in lst if lst.index(elm) + 2 in indices]
        self.checked_bins = self.Tallies[tally_id][filter_id]['Checked_bins']
        if 'MeshFilter' in self.Filters_comboBox.currentText():
            self.Tallies[tally_id][filter_id]['ijk_indices'] = {}
            if self.Mesh_xy_RB.isChecked():
                for bin_id in range(len(self.checked_bins)):
                    self.Tallies[tally_id][filter_id]['ijk_indices'][self.checked_bins[bin_id]] = []
                    k = self.checked_bins[bin_id]
                    ijk_indices = [item + (k,) for item in self.Tallies[tally_id][filter_id]['ij_indices']]
                    self.Tallies[tally_id][filter_id]['ijk_indices'][self.checked_bins[bin_id]] = ijk_indices
            elif self.Mesh_xz_RB.isChecked():
                for bin_id in range(len(self.checked_bins)):
                    self.Tallies[tally_id][filter_id]['ijk_indices'][self.checked_bins[bin_id]] = []
                    j = self.checked_bins[bin_id]
                    ijk_indices = [item[:1] + (j,) + item[1:] for item in self.Tallies[tally_id][filter_id]['ij_indices']]
                    self.Tallies[tally_id][filter_id]['ijk_indices'][self.checked_bins[bin_id]] = ijk_indices
            elif self.Mesh_yz_RB.isChecked():
                for bin_id in range(len(self.checked_bins)):
                    self.Tallies[tally_id][filter_id]['ijk_indices'][self.checked_bins[bin_id]] = []
                    i = self.checked_bins[bin_id]
                    ijk_indices = [(i,) + item for item in self.Tallies[tally_id][filter_id]['ij_indices']]
                    self.Tallies[tally_id][filter_id]['ijk_indices'][self.checked_bins[bin_id]] = ijk_indices
        elif 'CellFilter' in self.Filters_comboBox.currentText():
            self.Checked_cells = self.Tallies[tally_id][filter_id]['Checked_bins']
        elif 'SurfaceFilter' in self.Filters_comboBox.currentText():
            self.Checked_surfaces = self.Tallies[tally_id][filter_id]['Checked_bins']
        elif 'EnergyFilter' in self.Filters_comboBox.currentText():
            self.Checked_energies_Low = self.Tallies[tally_id][filter_id]['Checked_bins']
        elif 'MuFilter' in self.Filters_comboBox.currentText():
            self.Checked_mu_Low = self.Tallies[tally_id][filter_id]['Checked_bins']
        elif 'EnergyFilter' in self.Filters_comboBox.currentText():
            self.Checked_energies_High = self.Tallies[tally_id][filter_id]['Checked_bins']     # !!!!!!!!
        else:
            pass

    def Get_Tally_Inf(self):
        self.textEdit_2.clear()
        if self.sp_file:
            self.tabWidget_2.setCurrentIndex(1)
            sp = openmc.StatePoint(self.sp_file)
            for key in sp.tallies.keys():
                self.textEdit_2.insertPlainText(str(sp.tallies[key])+'\n')
        else:
            msg = 'Please select your StatePoint file first !'
            self.showDialog('Warning', msg)

    def Display_tally(self):
        if self.sp_file:
            self.tabWidget_2.setCurrentIndex(0)
            if self.Tally_id_comboBox.currentIndex() > 0:
                tally_id = int(self.Tally_id_comboBox.currentText())
                self.tally = sp.get_tally(id=tally_id)
                print(self.tally , '\n')
                df = self.tally.get_pandas_dataframe(float_format = '{:.2e}')  #'{:.6f}')
                if 'surface' in df.keys():
                    self.df = df.sort_values(by=['nuclide', 'surface'])
                elif 'cell' in df.keys():
                    self.df = df.sort_values(by=['score', 'nuclide', 'cell'])
                elif 'surface' in df.keys() and 'cell' in df.keys():
                    self.df = df.sort_values(by=['score', 'nuclide', 'surface', 'cell'])
                elif 'cell' in df.keys() and 'surface' in df.keys():
                    self.df = df.sort_values(by=['score', 'nuclide', 'cell', 'surface'])
                elif 'nuclide' in df.keys():
                    self.df = df.sort_values(by=['score', 'nuclide'])  
                
                self.df_reshaped = self.tally.get_reshaped_data()
                pd.options.display.float_format = '         {:,.2e}    '.format
                for key in self.df.keys()[:-2]:
                    self.df[key] = self.df[key].apply('{: >20}'.format)
                print(self.df.to_string() + '\n\n')
                print('\n Available keys : ', list(self.df.keys()[:]), '\n\n')
            else:
                self.showDialog('Warning', 'Select tally first !')
        else:
            msg = 'Please select your StatePoint file first !'
            self.showDialog('Warning', msg)
        
    def Clear_nuclides(self):
        self.Nuclides_List_LE.clear()
        self.Nuclides_comboBox.setCurrentIndex(0)

    def Display_scores(self):
        if not self.sp_file:
            self.showDialog('Warning', 'Please select your StatePoint file first !')
            return
        if self.Tally_id_comboBox.currentIndex() == 0:
            self.showDialog('Warning', "Select tally's id first !")
            return
        if not self.Scores_List_LE.text().strip():
            self.showDialog('Warning', 'Select score first!')
            return
        self.tabWidget_2.setCurrentIndex(0)
        self.Graph_Layout_CB.setEnabled(True)
        self.Graph_Layout_CB.setCurrentIndex(0)
        self.Add_error_bars_CB.setChecked(False)        
        self.tally_id = int(self.Tally_id_comboBox.currentText())
        #self.filter_ids = self.Tallies[self.tally_id]['filter_ids']
        df = self.tally.get_pandas_dataframe(float_format = '{:.2e}')  #'{:.6f}')
        if 'surface' in df.keys():
            self.df = df.sort_values(by=['nuclide', 'surface'])
        elif 'cell' in df.keys():
            self.df = df.sort_values(by=['score', 'nuclide', 'cell'])
        elif 'surface' in df.keys() and 'cell' in df.keys():
            self.df = df.sort_values(by=['score', 'nuclide', 'surface', 'cell'])
        elif 'cell' in df.keys() and 'surface' in df.keys():
            self.df = df.sort_values(by=['score', 'nuclide', 'cell', 'surface'])
        elif 'nuclide' in df.keys():
            self.df = df.sort_values(by=['score', 'nuclide']) 

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
        self.selected_score = list(filter(None, self.Scores_List_LE.text().split(' ')))
        self.selected_score = sorted(self.selected_score)
        self.selected_score = list(dict.fromkeys(self.selected_score))
        for elm in self.selected_score:
            if elm not in self.scores:
                self.showDialog('Warning', 'score : ' + str(elm) + ' not tallied for current tally!')
                return
        self.Tallies[self.tally_id]['selected_scores'] = self.selected_score

        self.Plot_by_CB.clear()
        self.Plot_by_CB.addItem('select item')
        if self.n_filters == 0:                                   # scores are not filtered
            self.filter_ids = [0]
            self.filter_id = 0               
            self.Unfiltered_Scores()
            self.Deactivate_Curve_Type()
        elif self.n_filters == 1:                                 # scores are filtered once
            Filter_Index = self.Filters_comboBox.currentIndex()
            self.filter_id = self.filter_ids[Filter_Index - 1]
            if not self.Tallies[self.tally_id][self.filter_id]['Checked_bins']:
                self.showDialog('Warning', 'Check filter bins first !')
                return

            print('Tally filter type: ', self.Filters_comboBox.currentText().split(',')[0])
            print('Tally filter bins: ', self.Tallies[self.tally_id][self.filter_id]['bins'])
            self.Filter_Bins_Select(self.tally_id, self.filter_id)
            
            if 'MeshFilter' in self.Filters_comboBox.currentText(): # MeshFilter
                for elm in self.buttons:
                    elm.setEnabled(False)
                self.Graph_Layout_CB.setEnabled(False)
                self.Plot_by_CB.setEnabled(False)
                self.score_plot_PB.setEnabled(True)
                self.label.setEnabled(False)
                self.score_plot_PB.setText('plot mesh')
                self.Mesh_scores()
                return
            else:
                if self.Graph_type_CB.currentIndex() == 0:
                    for elm in self.buttons:
                        elm.setEnabled(False)
                else:
                    for elm in self.buttons:
                        elm.setEnabled(True)
                self.Graph_Layout_CB.setEnabled(True)
                self.Plot_by_CB.setEnabled(True)
                self.label.setEnabled(True)
                self.Curve_yLabel.setText(self.Scores_List_LE.text())
                self.score_plot_PB.setText('plot score')
                if 'EnergyFilter' in self.Filters_comboBox.currentText(): # EnergyFilter
                    self.Curve_xLabel.setText('Energy / eV')
                    self.Select_Energies(Filter_Index)
                    self.Energy_scores()
                    self.Activate_Curve_Type()
                    self.Checked_energies = self.Checked_energies_Low
                    if self.row_SB.value() * self.col_SB.value() < len(self.Checked_energies) or self.row_SB.value() * self.col_SB.value() > len(self.Checked_energies) + 1:
                        self.col_SB.setValue(int(len(self.Checked_energies)/2 + 0.5))
                    #self.Plot_by_CB.addItem('energy')
                    key = 'energy low [eV]'
                    key_selected_bins = self.Checked_energies_Low
                elif 'MuFilter' in self.Filters_comboBox.currentText(): # MuFilter
                    self.Curve_xLabel.setText('mu')                    
                    self.Select_Mu(Filter_Index)
                    self.Mu_scores()
                    self.Activate_Curve_Type()
                    self.Checked_mu = self.Checked_mu_Low
                    if self.row_SB.value() * self.col_SB.value() < len(self.Checked_mu) or self.row_SB.value() * self.col_SB.value() > len(self.Checked_mu) + 1:
                        self.col_SB.setValue(int(len(self.Checked_mu)/2 + 0.5))
                    #self.Plot_by_CB.addItem('mu')
                    key = 'mu low'
                    key_selected_bins = self.Checked_mu_Low
                elif 'CellFilter' in self.Filters_comboBox.currentText(): # CellFilter
                    self.Curve_xLabel.setText('Cells')
                    self.Select_Cells(Filter_Index)
                    self.Cell_scores()
                    self.Deactivate_Curve_Type()
                    if self.row_SB.value() * self.col_SB.value() < len(self.Checked_cells) or self.row_SB.value() * self.col_SB.value() > len(self.Checked_cells) + 1:
                        self.col_SB.setValue(int(len(self.Checked_cells)/2 + 0.5))
                    #self.Plot_by_CB.addItem('cell')
                    key = 'cell'
                    key_selected_bins = self.Checked_cells
                elif 'SurfaceFilter' in self.Filters_comboBox.currentText(): # SurfaceFilter
                    self.Curve_xLabel.setText('Surfaces')
                    self.Select_Surfaces(Filter_Index)
                    self.Surface_scores()            
                    self.Deactivate_Curve_Type()
                    if self.row_SB.value() * self.col_SB.value() < len(self.Checked_surfaces) or self.row_SB.value() * self.col_SB.value() > len(self.Checked_surfaces) + 1:
                        self.col_SB.setValue(int(len(self.Checked_surfaces)/2 + 0.5))
                    #self.Plot_by_CB.addItem('surfaces')
                    key = 'surface'
                    key_selected_bins = self.Checked_surfaces

        elif self.n_filters > 1:
            self.showDialog('Warning', 'Sorry, under development !')
            for i in range(1, int(self.n_filters) + 1):
                self.filter_id = self.filter_ids[i-1]
                if 'CellFilter' in self.Filters_comboBox.itemText(i):
                    self.Select_Cells(i)
                elif 'EnergyFilter' in self.Filters_comboBox.itemText(i):
                    self.Select_Energies(i)

            for i in range(1, self.n_filters):
                self.filter_id = self.filter_ids[i-1]
                if 'CellFilter' in self.Filters_comboBox.itemText(i):
                    if 'EnergyFilter' in self.Filters_comboBox.itemText(i+1):
                        self.Cell_scores1()
                        self.filter_id = self.filter_ids[i]
                    else:
                        pass
                else:
                    pass
            return

        if 'surface' in self.df.keys():
            self.Plot_by_CB.addItems([item for item in list(self.df.keys()[:-2]) if item != 'nuclide'])    
        else:        
            self.Plot_by_CB.addItems(list(self.df.keys()[:-2]))            
        self.Plot_by_CB.setCurrentIndex(1)
        self.Curve_title.setText(self.Tally_name_LE.text())
        if len(self.selected_score) == 1: 
            if self.selected_score[0] == 'flux':
                self.Curve_yLabel.setText(self.selected_score[0] + ' /cm')
            else:
                self.Curve_yLabel.setText(self.selected_score[0])
        else:
            self.Curve_yLabel.setText('Tallies')
        if self.filter_id == 0:
            self.Curve_xLabel.setText('Nuclides')   
        print('\nTally nuclides : ', self.tally.nuclides)
        print('\nSelected nuclides : ', self.selected_nuclides)
        print('\nTally scores: ', self.tally.scores)
        print('\nSelected scores : ', self.selected_score, '\n')   
        if self.n_filters == 0:   
            print(self.df.loc[(df['score'].isin(self.selected_score)) & (df['nuclide'].isin(self.selected_nuclides))])       
        else:    
            print(self.df.loc[(df['score'].isin(self.selected_score)) & (df[key].isin(key_selected_bins)) & (df['nuclide'].isin(self.selected_nuclides))])       

    def Select_Energies(self, Filter_Index):
        all_bins = self.tally.filters[Filter_Index - 1].bins[:, 0]
        self.Checked_energies_Low = []
        self.Checked_energies_High = []
        self.Checked_Energy_Bins = []
        indices = self.Tallies[self.tally_id][self.filter_id]['Checked_bins']
        for index in indices:
            self.Checked_energies_Low.append(self.tally.filters[Filter_Index - 1].bins[:, 0][index - 2])
            self.Checked_energies_High.append(self.tally.filters[Filter_Index - 1].bins[:, 1][index - 2])
            self.Checked_Energy_Bins.append(self.tally.filters[Filter_Index - 1].bins[:][index - 2])
        print('Checked energies : ', self.Checked_Energy_Bins)

    def Energy_scores(self):
        df = self.df
        self.mean = {}
        self.std = {}
        if 'cell' not in self.df.keys()[:-2].tolist():
            self.Checked_cells = ['root']
        for nuclide in self.selected_nuclides:
            if nuclide != '':        
                for score in self.selected_score:
                    if score != '':
                        Score = df[df['score'] == score]

                        index = self.selected_score.index(score)
                        self.mean[index] = {}
                        self.std[index] = {}
                        Score1 = Score[Score['nuclide'] == nuclide]
                        self.mean[index][self.selected_nuclides.index(nuclide)] = []
                        self.std[index][self.selected_nuclides.index(nuclide)] = []
                        for Energy in self.Checked_energies_Low:
                            Score0 = Score1[Score1['energy low [eV]'] == Energy]
                            self.mean[index][self.selected_nuclides.index(nuclide)] += list(Score0['mean'])
                            self.std[index][self.selected_nuclides.index(nuclide)] += list(Score0['std. dev.'])

    def Select_Mu(self, Filter_Index):
        all_bins = self.tally.filters[Filter_Index - 1].bins[:, 0]
        self.Checked_mu_Low = []
        self.Checked_mu_High = []
        self.Checked_Mu_Bins = []
        indices = self.Tallies[self.tally_id][self.filter_id]['Checked_bins']
        for index in indices:
            self.Checked_mu_Low.append(self.tally.filters[Filter_Index - 1].bins[:, 0][index - 2])
            self.Checked_mu_High.append(self.tally.filters[Filter_Index - 1].bins[:, 1][index - 2])
            self.Checked_Mu_Bins.append(self.tally.filters[Filter_Index - 1].bins[:][index - 2])
        print('Checked mu : ', self.Checked_Mu_Bins)

    def Mu_scores(self):
        df = self.df
        self.mean = {}
        self.std = {}
        if 'cell' not in self.df.keys()[:-2].tolist():
            self.Checked_cells = ['root']
        for nuclide in self.selected_nuclides:
            if nuclide != '':        
                for score in self.selected_score:
                    if score != '':
                        Score = df[df['score'] == score]

                        index = self.selected_score.index(score)
                        self.mean[index] = {}
                        self.std[index] = {}
                        Score1 = Score[Score['nuclide'] == nuclide]
                        self.mean[index][self.selected_nuclides.index(nuclide)] = []
                        self.std[index][self.selected_nuclides.index(nuclide)] = []
                        for Mu in self.Checked_mu_Low:
                            Score0 = Score1[Score1['mu low'] == Mu]
                            self.mean[index][self.selected_nuclides.index(nuclide)] += list(Score0['mean'])
                            self.std[index][self.selected_nuclides.index(nuclide)] += list(Score0['std. dev.'])

    def Select_Cells(self, Filter_Index):
        self.Checked_cells = []
        indices = self.Tallies[self.tally_id][self.filter_id]['Checked_bins']
        for index in indices:
            self.Checked_cells.append(self.tally.filters[Filter_Index - 1].bins[:][index - 2])
        print('Checked cells : ', self.Checked_cells)

    def Cell_scores(self):
        df = self.df
        self.mean = {}
        self.std = {}
        if len(self.selected_nuclides) == 0 or len(self.Checked_cells) == 0:
            self.showDialog('Warning', 'No cell or nuclide selected !')
            return

        for cell in self.Checked_cells:
            self.mean[cell] = {}
            self.std[cell] = {} 
            Score = df[df['cell'] == cell]
            for nuclide in self.selected_nuclides:
                if nuclide != '': 
                    self.mean[cell][nuclide] = {}
                    self.std[cell][nuclide] = {} 
                    Score1 = Score[Score['nuclide'] == nuclide]
                    for score in self.selected_score:
                        if score != '':
                            Score2 = Score1[Score1['score'] == score]
                            index = self.selected_score.index(score)
                            self.mean[cell][nuclide][index] = []
                            self.std[cell][nuclide][index] = []
                            self.mean[cell][nuclide][index] += list(Score2['mean'])   
                            self.std[cell][nuclide][index] += list(Score2['std. dev.'])   

    def Cell_scores1(self):
        df = self.df
        self.mean = {}
        self.std = {}
        for score in self.selected_score:
            if score != '':
                Score = df[df['score'] == score]
                for nuclide in self.selected_nuclides:
                    print('Cell      Energy       Mean         STD')
                    if nuclide != '':
                        index = self.selected_score.index(score)
                        self.mean[index] = []
                        self.std[index] = []
                        Score = Score[Score['nuclide'] == nuclide]

                        for cell in self.Checked_cells:
                            Score = Score[Score['cell'] == cell]
                            for Energy in self.Checked_energies_Low:
                                Score0 = Score[Score['energy low [eV]'] == Energy]
                                self.mean[index] += list(Score0['mean'])   
                                self.std[index] += list(Score0['std. dev.'])  
                                print(cell, Energy, self.mean[index], self.std[index])

    def Select_Surfaces(self, Filter_Index):
        #all_bins = self.tally.filters[Filter_Index - 1].bins[:]
        self.Checked_surfaces = []
        indices = self.Tallies[self.tally_id][self.filter_id]['Checked_bins']
        for index in indices:
            self.Checked_surfaces.append(self.tally.filters[Filter_Index - 1].bins[:][index - 2])
        self.Checked_surfaces.sort()
        print('Checked surfaces : ', self.Checked_surfaces)

    def Surface_scores(self):
        df = self.df
        self.mean = {}
        self.std = {}
        for score in self.selected_score:
            if score != '':
                Score = df[df['score'] == score]
                for nuclide in self.selected_nuclides:
                    if nuclide != '':
                        index = self.selected_score.index(score)
                        self.mean[index] = []
                        self.std[index] = []
                        Score = Score[Score['nuclide'] == nuclide]

                        for surface in self.Checked_surfaces:
                            Score0 = Score[Score['surface'] == surface]
                            self.mean[index] += list(Score0['mean'])   
                            self.std[index] += list(Score0['std. dev.'])   

    def Unfiltered_Scores(self):
        df = self.df
        self.mean = {}
        self.std = {}
        self.Checked_cells = ['root']
        self.mean['root'] = {}
        self.std['root'] = {}
        if len(self.selected_nuclides) == 0:
            self.showDialog('Warning', 'No nuclide selected !')
            return
        for nuclide in self.selected_nuclides:
            if nuclide != '': 
                self.mean['root'][nuclide] = {}
                self.std['root'][nuclide] = {} 
                for score in self.selected_score:
                    if score != '':
                        Score = df[df['nuclide'] == nuclide]
                        Score1 = Score[Score['score'] == score]
                        index = self.selected_score.index(score)
                        self.mean['root'][nuclide][index] = []
                        self.std['root'][nuclide][index] = []
                        self.mean['root'][nuclide][index] += list(Score1['mean'])   
                        self.std['root'][nuclide][index] += list(Score1['std. dev.'])   

    def Plot(self):
        if 'MeshFilter' in self.Filters_comboBox.currentText():
            self.Plot_Mesh()
        else:
            self.Plot_Score()
   
    def set_Scales(self):
        self.xLog_CB.setChecked(False)
        self.yLog_CB.setChecked(False)        
        if self.Graph_type_CB.currentIndex() == 0:
            self.xLog_CB.setEnabled(False)
            self.yLog_CB.setEnabled(False)
        else:
            self.yLog_CB.setEnabled(True)
            if self.Graph_type_CB.currentText() in ['Bar', 'Stacked Bars', 'Stacked Area']:
                self.xLog_CB.setEnabled(False)
            elif self.Plot_By_Key not in ['cell', 'surface', 'nuclide', 'score']:
                self.xLog_CB.setEnabled(True)

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

    def Plot_Score(self):
        #Plot tallies
        self.Stack_Plot = False
        if self.Graph_Layout_CB.currentText() != 'BoxPlot' and self.Graph_type_CB.currentIndex() == 0:
            self.showDialog('Warning', 'Select graph type first!')
            return
        Graph_type = self.Graph_type_CB.currentText()
        if 'EnergyFilter' in self.Filters_comboBox.currentText():
            if Graph_type in ['Bar', 'Stacked Bars', 'Stacked Area']:
                Checked_bins = ['{:.1E}'.format(item[0]) + ' to ' + '{:.1E}'.format(item[1]) for item in self.Checked_Energy_Bins]
            else:
                if self.Plot_by_CB.currentText() == 'energy low [eV]':
                    Checked_bins = self.Checked_energies_Low
                elif self.Plot_by_CB.currentText() == 'energy high [eV]':
                    Checked_bins = self.Checked_energies_High
            if self.Plot_by_CB.currentText() in ['energy low [eV]', 'energy high [eV]']:
                X_ = np.arange(len(Checked_bins))
            elif self.Plot_by_CB.currentText() == 'nuclide':
                X_ = np.arange(len(self.selected_nuclides))
                Checked_bins = self.selected_nuclides
            elif self.Plot_by_CB.currentText() == 'score':
                X_ = np.arange(len(self.selected_score))
                Checked_bins = self.selected_score  
            self.Checked_Filter_Type = 'EnergyFilter'
        elif 'MuFilter' in self.Filters_comboBox.currentText():
            if Graph_type in ['Bar', 'Stacked Bars', 'Stacked Area']:
                Checked_bins = ['{:.1E}'.format(item[0]) + ' to ' + '{:.1E}'.format(item[1]) for item in self.Checked_Mu_Bins]
            else:
                if self.Plot_by_CB.currentText() == 'mu low':
                    Checked_bins = self.Checked_mu_Low
                elif self.Plot_by_CB.currentText() == 'mu high':
                    Checked_bins = self.Checked_mu_High
            if self.Plot_by_CB.currentText() in ['mu low', 'mu high']:
                X_ = np.arange(len(Checked_bins))
            elif self.Plot_by_CB.currentText() == 'nuclide':
                X_ = np.arange(len(self.selected_nuclides))
                Checked_bins = self.selected_nuclides
            elif self.Plot_by_CB.currentText() == 'score':
                X_ = np.arange(len(self.selected_score))
                Checked_bins = self.selected_score              
            self.Checked_Filter_Type = 'MuFilter'
        elif 'CellFilter' in self.Filters_comboBox.currentText():
            self.Checked_Filter_Type = 'CellFilter'
            if self.Plot_by_CB.currentText() == 'cell':
                X_ = np.arange(len(self.Checked_cells))
                Checked_bins = self.Checked_cells
            elif self.Plot_by_CB.currentText() == 'nuclide':
                X_ = np.arange(len(self.selected_nuclides))
                Checked_bins = self.selected_nuclides
            elif self.Plot_by_CB.currentText() == 'score':
                X_ = np.arange(len(self.selected_score))
                Checked_bins = self.selected_score        
        elif 'SurfaceFilter' in self.Filters_comboBox.currentText():
            self.Checked_Filter_Type = 'SurfaceFilter'
            if self.Plot_by_CB.currentText() == 'surface':
                X_ = np.arange(len(self.Checked_surfaces))
                Checked_bins = self.Checked_surfaces
            elif self.Plot_by_CB.currentText() == 'score':
                X_ = np.arange(len(self.selected_score))
                Checked_bins = self.selected_score 
        if self.filter_id == 0:
            if self.Plot_by_CB.currentText() == 'nuclide':
                X_ = np.arange(len(self.selected_nuclides))
                Checked_bins = self.selected_nuclides
                self.Checked_Filter_Type = 'Nuclide'
            elif self.Plot_by_CB.currentText() == 'score':
                X_ = np.arange(len(self.selected_score))
                Checked_bins = self.selected_score
                self.Checked_Filter_Type = 'Score'
        try:
            self.x = Checked_bins
        except:
            if self.filter_id != 0:
                self.showDialog('Warning', 'Select filter bins first or press select button again!')
            return

        if self.Graph_Layout_CB.currentIndex() == 0:
            self.showDialog('Warning', 'Select graph type first !')
        else:
            if self.Graph_Layout_CB.currentText() == 'Multiple curves':        # Multiple curves
                self.Multiple_Curves(X_)
                self.Stack_Plot = False
            elif self.Graph_Layout_CB.currentText() == 'Stacking subplots':    # Stacking subplots
                #if len(self.selected_score) > 1:                               # needs more than one score
                if self.filter_id == 0:
                    self.Stack_Plot = False
                    self.Multiple_Curves(X_)                    
                else:
                    self.Stack_Plot = True
                    self.Stacking_plot_Curves(X_)
            elif self.Graph_Layout_CB.currentText() == 'BoxPlot':               # Box Plots
                self.box_plot()
                self.Stack_Plot = False

    def Multiple_Curves(self, X_):
        if 'CellFilter' in self.Filters_comboBox.currentText() or self.n_filters == 0:
            ax = ['']*len(self.Checked_cells)*len(self.selected_nuclides)
        elif 'SurfaceFilter' in self.Filters_comboBox.currentText():
            ax = ['']*len(self.Checked_surfaces)*len(self.selected_score)        
        elif 'EnergyFilter' in self.Filters_comboBox.currentText():
            ax = ['']*len(self.Checked_energies_Low)*len(self.selected_nuclides)         
        elif 'MuFilter' in self.Filters_comboBox.currentText():
            ax = ['']*len(self.Checked_mu_Low)*len(self.selected_nuclides) 

        if self.Plot_By_Key == 'nuclide':  
            self.Plot_By_Nuclide(ax, X_)
        elif self.Plot_By_Key == 'cell':
            self.Plot_By_Cell(ax, X_)
        elif self.Plot_By_Key == 'surface':
            self.Plot_By_Surface(ax, X_)
        elif self.Plot_By_Key in ['energy low [eV]', 'energy high [eV]']:
            self.Plot_By_Energy(ax, X_)
        elif self.Plot_By_Key in ['mu low', 'mu high']:
            self.Plot_By_Mu(ax, X_)
        elif self.Plot_By_Key == 'score':  
            self.Plot_By_Score(ax, X_)
        if not self.Stack_Plot:
            plt.show()

    def Stacking_plot_Curves(self, X_):
        if self.row_SB.value() * self.col_SB.value() < 2:
            self.showDialog('Warning', 'Stacking plots need more rows and/or columns !')
            return        
        if self.Plot_by_CB.currentText() in ['cell', 'energy low [eV]', 'energy high [eV]', 'mu low', 'mu high'] and len(self.selected_nuclides) == 1:
            self.Stack_Plot = False
            self.Multiple_Curves(X_) 
            return 
        elif self.Plot_by_CB.currentText() == 'surface' and len(self.selected_score) == 1:
            self.Stack_Plot = False
            self.Multiple_Curves(X_) 
            return 

        fig, axs = plt.subplots(self.row_SB.value(), self.col_SB.value(), layout="constrained")   #, sharex=True)

        if 'CellFilter' in self.Filters_comboBox.currentText() or self.n_filters == 0:
            #Size = len(self.Checked_cells)*len(self.selected_nuclides)
            if self.Plot_By_Nuclide or self.Plot_By_Score:
                Size = len(self.Checked_cells)
            elif self.Plot_By_Cell:
                Size = len(self.selected_nuclides)
        elif 'SurfaceFilter' in self.Filters_comboBox.currentText():
            if self.Plot_By_Score:
                Size = len(self.Checked_surfaces)
            elif self.Plot_By_Surface:
                Size = len(self.selected_score)
        elif 'EnergyFilter' in self.Filters_comboBox.currentText():           
            #Size = len(self.Checked_energies_Low)*len(self.selected_nuclides)    
            if self.Plot_By_Nuclide or self.Plot_By_Score:
                Size = len(self.Checked_energies_Low)
            elif self.Plot_By_Energy:
                Size = len(self.selected_nuclides)   
        elif 'MuFilter' in self.Filters_comboBox.currentText():
            #Size = len(self.Checked_mu_Low)*len(self.selected_nuclides) 
            if self.Plot_By_Nuclide or self.Plot_By_Score:
                Size = len(self.Checked_mu_Low)
            elif self.Plot_By_Mu:
                Size = len(self.selected_nuclides)     
        if Size < self.row_SB.value()*self.col_SB.value():
            ax = ['']*self.row_SB.value()*self.col_SB.value()
        else:    
            ax = [''] * Size            
        
        for i, ax_ in enumerate(axs.flat):
            ax[i] = ax_

        if self.Plot_By_Key == 'nuclide':  
            self.Plot_By_Nuclide(ax, X_)
        elif self.Plot_By_Key == 'cell':
            self.Plot_By_Cell(ax, X_)
        elif self.Plot_By_Key == 'surface':
            self.Plot_By_Surface(ax, X_)
        elif self.Plot_By_Key in ['energy low [eV]', 'energy high [eV]']:
            self.Plot_By_Energy(ax, X_)
        elif self.Plot_By_Key in ['mu low', 'mu high']:
            self.Plot_By_Mu(ax, X_)
        elif self.Plot_By_Key == 'score':  
            self.Plot_By_Score(ax, X_)
        plt.show()

    def Plot_By_Nuclide(self, ax, X_): 
        Graph_type = self.Graph_type_CB.currentText()
        Width = 0.15 #/ len(self.selected_score)
        X_Shift = Width * 0.5 * (len(self.selected_score) - 1)

        if 'cell' in self.df.keys().tolist():
            Checked_bins = self.Checked_cells
            Bins_For_Title = self.Checked_cells
            BIN = ' in cell '
            UNIT = ''
        elif 'energy low [eV]' in self.df.keys():  #.tolist():
            Checked_bins = self.Checked_energies_Low
            Bins_For_Title = [(self.Checked_energies_Low[i], self.Checked_energies_High[i],) for i in range(len(Checked_bins))]
            BIN = ' energy '
            UNIT = ' eV'
        elif 'mu low' in self.df.keys():  #.tolist():
            Checked_bins = self.Checked_mu_Low
            Bins_For_Title = [(self.Checked_mu_Low[i], self.Checked_mu_High[i],) for i in range(len(Checked_bins))]
            BIN = ' mu '
            UNIT = ''
        elif 'surface' in self.df.keys():   #.tolist():
            Checked_bins = self.Checked_surfaces
            Bins_For_Title = self.Checked_surfaces
            BIN = ' at surface '
            UNIT = ''
        else:
            Checked_bins = self.Checked_cells
            Bins_For_Title = self.Checked_cells
            BIN = ' cell '
            UNIT = ''
        Stack_Size = self.row_SB.value()*self.col_SB.value()

        for i in range(len(Checked_bins)): 
            bin = Checked_bins[i]
            if not self.Stack_Plot:
                fig, ax[i] = plt.subplots()
            else:
                if i > Stack_Size - 1:
                    self.showDialog('Warning', 'Stack size less than requiered plots! \nLast plots will be removed!')
                    break
            xs_ = []; y_ = {}; y_err = {}  
            for score in self.selected_score:
                y_[score] = []; y_err[score] = []
            for nuclide in self.selected_nuclides: 
                nucl_idx = self.selected_nuclides.index(nuclide)
                y_error = []; ys_ = []; ys_err = []
                X = self.selected_nuclides.index(nuclide)   # + offset0
                multiplier = 0
                xs_.append(X)                
                for score in self.selected_score:
                    index = self.selected_score.index(score)
                    if Graph_type == 'Bar':
                        offset = Width * multiplier
                        X += offset
                    x = X 
                    multiplier = 1   
                    if 'cell' in self.df.keys():  #.tolist():
                        y = self.df[self.df.cell == bin][self.df.nuclide == nuclide][self.df.score == score]['mean'].values.tolist()
                        y_error = self.df[self.df.cell == bin][self.df.nuclide == nuclide][self.df.score == score]['std. dev.'].values.tolist()
                    elif 'surface' in self.df.keys().tolist():
                        y = self.df[self.df.surface == bin][self.df.nuclide == nuclide][self.df.score == score]['mean'].values.tolist()
                        y_error = self.df[self.df.surface == bin][self.df.nuclide == nuclide][self.df.score == score]['std. dev.'].values.tolist()
                    elif 'energy low [eV]' in self.df.keys().tolist():
                        y = self.df[self.df['energy low [eV]'] == bin][self.df.nuclide == nuclide][self.df.score == score]['mean'].values.tolist()
                        y_error = self.df[self.df['energy low [eV]'] == bin][self.df.nuclide == nuclide][self.df.score == score]['std. dev.'].values.tolist()
                    elif 'energy high [eV]' in self.df.keys().tolist():
                        y = self.df[self.df['energy high [eV]'] == bin][self.df.nuclide == nuclide][self.df.score == score]['mean'].values.tolist()
                        y_error = self.df[self.df['energy low [eV]'] == bin][self.df.nuclide == nuclide][self.df.score == score]['std. dev.'].values.tolist()
                    elif 'mu low' in self.df.keys().tolist():
                        y = self.df[self.df['mu low'] == bin][self.df.nuclide == nuclide][self.df.score == score]['mean'].values.tolist()
                        y_error = self.df[self.df['mu low'] == bin][self.df.nuclide == nuclide][self.df.score == score]['std. dev.'].values.tolist()   
                    elif 'mu high' in self.df.keys().tolist():
                        y = self.df[self.df['mu high'] == bin][self.df.nuclide == nuclide][self.df.score == score]['mean'].values.tolist()
                        y_error = self.df[self.df['mu high'] == bin][self.df.nuclide == nuclide][self.df.score == score]['std. dev.'].values.tolist()   
                    else:    
                        y = self.df[self.df.nuclide == nuclide][self.df.score == score]['mean'].values.tolist()
                        y_error = self.df[self.df.nuclide == nuclide][self.df.score == score]['std. dev.'].values.tolist()
                    
                    y_[score].append(y[0])
                    y_err[score].append(y_error[0])
                    ys_.append(y_[score])
                    ys_err.append(y_err[score]) 

                    Label = score if nucl_idx == 0 else None
                    if Graph_type in ['Bar', 'Scatter']:
                        if Graph_type == 'Bar':
                            ax[i].bar(x, y, width=Width, label=Label)
                        elif Graph_type == 'Scatter':
                            ax[i].scatter(x, y, marker='^', label = Label)
                        if self.Add_error_bars_CB.isChecked():
                            ax[i].errorbar(x, y, np.array(y_error)*100, ecolor='black')
                ax[i].set_prop_cycle(None)
                #plt.gca().set_prop_cycle(None)

            if Graph_type == 'Stacked Bars':
                Bottom = np.zeros(len(self.selected_nuclides))
                for score in self.selected_score:
                    Label = score if len(self.selected_score) > 1 else None
                    j = self.selected_score.index(score)
                    if self.Add_error_bars_CB.isChecked():
                        ax[i].bar(np.array(xs_) + X_Shift, ys_[j], yerr = np.array(ys_err[j])*100, bottom = Bottom, label = Label)
                    else:
                        ax[i].bar(np.array(xs_) + X_Shift, ys_[j], bottom = Bottom, label = Label)
                    Bottom += ys_[j]
            elif Graph_type == 'Stacked Area':
                ax[i].stackplot(np.array(xs_) + X_Shift, ys_[:len(self.selected_score)], labels = self.selected_score)
                if self.Add_error_bars_CB.isChecked():
                    Bottom = np.zeros(len(self.selected_nuclides))
                    for j in range(len(self.selected_score)):
                        ax[i].errorbar(np.array(xs_) + X_Shift, ys_[j] + Bottom, np.array(ys_err[j])*100, fmt = '|', ecolor='black')
                        Bottom += ys_[j]     
            
            if len(self.selected_score) > 1: 
                    ax[i].legend()

            ax[i].set_xlabel(self.Curve_xLabel.text())
            ax[i].set_ylabel(self.Curve_yLabel.text())            
            ax[i].set_title(self.Curve_title.text() + BIN + str(Bins_For_Title[i]) + UNIT)

            if Graph_type in ['Stacked Area', 'Stacked Bars', 'Bar']:  
                ax[i].set_xticks(X_ + X_Shift, self.x)
            else:
                ax[i].set_xticks(X_, self.x)

            self.Change_Scales(ax[i], Graph_type)
            
            if len(self.selected_score) > 1: 
                ax[i].legend()

            self.Labels_Font(ax[i], plt)
            if self.grid:
                ax[i].grid(visible=self.grid, which=self.which_grid, axis=self.which_axis)
            else:
                ax[i].grid(False)   

        if self.Stack_Plot: 
            if Stack_Size > len(Checked_bins):
                for i in range(len(Checked_bins), self.row_SB.value()*self.col_SB.value()):
                    ax[i].set_visible(False)        # to remove empty plots

        plt.subplots_adjust(left=0.18, right=0.98, top=0.92, bottom=0.12)
        plt.tight_layout()

    def Plot_By_Cell(self, ax, X_):    
        Graph_type = self.Graph_type_CB.currentText()
        Width = 0.15 #/ len(self.selected_score)
        X_Shift = Width * 0.5 * (len(self.selected_score) - 1)
        Stack_Size = self.row_SB.value()*self.col_SB.value()

        for i in range(len(self.selected_nuclides)):
            nuclide = self.selected_nuclides[i]
            if not self.Stack_Plot:
                fig, ax[i] = plt.subplots()
            else:
                if i > Stack_Size - 1:
                    self.showDialog('Warning', 'Stack size less than requiered plots! \nLast plots will be removed!')
                    break
            xs_ = []; y_ = {}; y_err = {}  
            for score in self.selected_score:
                y_[score] = []; y_err[score] = []
            for cell in self.Checked_cells: 
                cell_idx = self.Checked_cells.index(cell)
                y_error = []; ys_ = []; ys_err = []
                X = self.Checked_cells.index(cell)    # + offset0
                multiplier = 0
                xs_.append(X)
                for score in self.selected_score:
                    index = self.selected_score.index(score)
                    if Graph_type == 'Bar':
                        offset = Width * multiplier
                        X += offset
                    x = X 
                    multiplier = 1   
                    if 'nuclide' in self.df.keys()[:-2].tolist():
                        y = self.df[self.df.nuclide == nuclide][self.df.cell == cell][self.df.score == score]['mean'].values.tolist()
                        y_error = self.df[self.df.nuclide == nuclide][self.df.cell == cell][self.df.score == score]['std. dev.'].values.tolist()
                    else:    
                        y = self.df[self.df.cell == cell][self.df.score == score]['mean'].values.tolist()
                        y_error = self.df[self.df.cell == cell][self.df.score == score]['std. dev.'].values.tolist()
                
                    y_[score].append(y[0])
                    y_err[score].append(y_error[0])
                    ys_.append(y_[score])
                    ys_err.append(y_err[score])

                    Label = score if cell_idx == 0 else None
                    if Graph_type in ['Bar', 'Scatter']:
                        if Graph_type == 'Bar':
                            ax[i].bar(x, y, width=Width, label=Label)
                    
                        elif Graph_type == 'Scatter':
                            ax[i].scatter(x, y, marker='^', label = Label)
                            
                        if self.Add_error_bars_CB.isChecked():
                            ax[i].errorbar(x, y, np.array(y_error)*100, fmt='|', ecolor='black') 
                ax[i].set_prop_cycle(None)
                #plt.gca().set_prop_cycle(None)
                    
            if Graph_type == 'Stacked Bars':
                Bottom = np.zeros(len(self.Checked_cells))
                for score in self.selected_score:
                    Label = score if len(self.selected_score) > 1 else None
                    j = self.selected_score.index(score)
                    if self.Add_error_bars_CB.isChecked():
                        ax[i].bar(np.array(xs_) + X_Shift, ys_[j], yerr = np.array(ys_err[j])*100, bottom = Bottom, label = Label)
                    else:
                        ax[i].bar(np.array(xs_) + X_Shift, ys_[j], bottom = Bottom, label = Label)
                    Bottom += ys_[j]  
            elif Graph_type == 'Stacked Area':
                ax[i].stackplot(np.array(xs_) + X_Shift, ys_[:len(self.selected_score)], labels = self.selected_score)
                if self.Add_error_bars_CB.isChecked():
                    Bottom = np.zeros(len(self.Checked_cells))
                    for j in range(len(self.selected_score)):
                        ax[i].errorbar(np.array(xs_) + X_Shift, ys_[j] + Bottom, np.array(ys_err[j])*100, fmt = '|', ecolor='black')
                        Bottom += ys_[j]

            ax[i].set_title(self.Curve_title.text() + ' nuclide ' + str(nuclide))
            ax[i].set_xlabel(self.Curve_xLabel.text())
            ax[i].set_ylabel(self.Curve_yLabel.text())

            if Graph_type in ['Stacked Area', 'Stacked Bars', 'Bar']:  
                ax[i].set_xticks(X_ + X_Shift, self.x)
            else:
                ax[i].set_xticks(X_, self.x)
          
            self.Change_Scales(ax[i], Graph_type)

            if len(self.selected_score) > 1: 
                ax[i].legend()   
            if self.grid:
                ax[i].grid(visible=self.grid, which=self.which_grid, axis=self.which_axis)
            else:
                ax[i].grid(False)
            self.Labels_Font(ax[i], plt)
                
        if self.Stack_Plot: 
            if Stack_Size > len(self.selected_nuclides):
                for i in range(len(self.selected_nuclides), self.row_SB.value()*self.col_SB.value()):
                    ax[i].set_visible(False)        # to remove empty plots
 
        plt.subplots_adjust(left=0.18, right=0.98, top=0.92, bottom=0.12)
        plt.tight_layout()

    def Plot_By_Surface(self, ax, X_):    
        Graph_type = self.Graph_type_CB.currentText()
        Width = 0.15 #/ len(self.selected_score)
        X_Shift = Width * 0.5 * (len(self.selected_score) - 1)    
        Stack_Size = self.row_SB.value()*self.col_SB.value()
   
        for i in range(len(self.selected_nuclides)):
            nuclide = self.selected_nuclides[i]
            if not self.Stack_Plot:
                fig, ax[i] = plt.subplots()
            xs_ = []; y_ = {}; y_err = {}  
            for score in self.selected_score:
                y_[score] = []; y_err[score] = []
            for surface in self.Checked_surfaces: 
                surface_idx = self.Checked_surfaces.index(surface)
                y_error = []; ys_ = []; ys_err = []
                X = self.Checked_surfaces.index(surface)    # + offset0
                multiplier = 0
                xs_.append(X)
                for score in self.selected_score:
                    index = self.selected_score.index(score)
                    if Graph_type == 'Bar':
                        offset = Width * multiplier
                        X += offset
                    x = X 
                    multiplier = 1   

                    if 'nuclide' in self.df.keys()[:-2].tolist():
                        y = self.df[self.df.nuclide == nuclide][self.df.surface == surface][self.df.score == score]['mean'].values.tolist()
                        y_error = self.df[self.df.nuclide == nuclide][self.df.surface == surface][self.df.score == score]['std. dev.'].values.tolist()
                    else:    
                        y = self.df[self.df.surface == surface][self.df.score == score]['mean'].values.tolist()
                        y_error = self.df[self.df.surface == surface][self.df.score == score]['std. dev.'].values.tolist()
                    y_[score].append(y[0])
                    y_err[score].append(y_error[0])
                    ys_.append(y_[score])
                    ys_err.append(y_err[score])

                    Label = score if surface_idx == 0 else None
                    if Graph_type in ['Bar', 'Scatter']:
                        if Graph_type == 'Bar':
                            ax[i].bar(x, y, width=Width, label=Label)
                    
                        elif Graph_type == 'Scatter':
                            ax[i].scatter(x, y, marker='^', label = Label)
                            
                        if self.Add_error_bars_CB.isChecked():
                            ax[i].errorbar(x, y, np.array(y_error)*100, fmt='|', ecolor='black') 
                ax[i].set_prop_cycle(None)
                #plt.gca().set_prop_cycle(None)
                    
            if Graph_type == 'Stacked Bars':
                Bottom = np.zeros(len(self.Checked_surfaces))
                for score in self.selected_score:
                    Label = score if len(self.selected_score) > 1 else None
                    j = self.selected_score.index(score)
                    if self.Add_error_bars_CB.isChecked():
                        ax[i].bar(np.array(xs_) + X_Shift, ys_[j], yerr = np.array(ys_err[j])*100, bottom = Bottom, label = Label)
                    else:
                        ax[i].bar(np.array(xs_) + X_Shift, ys_[j], bottom = Bottom, label = Label)
                    Bottom += ys_[j]  
            elif Graph_type == 'Stacked Area':
                ax[i].stackplot(np.array(xs_) + X_Shift, ys_[:len(self.selected_score)], labels = self.selected_score)
                if self.Add_error_bars_CB.isChecked():
                    Bottom = np.zeros(len(self.Checked_surfaces))
                    for j in range(len(self.selected_score)):
                        ax[i].errorbar(np.array(xs_) + X_Shift, ys_[j] + Bottom, np.array(ys_err[j])*100, fmt = '|', ecolor='black')
                        Bottom += ys_[j]

            ax[i].set_title(self.Curve_title.text())
            ax[i].set_xlabel(self.Curve_xLabel.text())
            ax[i].set_ylabel(self.Curve_yLabel.text())

            if Graph_type in ['Stacked Area', 'Stacked Bars', 'Bar']:  
                ax[i].set_xticks(X_ + X_Shift, self.x)
            else:
                ax[i].set_xticks(X_, self.x)
          
            self.Change_Scales(ax[i], Graph_type)
            if len(self.selected_score) > 1: 
                ax[i].legend()   
            if self.grid:
                ax[i].grid(visible=self.grid, which=self.which_grid, axis=self.which_axis)
            else:
                ax[i].grid(False)
            self.Labels_Font(ax[i], plt)

        if self.Stack_Plot: 
            if Stack_Size > len(self.selected_nuclides):
                for i in range(len(self.selected_nuclides), self.row_SB.value()*self.col_SB.value()):
                    ax[i].set_visible(False)        # to remove empty plots

        plt.subplots_adjust(left=0.18, right=0.98, top=0.92, bottom=0.12)
        plt.tight_layout()

    def Plot_By_Energy(self, ax, X_):
        Graph_type = self.Graph_type_CB.currentText()
        Width = 0.15 #/ len(self.selected_score)
        X_Shift = Width * 0.5 * (len(self.selected_score) - 1)
        if self.Plot_By_Key == 'energy low [eV]':
            self.Checked_energies = self.Checked_energies_Low
            Energy_Key = 'energy low [eV]'
        elif self.Plot_By_Key  == 'energy high [eV]':
            self.Checked_energies = self.Checked_energies_High
            Energy_Key = 'energy high [eV]'
        x_Lin = self.Checked_energies
        Stack_Size = self.row_SB.value()*self.col_SB.value()

        for i in range(len(self.selected_nuclides)):
            nuclide = self.selected_nuclides[i]
            if not self.Stack_Plot:
                fig, ax[i] = plt.subplots()
            else:
                if i > Stack_Size - 1:
                    self.showDialog('Warning', 'Stack size less than requiered plots! \nLast plots will be removed!')
                    break
            xs_ = []; y_ = {}; y_err = {}  
            for score in self.selected_score:
                y_[score] = []; y_err[score] = []
            for energy in self.Checked_energies: 
                energy_idx = self.Checked_energies.index(energy)
                y_error = []; ys_ = []; ys_err = []
                X = self.Checked_energies.index(energy)    # + offset0
                multiplier = 0
                xs_.append(X)
                for score in self.selected_score:
                    index = self.selected_score.index(score)
                    if Graph_type == 'Bar':
                        offset = Width * multiplier 
                        X += offset
                    x = X 
                    multiplier = 1   
                    if 'nuclide' in self.df.keys()[:-2].tolist():
                        y = self.df[self.df.nuclide == nuclide][self.df[Energy_Key] == energy][self.df.score == score]['mean'].values.tolist()
                        y_error = self.df[self.df.nuclide == nuclide][self.df[Energy_Key] == energy][self.df.score == score]['std. dev.'].values.tolist()
                    else:    
                        y = self.df[self.df[Energy_Key] == energy][self.df.score == score]['mean'].values.tolist()
                        y_error = self.df[self.df[Energy_Key] == energy][self.df.score == score]['std. dev.'].values.tolist()
                    
                    y_[score].append(y[0])
                    y_err[score].append(y_error[0])
                    ys_.append(y_[score])
                    ys_err.append(y_err[score])                    
                    
                    if Graph_type == 'Bar':
                        Label = score if energy_idx == 0 else None
                        ax[i].bar(x, y, width=Width, label=Label)
                        if self.Add_error_bars_CB.isChecked():
                            ax[i].errorbar(x, y, y_error, fmt='|', ecolor='black')
                ax[i].set_prop_cycle(None)
                #plt.gca().set_prop_cycle(None)

            if Graph_type in ['Lin-Lin', 'Scatter', 'Stairs']:
                for score in self.selected_score:
                    if len(self.selected_score) > 1:
                        Label = score
                    else:
                        Label = None
                    j = self.selected_score.index(score)
                    if Graph_type == 'Lin-Lin':
                        if score == 'flux':    
                            ax[i].plot(x_Lin, ys_[j], label = Label, drawstyle='steps-mid')
                        else:
                            ax[i].plot(x_Lin, ys_[j], label = Label)
                    elif Graph_type == 'Scatter':
                        ax[i].scatter(x_Lin, ys_[j], marker='^', label = Label)
                    elif Graph_type == 'Stairs':
                        edges = [self.Checked_energies_Low[0]]
                        edges.extend(self.Checked_energies_High)
                        ax[i].stairs(ys_[j], edges, label = Label)
                    if self.Add_error_bars_CB.isChecked():
                        ax[i].errorbar(x_Lin, ys_[j], ys_err[j], fmt='|', ecolor='black')
            elif Graph_type == 'Stacked Bars':
                Bottom = np.zeros(len(self.Checked_energies))
                for score in self.selected_score:
                    Label = score if len(self.selected_score) > 1 else None           
                    j = self.selected_score.index(score)
                    if self.Add_error_bars_CB.isChecked():
                        ax[i].bar(np.array(xs_) + X_Shift, ys_[j], yerr=np.array(ys_err[j]), bottom=Bottom, label=Label)
                    else:
                        ax[i].bar(np.array(xs_) + X_Shift, ys_[j], bottom = Bottom, label = Label)
                    Bottom += ys_[j]            
            elif Graph_type == 'Stacked Area':
                ax[i].stackplot(np.array(xs_) + X_Shift, ys_[:len(self.selected_score)], labels = self.selected_score)
                if self.Add_error_bars_CB.isChecked():
                    Bottom = np.zeros(len(self.Checked_energies))
                    for j in range(len(self.selected_score)):
                        ax[i].errorbar(np.array(xs_) + X_Shift, ys_[j] + Bottom, np.array(ys_err[j]), fmt = '|', ecolor='black')
                        Bottom += ys_[j]

            ax[i].set_title(self.Curve_title.text() + ' nuclide ' + str(nuclide))
            ax[i].set_xlabel(self.Curve_xLabel.text())
            ax[i].set_ylabel(self.Curve_yLabel.text())

            if Graph_type in ['Stacked Area', 'Stacked Bars', 'Bar']:  
                ax[i].set_xticks(X_ + X_Shift, self.x)
                
            self.Change_Scales(ax[i], Graph_type)
            
            if len(self.selected_score) > 1: 
                ax[i].legend()

            if self.grid:
                ax[i].grid(visible=self.grid, which=self.which_grid, axis=self.which_axis)
            else:
                ax[i].grid(False)            
            self.Labels_Font(ax[i], plt)
                    
        if self.Stack_Plot: 
            if Stack_Size > len(self.selected_nuclides):
                for i in range(len(self.selected_nuclides), self.row_SB.value()*self.col_SB.value()):
                    ax[i].set_visible(False)        # to remove empty plots

        plt.subplots_adjust(left=0.18, right=0.98, top=0.92, bottom=0.12)
        plt.tight_layout()

    def Plot_By_Mu(self, ax, X_):
        Graph_type = self.Graph_type_CB.currentText()
        Width = 0.15 
        X_Shift = Width * 0.5 * (len(self.selected_score) - 1)
        if self.Plot_By_Key == 'mu low':
            self.Checked_mu = self.Checked_mu_Low
            Mu_Key = 'mu low'
        elif self.Plot_By_Key  == 'mu high':
            self.Checked_mu = self.Checked_mu_High
            Mu_Key = 'mu high'
        x_Lin = self.Checked_mu
        Stack_Size = self.row_SB.value()*self.col_SB.value()

        for i in range(len(self.selected_nuclides)):
            nuclide = self.selected_nuclides[i]
            if not self.Stack_Plot:
                fig, ax[i] = plt.subplots()
            else:
                if i > Stack_Size - 1:
                    self.showDialog('Warning', 'Stack size less than requiered plots! \nLast plots will be removed!')
                    break
            xs_ = []; y_ = {}; y_err = {}  
            for score in self.selected_score:
                y_[score] = []; y_err[score] = []
            for mu in self.Checked_mu: 
                mu_idx = self.Checked_mu.index(mu)
                y_error = []; ys_ = []; ys_err = []
                X = self.Checked_mu.index(mu)    # + offset0
                multiplier = 0
                xs_.append(X)
                for score in self.selected_score:
                    index = self.selected_score.index(score)
                    if Graph_type == 'Bar':
                        offset = Width * multiplier 
                        X += offset
                    x = X 
                    multiplier = 1   
                    if 'nuclide' in self.df.keys()[:-2].tolist():
                        y = self.df[self.df.nuclide == nuclide][self.df[Mu_Key] == mu][self.df.score == score]['mean'].values.tolist()
                        y_error = self.df[self.df.nuclide == nuclide][self.df[Mu_Key] == mu][self.df.score == score]['std. dev.'].values.tolist()
                    else:    
                        y = self.df[self.df[Mu_Key] == mu][self.df.score == score]['mean'].values.tolist()
                        y_error = self.df[self.df[Mu_Key] == mu][self.df.score == score]['std. dev.'].values.tolist()
                    
                    y_[score].append(y[0])
                    y_err[score].append(y_error[0])
                    ys_.append(y_[score])
                    ys_err.append(y_err[score])                    
                    
                    if Graph_type == 'Bar':
                        Label = score if mu_idx == 0 else None
                        ax[i].bar(x, y, width=Width, label=Label)
                        if self.Add_error_bars_CB.isChecked():
                            ax[i].errorbar(x, y, y_error, fmt='|', ecolor='black')
                ax[i].set_prop_cycle(None)
                #plt.gca().set_prop_cycle(None)

            if Graph_type in ['Lin-Lin', 'Scatter', 'Stairs']:
                for score in self.selected_score:
                    if len(self.selected_score) > 1:
                        Label = score
                    else:
                        Label = None
                    j = self.selected_score.index(score)
                    if Graph_type == 'Lin-Lin':
                        if score == 'flux':    
                            ax[i].plot(x_Lin, ys_[j], label = Label, drawstyle='steps-mid')
                        else:
                            ax[i].plot(x_Lin, ys_[j], label = Label)
                    elif Graph_type == 'Scatter':
                        ax[i].scatter(x_Lin, ys_[j], marker='^', label = Label)
                    elif Graph_type == 'Stairs':
                        edges = [self.Checked_mu_Low[0]]
                        edges.extend(self.Checked_mu_High)
                        ax[i].stairs(ys_[j], edges, label = Label)

                    if self.Add_error_bars_CB.isChecked():
                        ax[i].errorbar(x_Lin, ys_[j], ys_err[j], fmt='|', ecolor='black')
            elif Graph_type == 'Stacked Bars':
                Bottom = np.zeros(len(self.Checked_mu))
                for score in self.selected_score:
                    Label = score if len(self.selected_score) > 1 else None           
                    j = self.selected_score.index(score)
                    if self.Add_error_bars_CB.isChecked():
                        ax[i].bar(np.array(xs_) + X_Shift, ys_[j], yerr=np.array(ys_err[j]), bottom=Bottom, label=Label)
                    else:
                        ax[i].bar(np.array(xs_) + X_Shift, ys_[j], bottom = Bottom, label = Label)
                    Bottom += ys_[j]            
            elif Graph_type == 'Stacked Area':
                ax[i].stackplot(np.array(xs_) + X_Shift, ys_[:len(self.selected_score)], labels = self.selected_score)
                if self.Add_error_bars_CB.isChecked():
                    Bottom = np.zeros(len(self.Checked_mu))
                    for j in range(len(self.selected_score)):
                        ax[i].errorbar(np.array(xs_) + X_Shift, ys_[j] + Bottom, np.array(ys_err[j]), fmt = '|', ecolor='black')
                        Bottom += ys_[j]

            if score in ['flux', 'current']:
                ax[i].set_title(self.Curve_title.text())
            else:
                ax[i].set_title(self.Curve_title.text() + ' nuclide ' + str(nuclide))
            ax[i].set_xlabel(self.Curve_xLabel.text())
            ax[i].set_ylabel(self.Curve_yLabel.text())

            if Graph_type in ['Stacked Area', 'Stacked Bars', 'Bar']:  
                ax[i].set_xticks(X_ + X_Shift, self.x)
                
            self.Change_Scales(ax[i], Graph_type)

            if len(self.selected_score) > 1: 
                ax[i].legend()
            if self.grid:
                ax[i].grid(visible=self.grid, which=self.which_grid, axis=self.which_axis)
            else:
                ax[i].grid(False)
            self.Labels_Font(ax[i], plt)
        
        if self.Stack_Plot: 
            if Stack_Size > len(self.selected_nuclides):
                for i in range(len(self.selected_nuclides), self.row_SB.value()*self.col_SB.value()):
                    ax[i].set_visible(False)        # to remove empty plots

        plt.subplots_adjust(left=0.18, right=0.98, top=0.92, bottom=0.12)
        plt.tight_layout()

    def Plot_By_Score(self, ax, X_):   
        Graph_type = self.Graph_type_CB.currentText()
        Width = 0.15 #/ len(self.selected_score)
        X_Shift = Width * 0.5 * (len(self.selected_nuclides) - 1)
        if 'cell' in self.df.keys():  #.tolist():
            Checked_bins = self.Checked_cells
            Bins_For_Title = self.Checked_cells
            BIN = ' cell '
            UNIT = ''
        elif 'energy low [eV]' in self.df.keys():  #.tolist():
            Checked_bins = self.Checked_energies_Low
            Bins_For_Title = [(self.Checked_energies_Low[i], self.Checked_energies_High[i],) for i in range(len(Checked_bins))]
            BIN = ' energy '
            UNIT = ' eV'
            """elif 'energy high [eV]' in self.df.keys().tolist():
            Checked_bins = self.Checked_energies_High
            Bins_For_Title = [(self.Checked_energies_Low[i], self.Checked_energies_High[i],) for i in range(len(Checked_bins))]
            BIN = ' energy '
            UNIT = ' eV'"""
        elif 'mu low' in self.df.keys():  #.tolist():
            Checked_bins = self.Checked_mu_Low
            Bins_For_Title = [(self.Checked_mu_Low[i], self.Checked_mu_High[i],) for i in range(len(Checked_bins))]
            BIN = ' mu '
            UNIT = ''
        elif 'surface' in self.df.keys():  #.tolist():
            Checked_bins = self.Checked_surfaces
            Bins_For_Title = self.Checked_surfaces
            BIN = ' surface '
            UNIT = ''
        elif self.n_filters == 0:
            Checked_bins = self.Checked_cells
            Bins_For_Title = self.Checked_cells
            BIN = ' cell '
            UNIT = ''
        Stack_Size = self.row_SB.value()*self.col_SB.value()

        for i in range(len(Checked_bins)): 
            bin = Checked_bins[i]
            if not self.Stack_Plot:
                fig, ax[i] = plt.subplots()
            else:
                if i > Stack_Size - 1:
                    self.showDialog('Warning', 'Stack size less than requiered plots! \nLast plots will be removed!')
                    break
            xs_ = []; y_ = {}; y_err = {}  #y_ = ['']*len(self.selected_nuclides)
            for nuclide in self.selected_nuclides:
                y_[nuclide] = []; y_err[nuclide] = []
            for score in self.selected_score: 
                score_idx = self.selected_score.index(score)
                y_error = []; ys_ = []; ys_err = []
                X = self.selected_score.index(score)   # + offset0
                multiplier = 0
                xs_.append(X)                
                for nuclide in self.selected_nuclides:
                    index = self.selected_nuclides.index(nuclide)
                    if Graph_type == 'Bar':
                        offset = Width * multiplier
                        X += offset
                    x = X 
                    multiplier = 1   
                    if 'cell' in self.df.keys(): #.tolist():
                        y = self.df[self.df.cell == bin][self.df.nuclide == nuclide][self.df.score == score]['mean'].values.tolist()
                        y_error = self.df[self.df.cell == bin][self.df.nuclide == nuclide][self.df.score == score]['std. dev.'].values.tolist()
                    elif 'surface' in self.df.keys(): #.tolist():
                        y = self.df[self.df.surface == bin][self.df.nuclide == nuclide][self.df.score == score]['mean'].values.tolist()
                        y_error = self.df[self.df.surface == bin][self.df.nuclide == nuclide][self.df.score == score]['std. dev.'].values.tolist()
                    elif 'energy low [eV]' in self.df.keys(): #.tolist():
                        y = self.df[self.df['energy low [eV]'] == bin][self.df.nuclide == nuclide][self.df.score == score]['mean'].values.tolist()
                        y_error = self.df[self.df['energy low [eV]'] == bin][self.df.nuclide == nuclide][self.df.score == score]['std. dev.'].values.tolist()
                    elif 'energy high [eV]' in self.df.keys(): #.tolist():
                        y = self.df[self.df['energy high [eV]'] == bin][self.df.nuclide == nuclide][self.df.score == score]['mean'].values.tolist()
                        y_error = self.df[self.df['energy low [eV]'] == bin][self.df.nuclide == nuclide][self.df.score == score]['std. dev.'].values.tolist()
                    elif 'mu low' in self.df.keys(): #.tolist():
                        y = self.df[self.df['mu low'] == bin][self.df.nuclide == nuclide][self.df.score == score]['mean'].values.tolist()
                        y_error = self.df[self.df['mu low'] == bin][self.df.nuclide == nuclide][self.df.score == score]['std. dev.'].values.tolist()   
                    elif 'mu high' in self.df.keys(): #.tolist():
                        y = self.df[self.df['mu high'] == bin][self.df.nuclide == nuclide][self.df.score == score]['mean'].values.tolist()
                        y_error = self.df[self.df['mu high'] == bin][self.df.nuclide == nuclide][self.df.score == score]['std. dev.'].values.tolist()   
                    else:    
                        y = self.df[self.df.nuclide == nuclide][self.df.score == score]['mean'].values.tolist()
                        y_error = self.df[self.df.nuclide == nuclide][self.df.score == score]['std. dev.'].values.tolist()
                    y_[nuclide].append(y[0])
                    y_err[nuclide].append(y_error[0])
                    ys_.append(y_[nuclide])
                    ys_err.append(y_err[nuclide])

                    Label = nuclide if score_idx == 0 else None
                    if Graph_type in ['Bar', 'Scatter']:
                        if Graph_type == 'Bar':
                            ax[i].bar(x, y, width=Width, label=Label)
                        elif Graph_type == 'Scatter':
                            ax[i].scatter(x, y, marker='^', label = Label)

                        if self.Add_error_bars_CB.isChecked():
                            ax[i].errorbar(x, y, np.array(y_error)*100, ecolor='black')
                ax[i].set_prop_cycle(None)
                #plt.gca().set_prop_cycle(None)
 
            if Graph_type == 'Stacked Bars':
                Bottom = np.zeros(len(self.selected_score))
                for nuclide in self.selected_nuclides:
                    Label = nuclide if len(self.selected_nuclides) > 1 else None
                    j = self.selected_nuclides.index(nuclide)
                    if self.Add_error_bars_CB.isChecked():
                        ax[i].bar(np.array(xs_) + X_Shift, ys_[j], yerr = np.array(ys_err[j])*100, bottom = Bottom, label = Label)
                    else:
                        ax[i].bar(np.array(xs_) + X_Shift, ys_[j], bottom = Bottom, label = Label)
                    Bottom += ys_[j] 
            if Graph_type == 'Stacked Area':
                ax[i].stackplot(np.array(xs_) + X_Shift, ys_[:len(self.selected_nuclides)], labels = self.selected_nuclides)
                if self.Add_error_bars_CB.isChecked():
                    Bottom = np.zeros(len(self.selected_score))
                    for j in range(len(self.selected_nuclides)):
                        ax[i].errorbar(np.array(xs_) + X_Shift, ys_[j] + Bottom, np.array(ys_err[j])*100, fmt = '|', ecolor='black')
                        Bottom += ys_[j]     


            Suptitle = self.Curve_title.text() + BIN + str(Bins_For_Title[i]) + UNIT
            ax[i].set_title(Suptitle, ha='center' )            
            ax[i].set_xlabel(self.Curve_xLabel.text())
            ax[i].set_ylabel(self.Curve_yLabel.text())

            if Graph_type in ['Stacked Area', 'Stacked Bars', 'Bar']:  
                ax[i].set_xticks(X_ + X_Shift, self.x)
            else:
                ax[i].set_xticks(X_, self.x)

            self.Change_Scales(ax[i], Graph_type)
            if len(self.selected_nuclides) > 1: 
                ax[i].legend() 
                  
            if self.grid:
                ax[i].grid(visible=self.grid, which=self.which_grid, axis=self.which_axis)
            else:
                ax[i].grid(False)
            self.Labels_Font(ax[i], plt)
        
        if self.Stack_Plot: 
            if Stack_Size > len(Checked_bins):
                for i in range(len(Checked_bins), self.row_SB.value()*self.col_SB.value()):
                    ax[i].set_visible(False)        # to remove empty plots

        plt.subplots_adjust(left=0.18, right=0.98, top=0.92, bottom=0.12)
        plt.tight_layout()

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
        PLT.rc('legend',fontsize=LegendeFontSize)

    def Reset_Plot_Settings(self):
        self.xLabelRot_CB.setCurrentIndex(0)
        self.TitleFont_CB.setCurrentIndex(9)
        self.xFont_CB.setCurrentIndex(8)
        self.yFont_CB.setCurrentIndex(8)
        self.Legende_CB.setCurrentIndex(6)
        self.Graph_Layout_CB.setCurrentIndex(0)
        self.Graph_type_CB.setCurrentIndex(0)

    def Curve(self, PLT, x, y, Label, idx):
        Graph_type = self.Graph_type_CB.currentText()
        if Graph_type == 'Bar':  
            multiplier = 0
            Width = 0.15  #1. / len(X_)
            Style = ''
        else:
            Width = 0
            Style = 'steps-mid'

        if idx == 0:    
            if Graph_type == 'Bar':
                PLT.bar(x, y, width = Width, label = Label)
            elif Graph_type == 'Lin-Lin':
                if Label == 'flux':    
                    PLT.plot(x, y, drawstyle=Style, label = Label)
                else:
                    PLT.plot(x, y, label = Label)
            elif Graph_type == 'Scatter':
                PLT.scatter(x, y, marker='^', label = Label)
            elif Graph_type == 'Stairs':
                edges = [0]
                edges.extend(x)
                PLT.stairs(y, edges, label = Label)
        else:
            if Graph_type == 'Bar':
                PLT.bar(x, y, width = Width)
            elif Graph_type == 'Lin-Lin':
                if Label == 'flux':    
                    PLT.plot(x, y, drawstyle=Style)
                else:
                    PLT.plot(x, y)
            elif Graph_type == 'Scatter':
                PLT.scatter(x, y, marker='^')
            elif Graph_type == 'Stairs':
                edges = [0]
                edges.extend(x)
                PLT.stairs(y, edges)

    def Change_Scales(self, PLT, Graph_type):
        if Graph_type not in ['Bar','Stacked Bars']:
            if self.xLog_CB.isChecked():
                if self.Plot_By_Key not in ['cell', 'surface', 'nuclide', 'score']:
                    PLT.set_xscale('log')
            if self.yLog_CB.isChecked():    
                PLT.set_yscale('log')
        else:
            if self.yLog_CB.isChecked():    
                PLT.set_yscale('log')

    def box_plot(self):
        print('Ploted Scores : \n', self.df.to_string())
        key=self.Plot_by_CB.currentText()
        print('selected key : ', key)
        if key != 'score':
            #if key == 'nuclide':
            for score in self.selected_score:
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
        
    def set_Graph_stack(self): 
        self.row_SB.setValue(2)       
        if self.Graph_Layout_CB.currentIndex() == 0:
            self.score_plot_PB.setText('plot data')
            self.score_plot_PB.setEnabled(False)
            for elm in self.buttons:
                elm.setEnabled(False)
        elif self.Graph_Layout_CB.currentIndex() == 1:
            self.score_plot_PB.setEnabled(True)
            for elm in self.buttons:
                elm.setEnabled(True)            
            self.row_SB.setEnabled(False)
            self.col_SB.setEnabled(False)
            self.label_5.setEnabled(False)
            self.label_6.setEnabled(False)
            self.label_7.setEnabled(False)
            self.score_plot_PB.setText('plot score')
        elif self.Graph_Layout_CB.currentIndex() == 2:
            for elm in self.buttons:
                elm.setEnabled(True)
            self.score_plot_PB.setEnabled(True)
            self.score_plot_PB.setText('plot score')
        elif self.Graph_Layout_CB.currentIndex() == 3:
            self.score_plot_PB.setText('plot Box Plot')
            self.score_plot_PB.setEnabled(True)
            for elm in self.buttons:
                elm.setEnabled(False)

    def Plot_By(self):
        self.Plot_By_Key = self.Plot_by_CB.currentText()
        #self.Graph_type_CB.setCurrentIndex(0)
        if self.Plot_by_CB.currentIndex() > 0:
            if self.Plot_by_CB.currentText() == 'nuclide':
                self.Curve_xLabel.setText('Nuclides')
                self.Deactivate_Curve_Type()
                if 'cell' in self.df.keys(): 
                    self.col_SB.setValue(int(len(self.Checked_cells)/2 + 0.5))
                elif 'energy low [eV]' in self.df.keys():
                    self.col_SB.setValue(int(len(self.Checked_energies_Low)/2 + 0.5))
                elif 'mu low' in self.df.keys():
                    self.col_SB.setValue(int(len(self.Checked_mu_Low)/2 + 0.5))
                if len(self.selected_nuclides) == 1:  
                    self.Graph_type_CB.model().item(6).setEnabled(False) # deactivate stacked area
                else:
                    self.Graph_type_CB.model().item(6).setEnabled(True)
            elif self.Plot_by_CB.currentText() == 'cell':
                self.Curve_xLabel.setText('Cells')
                self.Deactivate_Curve_Type()
                self.col_SB.setValue(int(len(self.selected_nuclides)/2 + 0.5))
                if len(self.Checked_cells) == 1:      
                    self.Graph_type_CB.model().item(6).setEnabled(False) # deactivate stacked area
                else:
                    self.Graph_type_CB.model().item(6).setEnabled(True)
            elif self.Plot_by_CB.currentText() == 'score':
                self.Curve_xLabel.setText('Scores')
                self.Deactivate_Curve_Type()
                if 'cell' in self.df.keys(): 
                    self.col_SB.setValue(int(len(self.Checked_cells)/2 + 0.5))
                elif 'energy low [eV]' in self.df.keys():
                    self.col_SB.setValue(int(len(self.Checked_energies_Low)/2 + 0.5))
                elif 'mu low' in self.df.keys():
                    self.col_SB.setValue(int(len(self.Checked_mu_Low)/2 + 0.5))
                if len(self.selected_score) == 1:  
                    self.Graph_type_CB.model().item(6).setEnabled(False) # deactivate stacked area
                else:
                    self.Graph_type_CB.model().item(6).setEnabled(True)
            elif self.Plot_by_CB.currentText() == 'surface':
                self.Curve_xLabel.setText('Surfaces')
                self.Deactivate_Curve_Type()
                if len(self.Checked_surfaces) == 1:      
                    self.Graph_type_CB.model().item(6).setEnabled(False) # deactivate stacked area
                else:
                    self.Graph_type_CB.model().item(6).setEnabled(True)

            elif self.Plot_by_CB.currentText() in ['energy low [eV]', 'energy high [eV]']:
                self.Curve_xLabel.setText('Energy / eV')
                if self.Plot_by_CB.currentText() == 'energy low [eV]':
                    Checked_Energies = self.Checked_energies_Low
                if self.Plot_by_CB.currentText() == 'energy high [eV]':
                    Checked_Energies = self.Checked_energies_High
                self.col_SB.setValue(int(len(self.selected_nuclides)/2 + 0.5))
                if len(Checked_Energies) == 1:
                    self.Deactivate_Curve_Type()
                    self.Graph_type_CB.model().item(6).setEnabled(False) # deactivate stacked plot
                else:
                    self.Activate_Curve_Type()

            elif self.Plot_by_CB.currentText() in ['mu low', 'mu high']:
                if self.Plot_by_CB.currentText() == 'mu low':
                    Checked_mu = self.Checked_mu_Low
                    self.Curve_xLabel.setText('mu low')
                if self.Plot_by_CB.currentText() == 'mu high':
                    Checked_mu = self.Checked_mu_High
                    self.Curve_xLabel.setText('mu high')
                self.col_SB.setValue(int(len(self.selected_nuclides)/2 + 0.5))
                if len(Checked_mu) == 1:
                    self.Deactivate_Curve_Type()
                    self.Graph_type_CB.model().item(6).setEnabled(False) # deactivate stacked plot
                else:
                    self.Activate_Curve_Type()
            elif self.Plot_by_CB.currentText() == 'mu high':
                if len(self.Checked_mu_High) == 1:    #  ???
                    self.Deactivate_Curve_Type()
                    self.Graph_type_CB.model().item(6).setEnabled(False) # deactivate stacked plot
                else:
                    self.Activate_Curve_Type()
                    #self.Graph_type_CB.model().item(6).setEnabled(True)
  
    def Mesh_settings(self, enabled):
        self.score_plot_PB.setEnabled(False)
        self.Bins_comboBox[self.Filters_comboBox.currentIndex() - 1].clear()
        # if enabled:
        if self.sp_file:
            tally_id = int(self.Tally_id_comboBox.currentText())
            if self.Tally_id_comboBox.currentIndex() > 0:
                if self.Filters_comboBox.currentIndex() > 0:
                    #filter_id = self.Tallies[tally_id]['filter_ids'][self.Filters_comboBox.currentIndex() - 1]
                    filter_id = self.filter_ids[self.Filters_comboBox.currentIndex() - 1]
                    # self.Bins_comboBox.addItem('Select bins')
                    self.Bins_comboBox[self.Filters_comboBox.currentIndex() - 1].addItems(['Select bin', 'All bins'])
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
                    self.Tallies[tally_id][filter_id]['Checked_bins'].clear()
    
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
        #index = self.Tallies[self.tally_id]['filter_ids'].index(self.filter_id)
        index = self.filter_ids.index(self.filter_id)
        key = self.Tallies[self.tally_id]['filter_types'][index] + ' ' + str(self.mesh_id)
        self.mean[key] = {}

        for bin in self.checked_bins:
            self.mean[key][bin-1] = {}
            for score in self.selected_score:
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
        #self.Mesh_settings(True)
        #index = self.Tallies[self.tally_id]['filter_ids'].index(self.filter_id)
        index = self.filter_ids.index(self.filter_id)
        key = self.Tallies[self.tally_id]['filter_types'][index] + ' ' + str(self.mesh_id)
        x = np.linspace(self.LL1, self.UR1, num=self.dim1 + 1)
        y = np.linspace(self.LL2, self.UR2, num=self.dim2 + 1)
        for bin in self.checked_bins:
            for score in self.selected_score:
                if score != '':
                    for nuclide in self.selected_nuclides:
                        if nuclide != '':
                            mean = self.mean[key][bin-1][score][nuclide].reshape((self.dim1, self.dim2))
                            plt.subplots()
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

    def normalOutputWritten(self,text):
        self.cursor = self.editor.textCursor()
        self.cursor.insertText(text)
        self.editor.setTextCursor(self.cursor)

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
            self.model().item(1, 0).setCheckState(QtCore.Qt.Unchecked)

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


