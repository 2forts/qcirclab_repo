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
    """Cuccaro/CDKM ripple-carry adder without incoming carry.

    Layout, LSB first within registers:
        a[0..n-1], b[0..n-1], z, c

    Action:
        |a>|b>|0>|0> -> |a>|(a+b) mod 2^n>|carry>|0>

    Total qubits:
        2*n + 2
    """
    if n <= 0:
        raise ValueError("n must be positive")

    qc = Circuit(2 * n + 2, 0, name=f"cuccaro_add_{n}")

    a = list(range(n))
    b = list(range(n, 2 * n))
    z = 2 * n
    c = 2 * n + 1

    # Forward sweep: propagate carries through the internal carry line c
    for i in range(n):
        majority(qc, a[i], b[i], c)

    # Copy final carry-out into z
    qc.cx(a[n - 1], z)

    # Backward sweep: uncompute carries and write sum into b
    for i in reversed(range(n)):
        unmajority(qc, a[i], b[i], c)

    return qc


def controlled_increment(n: int) -> Circuit:
    qc = Circuit(n + 1, 0, name=f"cinc_{n}")
    ctrl = 0
    reg = list(range(1, n + 1))
    qc.cx(ctrl, reg[-1])
    for i in reversed(range(n - 1)):
        qc.mcx([ctrl, *reg[i + 1 :]], reg[i])
    return qc
