from __future__ import annotations

from typing import Dict

from .core import Circuit



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
