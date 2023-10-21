import os
import sys

from PyQt5 import QtPrintSupport, Qt
from PyQt5.QtCore import QFile, QStringListModel, QSize, QFileInfo, QCoreApplication, QSettings, QDir, QProcess, \
    QTextStream, QVariant, QPoint
from PyQt5.QtGui import QCursor, QIcon, QKeySequence, QTextCursor, QTextCharFormat, QColor, QTextDocument, \
    QTextFormat
from PyQt5.QtWidgets import QApplication, QLabel, QCompleter, QTextEdit, QHBoxLayout, QAction, QVBoxLayout, \
    QColorDialog, QComboBox, QWidget, QMenu, QInputDialog, QLineEdit, QMessageBox, QFileDialog, QSystemTrayIcon, QDialog

from gui import app
from src.PyEdit import myEditor, TextEdit, NumberBar, tab, lineHighlightColor
from src.syntax import Highlighter


def Editor(self):
    iconsize = QSize(24, 24)

    self.words = []
    self.root = QFileInfo.path(QFileInfo(QCoreApplication.arguments()[0]))
    self.wordList = []
    self.bookmarkslist = []
    print("self.root is: ", self.root)
    self.appfolder = self.root
    self.openPath = ""
    self.statusBar().showMessage(self.appfolder)
    self.lineLabel = QLabel("line")
    self.statusBar().addPermanentWidget(self.lineLabel)
    self.MaxRecentFiles = 15
    self.windowList = []
    self.recentFileActs = []
    self.settings = QSettings("PyEdit", "PyEdit")
    self.dirpath = QDir.homePath() + "$HOME/Documents/python_files/"
    self.setAttribute(Qt.WA_DeleteOnClose)
    self.setWindowIcon(QIcon("src/icons/python3.png"))
    self.editor = TextEdit()
    self.completer = QCompleter(self)
    self.completer.setModel(self.modelFromFile(self.root + '/resources/wordlist.txt'))
    self.completer.setModelSorting(QCompleter.CaseInsensitivelySortedModel)
    self.completer.setCaseSensitivity(Qt.CaseInsensitive)
    self.completer.setFilterMode(Qt.MatchContains)
    self.completer.setWrapAround(False)
    self.completer.setCompletionRole(Qt.DisplayRole)
    self.editor.setCompleter(self.completer)
    self.editor.cursorPositionChanged.connect(self.cursorPositionChanged)
    self.extra_selections = []
    self.mainText = " "  # "#!/usr/bin/python3\n# -*- coding: utf-8 -*-\n"
    self.fname = ""
    self.filename = ""
    self.mypython = "2"
    self.shellWin = QTextEdit()
    self.shellWin.setContextMenuPolicy(Qt.CustomContextMenu)
    self.shellWin.setFixedHeight(90)
    # Line Numbers ...
    self.numbers = NumberBar(self.editor)
    self.createActions()
    # Syntax Highlighter ...
    self.highlighter = Highlighter(self.editor.document())
    # Laying out...
    layoutH = QHBoxLayout()
    layoutH.setSpacing(1.5)
    layoutH.addWidget(self.numbers)
    layoutH.addWidget(self.editor)
    ### systray
    # self.createTrayIcon()
    # self.trayIcon.show()
    ### statusbar
    self.statusBar()
    self.statusBar().showMessage('Welcome')
    ### begin toolbar
    # tb = self.addToolBar("File")
    tb.setContextMenuPolicy(Qt.PreventContextMenu)
    tb.setIconSize(QSize(iconsize))
    tb.setMovable(False)
    tb.setAllowedAreas(Qt.AllToolBarAreas)
    tb.setFloatable(False)

    ### file buttons
    tb.addSeparator()
    tb.addSeparator()
    self.newAct = QAction(QIcon("src/icons/new24.png"), "&New", self, shortcut=QKeySequence.New,
                          statusTip="new file", triggered=self.newFile)
    # tb.addAction(self.newAct)
    '''
    self.openAct = QAction(QIcon("src/icons/open24.png"), "&Open", self, shortcut=QKeySequence.Open,
                           statusTip="open file", triggered=self.openFile)
    tb.addAction(self.openAct)

    self.saveAct = QAction(QIcon("src/icons/document-save.png"), "&Save", self, shortcut=QKeySequence.Save,
                           statusTip="save file", triggered=self.fileSave)
    tb.addAction(self.saveAct)

    self.saveAsAct = QAction(QIcon("src/icons/document-save-as.png"), "&Save as ...", self,
                             shortcut=QKeySequence.SaveAs,
                             statusTip="save file as ...", triggered=self.fileSaveAs)
    tb.addAction(self.saveAsAct)

    self.pdfAct = QAction(QIcon("src/icons/pdf.png"), "export PDF", self, shortcut="Ctrl+Shift+p",
                          statusTip="save file as PDF", triggered=self.exportPDF)
    tb.addAction(self.pdfAct)

    self.jumpToAct = QAction(QIcon("src/icons/go-next.png"), "go to Definition", self, shortcut="F12",
                             statusTip="go to def", triggered=self.gotoBookmarkFromMenu)

    ### comment buttons
    tb.addSeparator()
    self.commentAct = QAction(QIcon("src/icons/comment.png"), "#comment Line", self, shortcut="F2",
                              statusTip="comment Line (F2)", triggered=self.commentLine)
    tb.addAction(self.commentAct)

    self.uncommentAct = QAction(QIcon("src/icons/uncomment.png"), "uncomment Line", self, shortcut="F3",
                                statusTip="uncomment Line (F3)", triggered=self.uncommentLine)
    tb.addAction(self.uncommentAct)

    self.commentBlockAct = QAction(QIcon("src/icons/commentBlock.png"), "comment Block", self, shortcut="F6",
                                   statusTip="comment selected block (F6)", triggered=self.commentBlock)
    tb.addAction(self.commentBlockAct)

    self.uncommentBlockAct = QAction(QIcon("src/icons/uncommentBlock.png"), "uncomment Block (F7)", self, shortcut="F7",
                                     statusTip="uncomment selected block (F7)", triggered=self.uncommentBlock)
    tb.addAction(self.uncommentBlockAct)
    ### color chooser
    tb.addSeparator()
    tb.addAction(QIcon('src/icons/color1.png'), "insert QColor", self.insertColor)
    tb.addSeparator()
    tb.addAction(QIcon('src/icons/color2.png'), "change Color", self.changeColor)

    ### path python buttons
    self.py3Act = QAction(QIcon('src/icons/python3.png'), "run in Python 3 (F6)", self, shortcut="F6",
                          statusTip="run in Python 3 (F5)", triggered=self.runPy3)
    tb.addAction(self.py3Act)
    tb.addSeparator()

    self.termAct = QAction(QIcon('src/icons/terminal.png'), "run in Terminal",
                           statusTip="run in Terminal", triggered=self.runInTerminal)
    tb.addAction(self.termAct)
    tb.addSeparator()

    tb.addAction(QIcon("src/icons/eraser.png"), "clear Output Label", self.clearLabel)
    tb.addSeparator()
    ### print preview
    self.printPreviewAct = QAction(QIcon("src/icons/document-print-preview.png"), "Print Preview", self,
                                   shortcut="Ctrl+Shift+P",
                                   statusTip="Preview Document", triggered=self.handlePrintPreview)
    tb.addAction(self.printPreviewAct)
    ### print
    self.printAct = QAction(QIcon("src/icons/document-print.png"), "Print", self, shortcut=QKeySequence.Print,
                            statusTip="Print Document", triggered=self.handlePrint)
    tb.addAction(self.printAct)
    ### about buttons
    tb.addSeparator()
    tb.addAction(QIcon("src/icons/info2.png"), "&About PyEdit", self.about)
    tb.addAction(QAction(QIcon("src/icons/stop.png"), "kill python", self, triggered=self.killPython))
    ### show / hide shellWin
    tb.addSeparator()
    self.shToggleAction = QAction(QIcon("src/icons/close-terminal.png"), "show/ hide shell window", self,
                                  statusTip="show/ hide shell window", triggered=self.handleShellWinToggle)
    self.shToggleAction.setCheckable(True)
    tb.addAction(self.shToggleAction)

    ### thunar
    tb.addSeparator()
    self.fmanAction = QAction(QIcon("src/icons/FM.png"), "open Filemanager", self,
                              statusTip="open Filemanager", triggered=self.handleFM)
    tb.addAction(self.fmanAction)

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
    self.bgAct = QAction(QIcon("src/icons/sbg_color.png"), "change Background Color", self,
                         triggered=self.changeBGColor)
    self.bgAct.setStatusTip("change Background Color")
    tb.addSeparator()
    tb.addAction(self.bgAct)
    ### exit button
    tb.addSeparator()
    ## addStretch
    empty = QWidget();
    empty.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred);
    tb.addWidget(empty)
    self.exitAct = QAction(QIcon("src/icons/quit.png"), "exit", self, shortcut=QKeySequence.Quit,
                           statusTip="Exit", triggered=self.handleQuit)
    tb.addAction(self.exitAct)
    ### end toolbar
    self.indentAct = QAction(QIcon("src/icons/format-indent-more.png"), "indent more", self, triggered=self.indentLine,
                             shortcut="F8")
    self.indentLessAct = QAction(QIcon("src/icons/format-indent-less.png"), "indent less", self,
                                 triggered=self.indentLessLine, shortcut="F9")
    ### find / replace toolbar
    self.addToolBarBreak()
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
    tbf.addAction(self.indentAct)
    tbf.addAction(self.indentLessAct)
    tbf.addSeparator()
    self.gotofield = QLineEdit()
    self.gotofield.addAction(QIcon("src/icons/go-next.png"), QLineEdit.LeadingPosition)
    self.gotofield.setClearButtonEnabled(True)
    self.gotofield.setFixedWidth(120)
    self.gotofield.setPlaceholderText("go to line")
    self.gotofield.setToolTip("press RETURN to go to line")
    self.gotofield.returnPressed.connect(self.gotoLine)
    tbf.addWidget(self.gotofield)

    tbf.addSeparator()'''
    self.bookmarks = QComboBox()
    self.bookmarks.setFixedWidth(280)
    self.bookmarks.setToolTip("go to bookmark")
    self.bookmarks.activated[str].connect(self.gotoBookmark)
    '''tbf.addWidget(self.bookmarks)

    self.bookAct = QAction("add Bookmark", self,
                           statusTip="add Bookmark", triggered=self.addBookmark)
    self.bookAct.setIcon(QIcon("src/icons/add-bookmark.png"))
    tbf.addAction(self.bookAct)

    tbf.addSeparator()
    self.bookrefresh = QAction(QIcon("src/icons/update-bookmark.png"), "update Bookmarks", self,
                               statusTip="update Bookmarks", triggered=self.findBookmarks)
    tbf.addAction(self.bookrefresh)
    tbf.addAction(
        QAction(QIcon("src/icons/format-indent-more.png"), "check && reindent Text", self, triggered=self.reindentText))

    layoutV = QVBoxLayout()

    #bar = self.menuBar()

    # file menu
    self.filemenu = bar.addMenu("File")
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

    self.clearRecentAct = QAction(QIcon("src/icons/close.png"), "clear Recent Files List", self,
                                  triggered=self.clearRecentFiles)
    self.filemenu.addAction(self.clearRecentAct)
    self.filemenu.addSeparator()
    self.filemenu.addAction(self.exitAct)

    editmenu = bar.addMenu("Edit")
    editmenu.addAction(
        QAction(QIcon('src/icons/undo.png'), "Undo", self, triggered=self.editor.undo, shortcut="Ctrl+u"))
    editmenu.addAction(
        QAction(QIcon('src/icons/redo.png'), "Redo", self, triggered=self.editor.redo, shortcut="Shift+Ctrl+u"))
    editmenu.addSeparator()
    editmenu.addAction(
        QAction(QIcon('src/icons/copy.png'), "Copy", self, triggered=self.editor.copy, shortcut="Ctrl+c"))
    editmenu.addAction(QAction(QIcon('src/icons/cut.png'), "Cut", self, triggered=self.editor.cut, shortcut="Ctrl+x"))
    editmenu.addAction(
        QAction(QIcon('src/icons/paste.png'), "Paste", self, triggered=self.editor.paste, shortcut="Ctrl+v"))
    editmenu.addAction(
        QAction(QIcon('src/icons/delete.png'), "Delete", self, triggered=self.editor.cut, shortcut="Del"))
    editmenu.addSeparator()
    editmenu.addAction(QAction(QIcon('src/icons/select-all.png'), "Select All", self, triggered=self.editor.selectAll,
                               shortcut="Ctrl+a"))
    editmenu.addSeparator()
    editmenu.addAction(self.commentAct)
    editmenu.addAction(self.uncommentAct)
    editmenu.addSeparator()
    editmenu.addAction(self.commentBlockAct)
    editmenu.addAction(self.uncommentBlockAct)
    editmenu.addSeparator()
    editmenu.addAction(self.py3Act)
    editmenu.addSeparator()
    editmenu.addAction(self.jumpToAct)
    editmenu.addSeparator()
    editmenu.addAction(self.indentAct)
    editmenu.addAction(self.indentLessAct)
    '''
    layoutV = QVBoxLayout()
    layoutV.addLayout(layoutH)
    self.shellWin.setMinimumHeight(28)
    self.shellWin.customContextMenuRequested.connect(self.shellWincontextMenuRequested)
    layoutV.addWidget(self.shellWin)
    ### main window
    mq = QWidget(self)
    mq.setLayout(layoutV)
    self.setCentralWidget(mq)
    #   !!!!!!!!!!!!!!!!!!!!!!!!

    # Event Filter ...
    #        self.installEventFilter(self)
    self.editor.setFocus()
    self.cursor = QTextCursor()
    self.editor.setTextCursor(self.cursor)
    self.editor.setPlainText(self.mainText)
    self.editor.moveCursor(self.cursor.End)
    if self.mainText == ' ':
        self.editor.moveCursor(self.cursor.Left)
    self.editor.document().modificationChanged.connect(self.setWindowModified)

    # Brackets ExtraSelection ...
    self.left_selected_bracket = QTextEdit.ExtraSelection()
    self.right_selected_bracket = QTextEdit.ExtraSelection()

    ### shell settings
    self.process = QProcess(self)
    self.process.setProcessChannelMode(QProcess.MergedChannels)
    self.process.readyRead.connect(self.dataReady)
    self.process.started.connect(lambda: self.shellWin.append("starting shell"))
    self.process.finished.connect(lambda: self.shellWin.append("shell ended"))

    self.editor.setContextMenuPolicy(Qt.CustomContextMenu)
    self.editor.customContextMenuRequested.connect(self.contextMenuRequested)

    self.readSettings()
    self.statusBar().showMessage("self.root is: " + self.root, 0)


