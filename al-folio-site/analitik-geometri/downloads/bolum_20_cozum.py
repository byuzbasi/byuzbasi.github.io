# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Genel küre sınıflarının ve ölçek değişmezliğinin sınanması ---
import numpy as np
from agbook import general_sphere_diagnostics

cases = [
    ([1, 0, 0, 0, -4], "sphere"),
    ([1, 0, 0, 0,  0], "point"),
    ([1, 0, 0, 0,  1], "empty"),
]
for coefficients, expected in cases:
    base = general_sphere_diagnostics(coefficients)
    scaled = general_sphere_diagnostics(
        -7.0 * np.asarray(coefficients, dtype=float)
    )
    assert base.locus_type == expected
    assert scaled.locus_type == expected
    np.testing.assert_allclose(
        scaled.normalized_coefficients,
        base.normalized_coefficients,
    )

# --- 2. Doğru ve düzlem kesitlerinin artıklarla sınanması ---
import numpy as np
from agbook import (
    line_sphere_intersections_3d,
    sphere_plane_section_diagnostics,
)

opts = dict(
    absolute_tolerance=1e-12,
    relative_tolerance=1e-12,
    reference_scale=10.0,
)
line_cases = [
    (5.0, [0, 3, 0], "secant"),
    (5.0, [0, 5, 0], "tangent"),
    (5.0, [0, 6, 0], "disjoint"),
    (0.0, [0, 0, 0], "point"),
]
for radius, anchor, expected in line_cases:
    out = line_sphere_intersections_3d(
        [0, 0, 0], radius, anchor, [1, 0, 0], **opts
    )
    assert out.relation == expected
    np.testing.assert_allclose(out.line_residuals, 0, atol=1e-12)
    if expected in {"secant", "point"}:
        np.testing.assert_allclose(out.radial_residuals, 0, atol=1e-12)

plane_cases = [
    (5.0, [0, 0, 1,  0], "circle"),
    (5.0, [0, 0, 1, -5], "tangent"),
    (5.0, [0, 0, 1, -6], "disjoint"),
    (0.0, [0, 0, 1,  0], "point"),
]
for radius, plane, expected in plane_cases:
    out = sphere_plane_section_diagnostics(
        [0, 0, 0], radius, plane, **opts
    )
    assert out.relation == expected
    np.testing.assert_allclose(
        out.section_center_plane_residual, 0, atol=1e-12
    )

# --- 3. İki kürenin yedi konumunun sınanması ---
from agbook import sphere_sphere_intersection_diagnostics

opts = dict(
    absolute_tolerance=1e-12,
    relative_tolerance=1e-12,
    reference_scale=20.0,
)
cases = [
    ([0,0,0], 5, [0,0,0], 5, "coincident"),
    ([0,0,0], 5, [0,0,0], 3, "concentric_disjoint"),
    ([0,0,0], 5, [11,0,0], 5, "separate"),
    ([0,0,0], 5, [10,0,0], 5, "externally_tangent"),
    ([0,0,0], 5, [6,0,0], 5, "intersection_circle"),
    ([0,0,0], 5, [2,0,0], 3, "internally_tangent"),
    ([0,0,0], 5, [1,0,0], 3, "contained"),
]
for c1, r1, c2, r2, expected in cases:
    forward = sphere_sphere_intersection_diagnostics(
        c1, r1, c2, r2, **opts
    )
    reverse = sphere_sphere_intersection_diagnostics(
        c2, r2, c1, r1, **opts
    )
    assert forward.relation == reverse.relation == expected

# --- 4. Permütasyon, rijit hareket ve birim dönüşümü ---
import numpy as np
from agbook import sphere_system_diagnostics

C = np.array([
    [0., 0., 0.], [12., 0., 0.],
    [0., 16., 0.], [0., 0., 20.],
])
r = np.sqrt([196., 244., 260., 116.])
opts = dict(
    rank_tolerance=1e-12,
    absolute_tolerance=1e-11,
    relative_tolerance=1e-12,
    reference_scale=20.0,
)
base = sphere_system_diagnostics(C, r, **opts)
order = [2, 0, 3, 1]
permuted = sphere_system_diagnostics(C[order], r[order], **opts)
np.testing.assert_allclose(permuted.anchor, base.anchor)

Q = np.array([[0.,-1.,0.], [1.,0.,0.], [0.,0.,1.]])
t = np.array([30., -10., 7.])
moved = sphere_system_diagnostics(
    C @ Q.T + t, r,
    rank_tolerance=1e-12,
    absolute_tolerance=1e-11,
    relative_tolerance=1e-12,
    reference_scale=60.0,
)
np.testing.assert_allclose(moved.anchor, Q @ base.anchor + t)

c = 100.0
scaled = sphere_system_diagnostics(
    c*C, c*r,
    rank_tolerance=1e-12,
    absolute_tolerance=c*1e-11,
    relative_tolerance=1e-12,
    reference_scale=c*20.0,
)
np.testing.assert_allclose(scaled.anchor, c*base.anchor)
assert scaled.rank == base.rank
np.testing.assert_allclose(
    scaled.condition_number, base.condition_number
)
