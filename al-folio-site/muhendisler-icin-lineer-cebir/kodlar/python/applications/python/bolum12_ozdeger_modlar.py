#!/usr/bin/env python3
"""Chapter 12 deterministic eigenvalue, modal, and stability laboratory.

The module uses only NumPy and the Python standard library. It validates
matrix structure before selecting an eigensolver, never forms an explicit
matrix inverse, never silently symmetrizes an input, and never clips a
negative generalized eigenvalue into a vibration frequency.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np


class EigenAnalysisError(ValueError):
    """Raised when an eigenvalue analysis contract is not satisfied."""


def _as_square_matrix(value: Any, *, name: str = "matrix") -> np.ndarray:
    """Return a finite numeric square matrix without changing its structure."""

    try:
        array = np.asarray(value)
    except (TypeError, ValueError) as exc:
        raise EigenAnalysisError(f"{name} must be a numeric square matrix") from exc
    if array.ndim != 2:
        raise EigenAnalysisError(f"{name} must be two-dimensional")
    if array.shape[0] == 0 or array.shape[1] == 0:
        raise EigenAnalysisError(f"{name} must not be empty")
    if array.shape[0] != array.shape[1]:
        raise EigenAnalysisError(f"{name} must be square")
    if array.dtype.kind not in "biufc":
        raise EigenAnalysisError(f"{name} must be numeric")
    result = np.asarray(array, dtype=np.complex128 if np.iscomplexobj(array) else np.float64)
    if not np.all(np.isfinite(result)):
        raise EigenAnalysisError(f"{name} must contain only finite values")
    return result


def _as_vector(
    value: Any,
    *,
    length: int | None = None,
    name: str = "vector",
    allow_complex: bool = True,
) -> np.ndarray:
    """Return a finite numeric one-dimensional vector."""

    try:
        array = np.asarray(value)
    except (TypeError, ValueError) as exc:
        raise EigenAnalysisError(f"{name} must be a numeric vector") from exc
    if array.ndim != 1:
        raise EigenAnalysisError(f"{name} must be one-dimensional")
    if array.size == 0:
        raise EigenAnalysisError(f"{name} must not be empty")
    if length is not None and array.size != length:
        raise EigenAnalysisError(f"{name} length must be {length}")
    if array.dtype.kind not in "biufc":
        raise EigenAnalysisError(f"{name} must be numeric")
    if not allow_complex and np.iscomplexobj(array) and np.any(np.imag(array) != 0.0):
        raise EigenAnalysisError(f"{name} must be real")
    dtype = np.complex128 if np.iscomplexobj(array) else np.float64
    result = np.asarray(array, dtype=dtype)
    if not np.all(np.isfinite(result)):
        raise EigenAnalysisError(f"{name} must contain only finite values")
    return result


def _positive_real_vector(value: Any, *, name: str) -> np.ndarray:
    """Validate a nonempty vector of strictly positive real parameters."""

    vector = _as_vector(value, name=name, allow_complex=False).astype(np.float64)
    if np.any(vector <= 0.0):
        raise EigenAnalysisError(f"{name} entries must be strictly positive")
    return vector


def hermitian_tolerance(order: int) -> float:
    """Return the documented binary64 structure tolerance for an order n matrix."""

    if not isinstance(order, (int, np.integer)):
        raise EigenAnalysisError("matrix order must be an integer")
    if int(order) <= 0:
        raise EigenAnalysisError("matrix order must be positive")
    return float(64.0 * int(order) * np.finfo(np.float64).eps)


def hermitian_diagnostics(matrix: Any) -> dict[str, Any]:
    """Measure exact and normwise Hermitian defects without repairing input."""

    array = _as_square_matrix(matrix)
    component_scale = float(max(np.max(np.abs(array.real)), np.max(np.abs(array.imag))))
    scaled = array.copy()
    if component_scale:
        scaled = array.real / component_scale
        if np.iscomplexobj(array):
            scaled = scaled + 1j * (array.imag / component_scale)
    defect = scaled - scaled.conj().T
    defect_norm = float(np.linalg.norm(defect, ord="fro"))
    scaled_norm = float(np.linalg.norm(scaled, ord="fro"))
    relative = defect_norm / scaled_norm if scaled_norm else 0.0
    absolute = defect_norm * component_scale
    maximum = float(np.max(np.abs(defect))) * component_scale
    absolute_representable = bool(np.isfinite(absolute))
    tolerance = hermitian_tolerance(array.shape[0])
    return {
        "order": int(array.shape[0]),
        "is_exactly_hermitian": bool(np.array_equal(array, array.conj().T)),
        "absolute_frobenius_defect": absolute if absolute_representable else None,
        "absolute_defect_representable": absolute_representable,
        "relative_frobenius_defect": relative,
        "maximum_entry_defect": maximum if np.isfinite(maximum) else None,
        "relative_tolerance": tolerance,
        "passes_tolerance": bool(np.isfinite(relative) and relative <= tolerance),
        "silent_symmetrization_applied": False,
    }


def require_hermitian(matrix: Any, *, name: str = "matrix") -> np.ndarray:
    """Return a matrix only when its recorded Hermitian defect passes tolerance."""

    array = _as_square_matrix(matrix, name=name)
    diagnostics = hermitian_diagnostics(array)
    if not diagnostics["passes_tolerance"]:
        raise EigenAnalysisError(
            f"{name} is not Hermitian within the documented tolerance"
        )
    return array


def _component_scaled(array: np.ndarray) -> tuple[np.ndarray, float]:
    """Scale a local copy by its largest real/imaginary component."""

    scale = float(max(np.max(np.abs(array.real)), np.max(np.abs(array.imag))))
    if scale == 0.0:
        return array.copy(), scale
    scaled = array.real / scale
    if np.iscomplexobj(array):
        scaled = scaled + 1j * (array.imag / scale)
    return scaled, scale


def _unit_direction(vector: np.ndarray) -> np.ndarray:
    """Normalize a nonzero local direction without squaring tiny components."""

    scaled, scale = _component_scaled(vector)
    if scale == 0.0:
        raise EigenAnalysisError("a mode or eigenvector cannot be the zero vector")
    norm = math.hypot(*scaled.real, *scaled.imag)
    return scaled / norm


def _positive_definite_metric(
    metric: Any, *, name: str
) -> tuple[np.ndarray, np.ndarray, float]:
    """Check the existing Hermitian gate and SPD without input repair."""

    array = require_hermitian(metric, name=name)
    scaled, scale = _component_scaled(array)
    try:
        lower = np.linalg.cholesky(scaled)
    except np.linalg.LinAlgError as exc:
        raise EigenAnalysisError(f"{name} must be positive definite") from exc
    return array, lower, scale


def canonicalize_vector(vector: Any, *, normalize: bool = True) -> np.ndarray:
    """Choose a display sign or phase, optionally preserving vector scale."""

    result = _as_vector(vector, name="eigenvector").astype(
        np.complex128 if np.iscomplexobj(vector) else np.float64,
        copy=True,
    )
    norm = float(np.linalg.norm(result, ord=2))
    if norm == 0.0:
        raise EigenAnalysisError("an eigenvector cannot be the zero vector")
    if normalize:
        result /= norm
    pivot = int(np.argmax(np.abs(result)))
    pivot_value = result[pivot]
    if np.iscomplexobj(result):
        phase = pivot_value / abs(pivot_value)
        result /= phase
        result[pivot] = complex(abs(result[pivot]), 0.0)
    elif result[pivot] < 0.0:
        result *= -1.0
    return result


def canonicalize_columns(vectors: Any, *, normalize: bool = True) -> np.ndarray:
    """Canonicalize column phases, optionally preserving every column scale."""

    array = np.asarray(vectors)
    if array.ndim != 2 or array.shape[0] == 0 or array.shape[1] == 0:
        raise EigenAnalysisError("eigenvectors must be a nonempty two-dimensional array")
    if array.dtype.kind not in "biufc" or not np.all(np.isfinite(array)):
        raise EigenAnalysisError("eigenvectors must be finite and numeric")
    result = np.asarray(
        array, dtype=np.complex128 if np.iscomplexobj(array) else np.float64
    ).copy()
    for column in range(result.shape[1]):
        result[:, column] = canonicalize_vector(
            result[:, column], normalize=normalize
        )
    return result


def _general_sort_indices(eigenvalues: np.ndarray) -> np.ndarray:
    """Return a deterministic lexicographic order for complex eigenvalues."""

    values = np.asarray(eigenvalues, dtype=np.complex128)
    return np.lexsort((np.imag(values), np.real(values)))


def eigenpair_residuals(
    matrix: Any,
    eigenvalues: Any,
    eigenvectors: Any,
    *,
    metric: Any | None = None,
) -> dict[str, Any]:
    """Compute absolute and scaled residuals for A v = lambda B v."""

    array = _as_square_matrix(matrix, name="matrix")
    values = _as_vector(eigenvalues, name="eigenvalues")
    vectors = np.asarray(eigenvectors)
    if vectors.ndim != 2 or vectors.shape != (array.shape[0], values.size):
        raise EigenAnalysisError("eigenvector matrix has incompatible dimensions")
    if vectors.dtype.kind not in "biufc" or not np.all(np.isfinite(vectors)):
        raise EigenAnalysisError("eigenvector matrix must be finite and numeric")
    vectors = np.asarray(vectors, dtype=np.complex128)
    if metric is None:
        metric_array = np.eye(array.shape[0], dtype=np.complex128)
    else:
        metric_array = _as_square_matrix(metric, name="metric")
        if metric_array.shape != array.shape:
            raise EigenAnalysisError("metric must have the same shape as matrix")
    matrix_norm = float(np.linalg.norm(array, ord=2))
    metric_norm = float(np.linalg.norm(metric_array, ord=2))
    absolute: list[float] = []
    scaled: list[float] = []
    for index, value in enumerate(values):
        vector = vectors[:, index]
        local_vector, vector_scale = _component_scaled(vector)
        if vector_scale == 0.0:
            raise EigenAnalysisError("an eigenvector cannot be the zero vector")
        residual = array @ local_vector - value * (metric_array @ local_vector)
        local_residual_norm = math.hypot(*residual.real, *residual.imag)
        residual_norm = local_residual_norm * vector_scale
        if not math.isfinite(residual_norm):
            raise EigenAnalysisError("absolute eigenpair residual is not representable")
        denominator = (
            matrix_norm + abs(complex(value)) * metric_norm
        ) * math.hypot(*local_vector.real, *local_vector.imag)
        if not math.isfinite(local_residual_norm) or not math.isfinite(denominator):
            raise EigenAnalysisError("scaled eigenpair residual is not representable")
        absolute.append(residual_norm)
        scaled.append(0.0 if denominator == 0.0 else local_residual_norm / denominator)
    return {
        "absolute_residual_norms_2": np.asarray(absolute),
        "scaled_residuals_2": np.asarray(scaled),
        "maximum_absolute_residual_norm_2": max(absolute, default=0.0),
        "maximum_scaled_residual_2": max(scaled, default=0.0),
    }


def rayleigh_quotient(matrix: Any, vector: Any) -> float:
    """Return x^H A x / x^H x for Hermitian A and nonzero x."""

    array = require_hermitian(matrix)
    direction = _as_vector(vector, length=array.shape[0])
    denominator = np.vdot(direction, direction)
    if abs(complex(denominator)) == 0.0:
        raise EigenAnalysisError("Rayleigh quotient requires a nonzero vector")
    value = np.vdot(direction, array @ direction) / denominator
    imaginary_tolerance = hermitian_tolerance(array.shape[0]) * max(1.0, abs(value))
    if abs(float(np.imag(value))) > imaginary_tolerance:
        raise EigenAnalysisError("Hermitian Rayleigh quotient has an unexpected imaginary part")
    return float(np.real(value))


def generalized_rayleigh_quotient(stiffness: Any, mass: Any, vector: Any) -> float:
    """Return phi^H K phi / phi^H M phi for a positive mass metric."""

    stiffness_array = require_hermitian(stiffness, name="stiffness")
    mass_array = require_hermitian(mass, name="mass")
    if stiffness_array.shape != mass_array.shape:
        raise EigenAnalysisError("stiffness and mass must have the same shape")
    direction = _as_vector(vector, length=stiffness_array.shape[0])
    try:
        np.linalg.cholesky(mass_array)
    except np.linalg.LinAlgError as exc:
        raise EigenAnalysisError("mass must be positive definite") from exc
    denominator = np.vdot(direction, mass_array @ direction)
    if float(np.real(denominator)) <= 0.0:
        raise EigenAnalysisError("mass metric must give positive norm to the vector")
    value = np.vdot(direction, stiffness_array @ direction) / denominator
    tolerance = hermitian_tolerance(stiffness_array.shape[0]) * max(1.0, abs(value))
    if abs(float(np.imag(value))) > tolerance:
        raise EigenAnalysisError("generalized Rayleigh quotient is unexpectedly complex")
    return float(np.real(value))


def symmetric_eigendecomposition(matrix: Any) -> dict[str, Any]:
    """Compute and independently diagnose a Hermitian eigendecomposition."""

    array = require_hermitian(matrix)
    try:
        eigenvalues, raw_vectors = np.linalg.eigh(array)
    except np.linalg.LinAlgError as exc:
        raise EigenAnalysisError("Hermitian eigensolver did not converge") from exc
    eigenvectors = canonicalize_columns(raw_vectors)
    diagonal = np.diag(eigenvalues)
    reconstruction = eigenvectors @ diagonal @ eigenvectors.conj().T
    scale = float(np.linalg.norm(array, ord="fro"))
    reconstruction_error = float(np.linalg.norm(array - reconstruction, ord="fro"))
    identity = np.eye(array.shape[0])
    orthogonality_error = float(
        np.linalg.norm(eigenvectors.conj().T @ eigenvectors - identity, ord="fro")
    )
    residuals = eigenpair_residuals(array, eigenvalues, eigenvectors)
    return {
        "method": "numpy.linalg.eigh",
        "matrix_order": int(array.shape[0]),
        "eigenvalues": eigenvalues,
        "eigenvectors": eigenvectors,
        "hermitian_diagnostics": hermitian_diagnostics(array),
        "orthogonality_defect_frobenius": orthogonality_error,
        "absolute_reconstruction_error_frobenius": reconstruction_error,
        "relative_reconstruction_error_frobenius": (
            0.0 if scale == 0.0 else reconstruction_error / scale
        ),
        "trace": np.trace(array),
        "eigenvalue_sum": np.sum(eigenvalues),
        "residuals": residuals,
        "silent_symmetrization_applied": False,
        "eigenvalue_clipping_applied": False,
        "explicit_inverse_formed": False,
    }


def general_eigendecomposition(matrix: Any) -> dict[str, Any]:
    """Compute right eigenvectors of a general matrix and diagnose them."""

    array = _as_square_matrix(matrix)
    try:
        raw_values, raw_vectors = np.linalg.eig(array)
    except np.linalg.LinAlgError as exc:
        raise EigenAnalysisError("general eigensolver did not converge") from exc
    indices = _general_sort_indices(raw_values)
    eigenvalues = np.asarray(raw_values)[indices]
    eigenvectors = canonicalize_columns(np.asarray(raw_vectors)[:, indices])
    residuals = eigenpair_residuals(array, eigenvalues, eigenvectors)
    rank = int(np.linalg.matrix_rank(eigenvectors))
    condition = (
        float(np.linalg.cond(eigenvectors, p=2))
        if rank == array.shape[0]
        else math.inf
    )
    return {
        "method": "numpy.linalg.eig",
        "matrix_order": int(array.shape[0]),
        "eigenvalues": eigenvalues,
        "right_eigenvectors": eigenvectors,
        "right_eigenvector_rank": rank,
        "right_eigenvector_condition_number_2": condition,
        "diagonalizable_by_computed_basis": bool(rank == array.shape[0]),
        "residuals": residuals,
        "explicit_inverse_formed": False,
        "eigenvalue_clipping_applied": False,
    }


def characteristic_data_2x2(matrix: Any) -> dict[str, Any]:
    """Return hand-calculation coefficients for a real 2x2 matrix."""

    array = _as_square_matrix(matrix)
    if array.shape != (2, 2):
        raise EigenAnalysisError("characteristic_data_2x2 requires a 2x2 matrix")
    if np.iscomplexobj(array) and np.any(np.imag(array) != 0.0):
        raise EigenAnalysisError("the hand 2x2 example requires real entries")
    real_array = np.real(array)
    trace = float(np.trace(real_array))
    determinant = float(np.linalg.det(real_array))
    discriminant = trace * trace - 4.0 * determinant
    if discriminant >= 0.0:
        root = math.sqrt(discriminant)
        roots = np.asarray([(trace - root) / 2.0, (trace + root) / 2.0])
    else:
        root = math.sqrt(-discriminant)
        roots = np.asarray(
            [complex(trace / 2.0, -root / 2.0), complex(trace / 2.0, root / 2.0)]
        )
    return {
        "trace": trace,
        "determinant": determinant,
        "polynomial_coefficients_descending": np.asarray([1.0, -trace, determinant]),
        "discriminant": discriminant,
        "roots": roots,
        "purpose": "hand calculation only",
    }


def orthogonal_projector(basis: Any) -> np.ndarray:
    """Return the projector of an independent basis, including an empty basis."""

    array = np.asarray(basis)
    if array.ndim != 2 or array.shape[0] == 0:
        raise EigenAnalysisError("basis must have a positive ambient dimension")
    if array.dtype.kind not in "biufc" or not np.all(np.isfinite(array)):
        raise EigenAnalysisError("basis must be finite and numeric")
    array = np.asarray(array, dtype=np.complex128 if np.iscomplexobj(array) else np.float64)
    if array.shape[1] == 0:
        return np.zeros((array.shape[0], array.shape[0]), dtype=array.dtype)
    if array.shape[1] > array.shape[0]:
        raise EigenAnalysisError("a basis cannot have more columns than ambient dimensions")
    scaled, scale = _component_scaled(array)
    if scale == 0.0:
        raise EigenAnalysisError("basis columns must be linearly independent")
    singular_values = np.linalg.svd(scaled, compute_uv=False)
    tolerance = max(array.shape) * np.finfo(np.float64).eps * singular_values[0]
    if np.count_nonzero(singular_values > tolerance) != array.shape[1]:
        raise EigenAnalysisError("basis columns must be linearly independent")
    q, _ = np.linalg.qr(scaled, mode="reduced")
    return q @ q.conj().T


def subspace_distance(first_basis: Any, second_basis: Any) -> float:
    """Return the spectral norm of the difference between two projectors."""

    first = np.asarray(first_basis)
    second = np.asarray(second_basis)
    if first.ndim != 2 or second.ndim != 2 or first.shape[0] != second.shape[0]:
        raise EigenAnalysisError("subspace bases must share the same ambient dimension")
    return float(np.linalg.norm(orthogonal_projector(first) - orthogonal_projector(second), ord=2))


def modal_assurance_criterion(first: Any, second: Any, metric: Any | None = None) -> float:
    """Return MAC for nonzero modes and an SPD metric; never clip or repair."""

    first_vector = _as_vector(first, name="first mode")
    second_vector = _as_vector(second, length=first_vector.size, name="second mode")
    if metric is None:
        metric_array = np.eye(first_vector.size)
    else:
        metric_array = _as_square_matrix(metric, name="metric")
        if metric_array.shape[0] != first_vector.size:
            raise EigenAnalysisError("metric dimension must match the modes")
    _, lower, _ = _positive_definite_metric(metric_array, name="metric")
    first_unit = _unit_direction(lower.conj().T @ _unit_direction(first_vector))
    second_unit = _unit_direction(lower.conj().T @ _unit_direction(second_vector))
    return float(abs(np.vdot(first_unit, second_unit)) ** 2)


def eigenvalue_clusters(eigenvalues: Any, *, relative_gap: float = 1.0e-8) -> list[list[int]]:
    """Group sorted real eigenvalues whose adjacent relative gap is small."""

    values = _as_vector(eigenvalues, name="eigenvalues", allow_complex=False).astype(float)
    if relative_gap <= 0.0 or not math.isfinite(relative_gap):
        raise EigenAnalysisError("relative_gap must be finite and positive")
    if np.any(np.diff(values) < 0.0):
        raise EigenAnalysisError("eigenvalues must be sorted in nondecreasing order")
    groups: list[list[int]] = [[0]]
    for index in range(1, values.size):
        scale = max(1.0, abs(values[index - 1]), abs(values[index]))
        if abs(values[index] - values[index - 1]) <= relative_gap * scale:
            groups[-1].append(index)
        else:
            groups.append([index])
    return groups


def power_iteration(
    matrix: Any,
    initial_vector: Any,
    *,
    max_iterations: int = 100,
    tolerance: float = 1.0e-12,
) -> dict[str, Any]:
    """Educational dominant-eigenpair iteration with a required fixed start."""

    array = _as_square_matrix(matrix)
    vector = _as_vector(initial_vector, length=array.shape[0]).astype(
        np.complex128 if np.iscomplexobj(array) or np.iscomplexobj(initial_vector) else np.float64
    )
    if not isinstance(max_iterations, (int, np.integer)) or max_iterations <= 0:
        raise EigenAnalysisError("max_iterations must be a positive integer")
    if tolerance <= 0.0 or not math.isfinite(tolerance):
        raise EigenAnalysisError("tolerance must be finite and positive")
    norm = float(np.linalg.norm(vector, ord=2))
    if norm == 0.0:
        raise EigenAnalysisError("initial_vector must be nonzero")
    vector /= norm
    history: list[dict[str, Any]] = []
    converged = False
    eigenvalue: complex = complex(np.vdot(vector, array @ vector))
    for iteration in range(1, int(max_iterations) + 1):
        product = array @ vector
        product_norm = float(np.linalg.norm(product, ord=2))
        if product_norm == 0.0:
            raise EigenAnalysisError("power iteration reached the zero vector")
        vector = product / product_norm
        eigenvalue = complex(np.vdot(vector, array @ vector) / np.vdot(vector, vector))
        residual = float(np.linalg.norm(array @ vector - eigenvalue * vector, ord=2))
        scale = (
            float(np.linalg.norm(array, ord=2)) + abs(eigenvalue)
        ) * float(np.linalg.norm(vector, ord=2))
        scaled_residual = 0.0 if scale == 0.0 else residual / scale
        history.append(
            {
                "iteration": iteration,
                "eigenvalue_estimate": eigenvalue,
                "absolute_residual_norm_2": residual,
                "scaled_residual_2": scaled_residual,
            }
        )
        if scaled_residual <= tolerance:
            converged = True
            break
    return {
        "method": "educational power iteration",
        "eigenvalue": eigenvalue,
        "eigenvector": canonicalize_vector(vector),
        "iterations": len(history),
        "converged": converged,
        "tolerance": tolerance,
        "history": history,
        "random_start_used": False,
        "explicit_inverse_formed": False,
    }


def inverse_iteration(
    matrix: Any,
    shift: float | complex,
    initial_vector: Any,
    *,
    max_iterations: int = 40,
    tolerance: float = 1.0e-12,
) -> dict[str, Any]:
    """Educational shifted inverse iteration using solves, never an inverse."""

    array = _as_square_matrix(matrix)
    vector = _as_vector(initial_vector, length=array.shape[0]).astype(np.complex128)
    if not isinstance(max_iterations, (int, np.integer)) or max_iterations <= 0:
        raise EigenAnalysisError("max_iterations must be a positive integer")
    if tolerance <= 0.0 or not math.isfinite(tolerance):
        raise EigenAnalysisError("tolerance must be finite and positive")
    if not np.isfinite(shift):
        raise EigenAnalysisError("shift must be finite")
    norm = float(np.linalg.norm(vector, ord=2))
    if norm == 0.0:
        raise EigenAnalysisError("initial_vector must be nonzero")
    vector /= norm
    shifted = array.astype(np.complex128) - complex(shift) * np.eye(array.shape[0])
    history: list[dict[str, Any]] = []
    converged = False
    eigenvalue: complex = complex(np.vdot(vector, array @ vector))
    for iteration in range(1, int(max_iterations) + 1):
        try:
            solved = np.linalg.solve(shifted, vector)
        except np.linalg.LinAlgError as exc:
            raise EigenAnalysisError("shifted system is singular") from exc
        solved_norm = float(np.linalg.norm(solved, ord=2))
        if solved_norm == 0.0:
            raise EigenAnalysisError("inverse iteration reached the zero vector")
        vector = solved / solved_norm
        eigenvalue = complex(np.vdot(vector, array @ vector) / np.vdot(vector, vector))
        residual = float(np.linalg.norm(array @ vector - eigenvalue * vector, ord=2))
        scale = (
            float(np.linalg.norm(array, ord=2)) + abs(eigenvalue)
        ) * float(np.linalg.norm(vector, ord=2))
        scaled_residual = 0.0 if scale == 0.0 else residual / scale
        history.append(
            {
                "iteration": iteration,
                "eigenvalue_estimate": eigenvalue,
                "scaled_residual_2": scaled_residual,
            }
        )
        if scaled_residual <= tolerance:
            converged = True
            break
    return {
        "method": "educational shifted inverse iteration",
        "shift": shift,
        "eigenvalue": eigenvalue,
        "eigenvector": canonicalize_vector(vector),
        "iterations": len(history),
        "converged": converged,
        "history": history,
        "random_start_used": False,
        "explicit_inverse_formed": False,
    }


def assemble_shear_building(
    masses_kg: Any, story_stiffnesses_n_per_m: Any
) -> tuple[np.ndarray, np.ndarray]:
    """Assemble diagonal mass and fixed-base shear-building stiffness matrices."""

    masses = _positive_real_vector(masses_kg, name="masses_kg")
    stiffnesses = _positive_real_vector(
        story_stiffnesses_n_per_m, name="story_stiffnesses_n_per_m"
    )
    if masses.size != stiffnesses.size:
        raise EigenAnalysisError("one positive story stiffness is required per mass")
    order = masses.size
    mass = np.diag(masses)
    stiffness = np.zeros((order, order), dtype=np.float64)
    for index, value in enumerate(stiffnesses):
        if index == 0:
            stiffness[0, 0] += value
        else:
            stiffness[index - 1, index - 1] += value
            stiffness[index, index] += value
            stiffness[index - 1, index] -= value
            stiffness[index, index - 1] -= value
    return mass, stiffness


def assemble_free_chain(
    masses_kg: Any, coupling_stiffnesses_n_per_m: Any
) -> tuple[np.ndarray, np.ndarray]:
    """Assemble an ungrounded chain with one rigid-translation mode."""

    masses = _positive_real_vector(masses_kg, name="masses_kg")
    stiffnesses = _positive_real_vector(
        coupling_stiffnesses_n_per_m, name="coupling_stiffnesses_n_per_m"
    )
    if stiffnesses.size != masses.size - 1:
        raise EigenAnalysisError("an n-mass free chain requires n-1 couplings")
    mass = np.diag(masses)
    stiffness = np.zeros((masses.size, masses.size), dtype=np.float64)
    for index, value in enumerate(stiffnesses):
        stiffness[index, index] += value
        stiffness[index + 1, index + 1] += value
        stiffness[index, index + 1] -= value
        stiffness[index + 1, index] -= value
    return mass, stiffness


def _right_multiply_inverse_cholesky(left: np.ndarray, lower: np.ndarray) -> np.ndarray:
    """Return left @ L^{-H} by solving the transposed system."""

    return np.linalg.solve(lower, left.conj().T).conj().T


def classify_modal_eigenvalues(eigenvalues: Any) -> dict[str, Any]:
    """Classify real modal eigenvalues without clipping their signs."""

    values = _as_vector(eigenvalues, name="eigenvalues", allow_complex=False).astype(float)
    scale = max(1.0, float(np.max(np.abs(values))))
    tolerance = float(128.0 * max(1, values.size) * np.finfo(np.float64).eps * scale)
    classifications: list[str] = []
    angular_frequencies: list[float | None] = []
    frequencies_hz: list[float | None] = []
    for value in values:
        if value < -tolerance:
            classifications.append("negative")
            angular_frequencies.append(None)
            frequencies_hz.append(None)
        elif value < 0.0:
            classifications.append("negative_near_roundoff_boundary")
            angular_frequencies.append(None)
            frequencies_hz.append(None)
        elif value <= tolerance:
            classifications.append("zero_or_unresolved")
            angular_frequencies.append(math.sqrt(float(value)))
            frequencies_hz.append(math.sqrt(float(value)) / (2.0 * math.pi))
        else:
            classifications.append("positive")
            angular_frequencies.append(math.sqrt(float(value)))
            frequencies_hz.append(math.sqrt(float(value)) / (2.0 * math.pi))
    return {
        "sign_tolerance_s_minus_2": tolerance,
        "classifications": classifications,
        "angular_frequencies_rad_per_s": angular_frequencies,
        "frequencies_hz": frequencies_hz,
        "negative_values_clipped": False,
    }


def generalized_symmetric_eigh(stiffness: Any, mass: Any) -> dict[str, Any]:
    """Solve K phi = lambda M phi through a Cholesky reduction."""

    stiffness_array = require_hermitian(stiffness, name="stiffness")
    mass_array = require_hermitian(mass, name="mass")
    if stiffness_array.shape != mass_array.shape:
        raise EigenAnalysisError("stiffness and mass must have the same shape")
    try:
        lower = np.linalg.cholesky(mass_array)
    except np.linalg.LinAlgError as exc:
        raise EigenAnalysisError("mass must be positive definite") from exc
    left_scaled = np.linalg.solve(lower, stiffness_array)
    transformed = _right_multiply_inverse_cholesky(left_scaled, lower)
    transformed_diagnostics = hermitian_diagnostics(transformed)
    if not transformed_diagnostics["passes_tolerance"]:
        raise EigenAnalysisError("Cholesky-reduced matrix lost Hermitian structure")
    try:
        eigenvalues, transformed_vectors = np.linalg.eigh(transformed)
    except np.linalg.LinAlgError as exc:
        raise EigenAnalysisError("reduced Hermitian eigensolver did not converge") from exc
    modes = np.linalg.solve(lower.conj().T, transformed_vectors)
    for column in range(modes.shape[1]):
        modal_mass = np.vdot(modes[:, column], mass_array @ modes[:, column])
        modal_mass_real = float(np.real(modal_mass))
        if modal_mass_real <= 0.0:
            raise EigenAnalysisError("computed mode has nonpositive modal mass")
        modes[:, column] /= math.sqrt(modal_mass_real)
    modes = canonicalize_columns(modes, normalize=False)
    modal_mass_matrix = modes.conj().T @ mass_array @ modes
    modal_stiffness_matrix = modes.conj().T @ stiffness_array @ modes
    diagonal = np.diag(eigenvalues)
    mass_defect = float(
        np.linalg.norm(modal_mass_matrix - np.eye(modes.shape[1]), ord="fro")
    )
    stiffness_scale = max(1.0, float(np.linalg.norm(diagonal, ord="fro")))
    stiffness_defect = float(
        np.linalg.norm(modal_stiffness_matrix - diagonal, ord="fro")
        / stiffness_scale
    )
    transformed_scale = float(np.linalg.norm(transformed, ord="fro"))
    transformed_reconstruction = transformed_vectors @ diagonal @ transformed_vectors.conj().T
    transformed_reconstruction_error = float(
        np.linalg.norm(transformed - transformed_reconstruction, ord="fro")
    )
    residuals = eigenpair_residuals(
        stiffness_array, eigenvalues, modes, metric=mass_array
    )
    return {
        "method": "Cholesky reduction followed by numpy.linalg.eigh",
        "matrix_order": int(stiffness_array.shape[0]),
        "eigenvalues_s_minus_2": eigenvalues,
        "modes_mass_normalized": modes,
        "mass_cholesky_factor": lower,
        "reduced_matrix": transformed,
        "stiffness_hermitian_diagnostics": hermitian_diagnostics(stiffness_array),
        "mass_hermitian_diagnostics": hermitian_diagnostics(mass_array),
        "reduced_hermitian_diagnostics": transformed_diagnostics,
        "modal_mass_matrix": modal_mass_matrix,
        "modal_stiffness_matrix": modal_stiffness_matrix,
        "mass_orthogonality_defect_frobenius": mass_defect,
        "relative_stiffness_diagonalization_defect_frobenius": stiffness_defect,
        "relative_reduced_reconstruction_error_frobenius": (
            0.0
            if transformed_scale == 0.0
            else transformed_reconstruction_error / transformed_scale
        ),
        "residuals": residuals,
        "frequency_classification": classify_modal_eigenvalues(eigenvalues),
        "explicit_inverse_formed": False,
        "silent_symmetrization_applied": False,
        "eigenvalue_clipping_applied": False,
    }


def modal_participation(
    mass: Any, modes: Any, influence_vector: Any
) -> dict[str, Any]:
    """Compute masses for nonzero M-orthogonal modes and SPD M.

    The normalized modal Gram defect (Frobenius norm) must not exceed
    64 * max(n, r) * binary64 epsilon, the existing structure-tolerance rule.
    Modes are checked, never silently orthogonalized. For zero influence the
    historical captured_fraction=0 extension is retained by convention.
    """

    mass_array, lower, mass_scale = _positive_definite_metric(mass, name="mass")
    mode_array = np.asarray(modes)
    if mode_array.ndim != 2 or mode_array.shape[0] != mass_array.shape[0]:
        raise EigenAnalysisError("modes have incompatible dimensions")
    if mode_array.dtype.kind not in "biufc" or not np.all(np.isfinite(mode_array)):
        raise EigenAnalysisError("modes must be finite and numeric")
    mode_array = np.asarray(mode_array, dtype=np.complex128 if np.iscomplexobj(mode_array) else np.float64)
    influence = _as_vector(
        influence_vector, length=mass_array.shape[0], name="influence vector"
    )
    whitened = np.empty(mode_array.shape, dtype=np.result_type(mode_array, lower))
    for column in range(mode_array.shape[1]):
        whitened[:, column] = _unit_direction(
            lower.conj().T @ _unit_direction(mode_array[:, column])
        )
    gram = whitened.conj().T @ whitened
    gram_defect = float(np.linalg.norm(gram - np.eye(mode_array.shape[1]), ord="fro"))
    tolerance = hermitian_tolerance(max(mass_array.shape[0], mode_array.shape[1]))
    if not math.isfinite(gram_defect) or gram_defect > tolerance:
        raise EigenAnalysisError("modes must be mutually M-orthogonal")
    scaled_mass, _ = _component_scaled(mass_array)
    factors: list[complex] = []
    effective_masses: list[float] = []
    for column in range(mode_array.shape[1]):
        mode, mode_scale = _component_scaled(mode_array[:, column])
        denominator = np.vdot(mode, scaled_mass @ mode)
        if not np.isfinite(denominator) or float(np.real(denominator)) <= 0.0:
            raise EigenAnalysisError("every mode must have positive modal mass")
        local_factor = np.vdot(mode, scaled_mass @ influence) / denominator
        factor = complex(local_factor / mode_scale)
        effective_mass = float(abs(local_factor) ** 2 * np.real(denominator) * mass_scale)
        if not np.isfinite(factor) or not math.isfinite(effective_mass):
            raise EigenAnalysisError("participation factor or effective mass is not representable")
        factors.append(factor)
        effective_masses.append(effective_mass)
    total_mass = float(np.real(np.vdot(influence, mass_array @ influence)))
    captured = sum(effective_masses)
    if not math.isfinite(total_mass) or not math.isfinite(captured):
        raise EigenAnalysisError("total or captured modal mass is not representable")
    if np.any(influence != 0.0) and total_mass <= 0.0:
        raise EigenAnalysisError("nonzero influence mass is not positive or representable")
    fraction = 0.0 if total_mass == 0.0 else captured / total_mass
    if not math.isfinite(fraction):
        raise EigenAnalysisError("captured mass fraction is not representable")
    return {
        "participation_factors": np.asarray(factors),
        "effective_modal_masses_kg": np.asarray(effective_masses),
        "total_influence_mass_kg": total_mass,
        "captured_effective_mass_kg": captured,
        "captured_fraction": fraction,
    }


def dynamic_stiffness_sweep(
    stiffness: Any,
    mass: Any,
    force: Any,
    frequencies_hz: Iterable[float],
) -> list[dict[str, Any]]:
    """Solve undamped harmonic equilibrium away from exact singularities."""

    stiffness_array = require_hermitian(stiffness, name="stiffness")
    mass_array = require_hermitian(mass, name="mass")
    if stiffness_array.shape != mass_array.shape:
        raise EigenAnalysisError("stiffness and mass must have the same shape")
    force_vector = _as_vector(force, length=stiffness_array.shape[0], name="force")
    records: list[dict[str, Any]] = []
    for frequency in frequencies_hz:
        value = float(frequency)
        if not math.isfinite(value) or value < 0.0:
            raise EigenAnalysisError("frequencies must be finite and nonnegative")
        angular = 2.0 * math.pi * value
        dynamic = stiffness_array - angular * angular * mass_array
        condition = float(np.linalg.cond(dynamic, p=2))
        record: dict[str, Any] = {
            "frequency_hz": value,
            "angular_frequency_rad_per_s": angular,
            "condition_number_2": condition,
            "explicit_inverse_formed": False,
        }
        try:
            response = np.linalg.solve(dynamic, force_vector)
        except np.linalg.LinAlgError:
            record.update(
                {
                    "status": "singular_ideal_resonance",
                    "response": None,
                    "response_norm_2_m": None,
                    "scaled_backward_error_2": None,
                }
            )
        else:
            residual = force_vector - dynamic @ response
            denominator = (
                float(np.linalg.norm(dynamic, ord=2))
                * float(np.linalg.norm(response, ord=2))
                + float(np.linalg.norm(force_vector, ord=2))
            )
            record.update(
                {
                    "status": "solved_undamped_model",
                    "response": response,
                    "response_norm_2_m": float(np.linalg.norm(response, ord=2)),
                    "scaled_backward_error_2": (
                        0.0
                        if denominator == 0.0
                        else float(np.linalg.norm(residual, ord=2)) / denominator
                    ),
                }
            )
        records.append(record)
    return records


def spectral_radius(matrix: Any) -> float:
    """Return the largest eigenvalue modulus of a square matrix."""

    array = _as_square_matrix(matrix)
    try:
        values = np.linalg.eigvals(array)
    except np.linalg.LinAlgError as exc:
        raise EigenAnalysisError("eigenvalue computation did not converge") from exc
    return float(np.max(np.abs(values)))


def discrete_stability_report(matrix: Any) -> dict[str, Any]:
    """Classify x_(k+1)=A x_k by eigenvalue moduli."""

    array = _as_square_matrix(matrix)
    values = np.linalg.eigvals(array)
    radius = float(np.max(np.abs(values)))
    tolerance = hermitian_tolerance(array.shape[0])
    if radius < 1.0 - tolerance:
        classification = "asymptotically_stable"
    elif radius > 1.0 + tolerance:
        classification = "unstable"
    else:
        classification = "boundary_requires_jordan_or_power_check"
    return {
        "system": "x_(k+1) = A x_k",
        "eigenvalues": values[_general_sort_indices(values)],
        "spectral_radius": radius,
        "unit_circle_tolerance": tolerance,
        "classification": classification,
        "criterion": "all eigenvalue moduli strictly below one for asymptotic stability",
    }


def continuous_stability_report(matrix: Any) -> dict[str, Any]:
    """Classify x'(t)=A x(t) by eigenvalue real parts."""

    array = _as_square_matrix(matrix)
    values = np.linalg.eigvals(array)
    maximum_real = float(np.max(np.real(values)))
    scale = max(1.0, float(np.max(np.abs(values))))
    tolerance = hermitian_tolerance(array.shape[0]) * scale
    if maximum_real < -tolerance:
        classification = "asymptotically_stable"
    elif maximum_real > tolerance:
        classification = "unstable"
    else:
        classification = "boundary_requires_jordan_or_semisimplicity_check"
    return {
        "system": "x'(t) = A x(t)",
        "eigenvalues": values[_general_sort_indices(values)],
        "maximum_real_part_per_s": maximum_real,
        "imaginary_axis_tolerance_per_s": tolerance,
        "classification": classification,
        "criterion": "all eigenvalue real parts strictly negative for asymptotic stability",
    }


