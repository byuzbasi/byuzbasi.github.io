#!/usr/bin/env python3
"""Deterministic Chapter 8 computations for orthogonality, projection, and QR.

The module uses only NumPy and the Python standard library.  It deliberately
keeps exact-arithmetic teaching algorithms separate from the Householder QR
provided by ``numpy.linalg.qr``.  Every public computation validates shape and
finiteness, reports residuals, and avoids explicit matrix inverses.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
from dataclasses import asdict, dataclass
from typing import Any, Sequence

import numpy as np


class OrthogonalityQRError(ValueError):
    """Raised when a Chapter 8 numerical contract is not satisfied."""


@dataclass(frozen=True)
class QRResult:
    """A QR factorization together with independent numerical diagnostics."""

    method: str
    q: np.ndarray
    r: np.ndarray
    relative_tolerance: float
    numerical_rank: int
    diagonal_abs: np.ndarray
    condition_2: float
    reconstruction_residual_inf: float
    orthogonality_residual_inf: float
    lower_triangle_residual_inf: float


@dataclass(frozen=True)
class HouseholderResult:
    """One stable Householder reflection and its verification record."""

    vector: np.ndarray
    reflector_direction: np.ndarray
    beta: float
    alpha: float
    reflector: np.ndarray
    transformed_vector: np.ndarray
    orthogonality_residual_inf: float
    symmetry_residual_inf: float
    mapping_residual_inf: float


@dataclass(frozen=True)
class ProjectionResult:
    """Orthogonal decomposition of one vector relative to an orthonormal basis."""

    basis: np.ndarray
    vector: np.ndarray
    coordinates: np.ndarray
    projection: np.ndarray
    residual: np.ndarray
    projector: np.ndarray
    complementary_projector: np.ndarray
    unit: str
    reconstruction_residual_inf: float
    perpendicularity_residual_inf: float
    energy_residual_relative: float
    projector_symmetry_residual_inf: float
    projector_idempotence_residual_inf: float
    complementary_sum_residual_inf: float


@dataclass(frozen=True)
class SensorFrameResult:
    """Right-handed frame built from two calibrated direction columns."""

    direction_matrix: np.ndarray
    q_reduced: np.ndarray
    r: np.ndarray
    frame: np.ndarray
    determinant: float
    direction_cosine: float
    separation_sine: float
    condition_2: float
    frame_orthogonality_residual_inf: float
    qr_reconstruction_residual_inf: float
    qr_orthogonality_residual_inf: float
    relative_tolerance: float


def _as_finite_vector(values: Sequence[float] | np.ndarray, *, name: str) -> np.ndarray:
    """Return a copied, nonempty, finite one-dimensional float vector."""

    vector = np.asarray(values, dtype=float)
    if vector.ndim != 1:
        raise OrthogonalityQRError(f"{name} must be one-dimensional")
    if vector.size == 0:
        raise OrthogonalityQRError(f"{name} must not be empty")
    if not np.all(np.isfinite(vector)):
        raise OrthogonalityQRError(f"{name} must contain only finite values")
    return vector.copy()


def _as_finite_matrix(values: Sequence[Sequence[float]] | np.ndarray, *, name: str) -> np.ndarray:
    """Return a copied, nonempty, finite two-dimensional float matrix."""

    matrix = np.asarray(values, dtype=float)
    if matrix.ndim != 2:
        raise OrthogonalityQRError(f"{name} must be two-dimensional")
    if matrix.shape[0] == 0 or matrix.shape[1] == 0:
        raise OrthogonalityQRError(f"{name} must not have an empty dimension")
    if not np.all(np.isfinite(matrix)):
        raise OrthogonalityQRError(f"{name} must contain only finite values")
    return matrix.copy()


def _validated_relative_tolerance(
    relative_tolerance: float | None,
    *,
    dimension: int,
) -> float:
    """Return a positive, finite, dimension-aware relative tolerance."""

    if relative_tolerance is None:
        return float(32.0 * max(1, dimension) * np.finfo(float).eps)
    value = float(relative_tolerance)
    if not math.isfinite(value) or value <= 0.0:
        raise OrthogonalityQRError("relative_tolerance must be positive and finite")
    return value


def _inf_norm(values: np.ndarray) -> float:
    """Return a finite infinity norm for a vector or matrix."""

    return float(np.linalg.norm(values, ord=np.inf))


def _relative_residual(numerator: np.ndarray, reference: np.ndarray) -> float:
    """Scale an infinity-norm residual by the nonzero reference magnitude."""

    denominator = max(_inf_norm(reference), np.finfo(float).tiny)
    return _inf_norm(numerator) / denominator


def euclidean_inner(
    left_values: Sequence[float] | np.ndarray,
    right_values: Sequence[float] | np.ndarray,
) -> float:
    """Compute the Euclidean inner product after a dimension contract check."""

    left = _as_finite_vector(left_values, name="left")
    right = _as_finite_vector(right_values, name="right")
    if left.shape != right.shape:
        raise OrthogonalityQRError("left and right must have the same shape")
    return float(left @ right)


def normalize_vector(
    vector_values: Sequence[float] | np.ndarray,
) -> tuple[np.ndarray, float]:
    """Normalize a finite nonzero vector and return its original 2-norm."""

    vector = _as_finite_vector(vector_values, name="vector")
    norm_2 = float(np.linalg.norm(vector, ord=2))
    if norm_2 == 0.0 or not math.isfinite(norm_2):
        raise OrthogonalityQRError("vector must have a finite nonzero 2-norm")
    return vector / norm_2, norm_2


def orthogonality_residual(matrix_values: Sequence[Sequence[float]] | np.ndarray) -> float:
    """Measure ``||Q^T Q-I||_inf`` for a matrix with candidate columns."""

    matrix = _as_finite_matrix(matrix_values, name="matrix")
    identity = np.eye(matrix.shape[1], dtype=float)
    return _inf_norm(matrix.T @ matrix - identity)


def canonicalize_qr(
    q_values: Sequence[Sequence[float]] | np.ndarray,
    r_values: Sequence[Sequence[float]] | np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Move QR sign ambiguity into Q so the available R diagonal is nonnegative."""

    q = _as_finite_matrix(q_values, name="q")
    r = _as_finite_matrix(r_values, name="r")
    if q.shape[1] != r.shape[0]:
        raise OrthogonalityQRError("q columns must equal r rows")
    diagonal_size = min(r.shape)
    for index in range(diagonal_size):
        if r[index, index] < 0.0:
            q[:, index] *= -1.0
            r[index, :] *= -1.0
    return q, r


