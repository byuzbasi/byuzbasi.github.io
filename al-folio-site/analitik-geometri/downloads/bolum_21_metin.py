# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Bölüm 21: dönel yüzey profilinin doğrulanması ---
import numpy as np
from agbook import (
    piecewise_linear_revolution_diagnostics,
    surface_of_revolution_points,
)

s = np.array([0.0, 30.0, 60.0, 90.0])
rho = np.array([18.0, 18.0, 12.0, 12.0])
theta = np.linspace(0.0, 2.0*np.pi, 73)

out = piecewise_linear_revolution_diagnostics(s, rho)
mesh = surface_of_revolution_points(
    [40.0, -25.0, 15.0], [2.0, -1.0, 2.0],
    s, rho, theta, radial_reference=[1.0, 2.0, 0.0]
)

assert out.segment_types == ("cylinder", "frustum", "cylinder")
assert out.smooth_interior_joins == (False, False)
np.testing.assert_allclose(mesh[:, 0], mesh[:, -1])
np.testing.assert_allclose(
    out.total_lateral_area,
    180.0*np.pi*(10.0 + np.sqrt(26.0)),
)
