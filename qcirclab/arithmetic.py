from __future__ import annotations

from .core import Circuit



def majority(qc: Circuit, a: int, b: int, c: int) -> None:
    qc.cx(c, b)
    qc.cx(c, a)
    qc.ccx(a, b, c)



def unmajority(qc: Circuit, a: int, b: int, c: int) -> None:
    qc.ccx(a, b, c)
    qc.cx(c, a)
    qc.cx(a, b)



def cuccaro_adder(n: int) -> Circuit:
    """In-place ripple-carry adder on registers a, b with carry ancilla.

    Wire layout: a[0..n-1], b[0..n-1], carry.
    After execution: b <- a + b (mod 2^n), carry stores the overflow bit.
    """
    qc = Circuit(2 * n + 1, 0, name=f"cuccaro_add_{n}")
    a = list(range(n))
    b = list(range(n, 2 * n))
    c = 2 * n

    majority(qc, a[0], b[0], c)
    for i in range(1, n):
        majority(qc, a[i], b[i], b[i - 1])
    qc.cx(a[n - 1], c)
    for i in reversed(range(1, n)):
        unmajority(qc, a[i], b[i], b[i - 1])
    unmajority(qc, a[0], b[0], c)
    return qc



def controlled_increment(n: int) -> Circuit:
    qc = Circuit(n + 1, 0, name=f"cinc_{n}")
    ctrl = 0
    reg = list(range(1, n + 1))
    qc.cx(ctrl, reg[-1])
    for i in reversed(range(n - 1)):
        qc.mcx([ctrl, *reg[i + 1 :]], reg[i])
    return qc
