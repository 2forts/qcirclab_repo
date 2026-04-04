from qcirclab import bell_pair

qc = bell_pair()
print(qc.draw())
print(qc.run(shots=512, seed=1).counts)
