"""Bölüm 10 laboratuvarı: dairesel CAD güvenlik bölgesi geometrisi.

Model iki boyutlu ve deterministiktir; koordinatlar milimetredir. Bilinen bir
çember ile üç sonsuz takım yolu arasındaki kesen, teğet ve ayrık ilişkileri
hesaplanır. Sonuç; takım yarıçapı, hareket zamanı, üretim toleransı, parça
deformasyonu veya gerçek bir çarpışma güvenlik kararı içermez.
"""

from __future__ import annotations

import numpy as np

from agbook import (
    canonical_array_sha256,
    circle_line_intersections,
    general_circle_diagnostics,
    polar_line_of_point,
    rotation_matrix_2d,
    tangent_points_from_point,
)


ABSOLUTE_TOLERANCE_MM = 1e-9
RELATIVE_TOLERANCE = 1e-12


def transform_line(line: np.ndarray, rotation: np.ndarray, translation: np.ndarray) -> np.ndarray:
    """``x' = Qx+b`` altında genel doğru katsayılarını taşır."""

    moved_normal = rotation @ line[:2]
    moved_offset = line[2] - float(np.dot(moved_normal, translation))
    return np.r_[moved_normal, moved_offset]


def main() -> None:
    center_mm = np.array([120.0, 80.0])
    radius_mm = 45.0
    reference_scale_mm = 200.0
    general_coefficients = np.array(
        [
            1.0,
            -2.0 * center_mm[0],
            -2.0 * center_mm[1],
            float(np.dot(center_mm, center_mm) - radius_mm**2),
        ]
    )
    general = general_circle_diagnostics(general_coefficients)

    paths = {
        "kesen": np.array([0.0, 1.0, -100.0]),
        "teget": np.array([1.0, 0.0, -165.0]),
        "ayrik": np.array([0.0, 1.0, -135.0]),
    }
    diagnostics = {
        name: circle_line_intersections(
            center_mm,
            radius_mm,
            line,
            absolute_tolerance=ABSOLUTE_TOLERANCE_MM,
            relative_tolerance=RELATIVE_TOLERANCE,
            reference_scale=reference_scale_mm,
        )
        for name, line in paths.items()
    }

    inspection_point_mm = np.array([200.0, 140.0])
    contacts = tangent_points_from_point(
        center_mm,
        radius_mm,
        inspection_point_mm,
        absolute_tolerance=ABSOLUTE_TOLERANCE_MM,
        relative_tolerance=RELATIVE_TOLERANCE,
        reference_scale=reference_scale_mm,
    )
    polar = polar_line_of_point(center_mm, radius_mm, inspection_point_mm)
    polar_contact_residuals = contacts.points @ polar[:2] + polar[2]

    rotation = rotation_matrix_2d(np.deg2rad(27.0))
    translation_mm = np.array([400.0, -150.0])
    moved_center_mm = rotation @ center_mm + translation_mm
    moved_paths = {
        name: transform_line(line, rotation, translation_mm)
        for name, line in paths.items()
    }
    moved_diagnostics = {
        name: circle_line_intersections(
            moved_center_mm,
            radius_mm,
            line,
            absolute_tolerance=ABSOLUTE_TOLERANCE_MM,
            relative_tolerance=RELATIVE_TOLERANCE,
            reference_scale=reference_scale_mm,
        )
        for name, line in moved_paths.items()
    }

    chord_differences = [
        abs(
            (moved_diagnostics[name].chord_length or 0.0)
            - (diagnostics[name].chord_length or 0.0)
        )
        for name in paths
    ]
    distance_differences = [
        abs(moved_diagnostics[name].center_distance - diagnostics[name].center_distance)
        for name in paths
    ]

    print("birim: mm")
    print("model: sentetik_iki_boyutlu_cad_geometrisi")
    print("tam_carpisma_modeli_mi: False")
    print("cember_turu:", general.locus_type)
    print("merkez_mm:", np.round(general.center, 9))
    print("yaricap_mm:", f"{general.radius:.9f}")
    for name, result in diagnostics.items():
        print(
            f"yol_{name}:",
            result.relation,
            "merkez_uzakligi_mm=" + f"{result.center_distance:.9f}",
            "kiris_uzunlugu_mm="
            + ("yok" if result.chord_length is None else f"{result.chord_length:.9f}"),
        )
        print(f"yol_{name}_kesisimler_mm:", np.round(result.points, 9))
    print("dis_nokta_sinifi:", contacts.relation)
    print("teget_uzunlugu_mm:", f"{contacts.tangent_length:.9f}")
    print("temas_noktalari_mm:", np.round(contacts.points, 9))
    print("kutupsal_kanonik:", np.round(polar, 12))
    print("en_buyuk_kutupsal_artigi_mm:", f"{np.max(np.abs(polar_contact_residuals)):.3e}")
    print("rijit_siniflar_korundu_mu:", all(
        diagnostics[name].relation == moved_diagnostics[name].relation for name in paths
    ))
    print("en_buyuk_rijit_uzaklik_farki_mm:", f"{max(distance_differences):.3e}")
    print("en_buyuk_rijit_kiris_farki_mm:", f"{max(chord_differences):.3e}")

    signature_values = np.concatenate(
        [
            center_mm,
            np.array([radius_mm, reference_scale_mm, ABSOLUTE_TOLERANCE_MM, RELATIVE_TOLERANCE]),
            general_coefficients,
            *(line for line in paths.values()),
            inspection_point_mm,
            rotation.ravel(),
            translation_mm,
        ]
    )
    print("bilimsel_imza:", canonical_array_sha256(signature_values))


if __name__ == "__main__":
    main()