def _factorization_result(
    matrix: np.ndarray,
    q: np.ndarray,
    r: np.ndarray,
    *,
    method: str,
    relative_tolerance: float,
) -> QRResult:
    """Build a common diagnostic record for independently computed factors."""

    diagonal = np.abs(np.diag(r)).astype(float, copy=True)
    diagonal_scale = float(np.max(diagonal)) if diagonal.size else 0.0
    if diagonal_scale == 0.0:
        numerical_rank = 0
    else:
        numerical_rank = int(np.count_nonzero(diagonal > relative_tolerance * diagonal_scale))
    condition = float(np.linalg.cond(matrix, p=2))
    return QRResult(
        method=method,
        q=q.copy(),
        r=r.copy(),
        relative_tolerance=relative_tolerance,
        numerical_rank=numerical_rank,
        diagonal_abs=diagonal,
        condition_2=condition,
        reconstruction_residual_inf=_relative_residual(q @ r - matrix, matrix),
        orthogonality_residual_inf=orthogonality_residual(q),
        lower_triangle_residual_inf=_relative_residual(np.tril(r, k=-1), r),
    )


def classical_gram_schmidt(
    matrix_values: Sequence[Sequence[float]] | np.ndarray,
    *,
    relative_tolerance: float | None = None,
) -> QRResult:
    """Compute teaching QR by classical Gram-Schmidt for a tall full-rank matrix."""

    matrix = _as_finite_matrix(matrix_values, name="matrix")
    rows, columns = matrix.shape
    if rows < columns:
        raise OrthogonalityQRError("classical Gram-Schmidt requires rows >= columns")
    relative = _validated_relative_tolerance(relative_tolerance, dimension=max(matrix.shape))
    matrix_scale = max(float(np.linalg.norm(matrix, ord=2)), np.finfo(float).tiny)
    q = np.zeros((rows, columns), dtype=float)
    r = np.zeros((columns, columns), dtype=float)
    for column in range(columns):
        source = matrix[:, column]
        if column:
            coefficients = q[:, :column].T @ source
            r[:column, column] = coefficients
            residual = source - q[:, :column] @ coefficients
        else:
            residual = source.copy()
        diagonal = float(np.linalg.norm(residual, ord=2))
        if diagonal <= relative * matrix_scale:
            raise OrthogonalityQRError(
                "classical Gram-Schmidt encountered a dependent or unresolved column"
            )
        r[column, column] = diagonal
        q[:, column] = residual / diagonal
    q, r = canonicalize_qr(q, r)
    return _factorization_result(
        matrix,
        q,
        r,
        method="classical_gram_schmidt",
        relative_tolerance=relative,
    )