def textSize(self, pointSize):
    pointSize = float(self.comboSize.currentText())
    if pointSize > 0:
        fmt = QTextCharFormat()
        fmt.setFontPointSize(pointSize)
        self.mergeFormatOnWordOrSelection(fmt)


def mergeFormatOnWordOrSelection(self, format):
    cursor = self.editor.textCursor()
    if not cursor.hasSelection():
        cursor.select(QTextCursor.WordUnderCursor)

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


def runInTerminal(self):
    print("running in terminal")
    if self.editor.toPlainText() == "":
        self.statusBar().showMessage("no Code!")
        return
    # if not self.editor.toPlainText() == self.mainText:
    if self.editor.toPlainText() != '':
        if self.filename:
            #                self.mypython = "3"
            self.statusBar().showMessage("running " + self.filename + " in Lua")
            self.fileSave()
            self.shellWin.clear()
            dname = QFileInfo(self.filename).filePath().replace(QFileInfo(self.filename).fileName(), "")
            cmd = str('xfce4-terminal -e "python3 ' + dname + self.strippedName(self.filename) + '"')
            self.statusBar().showMessage(str(dname))
            QProcess().execute("cd '" + dname + "'")
            print(cmd)
            self.process.start(cmd)
        else:
            self.filename = "/tmp/tmp.py"
            self.fileSave()
            self.runInTerminal()
    else:
        self.statusBar().showMessage("no code to run")


