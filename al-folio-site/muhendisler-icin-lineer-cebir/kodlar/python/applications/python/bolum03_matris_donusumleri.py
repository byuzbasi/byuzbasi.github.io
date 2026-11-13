#!/usr/bin/env python3
"""Chapter 3 companion: safe matrix and planar transformation calculations.

The examples are deterministic and educational.  The warehouse-robot case is
not navigation, collision-avoidance, calibration, or safety software.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
from collections.abc import Sequence
from typing import Any

import numpy as np


VERSION = "v0.4"
CHAPTER = 3
SENSOR_POINT_M = np.array([2.0, 1.0])
SENSOR_FORWARD = np.array([1.0, 0.0])
SENSOR_IN_BODY_TRANSLATION_M = np.array([0.5, 0.2])
BODY_IN_MAP_TRANSLATION_M = np.array([4.0, 3.0])
SENSOR_IN_BODY_ANGLE_RAD = math.radians(90.0)
BODY_IN_MAP_ANGLE_RAD = math.radians(30.0)
NUMERICAL_ATOL = 1.0e-12


class MatrixValidationError(ValueError):
    """Raised when a matrix or transformation violates its stated contract."""


def as_finite_vector(
    values: Sequence[float] | np.ndarray,
    *,
    name: str = "vector",
    expected_size: int | None = None,
) -> np.ndarray:
    """Return a nonempty one-dimensional finite floating-point vector."""

    vector = np.asarray(values, dtype=float)
    if vector.ndim != 1:
        raise MatrixValidationError(f"{name} must be one-dimensional")
    if vector.size == 0:
        raise MatrixValidationError(f"{name} must not be empty")
    if not np.all(np.isfinite(vector)):
        raise MatrixValidationError(f"{name} must contain only finite values")
    if expected_size is not None and vector.size != expected_size:
        raise MatrixValidationError(
            f"{name} must have length {expected_size}, received {vector.size}"
        )
    return vector


def as_finite_matrix(
    values: Sequence[Sequence[float]] | np.ndarray,
    *,
    name: str = "matrix",
    expected_shape: tuple[int, int] | None = None,
) -> np.ndarray:
    """Return a nonempty two-dimensional finite floating-point matrix."""

    matrix = np.asarray(values, dtype=float)
    if matrix.ndim != 2:
        raise MatrixValidationError(f"{name} must be two-dimensional")
    if matrix.shape[0] == 0 or matrix.shape[1] == 0:
        raise MatrixValidationError(f"{name} must not have an empty dimension")
    if not np.all(np.isfinite(matrix)):
        raise MatrixValidationError(f"{name} must contain only finite values")
    if expected_shape is not None and matrix.shape != expected_shape:
        raise MatrixValidationError(
            f"{name} must have shape {expected_shape}, received {matrix.shape}"
        )
    return matrix


def matrix_vector_product(
    matrix_values: Sequence[Sequence[float]] | np.ndarray,
    vector_values: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Compute A @ x after enforcing the explicit two-dimensional contract."""

    matrix = as_finite_matrix(matrix_values, name="matrix")
    vector = as_finite_vector(vector_values, name="vector")
    if matrix.shape[1] != vector.size:
        raise MatrixValidationError(
            "matrix columns must equal vector length: "
            f"{matrix.shape[1]} != {vector.size}"
        )
    return matrix @ vector


