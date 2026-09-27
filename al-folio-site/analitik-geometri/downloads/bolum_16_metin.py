# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Altı katsayıdan genel konik tanısı ---
import numpy as np
from agbook import (
    quadratic_conic_diagnostics,
    quadratic_conic_residuals,
    rotation_matrix_2d,
    transform_quadratic_conic,
)

center = np.array([120.0, 80.0])       # mm
axes = np.array([45.0, 20.0])          # mm
angle = np.deg2rad(32.0)
R = rotation_matrix_2d(angle)

canonical = np.array([
    1 / axes[0]**2, 0.0, 1 / axes[1]**2,
    0.0, 0.0, -1.0,
])
coefficients = transform_quadratic_conic(
    canonical, R.T, -R.T @ center
)
diagnosis = quadratic_conic_diagnostics(
    coefficients,
    coordinate_scale=100.0,
    relative_tolerance=1e-12,
)

t = np.linspace(0.0, 2*np.pi, 25, endpoint=False)
local = np.column_stack([
    axes[0] * np.cos(t), axes[1] * np.sin(t)
])
points = local @ R.T + center
residuals = quadratic_conic_residuals(
    coefficients, points, coordinate_scale=100.0
)

print(diagnosis.locus_type)
print(diagnosis.center)
print(diagnosis.semi_axes)
print(np.rad2deg(diagnosis.orientation_radians))
print(np.max(np.abs(residuals)))
