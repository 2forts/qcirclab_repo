"""Operator-level helpers for qcirclab circuits."""

from __future__ import annotations

import numpy as np

from .core import Circuit


def circuit_unitary(qc: Circuit) -> np.ndarray:
    """Compute the full unitary matrix of a measurement-free circuit.

    This routine is intended for small circuits. It scales exponentially with
    the number of qubits because it simulates the circuit on each basis vector.
    """
    n = qc.n_qubits
    U = np.zeros((2**n, 2**n), dtype=complex)
    for j in range(2**n):
        basis = np.zeros(2**n, dtype=complex)
        basis[j] = 1.0
        tmp = qc.copy().set_statevector(basis)
        U[:, j] = tmp.statevector()
    return U


def inverse_circuit(qc: Circuit, name: str = "inverse") -> Circuit:
    """Construct the inverse of a measurement-free circuit by reversing gates."""
    inv = Circuit(qc.n_qubits, qc.n_clbits, name=name)
    for op in reversed(qc.operations):
        if op.name in {"measure", "reset"}:
            raise ValueError("Cannot invert circuits with measurements or resets")
        if op.name == "barrier":
            continue
        if op.matrix is None:
            raise ValueError(f"Operation {op.name!r} has no matrix representation")
        inv.unitary(op.matrix.conj().T, op.targets, name=op.name + "dg", controls=op.controls)
    return inv
