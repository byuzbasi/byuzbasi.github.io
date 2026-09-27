# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Uzay üçgeni ve tetrahedron tanısı ---
import numpy as np
from agbook import (
    spatial_orientation_diagnostics,
    tetrahedron_volume,
    triangle_area_3d,
    unit_normal_3d,
)

A = np.array([120.0, 80.0, 35.0])
B = np.array([156.0, 128.0, 35.0])
C = np.array([96.0, 98.0, 75.0])
D = np.array([168.0, 44.0, 80.0])

u, v, w = B - A, C - A, D - A
normal = unit_normal_3d(u, v)
area = triangle_area_3d(A, B, C)
volume = tetrahedron_volume(A, B, C, D)
diagnosis = spatial_orientation_diagnostics(
    u, v, w, relative_tolerance=1e-12
)

print(normal)
print(area, volume)
print(diagnosis.scalar_triple_product)
print(diagnosis.normalized_triple_product)
print(diagnosis.classification)
