from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

from . import gates


@dataclass
class Condition:
    bit: int
    value: int


@dataclass
class Operation:
    name: str
    targets: Tuple[int, ...]
    matrix: Optional[np.ndarray] = None
    controls: Tuple[int, ...] = field(default_factory=tuple)
    condition: Optional[Condition] = None
    ctargets: Tuple[int, ...] = field(default_factory=tuple)
    params: Tuple[float, ...] = field(default_factory=tuple)

    def label(self) -> str:
        if self.name == "measure":
            return "M"
        return self.name.upper()


class Circuit:
    """A minimal circuit DSL for educational quantum circuit work.

    Qubit 0 is the top wire in drawings and the most significant bit in basis labels.
    """

    def __init__(self, n_qubits: int, n_clbits: int = 0, name: str = "circuit") -> None:
        if n_qubits <= 0:
            raise ValueError("n_qubits must be positive")
        if n_clbits < 0:
            raise ValueError("n_clbits must be non-negative")
        self.n_qubits = n_qubits
        self.n_clbits = n_clbits
        self.name = name
        self.operations: List[Operation] = []
        self._initial_state = np.zeros(2**n_qubits, dtype=complex)
        self._initial_state[0] = 1.0

    def copy(self) -> "Circuit":
        other = Circuit(self.n_qubits, self.n_clbits, self.name)
        other.operations = list(self.operations)
        other._initial_state = self._initial_state.copy()
        return other

    def set_statevector(self, state: Sequence[complex]) -> "Circuit":
        arr = np.asarray(state, dtype=complex)
        if arr.shape != (2**self.n_qubits,):
            raise ValueError("statevector has incompatible size")
        norm = np.linalg.norm(arr)
        if norm == 0:
            raise ValueError("statevector cannot be zero")
        self._initial_state = arr / norm
        return self

    def initialize_basis(self, bitstring: str) -> "Circuit":
        if len(bitstring) != self.n_qubits or any(b not in "01" for b in bitstring):
            raise ValueError("bitstring must have length n_qubits and contain only 0/1")
        index = int(bitstring, 2)
        self._initial_state = np.zeros(2**self.n_qubits, dtype=complex)
        self._initial_state[index] = 1.0
        return self

    def barrier(self) -> "Circuit":
        self.operations.append(Operation(name="barrier", targets=tuple(range(self.n_qubits))))
        return self

    def gate(
        self,
        name: str,
        matrix: np.ndarray,
        targets: Sequence[int],
        *,
        controls: Sequence[int] = (),
        condition: Optional[Tuple[int, int]] = None,
        params: Sequence[float] = (),
    ) -> "Circuit":
        cond = Condition(*condition) if condition is not None else None
        targets_tuple = tuple(targets)
        controls_tuple = tuple(controls)
        self._validate_qubits((*targets_tuple, *controls_tuple))
        if set(targets_tuple) & set(controls_tuple):
            raise ValueError("targets and controls must be disjoint")
        expected = 2 ** len(targets_tuple)
        arr = np.asarray(matrix, dtype=complex)
        if arr.shape != (expected, expected):
            raise ValueError(f"matrix must have shape {(expected, expected)}")
        self.operations.append(
            Operation(
                name=name,
                targets=targets_tuple,
                matrix=arr,
                controls=controls_tuple,
                condition=cond,
                params=tuple(params),
            )
        )
        return self

    def unitary(
        self,
        matrix: np.ndarray,
        targets: Sequence[int],
        *,
        name: str = "u",
        controls: Sequence[int] = (),
        condition: Optional[Tuple[int, int]] = None,
    ) -> "Circuit":
        return self.gate(name, matrix, targets, controls=controls, condition=condition)

    def h(self, q: int, *, condition: Optional[Tuple[int, int]] = None) -> "Circuit":
        return self.gate("h", gates.H, [q], condition=condition)

    def x(self, q: int, *, condition: Optional[Tuple[int, int]] = None) -> "Circuit":
        return self.gate("x", gates.X, [q], condition=condition)

    def y(self, q: int, *, condition: Optional[Tuple[int, int]] = None) -> "Circuit":
        return self.gate("y", gates.Y, [q], condition=condition)

    def z(self, q: int, *, condition: Optional[Tuple[int, int]] = None) -> "Circuit":
        return self.gate("z", gates.Z, [q], condition=condition)

    def s(self, q: int, *, condition: Optional[Tuple[int, int]] = None) -> "Circuit":
        return self.gate("s", gates.S, [q], condition=condition)

    def sdg(self, q: int, *, condition: Optional[Tuple[int, int]] = None) -> "Circuit":
        return self.gate("sdg", gates.SDG, [q], condition=condition)

    def t(self, q: int, *, condition: Optional[Tuple[int, int]] = None) -> "Circuit":
        return self.gate("t", gates.T, [q], condition=condition)

    def tdg(self, q: int, *, condition: Optional[Tuple[int, int]] = None) -> "Circuit":
        return self.gate("tdg", gates.TDG, [q], condition=condition)

    def sx(self, q: int, *, condition: Optional[Tuple[int, int]] = None) -> "Circuit":
        return self.gate("sx", gates.SX, [q], condition=condition)

    def sxdg(self, q: int, *, condition: Optional[Tuple[int, int]] = None) -> "Circuit":
        return self.gate("sxdg", gates.SXDG, [q], condition=condition)

    def rx(self, theta: float, q: int, *, condition: Optional[Tuple[int, int]] = None) -> "Circuit":
        return self.gate("rx", gates.rx(theta), [q], condition=condition, params=[theta])

    def ry(self, theta: float, q: int, *, condition: Optional[Tuple[int, int]] = None) -> "Circuit":
        return self.gate("ry", gates.ry(theta), [q], condition=condition, params=[theta])

    def rz(self, theta: float, q: int, *, condition: Optional[Tuple[int, int]] = None) -> "Circuit":
        return self.gate("rz", gates.rz(theta), [q], condition=condition, params=[theta])

    def p(self, theta: float, q: int, *, condition: Optional[Tuple[int, int]] = None) -> "Circuit":
        return self.gate("p", gates.phase(theta), [q], condition=condition, params=[theta])

    def u(self, theta: float, phi: float, lam: float, q: int, *, condition: Optional[Tuple[int, int]] = None) -> "Circuit":
        return self.gate("u", gates.u(theta, phi, lam), [q], condition=condition, params=[theta, phi, lam])

    def cx(self, control: int, target: int, *, condition: Optional[Tuple[int, int]] = None) -> "Circuit":
        return self.gate("cx", gates.X, [target], controls=[control], condition=condition)

    def cz(self, control: int, target: int, *, condition: Optional[Tuple[int, int]] = None) -> "Circuit":
        return self.gate("cz", gates.Z, [target], controls=[control], condition=condition)

    def cp(self, theta: float, control: int, target: int, *, condition: Optional[Tuple[int, int]] = None) -> "Circuit":
        return self.gate("cp", gates.phase(theta), [target], controls=[control], condition=condition, params=[theta])

    def swap(self, q0: int, q1: int, *, condition: Optional[Tuple[int, int]] = None) -> "Circuit":
        return self.gate("swap", gates.swap(), [q0, q1], condition=condition)

    def ccx(self, c0: int, c1: int, target: int, *, condition: Optional[Tuple[int, int]] = None) -> "Circuit":
        return self.gate("ccx", gates.X, [target], controls=[c0, c1], condition=condition)

    def mcx(self, controls: Sequence[int], target: int, *, condition: Optional[Tuple[int, int]] = None) -> "Circuit":
        return self.gate("mcx", gates.X, [target], controls=controls, condition=condition)

    def measure(self, qubit: int, cbit: int) -> "Circuit":
        self._validate_qubits([qubit])
        self._validate_clbits([cbit])
        self.operations.append(Operation(name="measure", targets=(qubit,), ctargets=(cbit,)))
        return self

    def measure_all(self) -> "Circuit":
        if self.n_clbits < self.n_qubits:
            raise ValueError("measure_all requires at least as many classical bits as qubits")
        for q in range(self.n_qubits):
            self.measure(q, q)
        return self

    def reset(self, qubit: int) -> "Circuit":
        self._validate_qubits([qubit])
        self.operations.append(Operation(name="reset", targets=(qubit,)))
        return self

    def compose(
        self,
        other: "Circuit",
        qubits: Optional[Sequence[int]] = None,
        clbits: Optional[Sequence[int]] = None,
    ) -> "Circuit":
        qmap = tuple(range(other.n_qubits)) if qubits is None else tuple(qubits)
        cmap = tuple(range(other.n_clbits)) if clbits is None else tuple(clbits)
        if len(qmap) != other.n_qubits or len(cmap) != other.n_clbits:
            raise ValueError("mapping sizes must match the other circuit")
        self._validate_qubits(qmap)
        self._validate_clbits(cmap)
        for op in other.operations:
            mapped_targets = tuple(qmap[q] for q in op.targets)
            mapped_controls = tuple(qmap[q] for q in op.controls)
            mapped_ctargets = tuple(cmap[c] for c in op.ctargets)
            mapped_condition = None
            if op.condition is not None:
                mapped_condition = Condition(bit=cmap[op.condition.bit], value=op.condition.value)
            self.operations.append(
                Operation(
                    name=op.name,
                    targets=mapped_targets,
                    matrix=None if op.matrix is None else op.matrix.copy(),
                    controls=mapped_controls,
                    condition=mapped_condition,
                    ctargets=mapped_ctargets,
                    params=op.params,
                )
            )
        return self

    def append(self, other: "Circuit", *, qubits: Optional[Sequence[int]] = None, clbits: Optional[Sequence[int]] = None) -> "Circuit":
        return self.compose(other, qubits=qubits, clbits=clbits)

    def size(self) -> int:
        return sum(op.name != "barrier" for op in self.operations)

    def count_ops(self) -> Dict[str, int]:
        counts = Counter(op.name for op in self.operations if op.name != "barrier")
        return dict(counts)

    def depth(self) -> int:
        qlayers = [0] * self.n_qubits
        clayers = [0] * self.n_clbits
        max_depth = 0
        for op in self.operations:
            if op.name == "barrier":
                barrier_depth = max(max(qlayers, default=0), max(clayers, default=0)) + 1
                qlayers = [max(v, barrier_depth) for v in qlayers]
                clayers = [max(v, barrier_depth) for v in clayers]
                max_depth = max(max_depth, barrier_depth)
                continue
            used_q = set(op.targets) | set(op.controls)
            used_c = set(op.ctargets)
            if op.condition is not None:
                used_c.add(op.condition.bit)
            layer = 1
            if used_q:
                layer = max(layer, max(qlayers[q] for q in used_q) + 1)
            if used_c:
                layer = max(layer, max(clayers[c] for c in used_c) + 1)
            for q in used_q:
                qlayers[q] = layer
            for c in used_c:
                clayers[c] = layer
            max_depth = max(max_depth, layer)
        return max_depth

    def statevector(self) -> np.ndarray:
        state = self._initial_state.copy()
        classical = [0] * self.n_clbits
        for op in self.operations:
            if op.name == "barrier":
                continue
            if op.condition is not None and classical[op.condition.bit] != op.condition.value:
                continue
            if op.name == "measure":
                raise ValueError("statevector() is only defined for circuits without measurements")
            if op.name == "reset":
                state = _reset_qubit(state, self.n_qubits, op.targets[0])
                continue
            state = _apply_operation_to_state(state, self.n_qubits, op)
        return state

    def run(self, shots: int = 1024, seed: Optional[int] = None) -> "Result":
        rng = np.random.default_rng(seed)
        counts: Counter[str] = Counter()
        memory: List[str] = []
        final_state = None
        final_classical = None
        snapshots = []
        for shot_idx in range(shots):
            state = self._initial_state.copy()
            classical = [0] * self.n_clbits
            shot_snapshots = []
            for op in self.operations:
                if op.name == "barrier":
                    continue
                if op.condition is not None and classical[op.condition.bit] != op.condition.value:
                    continue
                if op.name == "measure":
                    bit = _measure_qubit(state, self.n_qubits, op.targets[0], rng)
                    classical[op.ctargets[0]] = bit
                    shot_snapshots.append((op.name, state.copy(), tuple(classical)))
                    continue
                if op.name == "reset":
                    state = _reset_qubit(state, self.n_qubits, op.targets[0])
                    shot_snapshots.append((op.name, state.copy(), tuple(classical)))
                    continue
                state = _apply_operation_to_state(state, self.n_qubits, op)
                shot_snapshots.append((op.name, state.copy(), tuple(classical)))
            bitstring = "".join(str(b) for b in classical)
            counts[bitstring] += 1
            memory.append(bitstring)
            if shot_idx == shots - 1:
                final_state = state
                final_classical = tuple(classical)
                snapshots = shot_snapshots
        return Result(
            counts=dict(counts),
            memory=memory,
            final_state=final_state,
            final_classical=final_classical,
            snapshots=snapshots,
        )

    def sample_counts(self, shots: int = 1024, seed: Optional[int] = None) -> Dict[str, int]:
        return self.run(shots=shots, seed=seed).counts

    def draw(self) -> str:
        from .draw import ascii_draw

        return ascii_draw(self)

    def _validate_qubits(self, qubits: Iterable[int]) -> None:
        for q in qubits:
            if q < 0 or q >= self.n_qubits:
                raise IndexError(f"invalid qubit index {q}")

    def _validate_clbits(self, clbits: Iterable[int]) -> None:
        for c in clbits:
            if c < 0 or c >= self.n_clbits:
                raise IndexError(f"invalid classical bit index {c}")