def transient_growth_report(
    matrix: Any,
    initial_vector: Any,
    *,
    steps: int = 20,
) -> dict[str, Any]:
    """Track trajectory and operator-norm growth for a discrete system."""

    array = _as_square_matrix(matrix)
    state = _as_vector(initial_vector, length=array.shape[0]).astype(np.complex128)
    if not isinstance(steps, (int, np.integer)) or steps < 0:
        raise EigenAnalysisError("steps must be a nonnegative integer")
    initial_norm = float(np.linalg.norm(state, ord=2))
    if initial_norm == 0.0:
        raise EigenAnalysisError("initial_vector must be nonzero")
    power = np.eye(array.shape[0], dtype=np.complex128)
    trajectory_norms: list[float] = []
    operator_norms: list[float] = []
    for _ in range(int(steps) + 1):
        trajectory_norms.append(float(np.linalg.norm(power @ state, ord=2)))
        operator_norms.append(float(np.linalg.norm(power, ord=2)))
        power = array @ power
    maximum_trajectory = max(trajectory_norms)
    maximum_operator = max(operator_norms)
    return {
        "steps": int(steps),
        "spectral_radius": spectral_radius(array),
        "trajectory_norms_2": np.asarray(trajectory_norms),
        "operator_norms_2": np.asarray(operator_norms),
        "maximum_trajectory_amplification": maximum_trajectory / initial_norm,
        "maximum_operator_amplification": maximum_operator,
        "peak_trajectory_step": int(np.argmax(trajectory_norms)),
        "peak_operator_step": int(np.argmax(operator_norms)),
    }