def matrix_product(
    left_values: Sequence[Sequence[float]] | np.ndarray,
    right_values: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """Compute A @ B without permitting implicit batch broadcasting."""

    left = as_finite_matrix(left_values, name="left matrix")
    right = as_finite_matrix(right_values, name="right matrix")
    if left.shape[1] != right.shape[0]:
        raise MatrixValidationError(
            "left columns must equal right rows: "
            f"{left.shape[1]} != {right.shape[0]}"
        )
    return left @ right


def rotation_matrix_2d(angle_rad: float) -> np.ndarray:
    """Return the active counterclockwise planar rotation for a radian angle."""

    angle = float(angle_rad)
    if not math.isfinite(angle):
        raise MatrixValidationError("angle_rad must be finite")
    cosine = math.cos(angle)
    sine = math.sin(angle)
    return np.array([[cosine, -sine], [sine, cosine]], dtype=float)


def scaling_matrix_2d(scale_x: float, scale_y: float) -> np.ndarray:
    """Return an axis-aligned planar scaling matrix, allowing a zero scale."""

    scales = as_finite_vector([scale_x, scale_y], name="scales", expected_size=2)
    return np.diag(scales)


def reflection_x_axis_2d() -> np.ndarray:
    """Return the reflection that keeps x and reverses y."""

    return np.array([[1.0, 0.0], [0.0, -1.0]])


def horizontal_shear_2d(factor: float) -> np.ndarray:
    """Return the shear (x, y) -> (x + factor*y, y)."""

    shear = float(factor)
    if not math.isfinite(shear):
        raise MatrixValidationError("shear factor must be finite")
    return np.array([[1.0, shear], [0.0, 1.0]])


def affine_transform_2d(
    linear_values: Sequence[Sequence[float]] | np.ndarray,
    translation_values: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Embed x -> A x + t in a 3 by 3 homogeneous affine matrix."""

    linear = as_finite_matrix(
        linear_values, name="linear block", expected_shape=(2, 2)
    )
    translation = as_finite_vector(
        translation_values, name="translation", expected_size=2
    )
    transform = np.eye(3, dtype=float)
    transform[:2, :2] = linear
    transform[:2, 2] = translation
    return transform


def rigid_transform_2d(
    angle_rad: float,
    translation_values: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Return a planar rotation followed by a translation."""

    return affine_transform_2d(
        rotation_matrix_2d(angle_rad), translation_values
    )


def as_affine_transform_2d(
    values: Sequence[Sequence[float]] | np.ndarray,
    *,
    name: str = "transform",
) -> np.ndarray:
    """Require the exact affine final row [0, 0, 1]; do not repair inputs."""

    transform = as_finite_matrix(values, name=name, expected_shape=(3, 3))
    if not np.array_equal(transform[2, :], [0.0, 0.0, 1.0]):
        raise MatrixValidationError(f"{name} must have exact final row [0, 0, 1]")
    return transform


def homogeneous_point_2d(
    point_values: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Return [x, y, 1] for a two-dimensional point."""

    point = as_finite_vector(point_values, name="point", expected_size=2)
    return np.array([point[0], point[1], 1.0])


def homogeneous_direction_2d(
    direction_values: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Return [vx, vy, 0] for a free direction vector."""

    direction = as_finite_vector(
        direction_values, name="direction", expected_size=2
    )
    return np.array([direction[0], direction[1], 0.0])


def transform_point_2d(
    transform_values: Sequence[Sequence[float]] | np.ndarray,
    point_values: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Apply an affine transform to a point and return ordinary coordinates."""

    transform = as_affine_transform_2d(transform_values)
    result = transform @ homogeneous_point_2d(point_values)
    if abs(result[2]) <= NUMERICAL_ATOL:
        raise MatrixValidationError("transformed point has a zero homogeneous scale")
    return result[:2] / result[2]


def transform_direction_2d(
    transform_values: Sequence[Sequence[float]] | np.ndarray,
    direction_values: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Apply only the linear block of an affine transform to a direction."""

    transform = as_affine_transform_2d(transform_values)
    result = transform @ homogeneous_direction_2d(direction_values)
    if abs(result[2]) > NUMERICAL_ATOL:
        raise MatrixValidationError("an affine direction must retain homogeneous zero")
    return result[:2]


def transform_points_2d(
    transform_values: Sequence[Sequence[float]] | np.ndarray,
    points_values: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """Transform an explicit n by 2 point table without batch broadcasting."""

    transform = as_affine_transform_2d(transform_values)
    points = as_finite_matrix(points_values, name="points")
    if points.shape[1] != 2:
        raise MatrixValidationError("points must have shape (n, 2)")
    homogeneous = np.column_stack((points, np.ones(points.shape[0], dtype=float)))
    transformed = (transform @ homogeneous.T).T
    scales = transformed[:, 2]
    if np.any(np.abs(scales) <= NUMERICAL_ATOL):
        raise MatrixValidationError("a transformed point has zero homogeneous scale")
    return transformed[:, :2] / scales[:, None]


def compose_affine_2d(
    outer_values: Sequence[Sequence[float]] | np.ndarray,
    inner_values: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """Return outer @ inner, so inner acts first on a column point."""

    outer = as_affine_transform_2d(outer_values, name="outer transform")
    inner = as_affine_transform_2d(inner_values, name="inner transform")
    return outer @ inner


def rigid_inverse_2d(
    transform_values: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """Use the special [R.T, -R.T@t] formula for a rigid transform."""

    transform = as_affine_transform_2d(transform_values)
    rotation = transform[:2, :2]
    translation = transform[:2, 2]
    if not np.allclose(
        rotation.T @ rotation,
        np.eye(2),
        rtol=0.0,
        atol=NUMERICAL_ATOL,
    ):
        raise MatrixValidationError("linear block must be orthogonal")
    inverse = np.eye(3, dtype=float)
    inverse[:2, :2] = rotation.T
    inverse[:2, 2] = -(rotation.T @ translation)
    return inverse


def linearity_case() -> dict[str, Any]:
    """Check superposition for a matrix map and expose an affine counterexample."""

    matrix = np.array([[2.0, -1.0], [0.5, 3.0]])
    x = np.array([1.0, 2.0])
    z = np.array([-2.0, 1.0])
    alpha = 1.5
    beta = -0.25
    left = matrix @ (alpha * x + beta * z)
    right = alpha * (matrix @ x) + beta * (matrix @ z)
    translation = np.array([3.0, -1.0])
    affine_zero = matrix @ np.zeros(2) + translation
    return {
        "matrix": matrix,
        "alpha": alpha,
        "beta": beta,
        "x": x,
        "z": z,
        "superposition_left": left,
        "superposition_right": right,
        "superposition_residual_2norm": float(np.linalg.norm(left - right)),
        "affine_translation": translation,
        "affine_image_of_zero": affine_zero,
    }


def rotation_identity_case() -> dict[str, Any]:
    """Measure the inner-product and norm invariants of a planar rotation."""

    rotation = rotation_matrix_2d(math.radians(37.0))
    x = np.array([3.0, -4.0])
    z = np.array([2.0, 5.0])
    rotated_x = rotation @ x
    rotated_z = rotation @ z
    orthogonality_residual = rotation.T @ rotation - np.eye(2)
    return {
        "angle_deg": 37.0,
        "rotation": rotation,
        "orthogonality_residual_fro": float(
            np.linalg.norm(orthogonality_residual, ord="fro")
        ),
        "input_norm": float(np.linalg.norm(x)),
        "output_norm": float(np.linalg.norm(rotated_x)),
        "norm_residual": float(np.linalg.norm(rotated_x) - np.linalg.norm(x)),
        "input_inner_product": float(x @ z),
        "output_inner_product": float(rotated_x @ rotated_z),
        "inner_product_residual": float((rotated_x @ rotated_z) - (x @ z)),
    }


def order_case() -> dict[str, Any]:
    """Show that rotation and translation do not commute."""

    point = np.array([1.0, 0.0])
    rotation = rigid_transform_2d(math.pi / 2.0, [0.0, 0.0])
    translation = affine_transform_2d(np.eye(2), [2.0, 0.0])
    rotate_then_translate = compose_affine_2d(translation, rotation)
    translate_then_rotate = compose_affine_2d(rotation, translation)
    first_result = transform_point_2d(rotate_then_translate, point)
    second_result = transform_point_2d(translate_then_rotate, point)
    return {
        "point": point,
        "rotate_then_translate_matrix": rotate_then_translate,
        "translate_then_rotate_matrix": translate_then_rotate,
        "rotate_then_translate_point": first_result,
        "translate_then_rotate_point": second_result,
        "order_gap_2norm": float(np.linalg.norm(first_result - second_result)),
    }


def _split_homogeneous_residual(
    difference_values: Sequence[float] | np.ndarray,
) -> tuple[float, float]:
    """Separate a planar coordinate residual from dimensionless homogeneous error.

    The first result has the supplied length unit; the second has no unit.
    The frame-chain example supplies the first two coordinates in metres.
    """

    difference = as_finite_vector(
        difference_values, name="homogeneous difference", expected_size=3
    )
    physical_residual = math.hypot(*difference[:2])
    if not math.isfinite(physical_residual):
        raise MatrixValidationError("physical residual exceeds floating-point range")
    return physical_residual, abs(float(difference[2]))


def frame_chain_case() -> dict[str, Any]:
    """Transform a LiDAR point from sensor to body to map coordinates."""

    transform_body_sensor = rigid_transform_2d(
        SENSOR_IN_BODY_ANGLE_RAD, SENSOR_IN_BODY_TRANSLATION_M
    )
    transform_map_body = rigid_transform_2d(
        BODY_IN_MAP_ANGLE_RAD, BODY_IN_MAP_TRANSLATION_M
    )
    transform_map_sensor = compose_affine_2d(
        transform_map_body, transform_body_sensor
    )
    point_body = transform_point_2d(transform_body_sensor, SENSOR_POINT_M)
    point_map_sequential = transform_point_2d(transform_map_body, point_body)
    point_map_composite = transform_point_2d(
        transform_map_sensor, SENSOR_POINT_M
    )
    direction_map = transform_direction_2d(
        transform_map_sensor, SENSOR_FORWARD
    )
    transform_sensor_map = rigid_inverse_2d(transform_map_sensor)
    recovered_sensor_point = transform_point_2d(
        transform_sensor_map, point_map_composite
    )
    homogeneous_sensor_point = homogeneous_point_2d(SENSOR_POINT_M)
    composition_difference = (
        transform_map_body @ (transform_body_sensor @ homogeneous_sensor_point)
        - transform_map_sensor @ homogeneous_sensor_point
    )
    round_trip_difference = (
        transform_sensor_map @ (transform_map_sensor @ homogeneous_sensor_point)
        - homogeneous_sensor_point
    )
    composition_residual_m, composition_homogeneous_residual = (
        _split_homogeneous_residual(composition_difference)
    )
    round_trip_residual_m, round_trip_homogeneous_residual = (
        _split_homogeneous_residual(round_trip_difference)
    )
    return {
        "sensor_point_m": SENSOR_POINT_M,
        "sensor_forward_unit": SENSOR_FORWARD,
        "transform_body_sensor": transform_body_sensor,
        "transform_map_body": transform_map_body,
        "transform_map_sensor": transform_map_sensor,
        "point_body_m": point_body,
        "point_map_sequential_m": point_map_sequential,
        "point_map_composite_m": point_map_composite,
        "composition_residual_m": composition_residual_m,
        "composition_homogeneous_residual": composition_homogeneous_residual,
        "sensor_forward_in_map_unit": direction_map,
        "direction_norm_residual": float(np.linalg.norm(direction_map) - 1.0),
        "transform_sensor_map": transform_sensor_map,
        "recovered_sensor_point_m": recovered_sensor_point,
        "round_trip_residual_m": round_trip_residual_m,
        "round_trip_homogeneous_residual": round_trip_homogeneous_residual,
    }


def graphics_case() -> dict[str, Any]:
    """Apply scale, rotation, and translation to an original rectangular profile."""

    profile = np.array([[0.0, 0.0], [2.0, 0.0], [2.0, 1.0], [0.0, 1.0]])
    scale = affine_transform_2d(scaling_matrix_2d(1.5, 0.5), [0.0, 0.0])
    rotate = rigid_transform_2d(math.radians(30.0), [0.0, 0.0])
    translate = affine_transform_2d(np.eye(2), [3.0, -1.0])
    pipeline = compose_affine_2d(
        translate, compose_affine_2d(rotate, scale)
    )
    transformed = transform_points_2d(pipeline, profile)
    centroid = np.mean(transformed, axis=0)
    return {
        "profile_points": profile,
        "pipeline_matrix": pipeline,
        "transformed_points": transformed,
        "transformed_centroid": centroid,
    }


def _json_ready(value: Any) -> Any:
    """Convert NumPy values recursively to ordinary JSON-compatible values."""

    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


def all_results() -> dict[str, Any]:
    """Return every deterministic chapter result with provenance metadata."""

    return _json_ready(
        {
            "schema_version": "1.0",
            "version": VERSION,
            "chapter": CHAPTER,
            "application": "warehouse_robot_frame_chain",
            "angle_convention": "radians_internal_counterclockwise_positive",
            "vector_convention": "column_vectors_left_multiplication",
            "frame_convention": "T_ab_maps_b_coordinates_to_a_coordinates",
            "randomness": False,
            "external_data": False,
            "safety_scope": "educational_not_navigation_or_collision_avoidance",
            "linearity_case": linearity_case(),
            "rotation_identity_case": rotation_identity_case(),
            "order_case": order_case(),
            "frame_chain_case": frame_chain_case(),
            "graphics_case": graphics_case(),
            "software": {"python": platform.python_version(), "numpy": np.__version__},
        }
    )


def format_human(results: dict[str, Any]) -> str:
    """Format the principal results and their limits for a human reader."""

    frame = results["frame_chain_case"]
    order = results["order_case"]
    rotation = results["rotation_identity_case"]
    lines = [
        "Bölüm 3 - Matrisler ve Dönüşümler",
        "Sözleşme: sütun vektörü, soldan çarpım; T_ab, b'den a'ya taşır.",
        f"Sensör noktası [m]: {frame['sensor_point_m']}",
        f"Gövde çerçevesindeki nokta [m]: {frame['point_body_m']}",
        f"Harita çerçevesindeki nokta [m]: {frame['point_map_composite_m']}",
        (
            "Bileşik-ardışık farkı [m]: "
            f"{frame['composition_residual_m']:.3e}"
        ),
        (
            "İleri-geri dönüşüm farkı [m]: "
            f"{frame['round_trip_residual_m']:.3e}"
        ),
        (
            "Homojen yapı artıkları [boyutsuz], bileşim / çevrim: "
            f"{frame['composition_homogeneous_residual']:.3e} / "
            f"{frame['round_trip_homogeneous_residual']:.3e}"
        ),
        (
            "Sıra karşı örneği: dön-sonra-ötele = "
            f"{order['rotate_then_translate_point']}, "
            "ötele-sonra-dön = "
            f"{order['translate_then_rotate_point']}"
        ),
        (
            "Dönme ortogonallik artığı (Frobenius): "
            f"{rotation['orthogonality_residual_fro']:.3e}"
        ),
        "Kullanım sınırı: Bu çıktı gerçek navigasyon veya güvenlik kararı değildir.",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    """Parse the deterministic output mode."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON output."
    )
    return parser.parse_args()


def main() -> None:
    """Run the chapter application without changing external state."""

    arguments = parse_args()
    results = all_results()
    if arguments.json:
        print(json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(format_human(results))


if __name__ == "__main__":
    main()
