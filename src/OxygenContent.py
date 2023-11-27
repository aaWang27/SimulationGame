import random
import numpy as np
from scipy.integrate import solve_ivp

import matplotlib.pyplot as plt


class OxygenContent:
    def __init__(self, parameterName, dosage, alpha, target, meds=['a', 'b']):
        self.param = parameterName
        # self.dosage = dosage
        self.medications = meds
        self.alpha = alpha
    
    # def updateDosage(self, newDosage):
    #     if (newDosage >= 0.5):
    #         newDosage = 0.5
    #     self.dosage = newDosage
    
    # def getDosage(self):
    #     return self.dosage

    def parameterModel(self, t, y):
        parameterComponent = random.uniform(-0.1*self.alpha, 0.1*self.alpha)
        return parameterComponent * y

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