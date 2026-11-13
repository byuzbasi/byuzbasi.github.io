#!/usr/bin/env python3
"""Bölüm 9: en küçük kareler, kalibrasyon ve ağırlıklı doğrulama.

Bu modül yalnız NumPy ve Python standart kütüphanesini kullanır. Bütün veri
deterministik ve öğretim amacıyla üretilmiştir. Kod gerçek bir cihaz
kalibrasyon sertifikası, GNSS çözümü veya emniyet kararı üretmez.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np


class LeastSquaresError(ValueError):
    """Girdi ya da yöntem sözleşmesi sağlanmadığında üretilen açık hata."""


@dataclass(frozen=True)
class LeastSquaresResult:
    """Tam sütun ranklı bir QR en küçük kareler hesabının kanıt kaydı."""

    method: str
    design: np.ndarray
    response: np.ndarray
    solution: np.ndarray
    fitted: np.ndarray
    residual: np.ndarray
    q: np.ndarray
    r_factor: np.ndarray
    rank: int
    singular_values: np.ndarray
    relative_tolerance: float
    absolute_rank_tolerance: float
    condition_2: float
    degrees_of_freedom: int
    residual_sum_squares: float
    residual_norm_2: float
    root_mean_square_error: float | None
    normal_equation_residual_inf: float
    normal_equation_residual_relative: float
    qr_reconstruction_residual_inf: float
    q_orthogonality_residual_inf: float
    triangular_solve_residual_inf: float
    relative_fit_residual: float
    leverage: np.ndarray
    leverage_sum_residual: float
    max_leverage: float


@dataclass(frozen=True)
class WeightedLeastSquaresResult:
    """Diyagonal ölçüm standart sapmalarıyla ağırlıklı çözüm kaydı."""

    method: str
    design: np.ndarray
    response: np.ndarray
    standard_deviations: np.ndarray
    whitened_design: np.ndarray
    whitened_response: np.ndarray
    solution: np.ndarray
    fitted: np.ndarray
    physical_residual: np.ndarray
    whitened_residual: np.ndarray
    weighted_sum_squares: float
    physical_residual_norm_2: float
    weighted_normal_residual_inf: float
    weight_ratio: float
    core: LeastSquaresResult


def _as_finite_vector(
    values: Sequence[float] | np.ndarray, *, name: str
) -> np.ndarray:
    """Bir boyutlu, boş olmayan ve sonlu float vektör döndür."""

    array = np.asarray(values, dtype=float)
    if array.ndim != 1:
        raise LeastSquaresError(f"{name} must be one-dimensional")
    if array.size == 0:
        raise LeastSquaresError(f"{name} must not be empty")
    if not np.all(np.isfinite(array)):
        raise LeastSquaresError(f"{name} must contain only finite values")
    return np.array(array, dtype=float, copy=True)


def _as_finite_matrix(
    values: Sequence[Sequence[float]] | np.ndarray, *, name: str
) -> np.ndarray:
    """İki boyutlu, boş olmayan ve sonlu float matrisi döndür."""

    array = np.asarray(values, dtype=float)
    if array.ndim != 2:
        raise LeastSquaresError(f"{name} must be two-dimensional")
    if array.shape[0] == 0 or array.shape[1] == 0:
        raise LeastSquaresError(f"{name} must not have an empty dimension")
    if not np.all(np.isfinite(array)):
        raise LeastSquaresError(f"{name} must contain only finite values")
    return np.array(array, dtype=float, copy=True)


def _validated_relative_tolerance(
    matrix: np.ndarray, relative_tolerance: float | None
) -> float:
    """Ölçekli rank kapısı için pozitif ve sonlu göreli tolerans seç."""

    if relative_tolerance is None:
        return float(8.0 * np.finfo(float).eps * max(matrix.shape))
    value = float(relative_tolerance)
    if not math.isfinite(value) or value <= 0.0:
        raise LeastSquaresError("relative_tolerance must be positive and finite")
    return value


def _rank_record(
    matrix: np.ndarray, relative_tolerance: float
) -> tuple[int, np.ndarray, float]:
    """Tekil değerlere dayalı sayısal rank ve mutlak eşiği döndür."""

    singular_values = np.linalg.svd(matrix, compute_uv=False)
    largest = float(singular_values[0]) if singular_values.size else 0.0
    threshold = float(relative_tolerance * largest)
    rank = int(np.count_nonzero(singular_values > threshold))
    return rank, singular_values, threshold


def _inf_norm(values: np.ndarray) -> float:
    """Boş olmayan dizi için sonsuz normu float olarak döndür."""

    return float(np.linalg.norm(values, ord=np.inf))


def _relative_residual(numerator: np.ndarray, scale: float) -> float:
    """Mutlak artığı sonlu, sıfırdan güvenli bir ölçeğe böl."""

    denominator = max(float(scale), np.finfo(float).tiny)
    return float(np.linalg.norm(numerator, ord=2) / denominator)


def _canonicalize_qr(q: np.ndarray, r_factor: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Sıfır olmayan R köşegenlerini pozitif yaparak QR işaretini sabitle."""

    q_result = np.array(q, dtype=float, copy=True)
    r_result = np.array(r_factor, dtype=float, copy=True)
    diagonal = np.diag(r_result)
    signs = np.where(diagonal < 0.0, -1.0, 1.0)
    q_result *= signs[np.newaxis, :]
    r_result *= signs[:, np.newaxis]
    return q_result, r_result


