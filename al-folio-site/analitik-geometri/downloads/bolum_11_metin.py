# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Bölüm 11: radikal eksen, merkez ve güç hücresi ---
import numpy as np
from agbook import (
    point_power,
    radical_axis_diagnostics,
    radical_center_diagnostics,
)

centers = np.array([[0., 0.], [8., 0.], [0., 6.]])
radii = np.array([5., 3., 4.])  # km
tol = dict(
    absolute_tolerance=1e-10,
    relative_tolerance=1e-12,
    reference_scale=20.0,
)
axis12 = radical_axis_diagnostics(
    centers[0], radii[0], centers[1], radii[1], **tol
)
center = radical_center_diagnostics(
    centers, radii, angular_tolerance=1e-12, **tol
)
powers = [
    point_power(c, r, center.point)
    for c, r in zip(centers, radii)
]
print(axis12.relation, axis12.line_coefficients)
print(center.relation, center.point, powers)
