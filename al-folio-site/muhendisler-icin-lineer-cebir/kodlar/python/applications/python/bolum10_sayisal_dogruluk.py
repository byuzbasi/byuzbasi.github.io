#!/usr/bin/env python3
"""Bölüm 10: sayısal doğruluk, koşulluluk ve güvenilirlik tanıları.

Modül yalnız Python standart kütüphanesi ile NumPy kullanır. Bütün örnekler
deterministik ve öğretim amacıyla özgün olarak üretilmiştir. Sonuçlar gerçek
bir robot denetleyici güvenlik sertifikası veya kimyasal analiz raporu değildir.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
from dataclasses import dataclass, fields, is_dataclass
from decimal import Decimal, localcontext
from typing import Any, Sequence

import numpy as np


class NumericalReliabilityError(ValueError):
    """Bir girdi veya sayısal yöntem sözleşmesi sağlanmadığında üretilir."""


@dataclass(frozen=True)
class SolveDiagnostics:
    """Bir kare lineer sistem çözümüne eşlik eden normsal kanıt kaydı."""

    method: str
    norm_name: str
    matrix: np.ndarray
    right_hand_side: np.ndarray
    solution: np.ndarray
    residual: np.ndarray
    matrix_norm: float
    right_hand_side_norm: float
    solution_norm: float
    residual_norm: float
    relative_right_hand_side_residual: float | None
    normwise_backward_error: float | None
    condition_number: float | None
    condition_times_relative_residual: float | None
    reference_solution: np.ndarray | None
    absolute_forward_error: float | None
    relative_forward_error: float | None


def _as_finite_scalar(value: float, *, name: str) -> float:
    """Sonlu bir float döndür; NaN ve sonsuz değerleri reddet."""

    result = float(value)
    if not math.isfinite(result):
        raise NumericalReliabilityError(f"{name} must be finite")
    return result


def _as_positive_scalar(value: float, *, name: str) -> float:
    """Pozitif ve sonlu bir float döndür."""

    result = _as_finite_scalar(value, name=name)
    if result <= 0.0:
        raise NumericalReliabilityError(f"{name} must be positive")
    return result


def _as_finite_vector(
    values: Sequence[float] | np.ndarray, *, name: str
) -> np.ndarray:
    """Boş olmayan, bir boyutlu ve sonlu float vektörü döndür."""

    array = np.asarray(values, dtype=float)
    if array.ndim != 1:
        raise NumericalReliabilityError(f"{name} must be one-dimensional")
    if array.size == 0:
        raise NumericalReliabilityError(f"{name} must not be empty")
    if not np.all(np.isfinite(array)):
        raise NumericalReliabilityError(f"{name} must contain only finite values")
    return np.array(array, dtype=float, copy=True)


def _as_finite_matrix(
    values: Sequence[Sequence[float]] | np.ndarray, *, name: str
) -> np.ndarray:
    """Boş olmayan, iki boyutlu ve sonlu float matrisi döndür."""

    array = np.asarray(values, dtype=float)
    if array.ndim != 2:
        raise NumericalReliabilityError(f"{name} must be two-dimensional")
    if array.shape[0] == 0 or array.shape[1] == 0:
        raise NumericalReliabilityError(f"{name} must not have an empty dimension")
    if not np.all(np.isfinite(array)):
        raise NumericalReliabilityError(f"{name} must contain only finite values")
    return np.array(array, dtype=float, copy=True)


def _validated_norm_order(norm_order: int | float) -> tuple[int | float, str]:
    """Desteklenen uyarılmış norm sırasını ve açık adını döndür."""

    if norm_order == 1:
        return 1, "1-norm"
    if norm_order == 2:
        return 2, "2-norm"
    if norm_order == np.inf:
        return np.inf, "infinity-norm"
    raise NumericalReliabilityError("norm_order must be 1, 2, or infinity")


def _safe_ratio(numerator: float, denominator: float) -> float | None:
    """Geri hata sözleşmesinde 0/0 için 0, diğer sıfır paydada None döndür."""

    if denominator == 0.0:
        return 0.0 if numerator == 0.0 else None
    return float(numerator / denominator)


def floating_point_environment() -> dict[str, Any]:
    """Çalışılan NumPy binary64 ortamının temsil sınırlarını kaydet."""

    info = np.finfo(np.float64)
    one = np.float64(1.0)
    next_up = np.nextafter(one, np.float64(np.inf))
    next_down = np.nextafter(one, np.float64(-np.inf))
    zero = np.float64(0.0)
    smallest_subnormal = np.nextafter(zero, one)
    return {
        "dtype": str(info.dtype),
        "bits": int(info.bits),
        "decimal_precision_digits": int(info.precision),
        "eps": float(info.eps),
        "epsneg": float(info.epsneg),
        "unit_roundoff_round_to_nearest": float(info.eps / 2.0),
        "max": float(info.max),
        "smallest_normal": float(info.smallest_normal),
        "smallest_subnormal": float(smallest_subnormal),
        "spacing_at_one": float(np.spacing(one)),
        "next_after_one_toward_positive_infinity": float(next_up),
        "next_after_one_toward_negative_infinity": float(next_down),
        "gap_above_one": float(next_up - one),
        "gap_below_one": float(one - next_down),
        "rounding_model_scope": (
            "normal finite results without overflow, exceptional values, or "
            "subnormal-relative-error claims"
        ),
    }


def arithmetic_experiments() -> dict[str, Any]:
    """Temsil, birleşmezlik, yutulma ve çıkarma örneklerini üret."""

    float_sum = 0.1 + 0.2
    with localcontext() as context:
        context.prec = 80
        decimal_sum = Decimal("0.1") + Decimal("0.2")
        decimal_x = Decimal("1e16")
        decimal_difference = (decimal_x + Decimal(1)).sqrt() - decimal_x.sqrt()

    large = float(2**53)
    left_associated = (1.0e16 + (-1.0e16)) + 1.0
    right_associated = 1.0e16 + ((-1.0e16) + 1.0)
    values = [1.0e16, 1.0, -1.0e16]
    naive_left_to_right = 0.0
    for value in values:
        naive_left_to_right += value
    x_value = 1.0e16
    cancellation_naive = math.sqrt(x_value + 1.0) - math.sqrt(x_value)
    cancellation_rewritten = 1.0 / (
        math.sqrt(x_value + 1.0) + math.sqrt(x_value)
    )
    return {
        "decimal_fraction": {
            "float_0_1_plus_0_2": float(float_sum),
            "decimal_0_1_plus_0_2": str(decimal_sum),
            "difference_from_float_literal_0_3": float(float_sum - 0.3),
        },
        "absorption": {
            "large": large,
            "large_plus_one": float(large + 1.0),
            "computed_increment": float((large + 1.0) - large),
            "exact_increment": 1.0,
        },
        "non_associativity": {
            "left_associated": float(left_associated),
            "right_associated": float(right_associated),
            "different": bool(left_associated != right_associated),
        },
        "summation": {
            "values": values,
            "naive_left_to_right_sum": float(naive_left_to_right),
            "builtin_sum": float(sum(values)),
            "accurate_fsum": float(math.fsum(values)),
            "exact_sum": 1.0,
        },
        "cancellation": {
            "x": x_value,
            "naive": float(cancellation_naive),
            "rewritten": float(cancellation_rewritten),
            "decimal_reference": str(decimal_difference),
        },
    }


def vector_norms(values: Sequence[float] | np.ndarray) -> dict[str, float]:
    """Bir vektörün 1, 2 ve sonsuz normlarını açık adlarla döndür."""

    vector = _as_finite_vector(values, name="values")
    return {
        "1-norm": float(np.linalg.norm(vector, ord=1)),
        "2-norm": float(np.linalg.norm(vector, ord=2)),
        "infinity-norm": float(np.linalg.norm(vector, ord=np.inf)),
    }


def matrix_norms(
    values: Sequence[Sequence[float]] | np.ndarray,
) -> dict[str, float]:
    """Bir matrisin uyarılmış 1/2/sonsuz ve Frobenius normlarını döndür."""

    matrix = _as_finite_matrix(values, name="values")
    return {
        "induced_1-norm": float(np.linalg.norm(matrix, ord=1)),
        "induced_2-norm": float(np.linalg.norm(matrix, ord=2)),
        "induced_infinity-norm": float(np.linalg.norm(matrix, ord=np.inf)),
        "frobenius-norm": float(np.linalg.norm(matrix, ord="fro")),
    }


def norm_examples() -> dict[str, Any]:
    """Norm aksiyomları ve uyarılmış norm eşitsizliği için sabit örnek üret."""

    vector = np.array([3.0, -4.0, 12.0])
    second = np.array([-1.0, 2.0, 2.0])
    scalar = -2.5
    matrix = np.array([[1.0, -2.0, 0.5], [3.0, 1.0, -1.0]])
    product = matrix @ vector
    vector_two = float(np.linalg.norm(vector, ord=2))
    matrix_two = float(np.linalg.norm(matrix, ord=2))
    product_two = float(np.linalg.norm(product, ord=2))
    return {
        "vector": vector,
        "second_vector": second,
        "matrix": matrix,
        "vector_norms": vector_norms(vector),
        "matrix_norms": matrix_norms(matrix),
        "positive_definiteness_value": vector_two,
        "homogeneity_left": float(np.linalg.norm(scalar * vector, ord=2)),
        "homogeneity_right": float(abs(scalar) * vector_two),
        "triangle_left": float(np.linalg.norm(vector + second, ord=2)),
        "triangle_right": float(
            np.linalg.norm(vector, ord=2) + np.linalg.norm(second, ord=2)
        ),
        "induced_action_left": product_two,
        "induced_action_right": matrix_two * vector_two,
        "induced_action_ratio": product_two / (matrix_two * vector_two),
    }


def solve_with_diagnostics(
    matrix_values: Sequence[Sequence[float]] | np.ndarray,
    right_hand_side_values: Sequence[float] | np.ndarray,
    *,
    norm_order: int | float = 2,
    reference_solution_values: Sequence[float] | np.ndarray | None = None,
) -> SolveDiagnostics:
    """Kare sistemi açık ters oluşturmadan çöz ve normsal tanıları hesapla."""

    matrix = _as_finite_matrix(matrix_values, name="matrix")
    right_hand_side = _as_finite_vector(
        right_hand_side_values, name="right_hand_side"
    )
    rows, columns = matrix.shape
    if rows != columns:
        raise NumericalReliabilityError("matrix must be square")
    if right_hand_side.shape[0] != rows:
        raise NumericalReliabilityError(
            "right_hand_side length must equal the matrix order"
        )
    validated_order, norm_name = _validated_norm_order(norm_order)
    reference_solution: np.ndarray | None = None
    if reference_solution_values is not None:
        reference_solution = _as_finite_vector(
            reference_solution_values, name="reference_solution"
        )
        if reference_solution.shape[0] != columns:
            raise NumericalReliabilityError(
                "reference_solution length must equal the matrix order"
            )

    try:
        solution = np.linalg.solve(matrix, right_hand_side)
    except np.linalg.LinAlgError as exc:
        raise NumericalReliabilityError("linear solve failed") from exc

    residual = right_hand_side - matrix @ solution
    matrix_norm = float(np.linalg.norm(matrix, ord=validated_order))
    right_hand_side_norm = float(
        np.linalg.norm(right_hand_side, ord=validated_order)
    )
    solution_norm = float(np.linalg.norm(solution, ord=validated_order))
    residual_norm = float(np.linalg.norm(residual, ord=validated_order))
    relative_residual = (
        None if right_hand_side_norm == 0.0
        else _safe_ratio(residual_norm, right_hand_side_norm)
    )
    backward_denominator = matrix_norm * solution_norm + right_hand_side_norm
    backward_error = _safe_ratio(residual_norm, backward_denominator)

    condition_raw = float(np.linalg.cond(matrix, p=validated_order))
    condition_number = condition_raw if math.isfinite(condition_raw) else None
    condition_times_residual = (
        float(condition_number * relative_residual)
        if condition_number is not None and relative_residual is not None
        else None
    )

    absolute_forward_error: float | None = None
    relative_forward_error: float | None = None
    if reference_solution is not None:
        absolute_forward_error = float(
            np.linalg.norm(solution - reference_solution, ord=validated_order)
        )
        reference_norm = float(
            np.linalg.norm(reference_solution, ord=validated_order)
        )
        relative_forward_error = (
            None if reference_norm == 0.0
            else _safe_ratio(absolute_forward_error, reference_norm)
        )

    return SolveDiagnostics(
        method="numpy.linalg.solve_lapack_gesv",
        norm_name=norm_name,
        matrix=matrix,
        right_hand_side=right_hand_side,
        solution=solution,
        residual=residual,
        matrix_norm=matrix_norm,
        right_hand_side_norm=right_hand_side_norm,
        solution_norm=solution_norm,
        residual_norm=residual_norm,
        relative_right_hand_side_residual=relative_residual,
        normwise_backward_error=backward_error,
        condition_number=condition_number,
        condition_times_relative_residual=condition_times_residual,
        reference_solution=reference_solution,
        absolute_forward_error=absolute_forward_error,
        relative_forward_error=relative_forward_error,
    )


def perturbation_bound_case() -> dict[str, Any]:
    """Yalnız sağ taraf pertürbasyonu için gerçekleşen ve üst sınırı karşılaştır."""

    matrix = np.array([[3.0, 1.0], [1.0, 2.0]])
    exact_solution = np.array([1.0, -2.0])
    right_hand_side = matrix @ exact_solution
    perturbation = np.array([1.0e-6, -2.0e-6])
    perturbed_right_hand_side = right_hand_side + perturbation
    original = solve_with_diagnostics(
        matrix, right_hand_side, reference_solution_values=exact_solution
    )
    perturbed = solve_with_diagnostics(
        matrix,
        perturbed_right_hand_side,
        reference_solution_values=exact_solution,
    )
    relative_data_change = float(
        np.linalg.norm(perturbation, ord=2)
        / np.linalg.norm(right_hand_side, ord=2)
    )
    condition_number = float(np.linalg.cond(matrix, p=2))
    return {
        "matrix": matrix,
        "exact_solution": exact_solution,
        "right_hand_side": right_hand_side,
        "perturbation": perturbation,
        "perturbed_right_hand_side": perturbed_right_hand_side,
        "relative_data_change": relative_data_change,
        "condition_number_2": condition_number,
        "right_hand_side_only_bound": condition_number * relative_data_change,
        "actual_relative_solution_change": perturbed.relative_forward_error,
        "original": original,
        "perturbed": perturbed,
    }


def small_residual_large_error_case() -> dict[str, Any]:
    """Küçük artıkla büyük ileri hatanın birlikte bulunduğu kesin örneği üret."""

    scale = 1.0e-12
    matrix = np.diag([1.0, scale])
    exact_solution = np.array([1.0, 1.0])
    right_hand_side = matrix @ exact_solution
    candidate = np.array([1.0, 0.0])
    residual = right_hand_side - matrix @ candidate
    residual_norm = float(np.linalg.norm(residual, ord=2))
    relative_rhs_residual = residual_norm / float(
        np.linalg.norm(right_hand_side, ord=2)
    )
    forward_error = float(
        np.linalg.norm(candidate - exact_solution, ord=2)
        / np.linalg.norm(exact_solution, ord=2)
    )
    condition_number = float(np.linalg.cond(matrix, p=2))
    backward_error = residual_norm / (
        float(np.linalg.norm(matrix, ord=2) * np.linalg.norm(candidate, ord=2))
        + float(np.linalg.norm(right_hand_side, ord=2))
    )
    return {
        "matrix": matrix,
        "exact_solution": exact_solution,
        "candidate_solution": candidate,
        "right_hand_side": right_hand_side,
        "residual": residual,
        "residual_norm_2": residual_norm,
        "relative_right_hand_side_residual": relative_rhs_residual,
        "normwise_backward_error": backward_error,
        "relative_forward_error_2": forward_error,
        "condition_number_2": condition_number,
        "condition_times_relative_residual": (
            condition_number * relative_rhs_residual
        ),
    }


def scale_linear_system(
    matrix_values: Sequence[Sequence[float]] | np.ndarray,
    right_hand_side_values: Sequence[float] | np.ndarray,
    row_factors_values: Sequence[float] | np.ndarray,
    column_factors_values: Sequence[float] | np.ndarray,
) -> dict[str, np.ndarray]:
    """R A C y = R b sistemini kur; özgün çözüm x = C y olur."""

    matrix = _as_finite_matrix(matrix_values, name="matrix")
    right_hand_side = _as_finite_vector(
        right_hand_side_values, name="right_hand_side"
    )
    row_factors = _as_finite_vector(row_factors_values, name="row_factors")
    column_factors = _as_finite_vector(
        column_factors_values, name="column_factors"
    )
    rows, columns = matrix.shape
    if right_hand_side.shape[0] != rows or row_factors.shape[0] != rows:
        raise NumericalReliabilityError(
            "right_hand_side and row_factors must match the matrix rows"
        )
    if column_factors.shape[0] != columns:
        raise NumericalReliabilityError(
            "column_factors must match the matrix columns"
        )
    if np.any(row_factors <= 0.0) or np.any(column_factors <= 0.0):
        raise NumericalReliabilityError("scaling factors must be positive")
    scaled_matrix = row_factors[:, np.newaxis] * matrix
    scaled_matrix = scaled_matrix * column_factors[np.newaxis, :]
    scaled_right_hand_side = row_factors * right_hand_side
    return {
        "matrix": matrix,
        "right_hand_side": right_hand_side,
        "row_factors": row_factors,
        "column_factors": column_factors,
        "scaled_matrix": scaled_matrix,
        "scaled_right_hand_side": scaled_right_hand_side,
    }


def quintic_boundary_system(
    duration_value: float,
    *,
    seconds_per_time_unit: float,
    start_position_radian: float = 0.20,
    end_position_radian: float = 1.10,
    start_velocity_radian_per_second: float = 0.0,
    end_velocity_radian_per_second: float = 0.0,
    start_acceleration_radian_per_second_squared: float = 0.0,
    end_acceleration_radian_per_second_squared: float = 0.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Konum-hız-ivme uç koşulları için 6x6 katsayı sistemini kur."""

    duration = _as_positive_scalar(duration_value, name="duration_value")
    seconds_per_unit = _as_positive_scalar(
        seconds_per_time_unit, name="seconds_per_time_unit"
    )
    q0 = _as_finite_scalar(start_position_radian, name="start_position_radian")
    q1 = _as_finite_scalar(end_position_radian, name="end_position_radian")
    v0 = _as_finite_scalar(
        start_velocity_radian_per_second,
        name="start_velocity_radian_per_second",
    )
    v1 = _as_finite_scalar(
        end_velocity_radian_per_second,
        name="end_velocity_radian_per_second",
    )
    a0 = _as_finite_scalar(
        start_acceleration_radian_per_second_squared,
        name="start_acceleration_radian_per_second_squared",
    )
    a1 = _as_finite_scalar(
        end_acceleration_radian_per_second_squared,
        name="end_acceleration_radian_per_second_squared",
    )

    t = duration
    matrix = np.array(
        [
            [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 2.0, 0.0, 0.0, 0.0],
            [1.0, t, t**2, t**3, t**4, t**5],
            [0.0, 1.0, 2.0 * t, 3.0 * t**2, 4.0 * t**3, 5.0 * t**4],
            [0.0, 0.0, 2.0, 6.0 * t, 12.0 * t**2, 20.0 * t**3],
        ]
    )
    right_hand_side = np.array(
        [
            q0,
            v0 * seconds_per_unit,
            a0 * seconds_per_unit**2,
            q1,
            v1 * seconds_per_unit,
            a1 * seconds_per_unit**2,
        ]
    )
    return matrix, right_hand_side


