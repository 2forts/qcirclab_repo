import math

import numpy as np

from qcirclab import Circuit, bell_pair, basic_metrics, cuccaro_adder, grover_two_qubit, qft, teleportation


def test_hadamard_statevector():
    qc = Circuit(1)
    qc.h(0)
    psi = qc.statevector()
    expected = np.array([1 / math.sqrt(2), 1 / math.sqrt(2)], dtype=complex)
    assert np.allclose(psi, expected)


def test_bell_counts():
    counts = bell_pair().run(shots=400, seed=1).counts
    assert set(counts) <= {"00", "11"}
    assert counts.get("00", 0) > 100
    assert counts.get("11", 0) > 100


def test_mid_circuit_control():
    qc = Circuit(2, 1)
    qc.x(0)
    qc.measure(0, 0)
    qc.x(1, condition=(0, 1))
    result = qc.run(shots=20, seed=1)
    assert set(result.counts) == {"1"}
    assert np.argmax(np.abs(result.final_state) ** 2) == 3


def test_qft_norm():
    qc = Circuit(3)
    qc.initialize_basis("101")
    qc.append(qft(3))
    psi = qc.statevector()
    assert np.isclose(np.linalg.norm(psi), 1.0)


def test_cuccaro_adder_runs():
    adder = cuccaro_adder(2)
    qc = Circuit(adder.n_qubits)
    qc.initialize_basis("01100")
    qc.append(adder)
    psi = qc.statevector()
    assert np.isclose(np.linalg.norm(psi), 1.0)


def test_metrics():
    qc = Circuit(2, 2)
    qc.h(0).cx(0, 1).measure_all()
    m = basic_metrics(qc)
    assert m["width"] == 2
    assert m["size"] == 4
    assert m["two_qubit_gates"] == 1
    assert m["depth"] >= 3


def test_teleportation_runs():
    qc = teleportation()
    result = qc.run(shots=10, seed=3)
    assert len(result.memory) == 10


def test_grover_runs():
    result = grover_two_qubit("10").run(shots=128, seed=7)
    assert result.counts.get("10", 0) > 80
