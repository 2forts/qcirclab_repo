from qcirclab import teleportation

qc = teleportation()
print(qc.draw())
print(qc.run(shots=32, seed=5).memory[:10])