def polynomial_derivative_coefficients(
    coefficient_values: Sequence[float] | np.ndarray, *, order: int = 1
) -> np.ndarray:
    """Artan kuvvet sırasındaki katsayıların belirtilen türevini döndür."""

    coefficients = _as_finite_vector(coefficient_values, name="coefficients")
    if not isinstance(order, int) or order < 0:
        raise NumericalReliabilityError("order must be a nonnegative integer")
    result = coefficients
    for _ in range(order):
        if result.size == 1:
            return np.array([0.0])
        result = np.arange(1, result.size, dtype=float) * result[1:]
    return np.array(result, dtype=float, copy=True)


def horner_evaluate(
    coefficient_values: Sequence[float] | np.ndarray, x_value: float
) -> float:
    """Artan kuvvet sırasındaki polinomu Horner düzeniyle değerlendir."""

    coefficients = _as_finite_vector(coefficient_values, name="coefficients")
    x = _as_finite_scalar(x_value, name="x_value")
    result = 0.0
    for coefficient in coefficients[::-1]:
        result = result * x + float(coefficient)
    return float(result)


def direct_power_evaluate(
    coefficient_values: Sequence[float] | np.ndarray, x_value: float
) -> float:
    """Polinomu açık kuvvet toplamıyla, öğretim karşılaştırması için hesapla."""

    coefficients = _as_finite_vector(coefficient_values, name="coefficients")
    x = _as_finite_scalar(x_value, name="x_value")
    return float(sum(float(coefficient) * x**power for power, coefficient in enumerate(coefficients)))


