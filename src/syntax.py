from PyQt5 import QtCore, QtGui

class Highlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent):
        super(Highlighter, self).__init__(parent)
        self.sectionFormat = QtGui.QTextCharFormat()
        self.sectionFormat.setForeground(QtCore.Qt.black)
        '''self.errorFormat = QtGui.QTextCharFormat()
        self.errorFormat.setForeground(QtCore.Qt.red)'''

    def highlightBlock(self, document):
        lines = document.split('\n')
        for line in lines:
            self.setFormat(120, len(line), self.sectionFormat)
            '''if "[VALID]" in line:
                self.setFormat(30, len(line), self.sectionFormat)
            elif "[NOT VALID]" in line or "[XML ERROR]" in line:
                self.setFormat(30, len(line), self.errorFormat)'''


