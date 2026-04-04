from __future__ import annotations

from typing import List

from .core import Circuit


def ascii_draw(circuit: Circuit) -> str:
    lines: List[str] = [f"q{q}: |0>" for q in range(circuit.n_qubits)]
    clines: List[str] = [f"c{c}:  0 " for c in range(circuit.n_clbits)]

    def pad_all() -> None:
        width = max(len(x) for x in [*lines, *clines])
        for i in range(len(lines)):
            lines[i] = lines[i].ljust(width)
        for i in range(len(clines)):
            clines[i] = clines[i].ljust(width)

    for op in circuit.operations:
        pad_all()
        if op.name == "barrier":
            for i in range(len(lines)):
                lines[i] += " ┆ "
            for i in range(len(clines)):
                clines[i] += "   "
            continue
        if op.name == "measure":
            q = op.targets[0]
            c = op.ctargets[0]
            for i in range(len(lines)):
                lines[i] += "───" if i != q else "─M─"
            for i in range(len(clines)):
                clines[i] += "═══" if i != c else "═╩═"
            continue
        label = op.label()[:3].center(3)
        for i in range(len(lines)):
            if i in op.controls:
                lines[i] += "─●─"
            elif i in op.targets:
                if op.name == "swap":
                    lines[i] += "─x─"
                elif op.name == "cx" and i not in op.controls:
                    lines[i] += "─X─"
                else:
                    lines[i] += f"[{label}]"
            else:
                lines[i] += "───"
        for i in range(len(clines)):
            clines[i] += "   "
    return "\n".join(lines + clines)
