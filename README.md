# qcirclab

`qcirclab` is a lightweight Python library for building, drawing, simulating, and testing quantum circuits.

It was developed as the companion code layer for the quantum circuits book `Quantum Circuit Theory and Design`, written by Francisco Orts. The goal is to make the constructions in the text executable while keeping the examples independent from large external frameworks whose APIs may change over time (and leave printed examples outdated).

The library is designed for clarity in teaching and experimentation. Circuits are written directly in Python, can be drawn as text diagrams, and can be simulated either as statevectors or through shot-based sampling.

## Installation

Install directly from GitHub:

```bash
pip install git+https://github.com/2forts/qcirclab.git
```

For local development, clone the repository and install it in editable mode:

```bash
git clone https://github.com/2forts/qcirclab.git
cd qcirclab
pip install -e .
```

In Google Colab:

```python
!pip install -q git+https://github.com/2forts/qcirclab.git
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

This prepares and measures a Bell state. The counts should be concentrated on `00` and `11`.

## A few examples

### Bell state

```python
from qcirclab import bell_pair

qc = bell_pair()
print(qc.draw())
print(qc.run(shots=512, seed=1).probabilities())
```

### Mid-circuit measurement and classical control

```python
from qcirclab import Circuit

qc = Circuit(2, 1)
qc.h(0)
qc.measure(0, 0)
qc.x(1, condition=(0, 1))

print(qc.draw())
print(qc.run(shots=20, seed=4).memory[:10])
```

### Statevector simulation

```python
from qcirclab import Circuit

qc = Circuit(1)
qc.h(0)

psi = qc.statevector()
print(psi)
```

### Quantum Fourier transform

```python
from qcirclab import qft

qc = qft(3)
print(qc.draw())
print(qc.statevector())
```

### Reversible arithmetic

```python
from qcirclab import cuccaro_adder, Circuit

adder = cuccaro_adder(2)

qc = Circuit(adder.n_qubits)
qc.initialize_basis("01100")  # example input
qc.append(adder)

print(qc.draw())
print(qc.statevector())
```

## Main features

- Circuit construction with standard one-, two-, and multi-qubit gates.
- Parameterized rotations.
- Circuit composition and reusable subcircuits.
- Basis-state initialization and custom statevector setup.
- Mid-circuit measurement.
- Simple classical control through conditional gates.
- Statevector simulation.
- Shot-based sampling with measurement collapse.
- Text-based circuit drawings.
- Basic structural metrics: size, depth, width, operation counts, and two-qubit gate counts.
- Ready-made examples for common circuits and algorithms.

## API sketch

### Circuits

```python
Circuit(n_qubits, n_clbits=0, name="circuit")
```

### Gates

```python
qc.h(0)
qc.x(0)
qc.rx(theta, 0)
qc.cx(0, 1)
qc.cz(0, 1)
qc.swap(0, 1)
qc.ccx(0, 1, 2)
qc.mcx([0, 1, 2], 3)
```

Available gates include:

- `h`, `x`, `y`, `z`
- `s`, `sdg`, `t`, `tdg`
- `sx`, `sxdg`
- `rx`, `ry`, `rz`, `p`, `u`
- `cx`, `cz`, `cp`, `swap`
- `ccx`, `mcx`
- `unitary(...)`

### Composition

```python
qc.append(other)
qc.compose(other)
```

### Measurement

```python
qc.measure(qubit, cbit)
qc.measure_all()
```

Conditional gates use:

```python
qc.x(1, condition=(0, 1))
```

### Simulation

```python
qc.statevector()
qc.run(shots=1024, seed=123)
qc.sample_counts(shots=1024)
```

### Introspection

```python
qc.draw()
qc.size()
qc.depth()
qc.count_ops()
```

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

## Examples included

The repository includes examples for:

- Bell states
- GHZ states
- teleportation
- Deutsch and Deutsch--Jozsa algorithms
- Bernstein--Vazirani algorithm
- quantum Fourier transform
- simplified phase estimation
- Grover search
- reversible arithmetic
- Cuccaro ripple-carry addition
- circuit metrics

## Using qcirclab with the book

A typical chapter workflow is:

1. introduce the circuit mathematically;
2. draw the circuit;
3. implement it with `qcirclab`;
4. simulate it for a small instance;
5. use the result to check the idea.

The code is there to support the circuit concepts. The examples are meant to be readable, modifiable, and close to the notation used in the text.

## Tests

Run the test suite with:

```bash
pytest
```

## License

This repository is released under the MIT License. See [`LICENSE`](LICENSE) for details.
