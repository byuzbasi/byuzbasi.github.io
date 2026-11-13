#!/usr/bin/env python3
"""Chapter 7: coordinates, basis changes, determinants, and orientation.

The routines are deterministic and designed for small teaching examples.
They keep coordinate direction, units, numerical tolerance, and validation
residuals visible. A determinant is never used here as a stand-alone measure
of conditioning, mesh quality, or engineering safety.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np

from bolum05_vektor_uzaylari import (
    VectorSpaceValidationError,
    as_finite_matrix,
    as_finite_vector,
    validated_relative_tolerance,
)


class CoordinateDeterminantError(VectorSpaceValidationError):
    """Raised when a coordinate or determinant contract is violated."""


@dataclass(frozen=True)
class BasisCoordinatesResult:
    """Coordinates of one vector in a square basis and validation metadata."""

    basis: np.ndarray
    vector: np.ndarray
    coordinates: np.ndarray
    reconstruction: np.ndarray
    residual_inf: float
    condition_2: float
    relative_tolerance: float


@dataclass(frozen=True)
class BasisChangeResult:
    """Two directed basis-change matrices and determinant consistency data."""

    source_basis: np.ndarray
    target_basis: np.ndarray
    source_to_target: np.ndarray
    target_to_source: np.ndarray
    matrix_residual_inf: float
    roundtrip_residual_inf: float
    determinant_source: float | None
    determinant_target: float | None
    determinant_change: float | None
    determinant_ratio_residual: float | None
    condition_source_2: float
    condition_target_2: float
    determinant_source_status: str
    determinant_target_status: str
    determinant_change_status: str
    determinant_ratio: float | None
    determinant_ratio_status: str
    determinant_source_sign: float
    determinant_target_sign: float
    determinant_change_sign: float
    log_abs_determinant_source: float
    log_abs_determinant_target: float
    log_abs_determinant_change: float
    determinant_ratio_sign_matches: bool
    determinant_log_ratio_residual: float


@dataclass(frozen=True)
class OperatorSimilarityResult:
    """One operator in two bases, joined by a directed similarity relation."""

    operator_standard: np.ndarray
    source_representation: np.ndarray
    target_representation: np.ndarray
    source_to_target: np.ndarray
    target_to_source: np.ndarray
    source_action_residual_inf: float
    target_action_residual_inf: float
    similarity_residual_inf: float
    determinant_standard: float
    determinant_source_representation: float
    determinant_target_representation: float


@dataclass(frozen=True)
class DeterminantDiagnostics:
    """Separate structural, scale, rank, and conditioning diagnostics."""

    determinant: float
    sign: float
    log_abs_determinant: float
    numerical_rank: int
    condition_2: float
    normalized_abs_determinant: float
    column_norm_product: float


@dataclass(frozen=True)
class TriangleMapResult:
    """Affine reference-triangle map with orientation and scale diagnostics."""

    vertices: np.ndarray
    jacobian: np.ndarray
    reference_coordinates: np.ndarray
    physical_point: np.ndarray
    recovered_reference_coordinates: np.ndarray | None
    recovery_residual_inf: float | None
    determinant: float | None
    signed_area: float | None
    area: float | None
    scaled_jacobian: float
    condition_2: float | None
    orientation: str
    inside_reference_triangle: bool
    relative_tolerance: float
    determinant_sign: float
    log_abs_determinant: float | None
    determinant_status: str
    log_abs_area: float | None
    area_status: str


def _inf_norm(values: np.ndarray) -> float:
    """Return an infinity norm, including a safe value for empty arrays."""

    if values.size == 0:
        return 0.0
    return float(np.linalg.norm(values, ord=np.inf))


def _as_square_matrix(
    values: Sequence[Sequence[float]] | np.ndarray,
    *,
    name: str,
) -> np.ndarray:
    """Return a finite, nonempty, square floating-point matrix."""

    matrix = as_finite_matrix(values, name=name)
    if matrix.shape[0] != matrix.shape[1]:
        raise CoordinateDeterminantError(
            f"{name} must be square, received shape {matrix.shape}"
        )
    return matrix.copy()


def _finite_condition_or_none(matrix: np.ndarray) -> float | None:
    """Return the 2-norm condition number, replacing infinity by None."""

    value = float(np.linalg.cond(matrix, p=2))
    return value if math.isfinite(value) else None


def _signed_log_value(sign: float, log_abs: float) -> tuple[float | None, str]:
    """Represent a signed log magnitude without confusing range loss with zero."""

    if sign == 0.0:
        return 0.0, "zero"
    if not math.isfinite(sign) or not math.isfinite(log_abs):
        raise CoordinateDeterminantError("signed log magnitude is not finite")
    try:
        magnitude = math.exp(log_abs)
    except OverflowError:
        return None, "overflow"
    if not math.isfinite(magnitude):
        return None, "overflow"
    if magnitude == 0.0:
        return None, "underflow"
    return math.copysign(magnitude, sign), "finite"


def basis_coordinates(
    basis_values: Sequence[Sequence[float]] | np.ndarray,
    vector_values: Sequence[float] | np.ndarray,
    *,
    relative_tolerance: float | None = None,
) -> BasisCoordinatesResult:
    """Solve B c = x for coordinates c without forming an explicit inverse."""

    basis = _as_square_matrix(basis_values, name="basis")
    vector = as_finite_vector(
        vector_values, name="vector", expected_size=basis.shape[0]
    )
    relative = validated_relative_tolerance(relative_tolerance)
    try:
        coordinates = np.linalg.solve(basis, vector)
    except np.linalg.LinAlgError as exc:
        raise CoordinateDeterminantError(
            "basis must be numerically nonsingular for unique coordinates"
        ) from exc
    reconstruction = basis @ coordinates
    residual = _inf_norm(reconstruction - vector)
    return BasisCoordinatesResult(
        basis=basis,
        vector=vector.copy(),
        coordinates=coordinates,
        reconstruction=reconstruction,
        residual_inf=residual,
        condition_2=float(np.linalg.cond(basis, p=2)),
        relative_tolerance=relative,
    )


def basis_change(
    source_basis_values: Sequence[Sequence[float]] | np.ndarray,
    target_basis_values: Sequence[Sequence[float]] | np.ndarray,
) -> BasisChangeResult:
    """Construct P_target<-source from target_basis @ P = source_basis."""

    source = _as_square_matrix(source_basis_values, name="source_basis")
    target = _as_square_matrix(target_basis_values, name="target_basis")
    if source.shape != target.shape:
        raise CoordinateDeterminantError(
            "source_basis and target_basis must have the same shape"
        )
    try:
        source_to_target = np.linalg.solve(target, source)
        target_to_source = np.linalg.solve(source, target)
    except np.linalg.LinAlgError as exc:
        raise CoordinateDeterminantError(
            "both basis matrices must be numerically nonsingular"
        ) from exc

    identity = np.eye(source.shape[0], dtype=float)
    matrix_residual = _inf_norm(target @ source_to_target - source)
    roundtrip_residual = max(
        _inf_norm(source_to_target @ target_to_source - identity),
        _inf_norm(target_to_source @ source_to_target - identity),
    )
    if not (np.all(np.isfinite(source_to_target)) and np.all(np.isfinite(target_to_source))):
        raise CoordinateDeterminantError("basis-change coordinates are not representable")
    sign_source, log_source = map(float, np.linalg.slogdet(source))
    sign_target, log_target = map(float, np.linalg.slogdet(target))
    sign_change, log_change = map(float, np.linalg.slogdet(source_to_target))
    if 0.0 in (sign_source, sign_target, sign_change):
        raise CoordinateDeterminantError("basis-change determinant identity is unresolved")
    log_ratio = log_source - log_target
    sign_ratio = sign_source * sign_target
    determinant_source, source_status = _signed_log_value(sign_source, log_source)
    determinant_target, target_status = _signed_log_value(sign_target, log_target)
    determinant_change, change_status = _signed_log_value(sign_change, log_change)
    determinant_ratio, ratio_status = _signed_log_value(sign_ratio, log_ratio)
    ratio_residual = (
        abs(determinant_change - determinant_ratio)
        if determinant_change is not None and determinant_ratio is not None
        else None
    )
    if ratio_residual is not None and not math.isfinite(ratio_residual):
        ratio_residual = None
    return BasisChangeResult(
        source_basis=source,
        target_basis=target,
        source_to_target=source_to_target,
        target_to_source=target_to_source,
        matrix_residual_inf=matrix_residual,
        roundtrip_residual_inf=roundtrip_residual,
        determinant_source=determinant_source,
        determinant_target=determinant_target,
        determinant_change=determinant_change,
        determinant_ratio_residual=ratio_residual,
        condition_source_2=float(np.linalg.cond(source, p=2)),
        condition_target_2=float(np.linalg.cond(target, p=2)),
        determinant_source_status=source_status,
        determinant_target_status=target_status,
        determinant_change_status=change_status,
        determinant_ratio=determinant_ratio,
        determinant_ratio_status=ratio_status,
        determinant_source_sign=sign_source,
        determinant_target_sign=sign_target,
        determinant_change_sign=sign_change,
        log_abs_determinant_source=log_source,
        log_abs_determinant_target=log_target,
        log_abs_determinant_change=log_change,
        determinant_ratio_sign_matches=sign_change == sign_ratio,
        determinant_log_ratio_residual=abs(log_change - log_ratio),
    )


def operator_in_basis(
    operator_values: Sequence[Sequence[float]] | np.ndarray,
    basis_values: Sequence[Sequence[float]] | np.ndarray,
) -> tuple[np.ndarray, float]:
    """Represent a standard-coordinate operator in one basis using a solve."""

    operator = _as_square_matrix(operator_values, name="operator")
    basis = _as_square_matrix(basis_values, name="basis")
    if operator.shape != basis.shape:
        raise CoordinateDeterminantError(
            "operator and basis must have the same square shape"
        )
    try:
        representation = np.linalg.solve(basis, operator @ basis)
    except np.linalg.LinAlgError as exc:
        raise CoordinateDeterminantError(
            "basis must be numerically nonsingular"
        ) from exc
    residual = _inf_norm(basis @ representation - operator @ basis)
    return representation, residual


def operator_similarity(
    operator_values: Sequence[Sequence[float]] | np.ndarray,
    source_basis_values: Sequence[Sequence[float]] | np.ndarray,
    target_basis_values: Sequence[Sequence[float]] | np.ndarray,
) -> OperatorSimilarityResult:
    """Verify A_target = P_target<-source A_source P_source<-target."""

    operator = _as_square_matrix(operator_values, name="operator")
    change = basis_change(source_basis_values, target_basis_values)
    if operator.shape != change.source_basis.shape:
        raise CoordinateDeterminantError(
            "operator and basis matrices must have the same square shape"
        )
    source_representation, source_residual = operator_in_basis(
        operator, change.source_basis
    )
    target_representation, target_residual = operator_in_basis(
        operator, change.target_basis
    )
    predicted_target = (
        change.source_to_target
        @ source_representation
        @ change.target_to_source
    )
    similarity_residual = _inf_norm(
        target_representation - predicted_target
    )
    return OperatorSimilarityResult(
        operator_standard=operator,
        source_representation=source_representation,
        target_representation=target_representation,
        source_to_target=change.source_to_target,
        target_to_source=change.target_to_source,
        source_action_residual_inf=source_residual,
        target_action_residual_inf=target_residual,
        similarity_residual_inf=similarity_residual,
        determinant_standard=float(np.linalg.det(operator)),
        determinant_source_representation=float(
            np.linalg.det(source_representation)
        ),
        determinant_target_representation=float(
            np.linalg.det(target_representation)
        ),
    )


def determinant_diagnostics(
    matrix_values: Sequence[Sequence[float]] | np.ndarray,
) -> DeterminantDiagnostics:
    """Report determinant, log determinant, rank, and conditioning separately."""

    matrix = _as_square_matrix(matrix_values, name="matrix")
    determinant = float(np.linalg.det(matrix))
    sign, log_abs = np.linalg.slogdet(matrix)
    column_norms = np.linalg.norm(matrix, ord=2, axis=0)
    column_norm_product = float(np.prod(column_norms))
    normalized = (
        abs(determinant) / column_norm_product
        if column_norm_product > 0.0
        else 0.0
    )
    return DeterminantDiagnostics(
        determinant=determinant,
        sign=float(sign),
        log_abs_determinant=float(log_abs),
        numerical_rank=int(np.linalg.matrix_rank(matrix)),
        condition_2=float(np.linalg.cond(matrix, p=2)),
        normalized_abs_determinant=normalized,
        column_norm_product=column_norm_product,
    )


def affine_triangle_map(
    vertex_values: Sequence[Sequence[float]] | np.ndarray,
    reference_coordinate_values: Sequence[float] | np.ndarray,
    *,
    relative_tolerance: float | None = None,
) -> TriangleMapResult:
    """Map one reference coordinate through a two-dimensional affine triangle."""

    vertices = as_finite_matrix(vertex_values, name="vertices")
    if vertices.shape != (3, 2):
        raise CoordinateDeterminantError(
            f"vertices must have shape (3, 2), received {vertices.shape}"
        )
    reference = as_finite_vector(
        reference_coordinate_values,
        name="reference_coordinates",
        expected_size=2,
    )
    relative = validated_relative_tolerance(relative_tolerance)
    try:
        with np.errstate(over="raise", invalid="raise"):
            jacobian = np.column_stack(
                (vertices[1] - vertices[0], vertices[2] - vertices[0])
            )
    except FloatingPointError as exc:
        raise CoordinateDeterminantError("triangle edge difference is not representable") from exc
    column_scales = np.max(np.abs(jacobian), axis=0)
    if np.any(column_scales == 0.0):
        scaled_jacobian = 0.0
        sign, log_abs = 0.0, -math.inf
    else:
        scaled_edges = jacobian / column_scales
        scaled_norms = np.linalg.norm(scaled_edges, ord=2, axis=0)
        unit_edges = scaled_edges / scaled_norms
        scaled_jacobian = float(np.linalg.det(unit_edges))
        sign, log_unit = map(float, np.linalg.slogdet(unit_edges))
        log_abs = (
            log_unit + float(np.sum(np.log(column_scales) + np.log(scaled_norms)))
            if sign != 0.0 else -math.inf
        )
    if not math.isfinite(scaled_jacobian):
        raise CoordinateDeterminantError("scaled triangle Jacobian is not finite")
    determinant, determinant_status = _signed_log_value(sign, log_abs)
    log_area = log_abs - math.log(2.0)
    signed_area, area_status = _signed_log_value(sign, log_area)
    if abs(scaled_jacobian) <= relative:
        orientation = "degenerate_to_tolerance"
    elif scaled_jacobian > 0.0:
        orientation = "counterclockwise"
    else:
        orientation = "clockwise"

    try:
        with np.errstate(over="raise", invalid="raise"):
            physical_point = vertices[0] + jacobian @ reference
    except FloatingPointError as exc:
        raise CoordinateDeterminantError("triangle physical point is not representable") from exc
    recovered: np.ndarray | None = None
    recovery_residual: float | None = None
    if orientation != "degenerate_to_tolerance":
        try:
            recovered = np.linalg.solve(
                jacobian, physical_point - vertices[0]
            )
            recovery_residual = _inf_norm(recovered - reference)
        except np.linalg.LinAlgError:
            recovered = None
            recovery_residual = None

    inside = bool(
        np.all(reference >= -relative)
        and float(np.sum(reference)) <= 1.0 + relative
    )
    return TriangleMapResult(
        vertices=vertices.copy(),
        jacobian=jacobian,
        reference_coordinates=reference.copy(),
        physical_point=physical_point,
        recovered_reference_coordinates=recovered,
        recovery_residual_inf=recovery_residual,
        determinant=determinant,
        signed_area=signed_area,
        area=abs(signed_area) if signed_area is not None else None,
        scaled_jacobian=scaled_jacobian,
        condition_2=_finite_condition_or_none(jacobian),
        orientation=orientation,
        inside_reference_triangle=inside,
        relative_tolerance=relative,
        determinant_sign=sign,
        log_abs_determinant=log_abs if sign != 0.0 else None,
        determinant_status=determinant_status,
        log_abs_area=log_area if sign != 0.0 else None,
        area_status=area_status,
    )


def rotation_matrix_2d(angle_radians: float) -> np.ndarray:
    """Return the standard two-dimensional proper rotation matrix."""

    angle = float(angle_radians)
    if not math.isfinite(angle):
        raise CoordinateDeterminantError("angle_radians must be finite")
    cosine = math.cos(angle)
    sine = math.sin(angle)
    return np.array([[cosine, -sine], [sine, cosine]], dtype=float)


def canonical_bases() -> tuple[np.ndarray, np.ndarray]:
    """Return the two exact bases used in the chapter's coordinate example."""

    source = np.array([[2.0, 1.0], [1.0, 2.0]], dtype=float)
    target = np.array([[1.0, -1.0], [1.0, 1.0]], dtype=float)
    return source, target