def trajectory_state_from_coefficients(
    coefficient_values: Sequence[float] | np.ndarray,
    time_value: float,
    *,
    seconds_per_time_unit: float,
) -> dict[str, float]:
    """Bir yörünge polinomundan fiziksel konum, hız ve ivmeyi hesapla."""

    coefficients = _as_finite_vector(coefficient_values, name="coefficients")
    if coefficients.size != 6:
        raise NumericalReliabilityError("trajectory coefficients must have length six")
    time = _as_finite_scalar(time_value, name="time_value")
    seconds_per_unit = _as_positive_scalar(
        seconds_per_time_unit, name="seconds_per_time_unit"
    )
    first = polynomial_derivative_coefficients(coefficients, order=1)
    second = polynomial_derivative_coefficients(coefficients, order=2)
    return {
        "position_radian": horner_evaluate(coefficients, time),
        "velocity_radian_per_second": (
            horner_evaluate(first, time) / seconds_per_unit
        ),
        "acceleration_radian_per_second_squared": (
            horner_evaluate(second, time) / seconds_per_unit**2
        ),
    }


def _normalized_reference_coefficients() -> np.ndarray:
    """Dinlenmeden dinlenmeye boyutsuz beşinci derece katsayılarını döndür."""

    return np.array([0.0, 0.0, 0.0, 10.0, -15.0, 6.0])


