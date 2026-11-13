#!/usr/bin/env python3
"""Chapter 5: transparent vector-space computations for small examples.

The routines in this module are intentionally limited to deterministic,
small teaching problems. They expose shape and tolerance choices instead of
silently turning an exact independence claim into a numerical one.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from dataclasses import dataclass
from typing import Sequence

import numpy as np


DEFAULT_RTOL = 64.0 * np.finfo(float).eps


class VectorSpaceValidationError(ValueError):
    """Raised when an input violates the chapter's explicit contract."""


class DependentBasisError(VectorSpaceValidationError):
    """Raised when a coordinate request receives a dependent family."""


class SpanMembershipError(VectorSpaceValidationError):
    """Raised when a target is outside the span of a proposed basis."""


@dataclass(frozen=True)
class RREFResult:
    """Reduced row echelon form and the numerical pivot contract."""

    reduced: np.ndarray
    pivot_columns: tuple[int, ...]
    relative_tolerance: float
    absolute_tolerance: float


@dataclass(frozen=True)
class CoordinateResult:
    """Coordinates of a vector in an independent spanning family."""

    coordinates: np.ndarray
    reconstruction: np.ndarray
    residual_inf: float
    relative_tolerance: float
    absolute_tolerance: float


@dataclass(frozen=True)
class MembershipResult:
    """Span-membership decision with an explicit consistency certificate."""

    in_span: bool
    coordinates: np.ndarray | None
    reconstruction_residual_inf: float | None
    inconsistency_certificate_inf: float
    relative_tolerance: float
    absolute_tolerance: float


def as_finite_vector(
    values: Sequence[float] | np.ndarray,
    *,
    name: str = "vector",
    expected_size: int | None = None,
) -> np.ndarray:
    """Return a nonempty, one-dimensional, finite floating-point vector."""

    vector = np.asarray(values, dtype=float)
    if vector.ndim != 1:
        raise VectorSpaceValidationError(f"{name} must be one-dimensional")
    if vector.size == 0:
        raise VectorSpaceValidationError(f"{name} must not be empty")
    if expected_size is not None and vector.size != expected_size:
        raise VectorSpaceValidationError(
            f"{name} must have length {expected_size}, received {vector.size}"
        )
    if not np.all(np.isfinite(vector)):
        raise VectorSpaceValidationError(f"{name} must contain only finite values")
    return vector


def as_finite_matrix(
    values: Sequence[Sequence[float]] | np.ndarray,
    *,
    name: str = "matrix",
) -> np.ndarray:
    """Return a nonempty, two-dimensional, finite floating-point matrix."""

    matrix = np.asarray(values, dtype=float)
    if matrix.ndim != 2:
        raise VectorSpaceValidationError(f"{name} must be two-dimensional")
    if matrix.shape[0] == 0 or matrix.shape[1] == 0:
        raise VectorSpaceValidationError(f"{name} must not have an empty dimension")
    if not np.all(np.isfinite(matrix)):
        raise VectorSpaceValidationError(f"{name} must contain only finite values")
    return matrix


def validated_relative_tolerance(relative_tolerance: float | None) -> float:
    """Return the default or a positive finite user-specified tolerance."""

    if relative_tolerance is None:
        return float(DEFAULT_RTOL)
    value = float(relative_tolerance)
    if not np.isfinite(value) or value <= 0.0:
        raise VectorSpaceValidationError(
            "relative_tolerance must be positive and finite"
        )
    return value


def pivot_tolerance(
    matrix_values: Sequence[Sequence[float]] | np.ndarray,
    *,
    relative_tolerance: float | None = None,
) -> tuple[float, float]:
    """Return relative and absolute pivot tolerances for one matrix."""

    matrix = as_finite_matrix(matrix_values)
    relative = validated_relative_tolerance(relative_tolerance)
    scale = float(np.linalg.norm(matrix, ord=np.inf))
    absolute = relative * scale if scale > 0.0 else relative
    return relative, absolute


def rref(
    matrix_values: Sequence[Sequence[float]] | np.ndarray,
    *,
    relative_tolerance: float | None = None,
) -> RREFResult:
    """Compute an educational RREF with partial row pivoting."""

    matrix = as_finite_matrix(matrix_values).copy()
    relative, absolute = pivot_tolerance(
        matrix, relative_tolerance=relative_tolerance
    )
    if not np.isfinite(absolute):
        raise VectorSpaceValidationError("input pivot scale is not representable")
    row_count, column_count = matrix.shape
    pivot_columns: list[int] = []
    pivot_row = 0

    for column in range(column_count):
        if pivot_row >= row_count:
            break
        candidate_offset = int(np.argmax(np.abs(matrix[pivot_row:, column])))
        candidate_row = pivot_row + candidate_offset
        if abs(matrix[candidate_row, column]) <= absolute:
            continue
        if candidate_row != pivot_row:
            matrix[[pivot_row, candidate_row], :] = matrix[
                [candidate_row, pivot_row], :
            ]

        matrix[pivot_row, :] /= matrix[pivot_row, column]
        for row in range(row_count):
            if row == pivot_row:
                continue
            factor = matrix[row, column]
            if factor != 0.0:
                matrix[row, :] -= factor * matrix[pivot_row, :]
            matrix[row, column] = 0.0
        matrix[pivot_row, column] = 1.0
        if not np.all(np.isfinite(matrix)):
            raise VectorSpaceValidationError("RREF intermediate result is not finite")

        pivot_columns.append(column)
        pivot_row += 1

    # The input-scale threshold has no meaning on rows normalized to a
    # leading one. Preserve those rows; clean only the remaining input-scale rows.
    remainder = matrix[pivot_row:, :]
    remainder[np.abs(remainder) <= absolute] = 0.0
    return RREFResult(
        reduced=matrix,
        pivot_columns=tuple(pivot_columns),
        relative_tolerance=relative,
        absolute_tolerance=absolute,
    )