def main_triangle_vertices() -> np.ndarray:
    """Return the physical vertices, in metres, of the main affine triangle."""

    return np.array(
        [[100.0, 50.0], [104.0, 51.0], [101.0, 53.0]], dtype=float
    )


def determinant_condition_counterexamples() -> dict[str, Any]:
    """Build two matrices that separate determinant size from conditioning."""

    small_determinant = np.diag([1.0e-10, 1.0e-10])
    unit_determinant = np.diag([1.0e10, 1.0e-10])
    small = determinant_diagnostics(small_determinant)
    unit = determinant_diagnostics(unit_determinant)
    return {
        "small_determinant_well_conditioned": {
            "matrix": small_determinant,
            "determinant": small.determinant,
            "condition_2": small.condition_2,
            "message": "small determinant does not imply poor conditioning",
        },
        "unit_determinant_ill_conditioned": {
            "matrix": unit_determinant,
            "determinant": unit.determinant,
            "condition_2": unit.condition_2,
            "message": "unit determinant does not imply good conditioning",
        },
    }


def determinant_underflow_example(dimension: int = 400) -> dict[str, Any]:
    """Compare det and slogdet on a scaled identity with a tiny determinant."""

    if not isinstance(dimension, int) or isinstance(dimension, bool):
        raise CoordinateDeterminantError("dimension must be an integer")
    if dimension < 1 or dimension > 600:
        raise CoordinateDeterminantError(
            "dimension must be between 1 and 600 for this teaching example"
        )
    matrix = 0.1 * np.eye(dimension, dtype=float)
    determinant = float(np.linalg.det(matrix))
    sign, log_abs = np.linalg.slogdet(matrix)
    return {
        "dimension": dimension,
        "diagonal_value": 0.1,
        "determinant": determinant,
        "sign": float(sign),
        "log_abs_determinant": float(log_abs),
        "analytic_log_abs_determinant": float(dimension * math.log(0.1)),
    }


