"""Bölüm 20: küre ve küre sistemleri laboratuvarı.

Uygulama, dört bilinen merkeze olan tam ve gürültüsüz uzaklıklardan sentetik
bir uzay noktasını bulur. İlk üç küre ayna simetrili iki aday bırakır; dördüncü
küre rankı tamamlayıp tek ortak noktayı seçer. Bu dosya GNSS, fiziksel ölçüm
belirsizliği veya kabul kararı modeli değildir.
"""

from __future__ import annotations

import numpy as np

from agbook import (
    canonical_array_sha256,
    radical_plane_diagnostics,
    sphere_plane_section_diagnostics,
    sphere_point_power,
    sphere_sphere_intersection_diagnostics,
    sphere_system_diagnostics,
    tangent_plane_at_sphere_point,
)


def main() -> None:
    length_unit = "m"
    rank_tolerance = 1.0e-12
    absolute_tolerance_m = 1.0e-11
    relative_tolerance = 1.0e-12
    reference_scale_m = 20.0
    system_options = {
        "rank_tolerance": rank_tolerance,
        "absolute_tolerance": absolute_tolerance_m,
        "relative_tolerance": relative_tolerance,
        "reference_scale": reference_scale_m,
    }
    geometry_options = {
        "absolute_tolerance": absolute_tolerance_m,
        "relative_tolerance": relative_tolerance,
        "reference_scale": reference_scale_m,
    }

    target = np.array([4.0, 6.0, 12.0])
    centers = np.array(
        [
            [0.0, 0.0, 0.0],
            [12.0, 0.0, 0.0],
            [0.0, 16.0, 0.0],
            [0.0, 0.0, 20.0],
        ]
    )
    squared_ranges = np.array([196.0, 244.0, 260.0, 116.0])
    ranges = np.sqrt(squared_ranges)

    three_sphere = sphere_system_diagnostics(
        centers[:3],
        ranges[:3],
        **system_options,
    )
    four_sphere = sphere_system_diagnostics(
        centers,
        ranges,
        **system_options,
    )
    first_pair = sphere_sphere_intersection_diagnostics(
        centers[0],
        ranges[0],
        centers[1],
        ranges[1],
        **geometry_options,
    )
    first_radical_plane = radical_plane_diagnostics(
        centers[0],
        ranges[0],
        centers[1],
        ranges[1],
        **geometry_options,
    )
    horizontal_section = sphere_plane_section_diagnostics(
        centers[0],
        ranges[0],
        [0.0, 0.0, 1.0, -12.0],
        **geometry_options,
    )
    tangent_plane = tangent_plane_at_sphere_point(
        centers[0],
        ranges[0],
        target,
        **geometry_options,
    )

    rotation = np.array(
        [
            [0.0, -1.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    translation = np.array([30.0, -10.0, 7.0])
    moved_centers = centers @ rotation.T + translation
    moved_target = rotation @ target + translation
    moved = sphere_system_diagnostics(
        moved_centers,
        ranges,
        rank_tolerance=rank_tolerance,
        absolute_tolerance=absolute_tolerance_m,
        relative_tolerance=relative_tolerance,
        reference_scale=60.0,
    )

    centimetre_scale = 100.0
    centimetre = sphere_system_diagnostics(
        centimetre_scale * centers,
        centimetre_scale * ranges,
        rank_tolerance=rank_tolerance,
        absolute_tolerance=centimetre_scale * absolute_tolerance_m,
        relative_tolerance=relative_tolerance,
        reference_scale=centimetre_scale * reference_scale_m,
    )

    target_powers = np.array(
        [
            sphere_point_power(centers[index], ranges[index], target)
            for index in range(centers.shape[0])
        ]
    )

    assert three_sphere.relation == "line"
    assert three_sphere.rank == 2
    assert three_sphere.common_locus_type == "two_points"
    np.testing.assert_allclose(three_sphere.anchor, [4.0, 6.0, 0.0], atol=2.0e-13)
    np.testing.assert_allclose(
        three_sphere.common_points,
        [[4.0, 6.0, -12.0], [4.0, 6.0, 12.0]],
        atol=2.0e-12,
    )
    assert four_sphere.relation == "point"
    assert four_sphere.rank == 3
    assert four_sphere.common_locus_type == "point"
    np.testing.assert_allclose(four_sphere.anchor, target, atol=2.0e-13)
    np.testing.assert_allclose(target_powers, 0.0, atol=1.0e-13)
    np.testing.assert_allclose(four_sphere.power_values, 0.0, atol=2.0e-12)
    assert first_pair.relation == "intersection_circle"
    assert first_radical_plane.relation == "plane"
    np.testing.assert_allclose(
        first_pair.circle_plane,
        first_radical_plane.plane_coefficients,
        atol=2.0e-15,
    )
    assert horizontal_section.relation == "circle"
    np.testing.assert_allclose(horizontal_section.section_center, [0.0, 0.0, 12.0])
    np.testing.assert_allclose(horizontal_section.section_radius, np.sqrt(52.0))
    np.testing.assert_allclose(tangent_plane[:3], target / ranges[0], atol=2.0e-15)
    np.testing.assert_allclose(
        tangent_plane[:3] @ target + tangent_plane[3],
        0.0,
        atol=3.0e-15,
    )
    np.testing.assert_allclose(moved.anchor, moved_target, atol=3.0e-13)
    np.testing.assert_allclose(
        centimetre.anchor,
        centimetre_scale * target,
        atol=3.0e-11,
    )
    assert centimetre.relation == four_sphere.relation
    np.testing.assert_allclose(
        centimetre.condition_number,
        four_sphere.condition_number,
        rtol=2.0e-15,
    )

    signature_values = np.concatenate(
        [
            target,
            centers.ravel(),
            squared_ranges,
            ranges,
            three_sphere.anchor,
            three_sphere.direction_basis.ravel(),
            three_sphere.common_points.ravel(),
            four_sphere.anchor,
            four_sphere.singular_values,
            four_sphere.equation_residuals,
            four_sphere.power_values,
            first_pair.circle_center,
            np.array([first_pair.circle_radius]),
            first_radical_plane.plane_coefficients,
            horizontal_section.section_center,
            np.array([horizontal_section.section_radius]),
            tangent_plane,
            moved.anchor,
            centimetre.anchor,
            np.array(
                [
                    four_sphere.condition_number,
                    four_sphere.length_threshold,
                    four_sphere.power_threshold,
                    rank_tolerance,
                    absolute_tolerance_m,
                    relative_tolerance,
                    reference_scale_m,
                ]
            ),
        ]
    )

    print("uzunluk_birimi:", length_unit)
    print("model: sentetik_gurultusuz_mesafe_kureleriyle_konumlama")
    print("gercek_gnss_modeli_mi: False")
    print("olculmus_veri_mi: False")
    print("olcum_belirsizligi_hesabi_mi: False")
    print("hedef_nokta_m:", target)
    print("uzakliklar_m:", ranges)
    print("ilk_uc_kure_ranki:", three_sphere.rank)
    print("ilk_uc_kure_esit_guc_yeri:", three_sphere.relation)
    print("ilk_uc_kure_ortak_yeri:", three_sphere.common_locus_type)
    print("ayna_adaylari_m:", three_sphere.common_points)
    print("dort_kure_ranki:", four_sphere.rank)
    print("dort_kure_esit_guc_yeri:", four_sphere.relation)
    print("dort_kure_ortak_yeri:", four_sphere.common_locus_type)
    print("cozum_m:", four_sphere.anchor)
    print("guc_degerleri_m2:", four_sphere.power_values)
    print("guc_yayilimi_m2:", f"{four_sphere.power_spread:.12e}")
    print("kosul_sayisi:", f"{four_sphere.condition_number:.12f}")
    print("birinci_ikili_kesisim:", first_pair.relation)
    print("birinci_radikal_duzlem:", first_radical_plane.plane_coefficients)
    print("z_12_kesit_yaricapi_m:", f"{horizontal_section.section_radius:.12f}")
    print("hedefte_teget_duzlem:", tangent_plane)
    print("rijit_harekette_cozum_korundu_mu:", np.allclose(moved.anchor, moved_target))
    print(
        "metreden_santimetreye_cozum_orani:",
        centimetre.anchor / four_sphere.anchor,
    )
    print("rank_esigi:", f"{rank_tolerance:.12e}")
    print("mutlak_uzunluk_esigi_m:", f"{absolute_tolerance_m:.12e}")
    print("bagil_uzunluk_esigi:", f"{relative_tolerance:.12e}")
    print("referans_uzunlugu_m:", f"{reference_scale_m:.12f}")
    print("bilimsel_imza:", canonical_array_sha256(signature_values))


if __name__ == "__main__":
    main()
