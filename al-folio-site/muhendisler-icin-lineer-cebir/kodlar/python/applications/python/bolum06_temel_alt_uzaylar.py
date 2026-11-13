#!/usr/bin/env python3
"""Chapter 6: four fundamental subspaces for small teaching matrices.

The routines are deterministic and intentionally limited to transparent,
small examples. Numerical rank decisions always retain their scale and
tolerance contract; they are not presented as exact symbolic proofs.
"""

from __future__ import annotations

import argparse
import json
import platform
from dataclasses import dataclass
from typing import Sequence

import numpy as np

from bolum05_vektor_uzaylari import (
    RREFResult,
    VectorSpaceValidationError,
    as_finite_matrix,
    as_finite_vector,
    rref,
    span_membership,
)


@dataclass(frozen=True)
class FundamentalSubspacesResult:
    """Column-oriented bases and the numerical contract for four subspaces."""

    matrix: np.ndarray
    rank: int
    transpose_rank: int
    pivot_columns: tuple[int, ...]
    free_columns: tuple[int, ...]
    column_space_basis: np.ndarray
    row_space_basis: np.ndarray
    null_space_basis: np.ndarray
    left_null_space_basis: np.ndarray
    relative_tolerance: float
    absolute_tolerance: float
    transpose_absolute_tolerance: float
    null_residual_inf: float
    left_null_residual_inf: float
    row_null_orthogonality_inf: float
    column_left_null_orthogonality_inf: float


@dataclass(frozen=True)
class LinearSystemGeometryResult:
    """Reachability decision and affine solution data for one right-hand side."""

    reachable: bool
    particular_solution: np.ndarray | None
    null_space_basis: np.ndarray
    reconstruction_residual_inf: float | None
    augmented_inconsistency_inf: float
    left_null_coordinates: np.ndarray
    left_null_certificate_inf: float
    relative_tolerance: float
    absolute_tolerance: float


@dataclass(frozen=True)
class IdentifiabilityResult:
    """Whether a linear functional belongs to the row space of a matrix."""

    identifiable: bool
    row_coordinates: np.ndarray | None
    reconstruction_residual_inf: float | None
    inconsistency_certificate_inf: float


def _inf_norm_or_zero(values: np.ndarray) -> float:
    """Return the infinity norm, defining the norm of an empty array as zero."""

    if values.size == 0:
        return 0.0
    return float(np.linalg.norm(values, ord=np.inf))


def _null_basis_from_reduction(reduction: RREFResult) -> np.ndarray:
    """Construct a column basis for a null space from one RREF result."""

    reduced = reduction.reduced
    column_count = reduced.shape[1]
    pivot_columns = tuple(
        column for column in reduction.pivot_columns if column < column_count
    )
    free_columns = tuple(
        column for column in range(column_count) if column not in pivot_columns
    )
    basis = np.zeros((column_count, len(free_columns)), dtype=float)
    for basis_column, free_column in enumerate(free_columns):
        basis[free_column, basis_column] = 1.0
        for pivot_row, pivot_column in enumerate(pivot_columns):
            basis[pivot_column, basis_column] = -reduced[pivot_row, free_column]
    return basis


def null_space_basis(
    matrix_values: Sequence[Sequence[float]] | np.ndarray,
    *,
    relative_tolerance: float | None = None,
) -> tuple[np.ndarray, RREFResult]:
    """Return a column basis for N(A) using free variables of an RREF."""

    matrix = as_finite_matrix(matrix_values)
    reduction = rref(matrix, relative_tolerance=relative_tolerance)
    return _null_basis_from_reduction(reduction), reduction


