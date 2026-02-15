"""Test script for enhanced PDF generation features."""

from tools.pdf_export import save_to_pdf

# Sample research data with all features
test_data = """
# Introduction to Quantum Computing

Quantum computing represents a revolutionary approach to computation that leverages quantum mechanical phenomena. Unlike classical computers that use bits (0 or 1), quantum computers use quantum bits or qubits.

## Basic Concepts

### Superposition

In quantum mechanics, superposition allows a qubit to exist in multiple states simultaneously. This is expressed mathematically as |ψ⟩ = α|0⟩ + β|1⟩ where α² + β² = 1.

### Quantum Entanglement

- Entangled particles remain connected even at large distances
- Measuring one particle instantly affects its entangled partner
- This phenomenon is key to quantum teleportation
  - Used in quantum communication protocols
  - Enables quantum cryptography

## Chemical Applications

Water (H₂O) molecules exhibit quantum properties at molecular scales. The oxygen atom forms bonds with two hydrogen atoms at angles of approximately 104.5°.

Other important molecules:
- Carbon dioxide: CO₂
- Methane: CH₄
- Ammonia: NH₃

## Mathematical Foundations

The Schrödinger equation describes quantum systems:

```python
def quantum_gate(qubit_state, gate_matrix):
    # Apply a quantum gate to a qubit state
    import numpy as np
    return np.dot(gate_matrix, qubit_state)

# Example: Hadamard gate
H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
initial_state = np.array([1, 0])  # |0⟩ state
result = quantum_gate(initial_state, H)
```

### Quantum Operations

Common quantum operations include:

1. Pauli-X gate (quantum NOT)
2. Hadamard gate (creates superposition)
3. CNOT gate (controlled NOT)

---

## Experimental Results

Here's a comparison of classical vs quantum computing speeds:

| Algorithm | Classical Time | Quantum Time | Speedup |
|-----------|---------------|--------------|---------|
| Factorization | O(e^n) | O(n²) | Exponential |
| Database Search | O(n) | O(√n) | Quadratic |
| Simulation | O(2^n) | O(n) | Exponential |

## Quantum Algorithms

### Shor's Algorithm

Shor's algorithm can factor large numbers exponentially faster than classical algorithms. For a number N, it runs in O((log N)²(log log N)(log log log N)) time.

```javascript
// Pseudocode for quantum Fourier transform
function QFT(qubits) {
    for (let i = 0; i < qubits.length; i++) {
        applyHadamard(qubits[i]);
        for (let j = i + 1; j < qubits.length; j++) {
            const phase = 2 * Math.PI / Math.pow(2, j - i + 1);
            applyControlledPhase(qubits[j], qubits[i], phase);
        }
    }
}
```

## Current Limitations

Despite promising advances, quantum computers face several challenges:

• **Decoherence**: Quantum states are fragile and easily disrupted
• **Error rates**: Current quantum gates have error rates of 10⁻³ to 10⁻²
• **Scalability**: Building systems with large numbers of qubits is difficult
• **Temperature requirements**: Many systems require cooling to near absolute zero

## Future Directions

Research continues in multiple areas:

- Topological quantum computing for error resistance
- Room-temperature quantum systems
- Quantum machine learning algorithms
- Quantum internet and communication networks

## References and Resources

For more information, see:
- https://quantum-computing.ibm.com/
- https://arxiv.org/abs/quant-ph/9508027
- https://www.nature.com/subjects/quantum-computing

## Conclusion

Quantum computing represents a paradigm shift in computational capabilities. While challenges remain, progress continues toward practical quantum computers that could revolutionize fields from cryptography to drug discovery.
"""

# Test the PDF generation
print("Testing enhanced PDF generation...")
print("-" * 60)

try:
    result = save_to_pdf.invoke({
        "data": test_data,
        "title": "Quantum Computing: A Comprehensive Overview",
        "filename": "test_quantum_computing_report.pdf"
    })
    print(f"✓ SUCCESS: {result}")
    print("\nFeatures tested:")
    print("  ✓ Cover page with title and date")
    print("  ✓ Table of Contents with section numbering")
    print("  ✓ Unicode subscripts (H₂O, CO₂)")
    print("  ✓ Unicode superscripts (10⁻³, 10⁻²)")
    print("  ✓ Section auto-numbering (1, 1.1, 1.2, etc.)")
    print("  ✓ Markdown tables with styling")
    print("  ✓ Code blocks with syntax highlighting labels")
    print("  ✓ Bullet points and nested bullets")
    print("  ✓ Clickable hyperlinks")
    print("  ✓ References section")
    print("  ✓ Page breaks (---)")
    print("  ✓ Professional header/footer with page numbers")
    print("  ✓ PDF metadata (title, author, subject)")
    print("\nPlease open the PDF to verify all features render correctly!")

except Exception as e:
    print(f"✗ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
