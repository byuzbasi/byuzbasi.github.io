"""Bölüm 24: bütünleştirici analitik geometri laboratuvarı.

Beş ayrı sentetik bağlam tek bir doğrulama protokolüyle işlenir: ölçme ve
haritalama, CAD/robotik, bilgisayarlı görü, geometrik optik ve yörünge
geometrisi. Veriler gerçek saha, üretim, kamera veya uzay görevi verisi
değildir; hiçbir sonuç fiziksel kabul ya da güvenlik kararı olarak kullanılamaz.
"""

from __future__ import annotations

import math

import numpy as np

from agbook import (
    apply_similarity_registration,
    canonical_array_sha256,
    fit_similarity_registration,
    line_sphere_intersections_3d,
    orbit_ellipse_frame_3d,
    orbit_ellipse_points_3d,
    project_pinhole,
    ray_plane_intersection,
    reflect_direction,
    triangulate_point_dlt,
)


def rotation_2d(angle: float) -> np.ndarray:
    cosine, sine = math.cos(angle), math.sin(angle)
    return np.array([[cosine, -sine], [sine, cosine]])


def rotation_3d(ax: float, ay: float, az: float) -> np.ndarray:
    cx, sx = math.cos(ax), math.sin(ax)
    cy, sy = math.cos(ay), math.sin(ay)
    cz, sz = math.cos(az), math.sin(az)
    rx = np.array([[1.0, 0.0, 0.0], [0.0, cx, -sx], [0.0, sx, cx]])
    ry = np.array([[cy, 0.0, sy], [0.0, 1.0, 0.0], [-sy, 0.0, cy]])
    rz = np.array([[cz, -sz, 0.0], [sz, cz, 0.0], [0.0, 0.0, 1.0]])
    return rz @ ry @ rx


def camera_matrix(center: np.ndarray) -> np.ndarray:
    intrinsic = np.array(
        [[1250.0, 0.0, 640.0], [0.0, 1250.0, 360.0], [0.0, 0.0, 1.0]]
    )
    return intrinsic @ np.column_stack((np.eye(3), -center))


