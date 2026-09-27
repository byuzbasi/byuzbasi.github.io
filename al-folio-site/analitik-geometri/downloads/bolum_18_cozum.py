# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Parametrik doğru değişmezleri ---
import numpy as np
import pytest
from agbook import parametric_line_points_3d

P = np.array([2.0, -1.0, 3.0])
v = np.array([4.0, 2.0, -2.0])
t = np.array([-2.0, -0.5, 0.0, 1.0, 3.0])
points = parametric_line_points_3d(P, v, t)

for delta in points - P:
    np.testing.assert_allclose(np.cross(delta, v), 0.0, atol=1e-13)

with pytest.raises(ValueError):
    parametric_line_points_3d(P, np.zeros(3), t)

# --- 2. Düzlem ölçek eşdeğerliği ---
import numpy as np
from agbook import canonical_plane_coefficients, plane_residuals_3d

plane = np.array([2.0, -4.0, 4.0, -10.0])
factors = np.array([-7.0, -0.5, 0.25, 3.0, 20.0])
points = np.array([
    [0.0, 0.0, 0.0],
    [1.0, 0.0, 2.0],
    [5.0, 0.0, 0.0],
    [2.0, -1.0, 1.0],
])
target = canonical_plane_coefficients(plane)
base_residual = plane_residuals_3d(plane, points)

for factor in factors:
    scaled = factor * plane
    np.testing.assert_allclose(
        canonical_plane_coefficients(scaled), target, atol=1e-14
    )
    np.testing.assert_allclose(
        plane_residuals_3d(scaled, points),
        factor * base_residual,
        atol=1e-13,
    )

# --- 3. Beş afin çözüm sınıfı ---
import numpy as np
from agbook import affine_system_diagnostics_3d

systems = {
    "space": (np.empty((0, 3)), np.empty(0)),
    "plane": (np.array([[1.0, 0.0, 0.0]]), np.array([2.0])),
    "line": (
        np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]),
        np.array([2.0, 3.0]),
    ),
    "point": (np.eye(3), np.array([2.0, 3.0, 4.0])),
    "empty": (
        np.array([[1.0, 0.0, 0.0], [1.0, 0.0, 0.0]]),
        np.array([0.0, 1.0]),
    ),
}

for expected, (A, b) in systems.items():
    result = affine_system_diagnostics_3d(
        A, b, rank_relative_tolerance=1e-12, reference_scale=10.0
    )
    assert result.classification == expected

# --- 4. Yakın bağımlılık ve açık rank eşiği ---
import numpy as np
from agbook import affine_system_diagnostics_3d

r1 = np.array([0.60, 0.80, 0.0])
r2 = np.array([-0.48, 0.36, 0.80])
P = np.array([120.0, 80.0, 35.0])

for delta in [0.0, 1e-14, 1e-10, 1e-6]:
    A = np.vstack([r1, r1 + delta * r2])
    b = A @ P
    for tolerance in [1e-8, 1e-12]:
        result = affine_system_diagnostics_3d(
            A,
            b,
            rank_relative_tolerance=tolerance,
            reference_scale=200.0,
        )
        print(delta, tolerance, result.classification,
              result.coefficient_singular_values,
              result.maximum_equation_residual)
