# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Genel bir kuadriği sınıflandırma ve iz çıkarma ---
import numpy as np
from agbook import (
    quadric_diagnostics,
    quadric_plane_trace,
    quadratic_conic_diagnostics,
)

# x^2/4 + y^2/9 + z^2/16 = 1
coeff = np.array([1/4, 0, 0, 1/9, 0, 1/16, 0, 0, 0, -1])
d = quadric_diagnostics(coeff, coordinate_scale=4.0)
assert d.locus_type == "ellipsoid"
np.testing.assert_allclose(d.center, [0, 0, 0])
np.testing.assert_allclose(d.semi_axes, [4, 3, 2])

# z = 0 düzlemindeki iz
B = np.array([[1, 0], [0, 1], [0, 0]], dtype=float)
trace = quadric_plane_trace(coeff, [0, 0, 0], B)
conic = quadratic_conic_diagnostics(trace.conic_coefficients)
assert trace.orthonormal and conic.locus_type == "ellipse"
