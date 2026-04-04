# qcirclab

A tiny educational quantum-circuit DSL and simulator for notebooks and teaching.

`qcirclab` is meant to replace the *software layer* of a circuit-theory book without turning the book into a dependency on a large external framework. It focuses on the parts that age well:

- building circuits from standard gates
- composing subcircuits
- parameterized single-qubit rotations
- mid-circuit measurement and classical control
- statevector simulation and shot-based sampling
- canonical examples such as Bell, GHZ, teleportation, Deutsch–Jozsa, Bernstein–Vazirani, QFT, simplified QPE, and Grover
- reversible/arithmetic building blocks such as multi-controlled X and a Cuccaro ripple-carry adder
- simple structural metrics such as size, depth, width, and two-qubit gate counts

It intentionally does **not** try to be a full compiler stack, noise framework, or hardware runtime.

## Why this shape?

The companion book needs a practical layer for

- initialization, composition, measurement, and simulation in the foundations chapters,
- canonical circuits and algorithms,
- reversible arithmetic and testing,
- parameterized circuits and basic metrics,

while advanced topics such as full transpilation, noise toolchains, and real hardware can be treated conceptually or separately. The companion book is positioned as a bridge between theory and implementation, with code serving to make abstract constructions tangible, not as an end in itself.

## Installation

### Colab

```python
!pip install -q git+https://github.com/YOUR_USER/qcirclab.git
```

or, from a cloned checkout,

```python
!pip install -q -e .
```

### Local

```bash
pip install -e .
```

## Quick start

```python
from qcirclab import Circuit

qc = Circuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

print(qc.draw())
result = qc.run(shots=1000, seed=7)
print(result.counts)
```

Expected counts are concentrated on `00` and `11`.

## DSL examples

### 1. Bell state

```python
from qcirclab import bell_pair

qc = bell_pair()
print(qc.draw())
print(qc.run(shots=512, seed=1).probabilities())
```

### 2. Mid-circuit measurement and classical control

```python
from qcirclab import Circuit

qc = Circuit(2, 1)
qc.h(0)
qc.measure(0, 0)
qc.x(1, condition=(0, 1))

print(qc.draw())
print(qc.run(shots=20, seed=4).memory[:10])
```

### 3. Statevector simulation

```python
from qcirclab import Circuit

qc = Circuit(1)
qc.h(0)
psi = qc.statevector()
print(psi)
```

### 4. QFT

```python
from qcirclab import qft

qc = qft(3)
print(qc.draw())
print(qc.statevector())
```

### 5. Arithmetic: Cuccaro adder

```python
from qcirclab import cuccaro_adder, Circuit

adder = cuccaro_adder(2)
qc = Circuit(adder.n_qubits)
qc.initialize_basis("01100")  # a=01, b=10, carry=0
qc.append(adder)
print(qc.draw())
print(qc.statevector())
```

## API sketch

### Main object

```python
Circuit(n_qubits, n_clbits=0, name="circuit")
```

### Gates

- `h, x, y, z, s, sdg, t, tdg, sx, sxdg`
- `rx, ry, rz, p, u`
- `cx, cz, cp, swap, ccx, mcx`
- `unitary(matrix, targets, name="u", controls=())`

### Composition and state setup

- `initialize_basis(bitstring)`
- `set_statevector(state)`
- `append(other, qubits=None, clbits=None)`
- `compose(...)`

### Measurement and control

- `measure(qubit, cbit)`
- `measure_all()`
- gate methods accept `condition=(cbit, value)`

### Simulation

- `statevector()` for purely unitary circuits
- `run(shots=1024, seed=None)` for sampled execution with measurement collapse
- `sample_counts(...)`

### Introspection

- `draw()`
- `size()`
- `depth()`
- `count_ops()`
- `basic_metrics(circuit)`

## Supported scope

This repository is intended to cover most of the practical needs of the book’s early and middle chapters:

- foundations of circuits and gates
- visualization and simulation
- subcircuits and parameterized circuits
- mid-circuit measurement and classical conditionals
- Bell/GHZ/SWAP-test-style examples
- teleportation
- arithmetic circuits and verification for small instances
- Deutsch, Deutsch–Jozsa, Bernstein–Vazirani, QFT, simplified phase estimation, Grover
- basic metrics for chapter-level analysis

## Explicit limitations

Not included in this first version:

- density-matrix noise simulation
- transpilation and backend-aware routing
- pulse-level timing
- runtime/hardware execution
- full Shor-scale modular exponentiation toolchains
- autodiff and optimizer stacks for full VQE/QAOA workflows

Those topics appear later in the manuscript, but they are software-intensive and change faster than the circuit-theory core. The table of contents itself separates foundations, arithmetic, algorithms, noise, optimization, variational methods, and real-hardware execution, which makes this split natural for a future-proof code layer.

## Repository layout

```text
qcirclab/
  __init__.py
  algorithms.py
  arithmetic.py
  core.py
  draw.py
  gates.py
  metrics.py
examples/
  bell.py
  deutsch_jozsa.py
  grover.py
  qft_demo.py
  teleportation.py
  cuccaro_adder.py
notebooks/
  getting_started.ipynb
tests/
  test_qcirclab.py
```

## Suggested use in the book

A good pattern is:

1. define the circuit mathematically,
2. show the diagram,
3. give the `qcirclab` implementation,
4. use simulation or counts only to verify the concept.

That keeps the book centered on circuit theory instead of framework internals.