def handleShellWinToggle(self):
    if self.shellWin.isVisible():
        self.shellWin.setVisible(False)
    else:
        self.shellWin.setVisible(True)


def handleFM(self):
    if "/" in self.shellWin.textCursor().selectedText():
        QProcess.startDetached("thunar", [self.shellWin.textCursor().selectedText()])
    else:
        QProcess.startDetached("thunar")


def killPython(self):
    if int(sys.version[0]) < 3:
        os.system("killall python")
    else:
        os.system("killall python3")


def keyPressEvent(self, event):
    if self.editor.hasFocus():
        if event.key() == Qt.Key_F10:
            self.findNextWord()


def cursorPositionChanged(self):
    line = self.editor.textCursor().blockNumber() + 1
    pos = self.editor.textCursor().positionInBlock()
    self.lineLabel.setText("line " + str(line) + " - position " + str(pos))


def textColor(self):
    col = QColorDialog.getColor(QColor("#" + self.editor.textCursor().selectedText()), self)
    self.pix.fill(col)
    if not col.isValid():
        return
    else:
        colorname = 'QColor("' + col.name() + '")'
        self.editor.textCursor().insertText(colorname)
        self.pix.fill(col)


def Test(self):
    self.editor.selectAll()


def reindentText(self):
    if self.editor.toPlainText() == "":  # or self.editor.toPlainText() == self.mainText:
        self.statusBar().showMessage("no code to reindent")
    else:
        self.editor.selectAll()
        tab = "\t"
        oldtext = self.editor.textCursor().selectedText()
        newtext = oldtext.replace(tab, "    ")
        self.editor.textCursor().insertText(newtext)
        self.statusBar().showMessage("code reindented")