def qr_least_squares(
    design_values: Sequence[Sequence[float]] | np.ndarray,
    response_values: Sequence[float] | np.ndarray,
    *,
    relative_tolerance: float | None = None,
) -> LeastSquaresResult:
    """Tam sütun ranklı uzun sistemi ince QR ile en küçük karelerde çöz."""

    design = _as_finite_matrix(design_values, name="design")
    response = _as_finite_vector(response_values, name="response")
    rows, columns = design.shape
    if response.shape[0] != rows:
        raise LeastSquaresError("response length must equal the design row count")
    if rows < columns:
        raise LeastSquaresError("qr_least_squares requires rows >= columns")

    tolerance = _validated_relative_tolerance(design, relative_tolerance)
    rank, singular_values, absolute_tolerance = _rank_record(design, tolerance)
    if rank != columns:
        raise LeastSquaresError(
            "qr_least_squares requires full column rank at the recorded tolerance"
        )

    q_raw, r_raw = np.linalg.qr(design, mode="reduced")
    q, r_factor = _canonicalize_qr(q_raw, r_raw)
    transformed_response = q.T @ response
    try:
        solution = np.linalg.solve(r_factor, transformed_response)
    except np.linalg.LinAlgError as exc:
        raise LeastSquaresError("triangular QR solve failed") from exc

    fitted = design @ solution
    residual = response - fitted
    normal_residual = design.T @ residual
    residual_sum_squares = float(residual @ residual)
    degrees_of_freedom = rows - columns
    rmse = (
        float(math.sqrt(residual_sum_squares / degrees_of_freedom))
        if degrees_of_freedom > 0
        else None
    )
    leverage = np.sum(q * q, axis=1)
    normal_scale = (
        float(np.linalg.norm(design, ord=2) * np.linalg.norm(residual, ord=2))
        + float(np.linalg.norm(design.T @ response, ord=2))
    )
    fit_scale = float(
        np.linalg.norm(design, ord=2) * np.linalg.norm(solution, ord=2)
        + np.linalg.norm(response, ord=2)
    )

    return LeastSquaresResult(
        method="reduced_householder_qr",
        design=design,
        response=response,
        solution=solution,
        fitted=fitted,
        residual=residual,
        q=q,
        r_factor=r_factor,
        rank=rank,
        singular_values=singular_values,
        relative_tolerance=tolerance,
        absolute_rank_tolerance=absolute_tolerance,
        condition_2=float(np.linalg.cond(design, p=2)),
        degrees_of_freedom=degrees_of_freedom,
        residual_sum_squares=residual_sum_squares,
        residual_norm_2=float(np.linalg.norm(residual, ord=2)),
        root_mean_square_error=rmse,
        normal_equation_residual_inf=_inf_norm(normal_residual),
        normal_equation_residual_relative=_relative_residual(
            normal_residual, normal_scale
        ),
        qr_reconstruction_residual_inf=_inf_norm(design - q @ r_factor),
        q_orthogonality_residual_inf=_inf_norm(q.T @ q - np.eye(columns)),
        triangular_solve_residual_inf=_inf_norm(
            r_factor @ solution - transformed_response
        ),
        relative_fit_residual=_relative_residual(residual, fit_scale),
        leverage=leverage,
        leverage_sum_residual=float(abs(np.sum(leverage) - columns)),
        max_leverage=float(np.max(leverage)),
    )