def independent_columns(
    family_values: Sequence[Sequence[float]] | np.ndarray,
    *,
    relative_tolerance: float | None = None,
) -> tuple[np.ndarray, tuple[int, ...], RREFResult]:
    """Select the original pivot columns as a basis for the given span."""

    family = as_finite_matrix(family_values, name="family")
    reduced = rref(family, relative_tolerance=relative_tolerance)
    indices = tuple(
        column for column in reduced.pivot_columns if column < family.shape[1]
    )
    basis = family[:, indices].copy()
    return basis, indices, reduced


def linear_combination(
    family_values: Sequence[Sequence[float]] | np.ndarray,
    coefficient_values: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Return the column combination family @ coefficients."""

    family = as_finite_matrix(family_values, name="family")
    coefficients = as_finite_vector(
        coefficient_values,
        name="coefficients",
        expected_size=family.shape[1],
    )
    return family @ coefficients


def span_membership(
    family_values: Sequence[Sequence[float]] | np.ndarray,
    target_values: Sequence[float] | np.ndarray,
    *,
    relative_tolerance: float | None = None,
) -> MembershipResult:
    """Decide whether target is in the span using one augmented RREF."""

    family = as_finite_matrix(family_values, name="family")
    target = as_finite_vector(
        target_values, name="target", expected_size=family.shape[0]
    )
    augmented = np.column_stack((family, target))
    reduction = rref(augmented, relative_tolerance=relative_tolerance)
    coefficient_part = reduction.reduced[:, : family.shape[1]]
    right_part = reduction.reduced[:, family.shape[1]]
    zero_left_rows = np.all(
        np.abs(coefficient_part) <= reduction.absolute_tolerance, axis=1
    )
    certificate = float(
        np.max(np.abs(right_part[zero_left_rows]))
        if np.any(zero_left_rows)
        else 0.0
    )
    if certificate > reduction.absolute_tolerance:
        return MembershipResult(
            in_span=False,
            coordinates=None,
            reconstruction_residual_inf=None,
            inconsistency_certificate_inf=certificate,
            relative_tolerance=reduction.relative_tolerance,
            absolute_tolerance=reduction.absolute_tolerance,
        )

    pivot_columns = tuple(
        column
        for column in reduction.pivot_columns
        if column < family.shape[1]
    )
    coordinates: np.ndarray | None = None
    residual: float | None = None
    if len(pivot_columns) == family.shape[1]:
        coordinates = right_part[: family.shape[1]].copy()
        reconstruction = family @ coordinates
        residual = float(np.linalg.norm(reconstruction - target, ord=np.inf))

    return MembershipResult(
        in_span=True,
        coordinates=coordinates,
        reconstruction_residual_inf=residual,
        inconsistency_certificate_inf=certificate,
        relative_tolerance=reduction.relative_tolerance,
        absolute_tolerance=reduction.absolute_tolerance,
    )


def coordinates_in_basis(
    basis_values: Sequence[Sequence[float]] | np.ndarray,
    target_values: Sequence[float] | np.ndarray,
    *,
    relative_tolerance: float | None = None,
) -> CoordinateResult:
    """Return unique coordinates after checking independence and membership."""

    basis = as_finite_matrix(basis_values, name="basis")
    basis_reduction = rref(basis, relative_tolerance=relative_tolerance)
    basis_pivots = tuple(
        column
        for column in basis_reduction.pivot_columns
        if column < basis.shape[1]
    )
    if len(basis_pivots) != basis.shape[1]:
        raise DependentBasisError("basis columns must be linearly independent")

    membership = span_membership(
        basis, target_values, relative_tolerance=relative_tolerance
    )
    if not membership.in_span or membership.coordinates is None:
        raise SpanMembershipError("target is not in the span of the basis")

    target = as_finite_vector(
        target_values, name="target", expected_size=basis.shape[0]
    )
    reconstruction = basis @ membership.coordinates
    residual = float(np.linalg.norm(reconstruction - target, ord=np.inf))
    return CoordinateResult(
        coordinates=membership.coordinates,
        reconstruction=reconstruction,
        residual_inf=residual,
        relative_tolerance=membership.relative_tolerance,
        absolute_tolerance=membership.absolute_tolerance,
    )


def evaluate_quadratic_profile(
    coefficient_values: Sequence[float] | np.ndarray,
    normalized_time_values: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Evaluate c0 + c1*tau + c2*tau**2 at finite normalized times."""

    coefficients = as_finite_vector(
        coefficient_values, name="polynomial coefficients", expected_size=3
    )
    normalized_time = as_finite_vector(
        normalized_time_values, name="normalized time"
    )
    evaluation_matrix = np.column_stack(
        (np.ones_like(normalized_time), normalized_time, normalized_time**2)
    )
    return evaluation_matrix @ coefficients


def rigid_plate_modes() -> np.ndarray:
    """Return local x, y, and rotation displacement modes as columns."""

    horizontal_translation = np.array([1.0, 0.0, 1.0, 0.0])
    vertical_translation = np.array([0.0, 1.0, 0.0, 1.0])
    small_rotation = np.array([0.0, -1.0, 0.0, 1.0])
    return np.column_stack(
        (horizontal_translation, vertical_translation, small_rotation)
    )


def chapter_results(
    *, relative_tolerance: float | None = None
) -> dict[str, object]:
    """Return deterministic results used by the manuscript and tests."""

    modes = rigid_plate_modes()
    basis, pivot_columns, reduction = independent_columns(
        modes, relative_tolerance=relative_tolerance
    )
    observed = np.array([0.01, 0.02, 0.01, 0.04])
    coordinate_result = coordinates_in_basis(
        basis, observed, relative_tolerance=relative_tolerance
    )
    deformation = np.array([0.01, 0.02, 0.03, 0.04])
    deformation_membership = span_membership(
        basis, deformation, relative_tolerance=relative_tolerance
    )

    polynomial_coefficients = np.array([2.0, -3.0, 0.5])
    normalized_times = np.array([-1.0, 0.0, 1.0])
    polynomial_values = evaluate_quadratic_profile(
        polynomial_coefficients, normalized_times
    )

    return {
        "schema_version": "1.0",
        "version": "v0.6",
        "chapter": 5,
        "vector_convention": "column_vectors_left_multiplication",
        "randomness": False,
        "external_data": False,
        "plate_case": {
            "measurement_order": ["d1x", "d1y", "d2x", "d2y"],
            "displacement_unit": "m",
            "basis_shape": list(basis.shape),
            "basis_columns": basis.tolist(),
            "pivot_columns_zero_based": list(pivot_columns),
            "local_motion_dimension": len(pivot_columns),
            "observed_displacement_m": observed.tolist(),
            "basis_coordinates": coordinate_result.coordinates.tolist(),
            "reconstructed_displacement_m": coordinate_result.reconstruction.tolist(),
            "reconstruction_residual_inf_m": coordinate_result.residual_inf,
            "deformation_candidate_m": deformation.tolist(),
            "deformation_in_span": deformation_membership.in_span,
            "deformation_inconsistency_certificate": (
                deformation_membership.inconsistency_certificate_inf
            ),
        },
        "polynomial_case": {
            "basis": ["1", "tau", "tau^2"],
            "normalized_times": normalized_times.tolist(),
            "coordinates": polynomial_coefficients.tolist(),
            "values": polynomial_values.tolist(),
        },
        "numerical_contract": {
            "method": "partial-pivoting-rref-for-small-teaching-examples",
            "relative_tolerance": reduction.relative_tolerance,
            "absolute_tolerance": reduction.absolute_tolerance,
        },
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }


def print_human_readable(results: dict[str, object]) -> None:
    """Print the chapter's central records without hiding units or limits."""

    plate = results["plate_case"]
    polynomial = results["polynomial_case"]
    numerical = results["numerical_contract"]
    assert isinstance(plate, dict)
    assert isinstance(polynomial, dict)
    assert isinstance(numerical, dict)
    print("Chapter 5 - Vector spaces, basis, and dimension")
    print(f"Local rigid-motion dimension: {plate['local_motion_dimension']}")
    print(f"Basis coordinates: {plate['basis_coordinates']}")
    print(
        "Reconstruction residual (inf-norm, m): "
        f"{plate['reconstruction_residual_inf_m']:.3e}"
    )
    print(f"Deformation candidate in span: {plate['deformation_in_span']}")
    print(f"Quadratic profile values: {polynomial['values']}")
    print(f"Relative pivot tolerance: {numerical['relative_tolerance']:.3e}")
    print("Scope: local small-motion teaching model; not a safety diagnosis")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse the human-readable or JSON output mode."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json", action="store_true", help="print machine-readable results"
    )
    parser.add_argument(
        "--rtol",
        type=float,
        default=None,
        help="positive relative pivot tolerance",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the deterministic chapter application."""

    arguments = parse_args(argv)
    try:
        results = chapter_results(relative_tolerance=arguments.rtol)
    except VectorSpaceValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if arguments.json:
        print(json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print_human_readable(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