def modified_gram_schmidt(
    matrix_values: Sequence[Sequence[float]] | np.ndarray,
    *,
    relative_tolerance: float | None = None,
) -> QRResult:
    """Compute teaching QR by modified Gram-Schmidt with explicit updates."""

    matrix = _as_finite_matrix(matrix_values, name="matrix")
    rows, columns = matrix.shape
    if rows < columns:
        raise OrthogonalityQRError("modified Gram-Schmidt requires rows >= columns")
    relative = _validated_relative_tolerance(relative_tolerance, dimension=max(matrix.shape))
    matrix_scale = max(float(np.linalg.norm(matrix, ord=2)), np.finfo(float).tiny)
    work = matrix.copy()
    q = np.zeros((rows, columns), dtype=float)
    r = np.zeros((columns, columns), dtype=float)
    for column in range(columns):
        diagonal = float(np.linalg.norm(work[:, column], ord=2))
        if diagonal <= relative * matrix_scale:
            raise OrthogonalityQRError(
                "modified Gram-Schmidt encountered a dependent or unresolved column"
            )
        r[column, column] = diagonal
        q[:, column] = work[:, column] / diagonal
        for following in range(column + 1, columns):
            coefficient = float(q[:, column] @ work[:, following])
            r[column, following] = coefficient
            work[:, following] -= coefficient * q[:, column]
    q, r = canonicalize_qr(q, r)
    return _factorization_result(
        matrix,
        q,
        r,
        method="modified_gram_schmidt",
        relative_tolerance=relative,
    )


def householder_reflector(
    vector_values: Sequence[float] | np.ndarray,
) -> HouseholderResult:
    """Construct a stable reflection that maps a vector to ``alpha e1``."""

    vector = _as_finite_vector(vector_values, name="vector")
    norm_2 = float(np.linalg.norm(vector, ord=2))
    if norm_2 == 0.0 or not math.isfinite(norm_2):
        raise OrthogonalityQRError("Householder input must have a finite nonzero norm")
    alpha = -math.copysign(norm_2, float(vector[0]))
    direction = vector.copy()
    direction[0] -= alpha
    direction_norm_squared = float(direction @ direction)
    if direction_norm_squared == 0.0 or not math.isfinite(direction_norm_squared):
        raise OrthogonalityQRError("Householder direction could not be resolved")
    beta = 2.0 / direction_norm_squared
    reflector = np.eye(vector.size) - beta * np.outer(direction, direction)
    transformed = reflector @ vector
    target = np.zeros_like(vector)
    target[0] = alpha
    identity = np.eye(vector.size)
    return HouseholderResult(
        vector=vector,
        reflector_direction=direction,
        beta=beta,
        alpha=alpha,
        reflector=reflector,
        transformed_vector=transformed,
        orthogonality_residual_inf=_inf_norm(reflector.T @ reflector - identity),
        symmetry_residual_inf=_inf_norm(reflector.T - reflector),
        mapping_residual_inf=_relative_residual(transformed - target, vector),
    )


