# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Dört doğru sınıfının otomatik sınanması ---
import numpy as np
from agbook import line_line_diagnostics_3d

opts = dict(
    angular_tolerance=1e-12,
    absolute_tolerance=1e-10,
    relative_tolerance=0.0,
    reference_scale=1.0,
)
cases = [
    ([0,0,0], [1,0,0], [2,0,0], [-3,0,0], "coincident"),
    ([0,0,0], [1,0,0], [0,2,0], [-3,0,0], "parallel"),
    ([0,0,0], [1,0,0], [1,-1,0], [0,1,0], "intersecting"),
    ([0,0,0], [1,0,0], [0,1,1], [0,1,0], "skew"),
]
for p, u, q, v, expected in cases:
    result = line_line_diagnostics_3d(p, u, q, v, **opts)
    assert result.relation == expected
    np.testing.assert_allclose(result.first_line_residual, 0, atol=1e-12)
    np.testing.assert_allclose(result.second_line_residual, 0, atol=1e-12)
    np.testing.assert_allclose(result.first_orthogonality_residual, 0, atol=1e-12)
    np.testing.assert_allclose(result.second_orthogonality_residual, 0, atol=1e-12)