def lstsq_reference(
    design_values: Sequence[Sequence[float]] | np.ndarray,
    response_values: Sequence[float] | np.ndarray,
    *,
    rcond: float | None = None,
) -> dict[str, Any]:
    """NumPy kitaplık sonucunu, boş artık dizisini yorumlamadan kaydet."""

    design = _as_finite_matrix(design_values, name="design")
    response = _as_finite_vector(response_values, name="response")
    if response.shape[0] != design.shape[0]:
        raise LeastSquaresError("response length must equal the design row count")
    if rcond is not None:
        rcond_value = float(rcond)
        if not math.isfinite(rcond_value):
            raise LeastSquaresError("rcond must be finite when supplied")
    try:
        solution, residuals, rank, singular_values = np.linalg.lstsq(
            design, response, rcond=rcond
        )
    except np.linalg.LinAlgError as exc:
        raise LeastSquaresError("numpy.linalg.lstsq did not converge") from exc
    physical_residual = response - design @ solution
    return {
        "method": "numpy_linalg_lstsq",
        "solution": solution,
        "reported_residuals": residuals,
        "reported_residuals_empty": bool(residuals.size == 0),
        "explicit_residual": physical_residual,
        "explicit_residual_sum_squares": float(physical_residual @ physical_residual),
        "rank": int(rank),
        "singular_values": singular_values,
        "rcond": rcond,
    }


def normal_equations_teaching(
    design_values: Sequence[Sequence[float]] | np.ndarray,
    response_values: Sequence[float] | np.ndarray,
) -> dict[str, Any]:
    """Normal denklemleri yalnız kontrollü öğretim karşılaştırması için çöz."""

    design = _as_finite_matrix(design_values, name="design")
    response = _as_finite_vector(response_values, name="response")
    if response.shape[0] != design.shape[0]:
        raise LeastSquaresError("response length must equal the design row count")
    gram = design.T @ design
    right_hand_side = design.T @ response
    try:
        solution = np.linalg.solve(gram, right_hand_side)
    except np.linalg.LinAlgError:
        return {
            "method": "normal_equations_teaching_only",
            "success": False,
            "solution": None,
            "gram": gram,
            "condition_design_2": float(np.linalg.cond(design, p=2)),
            "condition_gram_2": float(np.linalg.cond(gram, p=2)),
            "residual_norm_2": None,
            "normal_residual_inf": None,
        }
    residual = response - design @ solution
    return {
        "method": "normal_equations_teaching_only",
        "success": True,
        "solution": solution,
        "gram": gram,
        "condition_design_2": float(np.linalg.cond(design, p=2)),
        "condition_gram_2": float(np.linalg.cond(gram, p=2)),
        "residual_norm_2": float(np.linalg.norm(residual, ord=2)),
        "normal_residual_inf": _inf_norm(design.T @ residual),
    }


