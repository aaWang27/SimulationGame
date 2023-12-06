import random
import numpy as np
from scipy.integrate import solve_ivp

import matplotlib.pyplot as plt

from SimpleMedicationModel import SimpleMedicationModel

class MedicationOxygenModel:
    def __init__(self, parameterName, dosage, alpha, target):
        self.param = parameterName
        self.units = "mL"
        self.dosage = dosage
        # self.alpha = alpha
    
    def updateDosage(self, newDosage):
        if (newDosage >= 0.5):
            newDosage = 0.5
        self.dosage = newDosage
    
    def getDosage(self):
        return self.dosage

    def medModel(self, t, y):
        # parameterComponent = random.uniform(-0.005*self.alpha, 0.01*self.alpha)
        return self.dosage * y

    # def solve_ivp(self, tRange, y0):
    #     sol = solve_ivp(self.userModel, t_span=tRange, y0=y0, t_eval=np.linspace(tRange[0], tRange[1], tRange[1]+1))

    #     # print(sol.t)
    #     if(len(sol.t)>0):
    #         sol.y = sol.y.flatten()
    #     # print(sol.y)
    #     #
    #     # # Create the graph
    #     # plt.plot(sol.t, sol.y)
    #     #
    #     # # Add labels and a title
    #     # plt.xlabel('Time')
    #     # plt.ylabel(self.param)
    #     # plt.title(self.param + ' vs. Time')
    #     #
    #     # # Display the graph
    #     # plt.show()

    #     return sol

    def get_param_name(self):
        return self.param