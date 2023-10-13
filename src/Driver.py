import sys
import time


import numpy as np
from PyQt5.QtCore import QRect

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import \
    NavigationToolbar2QT as NavigationToolbar
# from matplotlib.backends.qt_compat import QtWidgets
from PyQt5 import QtCore, QtGui, QtWidgets

# importing libraries
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
 

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtCore import pyqtSlot

from matplotlib.figure import Figure

import SimpleMedicationModel as MedModel
from SimpleParameterModel import SimpleParameterModel as ParamModel
from UserParameterModel import UserParameterModel as UsrParamModel


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()

        self.savedTime = 0
        self.curTime = 0
        self.y = 0
        self.reset = False

        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)
        layout.setGeometry(QRect(0, 0, 00, 0))
        self._main.setGeometry(0, 0, 0, 00)
        self._main.setWindowTitle('Simulation Game')

        self.paramModel = UsrParamModel("Blood Pressure", 0)

        self.dynamic_canvas = FigureCanvas(Figure(figsize=(10, 6)))
        layout.addWidget(self.dynamic_canvas)
        layout.addWidget(NavigationToolbar(self.dynamic_canvas, self))



    

        layout.addWidget(self.UiComponents())



        self._dynamic_ax = self.dynamic_canvas.figure.subplots()

        # Set up a Line2D.
        self._dynamic_ax.set_xlim(0, 60)
        self._start_plot()
    


    def _start_plot(self):
        self.curTime = 0

        sol = self.paramModel.solve_ivp([0, self.curTime], [130])

        self._dynamic_ax.set_xlabel('Time')
        self._dynamic_ax.set_ylabel(self.paramModel.get_param_name())
        self._line, = self._dynamic_ax.plot(sol.t, sol.y, color='b')
        self._timer = self.dynamic_canvas.new_timer()
        self._timer.add_callback(self._update_canvas)
        self._timer.start()

    def _update_canvas(self):
        self.curTime += 1
        if (self.reset):
            sol = self.paramModel.solve_ivp([self.savedTime, self.curTime], [self.y])
            self.reset = False
        else:
            sol = self.paramModel.solve_ivp([0, self.curTime], [130])
        if self.curTime > 60:
            self._dynamic_ax.set_xlim(self.curTime - 59, self.curTime + 1)
        self.y = sol.y
        self._dynamic_ax.plot(sol.t, sol.y, color='b')
        self._line.figure.canvas.draw()

    def UiComponents(self):
 
        # creating a label
        self.label = QLabel(self)
 
        # setting geometry to the label
        self.label.setGeometry(5, 5, 260, 70)
 
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
 
 
        # adding number button to the screen
        # creating a push button
        push1 = QPushButton("1", self)
 
        # setting geometry
        push1.setGeometry(5, 150, 80, 40)
 
        # creating a push button
        push2 = QPushButton("2", self)
 
        # setting geometry
        push2.setGeometry(95, 150, 80, 40)
 
        # creating a push button
        push3 = QPushButton("3", self)
 
        # setting geometry
        push3.setGeometry(185, 150, 80, 40)
 
        # creating a push button
        push4 = QPushButton("4", self)
 
        # setting geometry
        push4.setGeometry(5, 200, 80, 40)
 
        # creating a push button
        push5 = QPushButton("5", self)
 
        # setting geometry
        push5.setGeometry(95, 200, 80, 40)
 
        # creating a push button
        push6 = QPushButton("5", self)
 
        # setting geometry
        push6.setGeometry(185, 200, 80, 40)
 
        # creating a push button
        push7 = QPushButton("7", self)
 
        # setting geometry
        push7.setGeometry(5, 250, 80, 40)
 
        # creating a push button
        push8 = QPushButton("8", self)
 
        # setting geometry
        push8.setGeometry(95, 250, 80, 40)
 
        # creating a push button
        push9 = QPushButton("9", self)
 
        # setting geometry
        push9.setGeometry(185, 250, 80, 40)
 
        # creating a push button
        push0 = QPushButton("0", self)
 
        # setting geometry
        push0.setGeometry(5, 300, 80, 40)
 
        # adding operator push button
        # creating push button
 
        # setting geometry
 
        # adding equal button a color effect
        c_effect = QGraphicsColorizeEffect()
        c_effect.setColor(Qt.blue)
 
        # creating push button
        push_OK = QPushButton("OK", self)
 
        # setting geometry
        push_OK.setGeometry(185, 300, 80, 40)
 
        # creating push button
        push_point = QPushButton(".", self)
 
        # setting geometry
        push_point.setGeometry(95, 300, 80, 40)
 
 
        # clear button
        push_clear = QPushButton("Clear", self)
        push_clear.setGeometry(5, 100, 170, 40)
 
        # del one character button
        push_del = QPushButton("Del", self)
        push_del.setGeometry(185, 100, 80, 40)
 
        # adding action to each of the button

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
 
    
    def actionOK(self):
        equation = self.label.text()
        self.label.setText("")
        self.paramModel.updateRate(eval(equation))
        self.savedTime = self.curTime
        self.reset = True

    
 
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
