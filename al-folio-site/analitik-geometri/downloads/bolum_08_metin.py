# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Bölüm 8: kutupsal ölçümden afin harita noktasına ---
import numpy as np
from agbook import (
    apply_affine_map,
    cartesian_to_polar,
    homogeneous_affine_matrix,
    inverse_affine_map,
    polar_to_cartesian,
)

angles_deg = np.array([-55., -35., -15., 5., 25., 45., 65.])
ranges_m = np.array([4.2, 4.8, 5.5, 6.0, 5.4, 4.7, 4.0])
polar = np.column_stack([ranges_m, np.deg2rad(angles_deg)])
sensor = polar_to_cartesian(polar)

A = np.array([[1.04, 0.12], [-0.03, 0.97]])
b = np.array([12.0, 8.0])  # m
mapped = apply_affine_map(sensor, A, b)
inverse = inverse_affine_map(A, b)
recovered = apply_affine_map(mapped, inverse.matrix,
                             inverse.translation)

H = homogeneous_affine_matrix(A, b)
sensor_h = np.column_stack([sensor, np.ones(sensor.shape[0])])
mapped_h = (H @ sensor_h.T).T[:, :2]
polar_back = cartesian_to_polar(recovered)

print("determinant:", f"{np.linalg.det(A):.12f}")
print("rank:", np.linalg.matrix_rank(A))
print("kosul_sayisi:", f"{np.linalg.cond(A):.9f}")
print("homojen_artik_m:", f"{np.max(np.abs(mapped_h-mapped)):.3e}")
print("gidis_donus_artigi_m:",
      f"{np.max(np.abs(recovered-sensor)):.3e}")
print("menzil_artigi_m:",
      f"{np.max(np.abs(polar_back[:, 0]-ranges_m)):.3e}")