def insertColor(self):
    col = QColorDialog.getColor(QColor("#000000"), self)
    if not col.isValid():
        return
    else:
        colorname = 'QColor("' + col.name() + '")'
        self.editor.textCursor().insertText(colorname)


def changeColor(self):
    if not self.editor.textCursor().selectedText() == "":
        col = QColorDialog.getColor(QColor("#" + self.editor.textCursor().selectedText()), self)
        if not col.isValid():
            return
        else:
            colorname = col.name()
            self.editor.textCursor().insertText(colorname.replace("#", ""))
    else:
        col = QColorDialog.getColor(QColor("black"), self)
        if not col.isValid():
            return
        else:
            colorname = col.name()
            self.editor.textCursor().insertText(colorname)


### QPlainTextEdit contextMenu
def contextMenuRequested(self, point):
    cmenu = QMenu()
    cmenu = self.editor.createStandardContextMenu()
    cmenu.addSeparator()
    cmenu.addAction(self.jumpToAct)
    cmenu.addSeparator()
    if not self.editor.textCursor().selectedText() == "":
        cmenu.addAction(QIcon.fromTheme("gtk-find-and-replace"), "replace all occurrences with", self.replaceThis)
        cmenu.addSeparator()
    cmenu.addAction(QIcon.fromTheme("zeal"), "show help with 'zeal'", self.showZeal)
    cmenu.addAction(QIcon.fromTheme("firefox"), "find with 'firefox'", self.findWithFirefox)
    cmenu.addAction(QIcon.fromTheme("gtk-find-"), "find this (F10)", self.findNextWord)
    cmenu.addAction(self.texteditAction)
    cmenu.addSeparator()
    cmenu.addAction(self.py2Act)
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
    cmenu.addAction(QIcon.fromTheme("preferences-color"), "insert QColor", self.insertColor)

    cmenu.addSeparator()
    cmenu.addAction(QIcon.fromTheme("preferences-color"), "change Color", self.changeColor)
    cmenu.exec_(self.editor.mapToGlobal(point))

    ### shellWin contextMenu