def three_platform_modal_case() -> dict[str, Any]:
    """Run the frozen fixed-base three-platform modal analysis."""

    masses = np.asarray([2000.0, 1500.0, 1000.0])
    stiffnesses = np.asarray([8.0e6, 6.0e6, 4.0e6])
    mass, stiffness = assemble_shear_building(masses, stiffnesses)
    analysis = generalized_symmetric_eigh(stiffness, mass)
    modes = analysis["modes_mass_normalized"]
    participation = modal_participation(mass, modes, np.ones(3))
    frequencies = analysis["frequency_classification"]["frequencies_hz"]
    first_frequency = float(frequencies[0])
    sweep_frequencies = [0.0, 0.8 * first_frequency, 0.98 * first_frequency, 1.02 * first_frequency, 1.2 * first_frequency]
    sweep = dynamic_stiffness_sweep(
        stiffness, mass, np.asarray([1000.0, 0.0, 0.0]), sweep_frequencies
    )
    return {
        "case": "synthetic three-platform fixed-base test rig",
        "masses_kg": masses,
        "story_stiffnesses_n_per_m": stiffnesses,
        "mass_matrix_kg": mass,
        "stiffness_matrix_n_per_m": stiffness,
        "assumptions": [
            "small horizontal displacements",
            "linear elastic story springs",
            "lumped platform masses",
            "fixed base",
            "undamped free vibration for modal extraction",
            "constant time-invariant parameters",
        ],
        "analysis": analysis,
        "participation": participation,
        "undamped_frequency_sweep": sweep,
        "safety_scope": "educational synthetic model, not a design certification",
    }


