from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Optional

import numpy as np
from qiskit.circuit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import QFTGate, DiagonalGate


def quantize_t_to_int(t: float, d: int) -> int:
    """Convert target phase t in [0,1) to integer T = round(2^d * t) mod 2^d."""
    if d <= 0:
        raise ValueError("d must be positive")
    M = 1 << d
    return int(round((t % 1.0) * M)) % M


def int_to_bits_le(x: int, m: int) -> List[int]:
    """Little-endian bits: bit 0 is the least significant bit."""
    if m < 0:
        raise ValueError("m must be non-negative")
    return [(x >> k) & 1 for k in range(m)]


def _as_complex_list(vals: Sequence[complex]) -> List[complex]:
    # Helps avoid dtype issues when constructing diagonal gates.
    return [complex(v) for v in vals]


def _power_eigs(eigs: Sequence[complex], power: int) -> List[complex]:
    return [v ** power for v in eigs]


def _inv_eigs(eigs: Sequence[complex]) -> List[complex]:
    return [np.conjugate(v) for v in eigs]


def build_qpe_circuit(
    eigs: Sequence[complex],
    n: int,
    m: int,
    name: str = "QPE",
    inverse: bool = False,
) -> QuantumCircuit:
    """Build a coherent QPE circuit for a diagonal U given by its eigenvalues.

    - `n`: number of eigenstates / search-register qubits
    - `m`: number of phase-register qubits

    Convention: phase bits are stored little-endian in the phase register:
    P[0] holds the least significant bit.
    """
    eigs = _as_complex_list(eigs)
    if len(eigs) != (1 << n):
        raise ValueError(f"Expected {1<<n} eigenvalues for n={n}, got {len(eigs)}")

    P = QuantumRegister(m, "P")
    S = QuantumRegister(n, "S")
    qc = QuantumCircuit(P, S, name=(name + ("†" if inverse else "")))

    if not inverse:
        qc.h(P)
        for k in range(m):
            power = 1 << k
            pow_eigs = _power_eigs(eigs, power)
            U_pow = DiagonalGate(pow_eigs)
            qc.append(U_pow.control(1), [P[k], *S])

        qc.append(QFTGate(num_qubits=m).inverse(), P)
    else:
        qc.append(QFTGate(num_qubits=m), P)
        for k in range(m):
            power = 1 << k
            pow_eigs = _inv_eigs(_power_eigs(eigs, power))
            U_pow_dag = DiagonalGate(pow_eigs)
            qc.append(U_pow_dag.control(1), [P[k], *S])

        qc.h(P)

    return qc


def build_diffuser(n: int, name: str = "D") -> QuantumCircuit:
    """Standard Grover diffuser on an n-qubit register."""
    S = QuantumRegister(n, "S")
    diffuser = QuantumCircuit(S, name=name)

    diffuser.h(S)
    diffuser.x(S)

    if n == 1:
        diffuser.z(S[0])
    else:
        diffuser.mcp(np.pi, list(S[:-1]), S[n - 1])

    diffuser.x(S)
    diffuser.h(S)
    return diffuser


def build_phase_oracle(
    eigs: Sequence[complex],
    n: int,
    d: int,
    t: float,
    name: str = "U_t",
) -> QuantumCircuit:
    """Oracle U_t acting on (phase register P of size d, search register S of size n).

    Pattern:
      1) QPE(U) on (P,S)
      2) apply X masks so that P==T maps to all-ones
      3) multi-controlled phase flip on P
      4) undo X masks
      5) inverse QPE(U)
    """
    eigs = _as_complex_list(eigs)
    m = d

    T_int = quantize_t_to_int(t, d)
    T_bits = int_to_bits_le(T_int, m)

    P = QuantumRegister(m, "phase")
    S = QuantumRegister(n, "search")
    oracle = QuantumCircuit(P, S, name=name)

    qpe_fwd = build_qpe_circuit(eigs, n=n, m=m, inverse=False).to_instruction()
    qpe_inv = build_qpe_circuit(eigs, n=n, m=m, inverse=True).to_instruction()

    oracle.append(qpe_fwd, [*P, *S])

    # Mask bits where T has 0 so equality test becomes all-ones
    for k, bit in enumerate(T_bits):
        if bit == 0:
            oracle.x(P[k])

    # Phase flip when all masked bits are |1>
    if m == 1:
        oracle.z(P[0])
    else:
        oracle.mcp(np.pi, list(P[:-1]), P[m - 1])

    # Undo mask
    for k, bit in enumerate(T_bits):
        if bit == 0:
            oracle.x(P[k])

    oracle.append(qpe_inv, [*P, *S])
    return oracle


def build_grover_qpe_circuit(
    eigs: Sequence[complex],
    n: int,
    d: int,
    t: float,
    grover_iters: Optional[int] = None,
) -> QuantumCircuit:
    """Full Grover-amplified QPE circuit.

    Initializes |+>^n on the search register, then repeats:
      U_t (mark phase == t) + diffuser on search register.
    """
    if grover_iters is None:
        grover_iters = int(np.rint(np.pi / (4 * np.arcsin(1 / np.sqrt(1 << n))) - 1 / 2))

    P = QuantumRegister(d, "phase")
    S = QuantumRegister(n, "search")
    qc = QuantumCircuit(P, S, name="Grover_QPE")

    oracle_inst = build_phase_oracle(eigs=eigs, n=n, d=d, t=t).to_instruction()
    diffuser_inst = build_diffuser(n).to_instruction()

    qc.h(S)

    for _ in range(grover_iters):
        qc.append(oracle_inst, [*P, *S])
        qc.append(diffuser_inst, [*S])

    return qc
