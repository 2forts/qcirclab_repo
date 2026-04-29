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
    """Cuccaro ripple-carry adder.

    Layout:
        cin, a[0..n-1], b[0..n-1], cout

    Action:
        |0>|a>|b>|0> -> |0>|a>|(a+b) mod 2^n>|carry>

    The input carry cin is restored to 0.
    """
    if n <= 0:
        raise ValueError("n must be positive")

    total = 2*n + 2
    qc = Circuit(total, name=f"cuccaro_add_{n}")

    cin = 0
    a = list(range(1, 1+n))
    b = list(range(1+n, 1+2*n))
    cout = 1 + 2*n

    # Forward ripple.
    majority(qc, cin, b[0], a[0])
    for i in range(1, n):
        majority(qc, a[i-1], b[i], a[i])

    # Copy final carry.
    qc.cx(a[n-1], cout)

    # Backward uncompute.
    for i in reversed(range(1, n)):
        unmajority(qc, a[i-1], b[i], a[i])
    unmajority(qc, cin, b[0], a[0])

    return qc


def controlled_increment(n: int) -> Circuit:
    qc = Circuit(n + 1, 0, name=f"cinc_{n}")
    ctrl = 0
    reg = list(range(1, n + 1))
    qc.cx(ctrl, reg[-1])
    for i in reversed(range(n - 1)):
        qc.mcx([ctrl, *reg[i + 1 :]], reg[i])
    return qc
