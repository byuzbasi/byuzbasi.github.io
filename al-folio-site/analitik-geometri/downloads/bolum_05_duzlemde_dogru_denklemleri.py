"""Bölüm 5 laboratuvarı: sentetik bir ölçme referans doğrusu."""

from __future__ import annotations

from importlib.metadata import version

import numpy as np

from agbook import (
    canonical_array_sha256,
    canonical_line_coefficients,
    line_from_point_direction,
    line_from_points,
    line_membership_diagnostics,
    line_residuals,
    parametric_line_points,
)


def main() -> None:
    # Bütün koordinatlar metredir; parametreler boyutsuzdur.
    control_a = np.array([1000.0, 500.0])
    control_b = np.array([1300.0, 700.0])
    direction = control_b - control_a
    parameters = np.array([0.0, 0.25, 0.5, 0.75, 1.0])

    coefficients = line_from_points(control_a, control_b)
    stations = parametric_line_points(control_a, direction, parameters)
    station_residuals = line_residuals(coefficients, stations)

    shifted_anchor = stations[2]
    equivalent = line_from_point_direction(shifted_anchor, -3.0 * direction)
    scaled_equation = canonical_line_coefficients(-7.0 * coefficients)

    # Aday, kanonik birim normal yönünde 0.006 m ötelenmiştir.
    candidate = stations[3] + 0.006 * coefficients[:2]
    membership = line_membership_diagnostics(
        coefficients,
        candidate,
        absolute_tolerance=0.010,
        relative_tolerance=0.0,
        reference_scale=500.0,
    )

    input_hash = canonical_array_sha256(
        np.concatenate([control_a, control_b, parameters])
    )
    print("birim: m")
    print("parametre_birimi: boyutsuz")
    print("kanonik_katsayilar:", np.round(coefficients, 9))
    print("istasyon_sekli:", stations.shape)
    print("istasyonlar_m:", np.round(stations, 3).tolist())
    print(f"en_buyuk_istasyon_artigi: {np.max(np.abs(station_residuals)):.3e}")
    print(f"baslangic_yon_esdegerlik_artigi: {np.max(np.abs(equivalent - coefficients)):.3e}")
    print(f"denklem_olcek_esdegerlik_artigi: {np.max(np.abs(scaled_equation - coefficients)):.3e}")
    print(f"aday_ham_artigi: {membership.residual:.6f}")
    print(f"uyelik_esigi: {membership.threshold:.6f}")
    print(f"aday_dogru_uzerinde: {membership.on_line}")
    print(f"girdi_sha256: {input_hash}")
    print(f"numpy_surumu: {version('numpy')}")


if __name__ == "__main__":
    main()