def weighted_least_squares(
    design_values: Sequence[Sequence[float]] | np.ndarray,
    response_values: Sequence[float] | np.ndarray,
    standard_deviation_values: Sequence[float] | np.ndarray,
    *,
    relative_tolerance: float | None = None,
) -> WeightedLeastSquaresResult:
    """Bağımsız ve bilinen pozitif standart sapmalarla satırları beyazlat."""

    design = _as_finite_matrix(design_values, name="design")
    response = _as_finite_vector(response_values, name="response")
    standard_deviations = _as_finite_vector(
        standard_deviation_values, name="standard_deviations"
    )
    if response.shape[0] != design.shape[0]:
        raise LeastSquaresError("response length must equal the design row count")
    if standard_deviations.shape[0] != design.shape[0]:
        raise LeastSquaresError(
            "standard_deviations length must equal the design row count"
        )
    if np.any(standard_deviations <= 0.0):
        raise LeastSquaresError("standard_deviations must be strictly positive")

    whitened_design = design / standard_deviations[:, np.newaxis]
    whitened_response = response / standard_deviations
    core = qr_least_squares(
        whitened_design,
        whitened_response,
        relative_tolerance=relative_tolerance,
    )
    solution = core.solution
    fitted = design @ solution
    physical_residual = response - fitted
    whitened_residual = physical_residual / standard_deviations

    return WeightedLeastSquaresResult(
        method="diagonal_whitening_then_reduced_qr",
        design=design,
        response=response,
        standard_deviations=standard_deviations,
        whitened_design=whitened_design,
        whitened_response=whitened_response,
        solution=solution,
        fitted=fitted,
        physical_residual=physical_residual,
        whitened_residual=whitened_residual,
        weighted_sum_squares=float(whitened_residual @ whitened_residual),
        physical_residual_norm_2=float(np.linalg.norm(physical_residual, ord=2)),
        weighted_normal_residual_inf=_inf_norm(
            whitened_design.T @ whitened_residual
        ),
        weight_ratio=float(
            (np.max(standard_deviations) / np.min(standard_deviations)) ** 2
        ),
        core=core,
    )


def coefficient_covariance_from_qr(
    r_factor_values: Sequence[Sequence[float]] | np.ndarray,
    variance: float,
) -> np.ndarray:
    """sigma^2 (R^T R)^(-1) matrisini açık ters kurmadan hesapla."""

    r_factor = _as_finite_matrix(r_factor_values, name="r_factor")
    if r_factor.shape[0] != r_factor.shape[1]:
        raise LeastSquaresError("r_factor must be square")
    variance_value = float(variance)
    if not math.isfinite(variance_value) or variance_value < 0.0:
        raise LeastSquaresError("variance must be nonnegative and finite")
    identity = np.eye(r_factor.shape[0])
    try:
        inverse_transpose = np.linalg.solve(r_factor.T, identity)
        gram_inverse = np.linalg.solve(r_factor, inverse_transpose)
    except np.linalg.LinAlgError as exc:
        raise LeastSquaresError("r_factor must be nonsingular") from exc
    covariance = variance_value * gram_inverse
    return 0.5 * (covariance + covariance.T)


def estimated_uncertainty(result: LeastSquaresResult) -> dict[str, Any]:
    """Eş varyanslı ilişkisiz hata varsayımıyla katsayı belirsizliği kaydı."""

    if result.degrees_of_freedom <= 0:
        raise LeastSquaresError("positive residual degrees of freedom are required")
    variance = result.residual_sum_squares / result.degrees_of_freedom
    covariance = coefficient_covariance_from_qr(result.r_factor, variance)
    diagonal = np.diag(covariance)
    if np.any(diagonal < -100.0 * np.finfo(float).eps):
        raise LeastSquaresError("computed covariance has a negative diagonal")
    standard_errors = np.sqrt(np.maximum(diagonal, 0.0))
    return {
        "assumptions": [
            "fixed full-column-rank design",
            "zero-mean errors",
            "uncorrelated errors",
            "common unknown variance",
        ],
        "residual_variance_estimate": float(variance),
        "covariance": covariance,
        "standard_errors": standard_errors,
        "normality_required_for_this_covariance_identity": False,
        "confidence_intervals_computed": False,
    }


