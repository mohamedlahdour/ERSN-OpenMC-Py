# Form implementation generated from reading ui file 'ui_output.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

import sys
from PyQt5 import QtCore ,QtWidgets
from ui_output import Ui_Form


'''class MainWindow(QtWidgets.QWidget, Ui_Form):   
    def __init__(self, parent=None):     
        super(MainWindow, self).__init__(parent)     
        self.setupUi(self)     
        self.go_button.clicked.connect(self.pressed)   
    def pressed(self):     
        self.webView.setUrl(QtCore.QUrl(self.lineEdit.displayText()))

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv) 
    view = MainWindow() 
    view.showMaximized()
    sys.exit(app.exec_())'''

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.lineEdit = QtWidgets.QLineEdit(Form)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.go_button = QtWidgets.QPushButton(Form)
        self.go_button.setObjectName("go_button")
        self.horizontalLayout.addWidget(self.go_button)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.webView = QtWebKitWidgets.QWebView(Form)
        self.webView.setUrl(QtCore.QUrl("about:blank"))
        self.webView.setObjectName("webView")
        self.verticalLayout.addWidget(self.webView)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pushButton.setText(_translate("Form", "<---"))
        self.pushButton_2.setText(_translate("Form", "--->"))
        self.go_button.setText(_translate("Form", "GO"))

from PyQt5 import QtWebKitWidgets

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())