def _raw_reference_coefficients(
    *,
    duration_value: float,
    start_position_radian: float,
    end_position_radian: float,
) -> np.ndarray:
    """Boyutsuz kanonik katsayıları seçilen zaman birimine geri taşı."""

    duration = _as_positive_scalar(duration_value, name="duration_value")
    q0 = _as_finite_scalar(start_position_radian, name="start_position_radian")
    q1 = _as_finite_scalar(end_position_radian, name="end_position_radian")
    delta_q = q1 - q0
    if delta_q == 0.0:
        raise NumericalReliabilityError("trajectory displacement must be nonzero")
    normalized = _normalized_reference_coefficients()
    raw = np.zeros(6)
    raw[0] = q0 + delta_q * normalized[0]
    for power in range(1, 6):
        raw[power] = delta_q * normalized[power] / duration**power
    return raw


def _trajectory_representation(
    *,
    label: str,
    duration_value: float,
    seconds_per_time_unit: float,
    start_position_radian: float,
    end_position_radian: float,
) -> dict[str, Any]:
    """Seçilen zaman birimindeki yörünge çözümünü ve fiziksel kontrolleri üret."""

    matrix, right_hand_side = quintic_boundary_system(
        duration_value,
        seconds_per_time_unit=seconds_per_time_unit,
        start_position_radian=start_position_radian,
        end_position_radian=end_position_radian,
    )
    reference = _raw_reference_coefficients(
        duration_value=duration_value,
        start_position_radian=start_position_radian,
        end_position_radian=end_position_radian,
    )
    diagnostics = solve_with_diagnostics(
        matrix,
        right_hand_side,
        norm_order=2,
        reference_solution_values=reference,
    )
    fractions = np.linspace(0.0, 1.0, 9)
    states = [
        trajectory_state_from_coefficients(
            diagnostics.solution,
            float(fraction * duration_value),
            seconds_per_time_unit=seconds_per_time_unit,
        )
        for fraction in fractions
    ]
    return {
        "label": label,
        "duration_value": float(duration_value),
        "seconds_per_time_unit": float(seconds_per_time_unit),
        "matrix_is_dimensionally_heterogeneous": True,
        "coefficient_unit_pattern": [
            "rad",
            "rad/time_unit",
            "rad/time_unit^2",
            "rad/time_unit^3",
            "rad/time_unit^4",
            "rad/time_unit^5",
        ],
        "diagnostics": diagnostics,
        "sample_fractions": fractions,
        "states": states,
    }


