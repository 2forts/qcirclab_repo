"""Visualization and sampling helpers for qcirclab.

These functions are intentionally small and NumPy-based so they can be used
in notebooks and textbook examples without depending on external quantum SDKs.
"""

from __future__ import annotations

from collections import Counter
from typing import Mapping

import numpy as np


def pretty_state(state, n_qubits: int | None = None, atol: float = 1e-10) -> str:
    """Return a compact ket-string representation of a statevector.

    Basis labels follow qcirclab's book convention: qubit 0 appears on the
    left of the displayed bitstring.
    """
    state = np.asarray(state, dtype=complex).reshape(-1)
    if state.size == 0 or state.size & (state.size - 1):
        raise ValueError("state length must be a positive power of 2")

    if n_qubits is None:
        n_qubits = int(np.log2(state.size))
    if 2**n_qubits != state.size:
        raise ValueError("n_qubits is incompatible with state length")

    terms = []
    for i, amp in enumerate(state):
        if abs(amp) > atol:
            terms.append(f"({amp:.3g})|{i:0{n_qubits}b}>")
    return " + ".join(terms) if terms else "0"


def counts_from_probs(probs, shots: int = 1000, seed: int | None = None) -> dict[str, int]:
    """Sample computational-basis counts from a probability vector."""
    if shots < 0:
        raise ValueError("shots must be non-negative")

    rng = np.random.default_rng(seed)
    probs = np.asarray(probs, dtype=float).reshape(-1)
    if probs.size == 0 or probs.size & (probs.size - 1):
        raise ValueError("probability vector length must be a positive power of 2")
    if np.any(probs < -1e-12):
        raise ValueError("probabilities must be non-negative")

    probs = np.maximum(probs, 0.0)
    total = probs.sum()
    if total <= 0:
        raise ValueError("probabilities must sum to a positive value")
    probs = probs / total

    n = int(np.log2(len(probs)))
    samples = rng.choice(len(probs), size=shots, p=probs)
    return dict(Counter(format(i, f"0{n}b") for i in samples))


def sample_counts_from_statevector(
    state,
    shots: int = 1000,
    seed: int | None = None,
    measured_qubits: range | list[int] | tuple[int, ...] | None = None,
) -> dict[str, int]:
    """Sample counts from a statevector.

    If measured_qubits is provided, only those qubits are reported in the
    returned bitstrings, using qcirclab's displayed basis-string convention.
    """
    state = np.asarray(state, dtype=complex).reshape(-1)
    if state.size == 0 or state.size & (state.size - 1):
        raise ValueError("state length must be a positive power of 2")

    probs = np.abs(state) ** 2
    probs = probs / probs.sum()
    n = int(np.log2(state.size))

    if measured_qubits is None:
        return counts_from_probs(probs, shots=shots, seed=seed)

    measured = tuple(measured_qubits)
    if any(q < 0 or q >= n for q in measured):
        raise ValueError("measured_qubits contains an invalid qubit index")

    rng = np.random.default_rng(seed)
    samples = rng.choice(state.size, size=shots, p=probs)
    bitstrings = []
    for idx in samples:
        full = format(idx, f"0{n}b")
        bitstrings.append("".join(full[q] for q in measured))
    return dict(Counter(bitstrings))


def counts_to_probvec(counts: Mapping[str, int], n: int | None = None) -> np.ndarray:
    """Convert a counts dictionary into a probability vector."""
    if n is None:
        n = max(len(k) for k in counts) if counts else 1
    if n <= 0:
        raise ValueError("n must be positive")

    p = np.zeros(2**n, dtype=float)
    total = sum(counts.values())
    if total <= 0:
        return p

    for bitstr, c in counts.items():
        if len(bitstr) != n or set(bitstr) - {"0", "1"}:
            raise ValueError("counts keys must be n-bit strings")
        p[int(bitstr, 2)] += c / total
    return p


def plot_counts(counts: Mapping[str, int], title: str = "Counts") -> None:
    """Plot a simple bar chart for a counts dictionary."""
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover - depends on optional extra
        raise ImportError("plot_counts requires matplotlib") from exc

    items = sorted(counts.items())
    labels = [k for k, _ in items]
    values = [v for _, v in items]

    plt.figure(figsize=(max(5, 0.45 * len(labels)), 3.2))
    plt.bar(labels, values)
    plt.title(title)
    plt.xlabel("bitstring")
    plt.ylabel("counts")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
