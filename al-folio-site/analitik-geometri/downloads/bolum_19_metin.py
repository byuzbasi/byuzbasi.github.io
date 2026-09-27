# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Uzay ilişkileri ve izdüşüm için yinelenebilir denetim ---
import numpy as np
from agbook import (
    line_line_diagnostics_3d,
    project_point_to_plane_3d,
)

opts = dict(
    angular_tolerance=1e-12,
    absolute_tolerance=1e-10,
    relative_tolerance=0.0,
    reference_scale=1.0,
)
pair = line_line_diagnostics_3d(
    [0, 0, 0], [1, 0, 0],
    [0, 1, 1], [0, 1, 0],
    **opts,
)
projection = project_point_to_plane_3d(
    [0, 0, 1, -2], [1, 3, 5]
)

assert pair.relation == "skew"
np.testing.assert_allclose(pair.distance, 1.0)
np.testing.assert_allclose(
    pair.separation_vector, [0, 0, 1]
)
np.testing.assert_allclose(projection.foot, [1, 3, 2])
np.testing.assert_allclose(projection.distance, 3.0)
print(pair.relation, pair.distance)
print(projection.foot, projection.distance)
