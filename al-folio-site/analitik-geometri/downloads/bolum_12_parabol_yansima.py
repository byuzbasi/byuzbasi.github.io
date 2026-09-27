"""Bölüm 12: ideal parabolik reflektör ve yansıma laboratuvarı.

Model, bir antenin yalnız iki boyutlu parabol kesitini ve geometrik optik
yansımasını temsil eder. Dalga boyu, kırınım, kazanç, besleme örüntüsü,
yüzey hatası, malzeme ve yapısal deformasyon içermez.
"""

from __future__ import annotations

import numpy as np

from agbook import (
    canonical_array_sha256,
    focus_directrix_diagnostics,
    parabola_algebraic_residuals,
    parabola_frame_from_vertex_axis,
    parabola_points,
    parabola_reflection_diagnostics,
    parabola_tangent_line,
    parabolic_reflector_focal_length,
    rotation_matrix_2d,
)


def main() -> None:
    aperture_diameter_m = 8.0
    depth_m = 1.0
    focal_length_m = parabolic_reflector_focal_length(
        aperture_diameter_m,
        depth_m,
    )
    vertex_m = np.array([0.0, 0.0])
    axis = np.array([0.0, 1.0])
    frame = parabola_frame_from_vertex_axis(vertex_m, axis, focal_length_m)

    rim_parameter = aperture_diameter_m / (4.0 * focal_length_m)
    parameters = np.linspace(-rim_parameter, rim_parameter, 9)
    surface_points_m = parabola_points(
        frame.vertex,
        frame.axis_direction,
        frame.focal_length,
        parameters,
    )
    algebraic_residuals_m2 = parabola_algebraic_residuals(
        surface_points_m,
        frame.vertex,
        frame.axis_direction,
        frame.focal_length,
    )
    locus = focus_directrix_diagnostics(
        surface_points_m,
        frame.focus,
        frame.directrix,
        1.0,
        reference_scale=aperture_diameter_m,
    )
    reflection = parabola_reflection_diagnostics(
        frame.vertex,
        frame.axis_direction,
        frame.focal_length,
        parameters,
    )
    tangent_lines = np.vstack(
        [
            parabola_tangent_line(
                frame.vertex,
                frame.axis_direction,
                frame.focal_length,
                parameter,
            )
            for parameter in parameters
        ]
    )
    tangent_point_residuals_m = np.sum(
        tangent_lines[:, :2] * surface_points_m,
        axis=1,
    ) + tangent_lines[:, 2]

    rim_depths_m = surface_points_m[[0, -1], 1] - frame.vertex[1]
    rim_span_m = np.linalg.norm(surface_points_m[-1] - surface_points_m[0])
    np.testing.assert_allclose(rim_depths_m, depth_m, atol=1e-14)
    np.testing.assert_allclose(rim_span_m, aperture_diameter_m, atol=1e-14)
    np.testing.assert_allclose(algebraic_residuals_m2, 0.0, atol=2e-14)
    np.testing.assert_allclose(tangent_point_residuals_m, 0.0, atol=2e-14)
    assert locus.maximum_absolute_residual < 2e-14
    assert reflection.maximum_direction_error < 2e-14
    assert reflection.maximum_focus_line_residual < 2e-14

    rotation = rotation_matrix_2d(np.deg2rad(29.0))
    translation_m = np.array([12.0, -7.0])
    moved_vertex_m = rotation @ frame.vertex + translation_m
    moved_axis = rotation @ frame.axis_direction
    moved = parabola_reflection_diagnostics(
        moved_vertex_m,
        moved_axis,
        frame.focal_length,
        parameters,
    )
    expected_moved_points_m = surface_points_m @ rotation.T + translation_m
    np.testing.assert_allclose(moved.points, expected_moved_points_m, atol=3e-14)
    np.testing.assert_allclose(
        moved.reflected_directions,
        reflection.reflected_directions @ rotation.T,
        atol=3e-14,
    )

    focal_length_mm = parabolic_reflector_focal_length(
        1000.0 * aperture_diameter_m,
        1000.0 * depth_m,
    )
    np.testing.assert_allclose(focal_length_mm, 1000.0 * focal_length_m)

    signature_values = np.concatenate(
        [
            np.array(
                [
                    aperture_diameter_m,
                    depth_m,
                    focal_length_m,
                    rim_parameter,
                ]
            ),
            frame.vertex,
            frame.focus,
            frame.directrix,
            frame.axis_direction,
            parameters,
            surface_points_m.ravel(),
            tangent_lines.ravel(),
            reflection.reflected_directions.ravel(),
            rotation.ravel(),
            translation_m,
            moved.points.ravel(),
        ]
    )

    print("birim: m")
    print("model: sentetik_iki_boyutlu_ideal_parabolik_reflektor")
    print("elektromanyetik_tasarim_mi: False")
    print("aciklik_capi_m:", aperture_diameter_m)
    print("merkez_derinligi_m:", depth_m)
    print("odak_uzakligi_m:", focal_length_m)
    print("odak_orani_f_bolu_D:", focal_length_m / aperture_diameter_m)
    print("tepe_m:", frame.vertex)
    print("odak_m:", frame.focus)
    print("dogrultman:", frame.directrix)
    print("yuzey_noktasi_sayisi:", surface_points_m.shape[0])
    print("kenar_noktalari_m:", surface_points_m[[0, -1]])
    print(
        "en_buyuk_odak_dogrultman_artigi_m:",
        f"{locus.maximum_absolute_residual:.3e}",
    )
    print(
        "en_buyuk_cebirsel_artik_m2:",
        f"{np.max(np.abs(algebraic_residuals_m2)):.3e}",
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
    print("rijit_noktalar_korundu_mu:", bool(np.allclose(moved.points, expected_moved_points_m)))
    print("mm_olceginde_odak_uzakligi:", focal_length_mm)
    print("bilimsel_imza:", canonical_array_sha256(signature_values))


if __name__ == "__main__":
    main()
