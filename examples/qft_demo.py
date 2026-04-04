from qcirclab import Circuit, qft

prep = Circuit(3)
prep.initialize_basis("101")
prep.append(qft(3))
print(prep.draw())
print(prep.statevector())
