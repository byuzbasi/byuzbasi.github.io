"""Bölüm 2 laboratuvarı: rüzgâr altında rota bileşenleri."""

from __future__ import annotations

import numpy as np

from agbook import angle_between, orthogonal_decomposition, vector_norm


def main() -> None:
    air_velocity = np.array([15.0, 2.0])
    wind_velocity = np.array([-3.0, 4.0])
    route_direction = np.array([4.0, 3.0])
    ground_velocity = air_velocity + wind_velocity

    decomposition = orthogonal_decomposition(ground_velocity, route_direction)
    scaled = orthogonal_decomposition(ground_velocity, 1.0e8 * route_direction)

    np.set_printoptions(precision=6, suppress=True)
    print(f"hava_hizi: {air_velocity}")
    print(f"ruzgar_hizi: {wind_velocity}")
    print(f"yer_hizi: {ground_velocity}")
    print(f"yer_surati: {vector_norm(ground_velocity):.6f}")
    print(f"rota_bileseni: {decomposition.scalar_component:.6f}")
    print(f"paralel: {decomposition.parallel}")
    print(f"capraz: {decomposition.perpendicular}")
    print(f"capraz_surat: {vector_norm(decomposition.perpendicular):.6f}")
    print(f"rota_acisi_derece: {angle_between(ground_velocity, route_direction, degrees=True):.6f}")
    print(f"yeniden_kurma_artigi: {decomposition.reconstruction_residual:.3e}")
    print(f"diklik_artigi: {decomposition.orthogonality_residual:.3e}")
    print(f"olcek_degismezligi: {vector_norm(decomposition.parallel - scaled.parallel):.3e}")


if __name__ == "__main__":
    main()