def robot_trajectory_case() -> dict[str, Any]:
    """Saniye, milisaniye ve boyutsuz yörünge temsillerini karşılaştır."""

    start_position = 0.20
    end_position = 1.10
    duration_seconds = 2.0
    seconds = _trajectory_representation(
        label="seconds",
        duration_value=duration_seconds,
        seconds_per_time_unit=1.0,
        start_position_radian=start_position,
        end_position_radian=end_position,
    )
    milliseconds = _trajectory_representation(
        label="milliseconds",
        duration_value=2000.0,
        seconds_per_time_unit=0.001,
        start_position_radian=start_position,
        end_position_radian=end_position,
    )

    normalized_matrix, normalized_rhs = quintic_boundary_system(
        1.0,
        seconds_per_time_unit=1.0,
        start_position_radian=0.0,
        end_position_radian=1.0,
    )
    normalized_reference = _normalized_reference_coefficients()
    normalized = solve_with_diagnostics(
        normalized_matrix,
        normalized_rhs,
        reference_solution_values=normalized_reference,
    )

    delta_position = end_position - start_position
    fractions = np.linspace(0.0, 1.0, 9)
    normalized_states: list[dict[str, float]] = []
    for fraction in fractions:
        tau = float(fraction)
        s = horner_evaluate(normalized.solution, tau)
        ds = horner_evaluate(
            polynomial_derivative_coefficients(normalized.solution), tau
        )
        d2s = horner_evaluate(
            polynomial_derivative_coefficients(normalized.solution, order=2), tau
        )
        normalized_states.append(
            {
                "position_radian": start_position + delta_position * s,
                "velocity_radian_per_second": (
                    delta_position * ds / duration_seconds
                ),
                "acceleration_radian_per_second_squared": (
                    delta_position * d2s / duration_seconds**2
                ),
            }
        )

    def maximum_state_difference(
        left: list[dict[str, float]], right: list[dict[str, float]]
    ) -> dict[str, float]:
        keys = (
            "position_radian",
            "velocity_radian_per_second",
            "acceleration_radian_per_second_squared",
        )
        return {
            key: max(abs(a[key] - b[key]) for a, b in zip(left, right))
            for key in keys
        }

    seconds_states = seconds["states"]
    milliseconds_states = milliseconds["states"]
    return {
        "start_position_radian": start_position,
        "end_position_radian": end_position,
        "duration_seconds": duration_seconds,
        "boundary_velocity_radian_per_second": [0.0, 0.0],
        "boundary_acceleration_radian_per_second_squared": [0.0, 0.0],
        "seconds": seconds,
        "milliseconds": milliseconds,
        "normalized": {
            "time_coordinate": "tau=t/T",
            "position_coordinate": "s=(q-q0)/(q1-q0)",
            "matrix_is_dimensionless": True,
            "diagnostics": normalized,
            "states": normalized_states,
        },
        "max_seconds_vs_normalized": maximum_state_difference(
            seconds_states, normalized_states
        ),
        "max_milliseconds_vs_normalized": maximum_state_difference(
            milliseconds_states, normalized_states
        ),
        "raw_condition_numbers_are_unit_dependent": True,
        "safety_certificate": False,
    }


