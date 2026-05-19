"""Density-matrix and simple noise-channel helpers for qcirclab."""

from __future__ import annotations

import numpy as np

from . import gates as qg


def state_to_density(state) -> np.ndarray:
    """Convert a pure statevector into a density matrix."""
    state = np.asarray(state, dtype=complex).reshape(-1)
    if state.size == 0 or state.size & (state.size - 1):
        raise ValueError("state length must be a positive power of 2")
    norm = np.linalg.norm(state)
    if norm == 0:
        raise ValueError("statevector cannot be zero")
    state = state / norm
    return np.outer(state, state.conj())


def probabilities_from_density(rho) -> np.ndarray:
    """Return computational-basis probabilities from a density matrix."""
    rho = np.asarray(rho, dtype=complex)
    if rho.ndim != 2 or rho.shape[0] != rho.shape[1]:
        raise ValueError("rho must be a square matrix")
    probs = np.real(np.diag(rho))
    probs = np.maximum(probs, 0.0)
    total = probs.sum()
    if total <= 0:
        raise ValueError("density matrix has zero trace/probability")
    return probs / total


def kron_all(mats) -> np.ndarray:
    """Kronecker product of a sequence of matrices."""
    out = np.array([[1]], dtype=complex)
    for M in mats:
        out = np.kron(out, np.asarray(M, dtype=complex))
    return out


def expand_operator(local_op, targets, n_qubits: int) -> np.ndarray:
    """Embed a one-qubit operator into an n-qubit Hilbert space.

    This lightweight helper supports one-qubit targets, which is enough for
    the simple noise channels used in the textbook examples.
    """
    if n_qubits <= 0:
        raise ValueError("n_qubits must be positive")

    targets = tuple(targets)
    if len(targets) != 1:
        raise NotImplementedError("This helper currently embeds one-qubit operators")

    t = targets[0]
    if t < 0 or t >= n_qubits:
        raise ValueError("target qubit out of range")

    local_op = np.asarray(local_op, dtype=complex)
    if local_op.shape != (2, 2):
        raise ValueError("local_op must be a 2x2 matrix")

    mats = [qg.I2 for _ in range(n_qubits)]
    mats[t] = local_op
    return kron_all(mats)


def apply_kraus_to_qubit(rho, kraus_ops, qubit: int, n_qubits: int) -> np.ndarray:
    """Apply a one-qubit Kraus channel to a density matrix."""
    rho = np.asarray(rho, dtype=complex)
    expected_shape = (2**n_qubits, 2**n_qubits)
    if rho.shape != expected_shape:
        raise ValueError(f"rho must have shape {expected_shape}")

    out = np.zeros_like(rho, dtype=complex)
    for K in kraus_ops:
        K_full = expand_operator(K, [qubit], n_qubits)
        out += K_full @ rho @ K_full.conj().T
    return out


def amplitude_damping_kraus(gamma: float) -> list[np.ndarray]:
    """Kraus operators for one-qubit amplitude damping."""
    if not 0 <= gamma <= 1:
        raise ValueError("gamma must be between 0 and 1")
    return [
        np.array([[1, 0], [0, np.sqrt(1 - gamma)]], dtype=complex),
        np.array([[0, np.sqrt(gamma)], [0, 0]], dtype=complex),
    ]


def phase_damping_kraus(gamma: float) -> list[np.ndarray]:
    """Kraus operators for one-qubit phase damping."""
    if not 0 <= gamma <= 1:
        raise ValueError("gamma must be between 0 and 1")
    return [
        np.array([[1, 0], [0, np.sqrt(1 - gamma)]], dtype=complex),
        np.array([[0, 0], [0, np.sqrt(gamma)]], dtype=complex),
    ]


def depolarizing_channel(rho, p: float, qubit: int = 0, n_qubits: int = 1) -> np.ndarray:
    """Apply a one-qubit depolarizing channel to a density matrix."""
    if not 0 <= p <= 1:
        raise ValueError("p must be between 0 and 1")

    X = expand_operator(qg.X, [qubit], n_qubits)
    Y = expand_operator(qg.Y, [qubit], n_qubits)
    Z = expand_operator(qg.Z, [qubit], n_qubits)
    rho = np.asarray(rho, dtype=complex)
    return (1 - p) * rho + (p / 3) * (X @ rho @ X + Y @ rho @ Y + Z @ rho @ Z)


def expectation(rho, observable) -> float:
    """Expectation value Tr(O rho)."""
    rho = np.asarray(rho, dtype=complex)
    observable = np.asarray(observable, dtype=complex)
    if rho.shape != observable.shape:
        raise ValueError("rho and observable must have the same shape")
    return float(np.trace(observable @ rho).real)


def fidelity_pure_density(psi, rho) -> float:
    """Fidelity <psi|rho|psi> between a pure state and a density matrix."""
    psi = np.asarray(psi, dtype=complex).reshape(-1)
    rho = np.asarray(rho, dtype=complex)
    if rho.shape != (psi.size, psi.size):
        raise ValueError("rho shape is incompatible with psi")
    norm = np.linalg.norm(psi)
    if norm == 0:
        raise ValueError("psi cannot be zero")
    psi = psi / norm
    return float(np.real(psi.conj() @ rho @ psi))
