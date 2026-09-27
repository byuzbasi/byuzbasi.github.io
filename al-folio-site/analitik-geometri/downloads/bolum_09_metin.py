# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Bölüm 9: odak--doğrultman tanısı ve rijit çerçeve ---
import numpy as np
from agbook import (
    focus_directrix_diagnostics,
    rotation_matrix_2d,
)

e, d = 0.6, 12_000.0  # d: km
focus = np.array([0.0, 0.0])
directrix = np.array([1.0, 0.0, -d])
xc = -(e**2) * d / (1.0 - e**2)
a0 = e * d / (1.0 - e**2)
b0 = a0 * np.sqrt(1.0 - e**2)
t = np.linspace(0.0, 2.0*np.pi, 12, endpoint=False)
points = np.column_stack([xc + a0*np.cos(t), b0*np.sin(t)])

before = focus_directrix_diagnostics(
    points, focus, directrix, e, reference_scale=d
)
Q = rotation_matrix_2d(np.deg2rad(23.0))
b = np.array([3_200.0, -1_800.0])  # km
moved = points @ Q.T + b
moved_focus = focus @ Q.T + b
n_moved = Q @ directrix[:2]
line_moved = np.r_[n_moved, directrix[2] - n_moved @ b]
after = focus_directrix_diagnostics(
    moved, moved_focus, line_moved, e, reference_scale=d
)

print(before.conic_type)
print(f"{before.maximum_absolute_residual:.3e}")
print(f"{before.maximum_scaled_residual:.3e}")
print(f"{np.max(np.abs(before.ratios-after.ratios)):.3e}")
