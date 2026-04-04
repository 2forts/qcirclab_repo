from qcirclab import Circuit, cuccaro_adder

adder = cuccaro_adder(2)
qc = Circuit(adder.n_qubits)
qc.initialize_basis("01100")
qc.append(adder)
print(qc.draw())
print(qc.statevector())
