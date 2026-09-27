"""Bölüm 11: nokta kuvveti, radikal eksen ve güç diyagramı laboratuvarı.

Model, üç sentetik dairesel hizmet bölgesini iki boyutlu Öklid düzleminde
karşılaştırır. Sinyal yayılımı, nüfus, maliyet, engel, ölçüm gürültüsü veya
gerçek hizmet kalitesi içermez.
"""

from __future__ import annotations

import numpy as np

from agbook import (
    canonical_array_sha256,
    circle_pencil_member,
    point_power,
    radical_axis_diagnostics,
    radical_center_diagnostics,
    rotation_matrix_2d,
)


TOLERANCES = {
    "absolute_tolerance": 1e-10,
    "relative_tolerance": 1e-12,
    "reference_scale": 20.0,
}

CENTER_TOLERANCES = {
    "angular_tolerance": 1e-12,
    **TOLERANCES,
}


def monic_circle(center: np.ndarray, radius: float) -> np.ndarray:
    """Merkez-yarıçap verisini ``(1,D,E,F)`` katsayılarına dönüştürür."""

    return np.array(
        [
            1.0,
            -2.0 * center[0],
            -2.0 * center[1],
            float(center @ center - radius**2),
        ]
    )


def main() -> None:
    centers = np.array([[0.0, 0.0], [8.0, 0.0], [0.0, 6.0]])  # km
    radii = np.array([5.0, 3.0, 4.0])  # km
    pairs = ((0, 1), (0, 2), (1, 2))

    axes = [
        radical_axis_diagnostics(
            centers[i], radii[i], centers[j], radii[j], **TOLERANCES
        )
        for i, j in pairs
    ]
    assert all(axis.relation == "line" for axis in axes)
    axis_matrix = np.vstack([axis.line_coefficients for axis in axes])

    radical_center = radical_center_diagnostics(
        centers, radii, **CENTER_TOLERANCES
    )
    assert radical_center.relation == "point"
    np.testing.assert_allclose(radical_center.point, [5.0, 3.75])
    np.testing.assert_allclose(radical_center.power_values, 14.0625, atol=1e-12)
    assert radical_center.max_axis_residual <= radical_center.length_threshold

    x_values = np.linspace(-4.0, 12.0, 65)
    y_values = np.linspace(-4.0, 10.0, 57)
    xx, yy = np.meshgrid(x_values, y_values)
    grid = np.column_stack([xx.ravel(), yy.ravel()])
    powers = np.sum(
        (grid[:, None, :] - centers[None, :, :]) ** 2,
        axis=2,
    ) - radii[None, :] ** 2
    labels = np.argmin(powers, axis=1)
    label_counts = np.bincount(labels, minlength=3)

    first_circle = monic_circle(centers[0], radii[0])
    second_circle = monic_circle(centers[1], radii[1])
    pencil_parameters = np.array([0.0, 0.5, 0.625, 1.0])
    pencil_members = [
        circle_pencil_member(first_circle, second_circle, parameter)
        for parameter in pencil_parameters
    ]
    assert [member.locus_type for member in pencil_members] == [
        "circle",
        "circle",
        "point",
        "circle",
    ]

    rotation = rotation_matrix_2d(np.deg2rad(23.0))
    translation = np.array([40.0, -25.0])  # km
    moved_centers = centers @ rotation.T + translation
    moved_grid = grid @ rotation.T + translation
    moved_center = radical_center_diagnostics(
        moved_centers, radii, **CENTER_TOLERANCES
    )
    expected_center = rotation @ radical_center.point + translation
    np.testing.assert_allclose(moved_center.point, expected_center, atol=2e-13)
    moved_powers = np.sum(
        (moved_grid[:, None, :] - moved_centers[None, :, :]) ** 2,
        axis=2,
    ) - radii[None, :] ** 2
    moved_labels = np.argmin(moved_powers, axis=1)
    np.testing.assert_allclose(moved_powers, powers, atol=2e-12, rtol=0.0)
    sorted_powers = np.sort(powers, axis=1)
    power_gaps = sorted_powers[:, 1] - sorted_powers[:, 0]
    stable_mask = power_gaps > 1e-10  # km^2
    assert np.array_equal(moved_labels[stable_mask], labels[stable_mask])
    boundary_count = int(np.count_nonzero(~stable_mask))

    center_powers = np.array(
        [point_power(center, radius, radical_center.point) for center, radius in zip(centers, radii)]
    )
    signature_values = np.concatenate(
        [
            centers.ravel(),
            radii,
            axis_matrix.ravel(),
            radical_center.point,
            center_powers,
            label_counts.astype(float),
            np.array([member.radius_squared for member in pencil_members]),
        ]
    )

    print("birim: km")
    print("model: sentetik_dairesel_hizmet_bolgeleri")
    print("gercek_kapsama_modeli_mi: False")
    print("merkezler_km:", centers.tolist())
    print("yaricaplar_km:", radii.tolist())
    for pair, axis in zip(pairs, axes):
        print(f"radikal_eksen_{pair}: {axis.line_coefficients}")
    print("radikal_merkez_km:", radical_center.point)
    print("ortak_kuvvet_km2:", center_powers)
    print("en_buyuk_eksen_artigi_km:", f"{radical_center.max_axis_residual:.3e}")
    print("eksen_sistem_kosul_sayisi:", f"{radical_center.condition_number:.9f}")
    print("izgara_nokta_sayisi:", grid.shape[0])
    print("guc_hucre_sayimlari:", label_counts)
    print("sinir_baglama_noktasi_sayisi:", boundary_count)
    print(
        "demet_siniflari:",
        [(parameter, member.locus_type, member.radius_squared) for parameter, member in zip(pencil_parameters, pencil_members)],
    )
    print(
        "rijit_ic_nokta_etiketleri_korundu_mu:",
        bool(np.array_equal(moved_labels[stable_mask], labels[stable_mask])),
    )
    print("bilimsel_imza:", canonical_array_sha256(signature_values))


if __name__ == "__main__":
    main()
