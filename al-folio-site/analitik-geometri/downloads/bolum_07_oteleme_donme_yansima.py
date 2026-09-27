"""Bölüm 7 laboratuvarı: yerel CAD çerçevesinden robot dünyasına geçiş.

Model iki boyutlu ve sentetiktir. Koordinatlar milimetre, açılar sunumda
derecedir. Üç boyutlu poz, mekanik tolerans, kamera modeli, çarpışma ve
güvenlik denetimi içermez.
"""

from __future__ import annotations

import numpy as np

from agbook import (
    canonical_array_sha256,
    compose_rigid_motions,
    coordinates_from_frame,
    coordinates_in_frame,
    inverse_rigid_motion,
    line_from_points,
    pairwise_distances,
    polygon_signed_area,
    reflect_across_line,
    rigid_motion_diagnostics,
    rigid_transform,
    rotation_matrix_2d,
)


def main() -> None:
    part_local = np.array(
        [[0.0, 0.0], [120.0, 0.0], [120.0, 60.0], [0.0, 60.0]]
    )  # mm
    feature_local = np.array([95.0, 45.0])  # mm
    frame_origin = np.array([420.0, 180.0])  # mm, dünya çerçevesinde
    frame_angle_deg = 35.0
    frame_axes = rotation_matrix_2d(np.deg2rad(frame_angle_deg))

    part_world = coordinates_from_frame(part_local, frame_origin, frame_axes)
    feature_world = coordinates_from_frame(feature_local, frame_origin, frame_axes)
    recovered_local = coordinates_in_frame(part_world, frame_origin, frame_axes)
    frame_diagnostics = rigid_motion_diagnostics(
        part_local,
        frame_axes,
        frame_origin,
    )

    local_datum = np.array([0.0, 1.0, -30.0])  # y=30 mm
    reflected_local = reflect_across_line(feature_local, local_datum)
    reflected_world_from_local = coordinates_from_frame(
        reflected_local,
        frame_origin,
        frame_axes,
    )
    datum_world_points = coordinates_from_frame(
        [[0.0, 30.0], [120.0, 30.0]],
        frame_origin,
        frame_axes,
    )
    datum_world = line_from_points(datum_world_points[0], datum_world_points[1])
    reflected_world_direct = reflect_across_line(feature_world, datum_world)

    sensor_rotation = rotation_matrix_2d(np.deg2rad(-12.0))
    sensor_origin_in_part = np.array([35.0, 20.0])  # mm
    sensor_shape = np.array([[0.0, 0.0], [24.0, 0.0], [12.0, 10.0]])  # mm
    composed = compose_rigid_motions(
        frame_axes,
        frame_origin,
        sensor_rotation,
        sensor_origin_in_part,
    )
    sensor_world_direct = rigid_transform(
        sensor_shape,
        composed.matrix,
        composed.translation,
    )
    sensor_world_sequential = coordinates_from_frame(
        rigid_transform(sensor_shape, sensor_rotation, sensor_origin_in_part),
        frame_origin,
        frame_axes,
    )
    inverse = inverse_rigid_motion(composed.matrix, composed.translation)
    sensor_recovered = rigid_transform(
        sensor_world_direct,
        inverse.matrix,
        inverse.translation,
    )

    print("birim: mm")
    print("cerceve_acisi_derece:", f"{frame_angle_deg:.1f}")
    print("cerceve_baslangici:", np.round(frame_origin, 9))
    print("cerceve_determinanti:", f"{np.linalg.det(frame_axes):.12f}")
    print("ortogonallik_artigi:", f"{frame_diagnostics.orthogonality_residual:.3e}")
    print("yerel_ozellik:", np.round(feature_local, 9))
    print("dunya_ozellik:", np.round(feature_world, 9))
    print("cerceve_gidis_donus_artigi_mm:", f"{np.max(np.abs(recovered_local - part_local)):.3e}")
    print("uzaklik_artigi_mm:", f"{np.max(np.abs(pairwise_distances(part_world) - pairwise_distances(part_local))):.3e}")
    print("yerel_yonlu_alan_mm2:", f"{polygon_signed_area(part_local):.6f}")
    print("dunya_yonlu_alan_mm2:", f"{polygon_signed_area(part_world):.6f}")
    print("yansitilmis_yerel_ozellik:", np.round(reflected_local, 9))
    print("yansima_cerceve_uyumu_mm:", f"{np.max(np.abs(reflected_world_direct - reflected_world_from_local)):.3e}")
    print("bilesik_determinant:", f"{composed.determinant:.12f}")
    print("bilesim_artigi_mm:", f"{np.max(np.abs(sensor_world_direct - sensor_world_sequential)):.3e}")
    print("ters_hareket_artigi_mm:", f"{np.max(np.abs(sensor_recovered - sensor_shape)):.3e}")
    signature_values = np.concatenate(
        [
            part_world.ravel(),
            feature_world,
            reflected_world_direct,
            composed.matrix.ravel(),
            composed.translation,
        ]
    )
    print("bilimsel_imza:", canonical_array_sha256(signature_values))


if __name__ == "__main__":
    main()
