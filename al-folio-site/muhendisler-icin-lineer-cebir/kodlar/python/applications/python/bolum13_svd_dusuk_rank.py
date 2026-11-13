#!/usr/bin/env python3
"""Chapter 13 deterministic SVD, low-rank, pseudoinverse, and PCA laboratory.

The module uses only NumPy and the Python standard library. It never forms an
explicit matrix inverse, never centers or scales data silently, never chooses
an application rank without recording a threshold, and uses deterministic
synthetic engineering cases with no external data or randomness.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
from typing import Any, Sequence

import numpy as np


class SVDAnalysisError(ValueError):
    """Raised when an SVD or data-analysis contract is not satisfied."""


def _as_matrix(value: Any, *, name: str = "matrix") -> np.ndarray:
    """Return a finite, numeric, nonempty two-dimensional array."""

    try:
        array = np.asarray(value)
    except (TypeError, ValueError) as exc:
        raise SVDAnalysisError(f"{name} must be a numeric matrix") from exc
    if array.ndim != 2:
        raise SVDAnalysisError(f"{name} must be two-dimensional")
    if array.shape[0] == 0 or array.shape[1] == 0:
        raise SVDAnalysisError(f"{name} must not be empty")
    if array.dtype.kind not in "biufc":
        raise SVDAnalysisError(f"{name} must be numeric")
    dtype = np.complex128 if np.iscomplexobj(array) else np.float64
    result = np.asarray(array, dtype=dtype)
    if not np.all(np.isfinite(result)):
        raise SVDAnalysisError(f"{name} must contain only finite values")
    return result


def _as_vector(
    value: Any,
    *,
    length: int | None = None,
    name: str = "vector",
) -> np.ndarray:
    """Return a finite numeric vector, optionally with a required length."""

    try:
        array = np.asarray(value)
    except (TypeError, ValueError) as exc:
        raise SVDAnalysisError(f"{name} must be a numeric vector") from exc
    if array.ndim != 1:
        raise SVDAnalysisError(f"{name} must be one-dimensional")
    if array.size == 0:
        raise SVDAnalysisError(f"{name} must not be empty")
    if length is not None and array.size != length:
        raise SVDAnalysisError(f"{name} length must be {length}")
    if array.dtype.kind not in "biufc":
        raise SVDAnalysisError(f"{name} must be numeric")
    dtype = np.complex128 if np.iscomplexobj(array) else np.float64
    result = np.asarray(array, dtype=dtype)
    if not np.all(np.isfinite(result)):
        raise SVDAnalysisError(f"{name} must contain only finite values")
    return result


def _nonnegative_real(value: Any, *, name: str) -> float:
    """Return a finite nonnegative real scalar."""

    if isinstance(value, (bool, np.bool_)):
        raise SVDAnalysisError(f"{name} must be a real scalar")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise SVDAnalysisError(f"{name} must be a real scalar") from exc
    if not math.isfinite(result) or result < 0.0:
        raise SVDAnalysisError(f"{name} must be finite and nonnegative")
    return result


def _rank_index(value: Any, *, maximum: int) -> int:
    """Validate a requested truncation rank in the closed interval [0, maximum]."""

    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
        raise SVDAnalysisError("rank must be an integer")
    result = int(value)
    if result < 0 or result > maximum:
        raise SVDAnalysisError(f"rank must satisfy 0 <= rank <= {maximum}")
    return result


def canonicalize_singular_vectors(
    left_vectors: Any,
    right_adjoint: Any,
) -> tuple[np.ndarray, np.ndarray]:
    """Choose paired display phases without changing U @ Sigma @ Vh."""

    left = _as_matrix(left_vectors, name="left singular vectors").copy()
    right_h = _as_matrix(right_adjoint, name="right singular vectors").copy()
    if left.shape[1] != right_h.shape[0]:
        raise SVDAnalysisError("paired singular-vector dimensions are incompatible")
    for index in range(left.shape[1]):
        column = left[:, index]
        pivot = int(np.argmax(np.abs(column)))
        pivot_value = column[pivot]
        if abs(pivot_value) == 0.0:
            row = right_h[index, :]
            pivot = int(np.argmax(np.abs(row)))
            pivot_value = np.conj(row[pivot])
        if abs(pivot_value) == 0.0:
            continue
        phase = pivot_value / abs(pivot_value)
        left[:, index] /= phase
        right_h[index, :] *= phase
        if not np.iscomplexobj(left_vectors) and not np.iscomplexobj(right_adjoint):
            left[:, index] = np.real(left[:, index])
            right_h[index, :] = np.real(right_h[index, :])
    return left, right_h


def rank_threshold(
    singular_values: Any,
    shape: tuple[int, int],
    *,
    relative_tolerance: float | None = None,
    absolute_tolerance: float = 0.0,
) -> dict[str, Any]:
    """Compute and record a numerical-rank threshold."""

    values = _as_vector(singular_values, name="singular values")
    if np.iscomplexobj(values) and np.any(np.imag(values) != 0.0):
        raise SVDAnalysisError("singular values must be real")
    values = np.asarray(np.real(values), dtype=np.float64)
    if np.any(values < 0.0):
        raise SVDAnalysisError("singular values must be nonnegative")
    if (
        not isinstance(shape, tuple)
        or len(shape) != 2
        or any(isinstance(item, bool) or not isinstance(item, int) for item in shape)
        or min(shape) <= 0
    ):
        raise SVDAnalysisError("shape must contain two positive integers")
    absolute = _nonnegative_real(absolute_tolerance, name="absolute tolerance")
    maximum = float(np.max(values)) if values.size else 0.0
    if relative_tolerance is None:
        relative = float(max(shape) * np.finfo(np.float64).eps)
        origin = "binary64_roundoff_default"
    else:
        relative = _nonnegative_real(
            relative_tolerance, name="relative tolerance"
        )
        origin = "user_supplied"
    threshold = max(absolute, relative * maximum)
    rank = int(np.count_nonzero(values > threshold))
    return {
        "relative_tolerance": relative,
        "absolute_tolerance": absolute,
        "threshold": threshold,
        "threshold_origin": origin,
        "rank": rank,
        "singular_value_count": int(values.size),
    }


def svd_diagnostics(
    matrix: Any,
    left_vectors: Any,
    singular_values: Any,
    right_adjoint: Any,
) -> dict[str, Any]:
    """Measure reconstruction, orthogonality, and two-sided triplet residuals."""

    array = _as_matrix(matrix)
    left = _as_matrix(left_vectors, name="left singular vectors")
    values = _as_vector(singular_values, name="singular values")
    right_h = _as_matrix(right_adjoint, name="right singular vectors")
    if np.iscomplexobj(values) and np.any(np.imag(values) != 0.0):
        raise SVDAnalysisError("singular values must be real")
    values = np.asarray(np.real(values), dtype=np.float64)
    k = values.size
    if left.shape != (array.shape[0], k):
        raise SVDAnalysisError("left singular-vector matrix has incompatible shape")
    if right_h.shape != (k, array.shape[1]):
        raise SVDAnalysisError("right singular-vector matrix has incompatible shape")
    reconstruction = (left * values) @ right_h
    residual = array - reconstruction
    absolute_fro = float(np.linalg.norm(residual, ord="fro"))
    scale_fro = float(np.linalg.norm(array, ord="fro"))
    left_defect = left.conj().T @ left - np.eye(k)
    right_defect = right_h @ right_h.conj().T - np.eye(k)
    norm_2 = float(np.linalg.norm(array, ord=2))
    forward_residuals: list[float] = []
    adjoint_residuals: list[float] = []
    scaled_forward: list[float] = []
    scaled_adjoint: list[float] = []
    for index, singular_value in enumerate(values):
        u = left[:, index]
        v = right_h[index, :].conj().T
        forward = array @ v - singular_value * u
        adjoint = array.conj().T @ u - singular_value * v
        forward_norm = float(np.linalg.norm(forward, ord=2))
        adjoint_norm = float(np.linalg.norm(adjoint, ord=2))
        forward_scale = (norm_2 + singular_value) * float(np.linalg.norm(v, 2))
        adjoint_scale = (norm_2 + singular_value) * float(np.linalg.norm(u, 2))
        forward_residuals.append(forward_norm)
        adjoint_residuals.append(adjoint_norm)
        scaled_forward.append(0.0 if forward_scale == 0.0 else forward_norm / forward_scale)
        scaled_adjoint.append(0.0 if adjoint_scale == 0.0 else adjoint_norm / adjoint_scale)
    return {
        "absolute_reconstruction_error_frobenius": absolute_fro,
        "relative_reconstruction_error_frobenius": (
            0.0 if scale_fro == 0.0 else absolute_fro / scale_fro
        ),
        "left_orthogonality_defect_frobenius": float(
            np.linalg.norm(left_defect, ord="fro")
        ),
        "right_orthogonality_defect_frobenius": float(
            np.linalg.norm(right_defect, ord="fro")
        ),
        "forward_triplet_residuals_2": forward_residuals,
        "adjoint_triplet_residuals_2": adjoint_residuals,
        "maximum_scaled_forward_residual_2": max(scaled_forward, default=0.0),
        "maximum_scaled_adjoint_residual_2": max(scaled_adjoint, default=0.0),
    }


def compute_svd(
    matrix: Any,
    *,
    full_matrices: bool = False,
    canonicalize_for_display: bool = True,
) -> dict[str, Any]:
    """Compute a full or thin library SVD and its validation passport."""

    array = _as_matrix(matrix)
    if not isinstance(full_matrices, (bool, np.bool_)):
        raise SVDAnalysisError("full_matrices must be boolean")
    if not isinstance(canonicalize_for_display, (bool, np.bool_)):
        raise SVDAnalysisError("canonicalize_for_display must be boolean")
    try:
        left, values, right_h = np.linalg.svd(
            array, full_matrices=bool(full_matrices), compute_uv=True
        )
    except np.linalg.LinAlgError as exc:
        raise SVDAnalysisError("SVD did not converge") from exc
    active = min(array.shape)
    diagnostic_left = left[:, :active]
    diagnostic_right_h = right_h[:active, :]
    if canonicalize_for_display:
        paired_left, paired_right_h = canonicalize_singular_vectors(
            diagnostic_left, diagnostic_right_h
        )
        left = left.copy()
        right_h = right_h.copy()
        left[:, :active] = paired_left
        right_h[:active, :] = paired_right_h
        diagnostic_left = paired_left
        diagnostic_right_h = paired_right_h
    diagnostics = svd_diagnostics(
        array, diagnostic_left, values, diagnostic_right_h
    )
    return {
        "input_shape": list(array.shape),
        "full_matrices": bool(full_matrices),
        "factor_shapes": {
            "U": list(left.shape),
            "s": list(values.shape),
            "Vh": list(right_h.shape),
        },
        "U": left,
        "singular_values": values,
        "Vh": right_h,
        "diagnostics": diagnostics,
        "canonicalized_for_display": bool(canonicalize_for_display),
        "explicit_inverse_formed": False,
        "normal_matrix_formed": False,
        "algorithm_interface": "numpy.linalg.svd",
    }


def _as_projector_basis(basis: Any, *, name: str = "basis") -> np.ndarray:
    """Validate a basis locally, allowing zero columns in a nonempty ambient space."""

    array = np.asarray(basis)
    if array.ndim != 2 or array.shape[0] == 0:
        raise SVDAnalysisError(f"{name} must have a positive ambient dimension")
    if array.dtype.kind not in "biufc" or not np.all(np.isfinite(array)):
        raise SVDAnalysisError(f"{name} must be finite and numeric")
    if array.shape[1] > array.shape[0]:
        raise SVDAnalysisError("a basis cannot have more columns than ambient dimensions")
    return np.asarray(array, dtype=np.complex128 if np.iscomplexobj(array) else np.float64)


def orthogonal_projector(basis: Any) -> np.ndarray:
    """Return Q Q^H for an independent basis; an empty basis gives zero.

    Numerical independence uses max(n, k) * eps * sigma_max after safe
    common-component scaling. This gate has no absolute unit-size floor.
    """

    array = _as_projector_basis(basis)
    if array.shape[1] == 0:
        return np.zeros((array.shape[0], array.shape[0]), dtype=array.dtype)
    scale = float(max(np.max(np.abs(array.real)), np.max(np.abs(array.imag))))
    if scale == 0.0:
        raise SVDAnalysisError("basis columns must be linearly independent")
    scaled = array.real / scale
    if np.iscomplexobj(array):
        scaled = scaled + 1j * (array.imag / scale)
    singular_values = np.linalg.svd(scaled, compute_uv=False)
    tolerance = max(array.shape) * np.finfo(np.float64).eps * singular_values[0]
    if np.count_nonzero(singular_values > tolerance) != array.shape[1]:
        raise SVDAnalysisError("basis columns must be linearly independent")
    q, _ = np.linalg.qr(scaled, mode="reduced")
    return q @ q.conj().T


def subspace_projector_distance(first_basis: Any, second_basis: Any) -> float:
    """Compare equally sized ambient subspaces by projector 2-norm."""

    first = _as_projector_basis(first_basis, name="first basis")
    second = _as_projector_basis(second_basis, name="second basis")
    if first.shape[0] != second.shape[0]:
        raise SVDAnalysisError("basis matrices must share an ambient dimension")
    return float(
        np.linalg.norm(
            orthogonal_projector(first) - orthogonal_projector(second), ord=2
        )
    )


def fundamental_subspaces(
    matrix: Any,
    *,
    relative_tolerance: float | None = None,
    absolute_tolerance: float = 0.0,
) -> dict[str, Any]:
    """Return SVD bases for all four fundamental subspaces."""

    array = _as_matrix(matrix)
    left, values, right_h = np.linalg.svd(array, full_matrices=True)
    decision = rank_threshold(
        values,
        array.shape,
        relative_tolerance=relative_tolerance,
        absolute_tolerance=absolute_tolerance,
    )
    rank = decision["rank"]
    right = right_h.conj().T
    return {
        "rank_decision": decision,
        "column_space_basis": left[:, :rank],
        "left_null_space_basis": left[:, rank:],
        "row_space_basis": right[:, :rank],
        "null_space_basis": right[:, rank:],
        "dimensions": {
            "column_space": rank,
            "left_null_space": int(array.shape[0] - rank),
            "row_space": rank,
            "null_space": int(array.shape[1] - rank),
        },
    }


def low_rank_approximation(matrix: Any, rank: int) -> dict[str, Any]:
    """Return the truncated SVD and measured/theoretical norm errors."""

    array = _as_matrix(matrix)
    maximum = min(array.shape)
    selected = _rank_index(rank, maximum=maximum)
    left, values, right_h = np.linalg.svd(array, full_matrices=False)
    approximation = (left[:, :selected] * values[:selected]) @ right_h[:selected, :]
    residual = array - approximation
    spectral_error = float(np.linalg.norm(residual, ord=2))
    frobenius_error = float(np.linalg.norm(residual, ord="fro"))
    theoretical_spectral = 0.0 if selected == maximum else float(values[selected])
    theoretical_frobenius = float(np.linalg.norm(values[selected:], ord=2))
    original_entries = int(array.size)
    stored_entries = int(selected * (array.shape[0] + array.shape[1] + 1))
    total_square = float(np.dot(values, values))
    captured_square = float(np.dot(values[:selected], values[:selected]))
    return {
        "rank": selected,
        "approximation": approximation,
        "singular_values": values,
        "spectral_error": spectral_error,
        "theoretical_spectral_error": theoretical_spectral,
        "frobenius_error": frobenius_error,
        "theoretical_frobenius_error": theoretical_frobenius,
        "relative_frobenius_error": (
            0.0
            if np.linalg.norm(array, ord="fro") == 0.0
            else frobenius_error / float(np.linalg.norm(array, ord="fro"))
        ),
        "captured_squared_singular_value_fraction": (
            1.0 if total_square == 0.0 else captured_square / total_square
        ),
        "storage": {
            "original_scalar_count": original_entries,
            "factor_scalar_count": stored_entries,
            "factor_to_original_ratio": stored_entries / original_entries,
            "is_storage_saving": bool(stored_entries < original_entries),
        },
        "optimality_scope": "best_rank_k_in_matrix_2_and_frobenius_norms",
    }


def pseudoinverse_svd(
    matrix: Any,
    *,
    relative_tolerance: float | None = None,
    absolute_tolerance: float = 0.0,
) -> dict[str, Any]:
    """Compute a thresholded pseudoinverse with original/retained diagnostics.

    The legacy moore_penrose_relative_defects field still refers to the
    original input A. The retained block refers to A_tau, whose inverse is
    computed after thresholding. A truncation discrepancy is not roundoff.
    """

    array = _as_matrix(matrix)
    left, values, right_h = np.linalg.svd(array, full_matrices=False)
    decision = rank_threshold(
        values,
        array.shape,
        relative_tolerance=relative_tolerance,
        absolute_tolerance=absolute_tolerance,
    )
    retained = values > decision["threshold"]
    reciprocal = np.zeros_like(values)
    reciprocal[retained] = 1.0 / values[retained]
    pseudo = (right_h.conj().T * reciprocal) @ left.conj().T
    apa = array @ pseudo @ array
    pap = pseudo @ array @ pseudo
    aa_plus = array @ pseudo
    a_plus_a = pseudo @ array
    scale_a = max(1.0, float(np.linalg.norm(array, ord="fro")))
    scale_p = max(1.0, float(np.linalg.norm(pseudo, ord="fro")))
    defects = {
        "A_Aplus_A_equals_A": float(np.linalg.norm(apa - array, ord="fro") / scale_a),
        "Aplus_A_Aplus_equals_Aplus": float(
            np.linalg.norm(pap - pseudo, ord="fro") / scale_p
        ),
        "A_Aplus_is_hermitian": float(
            np.linalg.norm(aa_plus - aa_plus.conj().T, ord="fro")
        ),
        "Aplus_A_is_hermitian": float(
            np.linalg.norm(a_plus_a - a_plus_a.conj().T, ord="fro")
        ),
    }
    retained_operator = (left * np.where(retained, values, 0.0)) @ right_h
    retained_apa = retained_operator @ pseudo @ retained_operator
    retained_pap = pseudo @ retained_operator @ pseudo
    retained_aa_plus = retained_operator @ pseudo
    retained_a_plus_a = pseudo @ retained_operator
    retained_scale = max(1.0, float(np.linalg.norm(retained_operator, ord="fro")))
    retained_defects = {
        "A_Aplus_A_equals_A": float(
            np.linalg.norm(retained_apa - retained_operator, ord="fro") / retained_scale
        ),
        "Aplus_A_Aplus_equals_Aplus": float(
            np.linalg.norm(retained_pap - pseudo, ord="fro") / scale_p
        ),
        "A_Aplus_is_hermitian": float(
            np.linalg.norm(retained_aa_plus - retained_aa_plus.conj().T, ord="fro")
        ),
        "Aplus_A_is_hermitian": float(
            np.linalg.norm(retained_a_plus_a - retained_a_plus_a.conj().T, ord="fro")
        ),
    }
    discarded_values = values[~retained]
    truncation_frobenius = math.hypot(*discarded_values)
    original_frobenius = math.hypot(*values)
    retained_values = values[retained]
    effective_condition = (
        math.inf
        if retained_values.size == 0 or retained_values[-1] == 0.0
        else float(retained_values[0] / retained_values[-1])
    )
    return {
        "pseudoinverse": pseudo,
        "singular_values": values,
        "rank_decision": decision,
        "retained_mask": retained,
        "effective_condition_number_2": effective_condition,
        "moore_penrose_relative_defects": defects,
        "moore_penrose_diagnostics": {
            "original": {
                "operator": "original_matrix",
                "relative_defects": defects.copy(),
            },
            "retained": {
                "operator": "retained_svd_operator",
                "relative_defects": retained_defects,
            },
        },
        "truncation_norms": {
            "frobenius": truncation_frobenius,
            "spectral": float(np.max(discarded_values)) if discarded_values.size else 0.0,
            "relative_frobenius": (
                None if original_frobenius == 0.0
                else truncation_frobenius / original_frobenius
            ),
        },
        "explicit_inverse_formed": False,
        "threshold_was_recorded": True,
    }


def minimum_norm_least_squares(
    matrix: Any,
    right_hand_side: Any,
    *,
    relative_tolerance: float | None = None,
    absolute_tolerance: float = 0.0,
) -> dict[str, Any]:
    """Solve least squares in the retained SVD subspace with minimum norm."""

    array = _as_matrix(matrix)
    vector = _as_vector(
        right_hand_side, length=array.shape[0], name="right-hand side"
    )
    left, values, right_h = np.linalg.svd(array, full_matrices=False)
    decision = rank_threshold(
        values,
        array.shape,
        relative_tolerance=relative_tolerance,
        absolute_tolerance=absolute_tolerance,
    )
    retained = values > decision["threshold"]
    coefficients = left[:, retained].conj().T @ vector
    solution = right_h[retained, :].conj().T @ (coefficients / values[retained])
    residual = vector - array @ solution
    normal_residual = array.conj().T @ residual
    spaces = fundamental_subspaces(
        array,
        relative_tolerance=decision["relative_tolerance"],
        absolute_tolerance=decision["absolute_tolerance"],
    )
    null_basis = spaces["null_space_basis"]
    null_component = (
        np.zeros(0, dtype=solution.dtype)
        if null_basis.shape[1] == 0
        else null_basis.conj().T @ solution
    )
    return {
        "solution": solution,
        "residual": residual,
        "residual_norm_2": float(np.linalg.norm(residual, ord=2)),
        "normal_residual_norm_2": float(np.linalg.norm(normal_residual, ord=2)),
        "solution_norm_2": float(np.linalg.norm(solution, ord=2)),
        "null_space_component_norm_2": float(np.linalg.norm(null_component, ord=2)),
        "rank_decision": decision,
        "explicit_inverse_formed": False,
    }


def center_columns(data: Any) -> dict[str, Any]:
    """Center columns and record the removed mean vector."""

    array = _as_matrix(data, name="data")
    if np.iscomplexobj(array):
        raise SVDAnalysisError("data must be real for this PCA laboratory")
    mean = np.mean(array, axis=0)
    centered = array - mean
    return {
        "transformed": centered,
        "means": mean,
        "scales": np.ones(array.shape[1]),
        "centered": True,
        "scaled": False,
    }


def prepare_pca_data(
    data: Any,
    *,
    center: bool,
    scale: bool,
) -> dict[str, Any]:
    """Apply only the explicitly requested PCA preprocessing operations."""

    array = _as_matrix(data, name="data")
    if np.iscomplexobj(array):
        raise SVDAnalysisError("data must be real for this PCA laboratory")
    if array.shape[0] < 2:
        raise SVDAnalysisError("PCA requires at least two observations")
    if not isinstance(center, (bool, np.bool_)) or not isinstance(
        scale, (bool, np.bool_)
    ):
        raise SVDAnalysisError("center and scale choices must be boolean")
    means = np.mean(array, axis=0) if center else np.zeros(array.shape[1])
    transformed = array - means
    if scale:
        scales = np.std(transformed, axis=0, ddof=1)
        if np.any(scales == 0.0):
            raise SVDAnalysisError("cannot scale a zero-variance feature")
        transformed = transformed / scales
    else:
        scales = np.ones(array.shape[1])
    return {
        "transformed": transformed,
        "means": means,
        "scales": scales,
        "centered": bool(center),
        "scaled": bool(scale),
    }


def pca_svd(
    data: Any,
    *,
    center: bool,
    scale: bool,
    component_count: int | None = None,
) -> dict[str, Any]:
    """Compute centered PCA or explicitly uncentered SVD, without silent centering.

    Variance/covariance fields apply only when ``center=True``; otherwise
    they are None. Energy fields remain available for both choices.
    """

    array = _as_matrix(data, name="data")
    prepared = prepare_pca_data(array, center=center, scale=scale)
    transformed = prepared["transformed"]
    left, values, right_h = np.linalg.svd(transformed, full_matrices=False)
    maximum = min(transformed.shape)
    selected = maximum if component_count is None else _rank_index(
        component_count, maximum=maximum
    )
    scores = left[:, :selected] * values[:selected]
    loadings = right_h[:selected, :].T
    reconstructed_transformed = scores @ loadings.T
    restored = reconstructed_transformed * prepared["scales"] + prepared["means"]
    variances = values**2 / (array.shape[0] - 1)
    total_variance = float(np.sum(variances))
    ratios = (
        np.zeros_like(variances)
        if total_variance == 0.0
        else variances / total_variance
    )
    energies = values**2
    second_moment = transformed.T @ transformed / array.shape[0]
    reconstructed_second_moment = right_h.T @ np.diag(
        energies / array.shape[0]
    ) @ right_h
    covariance_defect = None
    if prepared["centered"]:
        covariance_defect = float(np.linalg.norm(
            np.atleast_2d(np.cov(transformed, rowvar=False, ddof=1))
            - right_h.T @ np.diag(variances) @ right_h,
            ord="fro",
        ))
    return {
        "observation_count": int(array.shape[0]),
        "feature_count": int(array.shape[1]),
        "component_count": selected,
        "preprocessing": {
            "centered": prepared["centered"],
            "scaled": prepared["scaled"],
            "means": prepared["means"],
            "scales": prepared["scales"],
            "silent_transformation_applied": False,
        },
        "singular_values": values,
        "scores": scores,
        "loadings": loadings,
        "analysis_kind": "centered_PCA" if prepared["centered"] else "uncentered_SVD",
        "variance_fields_applicable": prepared["centered"],
        "explained_variances": variances if prepared["centered"] else None,
        "explained_variance_ratios": ratios if prepared["centered"] else None,
        "cumulative_explained_variance_ratios": np.cumsum(ratios) if prepared["centered"] else None,
        "singular_value_energies": energies,
        "energy_ratios": ratios,
        "cumulative_energy_ratios": np.cumsum(ratios),
        "second_moment_eigenvalues": energies / array.shape[0],
        "second_moment_reconstruction_defect_frobenius": float(np.linalg.norm(
            second_moment - reconstructed_second_moment, ord="fro"
        )),
        "reconstruction": restored,
        "relative_preprocessed_reconstruction_error_frobenius": (
            0.0
            if np.linalg.norm(transformed, ord="fro") == 0.0
            else float(
                np.linalg.norm(
                    transformed - reconstructed_transformed, ord="fro"
                )
                / np.linalg.norm(transformed, ord="fro")
            )
        ),
        "covariance_reconstruction_defect_frobenius": covariance_defect,
    }


def bridge_strain_sensor_data() -> dict[str, Any]:
    """Build the deterministic 24-by-8 bridge-deck strain case."""

    observation = np.arange(24.0)
    sensor = np.arange(8.0)
    common_pattern = np.ones(8) / math.sqrt(8.0)
    gradient_raw = np.asarray([-7.0, -5.0, -3.0, -1.0, 1.0, 3.0, 5.0, 7.0])
    gradient_pattern = gradient_raw / np.linalg.norm(gradient_raw, ord=2)
    common_score = 240.0 * np.sin(2.0 * np.pi * observation / 24.0)
    gradient_score = 90.0 * np.cos(4.0 * np.pi * observation / 24.0)
    offsets = np.asarray([18.0, 20.0, 17.0, 19.0, 21.0, 18.0, 20.0, 17.0])
    perturbation = 2.5 * np.sin(
        0.37 * np.outer(observation + 1.0, sensor + 1.0)
    ) + 1.25 * np.cos(0.19 * np.outer(observation + 2.0, sensor + 1.0))
    data = (
        offsets
        + np.outer(common_score, common_pattern)
        + np.outer(gradient_score, gradient_pattern)
        + perturbation
    )
    return {
        "data_microstrain": data,
        "observation_indices": np.arange(1, 25),
        "sensor_indices": np.arange(1, 9),
        "sensor_offsets_microstrain": offsets,
        "common_pattern": common_pattern,
        "gradient_pattern": gradient_pattern,
        "common_score_microstrain": common_score,
        "gradient_score_microstrain": gradient_score,
        "deterministic_perturbation_microstrain": perturbation,
        "randomness_used": False,
        "real_measurement_claimed": False,
    }


def bridge_strain_case() -> dict[str, Any]:
    """Analyze the frozen bridge sensor matrix by centered SVD and PCA."""

    case = bridge_strain_sensor_data()
    data = case["data_microstrain"]
    centered = center_columns(data)
    decomposition = compute_svd(centered["transformed"], full_matrices=False)
    rank_two = low_rank_approximation(centered["transformed"], 2)
    pca = pca_svd(data, center=True, scale=False, component_count=2)
    return {
        "model": case,
        "preprocessing": {
            "centered": True,
            "scaled": False,
            "removed_column_means_microstrain": centered["means"],
            "reason": "same_unit_comparably_calibrated_sensors",
            "raw_data_modified": False,
        },
        "svd": decomposition,
        "rank_two": rank_two,
        "pca": pca,
        "units": {
            "data": "microstrain",
            "singular_values": "microstrain",
            "loadings": "dimensionless",
            "scores": "microstrain",
        },
        "interpretation_scope": "synthetic_teaching_case_not_bridge_safety_assessment",
    }


def synthetic_thermal_image() -> np.ndarray:
    """Return an original deterministic 18-by-24 grayscale thermal field."""

    y = np.linspace(0.0, 1.0, 18)[:, None]
    x = np.linspace(0.0, 1.0, 24)[None, :]
    first_hotspot = 75.0 * np.exp(-((x - 0.28) ** 2 / 0.028 + (y - 0.35) ** 2 / 0.050))
    second_hotspot = 48.0 * np.exp(-((x - 0.73) ** 2 / 0.045 + (y - 0.67) ** 2 / 0.035))
    gradient = 25.0 + 12.0 * x + 7.0 * y
    seam = 9.0 * ((x > 0.53) & (y > 0.18) & (y < 0.82))
    texture = 1.5 * np.sin(5.0 * np.pi * x) * np.cos(3.0 * np.pi * y)
    return gradient + first_hotspot + second_hotspot + seam + texture


def thermal_image_case() -> dict[str, Any]:
    """Compare deterministic low-rank representations of a thermal image."""

    image = synthetic_thermal_image()
    approximations = {
        str(rank): low_rank_approximation(image, rank) for rank in (1, 2, 3, 5, 8)
    }
    return {
        "image_celsius": image,
        "shape": list(image.shape),
        "rank_approximations": approximations,
        "external_image_used": False,
        "randomness_used": False,
        "pixel_clipping_applied": False,
        "interpretation_scope": "synthetic_thermal_field_for_matrix_compression",
    }


def inverse_noise_case() -> dict[str, Any]:
    """Show noise amplification and an explicit truncated-SVD decision."""

    operator = np.diag([1.0, 0.1, 0.01, 0.001])
    true_parameter = np.asarray([1.0, -1.0, 2.0, 0.0])
    exact_data = operator @ true_parameter
    perturbation = np.asarray([0.0, 0.0, 2.0e-4, -2.0e-4])
    measured_data = exact_data + perturbation
    full = minimum_norm_least_squares(
        operator,
        measured_data,
        relative_tolerance=0.0,
        absolute_tolerance=0.0,
    )
    truncated = minimum_norm_least_squares(
        operator,
        measured_data,
        relative_tolerance=5.0e-3,
        absolute_tolerance=0.0,
    )
    return {
        "operator": operator,
        "singular_values": np.diag(operator),
        "true_parameter": true_parameter,
        "exact_data": exact_data,
        "deterministic_data_perturbation": perturbation,
        "measured_data": measured_data,
        "untruncated_solution": full,
        "truncated_solution": truncated,
        "untruncated_parameter_error_2": float(
            np.linalg.norm(full["solution"] - true_parameter, ord=2)
        ),
        "truncated_parameter_error_2": float(
            np.linalg.norm(truncated["solution"] - true_parameter, ord=2)
        ),
        "regularization_scope": "tsvd_preview_not_automatic_parameter_selection",
        "randomness_used": False,
    }


def repeated_singular_subspace_case() -> dict[str, Any]:
    """Demonstrate basis nonuniqueness inside a repeated singular subspace."""

    matrix = np.diag([3.0, 3.0, 1.0])
    reference = np.eye(3)[:, :2]
    angle = math.pi / 5.0
    rotation = np.asarray(
        [
            [math.cos(angle), -math.sin(angle)],
            [math.sin(angle), math.cos(angle)],
        ]
    )
    alternative = reference @ rotation
    return {
        "matrix": matrix,
        "repeated_singular_value": 3.0,
        "reference_basis": reference,
        "alternative_basis": alternative,
        "columnwise_absolute_inner_products": np.abs(reference.T @ alternative),
        "projector_distance_2": subspace_projector_distance(reference, alternative),
    }


def analytic_subspace_case() -> dict[str, Any]:
    """Provide a small exact-rank rectangular matrix for four-space checks."""

    matrix = np.asarray(
        [
            [1.0, 2.0, 3.0, 1.0],
            [2.0, 4.0, 6.0, 0.0],
            [-1.0, -2.0, -3.0, 1.0],
        ]
    )
    spaces = fundamental_subspaces(
        matrix, relative_tolerance=1.0e-12, absolute_tolerance=0.0
    )
    pseudo = pseudoinverse_svd(
        matrix, relative_tolerance=1.0e-12, absolute_tolerance=0.0
    )
    return {
        "matrix": matrix,
        "subspaces": spaces,
        "pseudoinverse_analysis": pseudo,
    }


def software_record() -> dict[str, Any]:
    """Return the runtime identity used for the deterministic report."""

    return {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "platform": platform.platform(),
        "randomness_used": False,
        "external_data_used": False,
    }


def run_all_cases() -> dict[str, Any]:
    """Run every deterministic Chapter 13 case and return a strict schema."""

    return {
        "schema_version": "1.0",
        "chapter": 13,
        "title": "Tekil Deger Ayristirmasi, Dusuk Rank ve Veri Yapisi",
        "bridge_strain_case": bridge_strain_case(),
        "thermal_image_case": thermal_image_case(),
        "inverse_noise_case": inverse_noise_case(),
        "repeated_singular_subspace_case": repeated_singular_subspace_case(),
        "analytic_subspace_case": analytic_subspace_case(),
        "method_contract": {
            "explicit_inverse_formed": False,
            "normal_matrix_formed_for_svd": False,
            "silent_centering_applied": False,
            "silent_scaling_applied": False,
            "hidden_singular_value_truncation_applied": False,
            "randomness_used": False,
            "external_data_used": False,
            "production_scale_claimed": False,
        },
        "software": software_record(),
    }


def _jsonable(value: Any) -> Any:
    """Convert NumPy and complex objects to strict JSON-compatible values."""

    if isinstance(value, np.ndarray):
        return [_jsonable(item) for item in value.tolist()]
    if isinstance(value, np.generic):
        return _jsonable(value.item())
    if isinstance(value, complex):
        if abs(value.imag) <= 1.0e-15:
            return float(value.real)
        return {"real": float(value.real), "imag": float(value.imag)}
    if isinstance(value, float) and not math.isfinite(value):
        if math.isnan(value):
            return "nan"
        return "infinity" if value > 0.0 else "-infinity"
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _human_summary(report: dict[str, Any]) -> str:
    """Return a compact Turkish summary of the frozen engineering cases."""

    bridge = report["bridge_strain_case"]
    values = np.asarray(bridge["svd"]["singular_values"], dtype=float)
    rank_two = bridge["rank_two"]
    thermal = report["thermal_image_case"]["rank_approximations"]["5"]
    inverse = report["inverse_noise_case"]
    return "\n".join(
        [
            "Bolum 13 - deterministik SVD ve dusuk-rank laboratuvari",
            f"Kopru matrisi boyutu: {bridge['model']['data_microstrain'].shape}",
            "Ilk iki tekil deger (microstrain): "
            + ", ".join(f"{value:.9f}" for value in values[:2]),
            "Rank-2 kareli tekil deger payi: "
            f"{rank_two['captured_squared_singular_value_fraction']:.9f}",
            f"Rank-2 goreli Frobenius hatasi: {rank_two['relative_frobenius_error']:.9f}",
            "Termal goruntu rank-5 goreli Frobenius hatasi: "
            f"{thermal['relative_frobenius_error']:.9f}",
            "Ters problem parametre hatasi (tam / kesilmis): "
            f"{inverse['untruncated_parameter_error_2']:.9f} / "
            f"{inverse['truncated_parameter_error_2']:.9f}",
            "Rastgelelik: yok; dis veri: yok; acik ters: yok.",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(
        description="Bölüm 13 SVD, düşük-rank, sözde ters ve PCA laboratuvarı"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Sonuçları katı JSON olarak yazdır.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the deterministic report in human-readable or JSON mode."""

    arguments = build_parser().parse_args(argv)
    report = run_all_cases()
    if arguments.json:
        print(json.dumps(_jsonable(report), ensure_ascii=False, indent=2, allow_nan=False))
    else:
        print(_human_summary(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
