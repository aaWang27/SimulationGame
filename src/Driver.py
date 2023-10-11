import sys
import time

import numpy as np
from PyQt5.QtCore import QRect

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import \
    NavigationToolbar2QT as NavigationToolbar
# from matplotlib.backends.qt_compat import QtWidgets
from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.figure import Figure

import SimpleMedicationModel as MedModel
from SimpleParameterModel import SimpleParameterModel as ParamModel


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()

        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)
        layout.setGeometry(QRect(10, 10, 100, 200))
        self._main.setGeometry(0, 0, 500, 300)
        self._main.setWindowTitle('Simulation Game')

        self.paramModel = ParamModel("Blood Pressure")

        self.dynamic_canvas = FigureCanvas(Figure(figsize=(10, 6)))
        layout.addWidget(self.dynamic_canvas)
        layout.addWidget(NavigationToolbar(self.dynamic_canvas, self))

        self._dynamic_ax = self.dynamic_canvas.figure.subplots()

        # Set up a Line2D.
        self._dynamic_ax.set_xlim(0, 60)
        self._start_plot()

    def _start_plot(self):
        self.curTime = 0

        sol = self.paramModel.solve_ivp([0, self.curTime], [2])

        self._dynamic_ax.set_xlabel('Time')
        self._dynamic_ax.set_ylabel(self.paramModel.get_param_name())
        self._line, = self._dynamic_ax.plot(sol.t, sol.y, color='b')
        self._timer = self.dynamic_canvas.new_timer()
        self._timer.add_callback(self._update_canvas)
        self._timer.start()

    def _update_canvas(self):
        self.curTime += 1
        sol = self.paramModel.solve_ivp([0, self.curTime], [2])
        if self.curTime > 60:
            self._dynamic_ax.set_xlim(self.curTime - 59, self.curTime + 1)
        self._dynamic_ax.plot(sol.t, sol.y, color='b')
        self._line.figure.canvas.draw()


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