def vandermonde_matrix(
    node_values: Sequence[float] | np.ndarray, *, degree: int
) -> np.ndarray:
    """Artan kuvvet sıralı Vandermonde matrisini doğrulanmış düğümlerle kur."""

    nodes = _as_finite_vector(node_values, name="nodes")
    if not isinstance(degree, int) or degree < 0:
        raise NumericalReliabilityError("degree must be a nonnegative integer")
    if nodes.size < degree + 1:
        raise NumericalReliabilityError("at least degree plus one nodes are required")
    if np.unique(nodes).size != nodes.size:
        raise NumericalReliabilityError("nodes must be distinct")
    return np.vander(nodes, N=degree + 1, increasing=True)


def vandermonde_scaling_case() -> dict[str, Any]:
    """Mutlak ve merkezlenmiş zamanla aynı polinom gösterimini karşılaştır."""

    absolute_time_seconds = np.linspace(100.0, 105.0, 6)
    center_seconds = 102.5
    half_span_seconds = 2.5
    scaled_coordinate = (
        absolute_time_seconds - center_seconds
    ) / half_span_seconds
    scaled_coefficients = np.array([1.2, -0.4, 0.25, -0.10, 0.05, -0.02])
    observations = np.array(
        [horner_evaluate(scaled_coefficients, value) for value in scaled_coordinate]
    )
    raw_matrix = vandermonde_matrix(absolute_time_seconds, degree=5)
    scaled_matrix = vandermonde_matrix(scaled_coordinate, degree=5)
    raw = solve_with_diagnostics(raw_matrix, observations)
    scaled = solve_with_diagnostics(
        scaled_matrix,
        observations,
        reference_solution_values=scaled_coefficients,
    )

    check_time_seconds = 102.75
    check_scaled_coordinate = (
        check_time_seconds - center_seconds
    ) / half_span_seconds
    reference_prediction = horner_evaluate(
        scaled_coefficients, check_scaled_coordinate
    )
    raw_horner_prediction = horner_evaluate(raw.solution, check_time_seconds)
    raw_direct_prediction = direct_power_evaluate(raw.solution, check_time_seconds)
    scaled_prediction = horner_evaluate(
        scaled.solution, check_scaled_coordinate
    )
    raw_condition = float(raw.condition_number or 0.0)
    scaled_condition = float(scaled.condition_number or 0.0)
    return {
        "absolute_time_seconds": absolute_time_seconds,
        "center_seconds": center_seconds,
        "half_span_seconds": half_span_seconds,
        "scaled_coordinate": scaled_coordinate,
        "observations": observations,
        "scaled_reference_coefficients": scaled_coefficients,
        "raw": raw,
        "scaled": scaled,
        "condition_ratio_raw_to_scaled": raw_condition / scaled_condition,
        "check_time_seconds": check_time_seconds,
        "check_scaled_coordinate": check_scaled_coordinate,
        "reference_prediction": reference_prediction,
        "raw_horner_prediction": raw_horner_prediction,
        "raw_direct_prediction": raw_direct_prediction,
        "scaled_horner_prediction": scaled_prediction,
        "raw_horner_absolute_error": abs(
            raw_horner_prediction - reference_prediction
        ),
        "raw_direct_absolute_error": abs(
            raw_direct_prediction - reference_prediction
        ),
        "scaled_absolute_error": abs(scaled_prediction - reference_prediction),
        "coefficient_vectors_use_different_coordinates": True,
    }


