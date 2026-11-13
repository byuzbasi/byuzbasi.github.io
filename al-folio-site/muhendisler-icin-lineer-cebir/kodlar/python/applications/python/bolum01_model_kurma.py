#!/usr/bin/env python3
"""Examples for constructing and validating linear models in Chapter 1.

This module is the sole computational source for the illustrative three-sensor
model. Its coefficients do not represent a real device and cannot support a
safety, calibration, or design decision. It uses no external data or randomness.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable, Sequence
from typing import Any

import numpy as np


SENSITIVITY_V_PER_INPUT = np.array(
    [
        [0.080, 0.010, -0.002],
        [0.015, 0.120, 0.004],
        [-0.010, 0.020, 0.050],
    ],
    dtype=float,
)
OFFSET_V = np.array([0.20, -0.10, 0.05], dtype=float)
STATE_CHANGE = np.array([10.0, 5.0, 20.0], dtype=float)
STATE_SCALE = np.array([10.0, 5.0, 20.0], dtype=float)
VALID_ABSOLUTE_CHANGE = np.array([12.0, 8.0, 25.0], dtype=float)

STATE_NAMES = ("temperature_change", "pressure_change", "humidity_change")
STATE_UNITS = ("degC_difference", "kPa", "percent_RH_difference")
OUTPUT_NAMES = ("sensor_1", "sensor_2", "sensor_3")
OUTPUT_UNITS = ("V", "V", "V")
COEFFICIENT_UNITS = (
    ("V/degC_difference", "V/kPa", "V/percent_RH_difference"),
    ("V/degC_difference", "V/kPa", "V/percent_RH_difference"),
    ("V/degC_difference", "V/kPa", "V/percent_RH_difference"),
)


class ModelValidationError(ValueError):
    """Raised when model dimensions or numerical inputs are invalid."""


def _as_finite_vector(values: Sequence[float] | np.ndarray, *, name: str) -> np.ndarray:
    vector = np.asarray(values, dtype=float)
    if vector.ndim != 1:
        raise ModelValidationError(f"{name} must be one-dimensional")
    if vector.size == 0:
        raise ModelValidationError(f"{name} must not be empty")
    if not np.all(np.isfinite(vector)):
        raise ModelValidationError(f"{name} must contain only finite values")
    return vector


def validate_linear_model(
    matrix: Sequence[Sequence[float]] | np.ndarray,
    state: Sequence[float] | np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return a finite 2-D matrix A and a compatible vector x for A @ x."""

    model_matrix = np.asarray(matrix, dtype=float)
    state_vector = _as_finite_vector(state, name="state")
    if model_matrix.ndim != 2:
        raise ModelValidationError("matrix must be two-dimensional")
    if 0 in model_matrix.shape:
        raise ModelValidationError("matrix dimensions must be positive")
    if not np.all(np.isfinite(model_matrix)):
        raise ModelValidationError("matrix must contain only finite values")
    if model_matrix.shape[1] != state_vector.size:
        raise ModelValidationError(
            "matrix column count must equal the state vector length"
        )
    return model_matrix, state_vector


