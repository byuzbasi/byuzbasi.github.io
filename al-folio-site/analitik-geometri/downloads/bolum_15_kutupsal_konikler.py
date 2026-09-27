"""Bölüm 15: kutupsal ve rasyonel konik laboratuvarı.

Uygulama, bir odağı merkez alan sentetik ideal bir eliptik yörünge
geometrisidir. Dinamik, zaman yasası, kütleçekim parametresi, efemeris,
bozucu etkiler, koordinat zamanı ve görev güvenliği modele dahil değildir.
"""

from __future__ import annotations

import numpy as np

from agbook import (
    canonical_array_sha256,
    focus_directrix_residuals,
    polar_conic_algebraic_residuals,
    polar_conic_diagnostics,
    polar_conic_frame,
    polar_conic_points,
    rational_conic_points,
    rotation_matrix_2d,
)


def main() -> None:
    length_unit = "km"
    focus_km = np.array([0.0, 0.0])
    periapsis_direction_deg = 35.0
    angle_rad = np.deg2rad(periapsis_direction_deg)
    axis_direction = np.array([np.cos(angle_rad), np.sin(angle_rad)])
    eccentricity = 0.4
    semilatus_rectum_km = 8400.0

    frame = polar_conic_frame(
        focus_km,
        axis_direction,
        eccentricity,
        semilatus_rectum_km,
    )
    semi_major_km = semilatus_rectum_km / (1.0 - eccentricity**2)
    semi_minor_km = semilatus_rectum_km / np.sqrt(1.0 - eccentricity**2)
    focal_distance_km = eccentricity * semi_major_km
    center_km = focus_km - focal_distance_km * frame.axis_direction
    second_focus_km = center_km - focal_distance_km * frame.axis_direction

    characteristic_angles_rad = np.deg2rad([0.0, 60.0, 90.0, 120.0, 180.0])
    diagnosis = polar_conic_diagnostics(
        frame.focus,
        frame.axis_direction,
        frame.eccentricity,
        frame.semilatus_rectum,
        characteristic_angles_rad,
    )
    periapsis_km = diagnosis.radii[0]
    apoapsis_km = diagnosis.radii[-1]

    comparison_angles_rad = np.deg2rad([-140.0, -90.0, -30.0, 0.0, 45.0, 110.0])
    tangent_half_angles = np.tan(comparison_angles_rad / 2.0)
    polar_points_km = polar_conic_points(
        frame.focus,
        frame.axis_direction,
        frame.eccentricity,
        frame.semilatus_rectum,
        comparison_angles_rad,
    )
    rational_points_km = rational_conic_points(
        frame.focus,
        frame.axis_direction,
        frame.eccentricity,
        frame.semilatus_rectum,
        tangent_half_angles,
    )
    representation_gap_km = np.linalg.norm(
        polar_points_km - rational_points_km,
        axis=1,
    )

    uniform_angles_rad = np.linspace(-np.pi, np.pi, 145)
    uniform_points_km = polar_conic_points(
        frame.focus,
        frame.axis_direction,
        frame.eccentricity,
        frame.semilatus_rectum,
        uniform_angles_rad,
    )
    chord_lengths_km = np.linalg.norm(np.diff(uniform_points_km, axis=0), axis=1)
    chord_ratio = float(np.max(chord_lengths_km) / np.min(chord_lengths_km))

    rotation = rotation_matrix_2d(np.deg2rad(23.0))
    translation_km = np.array([1300.0, -700.0])
    moved_focus_km = rotation @ frame.focus + translation_km
    moved_axis = rotation @ frame.axis_direction
    moved_points_km = polar_conic_points(
        moved_focus_km,
        moved_axis,
        frame.eccentricity,
        frame.semilatus_rectum,
        comparison_angles_rad,
    )
    expected_moved_points_km = polar_points_km @ rotation.T + translation_km
    rigid_gap_km = np.linalg.norm(moved_points_km - expected_moved_points_km, axis=1)

    points_m = 1000.0 * polar_points_km
    residual_km = polar_conic_algebraic_residuals(
        polar_points_km,
        frame.focus,
        frame.axis_direction,
        frame.eccentricity,
        frame.semilatus_rectum,
    )
    residual_m = polar_conic_algebraic_residuals(
        points_m,
        1000.0 * frame.focus,
        frame.axis_direction,
        frame.eccentricity,
        1000.0 * frame.semilatus_rectum,
    )

    np.testing.assert_allclose(semi_major_km, 10000.0, atol=1e-12)
    np.testing.assert_allclose(periapsis_km, 6000.0, atol=1e-12)
    np.testing.assert_allclose(apoapsis_km, 14000.0, atol=3e-12)
    np.testing.assert_allclose(polar_points_km, rational_points_km, atol=4e-12)
    np.testing.assert_allclose(rigid_gap_km, 0.0, atol=4e-12)
    np.testing.assert_allclose(residual_m, residual_km, atol=3e-15)
    assert diagnosis.maximum_absolute_algebraic_residual < 2e-15
    assert diagnosis.maximum_absolute_focus_directrix_residual < 4e-12
    assert chord_ratio > 1.5

    rational_algebraic = polar_conic_algebraic_residuals(
        rational_points_km,
        frame.focus,
        frame.axis_direction,
        frame.eccentricity,
        frame.semilatus_rectum,
    )
    rational_geometric_km = focus_directrix_residuals(
        rational_points_km,
        frame.focus,
        frame.directrix,
        frame.eccentricity,
    )

    signature_values = np.concatenate(
        [
            focus_km,
            axis_direction,
            np.array([eccentricity, semilatus_rectum_km]),
            frame.directrix,
            np.array([semi_major_km, semi_minor_km, focal_distance_km]),
            center_km,
            second_focus_km,
            characteristic_angles_rad,
            diagnosis.radii,
            diagnosis.points.ravel(),
            comparison_angles_rad,
            tangent_half_angles,
            polar_points_km.ravel(),
            rational_points_km.ravel(),
            uniform_angles_rad,
            chord_lengths_km,
            rotation.ravel(),
            translation_km,
            moved_points_km.ravel(),
            residual_km,
            residual_m,
        ]
    )

    print("uzunluk_birimi:", length_unit)
    print("model: sentetik_ideal_eliptik_yorunge_geometrisi")
    print("dinamik_ve_efemeris_modeli_mi: False")
    print("gercek_gorev_veya_guvenlik_hesabi_mi: False")
    print("odak_km:", frame.focus)
    print("periapsis_yonu_derece:", periapsis_direction_deg)
    print("dismerkezlik:", frame.eccentricity)
    print("yari_odak_kirisi_km:", frame.semilatus_rectum)
    print("yari_buyuk_eksen_km:", f"{semi_major_km:.6f}")
    print("yari_kucuk_eksen_km:", f"{semi_minor_km:.6f}")
    print("merkez_km:", center_km)
    print("ikinci_odak_km:", second_focus_km)
    print("periapsis_uzakligi_km:", f"{periapsis_km:.6f}")
    print("apoapsis_uzakligi_km:", f"{apoapsis_km:.6f}")
    print("ornek_acilar_derece:", np.rad2deg(characteristic_angles_rad))
    print("ornek_yaricaplar_km:", diagnosis.radii)
    print(
        "en_buyuk_cebirsel_artik:",
        f"{max(diagnosis.maximum_absolute_algebraic_residual, np.max(np.abs(rational_algebraic))):.3e}",
    )
    print(
        "en_buyuk_odak_dogrultman_artigi_km:",
        f"{max(diagnosis.maximum_absolute_focus_directrix_residual, np.max(np.abs(rational_geometric_km))):.3e}",
    )
    print("en_buyuk_kutupsal_rasyonel_fark_km:", f"{np.max(representation_gap_km):.3e}")
    print("esit_aci_adimi_kiris_orani:", f"{chord_ratio:.6f}")
    print("rijit_hareket_kovaryant_mi:", bool(np.max(rigid_gap_km) < 4e-12))
    print("ortak_olcekte_boyutsuz_artik_korundu_mu:", bool(np.allclose(residual_m, residual_km, atol=3e-15)))
    print("bilimsel_imza:", canonical_array_sha256(signature_values))


if __name__ == "__main__":
    main()
