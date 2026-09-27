"""Bölüm 19: uzayda kesişim, açı, izdüşüm ve uzaklık laboratuvarı.

Uygulama sentetik bir CAD datum düzlemi, delik ekseni ve ikinci doğru
adayını sınar. Ölçülmüş veri, üretim toleransı veya kabul kararı içermez.
"""

from __future__ import annotations

import numpy as np

from agbook import (
    canonical_array_sha256,
    line_line_diagnostics_3d,
    line_plane_diagnostics_3d,
    plane_plane_diagnostics_3d,
    project_point_to_line_3d,
    project_point_to_plane_3d,
)


def main() -> None:
    length_unit = "mm"
    angular_tolerance = 1.0e-12
    absolute_tolerance_mm = 1.0e-9
    relative_tolerance = 1.0e-12
    reference_scale_mm = 200.0
    relation_options = {
        "angular_tolerance": angular_tolerance,
        "absolute_tolerance": absolute_tolerance_mm,
        "relative_tolerance": relative_tolerance,
        "reference_scale": reference_scale_mm,
    }

    point_a = np.array([120.0, 80.0, 35.0])
    axis_direction = np.array([16.0, -12.0, 15.0])
    point_q = np.array([115.2, 83.6, 43.0])
    second_direction = np.array([12.0, 16.0, 0.0])
    connector = point_q - point_a

    datum_plane = np.array([0.64, -0.48, 0.60, -59.4])
    first_axis_normal = np.array([0.60, 0.80, 0.0])
    second_axis_normal = np.array([-0.48, 0.36, 0.80])
    first_axis_plane = np.append(first_axis_normal, -first_axis_normal @ point_a)
    second_axis_plane = np.append(second_axis_normal, -second_axis_normal @ point_a)

    line_pair = line_line_diagnostics_3d(
        point_a,
        axis_direction,
        point_q,
        second_direction,
        **relation_options,
    )
    q_on_axis_projection = project_point_to_line_3d(
        point_a,
        axis_direction,
        point_q,
    )
    a_on_second_projection = project_point_to_line_3d(
        point_q,
        second_direction,
        point_a,
    )
    axis_datum = line_plane_diagnostics_3d(
        point_a,
        axis_direction,
        datum_plane,
        **relation_options,
    )
    second_datum = line_plane_diagnostics_3d(
        point_q,
        second_direction,
        datum_plane,
        **relation_options,
    )
    axis_plane_pair = plane_plane_diagnostics_3d(
        first_axis_plane,
        second_axis_plane,
        **relation_options,
    )

    probe_point = point_a + 12.0 * datum_plane[:3]
    probe_projection = project_point_to_plane_3d(datum_plane, probe_point)

    scale = 1.0e-3
    metre_options = {
        "angular_tolerance": angular_tolerance,
        "absolute_tolerance": scale * absolute_tolerance_mm,
        "relative_tolerance": relative_tolerance,
        "reference_scale": scale * reference_scale_mm,
    }
    metre_pair = line_line_diagnostics_3d(
        scale * point_a,
        scale * axis_direction,
        scale * point_q,
        scale * second_direction,
        **metre_options,
    )

    loose_near_parallel = line_line_diagnostics_3d(
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [1.0, 1.0e-8, 0.0],
        angular_tolerance=1.0e-7,
        absolute_tolerance=1.0e-7,
        relative_tolerance=0.0,
        reference_scale=1.0,
    )
    strict_near_parallel = line_line_diagnostics_3d(
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [1.0, 1.0e-8, 0.0],
        angular_tolerance=1.0e-10,
        absolute_tolerance=1.0e-7,
        relative_tolerance=0.0,
        reference_scale=1.0,
    )

    np.testing.assert_allclose(np.dot(connector, axis_direction), 0.0, atol=3.0e-13)
    np.testing.assert_allclose(np.dot(connector, second_direction), 0.0, atol=3.0e-13)
    assert line_pair.relation == "skew"
    np.testing.assert_allclose(line_pair.closest_point_first, point_a, atol=3.0e-14)
    np.testing.assert_allclose(line_pair.closest_point_second, point_q, atol=3.0e-14)
    np.testing.assert_allclose(line_pair.distance, 10.0, atol=2.0e-14)
    np.testing.assert_allclose(q_on_axis_projection.foot, point_a, atol=3.0e-14)
    np.testing.assert_allclose(a_on_second_projection.foot, point_q, atol=3.0e-14)
    assert axis_datum.relation == "intersecting"
    np.testing.assert_allclose(axis_datum.intersection_point, point_a, atol=2.0e-14)
    assert second_datum.relation == "contained"
    assert axis_plane_pair.relation == "intersecting"
    np.testing.assert_allclose(
        axis_plane_pair.line_direction,
        axis_direction / np.linalg.norm(axis_direction),
        atol=2.0e-15,
    )
    np.testing.assert_allclose(probe_projection.foot, point_a, atol=3.0e-14)
    np.testing.assert_allclose(probe_projection.signed_distance, 12.0, atol=2.0e-14)
    assert metre_pair.relation == line_pair.relation
    np.testing.assert_allclose(metre_pair.distance, scale * line_pair.distance, atol=3.0e-17)
    assert loose_near_parallel.relation == "parallel"
    assert loose_near_parallel.numerically_ambiguous
    assert strict_near_parallel.relation == "intersecting"
    assert strict_near_parallel.condition_number > 1.0e8

    signature_values = np.concatenate(
        [
            point_a,
            axis_direction,
            point_q,
            second_direction,
            connector,
            datum_plane,
            first_axis_plane,
            second_axis_plane,
            line_pair.closest_point_first,
            line_pair.closest_point_second,
            line_pair.separation_vector,
            np.array(
                [
                    line_pair.distance,
                    line_pair.small_angle,
                    line_pair.condition_number,
                    q_on_axis_projection.distance,
                    a_on_second_projection.distance,
                    axis_datum.line_plane_angle,
                    second_datum.signed_anchor_distance,
                    axis_plane_pair.small_angle,
                    probe_projection.signed_distance,
                    metre_pair.distance,
                    loose_near_parallel.condition_number,
                    strict_near_parallel.condition_number,
                    angular_tolerance,
                    absolute_tolerance_mm,
                    relative_tolerance,
                    reference_scale_mm,
                ]
            ),
        ]
    )

    print("uzunluk_birimi:", length_unit)
    print("model: sentetik_cad_aykiri_dogrular_ve_datum_duzlemi")
    print("olculmus_veri_mi: False")
    print("uretim_toleransi_hesabi_mi: False")
    print("uretim_kabul_hesabi_mi: False")
    print("dogru_dogru_sinifi:", line_pair.relation)
    print("en_yakin_birinci_nokta_mm:", line_pair.closest_point_first)
    print("en_yakin_ikinci_nokta_mm:", line_pair.closest_point_second)
    print("ortak_dikme_uzunlugu_mm:", f"{line_pair.distance:.12f}")
    print("dogru_dogru_kucuk_aci_derece:", f"{np.degrees(line_pair.small_angle):.12f}")
    print("Q_noktasinin_eksen_izdusumu_mm:", q_on_axis_projection.foot)
    print("A_noktasinin_ikinci_dogru_izdusumu_mm:", a_on_second_projection.foot)
    print("delik_ekseni_datum_iliskisi:", axis_datum.relation)
    print("ikinci_dogru_datum_iliskisi:", second_datum.relation)
    print("eksen_duzlemleri_iliskisi:", axis_plane_pair.relation)
    print("eksen_duzlemleri_kesisim_yonu:", axis_plane_pair.line_direction)
    print("sonda_nokta_datum_uzakligi_mm:", f"{probe_projection.distance:.12f}")
    print("metreye_geciste_sinif_korundu_mu:", metre_pair.relation == line_pair.relation)
    print("metreye_geciste_uzaklik_orani:", f"{metre_pair.distance / line_pair.distance:.12f}")
    print("yakin_paralel_kaba_esik:", loose_near_parallel.relation)
    print("yakin_paralel_ince_esik:", strict_near_parallel.relation)
    print("yakin_paralel_kosul_sayisi:", f"{strict_near_parallel.condition_number:.6e}")
    print("acisal_esik:", f"{angular_tolerance:.12e}")
    print("mutlak_uzaklik_esigi_mm:", f"{absolute_tolerance_mm:.12e}")
    print("bagil_uzaklik_esigi:", f"{relative_tolerance:.12e}")
    print("referans_uzunlugu_mm:", f"{reference_scale_mm:.12f}")
    print("bilimsel_imza:", canonical_array_sha256(signature_values))


if __name__ == "__main__":
    main()