def main() -> None:
    seed = 2401
    rng = np.random.default_rng(seed)

    # 1. Ölçme-haritalama: bütün koordinatlar metre, ölçek boyutsuzdur.
    survey_local_m = np.array(
        [
            [-42.0, -25.0],
            [35.0, -31.0],
            [58.0, 18.0],
            [12.0, 54.0],
            [-51.0, 38.0],
            [4.0, 6.0],
        ]
    )
    survey_rotation_true = rotation_2d(math.radians(7.5))
    survey_scale_true = 1.00035
    survey_translation_true_m = np.array([448250.0, 4512310.0])
    survey_sigma_m = np.array([0.010, 0.012, 0.010, 0.018, 0.020, 0.015])
    survey_observed_m = (
        survey_scale_true * (survey_local_m @ survey_rotation_true.T)
        + survey_translation_true_m
    )
    survey_observed_m += rng.normal(scale=survey_sigma_m[:, None], size=(6, 2))
    survey_fit = fit_similarity_registration(
        survey_local_m,
        survey_observed_m,
        weights=1.0 / survey_sigma_m**2,
    )
    survey_check_m = np.array([[16.0, -12.0], [-20.0, 41.0]])
    survey_check_global_m = apply_similarity_registration(survey_check_m, survey_fit)

    # 2. CAD/robotik: bütün koordinatlar milimetredir; ölçek sabit birdir.
    cad_fiducials_mm = np.array(
        [
            [0.0, 0.0, 0.0],
            [120.0, 0.0, 0.0],
            [0.0, 80.0, 0.0],
            [120.0, 80.0, 0.0],
            [20.0, 25.0, 55.0],
            [95.0, 60.0, 42.0],
        ]
    )
    cad_rotation_true = rotation_3d(0.18, -0.27, 0.41)
    cad_translation_true_mm = np.array([420.0, -180.0, 760.0])
    robot_observed_mm = cad_fiducials_mm @ cad_rotation_true.T + cad_translation_true_mm
    robot_observed_mm += rng.normal(scale=0.05, size=robot_observed_mm.shape)
    cad_fit = fit_similarity_registration(
        cad_fiducials_mm,
        robot_observed_mm,
        estimate_scale=False,
    )
    tool_anchor_cad_mm = np.array([[60.0, 40.0, 90.0]])
    tool_anchor_robot_mm = apply_similarity_registration(tool_anchor_cad_mm, cad_fit)[0]
    tool_direction_robot = cad_fit.rotation @ np.array([0.0, 0.0, 1.0])
    exclusion_center_mm = tool_anchor_robot_mm + 65.0 * tool_direction_robot + np.array([32.0, 0.0, 0.0])
    exclusion_radius_mm = 20.0
    clearance = line_sphere_intersections_3d(
        exclusion_center_mm,
        exclusion_radius_mm,
        tool_anchor_robot_mm,
        tool_direction_robot,
        absolute_tolerance=1.0e-9,
        relative_tolerance=1.0e-12,
        reference_scale=1000.0,
    )

    # 3. Bilgisayarlı görü: dünya koordinatları metre, görüntüler pikseldir.
    camera_centers_m = np.array([[-0.9, 0.0, 0.0], [0.9, 0.0, 0.0], [0.0, 0.65, 0.0]])
    cameras = np.stack([camera_matrix(center) for center in camera_centers_m])
    world_point_true_m = np.array([[0.24, -0.16, 5.8]])
    image_points_px = np.vstack(
        [project_pinhole(camera, world_point_true_m).image_points[0] for camera in cameras]
    )
    image_points_px += rng.normal(scale=0.22, size=image_points_px.shape)
    triangulated = triangulate_point_dlt(cameras, image_points_px)
    triangulation_error_m = float(np.linalg.norm(triangulated.point - world_point_true_m[0]))

    # 4. Geometrik optik: noktalar milimetre, yönler boyutsuzdur.
    ray_origin_mm = np.array([35.0, -22.0, 80.0])
    ray_direction = np.array([-0.60, 0.25, -1.0])
    mirror_point_mm = np.array([0.0, 0.0, 0.0])
    mirror_normal = np.array([0.12, -0.08, 1.0])
    mirror_hit = ray_plane_intersection(
        ray_origin_mm,
        ray_direction,
        mirror_point_mm,
        mirror_normal,
        distance_tolerance=1.0e-9,
    )
    if mirror_hit.point is None:
        raise RuntimeError("Sentetik optik ışını aynayla kesişmedi.")
    reflected_direction = reflect_direction(mirror_hit.unit_direction, mirror_hit.unit_normal)
    reflection_norm_error = abs(np.linalg.norm(reflected_direction) - 1.0)
    reflection_angle_error = abs(
        abs(reflected_direction @ mirror_hit.unit_normal)
        - abs(mirror_hit.unit_direction @ mirror_hit.unit_normal)
    )

    # 5. Yörünge geometrisi: bütün konumlar kilometredir; zaman modeli yoktur.
    orbit = orbit_ellipse_frame_3d(
        focus=np.array([1200.0, -800.0, 350.0]),
        periapsis_direction=np.array([1.0, 0.25, 0.08]),
        plane_normal=np.array([0.22, -0.34, 0.91]),
        periapsis_radius=7000.0,
        apoapsis_radius=12000.0,
    )
    eccentric_anomaly = np.linspace(0.0, 2.0 * np.pi, 181)
    orbit_points_km = orbit_ellipse_points_3d(orbit, eccentric_anomaly)
    orbit_plane_residual_km = np.max(
        np.abs((orbit_points_km - orbit.focus) @ orbit.plane_normal)
    )
    orbit_focal_sum_residual_km = np.max(
        np.abs(
            np.linalg.norm(orbit_points_km - orbit.focus, axis=1)
            + np.linalg.norm(orbit_points_km - orbit.second_focus, axis=1)
            - 2.0 * orbit.semi_major_axis
        )
    )

    # Bağımsız yürütülebilirlik ve geometri kapıları.
    assert survey_fit.weighted_rms_residual < 0.03
    assert abs(survey_fit.scale - survey_scale_true) < 4.0e-4
    assert cad_fit.rms_residual < 0.12
    assert clearance.relation == "disjoint"
    assert clearance.clearance > 10.0
    assert triangulation_error_m < 0.01
    assert triangulated.rms_reprojection < 0.5
    assert np.all(triangulated.in_front)
    assert mirror_hit.classification == "intersecting"
    assert reflection_norm_error < 2.0e-15
    assert reflection_angle_error < 2.0e-15
    assert orbit_plane_residual_km < 5.0e-12
    assert orbit_focal_sum_residual_km < 1.0e-11

    signature_values = np.concatenate(
        (
            survey_local_m.ravel(),
            survey_observed_m.ravel(),
            survey_fit.homogeneous_matrix.ravel(),
            survey_check_global_m.ravel(),
            cad_fiducials_mm.ravel(),
            robot_observed_mm.ravel(),
            cad_fit.homogeneous_matrix.ravel(),
            exclusion_center_mm,
            [clearance.clearance],
            cameras.ravel(),
            image_points_px.ravel(),
            triangulated.point,
            triangulated.residual_vectors.ravel(),
            ray_origin_mm,
            ray_direction,
            mirror_hit.point,
            reflected_direction,
            orbit.focus,
            orbit.center,
            orbit.periapsis,
            orbit.apoapsis,
            orbit_points_km.ravel(),
        )
    )

    print("tohum:", seed)
    print("veri: sentetik_butunlestirici_uygulamalar")
    print("gercek_olcum_verisi_mi: False")
    print("eksik_deger_islemi: yok")
    print("gozlem_silindi_mi: False")
    print("harita_birimi: m")
    print("harita_olcek:", f"{survey_fit.scale:.10f}")
    print("harita_donme_derece:", f"{math.degrees(math.atan2(survey_fit.rotation[1, 0], survey_fit.rotation[0, 0])):.8f}")
    print("harita_agirlikli_rms_m:", f"{survey_fit.weighted_rms_residual:.9f}")
    print("cad_robot_birimi: mm")
    print("cad_robot_rms_mm:", f"{cad_fit.rms_residual:.9f}")
    print("takim_kure_iliskisi:", clearance.relation)
    print("takim_kure_acikligi_mm:", f"{clearance.clearance:.9f}")
    print("kamera_dunya_birimi: m")
    print("kamera_goruntu_birimi: piksel")
    print("ucgenlenen_nokta_m:", triangulated.point)
    print("ucgenleme_hatasi_m:", f"{triangulation_error_m:.9f}")
    print("geri_izdusum_rms_piksel:", f"{triangulated.rms_reprojection:.9f}")
    print("optik_konum_birimi: mm")
    print("ayna_kesisim_mm:", mirror_hit.point)
    print("yansiyan_birim_yon:", reflected_direction)
    print("yansima_aci_artigi:", f"{reflection_angle_error:.3e}")
    print("yorunge_birimi: km")
    print("yorunge_yari_buyuk_eksen_km:", f"{orbit.semi_major_axis:.6f}")
    print("yorunge_dismerkezlik:", f"{orbit.eccentricity:.9f}")
    print("yorunge_duzlem_artigi_km:", f"{orbit_plane_residual_km:.3e}")
    print("yorunge_odak_toplami_artigi_km:", f"{orbit_focal_sum_residual_km:.3e}")
    print("bilimsel_imza:", canonical_array_sha256(signature_values))


if __name__ == "__main__":
    main()
