# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Bölüm 13: elips çerçevesi ve sınır noktaları ---
import numpy as np
from agbook import (
    ellipse_algebraic_residuals,
    ellipse_focal_sum_residuals,
    ellipse_frame_from_center_axes,
    ellipse_points,
    ellipse_reflection_diagnostics,
)

a, b = 10.0, 6.0  # metre
frame = ellipse_frame_from_center_axes([0., 0.], [1., 0.], a, b)
t = np.linspace(0.0, 2.0 * np.pi, 12, endpoint=False)
points = ellipse_points(frame.center, frame.major_direction, a, b, t)
r_alg = ellipse_algebraic_residuals(
    points, frame.center, frame.major_direction, a, b
)
r_sum = ellipse_focal_sum_residuals(
    points, frame.first_focus, frame.second_focus, a
)
reflection = ellipse_reflection_diagnostics(
    frame.center, frame.major_direction, a, b, t
)
print(frame.focal_distance, frame.eccentricity)
print(np.max(np.abs(r_alg)), np.max(np.abs(r_sum)))
print(reflection.maximum_direction_error)

# --- 2. Bölüm 13 laboratuvarı: teğet ve rijit değişmezlik ---
from agbook import ellipse_tangent_line, rotation_matrix_2d

tangents = np.vstack([
    ellipse_tangent_line(frame.center, frame.major_direction, a, b, value)
    for value in t
])
tangent_residuals = np.sum(tangents[:, :2] * points, axis=1) + tangents[:, 2]

Q = rotation_matrix_2d(np.deg2rad(31.0))
shift = np.array([13.0, -7.0])  # metre
moved = ellipse_reflection_diagnostics(
    Q @ frame.center + shift, Q @ frame.major_direction, a, b, t
)
expected_points = points @ Q.T + shift
print(np.max(np.abs(tangent_residuals)))
print(np.max(np.abs(moved.points - expected_points)))
print(np.max(np.abs(
    moved.reflected_directions - reflection.reflected_directions @ Q.T
)))
