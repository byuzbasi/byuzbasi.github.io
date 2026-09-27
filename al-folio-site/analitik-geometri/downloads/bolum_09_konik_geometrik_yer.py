"""Bölüm 9 laboratuvarı: sentetik bir yörünge izinin konik geometrisi.

Model iki boyutlu ve sentetiktir. Koordinatlar kilometredir. Noktalar,
odak--doğrultman oranı sabit bir elips üzerinden tam olarak üretilir; sonra
aynı geometri rijit bir çerçeve değişiminde yeniden denetlenir. Zaman, hız,
kütleçekim kuvveti, ölçüm gürültüsü ve yörünge kestirimi modellenmez.
"""

from __future__ import annotations

import numpy as np

from agbook import (
    canonical_array_sha256,
    classify_standard_cone_plane,
    focus_directrix_diagnostics,
    rotation_matrix_2d,
)


def main() -> None:
    eccentricity = 0.6
    directrix_distance_km = 12_000.0
    focus_km = np.array([0.0, 0.0])
    directrix = np.array([1.0, 0.0, -directrix_distance_km])

    center_x_km = -(
        eccentricity**2
        * directrix_distance_km
        / (1.0 - eccentricity**2)
    )
    semimajor_km = (
        eccentricity
        * directrix_distance_km
        / (1.0 - eccentricity**2)
    )
    semiminor_km = semimajor_km * np.sqrt(1.0 - eccentricity**2)
    parameters = np.linspace(0.0, 2.0 * np.pi, 12, endpoint=False)
    orbit_points_km = np.column_stack(
        [
            center_x_km + semimajor_km * np.cos(parameters),
            semiminor_km * np.sin(parameters),
        ]
    )

    before = focus_directrix_diagnostics(
        orbit_points_km,
        focus_km,
        directrix,
        eccentricity,
        reference_scale=directrix_distance_km,
    )

    rotation = rotation_matrix_2d(np.deg2rad(23.0))
    translation_km = np.array([3_200.0, -1_800.0])
    transformed_points_km = orbit_points_km @ rotation.T + translation_km
    transformed_focus_km = focus_km @ rotation.T + translation_km
    transformed_normal = rotation @ directrix[:2]
    transformed_offset = directrix[2] - float(
        np.dot(transformed_normal, translation_km)
    )
    transformed_directrix = np.r_[transformed_normal, transformed_offset]
    after = focus_directrix_diagnostics(
        transformed_points_km,
        transformed_focus_km,
        transformed_directrix,
        eccentricity,
        reference_scale=directrix_distance_km,
    )

    section_cases = (
        ("yatay", [0.0, 0.0], 2.0),
        ("az_egimli", [0.5, 0.0], 2.0),
        ("uretece_paralel", [1.0, 0.0], 2.0),
        ("dik_egimli", [1.25, 0.0], 2.0),
        ("tepe_az_egimli", [0.5, 0.0], 0.0),
        ("tepe_uretece", [1.0, 0.0], 0.0),
        ("tepe_dik_egimli", [1.25, 0.0], 0.0),
    )

    print("birim: km")
    print("model: sentetik_iki_boyutlu_geometri")
    print("dinamik_model_var_mi: False")
    print("nokta_sayisi:", orbit_points_km.shape[0])
    print("dismerkezlik:", f"{eccentricity:.12f}")
    print("konik_turu:", before.conic_type)
    print("oran_araligi_once:", np.round([before.ratios.min(), before.ratios.max()], 12))
    print("en_buyuk_mutlak_artik_km_once:", f"{before.maximum_absolute_residual:.3e}")
    print("en_buyuk_olceksiz_artik_once:", f"{before.maximum_scaled_residual:.3e}")
    print("oran_araligi_sonra:", np.round([after.ratios.min(), after.ratios.max()], 12))
    print("en_buyuk_mutlak_artik_km_sonra:", f"{after.maximum_absolute_residual:.3e}")
    print("en_buyuk_olceksiz_artik_sonra:", f"{after.maximum_scaled_residual:.3e}")
    print(
        "rijit_oran_farki:",
        f"{np.max(np.abs(after.ratios - before.ratios)):.3e}",
    )
    for case_name, slopes, offset in section_cases:
        diagnosis = classify_standard_cone_plane(slopes, offset)
        print(
            f"kesit_{case_name}:",
            diagnosis.section_type,
            "dejenere=" + str(diagnosis.degenerate),
        )

    signature_values = np.concatenate(
        [
            np.array([eccentricity, directrix_distance_km]),
            focus_km,
            directrix,
            parameters,
            orbit_points_km.ravel(),
            rotation.ravel(),
            translation_km,
            transformed_points_km.ravel(),
        ]
    )
    print("bilimsel_imza:", canonical_array_sha256(signature_values))


if __name__ == "__main__":
    main()
