class SimpleMedicationModel:
    def exponential_decay(t, y): return -0.5 * y
    def nothing(t, y): return 0
    def something(t, y): return -0.1 * y

    def variableDerivative(t, y, rate): return -rate  * y