def exact_line_fit_case(
    *, relative_tolerance: float | None = None
) -> dict[str, Any]:
    """Kesin çözümü (2,3) ve dik artığı (1,-2,1,0) olan küçük örnek."""

    design = np.array(
        [[1.0, -1.0], [1.0, 0.0], [1.0, 1.0], [1.0, 2.0]], dtype=float
    )
    response = np.array([0.0, 0.0, 6.0, 8.0], dtype=float)
    qr = qr_least_squares(
        design, response, relative_tolerance=relative_tolerance
    )
    library = lstsq_reference(design, response, rcond=None)
    return {
        "design": design,
        "response": response,
        "expected_solution": np.array([2.0, 3.0]),
        "expected_residual": np.array([1.0, -2.0, 1.0, 0.0]),
        "qr": qr,
        "library": library,
    }


def load_cell_dataset() -> dict[str, Any]:
    """Beş kuvvet düzeyi ve ikişer tekrarlı özgün kalibrasyon verisini üret."""

    force_newton = np.repeat(np.array([0.0, 250.0, 500.0, 750.0, 1000.0]), 2)
    temperature_change_kelvin = np.repeat(
        np.array([-5.0, 5.0, 0.0, -5.0, 5.0]), 2
    )
    deterministic_residual_millivolt = np.array(
        [0.01, -0.01, 0.02, -0.02, 0.01, -0.01, 0.02, -0.02, 0.01, -0.01]
    )
    true_physical_coefficients = np.array([0.20, 0.004, 0.010])
    response_millivolt = (
        true_physical_coefficients[0]
        + true_physical_coefficients[1] * force_newton
        + true_physical_coefficients[2] * temperature_change_kelvin
        + deterministic_residual_millivolt
    )
    standard_deviation_millivolt = np.repeat(
        np.array([0.015, 0.025, 0.020, 0.030, 0.020]), 2
    )
    return {
        "force_newton": force_newton,
        "temperature_change_kelvin": temperature_change_kelvin,
        "response_millivolt": response_millivolt,
        "standard_deviation_millivolt": standard_deviation_millivolt,
        "deterministic_residual_millivolt": deterministic_residual_millivolt,
        "true_physical_coefficients": true_physical_coefficients,
        "force_scale_newton": 250.0,
        "temperature_scale_kelvin": 5.0,
        "check": {
            "force_newton": 625.0,
            "temperature_change_kelvin": 2.0,
            "observed_response_millivolt": 2.73,
        },
    }


def scaled_calibration_design(
    force_values: Sequence[float] | np.ndarray,
    temperature_change_values: Sequence[float] | np.ndarray,
    *,
    force_scale_newton: float = 250.0,
    temperature_scale_kelvin: float = 5.0,
) -> np.ndarray:
    """Sabit, ölçekli kuvvet ve ölçekli sıcaklık sütunlarını oluştur."""

    force = _as_finite_vector(force_values, name="force")
    temperature_change = _as_finite_vector(
        temperature_change_values, name="temperature_change"
    )
    if force.shape != temperature_change.shape:
        raise LeastSquaresError("force and temperature_change must have equal shapes")
    force_scale = float(force_scale_newton)
    temperature_scale = float(temperature_scale_kelvin)
    if not math.isfinite(force_scale) or force_scale <= 0.0:
        raise LeastSquaresError("force_scale_newton must be positive and finite")
    if not math.isfinite(temperature_scale) or temperature_scale <= 0.0:
        raise LeastSquaresError(
            "temperature_scale_kelvin must be positive and finite"
        )
    return np.column_stack(
        (
            np.ones(force.size),
            force / force_scale,
            temperature_change / temperature_scale,
        )
    )