def shellWincontextMenuRequested(self, point):
    shellWinMenu = QMenu()
    shellWinMenu = self.shellWin.createStandardContextMenu()
    #        shellWinMenu.addAction(QAction(QIcon.fromTheme('edit-copy'), "Copy", self, triggered = self.shellWin.copy, shortcut = "Ctrl+c"))
    shellWinMenu.addSeparator()
    shellWinMenu.addAction(QIcon.fromTheme("zeal"), "show help with 'zeal'", self.showZeal_shell)
    shellWinMenu.addAction(QIcon.fromTheme("firefox"), "find with 'firefox'", self.findWithFirefox_shell)
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


def showZeal(self):
    if self.editor.textCursor().selectedText() == "":
        tc = self.editor.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        rtext = tc.selectedText()
        print(rtext)
    else:
        rtext = self.editor.textCursor().selectedText()  ##.replace(".", "::")
    cmd = "zeal " + str(rtext)
    QProcess().startDetached(cmd)


def findWithFirefox(self):
    if self.editor.textCursor().selectedText() == "":
        tc = self.editor.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        rtext = tc.selectedText()
    else:
        rtext = "python%20" + self.editor.textCursor().selectedText().replace(" ", "%20")
    url = "https://www.google.com/search?q=" + rtext
    QProcess.startDetached("firefox " + url)


def showZeal_shell(self):
    if not self.shellWin.textCursor().selectedText() == "":
        rtext = self.shellWin.textCursor().selectedText()
        cmd = "zeal " + str(rtext)
        QProcess().startDetached(cmd)


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
        self.statusBar().showMessage("more indented")


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
        self.statusBar().showMessage("less indented")


def dataReady(self):
    out = ""
    try:
        out = str(self.process.readAll(), encoding='utf8').rstrip()
    except TypeError:
        self.msgbox("Error", str(self.process.readAll(), encoding='utf8'))
        out = str(self.process.readAll()).rstrip()
        self.shellWin.moveCursor(self.cursor.Start)  ### changed
    self.shellWin.append(out)
    if self.shellWin.find("line", QTextDocument.FindWholeWords):
        t = self.shellWin.toPlainText().partition("line")[2].partition("\n")[0].lstrip()
        if t.find(",", 0):
            tr = t.partition(",")[0]
        else:
            tr = t.lstrip()
        self.gotoErrorLine(tr)
    else:
        return
    self.shellWin.moveCursor(self.cursor.End)
    self.shellWin.ensureCursorVisible()


