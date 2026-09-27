# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Eksen çerçevesi değişmezlik sınaması ---
import numpy as np
from agbook import axis_frame_3d

directions = [
    [1,0,0], [0,1,0], [0,0,1],
    [-2,0,0], [1,2,3], [-4,5,-6],
]
for w in directions:
    f = axis_frame_3d([3,-2,7], w)
    B = np.column_stack((f.radial_u, f.radial_v, f.unit_axis))
    np.testing.assert_allclose(B.T @ B, np.eye(3), atol=2e-15)
    np.testing.assert_allclose(np.linalg.det(B), 1.0, atol=2e-15)

base = axis_frame_3d([0,0,0], [1,2,3], radial_reference=[1,0,0])
for c in [0.25, 3.0, 1000.0]:
    out = axis_frame_3d(
        [0,0,0], c*np.array([1.,2.,3.]), radial_reference=[1,0,0]
    )
    np.testing.assert_allclose(out.unit_axis, base.unit_axis)
    np.testing.assert_allclose(out.radial_u, base.radial_u)
    np.testing.assert_allclose(out.radial_v, base.radial_v)

# --- 2. Sonlu silindir üyelik tablosu ---
from agbook import circular_cylinder_diagnostics

cases = [
    ([1,0,2], "inside", "within"),
    ([3,0,2], "outside", "within"),
    ([2,0,2], "on_surface", "within"),
    ([1,0,0], "inside", "lower_boundary"),
    ([1,0,5], "inside", "upper_boundary"),
    ([1,0,6], "inside", "above"),
]
for point, radial, axial in cases:
    out = circular_cylinder_diagnostics(
        [0,0,0], [0,0,1], 2.0, point, axial_bounds=(0.0, 5.0)
    )
    assert out.radial_relation == radial
    assert out.axial_relation == axial
    print(point, radial, axial, out.lateral_surface_member,
          out.cap_member, out.closed_solid_member)

# --- 3. Koni kanatları ve tepe sınaması ---
import numpy as np
from agbook import circular_cone_diagnostics

opts = dict(absolute_tolerance=2e-15, reference_scale=3.0)
cases = [
    ([0,0,0], "double", "apex", "on_surface"),
    ([1,0,1], "double", "positive", "on_surface"),
    ([1,0,-1], "double", "negative", "on_surface"),
    ([0.5,0,1], "double", "positive", "inside"),
    ([2,0,1], "double", "positive", "outside"),
    ([1,0,-1], "positive", "negative", "wrong_nappe"),
]
for point, nappe, side, relation in cases:
    out = circular_cone_diagnostics(
        [0,0,0], [0,0,1], np.pi/4, point, nappe=nappe, **opts
    )
    assert out.side == side
    assert out.relation == relation

# --- 4. Dikiş, rijit hareket ve alan ölçeği ---
import numpy as np
from agbook import (
    piecewise_linear_revolution_diagnostics,
    surface_of_revolution_points,
)

A = np.array([1., -2., 3.])
w = np.array([2., -1., 2.])
s = np.array([0., 2., 5.])
rho = np.array([1., 3., 2.])
theta = np.linspace(0., 2*np.pi, 49)
reference = np.array([1., 0., 0.])
mesh = surface_of_revolution_points(
    A, w, s, rho, theta, radial_reference=reference
)
np.testing.assert_allclose(mesh[:, 0], mesh[:, -1], atol=2e-14)

Q = np.array([[0.,-1.,0.], [1.,0.,0.], [0.,0.,1.]])
t = np.array([8., 4., -5.])
moved = surface_of_revolution_points(
    Q@A+t, Q@w, s, rho, theta, radial_reference=Q@reference
)
np.testing.assert_allclose(moved, mesh@Q.T+t, atol=3e-14)

base = piecewise_linear_revolution_diagnostics(s, rho)
c = 0.001
scaled = piecewise_linear_revolution_diagnostics(c*s, c*rho)
np.testing.assert_allclose(
    scaled.total_lateral_area, c**2*base.total_lateral_area
)
