"""Bölüm 3 laboratuvarı: sıralı güvenlik bölgesinin alanı ve yönelimi."""

from __future__ import annotations

import numpy as np
from sympy import Matrix

from agbook import (
    determinant_2d,
    orientation_diagnostics,
    polygon_area,
    polygon_signed_area,
    triangle_area,
)


boundary = np.array(
    [
        [0.0, 0.0],
        [6.0, 0.0],
        [7.0, 3.0],
        [4.5, 5.0],
        [1.0, 4.0],
    ]
)
tolerance = 1.0e-10

signed_area = polygon_signed_area(boundary)
area = polygon_area(boundary)
fan_area = sum(triangle_area(boundary[0], boundary[i], boundary[i + 1]) for i in range(1, len(boundary) - 1))
first_turn = orientation_diagnostics(*boundary[:3], relative_tolerance=tolerance)
reversed_area = polygon_signed_area(boundary[::-1])
translated_area = polygon_signed_area(boundary + np.array([1.0e9, -2.0e9]))

linear_map = np.array([[1.2, 0.3], [-0.2, 0.8]])
mapped = boundary @ linear_map.T
area_scale = determinant_2d(linear_map[:, 0], linear_map[:, 1])
mapped_ratio = polygon_area(mapped) / area

near = np.array([[0.0, 0.0], [1.0e8, 1.0e8], [2.0e8, 2.0e8 + 1.0]])
near_result = orientation_diagnostics(*near, relative_tolerance=1.0e-8)
exact_double_area = Matrix(
    [
        [100000000, 100000000],
        [200000000, 200000001],
    ]
).det()

print(f"yonlu_alan_m2: {signed_area:.6f}")
print(f"alan_m2: {area:.6f}")
print(f"ilk_donus: {first_turn.classification}")
print(f"ucgen_yelpazesi_m2: {fan_area:.6f}")
print(f"ters_sira_yonlu_alan_m2: {reversed_area:.6f}")
print(f"oteleme_farki_m2: {translated_area - signed_area:.3e}")
print(f"donusum_determinanti: {area_scale:.6f}")
print(f"donusmus_alan_orani: {mapped_ratio:.6f}")
print(f"yakin_normalize_determinant: {near_result.normalized_determinant:.6e}")
print(f"yakin_sinif: {near_result.classification}")
print(f"kesin_iki_kat_alan: {exact_double_area}")
