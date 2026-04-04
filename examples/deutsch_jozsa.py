from qcirclab import deutsch_jozsa

qc = deutsch_jozsa(3, balanced_mask="101")
print(qc.draw())
print(qc.run(shots=256, seed=3).counts)