def scaled_to_physical_coefficients(
    scaled_values: Sequence[float] | np.ndarray,
    *,
    force_scale_newton: float = 250.0,
    temperature_scale_kelvin: float = 5.0,
) -> np.ndarray:
    """Ölçekli katsayıları mV, mV/N ve mV/K sözleşmesine geri taşı."""

    scaled = _as_finite_vector(scaled_values, name="scaled_coefficients")
    if scaled.shape != (3,):
        raise LeastSquaresError("scaled_coefficients must have length three")
    force_scale = float(force_scale_newton)
    temperature_scale = float(temperature_scale_kelvin)
    if not math.isfinite(force_scale) or force_scale <= 0.0:
        raise LeastSquaresError("force_scale_newton must be positive and finite")
    if not math.isfinite(temperature_scale) or temperature_scale <= 0.0:
        raise LeastSquaresError(
            "temperature_scale_kelvin must be positive and finite"
        )
    return np.array(
        [scaled[0], scaled[1] / force_scale, scaled[2] / temperature_scale]
    )


def load_cell_calibration_case(
    *, relative_tolerance: float | None = None
) -> dict[str, Any]:
    """Ana yük hücresi OLS/WLS hesabını ve bağımsız kontrolü üret."""

    data = load_cell_dataset()
    design = scaled_calibration_design(
        data["force_newton"],
        data["temperature_change_kelvin"],
        force_scale_newton=data["force_scale_newton"],
        temperature_scale_kelvin=data["temperature_scale_kelvin"],
    )
    qr = qr_least_squares(
        design,
        data["response_millivolt"],
        relative_tolerance=relative_tolerance,
    )
    weighted = weighted_least_squares(
        design,
        data["response_millivolt"],
        data["standard_deviation_millivolt"],
        relative_tolerance=relative_tolerance,
    )
    library = lstsq_reference(design, data["response_millivolt"], rcond=None)
    physical_coefficients = scaled_to_physical_coefficients(
        qr.solution,
        force_scale_newton=data["force_scale_newton"],
        temperature_scale_kelvin=data["temperature_scale_kelvin"],
    )
    weighted_physical_coefficients = scaled_to_physical_coefficients(
        weighted.solution,
        force_scale_newton=data["force_scale_newton"],
        temperature_scale_kelvin=data["temperature_scale_kelvin"],
    )
    check = data["check"]
    check_design = scaled_calibration_design(
        [check["force_newton"]],
        [check["temperature_change_kelvin"]],
        force_scale_newton=data["force_scale_newton"],
        temperature_scale_kelvin=data["temperature_scale_kelvin"],
    )
    check_prediction = float((check_design @ qr.solution)[0])
    check_residual = float(check["observed_response_millivolt"] - check_prediction)
    return {
        "data": data,
        "scaled_design": design,
        "scaled_expected_coefficients": np.array([0.20, 1.00, 0.05]),
        "qr": qr,
        "weighted": weighted,
        "library": library,
        "physical_coefficients": physical_coefficients,
        "weighted_physical_coefficients": weighted_physical_coefficients,
        "uncertainty": estimated_uncertainty(qr),
        "check_prediction_millivolt": check_prediction,
        "check_residual_millivolt": check_residual,
        "training_observation_count": int(design.shape[0]),
        "parameter_count": int(design.shape[1]),
        "check_used_for_fitting": False,
    }


def weighted_influence_case(
    *, relative_tolerance: float | None = None
) -> dict[str, Any]:
    """Düşük kesinlikli son gözlemin etkisini silmeden ağırlıkla karşılaştır."""

    coordinate = np.array([0.0, 1.0, 2.0, 3.0])
    design = np.column_stack((np.ones(coordinate.size), coordinate))
    response = np.array([1.0, 3.0, 5.0, 9.0])
    standard_deviations = np.array([0.2, 0.2, 0.2, 2.0])
    ordinary = qr_least_squares(
        design, response, relative_tolerance=relative_tolerance
    )
    weighted = weighted_least_squares(
        design,
        response,
        standard_deviations,
        relative_tolerance=relative_tolerance,
    )
    return {
        "coordinate": coordinate,
        "design": design,
        "response": response,
        "standard_deviations": standard_deviations,
        "ordinary": ordinary,
        "weighted": weighted,
        "observation_removed": False,
    }