def createActions(self):
    for i in range(self.MaxRecentFiles):
        self.recentFileActs.append(
            QAction(self, visible=False,
                    triggered=self.openRecentFile))


def addBookmark(self):
    linenumber = self.getLineNumber()
    linetext = self.editor.textCursor().block().text().strip()
    self.bookmarks.addItem(linetext, linenumber)


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


def gotoBookmark(self):
    if self.editor.find(self.bookmarks.itemText(self.bookmarks.currentIndex())):
        pass
    else:
        self.editor.moveCursor(QTextCursor.Start)
        self.editor.find(self.bookmarks.itemText(self.bookmarks.currentIndex()))

    self.editor.centerCursor()
    self.editor.moveCursor(self.cursor.StartOfLine, self.cursor.MoveAnchor)


def gotoBookmarkFromMenu(self):
    if self.editor.textCursor().selectedText() == "":
        tc = self.editor.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        rtext = tc.selectedText()
    else:
        rtext = self.editor.textCursor().selectedText()
    toFind = rtext
    self.bookmarks.setCurrentIndex(0)
    if self.bookmarks.findText(toFind, Qt.MatchContains):
        row = self.bookmarks.findText(toFind, Qt.MatchContains)
        self.statusBar().showMessage("found '" + toFind + "' at bookmark " + str(row))
        self.bookmarks.setCurrentIndex(row)
        self.gotoBookmark()
    else:
        self.statusBar().showMessage("def not found")


def clearBookmarks(self):
    self.bookmarks.clear()


#### find lines with def or class
def findBookmarks(self):
    self.editor.setFocus()
    self.editor.moveCursor(QTextCursor.Start)
    if not self.editor.toPlainText() == "":
        self.clearBookmarks()
        newline = "\n"  # u"\2029"
        fr = "from"
        im = "import"
        d = "def"
        d2 = "    def"
        c = "class"
        sn = str("if __name__ ==")
        line = ""
        list = []
        ot = self.editor.toPlainText()
        theList = ot.split(newline)
        linecount = ot.count(newline)
        for i in range(linecount + 1):
            if theList[i].startswith(im):
                line = str(theList[i]).replace("'\t','[", "").replace("]", "")
                self.bookmarks.addItem(str(line), i)
            elif theList[i].startswith(fr):
                line = str(theList[i]).replace("'\t','[", "").replace("]", "")
                self.bookmarks.addItem(str(line), i)
            elif theList[i].startswith(c):
                line = str(theList[i]).replace("'\t','[", "").replace("]", "")
                self.bookmarks.addItem(str(line), i)
            elif theList[i].startswith(tab + d):
                line = str(theList[i]).replace(tab, "").replace("'\t','[", "").replace("]", "")
                self.bookmarks.addItem(str(line), i)
            elif theList[i].startswith(d):
                line = str(theList[i]).replace(tab, "").replace("'\t','[", "").replace("]", "")
                self.bookmarks.addItem(str(line), i)
            elif theList[i].startswith(d2):
                line = str(theList[i]).replace(tab, "").replace("'\t','[", "").replace("]", "")
                self.bookmarks.addItem(str(line), i)
            elif theList[i].startswith(sn):
                line = str(theList[i]).replace("'\t','[", "").replace("]", "")
                self.bookmarks.addItem(str(line), i)

            self.bookmarkslist = [self.bookmarks.itemText(i) for i in range(self.bookmarks.count())]
            self.bookmarkslist = [w.replace('    ', '') for w in self.bookmarkslist]
            #                self.bookmarkslist = sorted(self.bookmarkslist, key = lambda x: (x[0]))
            self.bookmarkslist.sort()
            self.bookmarks.clear()
            self.bookmarks.addItems(self.bookmarkslist)

    self.statusBar().showMessage("bookmarks changed")


def clearLabel(self):
    self.shellWin.setText("")


def openRecentFile(self):
    action = self.sender()
    if action:
        myfile = action.data()
        print(myfile)
        if (self.maybeSave()):
            if QFile.exists(myfile):
                self.openFileOnStart(myfile)
            else:
                self.msgbox("Info", "File does not exist!")


