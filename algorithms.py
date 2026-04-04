from __future__ import annotations

import math
from typing import Callable, Sequence

import numpy as np

from .core import Circuit
from .gates import phase



def bell_pair() -> Circuit:
    qc = Circuit(2, 2, name="bell_pair")
    qc.h(0).cx(0, 1).measure_all()
    return qc



def ghz(n: int) -> Circuit:
    qc = Circuit(n, n, name="ghz")
    qc.h(0)
    for q in range(n - 1):
        qc.cx(q, q + 1)
    qc.measure_all()
    return qc



def teleportation() -> Circuit:
    qc = Circuit(3, 2, name="teleportation")
    qc.h(1).cx(1, 2)
    qc.cx(0, 1).h(0)
    qc.measure(0, 0).measure(1, 1)
    qc.x(2, condition=(1, 1))
    qc.z(2, condition=(0, 1))
    return qc



def deutsch(oracle_is_constant_zero: bool = True) -> Circuit:
    qc = Circuit(2, 1, name="deutsch")
    qc.x(1).h(0).h(1)
    if not oracle_is_constant_zero:
        qc.cx(0, 1)
    qc.h(0).measure(0, 0)
    return qc



def bernstein_vazirani(secret: str) -> Circuit:
    n = len(secret)
    qc = Circuit(n + 1, n, name="bernstein_vazirani")
    anc = n
    qc.x(anc)
    for q in range(n + 1):
        qc.h(q)
    for i, bit in enumerate(secret):
        if bit == "1":
            qc.cx(i, anc)
    for q in range(n):
        qc.h(q).measure(q, q)
    return qc



def deutsch_jozsa(n: int, balanced_mask: str | None = None) -> Circuit:
    qc = Circuit(n + 1, n, name="deutsch_jozsa")
    anc = n
    qc.x(anc)
    for q in range(n + 1):
        qc.h(q)
    if balanced_mask is not None:
        if len(balanced_mask) != n:
            raise ValueError("balanced_mask must have length n")
        for i, bit in enumerate(balanced_mask):
            if bit == "1":
                qc.cx(i, anc)
    for q in range(n):
        qc.h(q).measure(q, q)
    return qc



def qft(n: int, inverse: bool = False, include_swaps: bool = True) -> Circuit:
    qc = Circuit(n, n if inverse else 0, name="iqft" if inverse else "qft")
    qubits = range(n)
    if not inverse:
        for j in range(n):
            qc.h(j)
            for k in range(j + 1, n):
                qc.cp(math.pi / (2 ** (k - j)), k, j)
    else:
        for j in reversed(range(n)):
            for k in reversed(range(j + 1, n)):
                qc.cp(-math.pi / (2 ** (k - j)), k, j)
            qc.h(j)
    if include_swaps:
        for i in range(n // 2):
            qc.swap(i, n - i - 1)
    return qc



def phase_estimation(unitary: np.ndarray, ancilla_bits: int) -> Circuit:
    if unitary.shape != (2, 2):
        raise ValueError("This simplified phase estimation helper expects a 2x2 unitary")
    qc = Circuit(ancilla_bits + 1, ancilla_bits, name="qpe")
    target = ancilla_bits
    qc.x(target)
    for j in range(ancilla_bits):
        qc.h(j)
        powered = np.linalg.matrix_power(unitary, 2 ** (ancilla_bits - j - 1))
        qc.unitary(powered, [target], name="u", controls=[j])
    qc.compose(qft(ancilla_bits, inverse=True, include_swaps=True), qubits=range(ancilla_bits))
    for j in range(ancilla_bits):
        qc.measure(j, j)
    return qc



def grover_two_qubit(marked: str = "11") -> Circuit:
    if marked not in {"00", "01", "10", "11"}:
        raise ValueError("marked must be a two-bit string")
    qc = Circuit(2, 2, name="grover_2q")
    qc.h(0).h(1)
    oracle_for_marked(qc, marked)
    diffusion_2q(qc)
    qc.measure_all()
    return qc



def oracle_for_marked(qc: Circuit, marked: str) -> None:
    if marked[0] == "0":
        qc.x(0)
    if marked[1] == "0":
        qc.x(1)
    qc.h(1).cx(0, 1).h(1)
    if marked[0] == "0":
        qc.x(0)
    if marked[1] == "0":
        qc.x(1)



def diffusion_2q(qc: Circuit) -> None:
    qc.h(0).h(1)
    qc.x(0).x(1)
    qc.h(1).cx(0, 1).h(1)
    qc.x(0).x(1)
    qc.h(0).h(1)



def phase_oracle_from_boolean(fn: Callable[[str], bool], n: int) -> Circuit:
    qc = Circuit(n, 0, name="phase_oracle")
    phases = []
    for idx in range(2**n):
        bitstring = format(idx, f"0{n}b")
        phases.append(-1 if fn(bitstring) else 1)
    qc.unitary(np.diag(phases).astype(complex), list(range(n)), name="oracle")
    return qc



def variational_layer(n: int, params: Sequence[float]) -> Circuit:
    if len(params) != 2 * n:
        raise ValueError("variational_layer expects 2*n parameters")
    qc = Circuit(n, 0, name="variational_layer")
    for q in range(n):
        qc.ry(params[2 * q], q)
        qc.rz(params[2 * q + 1], q)
    for q in range(n - 1):
        qc.cx(q, q + 1)
    return qc