def _optical_case_for_matrix(
    matrix: np.ndarray,
    *,
    label: str,
    true_concentration_millimole_per_litre: np.ndarray,
    absorbance_perturbation: np.ndarray,
) -> dict[str, Any]:
    """Bir duyarlılık matrisinde veri ve çözüm pertürbasyonlarını kaydet."""

    true_concentration = _as_finite_vector(
        true_concentration_millimole_per_litre,
        name="true_concentration",
    )
    perturbation = _as_finite_vector(
        absorbance_perturbation, name="absorbance_perturbation"
    )
    absorbance = matrix @ true_concentration
    measured_absorbance = absorbance + perturbation
    original = solve_with_diagnostics(
        matrix,
        absorbance,
        reference_solution_values=true_concentration,
    )
    measured = solve_with_diagnostics(matrix, measured_absorbance)
    concentration_change = measured.solution - true_concentration
    relative_data_change = float(
        np.linalg.norm(perturbation, ord=2) / np.linalg.norm(absorbance, ord=2)
    )
    relative_solution_change = float(
        np.linalg.norm(concentration_change, ord=2)
        / np.linalg.norm(true_concentration, ord=2)
    )
    return {
        "label": label,
        "sensitivity_matrix": matrix,
        "true_concentration_millimole_per_litre": true_concentration,
        "true_absorbance": absorbance,
        "absorbance_perturbation": perturbation,
        "measured_absorbance": measured_absorbance,
        "original": original,
        "measured": measured,
        "concentration_change_millimole_per_litre": concentration_change,
        "relative_data_change_2": relative_data_change,
        "relative_solution_change_2": relative_solution_change,
        "observed_amplification": relative_solution_change / relative_data_change,
        "all_concentrations_nonnegative": bool(np.all(measured.solution >= 0.0)),
        "automatic_clipping_applied": False,
    }


def optical_inverse_problem_case() -> dict[str, Any]:
    """İyi ayrılmış ve yakın paralel iki bileşenli optik sistemi karşılaştır."""

    true_concentration = np.array([0.8, 0.4])
    perturbation = np.array([1.0e-4, -1.0e-4])
    well_separated_matrix = np.array([[1.0, 0.20], [0.15, 1.10]])
    nearly_parallel_matrix = np.array([[1.0, 0.99], [0.98, 0.9703]])
    well = _optical_case_for_matrix(
        well_separated_matrix,
        label="well_separated_spectral_signatures",
        true_concentration_millimole_per_litre=true_concentration,
        absorbance_perturbation=perturbation,
    )
    ill = _optical_case_for_matrix(
        nearly_parallel_matrix,
        label="nearly_parallel_spectral_signatures",
        true_concentration_millimole_per_litre=true_concentration,
        absorbance_perturbation=perturbation,
    )
    return {
        "physical_model": "two-wavelength linear Beer-Lambert superposition",
        "path_length_centimetre": 1.0,
        "absorbance_unit": "dimensionless",
        "concentration_unit": "mmol/L",
        "sensitivity_entry_unit": "L/mmol",
        "linearity_assumption": True,
        "homogeneous_narrow_band_assumption": True,
        "synthetic_data": True,
        "well_separated": well,
        "nearly_parallel": ill,
        "condition_ratio": (
            float(ill["measured"].condition_number or 0.0)
            / float(well["measured"].condition_number or 1.0)
        ),
        "laboratory_certificate": False,
    }