### New File
def newFile(self):
    if self.maybeSave():
        self.editor.clear()
        # self.editor.setPlainText(self.mainText)
        self.filename = ""
        self.setModified(False)
        self.editor.moveCursor(self.cursor.End)
        self.statusBar().showMessage("new File created.")
        self.editor.setFocus()
        self.bookmarks.clear()
        self.setWindowTitle("new File[*]")


### open File
def openFileOnStart(self, path=None):
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
            self.findBookmarks()
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
            self.statusBar().showMessage(
                "File '" + path + "' loaded succesfully & bookmarks added & backup created ('" + self.filename + "_backup" + "')")


#                self.settings.setValue('recentFileList', [])
#                self.addToWordlist(path)
### add all words to completer ###
#                mystr = self.editor.toPlainText()
#                self.wordList =mystr.split()
#                print(mystr)

def addToWordlist(self, file):
    wl = []
    with open(file, 'r') as f:
        for line in f:
            for word in line.split(" "):
                if len(word) > 1:
                    if not "." in word:
                        self.words.append(word.replace('\n', ''))
                    else:
                        self.words.append(word.replace('\n', '').partition(".")[0])
                        self.words.append(word.replace('\n', '').partition(".")[2])
        self.completer.model().setStringList(self.words)


#            self.completer.setModel(self.modelFromFile(self.root + '/resources/wordlist.txt'))
#            print(self.completer.model().stringList())

### open File
def openFile(self, path=None):
    if self.openPath == "":
        self.openPath = self.dirpath
    if self.maybeSave():
        if not path:
            path, _ = QFileDialog.getOpenFileName(self, "Open File", self.openPath,
                                                  "Python Files (*.py);; all Files (*)")

        if path:
            self.openFileOnStart(path)


def fileSave(self):
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
        self.statusBar().showMessage("File saved.")
        self.setCurrentFile(self.filename)
        self.editor.setFocus()


    else:
        self.fileSaveAs()

        ### save File


def fileSaveAs(self):
    fn, _ = QFileDialog.getSaveFileName(self, "Save as...", self.filename,
                                        "Python files (*.py)")

    if not fn:
        print("Error saving")
        return False

    lfn = fn.lower()
    if not lfn.endswith('.py'):
        fn += '.py'

    self.filename = fn
    self.fname = QFileInfo(QFile(fn).fileName())
    return self.fileSave()


def exportPDF(self):
    if self.editor.toPlainText() == "":
        self.statusBar().showMessage("no text")
    else:
        newname = self.strippedName(self.filename).replace(QFileInfo(self.filename).suffix(), "pdf")
        fn, _ = QFileDialog.getSaveFileName(self,
                                            "PDF files (*.pdf);;All Files (*)",
                                            (QDir.homePath() + "/PDF/" + newname))
        printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
        printer.setOutputFormat(QtPrintSupport.QPrinter.PdfFormat)
        printer.setOutputFileName(fn)
        self.editor.document().print_(printer)


def exportPDF1(self):
    fn, _ = QFileDialog.getSaveFileName(self, 'Export PDF', None, 'PDF files (.pdf);;All Files()')
    if fn != '':
        if QFileInfo(fn).suffix() == "": fn += '.pdf'
        printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
        printer.setOutputFormat(QtPrintSupport.QPrinter.PdfFormat)
        printer.setOutputFileName(fn)
        self.editor.document().print_(printer)


