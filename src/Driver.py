import os
from random import randint
import sys
import time

import numpy as np
import pandas as pd

from datetime import datetime

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from scipy.integrate import solve_ivp

# importing libraries
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import textwrap

from SimpleMedicationModel import SimpleMedicationModel as MedModel
from SimpleParameterModel import SimpleParameterModel as ParamModel
from UserParameterModel import UserParameterModel as UsrParamModel
from ComputerParameterModel import ComputerParameterModel as CompParamModel

# new
from BloodPressure import BloodPresssure
from DummyParam import DummyParam
from OxygenContent import OxygenContent

from MedicationAModel import MedicationAModel
from MedicationAComputerModel import MedicationAComputerModel


from MedicationOxygenModel import MedicationOxygenModel
from MedicationOxygenComputerModel import MedicationOxygenComputerModel

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        #self.setStyleSheet("background-color: grey;")
        self._main = QtWidgets.QWidget()
        self.metricsWindow = None

        # initialize parameter and medication name variables
        self.param = None
        self.medication = None
        self.curMedRate = 0
        self.composedModel = None

        self.combobox1 = QComboBox()
        #self.combobox1.setStyleSheet("background-color: white;")

        self.decayRate = MedModel.bodyMedicationADecay

        self.parameters = ["BloodPressure", "DummyParam", "OxygenContent"]

        self.medicationMap = {"BloodPressure": ["Prinivil"],
                              "DummyParam": ["a", "d"],
                              "OxygenContent": ["Oxygen"]}

        # maps parameter name to associated model
        self.paramModelMap = {"BloodPressure": BloodPresssure,
                              "DummyParam": DummyParam,
                              "OxygenContent": OxygenContent}
        
        self.targetMap = {"BloodPressure": [95, 105],
                            "DummyParam": [90, 110],
                              "OxygenContent": [80, 120]}
        
        self.startValueMap = {"BloodPressure": [180],
                            "DummyParam": [180],
                              "OxygenContent": [40]}

        # maps medication name to associated model
        self.medModelMap = {"Prinivil": MedicationAModel,
                              "Oxygen": MedicationOxygenModel,
                              "c": MedModel,
                              "d": MedModel,
                              "e": MedModel,
                              "f": MedModel}
    
        self.medModelComputerlMap = {"Prinivil": MedicationAComputerModel,
                              "Oxygen": MedicationOxygenComputerModel,
                              "c": MedModel,
                              "d": MedModel,
                              "e": MedModel,
                              "f": MedModel}

        self.uploadedModelPath = None

        # Metrics
        # Time in interval
        # Time to get to interval
        # Variance?
        # Mean blood pressure over time interval?
        # Percentage of absolute values of derivatives within a certain interval

        self.alpha = 1.2 # >=1

        # create GUI window
        self.setCentralWidget(self._main)
        self.layout = QtWidgets.QGridLayout(self._main)
        self.layout.setGeometry(QRect(0, 0, 0, 0))
        self._main.setGeometry(0, 0, 0, 0)
        self._main.setWindowTitle('Simulation Game')

        self.width = self.frameGeometry().width()
        self.height = self.frameGeometry().height()

        self.paramModel = None  # parameter model being used
        self.paramValues = []  # array to store values of parameter over time
        self.medModel = None
        self.medValues = []  # array to store values of medication over time
        self.times = []  # array to store timestamps
        self.started = False  # whether the simulation has been started
        self.stopTime = 70

        self.computerParamModel = None
        self.computerParamValues = []
        self.computerMedValues = []

        # create canvas to hold live graph
        self.dynamic_canvas = FigureCanvas(Figure(figsize=(10, 6)))
        self.layout.addWidget(self.dynamic_canvas, 0, 1)
        # self.layout.addWidget(NavigationToolbar(self.dynamic_canvas, self))

        # create axes for graphing parameter and medication values
        self._param_ax = self.dynamic_canvas.figure.add_subplot(111)
        self._med_ax = self._param_ax.twinx()
        self._param_ax.set_xlim(0, 60)

        # add keypad and dropdown menu to GUI
        self.layout.addLayout(self.keypadComponents(), 1, 1)
        self.layout.addLayout(self.UIDropdownComponents(), 0, 0)
        self.layout.addLayout(self.logComponents(), 1, 0)
        # self.layout.addLayout(self.uploadModelComponent(), 1,2)
        self.layout.addLayout(self.instructionPage(), 0, 2, 1, 1)

        self.showMaximized()

    def composeModels(self, pm, mm):
        return lambda t_, y_: pm.parameterModel(t_, y_) + mm.medModel(t_, y_)

    def solve_ivp_here(self, tRange, y0, composedModel):
        sol = solve_ivp(composedModel, t_span=tRange, y0=y0, t_eval=np.linspace(tRange[0], tRange[1], tRange[1]+1))

        # print(sol.t)
        if(len(sol.t)>0):
            sol.y = sol.y.flatten()
        # print(sol.y)
        #
        # # Create the graph
        # plt.plot(sol.t, sol.y)
        #
        # # Add labels and a title
        # plt.xlabel('Time')
        # plt.ylabel(self.param)
        # plt.title(self.param + ' vs. Time')
        #
        # # Display the graph
        # plt.show()

        return sol

    def _start_plot(self):
        self.curTime = 0  # current time
        # self.initVal = [180]  # initial parameter value
        # self.computerInitVal = [180]

        self.initVal = self.startValueMap[self.param]
        self.computerInitVal = self.startValueMap[self.param]

        self.savedTime = 0  # time at which to start integrating
        self.curMed = 0  # current medication value

        self.computerCurMed = 0
        self.computerSavedTime = 0
        
        # update time, parameter values, and medication values
        self.times.append(self.curTime)

        self.paramValues.append(self.initVal[0])
        self.medValues.append(0)

        self.computerParamValues.append(self.computerInitVal[0])
        self.computerMedValues.append(0)

        # solve IVP to get current parameter value
        sol = self.solve_ivp_here([self.savedTime, self.curTime], self.initVal, self.composedModel)
        computerSol = self.solve_ivp_here([self.savedTime, self.curTime], self.initVal, self.composedComputerModel)

        # initialize plot
        self._param_ax.set_xlabel('Time')
        self._param_ax.set_ylabel(self.paramModel.get_param_name(), color = 'b')
        self._med_ax.set_ylabel('Total Medication In the Body', color = 'r')
        self._param_line, = self._param_ax.plot(sol.t, sol.y, color='b')
        self._med_line, = self._med_ax.plot(self.times, self.medValues, color='r')
        self._timer = self.dynamic_canvas.new_timer()
        self._timer.add_callback(self._update_canvas)
        self._timer.start()  # start timer

    def _update_canvas(self):
        # update time
        self.curTime += 1

        if self.curTime<=self.stopTime:
            # solve IVP to get current parameter value
            sol = self.solve_ivp_here([self.savedTime, self.curTime], self.initVal, self.composedModel)
            computerSol = self.solve_ivp_here([self.computerSavedTime, self.curTime], self.computerInitVal, self.composedComputerModel)

            # update time, parameter values, and medication values
            self.times.append(self.curTime)
            self.paramValues.append(sol.y[-1])
            # self.curMedRate = self.medModel.getDosage()
            self.medValues.append(self.medValues[-1] + float(self.curMedRate)/60 + self.decayRate(self.medValues[-1]))
            self.medModel.updateDosage(self.medValues[-1])
            self.y = sol.y

            self.computerCurMed = self.medComputerModel.calculateRate(self.computerParamValues[-1], (self.targetMap[self.param][0]+self.targetMap[self.param][1])*0.5)

            # self.computerCurMed = (self.computerParamValues[-1] - 100) * 0.001
            # if (self.computerCurMed < 0 ): self.computerCurMed = 0
            # if (self.computerCurMed > 0.2): self.computerCurMed = 0.2
            
            
            self.computerParamValues.append(computerSol.y[-1])
            # self.curMedRate = self.medModel.getDosage()
            self.computerMedValues.append(self.computerMedValues[-1] + float(self.computerCurMed)/60 + self.decayRate(self.computerMedValues[-1]))
            self.medComputerModel.updateDosage(self.computerMedValues[-1])

            # if more than 60 seconds have passed since the start of the
            # simulation, shift the plot to only display the last 60 seconds
            if self.curTime >= 60:
                self._param_ax.set_xlim(self.curTime - 59, self.curTime + 1)
                self._med_ax.set_xlim(self.curTime - 59, self.curTime + 1)
                self._param_ax.plot(self.times[-60:], self.paramValues[-60:], color='b')
                self._med_ax.plot(self.times[-60:], self.medValues[-60:], color='r')

                self._param_ax.plot(self.times[-60:], [self.targetLow] * 60, color='k')
                self._param_ax.plot(self.times[-60:], [self.targetHigh] * 60, color='k')
            else:
                self._param_ax.plot(self.times, self.paramValues, color='b')
                self._med_ax.plot(self.times, self.medValues, color='r')

                self._param_ax.plot([self.targetLow] * 60, color='k')
                self._param_ax.plot([self.targetHigh] * 60, color='k')

            self._param_line.figure.canvas.draw()
            self._med_line.figure.canvas.draw()

        if self.curTime == self.stopTime and self.metricsWindow==None:
            self.metricsWindow = MetricsWindow(self.paramValues, self.medValues, self.computerParamValues,
                                               self.computerMedValues, self.times, self.targetLow, self.targetHigh)
            self.metricsWindow.show()

    def keypadComponents(self):
        # create a layout to hold the keypad buttons
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
        #push1.setStyleSheet("border : 1px solid black;")
        #push1.setStyleSheet("background-color: white;")
        # push1.setGeometry(5, 150, 80, 40)
 
        # creating a push button
        push2 = QPushButton("2", self)
        #push2.setStyleSheet("background-color: white;")
        # push2.setGeometry(95, 150, 80, 40)
 
        # creating a push button
        push3 = QPushButton("3", self)
        #push3.setStyleSheet("background-color: white;")
        # push3.setGeometry(185, 150, 80, 40)
 
        # creating a push button
        push4 = QPushButton("4", self)
        #push4.setStyleSheet("background-color: white;")
        # push4.setGeometry(5, 200, 80, 40)
 
        # creating a push button
        push5 = QPushButton("5", self)
        #push5.setStyleSheet("background-color: white;")
        # push5.setGeometry(95, 200, 80, 40)
 
        # creating a push button
        push6 = QPushButton("6", self)
        #push6.setStyleSheet("background-color: white;")
        # push6.setGeometry(185, 200, 80, 40)
 
        # creating a push button
        push7 = QPushButton("7", self)
        #push7.setStyleSheet("background-color: white;")
        # push7.setGeometry(5, 250, 80, 40)
 
        # creating a push button
        push8 = QPushButton("8", self)
        #push8.setStyleSheet("background-color: white;")
        # push8.setGeometry(95, 250, 80, 40)
 
        # creating a push button
        push9 = QPushButton("9", self)
        #push9.setStyleSheet("background-color: white;")
        # push9.setGeometry(185, 250, 80, 40)
 
        # creating a push button
        push0 = QPushButton("0", self)
        #push0.setStyleSheet("background-color: white;")
        # push0.setGeometry(5, 300, 80, 40)
 
        # adding operator push button
        # creating push button
 
        # adding equal button a color effect
        c_effect = QGraphicsColorizeEffect()
        c_effect.setColor(Qt.blue)
 
        # creating push button
        push_OK = QPushButton("OK", self)
        #push_OK.setStyleSheet("background-color: white;")
        # push_OK.setGeometry(185, 300, 80, 40)
 
        # creating push button
        push_point = QPushButton(".", self)
        #push_point.setStyleSheet("background-color: white;")
        # push_point.setGeometry(95, 300, 80, 40)

        # clear button
        push_clear = QPushButton("Clear", self)
        #push_clear.setStyleSheet("background-color: white;")
        # push_clear.setGeometry(5, 100, 170, 40)
 
        # del one character button
        push_del = QPushButton("Del", self)
        #push_del.setStyleSheet("background-color: white;")
        # push_del.setGeometry(185, 100, 80, 40)

        # add buttons to the keypad layout
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

    def logComponents(self):
        self.logLayout = QtWidgets.QGridLayout()
        self.medRate = QLabel('Log of Medication Rates', self)
        #self.medRate.setStyleSheet("background-color: white;")
        self.medRate.setAlignment(Qt.AlignHCenter)
        
        self.logLayout.addWidget(self.medRate)

        self.curText = str(self.curMedRate) + "\n"
        self.values = QLabel(self.curText, self)
        self.values.setAlignment(Qt.AlignHCenter)

        self.scrollArea = QScrollArea()
        vbar = self.scrollArea.verticalScrollBar()
        vbar.setValue(vbar.maximum())
        self.scrollArea.setWidget(self.values)
        self.scrollArea.ensureWidgetVisible(self.values, 200, 200)
        self.scrollArea.setWidgetResizable(True)
        #self.scrollArea.setStyleSheet("background-color: white;")

        self.logLayout.addWidget(self.scrollArea)

        return self.logLayout
    
    
    def UIDropdownComponents(self):
        def actionSetParam():
            self.combobox2.clear()
            self.combobox2.addItems(self.medicationMap[self.combobox1.currentText()])
            
            self.model_selected = True
            return self.combobox1.currentText()

        # create layout to hold the dropdown menu
        self.dropdownLayout = QtWidgets.QGridLayout()

        self.model_selected = False  # whether a model has been selected

        self.paramLabel = QLabel('Choose Parameter', self)
        self.paramLabel.setAlignment(Qt.AlignHCenter)
        #self.paramLabel.setStyleSheet("background-color: white;")

        for item in self.parameters:
            self.combobox1.addItem(item)

        self.combobox1.activated.connect(actionSetParam)
        self.combobox1.setCurrentIndex(-1)

        self.medLabel = QLabel('Choose Medication', self)
        self.medLabel.setAlignment(Qt.AlignHCenter)
        #self.medLabel.setStyleSheet("background-color: white;")

        self.combobox2 = QComboBox()
        #self.combobox2.setStyleSheet("background-color: white;")

        self.startButton = QPushButton("Start Simulation", self)
        self.startButton.clicked.connect(self.startSimulation)
        #self.startButton.setStyleSheet("background-color: white;")

        verticalSpacer = QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

        # add buttons and dropdown menus to dropdown layout
        self.dropdownLayout.addItem(verticalSpacer, 0, 0)
        self.dropdownLayout.addWidget(self.paramLabel, 1, 0, 1, 2)
        self.dropdownLayout.addWidget(self.combobox1, 2, 0, 1, 2)

        file_dialog = QFileDialog(self)

        self.uploadModelButton = QPushButton("Upload Model", self)
        self.uploadModelButton.clicked.connect(lambda: self.getFile(file_dialog))
        #self.uploadModelButton.setStyleSheet("background-color: white;")
        self.dropdownLayout.addWidget(self.uploadModelButton, 3, 0, 1, 2)
        self.dropdownLayout.addItem(verticalSpacer, 4, 0)

        self.dropdownLayout.addWidget(self.medLabel, 5, 0, 1, 2)
        self.dropdownLayout.addWidget(self.combobox2, 6, 0, 1, 2)

        self.addMedButton = QPushButton("Add Medication", self)
        self.addMedButton.clicked.connect(lambda: self.addMed(file_dialog))
        #self.addMedButton.setStyleSheet("background-color: white;")

        self.dropdownLayout.addWidget(self.addMedButton, 7, 0, 1, 2)
        self.dropdownLayout.addItem(verticalSpacer, 8, 0)

        self.restartModelButton = QPushButton("Restart Simulation", self)
        self.restartModelButton.clicked.connect(self.restart)
        #self.restartModelButton.setStyleSheet("background-color: white;")

        self.dropdownLayout.addWidget(self.startButton, 9, 0, 1, 2)
        self.dropdownLayout.addWidget(self.restartModelButton, 10, 0, 1, 2)

        self.dropdownLayout.addItem(verticalSpacer, 11, 0)

        self.dropdownLayout.setSpacing(20)
        self.dropdownLayout.setContentsMargins(0,50,0,50)

        return self.dropdownLayout

    file_dialog = None

    def uploadModelComponent(self):
        self.uploadModelButtonLayout = QtWidgets.QGridLayout()
        file_dialog = QFileDialog(self)
            
        self.uploadModelButton = QPushButton("Upload Model", self)
        self.uploadModelButton.clicked.connect(lambda: self.getFile(file_dialog))
        #self.uploadModelButton.setStyleSheet("background-color: white;")

        self.addMedButton = QPushButton("Add Medication", self)
        self.addMedButton.clicked.connect(lambda: self.addMed(file_dialog))
        #self.addMedButton.setStyleSheet("background-color: white;")
        
        # self.uploadModelButton.clicked.connect(self.uploadToDict)
        self.uploadModelButtonLayout.addWidget(self.uploadModelButton, 0, 0)
        self.uploadModelButtonLayout.addWidget(self.addMedButton, 0, 1)
            
        self.restartModelButton = QPushButton("Restart Simulation", self)
        self.restartModelButton.clicked.connect(self.restart)
        #self.restartModelButton.setStyleSheet("background-color: white;")
        # self.uploadModelButton.clicked.connect(self.uploadToDict)
        self.uploadModelButtonLayout.addWidget(self.restartModelButton, 1,0)


        return self.uploadModelButtonLayout


    def restart(self):
        os.execl(sys.executable, sys.executable, *sys.argv)

    def addMed(self, fd):
        modelName, done = QtWidgets.QInputDialog.getText(self, 'Input Dialog', 'Enter Model to Add Medication:')
        medName, done2 = QtWidgets.QInputDialog.getText(self, 'Input Dialog', 'Enter Medication Name:')
        compModel, done3 = QtWidgets.QInputDialog.getItem(self, 'Input Dialog', 'Is this a computer model:', ['yes', 'no'])

        if done and done2 and done3:
            file_path, _ = fd.getOpenFileName(self, 'Open Medication Model', '', 'All Files (*);;Text Files (*.txt)')
            print(file_path)
            self.uploadedModelPath = file_path

            if (modelName in self.medicationMap.keys):
                self.medicationMap[modelName] = []

            self.medicationMap[modelName].append(medName)

            # self.medModelMap[medName] = 


    def getFile(self, fd):
        modelName, done = QtWidgets.QInputDialog.getText(
              self, 'Input Dialog', 'Enter Model Name:')
        
        if done:
        
            file_path, _ = fd.getOpenFileName(self, 'Open File', '', 'All Files (*);;Text Files (*.txt)')
            print(file_path)
            self.uploadedModelPath = file_path

            self.combobox1.addItem(modelName)

            return modelName, file_path

    def instructionPage(self):
        self.instructionPageLayout = QtWidgets.QGridLayout()

        wrapper = textwrap.TextWrapper(width=self.width/10)

        introText = "\nThe objective of this simulation is to bring a physiological parameter within a target range by adjusting the medication level.\n\nThe physiological parameter value is represented by the blue line. \n\nThe medication level is represented by the red line. \n\nThe target range is indicated by the area between the black lines on the graph."
        startText1 = "\nSelect a physiological parameter to simulate, using either the dropdown menu to select an existing model, or the upload model button to use a custom model. \n\nSelect a medication associated with the physiological parameter, using either the dropdown menu or the upload model button. \n\nPress \"Start Simulation\" to begin the simulation."
        startText2 = "The simulation will run for 3 minutes. \n\nUse the keypad to control the medication level by clicking the numbers on the keypad. \n\nWhen the simulation is complete, a new window will display metrics that compare your performance to a computer algorithm."
        # introFormat = wrapper.fill(text=introText)
        # startFormat = wrapper.fill(text=startText1)
        # endFormat = wrapper.fill(text=startText2)

        self.title = QLabel("Instructions")
        self.title.setAlignment(Qt.AlignHCenter)
        #self.title.setStyleSheet("background-color: white;")

        self.intro = QLabel(introText+"\n\n", self)
        self.intro.setWordWrap(True)
        self.intro.adjustSize()
        self.intro.setAlignment(Qt.AlignTop)
        #self.setMinimumSize(self.sizeHint())

        self.instructionPageLayout.addWidget(self.title, 0, 0)

        instructionScrollArea = QScrollArea()
        vbar = instructionScrollArea.verticalScrollBar()
        vbar.setValue(vbar.maximum())
        instructionScrollArea.setWidget(self.intro)
        instructionScrollArea.ensureWidgetVisible(self.intro, 200, 200)
        instructionScrollArea.setWidgetResizable(True)
        #instructionScrollArea.setStyleSheet("background-color: white;")

        self.instructionPageLayout.addWidget(instructionScrollArea, 1, 0)


        self.startTitle = QLabel("To Start")
        self.startTitle.setAlignment(Qt.AlignHCenter)
        #self.startTitle.setStyleSheet("background-color: white;")

        self.startInstructions = QLabel(startText1+"\n\n"+startText2, self)
        self.startInstructions.setWordWrap(True)
        self.startInstructions.adjustSize()
        self.startInstructions.setAlignment(Qt.AlignTop)

        startScrollArea = QScrollArea()
        vbar = startScrollArea.verticalScrollBar()
        vbar.setValue(vbar.maximum())
        startScrollArea.setWidget(self.startInstructions)
        startScrollArea.ensureWidgetVisible(self.startInstructions, 200, 200)
        startScrollArea.setWidgetResizable(True)
        #startScrollArea.setStyleSheet("background-color: white;")

        self.instructionPageLayout.addWidget(self.startTitle, 2, 0)
        self.instructionPageLayout.addWidget(startScrollArea, 3, 0)

        return self.instructionPageLayout

    def startSimulation(self):
        # starts the simulation
        if self.model_selected and not self.started:
            self.started = True
            self.param = self.combobox1.currentText()
            self.medication = self.combobox2.currentText()
            self.targetLow =  self.targetMap[self.param][0]
            self.targetHigh = self.targetMap[self.param][1]

            self.paramModel = self.paramModelMap[self.param](self.param, 0, self.alpha, 100)
            self.medModel = self.medModelMap[self.medication](self.medication, 0, self.alpha, 100)
            self.medComputerModel = self.medModelComputerlMap[self.medication](self.medication, 0, self.alpha, 100)
            
            self.composedModel = self.composeModels(self.paramModel, self.medModel)
            self.composedComputerModel = self.composeModels(self.paramModel, self.medComputerModel)

            # self.computerParamModel = self.computerModelMap[self.param](self.param, 0, self.alpha, 100)
            self._start_plot()
    
    def actionOK(self):
        try:
            equation = self.label.text()
            self.label.setText("")
            # self.medModel.updateDosage(eval(equation))
            self.curMedRate = eval(equation)
            self.savedTime = self.curTime
            self.initVal = [self.paramValues[-1]]
            self.curText = equation + "\n" + self.curText
            self.values.setText(self.curText)
            # self.reset = True
        except:
            print("Invalid")

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
        self.label.setText(text[:len(text)-1])