def rigid_body_mode_case() -> dict[str, Any]:
    """Run an ungrounded chain whose uniform translation has zero energy."""

    mass, stiffness = assemble_free_chain(
        [2000.0, 1500.0, 1000.0], [6.0e6, 4.0e6]
    )
    analysis = generalized_symmetric_eigh(stiffness, mass)
    rigid_vector = np.ones(3)
    return {
        "case": "free chain with rigid translation",
        "mass_matrix_kg": mass,
        "stiffness_matrix_n_per_m": stiffness,
        "predicted_null_vector": rigid_vector,
        "null_residual_n_per_m": float(np.linalg.norm(stiffness @ rigid_vector, ord=2)),
        "analysis": analysis,
    }


def negative_tangent_stiffness_case() -> dict[str, Any]:
    """Run a deliberately indefinite tangent-stiffness boundary case."""

    mass, stiffness = assemble_shear_building(
        [2000.0, 1500.0, 1000.0], [8.0e6, 6.0e6, 4.0e6]
    )
    altered = stiffness.copy()
    altered[0, 0] -= 20.0e6
    analysis = generalized_symmetric_eigh(altered, mass)
    return {
        "case": "synthetic negative tangent stiffness",
        "mass_matrix_kg": mass,
        "stiffness_matrix_n_per_m": altered,
        "analysis": analysis,
        "interpretation": "negative generalized eigenvalue is not converted to a frequency",
    }