def teaching_householder_qr(
    matrix_values: Sequence[Sequence[float]] | np.ndarray,
    *,
    relative_tolerance: float | None = None,
) -> QRResult:
    """Compute an unblocked Householder QR for transparent small examples."""

    matrix = _as_finite_matrix(matrix_values, name="matrix")
    rows, columns = matrix.shape
    if rows < columns:
        raise OrthogonalityQRError("teaching Householder QR requires rows >= columns")
    relative = _validated_relative_tolerance(relative_tolerance, dimension=max(matrix.shape))
    matrix_scale = max(float(np.linalg.norm(matrix, ord=2)), np.finfo(float).tiny)
    work = matrix.copy()
    q_complete = np.eye(rows, dtype=float)
    for column in range(columns):
        tail = work[column:, column]
        tail_norm = float(np.linalg.norm(tail, ord=2))
        if tail_norm <= relative * matrix_scale:
            raise OrthogonalityQRError(
                "Householder QR encountered a dependent or unresolved column"
            )
        reflection = householder_reflector(tail)
        direction = reflection.reflector_direction
        beta = reflection.beta
        trailing = work[column:, column:]
        work[column:, column:] = trailing - beta * np.outer(
            direction, direction @ trailing
        )
        q_tail = q_complete[:, column:]
        q_complete[:, column:] = q_tail - beta * np.outer(
            q_tail @ direction, direction
        )
    q = q_complete[:, :columns]
    r = np.triu(work[:columns, :])
    q, r = canonicalize_qr(q, r)
    return _factorization_result(
        matrix,
        q,
        r,
        method="teaching_householder",
        relative_tolerance=relative,
    )


def numpy_householder_qr(
    matrix_values: Sequence[Sequence[float]] | np.ndarray,
    *,
    relative_tolerance: float | None = None,
) -> QRResult:
    """Compute the canonical reduced QR through NumPy's LAPACK interface."""

    matrix = _as_finite_matrix(matrix_values, name="matrix")
    rows, columns = matrix.shape
    if rows < columns:
        raise OrthogonalityQRError("the Chapter 8 reduced QR contract requires rows >= columns")
    relative = _validated_relative_tolerance(relative_tolerance, dimension=max(matrix.shape))
    try:
        q, r = np.linalg.qr(matrix, mode="reduced")
    except np.linalg.LinAlgError as exc:
        raise OrthogonalityQRError("NumPy QR factorization failed") from exc
    q, r = canonicalize_qr(q, r)
    matrix_scale = max(float(np.linalg.norm(matrix, ord=2)), np.finfo(float).tiny)
    threshold = relative * matrix_scale
    if not math.isfinite(threshold) or np.any(np.abs(np.diag(r)) <= threshold):
        raise OrthogonalityQRError(
            "NumPy QR encountered a dependent or unresolved column: "
            f"every abs(r_jj) must exceed {threshold!r} "
            f"(relative_tolerance={relative!r})"
        )
    return _factorization_result(
        matrix,
        q,
        r,
        method="numpy_householder",
        relative_tolerance=relative,
    )


