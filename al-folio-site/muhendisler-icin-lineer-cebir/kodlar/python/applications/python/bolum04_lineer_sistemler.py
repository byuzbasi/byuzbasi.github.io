"""Bölüm 4 için deterministik lineer sistem uygulamaları.

Bu modül eğitim amacıyla kısmi pivotlamalı PLU adımlarını görünür kılar.
Gerçek mühendislik hesaplarında NumPy/SciPy gibi sınanmış LAPACK tabanlı
yordamlar kullanılmalıdır. Modül dış ağa bağlanmaz ve dosya yazmaz.
"""

from __future__ import annotations

import argparse
import json
import platform
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class PLUFactors:
    """P @ A = L @ U ayrıştırmasının üç çarpanını tutar."""

    P: np.ndarray
    L: np.ndarray
    U: np.ndarray


def _square_system(A: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Girdileri kayan noktalı kare sistem olarak doğrular ve kopyalar."""

    A_work = np.array(A, dtype=float, copy=True)
    b_work = np.array(b, dtype=float, copy=True)
    if A_work.ndim != 2 or A_work.shape[0] != A_work.shape[1]:
        raise ValueError("A must be a square two-dimensional array")
    if b_work.ndim != 1 or b_work.shape[0] != A_work.shape[0]:
        raise ValueError("b must be a one-dimensional array matching A")
    if not np.all(np.isfinite(A_work)) or not np.all(np.isfinite(b_work)):
        raise ValueError("A and b must contain only finite values")
    return A_work, b_work


def _relative_pivot_threshold(matrix: np.ndarray) -> tuple[float, float]:
    """Return s and eps*n*||matrix/s||_inf without a unit-scale floor.

    Compare abs(pivot)/s with the second value. This is the relative
    eps*n*||matrix||_inf policy without underflowing its absolute threshold.
    """

    if matrix.size == 0:
        raise ValueError("the matrix must not be empty")
    scale = float(np.max(np.abs(matrix)))
    if scale == 0.0:
        raise np.linalg.LinAlgError("the zero matrix has no nonzero pivot")
    relative_tolerance = float(
        np.finfo(float).eps * max(matrix.shape[0], 1)
        * np.linalg.norm(matrix / scale, ord=np.inf)
    )
    return scale, relative_tolerance


def plu_factor(A: np.ndarray, pivot_tolerance: float | None = None) -> PLUFactors:
    """Kısmi pivotlamayla P @ A = L @ U ayrıştırmasını hesaplar.

    Yordam yoğun, gerçek ve kare matrisler için öğretim uygulamasıdır. Varsayılan
    eşik eps*n*||A||_inf'dir; ortak ölçek için mutlak alt sınır kullanılmaz.
    Açık pivot_tolerance sonlu, negatif olmayan mutlak bir eşiktir.
    """

    U = np.array(A, dtype=float, copy=True)
    if U.ndim != 2 or U.shape[0] != U.shape[1]:
        raise ValueError("A must be a square two-dimensional array")
    if not np.all(np.isfinite(U)):
        raise ValueError("A must contain only finite values")

    n = U.shape[0]
    P = np.eye(n, dtype=float)
    L = np.eye(n, dtype=float)
    if n == 0:
        raise ValueError("A must not be empty")
    if pivot_tolerance is None:
        scale, tolerance = _relative_pivot_threshold(U)
    else:
        scale = 1.0
        tolerance = float(pivot_tolerance)
        if not np.isfinite(tolerance) or tolerance < 0.0:
            raise ValueError("pivot_tolerance must be finite and nonnegative")

    for k in range(n):
        pivot = k + int(np.argmax(np.abs(U[k:, k])))
        if abs(float(U[pivot, k])) / scale <= tolerance:
            raise np.linalg.LinAlgError(
                f"matrix is singular to working tolerance at column {k}"
            )

        if pivot != k:
            U[[k, pivot], :] = U[[pivot, k], :]
            P[[k, pivot], :] = P[[pivot, k], :]
            if k:
                L[[k, pivot], :k] = L[[pivot, k], :k]

        for row in range(k + 1, n):
            multiplier = U[row, k] / U[k, k]
            L[row, k] = multiplier
            with np.errstate(over="ignore", invalid="ignore"):
                U[row, k:] -= multiplier * U[k, k:]
            if not np.all(np.isfinite(U[row, k:])):
                raise np.linalg.LinAlgError("PLU elimination exceeds floating-point range")
            U[row, k] = 0.0

    return PLUFactors(P=P, L=L, U=U)


def forward_substitution(L: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Sıfır olmayan köşegenli alt üçgensel sistemi çözer."""

    L_work, b_work = _square_system(L, b)
    n = b_work.size
    y = np.zeros(n, dtype=float)
    scale, tolerance = _relative_pivot_threshold(L_work)
    for row in range(n):
        diagonal = L_work[row, row]
        if abs(float(diagonal)) / scale <= tolerance:
            raise np.linalg.LinAlgError("zero diagonal in forward substitution")
        with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
            known = float(L_work[row, :row] @ y[:row])
            y[row] = (b_work[row] - known) / diagonal
        if not np.isfinite(y[row]):
            raise np.linalg.LinAlgError("forward substitution exceeds floating-point range")
    return y


def back_substitution(U: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Sıfır olmayan köşegenli üst üçgensel sistemi çözer."""

    U_work, b_work = _square_system(U, b)
    n = b_work.size
    x = np.zeros(n, dtype=float)
    scale, tolerance = _relative_pivot_threshold(U_work)
    for row in range(n - 1, -1, -1):
        diagonal = U_work[row, row]
        if abs(float(diagonal)) / scale <= tolerance:
            raise np.linalg.LinAlgError("zero diagonal in back substitution")
        with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
            known = float(U_work[row, row + 1 :] @ x[row + 1 :])
            x[row] = (b_work[row] - known) / diagonal
        if not np.isfinite(x[row]):
            raise np.linalg.LinAlgError("back substitution exceeds floating-point range")
    return x


def plu_solve(A: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, PLUFactors]:
    """Kısmi pivotlamalı PLU üzerinden kare sistemi çözer."""

    A_work, b_work = _square_system(A, b)
    factors = plu_factor(A_work)
    y = forward_substitution(factors.L, factors.P @ b_work)
    x = back_substitution(factors.U, y)
    return x, factors


def scaled_backward_error(A: np.ndarray, x: np.ndarray, b: np.ndarray) -> float:
    """Kitaptaki 2-normuna dayalı ölçeklendirilmiş geri hatayı hesaplar."""

    A_arr = np.asarray(A, dtype=float)
    x_arr = np.asarray(x, dtype=float)
    b_arr = np.asarray(b, dtype=float)
    numerator = float(np.linalg.norm(b_arr - A_arr @ x_arr, ord=2))
    denominator = float(
        np.linalg.norm(A_arr, ord=2) * np.linalg.norm(x_arr, ord=2)
        + np.linalg.norm(b_arr, ord=2)
    )
    if denominator == 0.0:
        return 0.0 if numerator == 0.0 else float("inf")
    return numerator / denominator


def solve_report(
    name: str,
    A: np.ndarray,
    b: np.ndarray,
    expected: np.ndarray | None = None,
) -> dict[str, Any]:
    """NumPy ve eğitim PLU çözümünü ortak doğrulama kaydında toplar."""

    A_work, b_work = _square_system(A, b)
    x_library = np.linalg.solve(A_work, b_work)
    x_plu, factors = plu_solve(A_work, b_work)
    residual = b_work - A_work @ x_library
    report: dict[str, Any] = {
        "name": name,
        "shape": list(A_work.shape),
        "solution": x_library.tolist(),
        "plu_solution": x_plu.tolist(),
        "residual": residual.tolist(),
        "residual_norm": float(np.linalg.norm(residual, ord=2)),
        "backward_error": scaled_backward_error(A_work, x_library, b_work),
        "condition_2": float(np.linalg.cond(A_work, p=2)),
        "plu_factorization_error_fro": float(
            np.linalg.norm(factors.P @ A_work - factors.L @ factors.U, ord="fro")
        ),
        "plu_vs_library_error": float(np.linalg.norm(x_plu - x_library, ord=2)),
    }
    if expected is not None:
        expected_arr = np.asarray(expected, dtype=float)
        report["expected"] = expected_arr.tolist()
        report["forward_error"] = float(
            np.linalg.norm(x_library - expected_arr, ord=2)
        )
    return report


def material_balance() -> dict[str, Any]:
    """Üç akışlı karışımın ölçeklenmiş ve fiziksel dengelerini çözer."""

    A_scaled = np.array(
        [
            [1.0, 1.0, 1.0],
            [2.0, 5.0, 8.0],
            [6.0, 2.0, 1.0],
        ]
    )
    b_scaled = np.array([100.0, 530.0, 250.0])
    expected = np.array([20.0, 50.0, 30.0])
    report = solve_report("material_balance", A_scaled, b_scaled, expected)

    A_physical = np.array(
        [
            [1.0, 1.0, 1.0],
            [0.2, 0.5, 0.8],
            [0.6, 0.2, 0.1],
        ]
    )
    b_physical = np.array([100.0, 53.0, 25.0])
    solution = np.asarray(report["solution"], dtype=float)
    report["units"] = "kg/h"
    report["physical_balance"] = (A_physical @ solution).tolist()
    report["physical_target"] = b_physical.tolist()
    report["physical_residual_norm"] = float(
        np.linalg.norm(b_physical - A_physical @ solution, ord=2)
    )
    return report


def resistor_network() -> dict[str, Any]:
    """Üç düğümlü direnç ağının gerilimlerini ve akım dengesini çözer."""

    G = np.array(
        [
            [4.0, -1.0, -1.0],
            [-1.0, 3.0, -1.0],
            [-1.0, -1.0, 3.0],
        ]
    )
    current = np.array([5.0, 0.0, 0.0])
    expected = np.array([5.0 / 3.0, 5.0 / 6.0, 5.0 / 6.0])
    report = solve_report("resistor_network", G, current, expected)
    voltage = np.asarray(report["solution"], dtype=float)
    report["solution_units"] = "V"
    report["right_hand_side_units"] = "A"
    report["nodal_current_balance"] = (G @ voltage).tolist()
    report["source_current"] = current.tolist()
    return report


def ill_conditioning_demo() -> dict[str, Any]:
    """Yakın bağımlı iki satırda veri hatasının çözümde büyümesini gösterir."""

    gap = 1.0e-10
    A = np.array([[1.0, 1.0], [1.0, 1.0 + gap]])
    exact = np.ones(2, dtype=float)
    b = A @ exact
    delta_b = np.array([0.0, 1.0e-12])
    perturbed_b = b + delta_b
    perturbed_solution = np.linalg.solve(A, perturbed_b)
    relative_data_change = float(
        np.linalg.norm(delta_b, ord=2) / np.linalg.norm(b, ord=2)
    )
    relative_solution_change = float(
        np.linalg.norm(perturbed_solution - exact, ord=2)
        / np.linalg.norm(exact, ord=2)
    )
    return {
        "name": "ill_conditioning_demo",
        "gap": gap,
        "exact_solution": exact.tolist(),
        "perturbed_solution": perturbed_solution.tolist(),
        "relative_data_change": relative_data_change,
        "relative_solution_change": relative_solution_change,
        "condition_2": float(np.linalg.cond(A, p=2)),
        "bound_multiplier": float(np.linalg.cond(A, p=2) * relative_data_change),
        "backward_error": scaled_backward_error(A, perturbed_solution, perturbed_b),
    }


def all_results() -> dict[str, Any]:
    """Pilot bölümün yeniden üretilebilir sonuç paketini döndürür."""

    return {
        "schema_version": "1.0",
        "book_version": "v0.1",
        "chapter": 4,
        "deterministic": True,
        "software": {
            "python": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "numpy": np.__version__,
            "platform": platform.platform(),
        },
        "applications": [material_balance(), resistor_network()],
        "sensitivity": ill_conditioning_demo(),
    }


def _human_summary(results: dict[str, Any]) -> str:
    lines = [
        "Mühendisler için Lineer Cebir - Bölüm 4 doğrulaması",
        f"Python {results['software']['python']} | NumPy {results['software']['numpy']}",
    ]
    for application in results["applications"]:
        solution = ", ".join(f"{value:.8g}" for value in application["solution"])
        lines.append(
            f"{application['name']}: x=[{solution}], "
            f"eta={application['backward_error']:.3e}, "
            f"cond2={application['condition_2']:.6g}"
        )
    sensitivity = results["sensitivity"]
    lines.append(
        "ill_conditioning_demo: "
        f"relative_data_change={sensitivity['relative_data_change']:.3e}, "
        f"relative_solution_change={sensitivity['relative_solution_change']:.3e}, "
        f"cond2={sensitivity['condition_2']:.3e}"
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        action="store_true",
        help="Sonuçları makinece okunabilir JSON olarak stdout'a yaz.",
    )
    args = parser.parse_args()
    results = all_results()
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(_human_summary(results))


if __name__ == "__main__":
    main()
