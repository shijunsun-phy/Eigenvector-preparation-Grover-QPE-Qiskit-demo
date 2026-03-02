# Eigenvector-preparation-Grover-QPE-Qiskit-demo
This repository is a small, self-contained demo of an eigenvector preparation circuit using a Grover-amplified Quantum Phase Estimation (QPE) style construction.

The **primary entrypoint** is the **`n=6, d=6`** example:
1) build and display the circuit, and  
2) verify that the most-likely measurement outcome matches the target phase `t`.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Run the n=6 demo (recommended)

```bash
python scripts/run_n6_demo.py
```

This will:
- build the `n=6, d=6` Grover+QPE circuit,
- print the target `t` and the most-likely measured bitstring,
- compute a simple success metric from the statevector,
- save a circuit figure to `artifacts/circuit_n6.png`.

### Notebook demo

Open and run:

- `notebooks/n6_demo.ipynb`

## Project layout

- `src/eigenprep/` — reusable circuit builders + small analysis helpers
- `scripts/run_n6_demo.py` — primary demo entrypoint
- `notebooks/` — lightweight, presentation-friendly notebooks
- `tests/` — small correctness checks (kept minimal)

## Notes

- This project uses `DiagonalGate` (not deprecated `Diagonal`) and appends subcircuits as
  `Instruction`s to avoid Qiskit deprecation warnings.