def orthogonal_projection(
    basis_values: Sequence[Sequence[float]] | np.ndarray,
    vector_values: Sequence[float] | np.ndarray,
    *,
    unit: str = "unspecified",
    relative_tolerance: float | None = None,
) -> ProjectionResult:
    """Project a vector onto the columns of a verified orthonormal matrix."""

    basis = _as_finite_matrix(basis_values, name="basis")
    vector = _as_finite_vector(vector_values, name="vector")
    if basis.shape[0] != vector.size:
        raise OrthogonalityQRError("basis rows must equal vector length")
    relative = _validated_relative_tolerance(relative_tolerance, dimension=max(basis.shape))
    basis_residual = orthogonality_residual(basis)
    if basis_residual > 10.0 * relative:
        raise OrthogonalityQRError("basis columns are not orthonormal within tolerance")
    try:
        with np.errstate(over="raise", invalid="raise"):
            coordinates = basis.T @ vector
            projection = basis @ coordinates
            residual = vector - projection
    except FloatingPointError as exc:
        raise OrthogonalityQRError("projection is not representable at the input scale") from exc
    projector = basis @ basis.T
    identity = np.eye(basis.shape[0], dtype=float)
    complementary = identity - projector
    scale = float(np.max(np.abs(vector)))
    if scale == 0.0:
        energy_residual = 0.0
    else:
        scaled_vector = vector / scale
        scaled_projection = projection / scale
        scaled_residual = residual / scale
        squared_norm = float(scaled_vector @ scaled_vector)
        energy_difference = abs(
            squared_norm - float(scaled_projection @ scaled_projection)
            - float(scaled_residual @ scaled_residual)
        )
        root_tiny = math.sqrt(np.finfo(float).tiny)
        if scale >= root_tiny / math.sqrt(squared_norm):
            energy_residual = energy_difference / squared_norm
        else:
            # Preserve max(||y||^2, tiny), including its absolute floor.
            energy_residual = energy_difference * (scale / root_tiny) ** 2
    if not math.isfinite(energy_residual):
        raise OrthogonalityQRError("projection energy diagnostic is not finite")
    return ProjectionResult(
        basis=basis,
        vector=vector,
        coordinates=coordinates,
        projection=projection,
        residual=residual,
        projector=projector,
        complementary_projector=complementary,
        unit=str(unit),
        reconstruction_residual_inf=_relative_residual(
            projection + residual - vector, vector
        ),
        perpendicularity_residual_inf=_relative_residual(
            basis.T @ residual, vector
        ),
        energy_residual_relative=energy_residual,
        projector_symmetry_residual_inf=_inf_norm(projector.T - projector),
        projector_idempotence_residual_inf=_inf_norm(projector @ projector - projector),
        complementary_sum_residual_inf=_inf_norm(projector + complementary - identity),
    )


def main_direction_matrix() -> np.ndarray:
    """Return the two calibrated, dimensionless Chapter 8 direction columns."""

    return np.array([[2.0, 3.0], [1.0, 1.0], [2.0, 1.0]], dtype=float)


def main_measurement_vector() -> np.ndarray:
    """Return the canonical acceleration measurement in metres per second squared."""

    return np.array([1.0, 2.0, -1.0], dtype=float)


def sensor_frame(
    direction_values: Sequence[Sequence[float]] | np.ndarray | None = None,
    *,
    relative_tolerance: float | None = None,
) -> SensorFrameResult:
    """Build a right-handed frame from two independent direction columns."""

    directions = main_direction_matrix() if direction_values is None else _as_finite_matrix(
        direction_values, name="directions"
    )
    if directions.shape != (3, 2):
        raise OrthogonalityQRError("directions must have shape (3, 2)")
    qr = numpy_householder_qr(directions, relative_tolerance=relative_tolerance)
    if qr.numerical_rank < 2:
        raise OrthogonalityQRError("two independent direction columns are required")
    q1 = qr.q[:, 0]
    q2 = qr.q[:, 1]
    q3, _ = normalize_vector(np.cross(q1, q2))
    frame = np.column_stack((q1, q2, q3))
    determinant = float(np.linalg.det(frame))
    if determinant < 0.0:
        frame[:, 2] *= -1.0
        determinant = float(np.linalg.det(frame))
    norm_first = float(np.linalg.norm(directions[:, 0], ord=2))
    norm_second = float(np.linalg.norm(directions[:, 1], ord=2))
    direction_cosine = float(
        directions[:, 0] @ directions[:, 1] / (norm_first * norm_second)
    )
    separation_sine = float(qr.r[1, 1] / norm_second)
    return SensorFrameResult(
        direction_matrix=directions,
        q_reduced=qr.q,
        r=qr.r,
        frame=frame,
        determinant=determinant,
        direction_cosine=direction_cosine,
        separation_sine=separation_sine,
        condition_2=qr.condition_2,
        frame_orthogonality_residual_inf=orthogonality_residual(frame),
        qr_reconstruction_residual_inf=qr.reconstruction_residual_inf,
        qr_orthogonality_residual_inf=qr.orthogonality_residual_inf,
        relative_tolerance=qr.relative_tolerance,
    )


