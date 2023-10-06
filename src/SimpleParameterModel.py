import numpy as np
from scipy.integrate import solve_ivp

import matplotlib.pyplot as plt

from SimpleMedicationModel import SimpleMedicationModel

def model(t, y):
    # TODO make random changes
    parameterComponent = 0.3
    return SimpleMedicationModel.something(t, y) + parameterComponent


sol = solve_ivp(model, [0, 10], [2])


print(sol.t)
sol.y = sol.y.flatten()
print(sol.y)


# Create the graph
plt.plot(sol.t, sol.y)

# Add labels and a title
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title('Simple Line Graph')

# Display the graph
plt.show()