@dataclass
class Result:
    counts: Dict[str, int]
    memory: List[str]
    final_state: Optional[np.ndarray]
    final_classical: Optional[Tuple[int, ...]]
    snapshots: List[Tuple[str, np.ndarray, Tuple[int, ...]]]

    def probabilities(self) -> Dict[str, float]:
        total = sum(self.counts.values())
        if total == 0:
            return {}
        return {k: v / total for k, v in self.counts.items()}



def _apply_operation_to_state(state: np.ndarray, n_qubits: int, op: Operation) -> np.ndarray:
    full = _expanded_operator(n_qubits, op.matrix, op.targets, op.controls)
    return full @ state



def _expanded_operator(
    n_qubits: int, matrix: np.ndarray, targets: Sequence[int], controls: Sequence[int]
) -> np.ndarray:
    dim = 2**n_qubits
    result = np.eye(dim, dtype=complex)
    target_masks = [_mask_for_qubit(n_qubits, q) for q in targets]
    control_masks = [_mask_for_qubit(n_qubits, q) for q in controls]

    result[:] = 0
    for col in range(dim):
        if any((col & mask) == 0 for mask in control_masks):
            result[col, col] = 1.0
            continue
        sub_index = 0
        for q in targets:
            sub_index = (sub_index << 1) | _bit_at(col, n_qubits, q)
        for row_sub in range(2 ** len(targets)):
            amp = matrix[row_sub, sub_index]
            if abs(amp) == 0:
                continue
            row = col
            for idx, q in enumerate(targets):
                desired = (row_sub >> (len(targets) - 1 - idx)) & 1
                row = _set_bit(row, n_qubits, q, desired)
            result[row, col] += amp
    return result