def main_measurement_decomposition(
    *,
    relative_tolerance: float | None = None,
) -> ProjectionResult:
    """Decompose the canonical acceleration into model-plane and normal parts."""

    frame = sensor_frame(relative_tolerance=relative_tolerance)
    return orthogonal_projection(
        frame.q_reduced,
        main_measurement_vector(),
        unit="m/s^2",
        relative_tolerance=frame.relative_tolerance,
    )


def near_parallel_direction_case(
    epsilon: float,
    *,
    relative_tolerance: float | None = None,
) -> dict[str, Any]:
    """Evaluate two directions whose angular separation is controlled by epsilon."""

    value = float(epsilon)
    if not math.isfinite(value) or value <= 0.0:
        raise OrthogonalityQRError("epsilon must be positive and finite")
    first = main_direction_matrix()[:, 0]
    offset = np.array([1.0, 0.0, -1.0], dtype=float)
    second = first + value * offset
    matrix = np.column_stack((first, second))
    relative = _validated_relative_tolerance(relative_tolerance, dimension=max(matrix.shape))
    try:
        qr = numpy_householder_qr(matrix, relative_tolerance=relative)
    except OrthogonalityQRError as exc:
        return {
            "status": "rejected_at_tolerance", "reason": str(exc),
            "epsilon": value, "matrix": matrix,
            "relative_tolerance": relative,
            "r_diagonal": None, "direction_cosine": None,
            "separation_sine": None, "condition_2": float(np.linalg.cond(matrix, p=2)),
            "numerical_rank": None, "orthogonality_residual_inf": None,
            "reconstruction_residual_inf": None,
        }
    norm_first = float(np.linalg.norm(first, ord=2))
    norm_second = float(np.linalg.norm(second, ord=2))
    cosine = float(first @ second / (norm_first * norm_second))
    sine = float(qr.r[1, 1] / norm_second)
    return {
        "status": "computed",
        "epsilon": value,
        "matrix": matrix,
        "r_diagonal": np.diag(qr.r).copy(),
        "direction_cosine": cosine,
        "separation_sine": sine,
        "condition_2": qr.condition_2,
        "numerical_rank": qr.numerical_rank,
        "relative_tolerance": qr.relative_tolerance,
        "orthogonality_residual_inf": qr.orthogonality_residual_inf,
        "reconstruction_residual_inf": qr.reconstruction_residual_inf,
    }


def gram_schmidt_stress_matrix(epsilon: float) -> np.ndarray:
    """Return the deterministic 4-by-3 near-dependent teaching family."""

    value = float(epsilon)
    if not math.isfinite(value) or value <= 0.0:
        raise OrthogonalityQRError("epsilon must be positive and finite")
    u = np.array([1.0, 1.0, 1.0, 1.0])
    v = np.array([1.0, -1.0, 1.0, -1.0])
    w = np.array([1.0, 1.0, -1.0, -1.0])
    return np.column_stack((u, u + value * v, u + value * v + value**2 * w))