def repeated_eigenspace_case() -> dict[str, Any]:
    """Show that a repeated eigenspace is fixed while its basis is not."""

    matrix = np.diag([2.0, 2.0, 5.0])
    first_basis = np.asarray([[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]])
    angle = math.pi / 7.0
    rotation = np.asarray(
        [[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]]
    )
    second_basis = first_basis @ rotation
    return {
        "matrix": matrix,
        "eigenvalue": 2.0,
        "first_basis": first_basis,
        "second_basis": second_basis,
        "columnwise_mac": np.asarray(
            [
                modal_assurance_criterion(first_basis[:, index], second_basis[:, index])
                for index in range(2)
            ]
        ),
        "projector_distance_2": subspace_distance(first_basis, second_basis),
        "interpretation": "basis vectors differ, invariant eigenspace agrees",
    }


def defective_matrix_case() -> dict[str, Any]:
    """Return a 2x2 Jordan-block example with one eigenvector direction."""

    matrix = np.asarray([[1.0, 1.0], [0.0, 1.0]])
    analysis = general_eigendecomposition(matrix)
    null_rank = int(np.linalg.matrix_rank(matrix - np.eye(2)))
    geometric_multiplicity = 2 - null_rank
    return {
        "matrix": matrix,
        "analysis": analysis,
        "algebraic_multiplicity_of_one": 2,
        "geometric_multiplicity_of_one": geometric_multiplicity,
    }


