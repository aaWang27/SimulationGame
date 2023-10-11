import numpy as np
from scipy.integrate import solve_ivp

import matplotlib.pyplot as plt

from SimpleMedicationModel import SimpleMedicationModel

class SimpleParameterModel:
    def __init__(self, parameterName):
        self.param = parameterName

    def model(self, t, y):
        # TODO make random changes
        parameterComponent = 0.3
        return SimpleMedicationModel.something(t, y) + parameterComponent

    def solve_ivp(self, tRange, y0):
        sol = solve_ivp(self.model, t_span=tRange, y0=y0, t_eval=np.linspace(0, tRange[1], tRange[1]+1))

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