def fundamental_subspaces(
    matrix_values: Sequence[Sequence[float]] | np.ndarray,
    *,
    relative_tolerance: float | None = None,
) -> FundamentalSubspacesResult:
    """Compute column-oriented bases for col(A), row(A), N(A), and N(A.T)."""

    matrix = as_finite_matrix(matrix_values)
    reduction = rref(matrix, relative_tolerance=relative_tolerance)
    transpose_reduction = rref(
        matrix.T, relative_tolerance=reduction.relative_tolerance
    )
    row_count, column_count = matrix.shape
    pivot_columns = tuple(
        column for column in reduction.pivot_columns if column < column_count
    )
    free_columns = tuple(
        column for column in range(column_count) if column not in pivot_columns
    )
    rank = len(pivot_columns)
    transpose_rank = len(transpose_reduction.pivot_columns)

    column_basis = (
        matrix[:, pivot_columns].copy()
        if pivot_columns
        else np.empty((row_count, 0), dtype=float)
    )
    row_basis = (
        reduction.reduced[:rank, :].T.copy()
        if rank
        else np.empty((column_count, 0), dtype=float)
    )
    null_basis = _null_basis_from_reduction(reduction)
    left_null_basis = _null_basis_from_reduction(transpose_reduction)

    # Separate reductions can disagree at a selected numerical threshold.
    # Do not publish four spaces that contradict their own dimension contract.
    expected_shapes = (
        (row_count, rank), (column_count, rank),
        (column_count, column_count - rank), (row_count, row_count - rank),
    )
    actual_shapes = tuple(
        basis.shape for basis in (column_basis, row_basis, null_basis, left_null_basis)
    )
    if rank != transpose_rank or actual_shapes != expected_shapes:
        raise VectorSpaceValidationError(
            "four-subspace rank/dimension contract unresolved: "
            f"rank(A)={rank}, rank(A.T)={transpose_rank}, "
            f"basis_shapes={actual_shapes}, expected={expected_shapes}, "
            f"relative_tolerance={reduction.relative_tolerance!r}, "
            f"absolute_tolerances=({reduction.absolute_tolerance!r}, "
            f"{transpose_reduction.absolute_tolerance!r}); "
            "no rank or tolerance was changed"
        )

    null_residual = _inf_norm_or_zero(matrix @ null_basis)
    left_null_residual = _inf_norm_or_zero(matrix.T @ left_null_basis)
    row_null_residual = _inf_norm_or_zero(row_basis.T @ null_basis)
    column_left_residual = _inf_norm_or_zero(
        column_basis.T @ left_null_basis
    )

    return FundamentalSubspacesResult(
        matrix=matrix.copy(),
        rank=rank,
        transpose_rank=transpose_rank,
        pivot_columns=pivot_columns,
        free_columns=free_columns,
        column_space_basis=column_basis,
        row_space_basis=row_basis,
        null_space_basis=null_basis,
        left_null_space_basis=left_null_basis,
        relative_tolerance=reduction.relative_tolerance,
        absolute_tolerance=reduction.absolute_tolerance,
        transpose_absolute_tolerance=transpose_reduction.absolute_tolerance,
        null_residual_inf=null_residual,
        left_null_residual_inf=left_null_residual,
        row_null_orthogonality_inf=row_null_residual,
        column_left_null_orthogonality_inf=column_left_residual,
    )


