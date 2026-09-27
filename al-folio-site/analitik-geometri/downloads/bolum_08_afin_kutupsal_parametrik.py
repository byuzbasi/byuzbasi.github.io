"""Bölüm 8 laboratuvarı: kutupsal taramayı afin harita çerçevesine taşıma.

Model iki boyutlu ve sentetiktir. Menziller metre, açılar derece olarak
girilip hesapta radyana çevrilir. Perspektif, üç boyutlu poz, gürültü,
belirsizlik, zaman senkronizasyonu ve güvenlik kararı içermez.
"""

from __future__ import annotations

import numpy as np

from agbook import (
    apply_affine_map,
    canonical_array_sha256,
    cartesian_to_polar,
    homogeneous_affine_matrix,
    inverse_affine_map,
    polar_to_cartesian,
    polygon_signed_area,
)


def main() -> None:
    angles_deg = np.array([-55.0, -35.0, -15.0, 5.0, 25.0, 45.0, 65.0])
    ranges_m = np.array([4.2, 4.8, 5.5, 6.0, 5.4, 4.7, 4.0])
    scan_parameter = np.linspace(0.0, 1.0, angles_deg.size)
    polar_measurements = np.column_stack([ranges_m, np.deg2rad(angles_deg)])
    sensor_points = polar_to_cartesian(polar_measurements)

    calibration_matrix = np.array([[1.04, 0.12], [-0.03, 0.97]])
    map_origin = np.array([12.0, 8.0])  # m
    map_points = apply_affine_map(sensor_points, calibration_matrix, map_origin)

    inverse = inverse_affine_map(calibration_matrix, map_origin)
    recovered_sensor = apply_affine_map(
        map_points,
        inverse.matrix,
        inverse.translation,
    )
    recovered_polar = cartesian_to_polar(recovered_sensor)

    homogeneous = homogeneous_affine_matrix(calibration_matrix, map_origin)
    homogeneous_sensor = np.column_stack(
        [sensor_points, np.ones(sensor_points.shape[0])]
    )
    homogeneous_map = (homogeneous @ homogeneous_sensor.T).T

    reference_triangle = np.array([[0.0, 0.0], [2.0, 0.0], [0.0, 1.5]])
    mapped_triangle = apply_affine_map(
        reference_triangle,
        calibration_matrix,
        map_origin,
    )
    area_ratio = polygon_signed_area(mapped_triangle) / polygon_signed_area(
        reference_triangle
    )

    print("birim: m")
    print("olcum_sayisi:", angles_deg.size)
    print("parametre_araligi:", np.round([scan_parameter[0], scan_parameter[-1]], 6))
    print("aci_araligi_derece:", np.round([angles_deg[0], angles_deg[-1]], 6))
    print("ilk_sensor_noktasi:", np.round(sensor_points[0], 9))
    print("son_sensor_noktasi:", np.round(sensor_points[-1], 9))
    print("ilk_harita_noktasi:", np.round(map_points[0], 9))
    print("son_harita_noktasi:", np.round(map_points[-1], 9))
    print("afin_determinant:", f"{np.linalg.det(calibration_matrix):.12f}")
    print("afin_rank:", np.linalg.matrix_rank(calibration_matrix))
    print("afin_kosul_sayisi:", f"{np.linalg.cond(calibration_matrix):.9f}")
    print("yonlu_alan_orani:", f"{area_ratio:.12f}")
    print(
        "alan_determinant_artigi:",
        f"{abs(area_ratio - np.linalg.det(calibration_matrix)):.3e}",
    )
    print(
        "homojen_dogrulama_artigi_m:",
        f"{np.max(np.abs(homogeneous_map[:, :2] - map_points)):.3e}",
    )
    print(
        "afin_gidis_donus_artigi_m:",
        f"{np.max(np.abs(recovered_sensor - sensor_points)):.3e}",
    )
    print(
        "kutupsal_gidis_donus_artigi_m:",
        f"{np.max(np.abs(recovered_polar[:, 0] - ranges_m)):.3e}",
    )
    print("parametre_sirasi_korundu:", bool(np.all(np.diff(scan_parameter) > 0.0)))

    signature_values = np.concatenate(
        [
            polar_measurements.ravel(),
            calibration_matrix.ravel(),
            map_origin,
            map_points.ravel(),
        ]
    )
    print("bilimsel_imza:", canonical_array_sha256(signature_values))


if __name__ == "__main__":
    main()
