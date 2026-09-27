"""Bölüm 16: genel ikinci derece denklem ve sınıflandırma laboratuvarı.

Uygulama, döndürülmüş eliptik bir CAD açıklığının sentetik geometrisidir.
Ölçüm verisi, konik uydurma, üretim toleransı veya kabul kararı içermez.
"""

from __future__ import annotations

import numpy as np

from agbook import (
    canonical_array_sha256,
    quadratic_conic_diagnostics,
    quadratic_conic_residuals,
    rotation_matrix_2d,
    transform_quadratic_conic,
)


def main() -> None:
    length_unit = "mm"
    center_mm = np.array([120.0, 80.0])
    semi_axes_mm = np.array([45.0, 20.0])
    major_axis_angle_deg = 32.0
    rotation = rotation_matrix_2d(np.deg2rad(major_axis_angle_deg))

    canonical_coefficients = np.array(
        [
            1.0 / semi_axes_mm[0] ** 2,
            0.0,
            1.0 / semi_axes_mm[1] ** 2,
            0.0,
            0.0,
            -1.0,
        ]
    )
    coefficients_mm = transform_quadratic_conic(
        canonical_coefficients,
        rotation.T,
        -rotation.T @ center_mm,
    )
    diagnosis_mm = quadratic_conic_diagnostics(
        coefficients_mm,
        coordinate_scale=100.0,
        relative_tolerance=1e-12,
    )

    parameters = np.linspace(0.0, 2.0 * np.pi, 25, endpoint=False)
    local_points_mm = np.column_stack(
        [
            semi_axes_mm[0] * np.cos(parameters),
            semi_axes_mm[1] * np.sin(parameters),
        ]
    )
    global_points_mm = local_points_mm @ rotation.T + center_mm
    residuals_mm = quadratic_conic_residuals(
        coefficients_mm,
        global_points_mm,
        coordinate_scale=100.0,
    )

    coefficients_m = coefficients_mm * np.array(
        [1e6, 1e6, 1e6, 1e3, 1e3, 1.0]
    )
    diagnosis_m = quadratic_conic_diagnostics(
        coefficients_m,
        coordinate_scale=0.1,
        relative_tolerance=1e-12,
    )
    residuals_m = quadratic_conic_residuals(
        coefficients_m,
        global_points_mm / 1000.0,
        coordinate_scale=0.1,
    )

    scaled_diagnosis = quadratic_conic_diagnostics(
        -17.0 * coefficients_mm,
        coordinate_scale=100.0,
        relative_tolerance=1e-12,
    )
    major_projector = np.outer(diagnosis_mm.principal_directions[:, 0], diagnosis_mm.principal_directions[:, 0])
    expected_major_projector = np.outer(rotation[:, 0], rotation[:, 0])

    np.testing.assert_allclose(diagnosis_mm.center, center_mm, atol=3e-13)
    np.testing.assert_allclose(diagnosis_mm.semi_axes, semi_axes_mm, atol=3e-13)
    np.testing.assert_allclose(major_projector, expected_major_projector, atol=3e-13)
    np.testing.assert_allclose(diagnosis_m.center, center_mm / 1000.0, atol=3e-15)
    np.testing.assert_allclose(diagnosis_m.semi_axes, semi_axes_mm / 1000.0, atol=3e-15)
    np.testing.assert_allclose(
        diagnosis_m.normalized_coefficients,
        diagnosis_mm.normalized_coefficients,
        atol=3e-15,
    )
    np.testing.assert_allclose(residuals_m, residuals_mm, atol=3e-15)
    np.testing.assert_allclose(scaled_diagnosis.center, diagnosis_mm.center, atol=3e-13)
    np.testing.assert_allclose(scaled_diagnosis.semi_axes, diagnosis_mm.semi_axes, atol=3e-13)
    assert diagnosis_mm.locus_type == diagnosis_m.locus_type == "ellipse"
    assert scaled_diagnosis.locus_type == "ellipse"
    assert not diagnosis_mm.numerically_ambiguous
    assert np.max(np.abs(residuals_mm)) < 2e-15

    near_boundary = quadratic_conic_diagnostics(
        [1.0, 0.0, 1e-14, 0.0, 0.0, -1.0],
        relative_tolerance=1e-12,
    )
    signature_values = np.concatenate(
        [
            center_mm,
            semi_axes_mm,
            np.array([major_axis_angle_deg]),
            rotation.ravel(),
            canonical_coefficients,
            coefficients_mm,
            diagnosis_mm.normalized_coefficients,
            diagnosis_mm.eigenvalues,
            diagnosis_mm.center,
            diagnosis_mm.semi_axes,
            diagnosis_mm.principal_directions.ravel(),
            parameters,
            global_points_mm.ravel(),
            residuals_mm,
            coefficients_m,
            diagnosis_m.normalized_coefficients,
        ]
    )

    print("uzunluk_birimi:", length_unit)
    print("model: sentetik_dondurulmus_eliptik_cad_acikligi")
    print("olculmus_veri_mi: False")
    print("konik_uydurma_yapildi_mi: False")
    print("uretim_kabul_hesabi_mi: False")
    print("genel_katsayilar_A_B_C_D_E_F0:", coefficients_mm)
    print("sinif:", diagnosis_mm.locus_type)
    print("Q_ranki:", diagnosis_mm.quadratic_rank)
    print("H_ranki:", diagnosis_mm.homogeneous_rank)
    print("atalet_pozitif_negatif_sifir:", diagnosis_mm.inertia)
    print("geri_kazanilan_merkez_mm:", diagnosis_mm.center)
    print("geri_kazanilan_yari_eksenler_mm:", diagnosis_mm.semi_axes)
    print("geri_kazanilan_ana_eksen_acisi_derece:", f"{np.rad2deg(diagnosis_mm.orientation_radians):.6f}")
    print("en_buyuk_boyutsuz_artik:", f"{np.max(np.abs(residuals_mm)):.3e}")
    print("katsayi_carpani_altinda_sinif_korundu_mu:", scaled_diagnosis.locus_type == diagnosis_mm.locus_type)
    print("metre_milimetre_tanisi_korundu_mu:", bool(np.allclose(diagnosis_m.normalized_coefficients, diagnosis_mm.normalized_coefficients, atol=3e-15)))
    print("yakin_rank_kaybi_adayi:", near_boundary.locus_type)
    print("yakin_rank_karari_belirsiz_isaretli_mi:", near_boundary.numerically_ambiguous)
    print("bilimsel_imza:", canonical_array_sha256(signature_values))


if __name__ == "__main__":
    main()
