from __future__ import annotations

from typing import Dict

from .core import Circuit

_NON_UNITARY_OR_META = {"barrier", "measure", "reset"}

def circuit_metrics(qc: Circuit) -> dict:
    """Return basic logical resource metrics for a circuit.

    The returned dictionary is intentionally simple and backend-independent.
    It is useful for comparing alternative circuit constructions before
    hardware-specific compilation.
    """
    counts = qc.count_ops()

    two_qubit = sum(
        1
        for op in qc.operations
        if op.name not in _NON_UNITARY_OR_META
        and len(op.targets) + len(op.controls) == 2
    )

    multi_qubit = sum(
        1
        for op in qc.operations
        if op.name not in _NON_UNITARY_OR_META
        and len(op.targets) + len(op.controls) >= 3
    )

    return {
        "qubits": qc.n_qubits,
        "classical_bits": qc.n_clbits,
        "operations": qc.size(),
        "depth": qc.depth(),
        "two_qubit_gates": two_qubit,
        "multi_qubit_gates": multi_qubit,
        "gate_counts": counts,
    }

def print_metrics(label: str, qc: Circuit) -> None:
    """Print a readable resource-metric report."""
    print(f"=== {label} ===")
    for key, value in circuit_metrics(qc).items():
        print(f"{key}: {value}")
    print()
    
def basic_metrics(circuit: Circuit) -> Dict[str, object]:
    ops = circuit.count_ops()
    two_qubit = sum(ops.get(g, 0) for g in ("cx", "cz", "cp", "swap"))
    return {
        "width": circuit.n_qubits,
        "clbits": circuit.n_clbits,
        "size": circuit.size(),
        "depth": circuit.depth(),
        "two_qubit_gates": two_qubit,
        "ops": ops,
    }
