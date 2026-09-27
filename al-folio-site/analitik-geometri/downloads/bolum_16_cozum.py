# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Afin ve homojen matris özdeşliği ---
import numpy as np
from agbook import quadratic_conic_matrices

cases = [
    [1, 0, 1, 0, 0, -1],
    [1, 0, -1, 0, 0, -1],
    [1, 2, 1, -4, 4, 0],
    [0, 0, 0, 6, 8, -10],
    [3, -8, 2, 6, -10, -7],
]
X = np.array([1.25, -0.75])
Xh = np.r_[X, 1.0]
for c in cases:
    A, B, C, D, E, F0 = c
    raw = A*X[0]**2 + B*X[0]*X[1] + C*X[1]**2 \
          + D*X[0] + E*X[1] + F0
    Q, g, H = quadratic_conic_matrices(c)
    np.testing.assert_allclose(X @ Q @ X + 2*g @ X + F0, raw)
    np.testing.assert_allclose(Xh @ H @ Xh, raw)

# --- 2. Tam katalog için küçük sınıflandırma tablosu ---
from agbook import quadratic_conic_diagnostics

cases = {
    "ellipse": [1/9, 0, 1/4, 0, 0, -1],
    "hyperbola": [1/9, 0, -1/4, 0, 0, -1],
    "parabola": [1, 0, 0, 0, -4, 0],
    "point": [1, 0, 1, 0, 0, 0],
    "intersecting_lines": [1, 0, -1, 0, 0, 0],
    "parallel_lines": [1, 0, 0, 0, 0, -4],
    "double_line": [1, 0, 0, -4, 0, 4],
    "line": [0, 0, 0, 2, -4, 6],
    "empty": [1, 0, 1, 0, 0, 1],
    "plane": [0, 0, 0, 0, 0, 0],
}
for expected, coefficients in cases.items():
    result = quadratic_conic_diagnostics(coefficients)
    assert result.locus_type == expected
    print(expected, result.quadratic_rank, result.homogeneous_rank)

# --- 3. Dönme ve öteleme kovaryansı ---
import numpy as np
from agbook import (
    quadratic_conic_diagnostics,
    quadratic_conic_residuals,
    rotation_matrix_2d,
    transform_quadratic_conic,
)

R = rotation_matrix_2d(np.deg2rad(37.0))
center = np.array([4.0, -2.0])
canonical = np.array([1/25, 0, 1/9, 0, 0, -1])
general = transform_quadratic_conic(
    canonical, R.T, -R.T @ center
)
result = quadratic_conic_diagnostics(
    general, coordinate_scale=5.0, relative_tolerance=1e-12
)
canonical_result = quadratic_conic_diagnostics(
    canonical, coordinate_scale=5.0, relative_tolerance=1e-12
)
np.testing.assert_allclose(result.center, center, atol=1e-12)
np.testing.assert_allclose(result.semi_axes, [5, 3], atol=1e-12)

Y = np.array([[0.0, 0.0], [1.0, -3.0], [2.0, 1.0]])
X = Y @ R.T + center
old = quadratic_conic_residuals(general, X, coordinate_scale=5.0)
new = quadratic_conic_residuals(canonical, Y, coordinate_scale=5.0)
np.testing.assert_allclose(
    old * result.normalization_factor,
    new * canonical_result.normalization_factor,
    atol=1e-12,
)

# --- 4. Yakın rank sınırını açık eşikle raporlama ---
from agbook import quadratic_conic_diagnostics

c = [1.0, 0.0, 1e-14, 0.0, 0.0, -1.0]
exact_float = quadratic_conic_diagnostics(c, relative_tolerance=0.0)
thresholded = quadratic_conic_diagnostics(c, relative_tolerance=1e-12)

print(exact_float.locus_type, exact_float.quadratic_rank,
      exact_float.numerically_ambiguous)
print(thresholded.locus_type, thresholded.quadratic_rank,
      thresholded.numerically_ambiguous)