def near_collinear_design(epsilon: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """İkinci ve üçüncü sütunları epsilon ile yakınlaştıran öğretim ailesi."""

    value = float(epsilon)
    if not math.isfinite(value) or value <= 0.0:
        raise LeastSquaresError("epsilon must be positive and finite")
    u = np.array([1.0, 1.0, 1.0, 1.0])
    v = np.array([1.0, -1.0, 1.0, -1.0])
    w = np.array([1.0, 1.0, -1.0, -1.0])
    orthogonal_residual_direction = np.array([1.0, -1.0, -1.0, 1.0])
    design = np.column_stack((u, v, v + value * w))
    expected_solution = np.array([1.0, 2.0, -2.0])
    response = design @ expected_solution + 1.0e-8 * orthogonal_residual_direction
    return design, response, expected_solution


def normal_equation_stress_case(
    epsilon: float, *, relative_tolerance: float | None = None
) -> dict[str, Any]:
    """Yakın bağımlılıkta QR, lstsq ve normal denklemleri karşılaştır."""

    design, response, expected_solution = near_collinear_design(epsilon)
    qr = qr_least_squares(
        design, response, relative_tolerance=relative_tolerance
    )
    library = lstsq_reference(design, response, rcond=None)
    normal = normal_equations_teaching(design, response)
    record: dict[str, Any] = {
        "epsilon": float(epsilon),
        "design": design,
        "response": response,
        "expected_solution": expected_solution,
        "condition_design_2": float(np.linalg.cond(design, p=2)),
        "condition_gram_2": float(np.linalg.cond(design.T @ design, p=2)),
        "qr": qr,
        "library": library,
        "normal_equations": normal,
        "qr_solution_error_inf": _inf_norm(qr.solution - expected_solution),
        "library_solution_error_inf": _inf_norm(
            library["solution"] - expected_solution
        ),
    }
    if normal["success"]:
        record["normal_solution_error_inf"] = _inf_norm(
            normal["solution"] - expected_solution
        )
    else:
        record["normal_solution_error_inf"] = None
    return record


def leveling_network_case(
    *, relative_tolerance: float | None = None
) -> dict[str, Any]:
    """Sabit A noktasıyla üç gözlemli küçük sentetik nivelman ayarlaması."""

    design = np.array([[1.0, 0.0], [-1.0, 1.0], [0.0, 1.0]])
    observed_height_differences_metre = np.array([1.020, 0.980, 2.010])
    standard_deviation_metre = np.array([0.010, 0.020, 0.010])
    weighted = weighted_least_squares(
        design,
        observed_height_differences_metre,
        standard_deviation_metre,
        relative_tolerance=relative_tolerance,
    )
    reference_height_a_metre = 100.0
    adjusted_heights = reference_height_a_metre + weighted.solution
    closure_misfit_metre = float(
        observed_height_differences_metre[0]
        + observed_height_differences_metre[1]
        - observed_height_differences_metre[2]
    )
    return {
        "design": design,
        "observed_height_differences_metre": observed_height_differences_metre,
        "standard_deviation_metre": standard_deviation_metre,
        "reference_height_a_metre": reference_height_a_metre,
        "adjusted_heights_b_c_metre": adjusted_heights,
        "closure_misfit_metre": closure_misfit_metre,
        "weighted": weighted,
        "official_geodetic_result": False,
    }


def _json_ready(value: Any) -> Any:
    """NumPy ve veri sınıfı nesnelerini katı JSON tiplerine dönüştür."""

    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, (LeastSquaresResult, WeightedLeastSquaresResult)):
        return {
            key: _json_ready(field_value)
            for key, field_value in value.__dict__.items()
        }
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    if isinstance(value, float):
        if not math.isfinite(value):
            raise LeastSquaresError("non-finite value cannot be serialized to strict JSON")
        return value
    return value


