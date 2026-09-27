# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Doğrultman ölçeği ve dejenere durum ---
import numpy as np
from agbook import parabola_frame_from_focus_directrix

focus = np.array([2., 1.])
lines = ([1., 0., 2.], [7., 0., 14.], [-3., 0., -6.])
frames = [parabola_frame_from_focus_directrix(focus, line)
          for line in lines]
for frame in frames:
    print(frame.vertex, frame.axis_direction, frame.focal_length)

assert all(np.allclose(frame.vertex, [0., 1.]) for frame in frames)
assert all(np.allclose(frame.axis_direction, [1., 0.]) for frame in frames)
assert all(np.isclose(frame.focal_length, 2.) for frame in frames)

try:
    parabola_frame_from_focus_directrix([0., 1.], [1., 0., 0.])
except ValueError as error:
    print(type(error).__name__, str(error))

# --- 2. Parabol noktaları ve teğet artıkları ---
import numpy as np
from agbook import (
    parabola_algebraic_residuals, parabola_points, parabola_tangent_line,
)

t = np.array([-2., -1., 0., 1., 2.])
points = parabola_points([0., 0.], [1., 0.], 2., t)
membership = parabola_algebraic_residuals(
    points, [0., 0.], [1., 0.], 2.
)
lines = np.vstack([
    parabola_tangent_line([0., 0.], [1., 0.], 2., value)
    for value in t
])
tangent = np.sum(lines[:, :2] * points, axis=1) + lines[:, 2]
print(points)
print(np.max(np.abs(membership)))
print(np.max(np.abs(tangent)))

# --- 3. Yansımanın rijit hareket altında denetimi ---
import numpy as np
from agbook import parabola_reflection_diagnostics, rotation_matrix_2d

t = np.linspace(-2., 2., 17)
before = parabola_reflection_diagnostics([0., 0.], [1., 0.], 3., t)
Q = rotation_matrix_2d(np.deg2rad(37.))
b = np.array([5., -3.])
after = parabola_reflection_diagnostics(b, Q @ np.array([1., 0.]), 3., t)

point_error = np.max(np.abs(after.points - (before.points @ Q.T + b)))
direction_error = np.max(np.abs(
    after.reflected_directions - before.reflected_directions @ Q.T
))
print(before.maximum_direction_error, point_error, direction_error)
assert before.maximum_direction_error < 2e-14
assert point_error < 3e-14
assert direction_error < 3e-14

# --- 4. Metre--milimetre ölçek denetimi ---
import numpy as np
from agbook import parabolic_reflector_focal_length

D_m, d_m = 8., 1.
f_m = parabolic_reflector_focal_length(D_m, d_m)
D_mm, d_mm = 1000. * D_m, 1000. * d_m
f_mm = parabolic_reflector_focal_length(D_mm, d_mm)

print(f_m, f_mm, f_m / D_m, f_mm / D_mm)
assert np.isclose(f_mm, 1000. * f_m)
assert np.isclose(f_m / D_m, f_mm / D_mm)
