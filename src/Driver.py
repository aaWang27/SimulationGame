import sys
import time

import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

# importing libraries
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import SimpleMedicationModel as MedModel
from SimpleParameterModel import SimpleParameterModel as ParamModel
from UserParameterModel import UserParameterModel as UsrParamModel


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()

        self.param = None
        self.medication = None
        self.medicationMap = {"Blood Pressure": ["a", "b"],
                              "Blood Glucose": ["c", "d"],
                              "Oxygen Content": ["e", "f"]}

        self.setCentralWidget(self._main)
        self.layout = QtWidgets.QGridLayout(self._main)
        self.layout.setGeometry(QRect(0, 0, 0, 0))
        self._main.setGeometry(0, 0, 0, 0)
        self._main.setWindowTitle('Simulation Game')

        self.paramModel = UsrParamModel("Blood Pressure", 0)
        self.paramValues = []
        self.medValues = []
        self.times = []

        self.dynamic_canvas = FigureCanvas(Figure(figsize=(10, 6)))
        self.layout.addWidget(self.dynamic_canvas, 0, 1)
        # self.layout.addWidget(NavigationToolbar(self.dynamic_canvas, self))

        self.layout.addLayout(self.UiComponents(), 1, 1)

        self.layout.addLayout(self.UIDropdownComponents(), 0, 0)

        self._param_ax = self.dynamic_canvas.figure.subplots()
        self._med_ax = self._param_ax.twinx()

        # Set up a Line2D.
        self._param_ax.set_xlim(0, 60)
        self._start_plot()

    def _start_plot(self):
        self.curTime = 0
        self.initVal = [130]
        self.savedTime = 0
        self.curMed = 0

        self.times.append(self.curTime)
        self.paramValues.append(self.initVal[0])
        self.medValues.append(self.curMed)

        sol = self.paramModel.solve_ivp([self.savedTime, self.curTime], self.initVal)
        self._param_ax.set_xlabel('Time')
        self._param_ax.set_ylabel(self.paramModel.get_param_name())
        self._med_ax.set_ylabel('Medication Rate')
        self._param_line, = self._param_ax.plot(sol.t, sol.y, color='b')
        self._med_line, = self._med_ax.plot(self.times, self.medValues, color='r')
        self._timer = self.dynamic_canvas.new_timer()
        self._timer.add_callback(self._update_canvas)
        self._timer.start()

    def _update_canvas(self):
        self.curTime += 1

        sol = self.paramModel.solve_ivp([self.savedTime, self.curTime], self.initVal)
        self.times.append(self.curTime)
        self.paramValues.append(sol.y[-1])
        self.medValues.append(self.curMed)
        self.y = sol.y
        if self.curTime > 60:
            self._param_ax.set_xlim(self.curTime - 59, self.curTime + 1)
            self._med_ax.set_xlim(self.curTime - 59, self.curTime + 1)
            self._param_ax.plot(self.times[-60:], self.paramValues[-60:], color='b')
            self._med_ax.plot(self.times[-60:], self.medValues[-60:], color='r')
            self._param_line.figure.canvas.draw()
            self._med_line.figure.canvas.draw()
        else:
            self._param_ax.plot(self.times, self.paramValues, color='b')
            self._med_ax.plot(self.times, self.medValues, color='r')
            self._param_line.figure.canvas.draw()
            self._med_line.figure.canvas.draw()

    def UiComponents(self):
        self.keypadLayout = QtWidgets.QGridLayout()

        # creating a label
        self.label = QLabel(self)
        # self.label.setGeometry(5, 5, 260, 70)
 
        # creating label multi line
        self.label.setWordWrap(True)
 
        # setting style sheet to the label
        self.label.setStyleSheet("QLabel"
                                 "{"
                                 "border : 4px solid black;"
                                 "background : white;"
                                 "}")
 
        # setting alignment to the label
        self.label.setAlignment(Qt.AlignRight)
 
        # setting font
        self.label.setFont(QFont('Arial', 15))
 
        # adding number buttons to the screen
        # creating a push button
        push1 = QPushButton("1", self)
        # push1.setGeometry(5, 150, 80, 40)
 
        # creating a push button
        push2 = QPushButton("2", self)
        # push2.setGeometry(95, 150, 80, 40)
 
        # creating a push button
        push3 = QPushButton("3", self)
        # push3.setGeometry(185, 150, 80, 40)
 
        # creating a push button
        push4 = QPushButton("4", self)
        # push4.setGeometry(5, 200, 80, 40)
 
        # creating a push button
        push5 = QPushButton("5", self)
        # push5.setGeometry(95, 200, 80, 40)
 
        # creating a push button
        push6 = QPushButton("5", self)
        # push6.setGeometry(185, 200, 80, 40)
 
        # creating a push button
        push7 = QPushButton("7", self)
        # push7.setGeometry(5, 250, 80, 40)
 
        # creating a push button
        push8 = QPushButton("8", self)
        # push8.setGeometry(95, 250, 80, 40)
 
        # creating a push button
        push9 = QPushButton("9", self)
        # push9.setGeometry(185, 250, 80, 40)
 
        # creating a push button
        push0 = QPushButton("0", self)
        # push0.setGeometry(5, 300, 80, 40)
 
        # adding operator push button
        # creating push button
 
        # adding equal button a color effect
        c_effect = QGraphicsColorizeEffect()
        c_effect.setColor(Qt.blue)
 
        # creating push button
        push_OK = QPushButton("OK", self)
        # push_OK.setGeometry(185, 300, 80, 40)
 
        # creating push button
        push_point = QPushButton(".", self)
        # push_point.setGeometry(95, 300, 80, 40)

        # clear button
        push_clear = QPushButton("Clear", self)
        # push_clear.setGeometry(5, 100, 170, 40)
 
        # del one character button
        push_del = QPushButton("Del", self)
        # push_del.setGeometry(185, 100, 80, 40)

        self.keypadLayout.addWidget(self.label, 0, 0, 1, 3)
        self.keypadLayout.addWidget(push_clear, 1, 0, 1, 2)
        self.keypadLayout.addWidget(push_del, 1, 2)
        self.keypadLayout.addWidget(push1, 2, 0)
        self.keypadLayout.addWidget(push2, 2, 1)
        self.keypadLayout.addWidget(push3, 2, 2)
        self.keypadLayout.addWidget(push4, 3, 0)
        self.keypadLayout.addWidget(push5, 3, 1)
        self.keypadLayout.addWidget(push6, 3, 2)
        self.keypadLayout.addWidget(push7, 4, 0)
        self.keypadLayout.addWidget(push8, 4, 1)
        self.keypadLayout.addWidget(push9, 4, 2)
        self.keypadLayout.addWidget(push0, 5, 0)
        self.keypadLayout.addWidget(push_point, 5, 1)
        self.keypadLayout.addWidget(push_OK, 5, 2)

        # add actions to each of the button
        push0.clicked.connect(self.action0)
        push1.clicked.connect(self.action1)
        push2.clicked.connect(self.action2)
        push3.clicked.connect(self.action3)
        push4.clicked.connect(self.action4)
        push5.clicked.connect(self.action5)
        push6.clicked.connect(self.action6)
        push7.clicked.connect(self.action7)
        push8.clicked.connect(self.action8)
        push9.clicked.connect(self.action9)
        push_OK.clicked.connect(self.actionOK)
        push_point.clicked.connect(self.action_point)
        push_clear.clicked.connect(self.action_clear)
        push_del.clicked.connect(self.action_del)

        return self.keypadLayout
    
    def UIDropdownComponents(self):

        def actionSetParam():
            self.combobox2.clear()
            self.combobox2.addItems(self.medicationMap[self.combobox1.currentText()])
            return self.combobox1.currentText()

        self.dropdownLayout = QtWidgets.QGridLayout()

        self.paramLabel = QLabel('Choose Parameter', self) 
 
        self.combobox1 = QComboBox()
        self.combobox1.addItem('Blood Pressure')
        self.combobox1.addItem('Blood Glucose')
        self.combobox1.addItem('Oxygen Content')

        self.combobox1.activated.connect(actionSetParam)
        
        self.dropdownLayout.addWidget(self.paramLabel, 0, 0)
        self.dropdownLayout.addWidget(self.combobox1, 1, 0)

        self.medLabel = QLabel('Choose Medication', self)

        self.combobox2 = QComboBox()

        self.dropdownLayout.addWidget(self.medLabel, 2, 0)
        self.dropdownLayout.addWidget(self.combobox2, 3, 0)
                
        return self.dropdownLayout

    def actionOK(self):
        equation = self.label.text()
        self.label.setText("")
        self.paramModel.updateRate(eval(equation))
        self.curMed = equation
        self.savedTime = self.curTime
        self.initVal = [self.paramValues[-1]]
        # self.reset = True
 
    def action_point(self):
        # appending label text
        text = self.label.text()
        self.label.setText(text + ".")
 
    def action0(self):
        # appending label text
        text = self.label.text()
        self.label.setText(text + "0")
 
    def action1(self):
        # appending label text
        text = self.label.text()
        self.label.setText(text + "1")
 
    def action2(self):
        # appending label text
        text = self.label.text()
        self.label.setText(text + "2")
 
    def action3(self):
        # appending label text
        text = self.label.text()
        self.label.setText(text + "3")
 
    def action4(self):
        # appending label text
        text = self.label.text()
        self.label.setText(text + "4")
 
    def action5(self):
        # appending label text
        text = self.label.text()
        self.label.setText(text + "5")
 
    def action6(self):
        # appending label text
        text = self.label.text()
        self.label.setText(text + "6")
 
    def action7(self):
        # appending label text
        text = self.label.text()
        self.label.setText(text + "7")
 
    def action8(self):
        # appending label text
        text = self.label.text()
        self.label.setText(text + "8")
 
    def action9(self):
        # appending label text
        text = self.label.text()
        self.label.setText(text + "9")
 
    def action_clear(self):
        # clearing the label text
        self.label.setText("")
 
    def action_del(self):
        # clearing a single digit
        text = self.label.text()
        print(text[:len(text)-1])
        self.label.setText(text[:len(text)-1])

if __name__ == "__main__":
    # Check whether there is already a running QApplication (e.g., if running
    # from an IDE).
    qapp = QtWidgets.QApplication.instance()
    if not qapp:
        qapp = QtWidgets.QApplication(sys.argv)

    app = ApplicationWindow()
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec()
