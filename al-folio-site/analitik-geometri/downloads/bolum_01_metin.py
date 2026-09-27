# Kitaptaki kod blokları; bu dosya içinde sırayla çalıştırılır.
# --- 1. Bölüm 1'in yeniden üretilebilir deneyi ---
import numpy as np

from agbook import (
    rigid_motion_diagnostics,
    rotation_matrix_2d,
    trilaterate_linear,
)

SEED = 20260907

triangle = np.array([[0.0, 0.0],
                     [4.0, 0.0],
                     [1.0, 3.0]])
Q = rotation_matrix_2d(np.deg2rad(37.0))
diag = rigid_motion_diagnostics(triangle, Q, [2.5, -1.25])

anchors = np.array([[0.0, 0.0],
                    [6.0, 0.0],
                    [0.0, 5.0],
                    [6.0, 5.0]])
true_point = np.array([2.3, 1.7])
rng = np.random.default_rng(SEED)
ranges = np.linalg.norm(anchors - true_point, axis=1)
ranges += rng.normal(0.0, 0.01, size=anchors.shape[0])
fit = trilaterate_linear(anchors, ranges)

print(f"ortogonallik: {diag.orthogonality_residual:.3e}")
print(f"uzaklik_hatasi: {diag.maximum_distance_error:.3e}")
print(f"tahmin: {fit.point}")
print(f"rank: {fit.rank}")
print(f"artik_normu: {fit.residual_norm:.6f}")
print(f"konum_hatasi: {np.linalg.norm(fit.point-true_point):.6f}")
