class SimpleMedicationModel:
    def exponential_decay(t, y): return -0.5 * y

    def nothing(t, y): return 0

    def something(t, y): return -0.1 * y

    def variableDerivative(t, y, dosage): return -dosage * y
    
    def bodyMedicationADecay(totalMedication):
        return -0.5/60 if totalMedication > 0.5 else -totalMedication/60