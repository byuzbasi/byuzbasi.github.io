# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Bölüm 12: reflektör çerçevesi ve yüzey noktaları ---
import numpy as np
from agbook import (
    focus_directrix_diagnostics,
    parabola_frame_from_vertex_axis,
    parabola_points,
    parabola_reflection_diagnostics,
    parabolic_reflector_focal_length,
)

D, d = 8.0, 1.0  # metre
f = parabolic_reflector_focal_length(D, d)
frame = parabola_frame_from_vertex_axis([0., 0.], [0., 1.], f)
t_rim = D / (4.0 * f)
t = np.linspace(-t_rim, t_rim, 9)
points = parabola_points(frame.vertex, frame.axis_direction, f, t)
locus = focus_directrix_diagnostics(
    points, frame.focus, frame.directrix, 1.0, reference_scale=D
)
reflection = parabola_reflection_diagnostics(
    frame.vertex, frame.axis_direction, f, t
)
print(f, frame.focus, points[[0, -1]])
print(locus.maximum_absolute_residual)
print(reflection.maximum_direction_error)

# --- 2. Bölüm 12 laboratuvarı: teğet ve rijit değişmezlik ---
from agbook import parabola_tangent_line, rotation_matrix_2d

tangents = np.vstack([
    parabola_tangent_line(frame.vertex, frame.axis_direction, f, value)
    for value in t
])
tangent_residuals = np.sum(tangents[:, :2] * points, axis=1) + tangents[:, 2]

Q = rotation_matrix_2d(np.deg2rad(29.0))
b = np.array([12.0, -7.0])  # metre
moved = parabola_reflection_diagnostics(Q @ frame.vertex + b, Q @ frame.axis_direction, f, t)
expected_points = points @ Q.T + b
print(np.max(np.abs(tangent_residuals)))
print(np.max(np.abs(moved.points - expected_points)))
print(np.max(np.abs(moved.reflected_directions - reflection.reflected_directions @ Q.T)))
