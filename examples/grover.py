from qcirclab import grover_two_qubit

qc = grover_two_qubit("10")
print(qc.draw())
print(qc.run(shots=256, seed=2).counts)