def stability_cases() -> dict[str, Any]:
    """Return deterministic discrete, continuous, and nonnormal examples."""

    discrete_stable = np.asarray([[0.8, 0.0], [0.0, 0.6]])
    discrete_unstable = np.asarray([[1.05, 0.0], [0.0, 0.8]])
    continuous_stable = np.asarray([[-0.4, -2.0], [2.0, -0.4]])
    continuous_unstable = np.asarray([[0.1, -2.0], [2.0, 0.1]])
    nonnormal = np.asarray([[0.8, 4.0], [0.0, 0.7]])
    transient = transient_growth_report(nonnormal, [0.0, 1.0], steps=30)
    return {
        "discrete_stable": discrete_stability_report(discrete_stable),
        "discrete_unstable": discrete_stability_report(discrete_unstable),
        "continuous_stable": continuous_stability_report(continuous_stable),
        "continuous_unstable": continuous_stability_report(continuous_unstable),
        "nonnormal_matrix": nonnormal,
        "nonnormal_discrete_classification": discrete_stability_report(nonnormal),
        "nonnormal_transient_growth": transient,
    }


def algorithm_demonstrations() -> dict[str, Any]:
    """Return deterministic small educational iteration examples."""

    matrix = np.asarray([[4.0, 1.0], [1.0, 2.0]])
    return {
        "matrix": matrix,
        "reference": symmetric_eigendecomposition(matrix),
        "power_iteration": power_iteration(
            matrix, [1.0, 1.0], max_iterations=80, tolerance=1.0e-13
        ),
        "inverse_iteration": inverse_iteration(
            matrix, 1.0, [1.0, -1.0], max_iterations=40, tolerance=1.0e-13
        ),
    }