def linear_system_geometry(
    matrix_values: Sequence[Sequence[float]] | np.ndarray,
    target_values: Sequence[float] | np.ndarray,
    *,
    relative_tolerance: float | None = None,
) -> LinearSystemGeometryResult:
    """Describe the exact-consistency geometry of A x = b at one tolerance."""

    matrix = as_finite_matrix(matrix_values)
    target = as_finite_vector(
        target_values, name="target", expected_size=matrix.shape[0]
    )
    spaces = fundamental_subspaces(
        matrix, relative_tolerance=relative_tolerance
    )
    augmented = np.column_stack((matrix, target))
    reduction = rref(
        augmented, relative_tolerance=spaces.relative_tolerance
    )
    coefficient_part = reduction.reduced[:, : matrix.shape[1]]
    right_part = reduction.reduced[:, matrix.shape[1]]
    zero_left_rows = np.all(
        np.abs(coefficient_part) <= reduction.absolute_tolerance, axis=1
    )
    augmented_inconsistency = float(
        np.max(np.abs(right_part[zero_left_rows]))
        if np.any(zero_left_rows)
        else 0.0
    )
    left_coordinates = spaces.left_null_space_basis.T @ target
    left_certificate = _inf_norm_or_zero(left_coordinates)
    reachable = augmented_inconsistency <= reduction.absolute_tolerance

    if not reachable:
        return LinearSystemGeometryResult(
            reachable=False,
            particular_solution=None,
            null_space_basis=spaces.null_space_basis.copy(),
            reconstruction_residual_inf=None,
            augmented_inconsistency_inf=augmented_inconsistency,
            left_null_coordinates=left_coordinates,
            left_null_certificate_inf=left_certificate,
            relative_tolerance=reduction.relative_tolerance,
            absolute_tolerance=reduction.absolute_tolerance,
        )

    particular = np.zeros(matrix.shape[1], dtype=float)
    coefficient_pivots = tuple(
        column
        for column in reduction.pivot_columns
        if column < matrix.shape[1]
    )
    for pivot_row, pivot_column in enumerate(coefficient_pivots):
        particular[pivot_column] = right_part[pivot_row]
    residual = _inf_norm_or_zero(matrix @ particular - target)
    return LinearSystemGeometryResult(
        reachable=True,
        particular_solution=particular,
        null_space_basis=spaces.null_space_basis.copy(),
        reconstruction_residual_inf=residual,
        augmented_inconsistency_inf=augmented_inconsistency,
        left_null_coordinates=left_coordinates,
        left_null_certificate_inf=left_certificate,
        relative_tolerance=reduction.relative_tolerance,
        absolute_tolerance=reduction.absolute_tolerance,
    )


def identifiable_functional(
    matrix_values: Sequence[Sequence[float]] | np.ndarray,
    functional_values: Sequence[float] | np.ndarray,
    *,
    relative_tolerance: float | None = None,
) -> IdentifiabilityResult:
    """Decide whether c.T x is determined by y=A x, equivalently c in row(A)."""

    matrix = as_finite_matrix(matrix_values)
    functional = as_finite_vector(
        functional_values,
        name="functional",
        expected_size=matrix.shape[1],
    )
    spaces = fundamental_subspaces(
        matrix, relative_tolerance=relative_tolerance
    )
    if spaces.row_space_basis.shape[1] == 0:
        # The empty basis spans exactly {0}; a tiny nonzero functional is
        # not silently declared zero by an unrelated matrix-scale threshold.
        is_zero = bool(np.all(functional == 0.0))
        return IdentifiabilityResult(
            identifiable=is_zero,
            row_coordinates=np.empty(0, dtype=float) if is_zero else None,
            reconstruction_residual_inf=0.0 if is_zero else None,
            inconsistency_certificate_inf=_inf_norm_or_zero(functional),
        )
    membership = span_membership(
        spaces.row_space_basis,
        functional,
        relative_tolerance=spaces.relative_tolerance,
    )
    return IdentifiabilityResult(
        identifiable=membership.in_span,
        row_coordinates=membership.coordinates,
        reconstruction_residual_inf=membership.reconstruction_residual_inf,
        inconsistency_certificate_inf=membership.inconsistency_certificate_inf,
    )


def actuator_sensor_matrix() -> np.ndarray:
    """Return the original dimensionless four-command, three-output model."""

    return np.array(
        [
            [1.0, 0.0, 1.0, 0.0],
            [0.0, 1.0, 1.0, 1.0],
            [1.0, 1.0, 2.0, 1.0],
        ]
    )


def _optional_array(values: np.ndarray | None) -> list[float] | None:
    """Convert an optional NumPy vector to a JSON-safe list."""

    return None if values is None else values.tolist()


