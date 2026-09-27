"""Bölüm 18: uzayda doğru, düzlem ve rank tanısı laboratuvarı.

Uygulama, sentetik bir CAD datum düzlemi ile delik ekseninin eşdeğer
gösterimlerini sınar. Ölçülmüş veri, üretim toleransı, delik kalitesi veya
kabul kararı içermez.
"""

from __future__ import annotations

import numpy as np

from agbook import (
    affine_system_diagnostics_3d,
    canonical_array_sha256,
    canonical_plane_coefficients,
    parametric_line_points_3d,
    plane_from_points_3d,
    plane_membership_diagnostics_3d,
    plane_residuals_3d,
)


def main() -> None:
    length_unit = "mm"
    rank_relative_tolerance = 1.0e-12
    reference_scale_mm = 200.0

    point_a = np.array([120.0, 80.0, 35.0])
    point_b = np.array([156.0, 128.0, 35.0])
    point_c = np.array([96.0, 98.0, 75.0])
    datum_points_mm = np.vstack([point_a, point_b, point_c])

    datum_plane_mm = plane_from_points_3d(point_a, point_b, point_c)
    expected_normal = np.array([0.64, -0.48, 0.60])
    scaled_plane = canonical_plane_coefficients(-25.0 * datum_plane_mm)

    # Yön uzunluk birimindedir; t boyutsuzdur ve ||direction|| = 25 mm'dir.
    axis_direction_mm = np.array([16.0, -12.0, 15.0])
    axis_parameters = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
    axis_points_mm = parametric_line_points_3d(
        point_a,
        axis_direction_mm,
        axis_parameters,
    )

    # İki birim normalin düzlemleri delik eksenini ortak çözüm olarak verir.
    tangent_1 = np.array([0.60, 0.80, 0.0])
    tangent_2 = np.array([-0.48, 0.36, 0.80])
    axis_matrix = np.vstack([tangent_1, tangent_2])
    axis_rhs_mm = axis_matrix @ point_a
    axis_diagnosis_mm = affine_system_diagnostics_3d(
        axis_matrix,
        axis_rhs_mm,
        rank_relative_tolerance=rank_relative_tolerance,
        reference_scale=reference_scale_mm,
    )
    axis_plane_residuals = np.column_stack(
        [
            plane_residuals_3d(
                np.concatenate([axis_matrix[index], [-axis_rhs_mm[index]]]),
                axis_points_mm,
            )
            for index in range(2)
        ]
    )

    full_matrix = np.vstack([axis_matrix, expected_normal])
    full_rhs_mm = full_matrix @ point_a
    anchor_diagnosis_mm = affine_system_diagnostics_3d(
        full_matrix,
        full_rhs_mm,
        rank_relative_tolerance=rank_relative_tolerance,
        reference_scale=reference_scale_mm,
    )

    membership_b = plane_membership_diagnostics_3d(
        datum_plane_mm,
        point_b,
        absolute_tolerance=1.0e-12,
        relative_tolerance=0.0,
        reference_scale=reference_scale_mm,
    )
    membership_c = plane_membership_diagnostics_3d(
        datum_plane_mm,
        point_c,
        absolute_tolerance=1.0e-12,
        relative_tolerance=0.0,
        reference_scale=reference_scale_mm,
    )

    datum_points_m = datum_points_mm * 1.0e-3
    datum_plane_m = plane_from_points_3d(*datum_points_m)
    axis_rhs_m = axis_matrix @ (point_a * 1.0e-3)
    axis_diagnosis_m = affine_system_diagnostics_3d(
        axis_matrix,
        axis_rhs_m,
        rank_relative_tolerance=rank_relative_tolerance,
        reference_scale=reference_scale_mm * 1.0e-3,
    )

    # Aynı tam verinin iki açık rank eşiğinde farklı sayısal çözünürlüğü.
    perturbation = 1.0e-10
    near_matrix = np.vstack([tangent_1, tangent_1 + perturbation * tangent_2])
    near_rhs_mm = near_matrix @ point_a
    coarse_rank = affine_system_diagnostics_3d(
        near_matrix,
        near_rhs_mm,
        rank_relative_tolerance=1.0e-8,
        reference_scale=reference_scale_mm,
    )
    fine_rank = affine_system_diagnostics_3d(
        near_matrix,
        near_rhs_mm,
        rank_relative_tolerance=1.0e-12,
        reference_scale=reference_scale_mm,
    )

    np.testing.assert_allclose(
        datum_plane_mm,
        [0.64, -0.48, 0.60, -59.4],
        atol=2.0e-14,
    )
    np.testing.assert_allclose(scaled_plane, datum_plane_mm, atol=2.0e-14)
    np.testing.assert_allclose(axis_direction_mm / 25.0, expected_normal)
    np.testing.assert_allclose(axis_points_mm[2], point_a)
    np.testing.assert_allclose(axis_plane_residuals, 0.0, atol=3.0e-14)
    assert axis_diagnosis_mm.classification == "line"
    assert axis_diagnosis_mm.coefficient_rank == 2
    assert axis_diagnosis_mm.solution_dimension == 1
    assert anchor_diagnosis_mm.classification == "point"
    assert anchor_diagnosis_mm.coefficient_rank == 3
    np.testing.assert_allclose(
        anchor_diagnosis_mm.least_squares_point,
        point_a,
        atol=4.0e-14,
    )
    assert membership_b.on_plane and membership_c.on_plane
    np.testing.assert_allclose(datum_plane_m[:3], datum_plane_mm[:3], atol=2.0e-15)
    np.testing.assert_allclose(datum_plane_m[3], 1.0e-3 * datum_plane_mm[3], atol=2.0e-16)
    assert axis_diagnosis_m.classification == axis_diagnosis_mm.classification
    np.testing.assert_allclose(
        axis_diagnosis_m.least_squares_point,
        1.0e-3 * axis_diagnosis_mm.least_squares_point,
        atol=3.0e-16,
    )
    assert coarse_rank.classification == "plane"
    assert fine_rank.classification == "line"

    signature_values = np.concatenate(
        [
            datum_points_mm.ravel(),
            datum_plane_mm,
            axis_direction_mm,
            axis_parameters,
            axis_points_mm.ravel(),
            axis_matrix.ravel(),
            axis_rhs_mm,
            axis_diagnosis_mm.coefficient_singular_values,
            axis_diagnosis_mm.augmented_singular_values,
            full_matrix.ravel(),
            full_rhs_mm,
            anchor_diagnosis_mm.least_squares_point,
            datum_points_m.ravel(),
            datum_plane_m,
            axis_rhs_m,
            near_matrix.ravel(),
            near_rhs_mm,
            coarse_rank.coefficient_singular_values,
            fine_rank.coefficient_singular_values,
            np.array(
                [
                    rank_relative_tolerance,
                    reference_scale_mm,
                    perturbation,
                    membership_b.normalized_residual,
                    membership_c.normalized_residual,
                ]
            ),
        ]
    )

    print("uzunluk_birimi:", length_unit)
    print("model: sentetik_cad_datum_duzlemi_ve_delik_ekseni")
    print("olculmus_veri_mi: False")
    print("uretim_toleransi_hesabi_mi: False")
    print("uretim_kabul_hesabi_mi: False")
    print("datum_noktalari_mm:")
    print(datum_points_mm)
    print("datum_duzlemi_kanonik:", datum_plane_mm)
    print("olceklenmis_denklem_ayni_duzlem_mi:", bool(np.allclose(scaled_plane, datum_plane_mm)))
    print("delik_ekseni_baslangici_mm:", point_a)
    print("delik_ekseni_yonu_mm:", axis_direction_mm)
    print("delik_ekseni_iki_duzlem_ranki:", axis_diagnosis_mm.coefficient_rank)
    print("delik_ekseni_cozum_boyutu:", axis_diagnosis_mm.solution_dimension)
    print("delik_ekseni_sinifi:", axis_diagnosis_mm.classification)
    print("uc_bagimsiz_duzlem_ranki:", anchor_diagnosis_mm.coefficient_rank)
    print("uc_bagimsiz_duzlem_sinifi:", anchor_diagnosis_mm.classification)
    print("tek_nokta_cozumu_mm:", anchor_diagnosis_mm.least_squares_point)
    print("B_ve_C_datum_duzleminde_mi:", membership_b.on_plane and membership_c.on_plane)
    print("metreye_geciste_normal_korundu_mu:", bool(np.allclose(datum_plane_m[:3], datum_plane_mm[:3])))
    print("metreye_geciste_sabit_terim_olcegi:", f"{datum_plane_m[3] / datum_plane_mm[3]:.12f}")
    print("metreye_geciste_rank_sinifi_korundu_mu:", axis_diagnosis_m.classification == axis_diagnosis_mm.classification)
    print("yakin_bagimli_sistem_kaba_esik:", coarse_rank.classification)
    print("yakin_bagimli_sistem_ince_esik:", fine_rank.classification)
    print("rank_bagil_esigi:", f"{rank_relative_tolerance:.12e}")
    print("referans_uzunlugu_mm:", f"{reference_scale_mm:.12f}")
    print("bilimsel_imza:", canonical_array_sha256(signature_values))


if __name__ == "__main__":
    main()