def chapter_results(
    *, relative_tolerance: float | None = None
) -> dict[str, Any]:
    """Bölüm 9'un bütün deterministik örneklerini tek kanonik kayıtta topla."""

    exact_line = exact_line_fit_case(relative_tolerance=relative_tolerance)
    calibration = load_cell_calibration_case(
        relative_tolerance=relative_tolerance
    )
    influence = weighted_influence_case(relative_tolerance=relative_tolerance)
    leveling = leveling_network_case(relative_tolerance=relative_tolerance)
    stress = [
        normal_equation_stress_case(
            epsilon, relative_tolerance=relative_tolerance
        )
        for epsilon in (1.0e-2, 1.0e-4, 1.0e-6, 1.0e-8)
    ]
    result = {
        "schema_version": "1.0",
        "version": "v1.0",
        "chapter": 9,
        "chapter_title": "En Kucuk Kareler ve Kalibrasyon",
        "vector_convention": "column_vectors_left_multiplication",
        "residual_convention": "response_minus_fitted",
        "external_data": False,
        "randomness": False,
        "units": {
            "load_cell_response": "mV",
            "force": "N",
            "temperature_change": "K",
            "force_sensitivity": "mV/N",
            "temperature_sensitivity": "mV/K",
            "leveling_height": "m",
            "whitened_residual": "dimensionless",
        },
        "assumptions": [
            "real finite-dimensional Euclidean observation space",
            "core QR problems have rows at least columns and full column rank",
            "calibration data are synthetic and deterministic",
            "training observations and the check observation are distinct",
            "weighted examples use supplied positive standard deviations",
            "weighted examples assume independent observation errors",
            "no missing values or outliers are silently removed",
            "numerical validation is not a physical acceptance certificate",
        ],
        "exact_line_fit": exact_line,
        "load_cell_calibration": calibration,
        "weighted_influence": influence,
        "normal_equation_stress_cases": stress,
        "leveling_network": leveling,
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }
    return _json_ready(result)


def print_human_readable(results: dict[str, Any]) -> None:
    """Kanonik kaydın kısa insan-okur özetini yazdır."""

    calibration = results["load_cell_calibration"]
    exact_line = results["exact_line_fit"]
    stress = results["normal_equation_stress_cases"][-1]
    print("Bölüm 9 - En Küçük Kareler ve Kalibrasyon")
    print(f"Kesin doğru örneği çözümü: {exact_line['qr']['solution']}")
    print(f"Kesin doğru örneği artığı: {exact_line['qr']['residual']}")
    print(
        "Yük hücresi fiziksel katsayıları "
        f"[mV, mV/N, mV/K]: {calibration['physical_coefficients']}"
    )
    print(
        "Bağımsız kontrol artığı [mV]: "
        f"{calibration['check_residual_millivolt']:.6g}"
    )
    print(
        "En zor stres koşulu kappa_2(A): "
        f"{stress['condition_design_2']:.6e}"
    )
    print("Dış veri: hayır; rastgelelik: hayır; fiziksel sertifika: hayır")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Komut satırı seçeneklerini ayrıştır."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json", action="store_true", help="Kanonik JSON kanıt kaydını yazdır."
    )
    parser.add_argument(
        "--relative-tolerance",
        type=float,
        default=None,
        help="Rank kapısı için pozitif göreli tolerans.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Bölüm sonuçlarını üret ve seçilen görünümde yazdır."""

    arguments = parse_args(argv)
    try:
        results = chapter_results(relative_tolerance=arguments.relative_tolerance)
    except LeastSquaresError as exc:
        print(f"ERROR: {exc}")
        return 2
    if arguments.json:
        print(json.dumps(results, ensure_ascii=False, allow_nan=False, indent=2))
    else:
        print_human_readable(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