def closeEvent(self, e):
    self.writeSettings()
    if self.maybeSave():
        e.accept()
    else:
        e.ignore()

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
                ©2022 M. Lahdour & T. El Bardouni </strong></span></p>
                    """
    self.infobox(title, message)


def runPy3(self):
    if self.editor.toPlainText() == "":
        self.statusBar().showMessage("no Code!")
        return
    # if not self.editor.toPlainText() == self.mainText:
    if self.editor.toPlainText() != '':
        if self.filename:
            self.mypython = "3"
            self.statusBar().showMessage("running " + self.filename + " in Python 3")
            self.fileSave()
            cmd = "python3"
            self.readData(cmd)
        else:
            self.filename = "/tmp/tmp.py"
            self.fileSave()
            self.runPy3()
    else:
        self.statusBar().showMessage("no code to run")


def readData(self, cmd):
    self.shellWin.clear()
    dname = QFileInfo(self.filename).filePath().replace(QFileInfo(self.filename).fileName(), "")
    self.statusBar().showMessage(str(dname))
    QProcess().execute("cd '" + dname + "'")
    self.process.start(cmd, ['-u', dname + self.strippedName(self.filename)])


#    def killPython(self):
#        if (self.mypython == "3"):
#            cmd = "killall python3"
#        else:
#            cmd = "killall python"
#        self.readData(cmd)

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

    self.statusBar().showMessage("added block comment")


def commentLine(self):
    newline = u"\u2029"
    comment = "#"
    list = []
    ot = self.editor.textCursor().selectedText()
    if not self.editor.textCursor().selectedText() == "":
        ### multiple lines selected
        theList = ot.splitlines()
        linecount = ot.count(newline)
        for i in range(linecount + 1):
            list.insert(i, comment + theList[i])
        self.editor.textCursor().insertText(newline.join(list))
        self.setModified(True)
        self.statusBar().showMessage("added comment")
    else:
        ### one line selected
        self.editor.moveCursor(QTextCursor.StartOfLine)
        self.editor.textCursor().insertText("#")


def uncommentLine(self):
    comment = "#"
    newline = u"\u2029"
    list = []
    ot = self.editor.textCursor().selectedText()
    if not self.editor.textCursor().selectedText() == "":
        ### multiple lines selected
        theList = ot.splitlines()
        linecount = ot.count(newline)
        for i in range(linecount + 1):
            list.insert(i, (theList[i]).replace(comment, "", 1))
        self.editor.textCursor().insertText(newline.join(list))
        self.setModified(True)
        self.statusBar().showMessage("comment removed")
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
        self.statusBar().showMessage("found <b>'" + self.findfield.text() + "'</b> at Line: " + str(linenumber))
        self.editor.centerCursor()
    else:
        self.statusBar().showMessage("<b>'" + self.findfield.text() + "'</b> not found")
        self.editor.moveCursor(QTextCursor.Start)
        if self.editor.find(word):
            linenumber = self.editor.textCursor().blockNumber() + 1
            self.statusBar().showMessage("found <b>'" + self.findfield.text() + "'</b> at Line: " + str(linenumber))
            self.editor.centerCursor()


def findBookmark(self, word):
    if self.editor.find(word):
        linenumber = self.getLineNumber()  # self.editor.textCursor().blockNumber() + 1
        self.statusBar().showMessage("found <b>'" + self.findfield.text() + "'</b> at Line: " + str(linenumber))


def handleQuit(self):
    if self.maybeSave():
        print("Goodbye ...")
        app.quit()


def set_numbers_visible(self, value=True):
    self.numbers.setVisible(False)


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
            self.statusBar().showMessage("replacing all")
            oldtext = self.editor.document().toPlainText()
            newtext = oldtext.replace(self.findfield.text(), self.replacefield.text())
            self.editor.setPlainText(newtext)
            self.setModified(True)
        else:
            self.statusBar().showMessage("nothing to replace")
    else:
        self.statusBar().showMessage("no text")


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

    for widget in QApplication.topLevelWidgets():
        if isinstance(widget, myEditor):
            widget.updateRecentFileActions()


def updateRecentFileActions(self):
    if self.settings.contains('recentFileList'):
        mytext = ""
        files = self.settings.value('recentFileList', [])
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


def strippedName(self, fullFileName):
    return QFileInfo(fullFileName).fileName()


def clearRecentFiles(self):
    self.settings.remove('recentFileList')
    self.recentFileActs = []
    self.settings.sync()
    for widget in QApplication.topLevelWidgets():
        if isinstance(widget, myEditor):
            widget.updateRecentFileActions()
    self.updateRecentFileActions()


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


def selectLine(self, line):
    linecursor = QTextCursor(self.editor.document().findBlockByLineNumber(line - 1))
    self.editor.moveCursor(QTextCursor.End)
    self.editor.setTextCursor(linecursor)


def createTrayIcon(self):
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "Systray",
                             "I couldn't detect any system tray on this system.")
    else:
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(QIcon.fromTheme("applications-python"))
        self.trayIconMenu = QMenu(self)
        self.trayIconMenu.addAction(
            QAction(QIcon.fromTheme("applications-python"), "about PyEdit", self, triggered=self.about))
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(
            QAction(QIcon.fromTheme("application-exit"), "Exit", self, triggered=self.handleQuit))
        self.trayIcon.setContextMenu(self.trayIconMenu)


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
        dialog.setFixedSize(900, 650)
        dialog.paintRequested.connect(self.handlePaintRequest)
        dialog.exec_()
        self.statusBar().showMessage("Print Preview closed")


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