def gram_schmidt_stress_case(
    epsilon: float,
    *,
    relative_tolerance: float | None = None,
) -> dict[str, Any]:
    """Compare CGS, MGS, teaching Householder, and NumPy Householder QR."""

    matrix = gram_schmidt_stress_matrix(epsilon)
    methods: dict[str, dict[str, Any]] = {}
    for name, method in (
        ("classical_gram_schmidt", classical_gram_schmidt),
        ("modified_gram_schmidt", modified_gram_schmidt),
        ("teaching_householder", teaching_householder_qr),
        ("numpy_householder", numpy_householder_qr),
    ):
        try:
            result = method(matrix, relative_tolerance=relative_tolerance)
        except OrthogonalityQRError as exc:
            methods[name] = {
                "status": "rejected_at_tolerance", "reason": str(exc),
                "orthogonality_residual_inf": None,
                "reconstruction_residual_inf": None,
                "lower_triangle_residual_inf": None, "r_diagonal": None,
            }
        else:
            methods[name] = {
                "status": "computed",
                "orthogonality_residual_inf": result.orthogonality_residual_inf,
                "reconstruction_residual_inf": result.reconstruction_residual_inf,
                "lower_triangle_residual_inf": result.lower_triangle_residual_inf,
                "r_diagonal": np.diag(result.r).copy(),
            }
    return {
        "epsilon": float(epsilon),
        "matrix": matrix,
        "condition_2": float(np.linalg.cond(matrix, p=2)),
        "relative_tolerance": _validated_relative_tolerance(
            relative_tolerance, dimension=max(matrix.shape)
        ),
        "methods": methods,
    }


def square_qr_solve(
    matrix_values: Sequence[Sequence[float]] | np.ndarray,
    right_hand_side_values: Sequence[float] | np.ndarray,
    *,
    relative_tolerance: float | None = None,
) -> dict[str, Any]:
    """Solve a square full-rank system through QR without forming an inverse."""

    matrix = _as_finite_matrix(matrix_values, name="matrix")
    right_hand_side = _as_finite_vector(right_hand_side_values, name="right_hand_side")
    if matrix.shape[0] != matrix.shape[1]:
        raise OrthogonalityQRError("square_qr_solve requires a square matrix")
    if right_hand_side.size != matrix.shape[0]:
        raise OrthogonalityQRError("right_hand_side length must equal matrix size")
    qr = numpy_householder_qr(matrix, relative_tolerance=relative_tolerance)
    if qr.numerical_rank < matrix.shape[1]:
        raise OrthogonalityQRError("square system is singular or unresolved at the tolerance")
    transformed_rhs = qr.q.T @ right_hand_side
    try:
        solution = np.linalg.solve(qr.r, transformed_rhs)
    except np.linalg.LinAlgError as exc:
        raise OrthogonalityQRError("triangular QR solve failed") from exc
    return {
        "matrix": matrix,
        "right_hand_side": right_hand_side,
        "q": qr.q,
        "r": qr.r,
        "transformed_right_hand_side": transformed_rhs,
        "solution": solution,
        "relative_residual_inf": _relative_residual(
            matrix @ solution - right_hand_side, right_hand_side
        ),
        "condition_2": qr.condition_2,
        "relative_tolerance": qr.relative_tolerance,
    }


def _json_ready(value: Any) -> Any:
    """Convert dataclasses and NumPy values into strict JSON-compatible values."""

    if hasattr(value, "__dataclass_fields__"):
        return _json_ready(asdict(value))
    if isinstance(value, np.ndarray):
        return _json_ready(value.tolist())
    if isinstance(value, np.generic):
        return _json_ready(value.item())
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    return value


