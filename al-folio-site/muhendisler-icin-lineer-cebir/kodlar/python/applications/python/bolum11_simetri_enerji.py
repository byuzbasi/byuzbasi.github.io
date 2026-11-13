#!/usr/bin/env python3
"""Deterministic Chapter 11 calculations for symmetry, energy, and Cholesky.

The module is deliberately small enough to audit. It uses NumPy's maintained
linear algebra routines for production-style calculations, forms no explicit
matrix inverse, performs an explicit Hermitian check before Cholesky, and
never repairs a matrix by silent symmetrization or diagonal jitter.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path
from typing import Any

import numpy as np


class StructuralEnergyError(ValueError):
    """Raised when dimensions, finiteness, symmetry, or positivity fail."""


def _numeric_dtype(value: Any) -> np.dtype[Any]:
    """Return binary64 or complex128 while preserving complex input."""

    array = np.asarray(value)
    if np.iscomplexobj(array):
        return np.dtype(np.complex128)
    return np.dtype(np.float64)


def _as_finite_matrix(value: Any, name: str) -> np.ndarray:
    """Validate and return a finite two-dimensional numeric array."""

    try:
        array = np.asarray(value, dtype=_numeric_dtype(value))
    except (TypeError, ValueError) as exc:
        raise StructuralEnergyError(f"{name} must be numeric") from exc
    if array.ndim != 2:
        raise StructuralEnergyError(f"{name} must be two-dimensional")
    if array.size == 0:
        raise StructuralEnergyError(f"{name} must not be empty")
    if not bool(np.all(np.isfinite(array))):
        raise StructuralEnergyError(f"{name} must contain only finite values")
    return array


def _as_square_matrix(value: Any, name: str = "A") -> np.ndarray:
    """Validate and return a finite square matrix."""

    matrix = _as_finite_matrix(value, name)
    if matrix.shape[0] != matrix.shape[1]:
        raise StructuralEnergyError(f"{name} must be square")
    return matrix


def _as_finite_vector(value: Any, length: int | None, name: str) -> np.ndarray:
    """Validate and return a finite one-dimensional vector."""

    try:
        vector = np.asarray(value, dtype=_numeric_dtype(value))
    except (TypeError, ValueError) as exc:
        raise StructuralEnergyError(f"{name} must be numeric") from exc
    if vector.ndim != 1:
        raise StructuralEnergyError(f"{name} must be one-dimensional")
    if vector.size == 0:
        raise StructuralEnergyError(f"{name} must not be empty")
    if length is not None and vector.shape[0] != length:
        raise StructuralEnergyError(f"{name} has incompatible length")
    if not bool(np.all(np.isfinite(vector))):
        raise StructuralEnergyError(f"{name} must contain only finite values")
    return vector


def _as_positive_vector(value: Any, length: int | None, name: str) -> np.ndarray:
    """Validate a finite, real, strictly positive parameter vector."""

    vector = _as_finite_vector(value, length, name)
    if np.iscomplexobj(vector):
        raise StructuralEnergyError(f"{name} must be real")
    if not bool(np.all(vector > 0.0)):
        raise StructuralEnergyError(f"{name} must be strictly positive")
    return np.asarray(vector, dtype=np.float64)


def _adjoint(matrix: np.ndarray) -> np.ndarray:
    """Return the transpose for real data and conjugate transpose otherwise."""

    return matrix.conj().T


def _safe_ratio(numerator: float, denominator: float) -> float | None:
    """Return a finite ratio, leaving an undefined zero denominator explicit."""

    if denominator == 0.0:
        return 0.0 if numerator == 0.0 else None
    value = numerator / denominator
    return float(value) if np.isfinite(value) else None


def symmetry_tolerance(order: int) -> float:
    """Return the documented relative Hermitian tolerance for binary64."""

    if not isinstance(order, int) or isinstance(order, bool) or order < 1:
        raise StructuralEnergyError("order must be a positive integer")
    return float(64.0 * np.finfo(np.float64).eps * max(1, order))


def symmetry_diagnostics(matrix: Any) -> dict[str, Any]:
    """Measure the absolute and relative Hermitian defect of a square matrix."""

    array = _as_square_matrix(matrix)
    component_scale = float(max(np.max(np.abs(array.real)), np.max(np.abs(array.imag))))
    scaled = array.copy()
    if component_scale:
        scaled = array.real / component_scale
        if np.iscomplexobj(array):
            scaled = scaled + 1j * (array.imag / component_scale)
    defect = scaled - _adjoint(scaled)
    defect_norm = float(np.linalg.norm(defect, ord="fro"))
    scaled_norm = float(np.linalg.norm(scaled, ord="fro"))
    relative = defect_norm / scaled_norm if scaled_norm else 0.0
    absolute = defect_norm * component_scale
    maximum = float(np.max(np.abs(defect))) * component_scale
    absolute_representable = bool(np.isfinite(absolute))
    tolerance = symmetry_tolerance(array.shape[0])
    return {
        "order": int(array.shape[0]),
        "absolute_frobenius_defect": absolute if absolute_representable else None,
        "absolute_defect_representable": absolute_representable,
        "relative_frobenius_defect": relative,
        "maximum_entry_defect": maximum if np.isfinite(maximum) else None,
        "relative_tolerance": tolerance,
        "is_exactly_hermitian": bool(np.array_equal(array, _adjoint(array))),
        "passes_tolerance": bool(np.isfinite(relative) and relative <= tolerance),
    }


def symmetric_skew_decomposition(matrix: Any) -> dict[str, np.ndarray]:
    """Split a square matrix into Hermitian and skew-Hermitian parts."""

    array = _as_square_matrix(matrix)
    hermitian = 0.5 * (array + _adjoint(array))
    skew = 0.5 * (array - _adjoint(array))
    return {
        "hermitian": hermitian,
        "skew_hermitian": skew,
        "reconstruction": hermitian + skew,
    }


def quadratic_form(matrix: Any, vector: Any) -> complex | float:
    """Evaluate x* A x with the conjugate inner-product convention."""

    array = _as_square_matrix(matrix)
    x = _as_finite_vector(vector, array.shape[0], "x")
    dtype = np.result_type(array.dtype, x.dtype)
    array = np.asarray(array, dtype=dtype)
    x = np.asarray(x, dtype=dtype)
    value = np.vdot(x, array @ x)
    if abs(float(np.imag(value))) <= 32.0 * np.finfo(np.float64).eps * max(
        1.0, abs(float(np.real(value)))
    ):
        return float(np.real(value))
    return complex(value)


def leading_principal_minors(matrix: Any) -> list[float]:
    """Return real leading principal determinants after a Hermitian check."""

    array = _as_square_matrix(matrix)
    diagnostics = symmetry_diagnostics(array)
    if not diagnostics["passes_tolerance"]:
        raise StructuralEnergyError("A must be Hermitian before testing minors")
    determinants: list[float] = []
    for stop in range(1, array.shape[0] + 1):
        value = np.linalg.det(array[:stop, :stop])
        imaginary = abs(float(np.imag(value)))
        real = float(np.real(value))
        if imaginary > 128.0 * np.finfo(np.float64).eps * max(1.0, abs(real)):
            raise StructuralEnergyError("a Hermitian leading minor became non-real")
        determinants.append(real)
    return determinants


def educational_cholesky(matrix: Any) -> np.ndarray:
    """Compute a small Cholesky factor with explicit textbook loops.

    This routine is for education and independent checking only. Use the
    maintained library factorization for actual engineering calculations.
    """

    array = _as_square_matrix(matrix)
    diagnostics = symmetry_diagnostics(array)
    if not diagnostics["passes_tolerance"]:
        raise StructuralEnergyError("A must be Hermitian before Cholesky")
    order = array.shape[0]
    factor = np.zeros_like(array)
    scale = max(1.0, float(np.linalg.norm(array, ord=np.inf)))
    pivot_tolerance = 128.0 * np.finfo(np.float64).eps * scale
    for column in range(order):
        previous = np.vdot(factor[column, :column], factor[column, :column])
        pivot = array[column, column] - previous
        if abs(float(np.imag(pivot))) > pivot_tolerance:
            raise StructuralEnergyError("a Cholesky pivot is not real")
        pivot_real = float(np.real(pivot))
        if pivot_real <= pivot_tolerance:
            raise StructuralEnergyError("A is not numerically positive definite")
        factor[column, column] = np.sqrt(pivot_real)
        for row in range(column + 1, order):
            correction = np.dot(
                factor[row, :column], np.conjugate(factor[column, :column])
            )
            factor[row, column] = (
                array[row, column] - correction
            ) / factor[column, column]
    return factor


def cholesky_solve_with_diagnostics(matrix: Any, right_hand_side: Any) -> dict[str, Any]:
    """Solve a Hermitian positive-definite system and report diagnostics."""

    array = _as_square_matrix(matrix)
    rhs = _as_finite_vector(right_hand_side, array.shape[0], "b")
    dtype = np.result_type(array.dtype, rhs.dtype)
    array = np.asarray(array, dtype=dtype)
    rhs = np.asarray(rhs, dtype=dtype)
    symmetry = symmetry_diagnostics(array)
    if not symmetry["passes_tolerance"]:
        raise StructuralEnergyError(
            "A failed the explicit Hermitian check; no symmetrization was applied"
        )
    try:
        lower = np.linalg.cholesky(array)
    except np.linalg.LinAlgError as exc:
        raise StructuralEnergyError(
            "A is not positive definite; no diagonal jitter was applied"
        ) from exc
    pivot_scale = max(1.0, float(np.linalg.norm(array, ord=np.inf)))
    pivot_threshold = 128.0 * np.finfo(np.float64).eps * pivot_scale
    smallest_computed_pivot = float(np.min(np.abs(np.diag(lower))) ** 2)
    if smallest_computed_pivot <= pivot_threshold:
        raise StructuralEnergyError(
            "A is numerically semidefinite at the documented pivot tolerance; "
            "no diagonal jitter was applied"
        )
    intermediate = np.linalg.solve(lower, rhs)
    solution = np.linalg.solve(_adjoint(lower), intermediate)
    residual = rhs - array @ solution
    residual_norm = float(np.linalg.norm(residual, ord=2))
    matrix_norm = float(np.linalg.norm(array, ord=2))
    solution_norm = float(np.linalg.norm(solution, ord=2))
    rhs_norm = float(np.linalg.norm(rhs, ord=2))
    denominator = matrix_norm * solution_norm + rhs_norm
    factor_residual = array - lower @ _adjoint(lower)
    factor_residual_norm = float(np.linalg.norm(factor_residual, ord="fro"))
    matrix_frobenius = float(np.linalg.norm(array, ord="fro"))
    return {
        "solution": solution,
        "lower_factor": lower,
        "intermediate_solution": intermediate,
        "residual": residual,
        "residual_norm_2": residual_norm,
        "relative_rhs_residual_2": _safe_ratio(residual_norm, rhs_norm),
        "scaled_backward_error_2": _safe_ratio(residual_norm, denominator),
        "condition_number_2": float(np.linalg.cond(array, p=2)),
        "factor_residual_frobenius": factor_residual_norm,
        "relative_factor_residual_frobenius": _safe_ratio(
            factor_residual_norm, matrix_frobenius
        ),
        "smallest_computed_pivot": smallest_computed_pivot,
        "pivot_rejection_threshold": pivot_threshold,
        "symmetry": symmetry,
        "explicit_inverse_formed": False,
        "silent_symmetrization_applied": False,
        "diagonal_jitter_applied": False,
    }


def assemble_spring_stiffness(incidence: Any, spring_constants: Any) -> dict[str, Any]:
    """Assemble K = B* D B for an oriented spring incidence matrix."""

    b_matrix = _as_finite_matrix(incidence, "B")
    if np.iscomplexobj(b_matrix):
        raise StructuralEnergyError("B must be real for the spring model")
    constants = _as_positive_vector(spring_constants, b_matrix.shape[0], "k")
    diagonal = np.diag(constants)
    stiffness = b_matrix.T @ diagonal @ b_matrix
    return {
        "incidence": np.asarray(b_matrix, dtype=np.float64),
        "spring_constants": constants,
        "spring_diagonal": diagonal,
        "stiffness": stiffness,
        "symmetry": symmetry_diagnostics(stiffness),
    }


def spring_energy(incidence: Any, spring_constants: Any, displacement: Any) -> dict[str, Any]:
    """Compute extensions, spring forces, and elastic energy."""

    assembly = assemble_spring_stiffness(incidence, spring_constants)
    b_matrix = assembly["incidence"]
    displacement_vector = _as_finite_vector(
        displacement, b_matrix.shape[1], "u"
    )
    if np.iscomplexobj(displacement_vector):
        raise StructuralEnergyError("u must be real for the spring model")
    extension = b_matrix @ displacement_vector
    spring_force = assembly["spring_diagonal"] @ extension
    energy_from_springs = 0.5 * float(extension @ spring_force)
    energy_from_stiffness = 0.5 * float(
        displacement_vector @ assembly["stiffness"] @ displacement_vector
    )
    return {
        **assembly,
        "displacement": displacement_vector,
        "extension": extension,
        "spring_force": spring_force,
        "internal_energy_from_springs": energy_from_springs,
        "internal_energy_from_stiffness": energy_from_stiffness,
        "energy_identity_error": abs(energy_from_springs - energy_from_stiffness),
    }


def grounded_spring_case() -> dict[str, Any]:
    """Solve the three-degree-of-freedom grounded spring benchmark."""

    incidence = np.array(
        [
            [1.0, 0.0, 0.0],
            [-1.0, 1.0, 0.0],
            [0.0, -1.0, 1.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float64,
    )
    constants = np.array([1200.0, 800.0, 1500.0, 1000.0], dtype=np.float64)
    applied_force = np.array([100.0, -40.0, 60.0], dtype=np.float64)
    assembly = assemble_spring_stiffness(incidence, constants)
    solve = cholesky_solve_with_diagnostics(assembly["stiffness"], applied_force)
    displacement = solve["solution"]
    energy = spring_energy(incidence, constants, displacement)
    internal = energy["internal_energy_from_springs"]
    external_work = float(applied_force @ displacement)
    potential = internal - external_work
    equilibrium_residual = assembly["stiffness"] @ displacement - applied_force
    perturbation = np.array([0.001, -0.0005, 0.0008], dtype=np.float64)
    displaced = displacement + perturbation
    perturbed_energy = spring_energy(incidence, constants, displaced)
    perturbed_potential = (
        perturbed_energy["internal_energy_from_springs"]
        - float(applied_force @ displaced)
    )
    predicted_increase = 0.5 * float(
        perturbation @ assembly["stiffness"] @ perturbation
    )
    return {
        "incidence": incidence,
        "spring_constants": constants,
        "applied_force": applied_force,
        "stiffness": assembly["stiffness"],
        "leading_principal_minors": leading_principal_minors(assembly["stiffness"]),
        "solve": solve,
        "displacement": displacement,
        "extension": energy["extension"],
        "spring_force": energy["spring_force"],
        "equilibrium_residual": equilibrium_residual,
        "internal_energy": internal,
        "external_work": external_work,
        "total_potential": potential,
        "work_energy_identity_error": abs(external_work - 2.0 * internal),
        "energy_identity_error": energy["energy_identity_error"],
        "perturbation": perturbation,
        "perturbed_potential": perturbed_potential,
        "predicted_potential_increase": predicted_increase,
        "observed_potential_increase": perturbed_potential - potential,
        "units": {
            "spring_constant": "N/m",
            "applied_force": "N",
            "displacement": "m",
            "extension": "m",
            "spring_force": "N",
            "energy": "J",
            "stiffness": "N/m",
        },
    }


def free_free_spring_case() -> dict[str, Any]:
    """Expose the rigid translation mode of an ungrounded spring chain."""

    incidence = np.array(
        [[-1.0, 1.0, 0.0], [0.0, -1.0, 1.0]], dtype=np.float64
    )
    constants = np.array([800.0, 1500.0], dtype=np.float64)
    assembly = assemble_spring_stiffness(incidence, constants)
    stiffness = assembly["stiffness"]
    translation = np.ones(3, dtype=np.float64)
    trial = np.array([0.01, -0.02, 0.015], dtype=np.float64)
    shift = 0.125
    base_energy = spring_energy(incidence, constants, trial)
    shifted_energy = spring_energy(incidence, constants, trial + shift * translation)
    failure_message = ""
    cholesky_succeeded = False
    try:
        cholesky_solve_with_diagnostics(stiffness, np.array([50.0, -80.0, 30.0]))
        cholesky_succeeded = True
    except StructuralEnergyError as exc:
        failure_message = str(exc)
    return {
        "incidence": incidence,
        "spring_constants": constants,
        "stiffness": stiffness,
        "translation_mode": translation,
        "translation_null_residual": stiffness @ translation,
        "rank": int(np.linalg.matrix_rank(stiffness)),
        "determinant": float(np.linalg.det(stiffness)),
        "trial_displacement": trial,
        "shift": shift,
        "base_energy": base_energy["internal_energy_from_springs"],
        "shifted_energy": shifted_energy["internal_energy_from_springs"],
        "translation_energy_difference": (
            shifted_energy["internal_energy_from_springs"]
            - base_energy["internal_energy_from_springs"]
        ),
        "cholesky_succeeded": cholesky_succeeded,
        "failure_message": failure_message,
        "positive_semidefinite_by_construction": True,
    }


def grounding_transition_case() -> dict[str, Any]:
    """Show how a weakening ground spring approaches a free rigid mode."""

    internal_incidence = np.array(
        [[-1.0, 1.0, 0.0], [0.0, -1.0, 1.0]], dtype=np.float64
    )
    internal_constants = np.array([800.0, 1500.0], dtype=np.float64)
    ground_constants = [1000.0, 100.0, 1.0, 0.001]
    rows: list[dict[str, Any]] = []
    force = np.array([10.0, -4.0, 3.0], dtype=np.float64)
    for ground_constant in ground_constants:
        incidence = np.vstack((np.array([[1.0, 0.0, 0.0]]), internal_incidence))
        constants = np.concatenate(
            (np.array([ground_constant], dtype=np.float64), internal_constants)
        )
        assembly = assemble_spring_stiffness(incidence, constants)
        solve = cholesky_solve_with_diagnostics(assembly["stiffness"], force)
        rows.append(
            {
                "ground_constant": ground_constant,
                "condition_number_2": solve["condition_number_2"],
                "solution_norm_2": float(np.linalg.norm(solve["solution"], ord=2)),
                "scaled_backward_error_2": solve["scaled_backward_error_2"],
                "smallest_cholesky_diagonal": float(
                    np.min(np.diag(solve["lower_factor"]))
                ),
                "leading_principal_minors": leading_principal_minors(
                    assembly["stiffness"]
                ),
            }
        )
    return {
        "rows": rows,
        "trend": "condition_number_increases_as_grounding_weakens",
        "units": {"ground_constant": "N/m", "solution_norm": "m"},
    }


def quadratic_minimization_case() -> dict[str, Any]:
    """Verify the completed-square identity at a strict quadratic minimum."""

    matrix = np.array(
        [[6.0, -2.0, 1.0], [-2.0, 5.0, 0.5], [1.0, 0.5, 3.0]],
        dtype=np.float64,
    )
    linear = np.array([4.0, -3.0, 2.0], dtype=np.float64)
    solve = cholesky_solve_with_diagnostics(matrix, linear)
    minimizer = solve["solution"]
    direction = np.array([0.25, -0.5, 0.4], dtype=np.float64)

    def objective(vector: np.ndarray) -> float:
        return 0.5 * float(vector @ matrix @ vector) - float(linear @ vector)

    minimum_value = objective(minimizer)
    trial_value = objective(minimizer + direction)
    predicted_increase = 0.5 * float(direction @ matrix @ direction)
    return {
        "matrix": matrix,
        "linear_term": linear,
        "minimizer": minimizer,
        "stationarity_residual": matrix @ minimizer - linear,
        "minimum_value": minimum_value,
        "direction": direction,
        "trial_value": trial_value,
        "observed_increase": trial_value - minimum_value,
        "predicted_increase": predicted_increase,
        "leading_principal_minors": leading_principal_minors(matrix),
        "solve": solve,
    }


def covariance_whitening_case() -> dict[str, Any]:
    """Whiten a correlated three-sensor residual without an explicit inverse."""

    covariance = np.array(
        [[4.0, 1.2, 0.4], [1.2, 2.25, 0.3], [0.4, 0.3, 1.0]],
        dtype=np.float64,
    )
    residual = np.array([1.0, -0.5, 0.25], dtype=np.float64)
    lower = np.linalg.cholesky(covariance)
    whitened = np.linalg.solve(lower, residual)
    left_whitened_covariance = np.linalg.solve(lower, covariance)
    whitened_covariance = np.linalg.solve(
        lower, left_whitened_covariance.T
    ).T
    covariance_solution = np.linalg.solve(covariance, residual)
    mahalanobis_squared = float(residual @ covariance_solution)
    whitened_squared_norm = float(whitened @ whitened)
    diagonal_only_squared = float(
        np.sum((residual * residual) / np.diag(covariance))
    )
    return {
        "covariance": covariance,
        "residual": residual,
        "lower_factor": lower,
        "whitened_residual": whitened,
        "whitened_covariance": whitened_covariance,
        "whitening_identity_error_frobenius": float(
            np.linalg.norm(whitened_covariance - np.eye(3), ord="fro")
        ),
        "mahalanobis_squared": mahalanobis_squared,
        "whitened_squared_norm": whitened_squared_norm,
        "identity_error": abs(mahalanobis_squared - whitened_squared_norm),
        "diagonal_only_squared": diagonal_only_squared,
        "correlations_ignored_by_diagonal_only": True,
        "leading_principal_minors": leading_principal_minors(covariance),
        "units": {
            "sensor_residual": "calibrated sensor units",
            "covariance_entry": "product of corresponding sensor units",
            "whitened_residual": "dimensionless",
            "mahalanobis_squared": "dimensionless",
        },
    }


def hermitian_extension_case() -> dict[str, Any]:
    """Verify a complex Hermitian energy and its Cholesky factor."""

    matrix = np.array(
        [[3.0 + 0.0j, 1.0 + 1.0j], [1.0 - 1.0j, 2.0 + 0.0j]],
        dtype=np.complex128,
    )
    vector = np.array([1.0 + 2.0j, -0.5 + 0.25j], dtype=np.complex128)
    factor = np.linalg.cholesky(matrix)
    energy = quadratic_form(matrix, vector)
    decomposition = symmetric_skew_decomposition(matrix)
    return {
        "matrix": matrix,
        "vector": vector,
        "energy": energy,
        "lower_factor": factor,
        "factor_residual_frobenius": float(
            np.linalg.norm(matrix - factor @ _adjoint(factor), ord="fro")
        ),
        "symmetry": symmetry_diagnostics(matrix),
        "leading_principal_minors": leading_principal_minors(matrix),
        "skew_part_norm_frobenius": float(
            np.linalg.norm(decomposition["skew_hermitian"], ord="fro")
        ),
        "energy_is_real": not isinstance(energy, complex),
    }


def rejected_nonsymmetric_case() -> dict[str, Any]:
    """Record the required rejection of a non-symmetric Cholesky input."""

    matrix = np.array([[2.0, 1.0], [0.0, 2.0]], dtype=np.float64)
    rhs = np.array([1.0, 1.0], dtype=np.float64)
    message = ""
    rejected = False
    try:
        cholesky_solve_with_diagnostics(matrix, rhs)
    except StructuralEnergyError as exc:
        rejected = True
        message = str(exc)
    return {
        "matrix": matrix,
        "symmetry": symmetry_diagnostics(matrix),
        "rejected": rejected,
        "message": message,
        "silent_symmetrization_applied": False,
        "diagonal_jitter_applied": False,
    }


def _json_ready(value: Any) -> Any:
    """Convert NumPy and complex values to strict, deterministic JSON data."""

    if isinstance(value, np.ndarray):
        return [_json_ready(item) for item in value.tolist()]
    if isinstance(value, np.generic):
        return _json_ready(value.item())
    if isinstance(value, complex):
        if not np.isfinite(value.real) or not np.isfinite(value.imag):
            raise StructuralEnergyError("non-finite complex value in output")
        if value.imag == 0.0:
            return float(value.real)
        return {"real": float(value.real), "imag": float(value.imag)}
    if isinstance(value, float):
        if not np.isfinite(value):
            raise StructuralEnergyError("non-finite floating value in output")
        return value
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


def chapter_results() -> dict[str, Any]:
    """Return the complete deterministic Chapter 11 result contract."""

    raw = {
        "schema_version": "1.0",
        "version": "v1.2",
        "chapter": 11,
        "title": "Simetri, Enerji ve Pozitif Tanımlılık",
        "vector_convention": "column_vectors_left_multiplication",
        "inner_product_convention": "conjugate_linear_first_argument",
        "residual_convention": "right_hand_side_minus_matrix_times_solution",
        "factor_convention": "A_equals_L_times_conjugate_transpose_L",
        "floating_point_type": "numpy.float64_and_complex128",
        "external_data": False,
        "randomness": False,
        "explicit_matrix_inverse_for_solves": False,
        "silent_symmetrization": False,
        "diagonal_jitter": False,
        "grounded_spring": grounded_spring_case(),
        "free_free_spring": free_free_spring_case(),
        "grounding_transition": grounding_transition_case(),
        "quadratic_minimization": quadratic_minimization_case(),
        "covariance_whitening": covariance_whitening_case(),
        "hermitian_extension": hermitian_extension_case(),
        "rejected_nonsymmetric_input": rejected_nonsymmetric_case(),
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "platform": platform.platform(),
            "executable": Path(sys.executable).name,
        },
    }
    return _json_ready(raw)


def strict_json_dumps(value: Any) -> str:
    """Serialize an output while refusing NaN and infinity."""

    return json.dumps(
        _json_ready(value),
        allow_nan=False,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )


def human_summary(results: dict[str, Any]) -> str:
    """Return a compact terminal summary of the principal validation facts."""

    grounded = results["grounded_spring"]
    free = results["free_free_spring"]
    covariance = results["covariance_whitening"]
    lines = [
        "Bölüm 11 deterministik hesap özeti",
        f"Mesnetli sistem koşul sayısı: {grounded['solve']['condition_number_2']:.6g}",
        f"Mesnetli sistem geri hatası: {grounded['solve']['scaled_backward_error_2']:.3e}",
        f"Enerji özdeşliği hatası: {grounded['energy_identity_error']:.3e} J",
        f"Serbest sistem rankı: {free['rank']} / 3",
        f"Serbest sistem Cholesky başarısı: {free['cholesky_succeeded']}",
        f"Beyazlatma özdeşlik hatası: {covariance['whitening_identity_error_frobenius']:.3e}",
        "Açık ters: yok; sessiz simetrikleştirme: yok; köşegen jitter: yok",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    """Parse the command-line output mode."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json", action="store_true", help="Print the strict JSON result contract."
    )
    return parser.parse_args()


def main() -> None:
    """Run every deterministic case and print the requested representation."""

    arguments = parse_args()
    results = chapter_results()
    if arguments.json:
        print(strict_json_dumps(results))
    else:
        print(human_summary(results))


if __name__ == "__main__":
    main()
