# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1.  ---
import numpy as np
from agbook import sphere_system_diagnostics

centers = np.array([
    [0.0, 0.0, 0.0],
    [12.0, 0.0, 0.0],
    [0.0, 16.0, 0.0],
    [0.0, 0.0, 20.0],
])
radii = np.sqrt([196.0, 244.0, 260.0, 116.0])
options = dict(
    rank_tolerance=1e-12,
    absolute_tolerance=1e-11,
    relative_tolerance=1e-12,
    reference_scale=20.0,
)

three = sphere_system_diagnostics(centers[:3], radii[:3], **options)
four = sphere_system_diagnostics(centers, radii, **options)

assert three.relation == "line"
assert three.common_locus_type == "two_points"
np.testing.assert_allclose(
    three.common_points,
    [[4.0, 6.0, -12.0], [4.0, 6.0, 12.0]],
)
assert four.relation == "point"
assert four.common_locus_type == "point"
np.testing.assert_allclose(four.anchor, [4.0, 6.0, 12.0])
np.testing.assert_allclose(four.power_values, 0.0, atol=1e-12)