def software_record() -> dict[str, Any]:
    """Return the local scientific software identity used for the report."""

    return {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "platform": platform.platform(),
        "module": "applications/python/" + Path(__file__).name,
        "floating_dtype": "binary64/complex128",
        "randomness_used": False,
    }


def run_all_cases() -> dict[str, Any]:
    """Run the complete deterministic Chapter 12 result passport."""

    rotation = np.asarray([[0.0, -1.0], [1.0, 0.0]])
    return {
        "schema_version": "1.0",
        "chapter": 12,
        "title": "Özdeğerler, Modlar ve Kararlılık",
        "software": software_record(),
        "method_contract": {
            "symmetric_solver": "numpy.linalg.eigh after explicit structure validation",
            "general_solver": "numpy.linalg.eig",
            "generalized_solver": "Cholesky reduction and numpy.linalg.eigh",
            "explicit_inverse_formed": False,
            "silent_symmetrization_applied": False,
            "eigenvalue_clipping_applied": False,
            "randomness_used": False,
        },
        "three_platform_case": three_platform_modal_case(),
        "rigid_body_case": rigid_body_mode_case(),
        "negative_stiffness_case": negative_tangent_stiffness_case(),
        "repeated_eigenspace_case": repeated_eigenspace_case(),
        "defective_matrix_case": defective_matrix_case(),
        "complex_pair_case": general_eigendecomposition(rotation),
        "algorithm_demonstrations": algorithm_demonstrations(),
        "stability_cases": stability_cases(),
    }