def chapter_results(
    *, relative_tolerance: float | None = None
) -> dict[str, object]:
    """Return the deterministic results shared by the manuscript and tests."""

    matrix = actuator_sensor_matrix()
    spaces = fundamental_subspaces(
        matrix, relative_tolerance=relative_tolerance
    )
    reachable_target = np.array([2.0, 3.0, 5.0])
    inconsistent_target = np.array([2.0, 3.0, 5.2])
    reachable = linear_system_geometry(
        matrix,
        reachable_target,
        relative_tolerance=spaces.relative_tolerance,
    )
    inconsistent = linear_system_geometry(
        matrix,
        inconsistent_target,
        relative_tolerance=spaces.relative_tolerance,
    )
    first_command = np.array([2.0, 3.0, 0.0, 0.0])
    second_command = np.array([2.0, 2.0, 0.0, 1.0])
    visible_functional = identifiable_functional(
        matrix,
        [1.0, 0.0, 1.0, 0.0],
        relative_tolerance=spaces.relative_tolerance,
    )
    hidden_component = identifiable_functional(
        matrix,
        [0.0, 0.0, 0.0, 1.0],
        relative_tolerance=spaces.relative_tolerance,
    )

    return {
        "schema_version": "1.0",
        "version": "v0.7",
        "chapter": 6,
        "vector_convention": "column_vectors_left_multiplication",
        "randomness": False,
        "external_data": False,
        "actuator_sensor_case": {
            "matrix": matrix.tolist(),
            "matrix_shape": list(matrix.shape),
            "input_labels": ["u1", "u2", "u3", "u4"],
            "output_labels": ["y1", "y2", "y3"],
            "input_unit": "dimensionless_fraction_of_reference_command",
            "output_unit": "dimensionless_calibrated_feature",
            "assumptions": [
                "local_first_order_model",
                "fixed_calibration_point",
                "no_saturation_hysteresis_delay_or_noise",
                "teaching_model_not_a_hardware_safety_decision",
            ],
            "rank": spaces.rank,
            "transpose_rank": spaces.transpose_rank,
            "pivot_columns_zero_based": list(spaces.pivot_columns),
            "free_columns_zero_based": list(spaces.free_columns),
            "dimensions": {
                "column_space": spaces.column_space_basis.shape[1],
                "row_space": spaces.row_space_basis.shape[1],
                "null_space": spaces.null_space_basis.shape[1],
                "left_null_space": spaces.left_null_space_basis.shape[1],
                "input_space": matrix.shape[1],
                "output_space": matrix.shape[0],
            },
            "column_space_basis": spaces.column_space_basis.tolist(),
            "row_space_basis": spaces.row_space_basis.tolist(),
            "null_space_basis": spaces.null_space_basis.tolist(),
            "left_null_space_basis": spaces.left_null_space_basis.tolist(),
            "subspace_residuals_inf": {
                "A_times_null_basis": spaces.null_residual_inf,
                "A_transpose_times_left_null_basis": spaces.left_null_residual_inf,
                "row_basis_transpose_times_null_basis": spaces.row_null_orthogonality_inf,
                "column_basis_transpose_times_left_null_basis": spaces.column_left_null_orthogonality_inf,
            },
            "reachable_target": {
                "target": reachable_target.tolist(),
                "reachable": reachable.reachable,
                "particular_solution": _optional_array(
                    reachable.particular_solution
                ),
                "null_space_basis": reachable.null_space_basis.tolist(),
                "reconstruction_residual_inf": reachable.reconstruction_residual_inf,
                "left_null_coordinates": reachable.left_null_coordinates.tolist(),
                "left_null_certificate_inf": reachable.left_null_certificate_inf,
            },
            "same_output_commands": {
                "first": first_command.tolist(),
                "second": second_command.tolist(),
                "first_output": (matrix @ first_command).tolist(),
                "second_output": (matrix @ second_command).tolist(),
                "difference": (second_command - first_command).tolist(),
            },
            "inconsistent_target": {
                "target": inconsistent_target.tolist(),
                "reachable": inconsistent.reachable,
                "particular_solution": _optional_array(
                    inconsistent.particular_solution
                ),
                "augmented_inconsistency_inf": inconsistent.augmented_inconsistency_inf,
                "left_null_coordinates": inconsistent.left_null_coordinates.tolist(),
                "left_null_certificate_inf": inconsistent.left_null_certificate_inf,
            },
            "identifiable_functionals": {
                "y1_functional": {
                    "vector": [1.0, 0.0, 1.0, 0.0],
                    "identifiable": visible_functional.identifiable,
                    "row_coordinates": _optional_array(
                        visible_functional.row_coordinates
                    ),
                },
                "u4_alone": {
                    "vector": [0.0, 0.0, 0.0, 1.0],
                    "identifiable": hidden_component.identifiable,
                    "row_coordinates": _optional_array(
                        hidden_component.row_coordinates
                    ),
                    "inconsistency_certificate_inf": hidden_component.inconsistency_certificate_inf,
                },
            },
        },
        "numerical_contract": {
            "method": "chapter-5-partial-pivoting-rref-for-small-teaching-examples",
            "relative_tolerance": spaces.relative_tolerance,
            "absolute_tolerance": spaces.absolute_tolerance,
            "transpose_absolute_tolerance": spaces.transpose_absolute_tolerance,
            "basis_orientation": "basis_vectors_are_columns",
            "column_space_rule": "original_pivot_columns_not_rref_columns",
            "limitations": [
                "floating_point_rank_depends_on_scale_and_tolerance",
                "use_qr_or_svd_for_large_noisy_or_ill_scaled_problems",
            ],
        },
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }


