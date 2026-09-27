"""Bölüm 1 laboratuvarı: değişmezlik ve üçleme denetimi."""

from __future__ import annotations

import numpy as np

from agbook import (
    rigid_motion_diagnostics,
    rotation_matrix_2d,
    trilaterate_linear,
)


SEED = 20260907


def main() -> None:
    triangle = np.array([[0.0, 0.0], [4.0, 0.0], [1.0, 3.0]])
    rotation = rotation_matrix_2d(np.deg2rad(37.0))
    diagnostics = rigid_motion_diagnostics(triangle, rotation, [2.5, -1.25])

    anchors = np.array([[0.0, 0.0], [6.0, 0.0], [0.0, 5.0], [6.0, 5.0]])
    true_point = np.array([2.3, 1.7])
    rng = np.random.default_rng(SEED)
    measured_ranges = np.linalg.norm(anchors - true_point, axis=1)
    measured_ranges += rng.normal(loc=0.0, scale=0.01, size=anchors.shape[0])
    estimate = trilaterate_linear(anchors, measured_ranges)

    np.set_printoptions(precision=6, suppress=True)
    print(f"tohum: {SEED}")
    print(f"ortogonallik_artigi: {diagnostics.orthogonality_residual:.3e}")
    print(f"determinant: {diagnostics.determinant:.6f}")
    print(f"en_buyuk_uzaklik_hatasi: {diagnostics.maximum_distance_error:.3e}")
    print(f"gercek_nokta: {true_point}")
    print(f"tahmin: {estimate.point}")
    print(f"rank: {estimate.rank}")
    print(f"uzaklik_artik_normu: {estimate.residual_norm:.6f}")
    print(f"konum_hatasi: {np.linalg.norm(estimate.point - true_point):.6f}")


if __name__ == "__main__":
    main()