def _json_ready(value: Any) -> Any:
    """Convert dataclasses, arrays, and NumPy scalars to strict JSON values."""

    if hasattr(value, "__dataclass_fields__"):
        return {
            field: _json_ready(getattr(value, field))
            for field in value.__dataclass_fields__
        }
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def chapter_results(
    *,
    relative_tolerance: float | None = None,
) -> dict[str, Any]:
    """Return the complete deterministic Chapter 7 validation record."""

    relative = validated_relative_tolerance(relative_tolerance)
    source_basis, target_basis = canonical_bases()
    source_coordinates = np.array([2.0, -1.0], dtype=float)
    vector = source_basis @ source_coordinates
    target_coordinate_result = basis_coordinates(
        target_basis, vector, relative_tolerance=relative
    )
    change = basis_change(source_basis, target_basis)
    operator = np.array([[2.0, 1.0], [0.0, 1.0]], dtype=float)
    similarity = operator_similarity(operator, source_basis, target_basis)

    vertices = main_triangle_vertices()
    reference = np.array([0.25, 0.50], dtype=float)
    main_triangle = affine_triangle_map(
        vertices, reference, relative_tolerance=relative
    )
    reversed_triangle = affine_triangle_map(
        vertices[[0, 2, 1], :], reference, relative_tolerance=relative
    )
    flat_vertices = vertices.copy()
    flat_vertices[2] = vertices[0] + 0.5 * (vertices[1] - vertices[0])
    flat_triangle = affine_triangle_map(
        flat_vertices, reference, relative_tolerance=relative
    )

    rotation = rotation_matrix_2d(math.pi / 6.0)
    reflection = np.diag([1.0, -1.0])
    rotation_orthogonality_residual = _inf_norm(
        rotation.T @ rotation - np.eye(2)
    )

    results = {
        "schema_version": "1.1",
        "version": "v0.8",
        "chapter": 7,
        "vector_convention": "column_vectors_left_multiplication",
        "basis_change_convention": "P_target_from_source_maps_source_coordinates_to_target_coordinates",
        "units": {
            "main_triangle_vertices": "metre",
            "reference_coordinates": "dimensionless",
            "jacobian_columns": "metre_per_reference_coordinate",
            "jacobian_determinant": "square_metre",
            "scaled_jacobian": "dimensionless",
        },
        "assumptions": [
            "two-dimensional affine triangle",
            "fixed Cartesian physical frame",
            "constant Jacobian over the teaching element",
            "finite floating-point inputs",
            "orientation decision uses a scale-normalized tolerance",
            "not a mesh acceptance or engineering safety calculation",
        ],
        "relative_tolerance": relative,
        "coordinate_case": {
            "source_basis": source_basis,
            "target_basis": target_basis,
            "source_coordinates": source_coordinates,
            "geometric_vector": vector,
            "target_coordinates": target_coordinate_result.coordinates,
            "target_coordinate_residual_inf": target_coordinate_result.residual_inf,
            "basis_change": change,
            "coordinates_via_change": change.source_to_target
            @ source_coordinates,
        },
        "operator_similarity_case": similarity,
        "triangle_case": {
            "main": main_triangle,
            "reversed_node_order": reversed_triangle,
            "flat": flat_triangle,
            "translation_invariance_check": affine_triangle_map(
                vertices + np.array([250.0, -75.0]),
                reference,
                relative_tolerance=relative,
            ),
        },
        "orientation_case": {
            "rotation_30_degrees": rotation,
            "rotation_determinant": float(np.linalg.det(rotation)),
            "rotation_orthogonality_residual_inf": rotation_orthogonality_residual,
            "reflection_x_axis": reflection,
            "reflection_determinant": float(np.linalg.det(reflection)),
        },
        "conditioning_counterexamples": determinant_condition_counterexamples(),
        "underflow_case": determinant_underflow_example(),
        "randomness": False,
        "external_data": False,
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }
    return _json_ready(results)


