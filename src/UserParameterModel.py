import numpy as np
from scipy.integrate import solve_ivp

import matplotlib.pyplot as plt

from SimpleMedicationModel import SimpleMedicationModel

class UserParameterModel:
<<<<<<< HEAD
    def __init__(self, parameterName, dosage):
        self.param = parameterName
        self.dosage = dosage
=======
    def __init__(self, parameterName, medicationModel, rate):
        self.param = parameterName
        self.rate = rate
        self.medicationModel = medicationModel
>>>>>>> 0e5cfb6f074456ebb8f0cad6c75853c526378aff
    
    def updateDosage(self, newDosage):
        self.dosage = newDosage

    def userModel(self, t, y):
        # TODO make random changes
<<<<<<< HEAD
        parameterComponent = 0.01
        return SimpleMedicationModel.variableDerivative(t, y, self.dosage) + parameterComponent * y
=======
        parameterComponent = 0.1
        return self.medicationModel.variableDerivative(t, y, self.rate) + parameterComponent * y
>>>>>>> 0e5cfb6f074456ebb8f0cad6c75853c526378aff

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