# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. İki elips kurucusunun eşdeğerliği ---
import numpy as np
from agbook import (
    ellipse_frame_from_center_axes,
    ellipse_frame_from_foci,
)

first = ellipse_frame_from_center_axes([1., -2.], [2., 1.], 7., 4.)
second = ellipse_frame_from_foci(
    first.first_focus, first.second_focus, first.semi_major
)

for name in ("center", "first_focus", "second_focus", "major_direction"):
    assert np.allclose(getattr(first, name), getattr(second, name))
assert np.isclose(first.semi_minor, second.semi_minor)
assert np.isclose(first.eccentricity, second.eccentricity)
print(first.focal_distance, first.eccentricity)

# --- 2. Üyelik ve teğet artıkları ---
import numpy as np
from agbook import (
    ellipse_algebraic_residuals,
    ellipse_focal_sum_residuals,
    ellipse_frame_from_center_axes,
    ellipse_points,
    ellipse_tangent_line,
)

frame = ellipse_frame_from_center_axes([0., 0.], [1., 0.], 5., 3.)
t = np.linspace(0., 2. * np.pi, 8, endpoint=False)
points = ellipse_points([0., 0.], [1., 0.], 5., 3., t)
r_alg = ellipse_algebraic_residuals(points, [0., 0.], [1., 0.], 5., 3.)
r_sum = ellipse_focal_sum_residuals(
    points, frame.first_focus, frame.second_focus, 5.
)
lines = np.vstack([
    ellipse_tangent_line([0., 0.], [1., 0.], 5., 3., value)
    for value in t
])
r_tan = np.sum(lines[:, :2] * points, axis=1) + lines[:, 2]
print(np.max(np.abs(r_alg)), np.max(np.abs(r_sum)), np.max(np.abs(r_tan)))
assert np.max(np.abs(r_alg)) < 2e-15
assert np.max(np.abs(r_sum)) < 1e-14
assert np.max(np.abs(r_tan)) < 1e-14

# --- 3. Yansımanın rijit hareket altında kovaryantlığı ---
import numpy as np
from agbook import ellipse_reflection_diagnostics, rotation_matrix_2d

t = np.linspace(0., 2. * np.pi, 19, endpoint=False)
before = ellipse_reflection_diagnostics([0., 0.], [1., 0.], 10., 6., t)
Q = rotation_matrix_2d(np.deg2rad(37.))
shift = np.array([5., -3.])
after = ellipse_reflection_diagnostics(shift, Q @ np.array([1., 0.]), 10., 6., t)

assert np.allclose(after.points, before.points @ Q.T + shift)
assert np.allclose(
    after.reflected_directions, before.reflected_directions @ Q.T
)
assert np.allclose(after.focal_path_lengths, before.focal_path_lengths)
print(before.maximum_direction_error, after.maximum_direction_error)

# --- 4. Ölçek değişmezliği ve açık sınır hataları ---
import numpy as np
from agbook import (
    ellipse_frame_from_center_axes,
    ellipse_points,
    ellipse_focal_sum_residuals,
    ellipse_reflection_diagnostics,
)

t = np.array([0.2, 1.1, 2.7])
m = ellipse_frame_from_center_axes([0., 0.], [1., 0.], 5., 3.)
mm = ellipse_frame_from_center_axes([0., 0.], [1., 0.], 5000., 3000.)
assert np.isclose(mm.focal_distance, 1000. * m.focal_distance)
assert np.isclose(mm.eccentricity, m.eccentricity)

p = ellipse_points([0., 0.], [1., 0.], 5., 3., t) + np.array([0.01, 0.])
r_m = ellipse_focal_sum_residuals(p, m.first_focus, m.second_focus, 5.)
r_mm = ellipse_focal_sum_residuals(
    1000. * p, mm.first_focus, mm.second_focus, 5000.
)
assert np.allclose(r_mm, 1000. * r_m)

for bad in ((5., 5.), (3., 5.)):
    try:
        ellipse_frame_from_center_axes([0., 0.], [1., 0.], *bad)
    except ValueError as error:
        print(type(error).__name__, str(error))
