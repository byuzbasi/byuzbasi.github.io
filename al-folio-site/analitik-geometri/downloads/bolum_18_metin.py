# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Üç noktadan datum ve iki düzlemden eksen ---
import numpy as np
from agbook import (
    affine_system_diagnostics_3d,
    canonical_plane_coefficients,
    plane_from_points_3d,
)

A = np.array([120.0, 80.0, 35.0])
B = np.array([156.0, 128.0, 35.0])
C = np.array([96.0, 98.0, 75.0])

datum = plane_from_points_3d(A, B, C)
same = canonical_plane_coefficients(-25.0 * datum)

r1 = np.array([0.60, 0.80, 0.0])
r2 = np.array([-0.48, 0.36, 0.80])
M = np.vstack([r1, r2])
b = M @ A
diagnosis = affine_system_diagnostics_3d(
    M,
    b,
    rank_relative_tolerance=1e-12,
    reference_scale=200.0,
)

print(datum)
print(np.allclose(datum, same))
print(diagnosis.coefficient_rank)
print(diagnosis.solution_dimension)
print(diagnosis.classification)
print(diagnosis.maximum_equation_residual)
