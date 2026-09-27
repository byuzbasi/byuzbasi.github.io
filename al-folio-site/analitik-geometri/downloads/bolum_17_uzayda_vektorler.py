"""Bölüm 17: uzayda vektörler ve yön tanısı laboratuvarı.

Uygulama, döndürülmüş ve ötelenmiş sentetik bir CAD tetrahedronudur.
Ölçülmüş veri, ağ kalitesi, üretim toleransı veya kabul kararı içermez.
"""

from __future__ import annotations

import numpy as np

from agbook import (
    canonical_array_sha256,
    scalar_triple_product,
    spatial_orientation_diagnostics,
    tetrahedron_volume,
    triangle_area_3d,
    unit_normal_3d,
)


def main() -> None:
    length_unit = "mm"

    # Sütunları sağ yönlü, ortonormal bir yerel CAD çerçevesidir.
    rotation = np.array(
        [
            [3.0 / 5.0, -12.0 / 25.0, 16.0 / 25.0],
            [4.0 / 5.0, 9.0 / 25.0, -12.0 / 25.0],
            [0.0, 20.0 / 25.0, 15.0 / 25.0],
        ]
    )
    origin_mm = np.array([120.0, 80.0, 35.0])
    edge_lengths_mm = np.array([60.0, 50.0, 75.0])
    vertices_mm = np.vstack(
        [
            origin_mm,
            origin_mm + edge_lengths_mm[0] * rotation[:, 0],
            origin_mm + edge_lengths_mm[1] * rotation[:, 1],
            origin_mm + edge_lengths_mm[2] * rotation[:, 2],
        ]
    )
    point_a, point_b, point_c, point_d = vertices_mm
    edge_ab = point_b - point_a
    edge_ac = point_c - point_a
    edge_ad = point_d - point_a

    face_normal = unit_normal_3d(edge_ab, edge_ac)
    face_area_mm2 = triangle_area_3d(point_a, point_b, point_c)
    signed_box_volume_mm3 = scalar_triple_product(edge_ab, edge_ac, edge_ad)
    tetrahedron_volume_mm3 = tetrahedron_volume(
        point_a,
        point_b,
        point_c,
        point_d,
    )
    diagnosis = spatial_orientation_diagnostics(
        edge_ab,
        edge_ac,
        edge_ad,
        relative_tolerance=1e-12,
    )
    swapped_diagnosis = spatial_orientation_diagnostics(
        edge_ac,
        edge_ab,
        edge_ad,
        relative_tolerance=1e-12,
    )

    vertices_m = vertices_mm / 1000.0
    point_a_m, point_b_m, point_c_m, point_d_m = vertices_m
    face_area_m2 = triangle_area_3d(point_a_m, point_b_m, point_c_m)
    tetrahedron_volume_m3 = tetrahedron_volume(
        point_a_m,
        point_b_m,
        point_c_m,
        point_d_m,
    )

    # İlk iki kenarın düzlemine çok yakın, fakat tam düzlemde olmayan aday.
    near_edge = (
        15.0 * rotation[:, 0]
        + 15.0 * rotation[:, 1]
        + 1e-10 * rotation[:, 2]
    )
    near_diagnosis = spatial_orientation_diagnostics(
        edge_ab,
        edge_ac,
        near_edge,
        relative_tolerance=1e-10,
    )

    np.testing.assert_allclose(rotation.T @ rotation, np.eye(3), atol=2e-15)
    np.testing.assert_allclose(np.linalg.det(rotation), 1.0, atol=2e-15)
    np.testing.assert_allclose(
        vertices_mm,
        np.array(
            [
                [120.0, 80.0, 35.0],
                [156.0, 128.0, 35.0],
                [96.0, 98.0, 75.0],
                [168.0, 44.0, 80.0],
            ]
        ),
        atol=2e-14,
    )
    np.testing.assert_allclose(face_normal, rotation[:, 2], atol=2e-15)
    np.testing.assert_allclose(face_area_mm2, 1500.0, atol=2e-12)
    np.testing.assert_allclose(signed_box_volume_mm3, 225000.0, atol=2e-10)
    np.testing.assert_allclose(tetrahedron_volume_mm3, 37500.0, atol=2e-11)
    np.testing.assert_allclose(face_area_m2, face_area_mm2 * 1e-6, atol=2e-18)
    np.testing.assert_allclose(
        tetrahedron_volume_m3,
        tetrahedron_volume_mm3 * 1e-9,
        atol=2e-18,
    )
    assert diagnosis.classification == "right_handed"
    assert not diagnosis.numerically_ambiguous
    assert swapped_diagnosis.classification == "left_handed"
    assert near_diagnosis.classification == "uncertain"
    assert near_diagnosis.numerically_ambiguous

    signature_values = np.concatenate(
        [
            rotation.ravel(),
            origin_mm,
            edge_lengths_mm,
            vertices_mm.ravel(),
            edge_ab,
            edge_ac,
            edge_ad,
            face_normal,
            np.array(
                [
                    face_area_mm2,
                    signed_box_volume_mm3,
                    tetrahedron_volume_mm3,
                    diagnosis.normalized_triple_product,
                    swapped_diagnosis.normalized_triple_product,
                ]
            ),
            vertices_m.ravel(),
            np.array([face_area_m2, tetrahedron_volume_m3]),
            near_edge,
            np.array(
                [
                    near_diagnosis.scalar_triple_product,
                    near_diagnosis.normalized_triple_product,
                    near_diagnosis.relative_tolerance,
                ]
            ),
        ]
    )

    print("uzunluk_birimi:", length_unit)
    print("model: sentetik_dondurulmus_cad_tetrahedronu")
    print("olculmus_veri_mi: False")
    print("ag_kalitesi_hesabi_mi: False")
    print("uretim_kabul_hesabi_mi: False")
    print("yerel_cerceve_ortogonal_mi: True")
    print("yerel_cerceve_determinanti:", f"{np.linalg.det(rotation):.12f}")
    print("kose_noktalari_mm:")
    print(vertices_mm)
    print("ABC_birim_normali:", face_normal)
    print("ABC_ucgen_alani_mm2:", f"{face_area_mm2:.12f}")
    print("yonlu_paralelyuz_hacmi_mm3:", f"{signed_box_volume_mm3:.12f}")
    print("tetrahedron_hacmi_mm3:", f"{tetrahedron_volume_mm3:.12f}")
    print("yon_sinifi:", diagnosis.classification)
    print("boyutsuz_normalize_karma_carpim:", f"{diagnosis.normalized_triple_product:.12f}")
    print("ilk_iki_kenar_degistirilince_yon:", swapped_diagnosis.classification)
    print(
        "metre_milimetre_alan_hacim_olcegi_korundu_mu:",
        bool(
            np.isclose(face_area_m2, face_area_mm2 * 1e-6)
            and np.isclose(tetrahedron_volume_m3, tetrahedron_volume_mm3 * 1e-9)
        ),
    )
    print("duzleme_yakin_aday_sinifi:", near_diagnosis.classification)
    print("duzleme_yakin_aday_belirsiz_mi:", near_diagnosis.numerically_ambiguous)
    print(
        "duzleme_yakin_aday_normalize_karma_carpim:",
        f"{near_diagnosis.normalized_triple_product:.12e}",
    )
    print("bilimsel_imza:", canonical_array_sha256(signature_values))


if __name__ == "__main__":
    main()