def print_human_readable(results: dict[str, Any]) -> None:
    """Print a concise Turkish summary of the canonical results."""

    coordinate = results["coordinate_case"]
    triangle = results["triangle_case"]
    main = triangle["main"]
    reversed_case = triangle["reversed_node_order"]
    flat = triangle["flat"]
    counterexamples = results["conditioning_counterexamples"]
    underflow = results["underflow_case"]
    print("Bölüm 7 - Koordinatlar, Baz Değişimi ve Determinant")
    print(f"Geometrik vektör: {coordinate['geometric_vector']}")
    print(f"B-bazı koordinatları: {coordinate['source_coordinates']}")
    print(f"C-bazı koordinatları: {coordinate['target_coordinates']}")
    print(f"Ana üçgen Jakobeni: {main['jacobian']}")
    print(
        "Ana üçgen: "
        f"det={main['determinant']:.12g} m^2, "
        f"alan={main['area']:.12g} m^2, "
        f"yönelim={main['orientation']}"
    )
    print(
        "Ters düğüm sırası: "
        f"det={reversed_case['determinant']:.12g} m^2, "
        f"alan={reversed_case['area']:.12g} m^2, "
        f"yönelim={reversed_case['orientation']}"
    )
    print(f"Düz eleman yönelimi: {flat['orientation']}")
    print(
        "Küçük determinant örneği: "
        f"det={counterexamples['small_determinant_well_conditioned']['determinant']:.3e}, "
        f"kappa2={counterexamples['small_determinant_well_conditioned']['condition_2']:.3e}"
    )
    print(
        "Birim determinant örneği: "
        f"det={counterexamples['unit_determinant_ill_conditioned']['determinant']:.3e}, "
        f"kappa2={counterexamples['unit_determinant_ill_conditioned']['condition_2']:.3e}"
    )
    print(
        "Alt-taşma örneği: "
        f"det={underflow['determinant']}, "
        f"işaret={underflow['sign']}, "
        f"log|det|={underflow['log_abs_determinant']:.6f}"
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line options for human-readable or JSON output."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the deterministic validation record as JSON.",
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
        help="Positive scale-normalized orientation tolerance.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the canonical Chapter 7 example."""

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