def _jsonable(value: Any) -> Any:
    """Convert NumPy and complex objects to strict JSON-compatible values."""

    if isinstance(value, np.ndarray):
        return _jsonable(value.tolist())
    if isinstance(value, np.generic):
        return _jsonable(value.item())
    if isinstance(value, complex):
        if value.imag == 0.0:
            return float(value.real)
        return {"real": float(value.real), "imag": float(value.imag)}
    if isinstance(value, float):
        if not math.isfinite(value):
            if math.isnan(value):
                return "nan"
            return "infinity" if value > 0 else "-infinity"
        return value
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _human_summary(report: dict[str, Any]) -> str:
    """Return a concise human-readable summary of the result passport."""

    modal = report["three_platform_case"]["analysis"]
    frequencies = modal["frequency_classification"]["frequencies_hz"]
    rigid = report["rigid_body_case"]["analysis"]["eigenvalues_s_minus_2"]
    negative = report["negative_stiffness_case"]["analysis"]["eigenvalues_s_minus_2"]
    transient = report["stability_cases"]["nonnormal_transient_growth"]
    lines = [
        "Bölüm 12: Özdeğerler, Modlar ve Kararlılık",
        "Yöntem: Cholesky indirgemesi + numpy.linalg.eigh",
        "Doğal frekanslar (Hz): " + ", ".join(f"{float(item):.6f}" for item in frequencies),
        f"En büyük ölçeklendirilmiş modal artık: {modal['residuals']['maximum_scaled_residual_2']:.3e}",
        f"M-ortogonallik kusuru: {modal['mass_orthogonality_defect_frobenius']:.3e}",
        f"Serbest zincirin en küçük özdeğeri (s^-2): {float(rigid[0]):.3e}",
        f"Negatif teğet rijitlik en küçük özdeğeri (s^-2): {float(negative[0]):.3e}",
        f"Normal olmayan geçici büyüme: {transient['maximum_trajectory_amplification']:.3f}",
        "Açık ters: hayır | sessiz simetrikleştirme: hayır | özdeğer kırpma: hayır",
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line interface."""

    parser = argparse.ArgumentParser(
        description="Deterministic Chapter 12 eigenvalue and modal laboratory"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit the complete strict JSON result passport",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line interface and return a process status."""

    arguments = build_parser().parse_args(argv)
    report = run_all_cases()
    if arguments.json:
        print(json.dumps(_jsonable(report), ensure_ascii=False, indent=2, allow_nan=False))
    else:
        print(_human_summary(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