def print_human_readable(results: dict[str, object]) -> None:
    """Print a compact, deterministic summary for a student."""

    case = results["actuator_sensor_case"]
    contract = results["numerical_contract"]
    print("Bölüm 6 - Dört Temel Alt Uzay ve Rank")
    print(f"Matris boyutu: {case['matrix_shape'][0]} x {case['matrix_shape'][1]}")
    print(f"Rank: {case['rank']}")
    dimensions = case["dimensions"]
    print(
        "Boyutlar: "
        f"col={dimensions['column_space']}, "
        f"row={dimensions['row_space']}, "
        f"null={dimensions['null_space']}, "
        f"left-null={dimensions['left_null_space']}"
    )
    reachable = case["reachable_target"]
    print(f"Ulaşılabilir hedef: {reachable['reachable']}")
    print(f"Özel çözüm: {reachable['particular_solution']}")
    print(
        "Yeniden kurma artığı (sonsuz norm): "
        f"{reachable['reconstruction_residual_inf']:.3e}"
    )
    inconsistent = case["inconsistent_target"]
    print(f"Tutarsız hedef ulaşılabilir mi: {inconsistent['reachable']}")
    print(
        "Sol-sıfır sertifikası (sonsuz norm): "
        f"{inconsistent['left_null_certificate_inf']:.3e}"
    )
    print(f"Göreli pivot toleransı: {contract['relative_tolerance']:.3e}")
    print(f"Mutlak pivot toleransı: {contract['absolute_tolerance']:.3e}")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse the command-line interface without side effects."""

    parser = argparse.ArgumentParser(
        description="Compute the four fundamental subspaces for Chapter 6."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="write the canonical result as JSON",
    )
    parser.add_argument(
        "--relative-tolerance",
        type=float,
        default=None,
        help="positive relative pivot tolerance; default is recorded",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the canonical Chapter 6 example."""

    args = parse_args(argv)
    try:
        results = chapter_results(relative_tolerance=args.relative_tolerance)
    except VectorSpaceValidationError as error:
        raise SystemExit(f"input validation failed: {error}") from error
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print_human_readable(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

