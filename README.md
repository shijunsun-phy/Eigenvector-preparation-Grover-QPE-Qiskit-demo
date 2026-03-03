# Eigenvector preparation (Grover + QPE) — Qiskit demo

Shijun Sun

This repository is a small, self-contained demo of an eigenvector preparation circuit using a Grover-amplified Quantum Phase Estimation (QPE) style construction.

## Problem Setting

Suppose we are given:

- An **n-qubit diagonal unitary** $U |x\rangle = e^{2πi θ(x)} |x\rangle$

- A promise that each eigenphase is a dyadic fraction:  $2^d \theta(x) \in \mathbb{Z}$

- A **target phase** $t \in [0,1)$

and we are promised that there exists a *unique* computational basis state $|x^*\rangle$ such that  

$$U |x^* \rangle = e^{2πi t} |x^* \rangle.$$

The goal is to **prepare the eigenvector $|x^*\rangle$** using a fully unitary circuit.


## Oracle Construction

**Key idea:** Turn Quantum Phase Estimation into a phase filter that acts as a Grover oracle.

The oracle is built using three steps:

### 1. Phase Estimation

We run QPE using:

- a phase register P of size d
- a search register S of size n

This maps:

$$|x\rangle_S |0\rangle_P → |x\rangle_S |\theta(x)\rangle_P$$

Because of the promise, the phase is exactly representable in d bits.


### 2. Phase Matching

We compare the extracted phase with the target phase t.

If they match, a controlled phase flip is applied:

$$|x\rangle_S |\theta(x)\rangle_P → (−1)^{[\theta(x)=t]} |x\rangle_S |\theta(x)\rangle_P$$


### 3. Uncomputation

We invert QPE:

$$|\theta(x)\rangle_P \rightarrow |0\rangle_P$$

leaving:

$$(−1)^{[θ(x)=t]} |x\rangle_S$$

This is exactly the Grover oracle.


## Final Circuit

The full Grover iterate is:

$$G = U_t \cdot D$$

where $D$ is the Grover diffuser acting on the search register.

Repeating this iteration prepares the unique eigenvector corresponding to the target phase.

---

## Primary Demo: n = 6

The main entrypoint demonstrates:

- A 6-qubit search space
- A 6-bit phase register
- Fully coherent eigenvector preparation

Run the demo:

```bash
python scripts/run_n6_demo.py
```

This will:

1. Build and save the circuit
2. Simulate the prepared state
3. Compare the inferred phase with the target t

Example output:

[Output circuit](output_circuit_n6.png)
Note: for Grover search with $n=6$, $K = \operatorname{round}\!\left(
\frac{\pi}{4\,\arcsin\!\left(2^{-n/2}\right)} - \frac{1}{2}
\right) = 6$ iterations are needed

Target phase t:      0.375  
Estimated phase:     0.375  
Most likely state:   $|x*\rangle$  
Success probability: 0.997  


---

## Navigating the Repository

- `eigenprep/` — reusable circuit builders + small analysis helpers
- `scripts/run_n6_demo.py` — primary demo entrypoint
- `notebooks/` — lightweight, presentation-friendly notebooks
- `tests/` — small correctness checks (kept minimal)
