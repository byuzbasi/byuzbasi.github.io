# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Bölüm 10: doğru--çember ve kutupsal tanısı ---
import numpy as np
from agbook import (
    circle_line_intersections,
    polar_line_of_point,
    tangent_points_from_point,
)

C = np.array([120.0, 80.0])  # mm
r = 45.0                     # mm
paths = {
    "kesen": [0.0, 1.0, -100.0],
    "teget": [1.0, 0.0, -165.0],
    "ayrik": [0.0, 1.0, -135.0],
}
tol = dict(
    absolute_tolerance=1e-9,
    relative_tolerance=1e-12,
    reference_scale=200.0,
)
for name, line in paths.items():
    out = circle_line_intersections(C, r, line, **tol)
    print(name, out.relation, out.center_distance,
          out.chord_length)

A = np.array([200.0, 140.0])  # mm
contacts = tangent_points_from_point(C, r, A, **tol)
polar = polar_line_of_point(C, r, A)
print(contacts.relation, contacts.tangent_length)
print(polar)
