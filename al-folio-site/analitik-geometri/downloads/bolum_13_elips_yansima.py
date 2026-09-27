"""Bölüm 13: ideal eliptik akustik/optik yansıtıcı laboratuvarı.

Model yalnız iki boyutlu bir elips kesitini ve geometrik ışın yansımasını
temsil eder. Kırınım, soğurma, faz, yüzey kusuru, kaynak yönlülüğü ve gerçek
bir yapının akustik ya da optik performansı modele dahil değildir.
"""

from __future__ import annotations

import numpy as np

from agbook import (
    canonical_array_sha256,
    ellipse_algebraic_residuals,
    ellipse_focal_sum_residuals,
    ellipse_frame_from_center_axes,
    ellipse_points,
    ellipse_reflection_diagnostics,
    ellipse_tangent_line,
    focus_directrix_diagnostics,
    rotation_matrix_2d,
)


def main() -> None:
    semi_major_m = 10.0
    semi_minor_m = 6.0
    center_m = np.array([0.0, 0.0])
    major_axis = np.array([1.0, 0.0])
    frame = ellipse_frame_from_center_axes(
        center_m,
        major_axis,
        semi_major_m,
        semi_minor_m,
    )

    parameters_rad = np.linspace(0.0, 2.0 * np.pi, 12, endpoint=False)
    boundary_points_m = ellipse_points(
        frame.center,
        frame.major_direction,
        frame.semi_major,
        frame.semi_minor,
        parameters_rad,
    )
    algebraic_residuals = ellipse_algebraic_residuals(
        boundary_points_m,
        frame.center,
        frame.major_direction,
        frame.semi_major,
        frame.semi_minor,
    )
    focal_sum_residuals_m = ellipse_focal_sum_residuals(
        boundary_points_m,
        frame.first_focus,
        frame.second_focus,
        frame.semi_major,
    )
    focus_directrix = focus_directrix_diagnostics(
        boundary_points_m,
        frame.second_focus,
        frame.second_directrix,
        frame.eccentricity,
        reference_scale=2.0 * frame.semi_major,
    )
    reflection = ellipse_reflection_diagnostics(
        frame.center,
        frame.major_direction,
        frame.semi_major,
        frame.semi_minor,
        parameters_rad,
    )
    tangent_lines = np.vstack(
        [
            ellipse_tangent_line(
                frame.center,
                frame.major_direction,
                frame.semi_major,
                frame.semi_minor,
                parameter,
            )
            for parameter in parameters_rad
        ]
    )
    tangent_point_residuals_m = np.sum(
        tangent_lines[:, :2] * boundary_points_m,
        axis=1,
    ) + tangent_lines[:, 2]

    np.testing.assert_allclose(algebraic_residuals, 0.0, atol=4e-15)
    np.testing.assert_allclose(focal_sum_residuals_m, 0.0, atol=4e-15)
    np.testing.assert_allclose(tangent_point_residuals_m, 0.0, atol=4e-15)
    np.testing.assert_allclose(reflection.focal_path_lengths, 20.0, atol=4e-14)
    assert focus_directrix.maximum_absolute_residual < 4e-15
    assert reflection.maximum_direction_error < 2e-15
    assert reflection.maximum_focus_line_residual < 2e-14

    rotation = rotation_matrix_2d(np.deg2rad(31.0))
    translation_m = np.array([13.0, -7.0])
    moved_center_m = rotation @ frame.center + translation_m
    moved_axis = rotation @ frame.major_direction
    moved = ellipse_reflection_diagnostics(
        moved_center_m,
        moved_axis,
        frame.semi_major,
        frame.semi_minor,
        parameters_rad,
    )
    expected_moved_points_m = boundary_points_m @ rotation.T + translation_m
    np.testing.assert_allclose(moved.points, expected_moved_points_m, atol=4e-14)
    np.testing.assert_allclose(
        moved.reflected_directions,
        reflection.reflected_directions @ rotation.T,
        atol=4e-14,
    )

    scaled = ellipse_frame_from_center_axes(
        1000.0 * frame.center,
        frame.major_direction,
        1000.0 * frame.semi_major,
        1000.0 * frame.semi_minor,
    )
    np.testing.assert_allclose(scaled.eccentricity, frame.eccentricity)
    np.testing.assert_allclose(scaled.focal_distance, 1000.0 * frame.focal_distance)

    signature_values = np.concatenate(
        [
            np.array(
                [
                    frame.semi_major,
                    frame.semi_minor,
                    frame.focal_distance,
                    frame.eccentricity,
                ]
            ),
            frame.center,
            frame.first_focus,
            frame.second_focus,
            frame.first_directrix,
            frame.second_directrix,
            parameters_rad,
            boundary_points_m.ravel(),
            tangent_lines.ravel(),
            reflection.reflected_directions.ravel(),
            reflection.focal_path_lengths,
            rotation.ravel(),
            translation_m,
            moved.points.ravel(),
        ]
    )

    print("birim: m")
    print("model: sentetik_iki_boyutlu_ideal_eliptik_yansitici")
    print("gercek_akustik_veya_optik_tasarim_mi: False")
    print("yari_buyuk_eksen_m:", frame.semi_major)
    print("yari_kucuk_eksen_m:", frame.semi_minor)
    print("dogrusal_dismerkezlik_m:", frame.focal_distance)
    print("dismerkezlik:", frame.eccentricity)
    print("birinci_odak_m:", frame.first_focus)
    print("ikinci_odak_m:", frame.second_focus)
    print("sinir_noktasi_sayisi:", boundary_points_m.shape[0])
    print("sabit_kirik_yol_m:", 2.0 * frame.semi_major)
    print(
        "en_buyuk_cebirsel_artik:",
        f"{np.max(np.abs(algebraic_residuals)):.3e}",
    )
    print(
        "en_buyuk_odak_toplam_artigi_m:",
        f"{np.max(np.abs(focal_sum_residuals_m)):.3e}",
    )
    print(
        "en_buyuk_odak_dogrultman_artigi_m:",
        f"{focus_directrix.maximum_absolute_residual:.3e}",
    )
    print(
        "en_buyuk_teget_nokta_artigi_m:",
        f"{np.max(np.abs(tangent_point_residuals_m)):.3e}",
    )
    print(
        "en_buyuk_yansima_yon_hatasi:",
        f"{reflection.maximum_direction_error:.3e}",
    )
    print(
        "en_buyuk_odak_cizgisi_artigi_m:",
        f"{reflection.maximum_focus_line_residual:.3e}",
    )
    print(
        "rijit_noktalar_korundu_mu:",
        bool(np.allclose(moved.points, expected_moved_points_m)),
    )
    print("mm_olceginde_dogrusal_dismerkezlik:", scaled.focal_distance)
    print("bilimsel_imza:", canonical_array_sha256(signature_values))


if __name__ == "__main__":
    main()
