from __future__ import annotations

from typing import Dict, Tuple

import numpy as np
from qiskit.quantum_info import Statevector

from .circuits import int_to_bits_le, quantize_t_to_int


def most_likely_bitstring(probs: np.ndarray, num_bits: int) -> Tuple[int, str]:
    """Return (argmax_index, little-endian bitstring) for a probability array."""
    idx = int(np.argmax(probs))
    bits = int_to_bits_le(idx, num_bits)
    return idx, "".join(str(b) for b in bits)


def summarize_phase_match(
    circuit,
    n: int,
    d: int,
    t: float,
    round_probs: int = 6,
) -> Dict[str, object]:
    """Simulate via Statevector and summarize how the most-likely outcome matches target t."""
    sv = Statevector(circuit)
    probs = np.round(sv.probabilities(), round_probs)

    num_bits = n + d
    idx, bits_le = most_likely_bitstring(probs, num_bits)

    target_phase_int = quantize_t_to_int(t, d)
    target_bits_le = int_to_bits_le(target_phase_int, d)

    # Split measured bits into [phase bits | search bits] under the same ordering used in the notebook:
    phase_bits_meas = int_to_bits_le(idx, num_bits)[:d]
    search_bits_meas = int_to_bits_le(idx, num_bits)[d:]

    return {
        "t": t,
        "n": n,
        "d": d,
        "most_likely_index": idx,
        "most_likely_bits_le": bits_le,
        "measured_phase_bits_le": phase_bits_meas,
        "measured_search_bits_le": search_bits_meas,
        "target_phase_int": target_phase_int,
        "target_phase_bits_le": target_bits_le,
        "p_max": float(np.max(probs)),
        "error_1_minus_pmax": float(1.0 - np.max(probs)),
    }