def _measure_qubit(state: np.ndarray, n_qubits: int, qubit: int, rng: np.random.Generator) -> int:
    mask = _mask_for_qubit(n_qubits, qubit)
    p1 = float(np.sum(np.abs(state[(np.arange(state.size) & mask) != 0]) ** 2))
    bit = int(rng.random() < p1)
    if bit == 1:
        state[(np.arange(state.size) & mask) == 0] = 0
    else:
        state[(np.arange(state.size) & mask) != 0] = 0
    norm = np.linalg.norm(state)
    if norm == 0:
        raise RuntimeError("measurement collapsed to zero norm state")
    state /= norm
    return bit



def _reset_qubit(state: np.ndarray, n_qubits: int, qubit: int) -> np.ndarray:
    measured = state.copy()
    bit = _measure_qubit(measured, n_qubits, qubit, np.random.default_rng())
    if bit == 1:
        flip = Operation(name="x", targets=(qubit,), matrix=gates.X)
        measured = _apply_operation_to_state(measured, n_qubits, flip)
    return measured



def _mask_for_qubit(n_qubits: int, qubit: int) -> int:
    return 1 << (n_qubits - 1 - qubit)



def _bit_at(index: int, n_qubits: int, qubit: int) -> int:
    return 1 if index & _mask_for_qubit(n_qubits, qubit) else 0



def _set_bit(index: int, n_qubits: int, qubit: int, bit: int) -> int:
    mask = _mask_for_qubit(n_qubits, qubit)
    if bit:
        return index | mask
    return index & ~mask
