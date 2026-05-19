"""Operator-level helpers for qcirclab circuits."""

from __future__ import annotations

import numpy as np

from .core import Circuit

def append_operation(dst: Circuit, op) -> Circuit:
    """Append a stored qcirclab operation to another circuit.

    This is mainly a utility for writing circuit transformations and small
    compilation passes. It preserves controls and classical conditions when
    possible.
    """
    if op.name == "barrier":
        dst.barrier()
        return dst

    if op.name == "measure":
        dst.measure(op.targets[0], op.ctargets[0])
        return dst

    if op.name == "reset":
        dst.reset(op.targets[0])
        return dst

    condition = None
    if op.condition is not None:
        condition = (op.condition.bit, op.condition.value)

    dst.unitary(
        op.matrix,
        op.targets,
        name=op.name,
        controls=op.controls,
        condition=condition,
    )
    return dst


def circuit_without_measurements(qc: Circuit) -> Circuit:
    """Return a copy of ``qc`` containing only its unitary operations.

    Measurements and resets are skipped. Barriers are preserved.
    Classical bits are omitted in the returned circuit.
    """
    out = Circuit(qc.n_qubits, 0, name=qc.name + "_unitary_part")
    for op in qc.operations:
        if op.name in {"measure", "reset"}:
            continue
        append_operation(out, op)
    return out


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

def equal_up_to_global_phase(
    U: np.ndarray,
    V: np.ndarray,
    atol: float = 1e-9,
) -> bool:
    """Return True if two matrices are equal up to a global phase."""
    U = np.asarray(U, dtype=complex)
    V = np.asarray(V, dtype=complex)

    if U.shape != V.shape:
        return False

    u = U.reshape(-1)
    v = V.reshape(-1)

    idx = None
    for k in range(len(v)):
        if abs(v[k]) > atol and abs(u[k]) > atol:
            idx = k
            break

    if idx is None:
        return np.allclose(U, V, atol=atol)

    phase = u[idx] / v[idx]
    return np.allclose(U, phase * V, atol=atol)

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
