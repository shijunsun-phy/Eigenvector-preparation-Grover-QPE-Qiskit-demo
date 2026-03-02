from __future__ import annotations

import os
import numpy as np

from qiskit.circuit import QuantumCircuit
from qiskit.visualization import circuit_drawer

from eigenprep import build_grover_qpe_circuit, summarize_phase_match


def main() -> None:
    # Primary demo parameters (from the notebook)
    n = 6
    d = 6
    N = 1 << n
    t = 1 / N

    # Diagonal unitary eigenvalues: exp(2π i k / N)
    eigs = [np.exp(1j * 2 * np.pi * k / N) for k in range(N)]

    circ: QuantumCircuit = build_grover_qpe_circuit(eigs=eigs, n=n, d=d, t=t)

    # 1) Show/save the circuit (mpl)
    os.makedirs("artifacts", exist_ok=True)
    fig_path = os.path.join("artifacts", "circuit_n6.png")
    circuit_drawer(circ, output="mpl", filename=fig_path)
    print(f"Saved circuit figure to: {fig_path}")

    # 2) Show phase match summary
    summary = summarize_phase_match(circ, n=n, d=d, t=t)

    print("\n=== Eigenvector preparation demo (n=6, d=6) ===")
    print(f"Target t = {summary['t']:.10f}  (target phase int = {summary['target_phase_int']})")
    print(f"Target phase bits (LE, length d): {summary['target_phase_bits_le']}")
    print(f"Most likely outcome index: {summary['most_likely_index']}")
    print(f"Measured phase bits (LE): {summary['measured_phase_bits_le']}")
    print(f"Measured search bits (LE): {summary['measured_search_bits_le']}")
    print(f"Max probability p_max = {summary['p_max']:.6f}")
    print(f"Error = 1 - p_max = {summary['error_1_minus_pmax']:.6f}")
    print(f"Reference bound: 1/2^n = {1/N:.6f}")


if __name__ == "__main__":
    main()