class MetricsWindow(QtWidgets.QMainWindow):
    def __init__(self, userVals, medVals, computerVals, computerMedVals, times, lowBound, highBound):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        self.layout = QtWidgets.QGridLayout(self._main)

        self.paramValues = np.array(userVals)
        self.medValues = np.array(medVals)
        self.computerParamValues = np.array(computerVals)
        self.computerMedValues = np.array(computerMedVals)
        self.times = np.array(times)


        df = pd.DataFrame(np.asarray([ times, self.paramValues, self.medValues, self.computerParamValues, self.computerMedValues ]))
        curr_dt = datetime.now()
        time = str(int(round(curr_dt.timestamp())))
        df.to_csv("./data/"+time+".csv")


        self.targetLow = lowBound
        self.targetHigh = highBound

        self.timeInIntervalLabel = QLabel("Time In Interval", self)
        self.timeInIntervalMetric = QLabel(
            str(self.calc_time_in_interval(self.paramValues, self.targetLow, self.targetHigh)), self)
        self.timeUntilIntervalLabel = QLabel("Time Until Interval", self)
        if self.calc_time_until_interval(self.paramValues, self.targetLow, self.targetHigh)==-1:
            self.timeUntilIntervalMetric = QLabel("N/A", self)
        else:
            self.timeUntilIntervalMetric = QLabel(
                str(self.calc_time_until_interval(self.paramValues, self.targetLow, self.targetHigh)), self)
        self.derivativeLabel = QLabel("Average Absolute Derivative", self)
        self.derivativeMetric = QLabel(str(self.calc_average_derivative(self.paramValues)), self)

        self.timeInIntervalMetricComputer = QLabel(
            str(self.calc_time_in_interval(self.computerParamValues, self.targetLow, self.targetHigh)), self)
        self.timeUntilIntervalMetricComputer = QLabel(
            str(self.calc_time_until_interval(self.computerParamValues, self.targetLow, self.targetHigh)), self)
        self.derivativeMetricComputer = QLabel(str(self.calc_average_derivative(self.computerParamValues)), self)
    
        self.title = QLabel("Metrics", self)
        self.userTitle = QLabel("User Metrics", self)
        self.computerTitle = QLabel("Algorithm Metrics", self)

        self.title.setAlignment(Qt.AlignCenter)
        self.userTitle.setAlignment(Qt.AlignCenter)
        self.computerTitle.setAlignment(Qt.AlignCenter)
        self.timeInIntervalLabel.setAlignment(Qt.AlignCenter)
        self.timeInIntervalMetric.setAlignment(Qt.AlignCenter)
        self.timeInIntervalMetricComputer.setAlignment(Qt.AlignCenter)
        self.timeUntilIntervalLabel.setAlignment(Qt.AlignCenter)
        self.timeUntilIntervalMetric.setAlignment(Qt.AlignCenter)
        self.timeUntilIntervalMetricComputer.setAlignment(Qt.AlignCenter)
        self.derivativeMetric.setAlignment(Qt.AlignCenter)
        self.derivativeMetricComputer.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.title, 0, 0)
        self.layout.addWidget(self.userTitle, 0, 1)
        self.layout.addWidget(self.computerTitle, 0, 2)
        self.layout.addWidget(self.timeInIntervalLabel, 1, 0)
        self.layout.addWidget(self.timeInIntervalMetric, 1, 1)
        self.layout.addWidget(self.timeInIntervalMetricComputer, 1, 2)
        self.layout.addWidget(self.timeUntilIntervalLabel, 2, 0)
        self.layout.addWidget(self.timeUntilIntervalMetric, 2, 1)
        self.layout.addWidget(self.timeUntilIntervalMetricComputer, 2, 2)
        self.layout.addWidget(self.derivativeLabel, 3, 0)
        self.layout.addWidget(self.derivativeMetric, 3, 1)
        self.layout.addWidget(self.derivativeMetricComputer, 3, 2)

        self.user_canvas = FigureCanvas(Figure(figsize=(10, 6)))

        # create axes for graphing parameter and medication values
        self._param_ax = self.user_canvas.figure.add_subplot(111)
        self._med_ax = self._param_ax.twinx()
        self._param_ax.set_xlabel('Time')
        self._param_ax.set_ylabel('Blood Pressure', color='b')
        self._med_ax.set_ylabel('Total Medication In the Body', color='r')
        self._param_ax.set_xlim(0, self.times[-1])
        self._param_ax.plot(self.times, self.paramValues, color='b')
        self._med_ax.plot(self.times, self.medValues, color='r')
        self._param_ax.plot(self.times, [self.targetLow] * len(self.times), color='k', linestyle='dashed')
        self._param_ax.plot(self.times, [self.targetHigh] * len(self.times), color='k', linestyle='dashed')

        self.layout.addWidget(self.user_canvas, 4, 1, 1, 1)

        # computer graph
        self.computer_canvas = FigureCanvas(Figure(figsize=(10, 6)))

        self._computer_param_ax = self.computer_canvas.figure.add_subplot(111)
        self._computer_med_ax = self._computer_param_ax.twinx()
        self._computer_param_ax.set_xlabel('Time')
        self._computer_param_ax.set_ylabel('Blood Pressure', color='b')
        self._computer_med_ax.set_ylabel('Total Medication In the Body', color='r')
        self._computer_param_ax.set_xlim(0, self.times[-1])
        self._computer_param_ax.plot(self.times, self.computerParamValues, color='b')
        self._computer_med_ax.plot(self.times, self.computerMedValues, color='r')
        self._computer_param_ax.plot(self.times, [self.targetLow] * len(self.times), color='k', linestyle='dashed')
        self._computer_param_ax.plot(self.times, [self.targetHigh] * len(self.times), color='k', linestyle='dashed')

        self.layout.addWidget(self.computer_canvas, 4, 2, 1, 1)

    def calc_time_in_interval(self, paramValues, targetLow, targetHigh):
        return sum(np.logical_and(paramValues >= targetLow, paramValues <= targetHigh))

    def calc_time_until_interval(self, paramValues, targetLow, targetHigh):
        in_interval = np.where(np.logical_and(paramValues >= targetLow, paramValues <= targetHigh))[0]

        if len(in_interval) == 0:
            return -1
        else:
            return in_interval[0]
    
    def calc_average_derivative(self, paramValues):
        diff = np.gradient(paramValues, 1)
        return np.sum(np.abs(diff))
        
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