def _json_ready(value: Any) -> Any:
    """NumPy ve veri sınıfı nesnelerini katı JSON tiplerine dönüştür."""

    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _json_ready(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    if isinstance(value, float):
        if not math.isfinite(value):
            raise NumericalReliabilityError(
                "non-finite value cannot be serialized to strict JSON"
            )
        return value
    return value


def chapter_results() -> dict[str, Any]:
    """Bölüm 10'un bütün deterministik kanıtlarını tek kayıtta topla."""

    result = {
        "schema_version": "1.0",
        "version": "v1.1",
        "chapter": 10,
        "chapter_title": "Sayisal Dogruluk ve Kosulluluk",
        "vector_convention": "column_vectors_left_multiplication",
        "residual_convention": "right_hand_side_minus_matrix_times_solution",
        "condition_norm_default": "2-norm",
        "external_data": False,
        "randomness": False,
        "automatic_clipping": False,
        "explicit_matrix_inverse_for_solves": False,
        "assumptions": [
            "real finite-dimensional vector spaces",
            "core solve diagnostics use square nonsingular matrices",
            "floating-point local relative-error model excludes overflow and subnormal-relative-error claims",
            "raw dimensional condition numbers are not compared as physical invariants",
            "robot trajectory data are synthetic and deterministic",
            "optical sensitivities are synthetic and use linear superposition",
            "forward error is reported only when a reference solution is supplied",
            "no physical safety or laboratory certificate is produced",
        ],
        "units": {
            "robot_position": "rad",
            "robot_velocity": "rad/s",
            "robot_acceleration": "rad/s^2",
            "optical_absorbance": "dimensionless",
            "optical_concentration": "mmol/L",
            "backward_error": "dimensionless",
            "condition_number": "dimensionless_after_coordinate_contract",
        },
        "floating_point_environment": floating_point_environment(),
        "arithmetic_experiments": arithmetic_experiments(),
        "norm_examples": norm_examples(),
        "perturbation_bound": perturbation_bound_case(),
        "small_residual_large_error": small_residual_large_error_case(),
        "robot_trajectory": robot_trajectory_case(),
        "vandermonde_scaling": vandermonde_scaling_case(),
        "optical_inverse_problem": optical_inverse_problem_case(),
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "platform": platform.platform(),
        },
    }
    return _json_ready(result)


def print_human_readable(results: dict[str, Any]) -> None:
    """Kanonik kaydın kısa, birimli insan-okur özetini yazdır."""

    environment = results["floating_point_environment"]
    small = results["small_residual_large_error"]
    trajectory = results["robot_trajectory"]
    vandermonde = results["vandermonde_scaling"]
    optical = results["optical_inverse_problem"]
    print("Bölüm 10 - Sayısal Doğruluk ve Koşulluluk")
    print(f"binary64 eps: {environment['eps']:.17g}")
    print(
        "Küçük artık örneği: "
        f"göreli artık={small['relative_right_hand_side_residual']:.3e}, "
        f"göreli ileri hata={small['relative_forward_error_2']:.3e}"
    )
    print(
        "Robot ham koşul sayıları [s, ms]: "
        f"{trajectory['seconds']['diagnostics']['condition_number']:.3e}, "
        f"{trajectory['milliseconds']['diagnostics']['condition_number']:.3e}"
    )
    print(
        "Vandermonde koşul oranı ham/ölçekli: "
        f"{vandermonde['condition_ratio_raw_to_scaled']:.3e}"
    )
    print(
        "Optik ters problem koşul oranı: "
        f"{optical['condition_ratio']:.3e}; "
        "otomatik kırpma: hayır"
    )
    print("Dış veri: hayır; rastgelelik: hayır; fiziksel sertifika: hayır")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Komut satırı seçeneklerini ayrıştır."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json", action="store_true", help="Kanonik JSON kanıt kaydını yazdır."
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Bölüm sonuçlarını üret ve seçilen görünümde yazdır."""

    arguments = parse_args(argv)
    try:
        results = chapter_results()
    except NumericalReliabilityError as exc:
        print(f"ERROR: {exc}")
        return 2
    if arguments.json:
        print(json.dumps(results, ensure_ascii=False, allow_nan=False, indent=2))
    else:
        print_human_readable(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
