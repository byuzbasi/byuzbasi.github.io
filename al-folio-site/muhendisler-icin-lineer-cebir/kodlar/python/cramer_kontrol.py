"""Small exact Cramer examples; not a production linear-system solver.

Run from the manuscript directory:
    python3 python/cramer_kontrol.py
    python3 python/cramer_kontrol.py --self-test

Only 1x1, 2x2 and 3x3 integer/Fraction data are accepted by cramer_exact.
No output files, random draws or application kernels are changed.
"""
from fractions import Fraction
from itertools import permutations
from numbers import Integral
import argparse
import json
import numpy as np


def determinant_small(A):
    """Exact permutation formula, restricted to at most six summands."""
    rows = [list(row) for row in A]
    n = len(rows)
    if n not in (1, 2, 3) or any(len(row) != n for row in rows):
        raise ValueError("Expected a square matrix of order 1, 2 or 3")
    exact = []
    for row in rows:
        converted = []
        for value in row:
            if isinstance(value, Fraction):
                converted.append(value)
            elif isinstance(value, Integral) and not isinstance(value, bool):
                converted.append(Fraction(int(value)))
            else:
                raise TypeError("Exact input entries must be integers or Fraction")
        exact.append(converted)
    result = Fraction(0)
    for order in permutations(range(n)):
        inversions = sum(order[i] > order[j]
                         for i in range(n) for j in range(i + 1, n))
        term = Fraction((-1) ** inversions)
        for i in range(n):
            term *= exact[i][order[i]]
        result += term
    return result


def cramer_exact(A, b):
    """Return denominator, replaced-column determinants and exact solution."""
    rows = [list(row) for row in A]
    denominator = determinant_small(rows)
    rhs = list(b)
    n = len(rows)
    if len(rhs) != n:
        raise ValueError("Right-hand side length must match the matrix order")
    if denominator == 0:
        raise ValueError("Cramer's rule requires a nonzero determinant")
    numerators = []
    for j in range(n):
        Aj = [row.copy() for row in rows]
        for i in range(n):
            Aj[i][j] = rhs[i]
        numerators.append(determinant_small(Aj))
    solution = [value / denominator for value in numerators]
    return denominator, numerators, solution


def solve_passport(A, b):
    """NumPy solve and 2-norm diagnostics for these small finite examples."""
    matrix = np.asarray(A, dtype=float)
    rhs = np.asarray(b, dtype=float)
    if (matrix.ndim != 2 or matrix.shape[0] not in (1, 2, 3)
            or matrix.shape[1] != matrix.shape[0]
            or rhs.shape != (matrix.shape[0],)):
        raise ValueError("Expected a square matrix of order 1..3 and one RHS")
    if not np.isfinite(matrix).all() or not np.isfinite(rhs).all():
        raise ValueError("Inputs must be finite")
    solution = np.linalg.solve(matrix, rhs)
    residual = rhs - matrix @ solution
    residual_norm = float(np.linalg.norm(residual, 2))
    scale = (np.linalg.norm(matrix, 2) * np.linalg.norm(solution, 2)
             + np.linalg.norm(rhs, 2))
    if not np.isfinite(solution).all() or not np.isfinite(scale):
        raise ValueError("Example exceeds the finite diagnostic range")
    backward_error = residual_norm / scale if scale > 0 else 0.0
    return {"solution": solution.tolist(), "residual_norm": residual_norm,
            "backward_error": float(backward_error)}


CASES = (
    ([[2, 1], [1, -1]], [5, 1], [-3, -6, -3], [2, 1]),
    ([[1, 1, 1], [2, -1, 1], [1, 2, -1]], [6, 3, 2],
     [7, 7, 14, 21], [1, 2, 3]),
    ([[3, -2], [5, 4]], [7, 1], [22, 30, -32],
     [Fraction(15, 11), Fraction(-16, 11)]),
    ([[2, -1, 1], [1, 2, -1], [3, 1, 2]], [7, -6, 7],
     [10, 10, -20, 30], [1, -2, 3]),
)


def self_test():
    checks = 0
    for A, b, determinants, expected in CASES:
        det_A, numerators, exact = cramer_exact(A, b)
        assert [det_A, *numerators] == determinants
        assert exact == expected
        assert all(sum(Fraction(a) * x for a, x in zip(row, exact)) == value
                   for row, value in zip(A, b))
        result = solve_passport(A, b)
        np.testing.assert_allclose(result["solution"], [float(x) for x in exact],
                                   rtol=0, atol=2e-14)
        assert result["backward_error"] < 5e-16
        checks += 5
    assert cramer_exact([[4]], [8]) == (Fraction(4), [Fraction(8)], [Fraction(2)])
    checks += 1
    for A, b in (([[1, 2], [2, 4]], [3, 6]),
                 ([[1, 0, 0], [0, 0, 0], [0, 0, 0]], [0, 1, 0])):
        try:
            cramer_exact(A, b)
        except ValueError:
            checks += 1
        else:
            raise AssertionError("A singular system must be rejected")
    for A, b in (([[1, 2]], [1]), ([[1]], [1, 2])):
        try:
            cramer_exact(A, b)
        except ValueError:
            checks += 1
        else:
            raise AssertionError("Invalid dimensions must be rejected")
    assert solve_passport([[1]], [0])["backward_error"] == 0.0
    checks += 1
    print(json.dumps({"self_test": "passed", "checks": checks}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    for A, b, _, _ in CASES[:2]:
        denominator, numerators, exact = cramer_exact(A, b)
        result = {"det_A": str(denominator),
                  "det_Aj": [str(value) for value in numerators],
                  "exact_solution": [str(value) for value in exact],
                  **solve_passport(A, b)}
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