def linear_output(
    matrix: Sequence[Sequence[float]] | np.ndarray,
    state: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Compute the linear output y = A @ x for a fixed matrix A."""

    model_matrix, state_vector = validate_linear_model(matrix, state)
    return model_matrix @ state_vector


def affine_output(
    matrix: Sequence[Sequence[float]] | np.ndarray,
    state: Sequence[float] | np.ndarray,
    offset: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Compute the affine output y_raw = A @ x + y0."""

    model_matrix, state_vector = validate_linear_model(matrix, state)
    offset_vector = _as_finite_vector(offset, name="offset")
    if offset_vector.size != model_matrix.shape[0]:
        raise ModelValidationError(
            "offset length must equal the matrix row count"
        )
    return model_matrix @ state_vector + offset_vector


def superposition_diagnostics(
    mapping: Callable[[np.ndarray], np.ndarray],
    u: Sequence[float] | np.ndarray,
    v: Sequence[float] | np.ndarray,
    alpha: float,
    beta: float,
    output_scale: float = 1.0,
) -> dict[str, Any]:
    """F(alpha*u+beta*v) ile alpha*F(u)+beta*F(v) farkını raporlar."""

    u_vector = _as_finite_vector(u, name="u")
    v_vector = _as_finite_vector(v, name="v")
    if u_vector.shape != v_vector.shape:
        raise ModelValidationError("u and v must have the same shape")
    if not np.isfinite(alpha) or not np.isfinite(beta):
        raise ModelValidationError("alpha and beta must be finite")
    if not np.isfinite(output_scale) or output_scale <= 0.0:
        raise ModelValidationError("output_scale must be finite and positive")

    lhs = _as_finite_vector(mapping(alpha * u_vector + beta * v_vector), name="lhs")
    rhs = _as_finite_vector(
        alpha * mapping(u_vector) + beta * mapping(v_vector), name="rhs"
    )
    if lhs.shape != rhs.shape:
        raise ModelValidationError("mapping returned inconsistent output shapes")

    residual = lhs - rhs
    absolute_inf = float(np.max(np.abs(residual)))
    reference = max(
        float(np.max(np.abs(lhs))),
        float(np.max(np.abs(rhs))),
        float(output_scale),
    )
    return {
        "alpha": float(alpha),
        "beta": float(beta),
        "coefficient_sum": float(alpha + beta),
        "output_scale": float(output_scale),
        "lhs": lhs.tolist(),
        "rhs": rhs.tolist(),
        "residual": residual.tolist(),
        "absolute_residual_inf": absolute_inf,
        "relative_residual_inf": absolute_inf / reference,
    }


def sensor_case() -> dict[str, Any]:
    """Varsayımsal üç-sensör sisteminin fiziksel ve ölçekli sonuçlarını üretir."""

    zero_corrected_v = linear_output(SENSITIVITY_V_PER_INPUT, STATE_CHANGE)
    raw_output_v = affine_output(
        SENSITIVITY_V_PER_INPUT, STATE_CHANGE, OFFSET_V
    )

    dimensionless_state = STATE_CHANGE / STATE_SCALE
    scaled_matrix_v = SENSITIVITY_V_PER_INPUT * STATE_SCALE[np.newaxis, :]
    scaled_output_v = linear_output(scaled_matrix_v, dimensionless_state)
    scaling_residual_v = zero_corrected_v - scaled_output_v

    return {
        "name": "three_sensor_forward_model",
        "status": "illustrative_hypothetical_coefficients",
        "matrix_shape": list(SENSITIVITY_V_PER_INPUT.shape),
        "state_names": list(STATE_NAMES),
        "state_units": list(STATE_UNITS),
        "output_names": list(OUTPUT_NAMES),
        "output_units": list(OUTPUT_UNITS),
        "coefficient_units": [list(row) for row in COEFFICIENT_UNITS],
        "sensitivity_matrix": SENSITIVITY_V_PER_INPUT.tolist(),
        "state_change": STATE_CHANGE.tolist(),
        "offset_v": OFFSET_V.tolist(),
        "zero_corrected_output_v": zero_corrected_v.tolist(),
        "raw_output_v": raw_output_v.tolist(),
        "state_scale": STATE_SCALE.tolist(),
        "dimensionless_state": dimensionless_state.tolist(),
        "scaled_matrix_v": scaled_matrix_v.tolist(),
        "scaled_output_v": scaled_output_v.tolist(),
        "scaling_residual_inf_v": float(np.max(np.abs(scaling_residual_v))),
        "valid_absolute_change": VALID_ABSOLUTE_CHANGE.tolist(),
        "within_declared_working_region": bool(
            np.all(np.abs(STATE_CHANGE) <= VALID_ABSOLUTE_CHANGE)
        ),
    }


def linearity_cases() -> dict[str, Any]:
    """Lineer ve afin sensör haritalarını aynı süperpozisyon deneyiyle karşılaştırır."""

    u = np.array([2.0, 1.0, 4.0], dtype=float)
    v = np.array([-1.0, 2.0, 3.0], dtype=float)
    alpha = 1.5
    beta = -0.25

    linear_mapping = lambda value: linear_output(SENSITIVITY_V_PER_INPUT, value)
    affine_mapping = lambda value: affine_output(
        SENSITIVITY_V_PER_INPUT, value, OFFSET_V
    )

    affine_alpha = 0.35
    affine_beta = 0.65
    return {
        "test_vectors": {"u": u.tolist(), "v": v.tolist()},
        "general_coefficients": {"alpha": alpha, "beta": beta},
        "linear_map": superposition_diagnostics(
            linear_mapping, u, v, alpha, beta
        ),
        "affine_map_general_combination": superposition_diagnostics(
            affine_mapping, u, v, alpha, beta
        ),
        "affine_map_affine_combination": superposition_diagnostics(
            affine_mapping, u, v, affine_alpha, affine_beta
        ),
        "linear_zero_response_v": linear_mapping(np.zeros(3)).tolist(),
        "affine_zero_response_v": affine_mapping(np.zeros(3)).tolist(),
    }


def local_sensor_change(
    temperature_change: float,
    *,
    slope_v_per_degree: float = 0.040,
    curvature_v_per_degree_squared: float = 0.0008,
) -> dict[str, float | bool]:
    """Basit eğrisel yanıtı ve çalışma noktası çevresindeki lineer artışı karşılaştırır."""

    if not all(
        np.isfinite(value)
        for value in (
            temperature_change,
            slope_v_per_degree,
            curvature_v_per_degree_squared,
        )
    ):
        raise ModelValidationError("local model values must be finite")

    exact_change_v = (
        slope_v_per_degree * temperature_change
        + curvature_v_per_degree_squared * temperature_change**2
    )
    linear_change_v = slope_v_per_degree * temperature_change
    approximation_error_v = exact_change_v - linear_change_v
    return {
        "temperature_change_degC": float(temperature_change),
        "exact_change_v": float(exact_change_v),
        "linear_change_v": float(linear_change_v),
        "approximation_error_v": float(approximation_error_v),
        "absolute_error_v": float(abs(approximation_error_v)),
        "within_0_025_v_tolerance": bool(abs(approximation_error_v) <= 0.025),
    }


def local_model_case() -> dict[str, Any]:
    """Yerel yaklaşımın uzaklıkla büyüyen hatasını sabit noktalarda raporlar."""

    temperature_changes = (-10.0, -5.0, -1.0, 1.0, 5.0, 10.0)
    return {
        "name": "local_temperature_sensor_model",
        "status": "illustrative_hypothetical_transfer_curve",
        "operating_temperature_degC": 20.0,
        "slope_v_per_degC": 0.040,
        "curvature_v_per_degC_squared": 0.0008,
        "declared_error_tolerance_v": 0.025,
        "evaluations": [local_sensor_change(value) for value in temperature_changes],
    }


def all_results() -> dict[str, Any]:
    """Kitap, test ve doğrulama betiği için tek JSON-uyumlu sonuç paketi."""

    return {
        "schema_version": "1.0",
        "chapter": 1,
        "version": "v0.2",
        "randomness": False,
        "external_data": False,
        "sensor_case": sensor_case(),
        "linearity_cases": linearity_cases(),
        "local_model_case": local_model_case(),
        "software": {
            "python": __import__("platform").python_version(),
            "numpy": np.__version__,
        },
    }


def format_human(results: dict[str, Any]) -> str:
    """Ana sonuçları kısa, denetlenebilir insan-okur çıktısına dönüştürür."""

    sensor = results["sensor_case"]
    linear = results["linearity_cases"]["linear_map"]
    affine = results["linearity_cases"]["affine_map_general_combination"]
    local = results["local_model_case"]["evaluations"]
    lines = [
        "Bölüm 1 - model kurma doğrulaması",
        f"A.shape = {tuple(sensor['matrix_shape'])}",
        f"Sıfır-düzeltilmiş çıktı [V] = {sensor['zero_corrected_output_v']}",
        f"Ham çıktı [V] = {sensor['raw_output_v']}",
        (
            "Ölçekleme tutarlılığı ||r||_inf [V] = "
            f"{sensor['scaling_residual_inf_v']:.3e}"
        ),
        (
            "Lineer harita süperpozisyon artığı [V] = "
            f"{linear['absolute_residual_inf']:.3e}"
        ),
        (
            "Afin harita genel süperpozisyon artığı [V] = "
            f"{affine['absolute_residual_inf']:.3e}"
        ),
        "Yerel yaklaşım |hata| [V]: "
        + ", ".join(
            f"ΔT={item['temperature_change_degC']:+g}: {item['absolute_error_v']:.4f}"
            for item in local
        ),
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json", action="store_true", help="Sonuçları JSON biçiminde yazdır."
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = all_results()
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(format_human(results))


if __name__ == "__main__":
    main()
