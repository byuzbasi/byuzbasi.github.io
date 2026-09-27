# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Kanonik doğru ve açık üyelik denetimi ---
import numpy as np
from agbook import (
    canonical_line_coefficients,
    line_from_point_direction,
    line_from_points,
    line_membership_diagnostics,
    line_residuals,
    parametric_line_points,
)

A = np.array([1000.0, 500.0])  # metre
B = np.array([1300.0, 700.0])  # metre
v = B - A
t = np.array([0.0, 0.25, 0.5, 0.75, 1.0])

line = line_from_points(A, B)
stations = parametric_line_points(A, v, t)
residuals = line_residuals(line, stations)
same_from_shift = line_from_point_direction(stations[2], -3.0 * v)
same_from_scale = canonical_line_coefficients(-7.0 * line)

candidate = stations[3] + 0.006 * line[:2]
membership = line_membership_diagnostics(
    line,
    candidate,
    absolute_tolerance=0.010,
    relative_tolerance=0.0,
    reference_scale=500.0,
)