def chapter_results(*, relative_tolerance: float | None = None) -> dict[str, Any]:
    """Return the complete deterministic Chapter 8 evidence record."""

    directions = main_direction_matrix()
    cgs = classical_gram_schmidt(directions, relative_tolerance=relative_tolerance)
    mgs = modified_gram_schmidt(directions, relative_tolerance=relative_tolerance)
    teaching = teaching_householder_qr(directions, relative_tolerance=relative_tolerance)
    numpy_qr = numpy_householder_qr(directions, relative_tolerance=relative_tolerance)
    frame = sensor_frame(directions, relative_tolerance=relative_tolerance)
    decomposition = main_measurement_decomposition(relative_tolerance=relative_tolerance)
    reflector = householder_reflector(np.array([4.0, 3.0, 0.0]))
    square_solve = square_qr_solve(
        np.array([[2.0, 1.0], [1.0, 2.0]]),
        np.array([5.0, 4.0]),
        relative_tolerance=relative_tolerance,
    )
    results = {
        "schema_version": "1.1",
        "version": "v0.9",
        "chapter": 8,
        "chapter_title": "Ortogonallik, Izdusum ve QR Ayrisimi",
        "vector_convention": "column_vectors_left_multiplication",
        "units": {
            "direction_columns": "dimensionless calibrated directions",
            "measurement": "m/s^2",
            "projection": "m/s^2",
            "residual": "m/s^2",
            "squared_norms": "(m/s^2)^2",
        },
        "assumptions": [
            "real finite-dimensional Euclidean space",
            "direction columns share one calibrated body frame",
            "raw channels with unlike units are not directly inner-producted",
            "the main direction matrix has full column rank",
            "QR signs are canonicalized through a nonnegative R diagonal",
            "a projection residual is model-external, not automatically sensor noise",
            "the example is instructional and not a navigation or safety certificate",
            "no external data or randomness is used",
        ],
        "main_direction_matrix": directions,
        "main_qr": {
            "classical_gram_schmidt": cgs,
            "modified_gram_schmidt": mgs,
            "teaching_householder": teaching,
            "numpy_householder": numpy_qr,
        },
        "sensor_frame": frame,
        "measurement_decomposition": decomposition,
        "householder_example": reflector,
        "square_qr_solve": square_solve,
        "near_parallel_cases": [
            near_parallel_direction_case(value, relative_tolerance=relative_tolerance)
            for value in (1e-2, 1e-6, 1e-10)
        ],
        "gram_schmidt_stress_cases": [
            gram_schmidt_stress_case(value, relative_tolerance=relative_tolerance)
            for value in (1e-2, 1e-4, 1e-6)
        ],
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "external_data": False,
        "randomness": False,
    }
    return _json_ready(results)


def print_human_readable(results: dict[str, Any]) -> None:
    """Print a concise Turkish summary of the canonical evidence record."""

    frame = results["sensor_frame"]
    decomposition = results["measurement_decomposition"]
    numpy_qr = results["main_qr"]["numpy_householder"]
    print("Bölüm 8 - Ortogonallik, İzdüşüm ve QR Ayrışımı")
    print(f"Yön matrisi: {results['main_direction_matrix']}")
    print(f"Kanonik Q2: {numpy_qr['q']}")
    print(f"Kanonik R: {numpy_qr['r']}")
    print(f"Sağ-elli çerçeve determinantı: {frame['determinant']:.12g}")
    print(f"Ölçüm: {decomposition['vector']} {decomposition['unit']}")
    print(f"İzdüşüm: {decomposition['projection']} {decomposition['unit']}")
    print(f"Dik artık: {decomposition['residual']} {decomposition['unit']}")
    print(
        "QR artıkları: "
        f"yeniden_kurma={numpy_qr['reconstruction_residual_inf']:.3e}, "
        f"ortogonallik={numpy_qr['orthogonality_residual_inf']:.3e}"
    )
    print(
        "İzdüşüm artıkları: "
        f"diklik={decomposition['perpendicularity_residual_inf']:.3e}, "
        f"enerji={decomposition['energy_residual_relative']:.3e}"
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line options for human-readable or strict JSON output."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the deterministic validation record as strict JSON.",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation when --json is used.",
    )
    parser.add_argument(
        "--relative-tolerance",
        type=float,
        default=None,
        help="Positive relative tolerance for rank and orthonormality contracts.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the canonical Chapter 8 example."""

    arguments = parse_args(argv)
    results = chapter_results(relative_tolerance=arguments.relative_tolerance)
    if arguments.json:
        print(
            json.dumps(
                results,
                ensure_ascii=False,
                indent=arguments.indent,
                sort_keys=True,
                allow_nan=False,
            )
        )
    else:
        print_human_readable(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
