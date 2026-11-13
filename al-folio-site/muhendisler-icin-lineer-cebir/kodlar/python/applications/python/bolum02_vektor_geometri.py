#!/usr/bin/env python3
"""Deterministic vector geometry examples for Chapter 2.

The scenarios are hypothetical teaching examples. They do not provide flight,
structural, sensor, or safety guidance. No external data or randomness is used.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
from collections.abc import Sequence
from typing import Any

import numpy as np


AIR_VELOCITY_MPS = np.array([12.0, 5.0])
WIND_VELOCITY_MPS = np.array([-4.0, 3.0])
TARGET_DISPLACEMENT_M = np.array([80.0, 60.0])
UPDATE_TIME_S = 10.0


class VectorValidationError(ValueError):
    """Raised when a vector operation has an invalid numerical input."""


def as_finite_vector(
    values: Sequence[float] | np.ndarray, *, name: str
) -> np.ndarray:
    """Return a nonempty, one-dimensional, finite floating-point vector."""

    vector = np.asarray(values, dtype=float)
    if vector.ndim != 1:
        raise VectorValidationError(f"{name} must be one-dimensional")
    if vector.size == 0:
        raise VectorValidationError(f"{name} must not be empty")
    if not np.all(np.isfinite(vector)):
        raise VectorValidationError(f"{name} must contain only finite values")
    return vector


def compatible_vectors(
    left: Sequence[float] | np.ndarray,
    right: Sequence[float] | np.ndarray,
    *,
    left_name: str = "left",
    right_name: str = "right",
) -> tuple[np.ndarray, np.ndarray]:
    """Validate two vectors that must have identical shapes."""

    left_vector = as_finite_vector(left, name=left_name)
    right_vector = as_finite_vector(right, name=right_name)
    if left_vector.shape != right_vector.shape:
        raise VectorValidationError("vectors must have the same shape")
    return left_vector, right_vector


def inner_product(
    left: Sequence[float] | np.ndarray,
    right: Sequence[float] | np.ndarray,
) -> float:
    """Compute the real Euclidean inner product."""

    left_vector, right_vector = compatible_vectors(left, right)
    return float(np.dot(left_vector, right_vector))


def vector_norm(values: Sequence[float] | np.ndarray, order: float = 2.0) -> float:
    """Compute a representable 1-, 2-, or infinity-norm; reject overflow."""

    vector = as_finite_vector(values, name="values")
    if order == 1:
        try:
            length = math.fsum(abs(float(value)) for value in vector)
        except OverflowError as error:
            raise VectorValidationError("the norm exceeds floating-point range") from error
    elif order == 2:
        length = math.hypot(*vector)
    elif order == math.inf:
        length = float(np.max(np.abs(vector)))
    else:
        raise VectorValidationError("order must be 1, 2, or infinity")
    if not math.isfinite(length):
        raise VectorValidationError("the norm exceeds floating-point range")
    return length


def unit_vector(values: Sequence[float] | np.ndarray) -> np.ndarray:
    """Normalize after scaling; only the exact zero vector has no direction."""

    vector = as_finite_vector(values, name="values")
    scale = float(np.max(np.abs(vector)))
    if scale == 0.0:
        raise VectorValidationError("the zero vector has no direction")
    scaled = vector / scale
    return scaled / math.hypot(*scaled)


def euclidean_distance(
    left: Sequence[float] | np.ndarray,
    right: Sequence[float] | np.ndarray,
) -> float:
    """Compute Euclidean distance between compatible vectors."""

    left_vector, right_vector = compatible_vectors(left, right)
    return vector_norm(left_vector - right_vector)


def angle_between(
    left: Sequence[float] | np.ndarray,
    right: Sequence[float] | np.ndarray,
    *,
    degrees: bool = False,
) -> float:
    """Compute the smaller angle from safely normalized Euclidean directions."""

    left_vector, right_vector = compatible_vectors(left, right)
    left_unit = unit_vector(left_vector)
    right_unit = unit_vector(right_vector)
    cosine = math.fsum(float(a) * float(b) for a, b in zip(left_unit, right_unit))
    if not math.isfinite(cosine) or abs(cosine) > 1.0 + 32 * math.ulp(1.0):
        raise VectorValidationError("computed cosine exceeds the roundoff bound")
    safe_cosine = max(-1.0, min(1.0, cosine))
    angle = math.acos(safe_cosine)
    return math.degrees(angle) if degrees else angle


def rms(values: Sequence[float] | np.ndarray) -> float:
    """Compute RMS after scaling, without squaring the original magnitudes."""

    vector = as_finite_vector(values, name="values")
    scale = float(np.max(np.abs(vector)))
    if scale == 0.0:
        return 0.0
    scaled = vector / scale
    mean_square = math.fsum(float(value) ** 2 for value in scaled) / vector.size
    return scale * math.sqrt(mean_square)


def rms_deviation(
    observed: Sequence[float] | np.ndarray,
    reference: Sequence[float] | np.ndarray,
) -> float:
    """Compute RMS of componentwise observation errors."""

    observed_vector, reference_vector = compatible_vectors(
        observed, reference, left_name="observed", right_name="reference"
    )
    return rms(observed_vector - reference_vector)


def scaled_distance(
    left: Sequence[float] | np.ndarray,
    right: Sequence[float] | np.ndarray,
    scales: Sequence[float] | np.ndarray,
) -> float:
    """Compute Euclidean distance after explicit component scaling."""

    left_vector, right_vector = compatible_vectors(left, right)
    scale_vector = as_finite_vector(scales, name="scales")
    if scale_vector.shape != left_vector.shape:
        raise VectorValidationError("scales must match the vector shape")
    if np.any(scale_vector <= 0.0):
        raise VectorValidationError("scales must be strictly positive")
    return vector_norm((left_vector - right_vector) / scale_vector)


def drone_case() -> dict[str, Any]:
    """Return the velocity, direction, position, and target checks."""

    ground_velocity = AIR_VELOCITY_MPS + WIND_VELOCITY_MPS
    predicted_displacement = UPDATE_TIME_S * ground_velocity
    target_error = predicted_displacement - TARGET_DISPLACEMENT_M
    return {
        "name": "wind_affected_inspection_drone",
        "status": "hypothetical_teaching_example_not_flight_guidance",
        "coordinate_order": ["east", "north"],
        "velocity_unit": "m/s",
        "displacement_unit": "m",
        "time_unit": "s",
        "air_velocity_mps": AIR_VELOCITY_MPS.tolist(),
        "wind_velocity_mps": WIND_VELOCITY_MPS.tolist(),
        "ground_velocity_mps": ground_velocity.tolist(),
        "air_speed_mps": vector_norm(AIR_VELOCITY_MPS),
        "wind_speed_mps": vector_norm(WIND_VELOCITY_MPS),
        "ground_speed_mps": vector_norm(ground_velocity),
        "ground_direction_unit": unit_vector(ground_velocity).tolist(),
        "target_displacement_m": TARGET_DISPLACEMENT_M.tolist(),
        "target_distance_m": vector_norm(TARGET_DISPLACEMENT_M),
        "target_direction_unit": unit_vector(TARGET_DISPLACEMENT_M).tolist(),
        "ground_target_angle_deg": angle_between(
            ground_velocity, TARGET_DISPLACEMENT_M, degrees=True
        ),
        "update_time_s": UPDATE_TIME_S,
        "predicted_displacement_m": predicted_displacement.tolist(),
        "target_error_m": target_error.tolist(),
        "target_error_norm_m": vector_norm(target_error),
        "triangle_upper_bound_mps": (
            vector_norm(AIR_VELOCITY_MPS) + vector_norm(WIND_VELOCITY_MPS)
        ),
    }


def geometry_identity_case() -> dict[str, Any]:
    """Return deterministic Cauchy-Schwarz, triangle, and Pythagoras checks."""

    u = np.array([3.0, -4.0, 1.0])
    v = np.array([-2.0, 5.0, 2.0])
    p = np.array([3.0, 4.0])
    q = np.array([-4.0, 3.0])
    cauchy_left = abs(inner_product(u, v))
    cauchy_right = vector_norm(u) * vector_norm(v)
    triangle_left = vector_norm(u + v)
    triangle_right = vector_norm(u) + vector_norm(v)
    pythagoras_left = vector_norm(p + q) ** 2
    pythagoras_right = vector_norm(p) ** 2 + vector_norm(q) ** 2
    return {
        "u": u.tolist(),
        "v": v.tolist(),
        "inner_product": inner_product(u, v),
        "cauchy_left": cauchy_left,
        "cauchy_right": cauchy_right,
        "cauchy_holds": bool(cauchy_left <= cauchy_right + 1e-14),
        "triangle_left": triangle_left,
        "triangle_right": triangle_right,
        "triangle_holds": bool(triangle_left <= triangle_right + 1e-14),
        "orthogonal_p": p.tolist(),
        "orthogonal_q": q.tolist(),
        "orthogonal_dot": inner_product(p, q),
        "pythagoras_left": pythagoras_left,
        "pythagoras_right": pythagoras_right,
        "pythagoras_residual": pythagoras_left - pythagoras_right,
    }


def signal_case() -> dict[str, Any]:
    """Return RMS magnitude and RMS deviation for four voltage samples."""

    reference = np.array([1.0, 2.0, 3.0, 4.0])
    observed = np.array([1.2, 1.8, 3.3, 3.7])
    return {
        "sample_unit": "V",
        "reference_v": reference.tolist(),
        "observed_v": observed.tolist(),
        "reference_rms_v": rms(reference),
        "observed_rms_v": rms(observed),
        "rms_deviation_v": rms_deviation(observed, reference),
    }


def scaled_sensor_case() -> dict[str, Any]:
    """Return a dimensionless sensor distance and a unit-change check."""

    baseline = np.array([20.0, 100.0, 0.4])
    observation = np.array([22.0, 98.0, 0.7])
    scales = np.array([5.0, 10.0, 1.0])
    original_distance = scaled_distance(observation, baseline, scales)

    baseline_pa = baseline.copy()
    observation_pa = observation.copy()
    scales_pa = scales.copy()
    baseline_pa[1] *= 1000.0
    observation_pa[1] *= 1000.0
    scales_pa[1] *= 1000.0
    converted_distance = scaled_distance(observation_pa, baseline_pa, scales_pa)
    return {
        "feature_order": ["temperature", "pressure", "vibration"],
        "original_units": ["degC_difference", "kPa", "mm/s"],
        "baseline": baseline.tolist(),
        "observation": observation.tolist(),
        "reference_scales": scales.tolist(),
        "dimensionless_difference": ((observation - baseline) / scales).tolist(),
        "scaled_distance": original_distance,
        "converted_pressure_unit": "Pa",
        "converted_scaled_distance": converted_distance,
        "unit_conversion_residual": converted_distance - original_distance,
    }


def all_results() -> dict[str, Any]:
    """Return one JSON-compatible result object for the book and tests."""

    return {
        "schema_version": "1.0",
        "chapter": 2,
        "version": "v0.3",
        "randomness": False,
        "external_data": False,
        "drone_case": drone_case(),
        "geometry_identity_case": geometry_identity_case(),
        "signal_case": signal_case(),
        "scaled_sensor_case": scaled_sensor_case(),
        "software": {"python": platform.python_version(), "numpy": np.__version__},
    }


def format_human(results: dict[str, Any]) -> str:
    """Format the main validation results for a terminal reader."""

    drone = results["drone_case"]
    identity = results["geometry_identity_case"]
    signal = results["signal_case"]
    sensor = results["scaled_sensor_case"]
    lines = [
        "Chapter 2 - vector geometry validation",
        f"ground velocity [m/s] = {drone['ground_velocity_mps']}",
        f"ground speed [m/s] = {drone['ground_speed_mps']:.6f}",
        f"target angle [deg] = {drone['ground_target_angle_deg']:.6f}",
        f"target error norm [m] = {drone['target_error_norm_m']:.6f}",
        f"Cauchy-Schwarz holds = {identity['cauchy_holds']}",
        f"triangle inequality holds = {identity['triangle_holds']}",
        f"Pythagoras residual = {identity['pythagoras_residual']:.3e}",
        f"RMS deviation [V] = {signal['rms_deviation_v']:.6f}",
        f"scaled sensor distance = {sensor['scaled_distance']:.6f}",
        f"unit conversion residual = {sensor['unit_conversion_residual']:.3e}",
        "Safety note: hypothetical teaching example only.",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    """Parse the deterministic output mode."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit JSON")
    return parser.parse_args()


def main() -> None:
    """Run all Chapter 2 examples."""

    args = parse_args()
    results = all_results()
    if args.json:
        print(json.dumps(results, indent=2, sort_keys=True))
    else:
        print(format_human(results))


if __name__ == "__main__":
    main()

