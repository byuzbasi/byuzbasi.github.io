# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Vektörel çarpım karşılaştırması ---
import numpy as np
from agbook import cross_product_3d

pairs = [
    ([1, 0, 0], [0, 1, 0]),
    ([2, -1, 3], [4, 5, -2]),
    ([1, 2, 0], [-3, 1, 4]),
    ([0, 0, 5], [2, -7, 0]),
    ([1, 2, 3], [2, 4, 6]),
]
for u_raw, v_raw in pairs:
    u = np.asarray(u_raw, dtype=float)
    v = np.asarray(v_raw, dtype=float)
    result = cross_product_3d(u, v)
    np.testing.assert_allclose(result, np.cross(u, v))
    np.testing.assert_allclose(result @ u, 0.0, atol=1e-14)
    np.testing.assert_allclose(result @ v, 0.0, atol=1e-14)

# --- 2. Öteleme değişmezliği ---
import numpy as np
from agbook import triangle_area_3d, unit_normal_3d

points = np.array([[1., 0., 2.], [4., 1., 2.], [2., 5., 4.]])
translations = np.array([
    [0., 0., 0.], [10., -4., 7.], [-3., 8., 2.],
    [1e3, -2e3, 3e3], [-0.25, 0.5, -0.75],
])
area0 = triangle_area_3d(*points)
normal0 = unit_normal_3d(points[1] - points[0], points[2] - points[0])
for shift in translations:
    moved = points + shift
    np.testing.assert_allclose(triangle_area_3d(*moved), area0)
    np.testing.assert_allclose(
        unit_normal_3d(moved[1] - moved[0], moved[2] - moved[0]),
        normal0,
    )

# --- 3. Dönme ve yansıma yasası ---
import numpy as np
from agbook import cross_product_3d

R = np.array([
    [3/5, -12/25, 16/25],
    [4/5,   9/25, -12/25],
    [0,    20/25, 15/25],
], dtype=float)
Q = np.diag([-1., 1., 1.])
pairs = [
    (np.array([1., 2., 3.]), np.array([2., -1., 4.])),
    (np.array([3., 0., -2.]), np.array([1., 5., 1.])),
    (np.array([0., 1., 0.]), np.array([0., 0., 1.])),
]
for transform in (R, Q):
    sign = np.linalg.det(transform)
    for u, v in pairs:
        np.testing.assert_allclose(
            cross_product_3d(transform @ u, transform @ v),
            sign * transform @ cross_product_3d(u, v),
            atol=2e-14,
        )
print(np.linalg.det(R), np.linalg.det(Q))  # 1.0, -1.0

# --- 4. Yakın eşdüzlemlilik tablosu ---
from agbook import spatial_orientation_diagnostics

deltas = [0.0, 1e-16, 1e-14, 1e-10, 1e-6]
tolerances = [0.0, 1e-12, 1e-8]
for delta in deltas:
    for tolerance in tolerances:
        result = spatial_orientation_diagnostics(
            [1., 0., 0.], [0., 1., 0.], [1., 1., delta],
            relative_tolerance=tolerance,
        )
        print(delta, tolerance,
              result.normalized_triple_product,
              result.classification)
