# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\marinc\AutonoMouse\Software\schedule-generator\UI\GNGPlumeBgDelaysUI.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1119, 607)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.trialLengthEdit = QtWidgets.QLineEdit(Form)
        self.trialLengthEdit.setObjectName("trialLengthEdit")
        self.gridLayout.addWidget(self.trialLengthEdit, 5, 1, 1, 1)
        self.mindelayEdit = QtWidgets.QLineEdit(Form)
        self.mindelayEdit.setObjectName("mindelayEdit")
        self.gridLayout.addWidget(self.mindelayEdit, 5, 2, 1, 1)
        self.label_13 = QtWidgets.QLabel(Form)
        self.label_13.setObjectName("label_13")
        self.gridLayout.addWidget(self.label_13, 1, 0, 1, 6)
        self.label_3 = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_3.setFont(font)
        self.label_3.setScaledContents(False)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 4)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 4, 2, 1, 1)
        self.label_5 = QtWidgets.QLabel(Form)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 4, 1, 1, 1)
        self.line_2 = QtWidgets.QFrame(Form)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 2, 0, 1, 6)
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 4, 0, 1, 1)
        self.odour1rewardedCheck = QtWidgets.QCheckBox(Form)
        self.odour1rewardedCheck.setText("")
        self.odour1rewardedCheck.setObjectName("odour1rewardedCheck")
        self.gridLayout.addWidget(self.odour1rewardedCheck, 5, 5, 1, 1)
        self.nTrialsEdit = QtWidgets.QLineEdit(Form)
        self.nTrialsEdit.setObjectName("nTrialsEdit")
        self.gridLayout.addWidget(self.nTrialsEdit, 5, 0, 1, 1)
        self.label_7 = QtWidgets.QLabel(Form)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 4, 5, 1, 1)
        self.label_10 = QtWidgets.QLabel(Form)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 6, 2, 1, 1)
        self.shatterHzEdit = QtWidgets.QLineEdit(Form)
        self.shatterHzEdit.setObjectName("shatterHzEdit")
        self.gridLayout.addWidget(self.shatterHzEdit, 7, 0, 1, 1)
        self.label_9 = QtWidgets.QLabel(Form)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 6, 1, 1, 1)
        self.dataSamplingRateEdit = QtWidgets.QLineEdit(Form)
        self.dataSamplingRateEdit.setObjectName("dataSamplingRateEdit")
        self.gridLayout.addWidget(self.dataSamplingRateEdit, 7, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(Form)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 6, 0, 1, 1)
        self.targetMax1Edit = QtWidgets.QLineEdit(Form)
        self.targetMax1Edit.setObjectName("targetMax1Edit")
        self.gridLayout.addWidget(self.targetMax1Edit, 7, 2, 1, 1)
        self.openPlumeDataButton1 = QtWidgets.QToolButton(Form)
        self.openPlumeDataButton1.setObjectName("openPlumeDataButton1")
        self.gridLayout.addWidget(self.openPlumeDataButton1, 6, 3, 1, 1)
        self.plumeDataLabel1 = QtWidgets.QLabel(Form)
        self.plumeDataLabel1.setObjectName("plumeDataLabel1")
        self.gridLayout.addWidget(self.plumeDataLabel1, 7, 3, 1, 1)
        self.label_6 = QtWidgets.QLabel(Form)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 6, 4, 1, 1)
        self.lickFractionEdit = QtWidgets.QLineEdit(Form)
        self.lickFractionEdit.setObjectName("lickFractionEdit")
        self.gridLayout.addWidget(self.lickFractionEdit, 7, 4, 1, 1)
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setEnabled(True)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 4, 4, 1, 1)
        self.offsetEdit = QtWidgets.QLineEdit(Form)
        self.offsetEdit.setObjectName("offsetEdit")
        self.gridLayout.addWidget(self.offsetEdit, 5, 4, 1, 1)
        self.maxdelayEdit = QtWidgets.QLineEdit(Form)
        self.maxdelayEdit.setObjectName("maxdelayEdit")
        self.gridLayout.addWidget(self.maxdelayEdit, 5, 3, 1, 1)
        self.label_11 = QtWidgets.QLabel(Form)
        self.label_11.setObjectName("label_11")
        self.gridLayout.addWidget(self.label_11, 4, 3, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.trialLengthEdit.setText(_translate("Form", "2.0"))
        self.mindelayEdit.setText(_translate("Form", "0.1"))
        self.label_13.setText(_translate("Form", "Valve Map Setup : 0 = Blank, 1 = Odour 1, 2 = Odour 2; plays blank plume in the background"))
        self.label_3.setText(_translate("Form", "Simple Go / No-Go with Plumes in Background"))
        self.label_2.setText(_translate("Form", "Min Odour Delay (s)"))
        self.label_5.setText(_translate("Form", "Trial Length (s)"))
        self.label.setText(_translate("Form", "Number of Trials"))
        self.nTrialsEdit.setText(_translate("Form", "300"))
        self.label_7.setText(_translate("Form", "Odour 1 Rewarded"))
        self.label_10.setText(_translate("Form", "Target Max 1"))
        self.shatterHzEdit.setText(_translate("Form", "500"))
        self.label_9.setText(_translate("Form", "Data Sampling Rate"))
        self.dataSamplingRateEdit.setText(_translate("Form", "10000"))
        self.label_8.setText(_translate("Form", "Shatter Frequency (Hz)"))
        self.targetMax1Edit.setText(_translate("Form", "1.0"))
        self.openPlumeDataButton1.setText(_translate("Form", "Open Plume Data 1"))
        self.plumeDataLabel1.setText(_translate("Form", "-"))
        self.label_6.setText(_translate("Form", "Lick Fraction"))
        self.lickFractionEdit.setText(_translate("Form", "0.1"))
        self.label_4.setText(_translate("Form", "Trial Offset (s)"))
        self.offsetEdit.setText(_translate("Form", "0.1"))
        self.maxdelayEdit.setText(_translate("Form", "0.1"))
        self.label_11.setText(_translate("Form", "Max Odour Delay (s)"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
