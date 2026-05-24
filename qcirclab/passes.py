from __future__ import annotations

from typing import Iterable, Protocol

from .core import Circuit


class CircuitPass(Protocol):
    """Protocol for minimal educational circuit passes."""

    property_set: dict

    def run(self, qc: Circuit) -> Circuit:
        ...


class AnalysisPass:
    """Minimal analysis pass with a shared property set.

    Analysis passes inspect a circuit and may store information in
    ``property_set``. They return the input circuit unchanged.
    """

    def __init__(self) -> None:
        self.property_set: dict = {}

    def run(self, qc: Circuit) -> Circuit:
        return qc


class TransformationPass:
    """Minimal transformation pass with a shared property set.

    Transformation passes return a circuit, which may be the original
    circuit or a transformed copy.
    """

    def __init__(self) -> None:
        self.property_set: dict = {}

    def run(self, qc: Circuit) -> Circuit:
        return qc


class PassPipeline:
    """Apply passes sequentially, sharing a single property set.

    This is intentionally small. It is meant for notebook-level
    optimization examples, not as a full compiler infrastructure.
    """

    def __init__(self, passes: Iterable[CircuitPass]) -> None:
        self.passes = list(passes)
        self.property_set: dict = {}

    def run(self, qc: Circuit) -> Circuit:
        out = qc

        for circuit_pass in self.passes:
            circuit_pass.property_set = self.property_set
            out = circuit_pass.run(out)
            self.property_set = circuit_pass.property_set

        return out
