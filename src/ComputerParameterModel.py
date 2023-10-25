import random
import numpy as np
from scipy.integrate import solve_ivp

import matplotlib.pyplot as plt

from SimpleMedicationModel import SimpleMedicationModel

class ComputerParameterModel:
    def __init__(self, parameterName, dosage, alpha, target):
        self.param = parameterName
        self.dosage = dosage
        self.alpha = alpha
        self.target = target
    
    def updateDosage(self, newDosage):
        self.dosage = newDosage

    def userModel(self, t, y):
        parameterComponent = random.uniform(-0.005*self.alpha, 0.01*self.alpha)
        print(y)
        dosageRate = 0.1 * (y - self.target)
        print(self.target)
        if (dosageRate < 0): dosageRate = 0
        return (dosageRate + parameterComponent) * y

    def solve_ivp(self, tRange, y0):
        sol = solve_ivp(self.userModel, t_span=tRange, y0=y0, t_eval=np.linspace(tRange[0], tRange[1], tRange[1]+1))

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

    def get_param_name(self):
        return self.param