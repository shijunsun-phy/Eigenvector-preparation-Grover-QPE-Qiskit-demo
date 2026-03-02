import numpy as np
from eigenprep import build_grover_qpe_circuit, summarize_phase_match


def test_n6_demo_builds_and_has_reasonable_success():
    n = 6
    d = 6
    N = 1 << n
    t = 1 / N
    eigs = [np.exp(1j * 2 * np.pi * k / N) for k in range(N)]

    circ = build_grover_qpe_circuit(eigs=eigs, n=n, d=d, t=t)
    summary = summarize_phase_match(circ, n=n, d=d, t=t)

    # Very lightweight sanity checks: we just require a strong peak.
    assert summary["p_max"] > 0.5
    assert len(summary["target_phase_bits_le"]) == d
